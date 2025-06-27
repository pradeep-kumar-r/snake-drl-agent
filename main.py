from src.game.env import SnakeEnv
from src.agent.agents import RandomSnakeAgent, DQNSnakeAgent
from src.config import config as app_config


def main():
    env = SnakeEnv(app_config)
    agent = RandomSnakeAgent(app_config)
    training_config = app_config.get_training_config()
    max_episodes = training_config["MAX_TRAINING_EPISODES"]
    max_steps_per_episode = training_config["MAX_TIMESTEPS_PER_EPISODE"]
    total_rewards = []
    episode_lengths = []
    
    print(f"Starting Snake game with Random Agent for {max_episodes} episodes")
    for episode in range(1, max_episodes + 1):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        print(f"\nEpisode {episode}/{max_episodes}")
        print(f"Initial state: {info}")
        for _ in range(1, max_steps_per_episode + 1):
            action = agent.select_action(obs)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            env.render()
            if terminated or truncated:
                break
        total_rewards.append(episode_reward)
        episode_lengths.append(steps)
        print(f"Episode {episode} finished after {steps} steps")
        print(f"Total reward: {episode_reward}")
        print(f"Final state: {info}")
    
    print("\n===== Game Summary =====")
    print(f"Episodes played: {max_episodes}")
    print(f"Average reward: {sum(total_rewards) / len(total_rewards):.2f}")
    print(f"Average episode length: {sum(episode_lengths) / len(episode_lengths):.2f}")
    print(f"Max reward: {max(total_rewards):.2f}")
    print(f"Max episode length: {max(episode_lengths)}")
    env.close()


if __name__ == "__main__":
    main()
