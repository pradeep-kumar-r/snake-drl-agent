import random
import os
import torch
import torch.nn as nn
import torch.optim as optim
from src.agent.dqn_model import ConvDQN
from src.config import config as app_config # Main config module
from src.agent.replay_buffer import ReplayBuffer, Transition


class SnakeAgent:
    def __init__(self, env_action_space_n, config_module=app_config):
        self.config = config_module
        self.model_cfg = self.config.get_model_config()
        self.train_cfg = self.config.get_training_config()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"SnakeAgent using device: {self.device}")

        self.num_actions = env_action_space_n # Should match env.action_space.n

        self.policy_net = ConvDQN(num_classes=self.num_actions).to(self.device)
        self.target_net = ConvDQN(num_classes=self.num_actions).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval() # Target network is not trained directly

        self.optimizer = optim.AdamW(self.policy_net.parameters(), lr=self.model_cfg.LEARNING_RATE, amsgrad=True)
        
        buffer_capacity = self.train_cfg.REPLAY_MEMORY_SIZE
        self.memory = ReplayBuffer(buffer_capacity)

        self.batch_size = self.train_cfg.BATCH_SIZE
        self.gamma = self.train_cfg.GAMMA
        self.epsilon_start = self.train_cfg.EPSILON_START
        self.epsilon_end = self.train_cfg.EPSILON_END
        self.epsilon_decay = self.train_cfg.EPSILON_DECAY
        self.target_update_frequency = self.train_cfg.TARGET_UPDATE_FREQUENCY

        self.steps_done = 0

    def select_action(self, state_tensor):
        """Selects an action using an epsilon-greedy policy."""
        # state_tensor is expected to be [1, C, H, W]
        sample = random.random()
        # Epsilon decay: epsilon_start * (epsilon_decay ^ steps_done)
        # More commonly: eps_threshold = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * \
        #                             math.exp(-1. * self.steps_done / self.epsilon_decay)
        # Using a simpler linear decay or step decay might be easier to tune initially.
        # For now, let's use the exponential decay from PyTorch DQN tutorial for consistency if that's a reference.
        # Or a simpler one: reduce epsilon after each episode or N steps.
        
        # Let's use a common exponential decay for epsilon
        # eps_threshold = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * \
        #                 math.exp(-1. * self.steps_done / self.epsilon_decay)
        # A simpler decay: reduce epsilon linearly until it reaches epsilon_end
        if self.steps_done < self.train_cfg.EPSILON_DECAY_LAST_FRAME: # Number of frames for epsilon to decay
            eps_threshold = self.epsilon_start - (self.epsilon_start - self.epsilon_end) * (self.steps_done / self.train_cfg.EPSILON_DECAY_LAST_FRAME)
        else:
            eps_threshold = self.epsilon_end

        self.steps_done += 1

        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return the largest column value of each row.
                # second column on max result is index of where max element was found,
                # so we pick action with the larger expected reward.
                # Ensure state_tensor is on the correct device
                q_values = self.policy_net(state_tensor.to(self.device))
                return q_values.max(1)[1].view(1, 1)
        else:
            return torch.tensor([[random.randrange(self.num_actions)]], device=self.device, dtype=torch.long)

    def optimize_model(self):
        if len(self.memory) < self.batch_size:
            return # Not enough samples in memory to learn

        transitions = self.memory.sample(self.batch_size)
        # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
        # detailed explanation). This converts batch-array of Transitions
        # to Transition of batch-arrays.
        batch = Transition(*zip(*transitions))

        # Compute a mask of non-final states and concatenate the batch elements
        # (a final state would've been the one after which simulation ended)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), 
                                      device=self.device, dtype=torch.bool)
        
        non_final_next_states_list = [s for s in batch.next_state if s is not None]
        if not non_final_next_states_list: # All next states are None (all episodes in batch ended)
            non_final_next_states = torch.empty(0, *batch.state[0].shape[1:]).to(self.device) # Use shape of state
        else:
            non_final_next_states = torch.cat(non_final_next_states_list).to(self.device)

        state_batch = torch.cat(batch.state).to(self.device)
        action_batch = torch.cat(batch.action).to(self.device)
        reward_batch = torch.cat(batch.reward).to(self.device)

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken. These are the actions which would've been taken
        # for each batch state according to policy_net
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        # Expected values of actions for non_final_next_states are computed based
        # on the "older" target_net; selecting their best reward with max(1)[0].
        # This is merged based on the mask, such that we'll have either the expected
        # state value or 0 in case the state was final.
        next_state_values = torch.zeros(self.batch_size, device=self.device)
        if non_final_next_states.nelement() > 0: # Check if tensor is not empty
            with torch.no_grad():
                next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0]
        
        # Compute the expected Q values
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch

        # Compute Huber loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        # In-place gradient clipping
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        self.optimizer.step()
        
        return loss.item() # Return loss for logging

    def update_target_network_if_needed(self, current_episode_or_step):
        if current_episode_or_step % self.target_update_frequency == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            print(f"Target network updated at step/episode {current_episode_or_step}")

    def save_model(self, path, episode):
        if not os.path.exists(path):
            os.makedirs(path)
        model_path = os.path.join(path, f"{self.model_cfg.MODEL_NAME_PREFIX}episode_{episode}.pth")
        torch.save({
            'episode': episode,
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'steps_done': self.steps_done
        }, model_path)
        print(f"Model saved to {model_path}")

    def load_model(self, full_path):
        if os.path.exists(full_path):
            checkpoint = torch.load(full_path, map_location=self.device)
            self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
            self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.steps_done = checkpoint.get('steps_done', 0) # Default to 0 if not found
            # episode = checkpoint.get('episode', 0)
            self.policy_net.train() # Ensure policy_net is in train mode
            self.target_net.eval()  # Ensure target_net is in eval mode
            print(f"Model loaded from {full_path}")
            return checkpoint.get('episode', 0) # Return loaded episode
        else:
            print(f"No model found at {full_path}, starting from scratch.")
            return 0
