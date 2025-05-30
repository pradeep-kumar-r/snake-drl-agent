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

snake_drl_agent/
├── game/
│   ├── __init__.py
│   ├── game.py         # Main game loop and rendering
│   ├── snake.py        # Snake class: movement, growth, collision
│   └── food.py         # Food class: spawning, bonus logic
├── agent/
│   ├── __init__.py
│   ├── dqn.py          # DQN agent logic
│   └── model.py        # Neural network architecture
├── utils/
│   ├── __init__.py
│   ├── logger.py       # Logging utilities
│   └── recorder.py     # Screen recording utilities
├── tests/
│   ├── __init__.py
│   ├── test_game.py    # Tests for game mechanics
│   └── test_agent.py   # Tests for agent behavior
├── main.py             # Entry point to run the game or training
├── requirements.txt    # Project dependencies
└── README.md           # Project overview and instructions


## Technologies Used
ML: PyTorch
UI: Tkinter
Web App: FastAPI & Gradio
Deployment: Docker, Docker Compose
Logging: Loguru
