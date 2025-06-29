from src.game.env import SnakeEnv
from src.agent.agents import RandomSnakeAgent, DQNSnakeAgent
from src.config import config as app_config
from src.utils.logger import logger


def main():
    env = SnakeEnv(app_config)
    # agent = RandomSnakeAgent(app_config)
    agent = DQNSnakeAgent(app_config)
    training_config = app_config.get_training_config()
    model_config = app_config.get_model_config()
    max_episodes = training_config["MAX_TRAINING_EPISODES"]
    max_steps_per_episode = training_config["MAX_TIMESTEPS_PER_EPISODE"]
    episodes_per_checkpoint = training_config["EPISODES_PER_CHECKPOINT"]
    total_rewards = []
    episode_lengths = []
    
    logger.info(f"Starting Snake game with DQN Agent for {max_episodes} episodes")
    for episode in range(1, max_episodes + 1):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0
        logger.info(f"Episode {episode}/{max_episodes}")
        logger.debug(f"Initial state: {info}")
        
        for step in range(1, max_steps_per_episode + 1):
            action = agent.select_action(obs, episode)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1
            
            loss = agent.optimize_model()
            if loss is not None and step % training_config["PRINT_LOSS_EVERY"] == 0:
                logger.info(f"Step {step}, Loss: {loss:.4f}, Epsilon: {agent.current_epsilon:.4f}")
                
            env.render()
            if terminated or truncated:
                break
                
        total_rewards.append(episode_reward)
        episode_lengths.append(steps)
        
        agent.training_metrics['rewards'].append(episode_reward)
        agent.training_metrics['episode_lengths'].append(steps)
        
        logger.info(f"Episode {episode} finished after {steps} steps")
        logger.info(f"Total reward: {episode_reward}")
        logger.debug(f"Final state: {info}")
        
        if episode % episodes_per_checkpoint == 0:
            logger.info(f"Saving checkpoint at episode {episode}")
            agent.save(model_config["MODELS_FOLDER_PATH"], episode)
    
    logger.info("===== Game Summary =====")
    logger.info(f"Episodes played: {max_episodes}")
    logger.info(f"Average reward: {sum(total_rewards) / len(total_rewards):.2f}")
    logger.info(f"Average episode length: {sum(episode_lengths) / len(episode_lengths):.2f}")
    logger.info(f"Max reward: {max(total_rewards):.2f}")
    logger.info(f"Max episode length: {max(episode_lengths)}")
    env.close()


if __name__ == "__main__":
    main()
