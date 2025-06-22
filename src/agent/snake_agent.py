import random
import os
import math
from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from src.agent.dqn_model import ConvDQN
from src.agent.replay_buffer import ReplayBuffer, Transition
from src.config import ConfigManager


class BaseSnakeAgent(ABC):
    """Interface for all Snake agents."""
    def __init__(self, config: ConfigManager):
        """Initialize the base agent.
        Args:
            config: Configuration object with agent parameters
        """
        self.action_space_n = config.get_model_config()["NUM_ACTIONS"]
        self.config = config
    
    @abstractmethod
    def select_action(self, state: np.ndarray) -> int:
        """Select an action given the current state.
        Args:
            state: Current state/observation from the environment
        Returns:
            int: Selected action
        """
    
    def on_episode_start(self, episode: int) -> None:
        """Called at the start of each episode.
        Args:
            episode: Current episode number
        """
    
    def on_episode_end(self, episode: int) -> None:
        """Called at the end of each episode.
        Args:
            episode: Current episode number
        """
    
    def on_step(self, 
                state: np.ndarray, 
                action: int, 
                reward: float, 
                next_state: np.ndarray, 
                done: bool) -> None:
        """Called after each step in the environment.
        Args:
            state: Previous state
            action: Action taken
            reward: Reward received
            next_state: New state after taking the action
            done: Whether the episode is done
        """
    
    def save(self, path: str, episode: int) -> None:
        """Save the agent's state to disk.
        Args:
            path: Directory to save the model
            episode: Current episode number
        """
    
    def load(self, path: str) -> int:
        """Load the agent's state from disk.
        Args:
            path: Path to the saved model
        Returns:
            int: The episode number of the loaded model, or 0 if starting fresh
        """
        if path or not path:
            return 0


class RandomSnakeAgent(BaseSnakeAgent):
    """A simple agent that selects actions randomly."""
    def __init__(self, config: ConfigManager):
        super().__init__(config)
        self.action_space = list(range(self.action_space_n))
    
    def select_action(self, state: np.ndarray) -> int:
        return random.choice(self.action_space)


class DQNSnakeAgent(BaseSnakeAgent):
    """DQN based RL agent."""
    def __init__(self, config: ConfigManager):
        super().__init__(config)
        
        # Get configurations
        self.model_config = self.config.get_model_config()
        self.train_config = self.config.get_training_config()
        
        # Set device (GPU if available, else CPU)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"DQNSnakeAgent using device: {self.device}")
        
        # Initialize policy and target networks
        self.policy_net = ConvDQN(num_classes=self.action_space_n).to(self.device)
        self.target_net = ConvDQN(num_classes=self.action_space_n).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()  # Target network is not trained directly
        
        # Initialize optimizer
        self.optimizer = optim.AdamW(
            self.policy_net.parameters(), 
            lr=self.model_config["LEARNING_RATE"], 
            amsgrad=True
        )
        
        self.memory = ReplayBuffer(self.train_config["REPLAY_MEMORY_SIZE"])
        
        self.batch_size = self.train_config["BATCH_SIZE"]
        self.gamma = self.train_config["GAMMA"]
        self.epsilon_start = self.train_config["EPSILON_START"]
        self.epsilon_end = self.train_config["EPSILON_END"]
        self.epsilon_decay = self.train_config["EPSILON_DECAY"]
        self.target_update_frequency = self.train_config["TARGET_UPDATE_FREQUENCY"]
        
        self.steps_done = 0
        self.current_epsilon = self.epsilon_start
    
    def select_action(self, state: np.ndarray) -> int:
        self.current_epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * \
                              math.exp(-1. * self.steps_done / self.epsilon_decay)
        
        self.steps_done += 1
        if random.random() > self.current_epsilon:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.policy_net(state_tensor)
                return q_values.max(1)[1].item()
        else:
            return random.randrange(self.action_space_n)
    
    def on_step(self, 
                state: np.ndarray, 
                action: int, 
                reward: float, 
                next_state: np.ndarray, 
                done: bool) -> None:
        state_tensor = torch.FloatTensor(state).to(self.device)
        next_state_tensor = torch.FloatTensor(next_state).to(self.device) if not done else None
        action_tensor = torch.tensor([action], device=self.device)
        reward_tensor = torch.tensor([reward], device=self.device, dtype=torch.float32)
        self.memory.push(state_tensor, action_tensor, next_state_tensor, reward_tensor)
        self.optimize_model()
    
    def optimize_model(self) -> Optional[float]:
        if len(self.memory) < self.batch_size:
            return None
        
        transitions = self.memory.sample(self.batch_size)
        batch = Transition(*zip(*transitions))
        
        non_final_mask = torch.tensor(
            tuple(map(lambda s: s is not None, batch.next_state)),
            device=self.device, 
            dtype=torch.bool
        )
        
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
        
        state_batch = torch.cat(batch.state).to(self.device)
        action_batch = torch.cat(batch.action).to(self.device)
        reward_batch = torch.cat(batch.reward).to(self.device)
        
        state_action_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))
        
        next_state_values = torch.zeros(self.batch_size, device=self.device)
        if non_final_next_states.size(0) > 0:
            with torch.no_grad():
                next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0]
        
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch
        
        criterion = nn.SmoothL1Loss()
        loss = criterion(
            state_action_values, 
            expected_state_action_values.unsqueeze(1)
        )
        
        self.optimizer.zero_grad()
        loss.backward()
        
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        self.optimizer.step()
        
        return loss.item()
    
    def update_target_network(self) -> None:
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def on_episode_end(self, episode: int) -> None:
        if episode % self.target_update_frequency == 0:
            self.update_target_network()
            print(f"Target network updated at episode {episode}")
    
    def save(self, path: str, episode: int) -> None:
        if not os.path.exists(path):
            os.makedirs(path)
            
        model_path = os.path.join(path, f"{self.model_config['MODEL_NAME_PREFIX']}_episode_{episode}.pth")
        
        torch.save({
            'episode': episode,
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'steps_done': self.steps_done,
            'epsilon': self.current_epsilon
        }, model_path)
        
        print(f"Model saved to {model_path}")
    
    def load(self, path: str) -> int:
        if os.path.exists(path):
            checkpoint = torch.load(path, map_location=self.device)
            
            self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
            self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            
            self.steps_done = checkpoint.get('steps_done', 0)
            self.current_epsilon = checkpoint.get('epsilon', self.epsilon_start)
            
            self.policy_net.train()
            self.target_net.eval()
            
            episode = checkpoint.get('episode', 0)
            print(f"Model loaded from {path} (episode {episode})")
            return episode
        else:
            print(f"No model found at {path}, starting from scratch.")
            return 0
