# Deep Reinforcement Learning for Snake Game

## Description
This project implements a Deep Reinforcement Learning (DRL) agent trained to play the classic Snake game. The agent uses a Deep Q-Network (DQN) to learn from game interactions and is deployed with a simple Gradio interface for demonstration. The Snake game is visualised using tkinter.

## Features
- Custom Snake game built using Tkinter
- RL agent based on DQN implemented in PyTorch
- Training pipeline with experience replay and target networks
- Deployment ready application using Docker and Kubernetes
- Interactive web interface for playing with the trained agent

## Repository Structure

    project-snake-drl/
    │
    ├── notebooks/
    │   ├── training_pipeline.ipynb        # Jupyter Notebook for model training
    │   ├── experimentation.ipynb          # Jupyter Notebook for experimentation and analysis
    │
    ├── src/
    │   ├── environment/
    │   │   ├── snake_game.py              # Implementation of the Snake game environment
    │   │   ├── snake_environment.py       # Gym-compatible wrapper for the game
    │   │
    │   ├── rl/
    │   │   ├── dqn_agent.py               # Deep Q-Network agent
    │   │   ├── replay_buffer.py           # Experience replay buffer
    │   │   ├── trainer.py                 # Training loop for the RL agent
    │   │
    │   ├── utils/
    │       ├── logger.py                  # Loguru-based logging setup
    │       ├── config.py                  # Configuration management
    │       ├── visualizer.py              # Visualization utilities
    │
    ├── app/
    │   ├── run_agent.py                   # Script to run the trained agent
    │   ├── app_interface.py               # Gradio-based web interface for showcasing the agent
    │
    ├── deployments/
    │   ├── Dockerfile                     # Docker setup
    │   ├── k8s.yaml                       # Kubernetes deployment file
    │
    ├── tests/
    │   ├── test_environment.py            # Unit tests for game environment
    │   ├── test_agent.py                  # Unit tests for agent
    │
    ├── .env                               # Environment variables
    ├── requirements.txt                   # Dependencies
    ├── README.md                          # Detailed project documentation
    └── config.yaml                        # General configuration file

## Technologies Used
ML: PyTorch
UI: Tkinter
Web App: FastAPI & Gradio
Deployment: Docker, Kubernetes
Logging: Loguru
