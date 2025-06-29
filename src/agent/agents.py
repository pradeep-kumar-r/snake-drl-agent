import random
import os
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from src.agent.models import ConvDQN
from src.agent.replay_buffer import ReplayBuffer, Transition
from src.config import ConfigManager
from src.utils.logger import logger


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
        
        self.model_config = self.config.get_model_config()
        self.train_config = self.config.get_training_config()
        self.data_config = self.config.get_data_config()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"DQNSnakeAgent using device: {self.device}")
        
        self.run_start_time = datetime.now().strftime("%Y%m%d_%H%M")
        
        self.training_metrics = {
            'losses': [],
            'rewards': [],
            'episode_lengths': [],
            'epsilon_values': []
        }
        
        image_height, image_width = self.model_config["IMAGE_INPUT_SIZE"]
        input_shape = (3, image_height, image_width)
        
        self.policy_net = ConvDQN(num_classes=self.action_space_n, input_shape=input_shape).to(self.device)
        self.target_net = ConvDQN(num_classes=self.action_space_n, input_shape=input_shape).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.AdamW(
            self.policy_net.parameters(), 
            lr=self.train_config["LEARNING_RATE"], 
            amsgrad=True
        )
        
        self.metrics_dir = os.path.join(self.data_config["MODEL_DATA_FOLDER_PATH"], f"run_{self.run_start_time}")
        if not os.path.exists(self.metrics_dir):
            os.makedirs(self.metrics_dir)
        
        self.memory = ReplayBuffer(self.train_config["REPLAY_MEMORY_SIZE"])
        
        self.batch_size = self.train_config["BATCH_SIZE"]
        self.gamma = self.train_config["GAMMA"]
        self.epsilon_start = self.train_config["EPSILON_START"]
        self.epsilon_end = self.train_config["EPSILON_END"]
        self.epsilon_decay = self.train_config["EPSILON_DECAY"]
        self.target_update_frequency = self.train_config["TARGET_UPDATE_FREQUENCY"]
        
        self.steps_done = 0
        self.current_epsilon = self.epsilon_start
    
    def select_action(self, state: np.ndarray, episode: int) -> int:
        if episode <= 1:
            self.current_epsilon = self.epsilon_start
        elif episode > self.train_config["EXPLOITATION_THRESHOLD"]:
            self.current_epsilon = 0
        else:
            self.current_epsilon = self.current_epsilon * (self.epsilon_decay ** (episode - 1))
            self.current_epsilon = max(self.epsilon_end, self.current_epsilon)
        
        self.steps_done += 1
        
        logger.debug(f"State shape: {state.shape}, Epsilon: {self.current_epsilon:.4f}, Steps: {self.steps_done}")
        
        if random.random() > self.current_epsilon:
            try:
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                    logger.debug(f"Input tensor shape: {state_tensor.shape}")
                    q_values = self.policy_net(state_tensor)
                    logger.debug(f"Q-values: {q_values}")
                    action = q_values.max(1)[1].item()
                    logger.debug(f"Selected action (exploit): {action}")
                    return action
            except Exception as e:
                logger.error(f"Error in action selection: {e}")
                action = random.randrange(self.action_space_n)
                logger.warning(f"Fallback random action: {action}")
                return action
        else:
            action = random.randrange(self.action_space_n)
            logger.debug(f"Selected action (explore): {action}")
            return action
    
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
        
        with torch.no_grad():
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
        
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), self.train_config["CLIP_GRADIENTS"])
        self.optimizer.step()
        
        loss_value = loss.item()
        self.training_metrics['losses'].append(loss_value)
        self.training_metrics['epsilon_values'].append(self.current_epsilon)
        
        return loss_value
    
    def update_target_network(self) -> None:
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def on_episode_end(self, episode: int) -> None:
        if episode % self.target_update_frequency == 0:
            self.update_target_network()
            logger.info(f"Target network updated at episode {episode}")
    
    def save(self, path: str, episode: int) -> None:
        if not os.path.exists(path):
            os.makedirs(path)
        
        if not hasattr(self, 'run_start_time'):
            self.run_start_time = datetime.now().strftime("%Y%m%d_%H%M")
            
        model_path = os.path.join(path, f"{self.model_config['MODEL_NAME_PREFIX']}_{self.run_start_time}_episode_{episode}.pt")
        
        torch.save({
            'episode': episode,
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'steps_done': self.steps_done,
            'epsilon': self.current_epsilon,
            'training_metrics': getattr(self, 'training_metrics', {})
        }, model_path)
        
        self.save_training_metrics(episode)
        
        logger.info(f"Model saved to {model_path}")
        
    def save_training_metrics(self, episode: int) -> None:
        metrics_df = pd.DataFrame({
            'episode': episode,
            'loss': np.mean(self.training_metrics['losses'][-100:]) if self.training_metrics['losses'] else np.nan,
            'reward': np.mean(self.training_metrics['rewards'][-10:]) if self.training_metrics['rewards'] else np.nan,
            'episode_length': np.mean(self.training_metrics['episode_lengths'][-10:]) if self.training_metrics['episode_lengths'] else np.nan,
            'epsilon': self.current_epsilon,
            'timestamp': pd.Timestamp.now()
        }, index=[0])
        
        metrics_path = os.path.join(self.metrics_dir, "metrics.csv")
        
        if os.path.exists(metrics_path):
            existing_df = pd.read_csv(metrics_path)
            updated_df = pd.concat([existing_df, metrics_df], ignore_index=True)
            updated_df.to_csv(metrics_path, index=False)
        else:
            metrics_df.to_csv(metrics_path, index=False)
            
        detailed_metrics = {
            'losses': np.array(self.training_metrics['losses']),
            'rewards': np.array(self.training_metrics['rewards']),
            'episode_lengths': np.array(self.training_metrics['episode_lengths']),
            'epsilon_values': np.array(self.training_metrics['epsilon_values'])
        }
        
        np.savez(
            os.path.join(self.metrics_dir, f"detailed_metrics_episode_{episode}.npz"),
            **detailed_metrics
        )
        
        logger.info(f"Training metrics saved to {self.metrics_dir}")
    
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
            logger.info(f"Model loaded from {path} (episode {episode})")
            return episode
        else:
            logger.warning(f"No model found at {path}, starting from scratch.")
            return 0
