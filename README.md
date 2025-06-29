# Snake DRL Agent

## Overview
This project implements a Deep Reinforcement Learning (DRL) agent trained to play the classic Snake game. The agent uses a Deep Q-Network (DQN) architecture to learn optimal gameplay strategies through interaction with the environment. The Snake game environment is built with a customizable UI using Tkinter, and the entire system is designed with a modular architecture for easy experimentation.

## Features
- Custom Snake game environment with configurable settings
- Deep Q-Network (DQN) agent implementation with PyTorch
- Experience replay buffer for improved learning stability
- Target network mechanism to reduce overestimation bias
- Configurable training parameters via YAML configuration
- Visualization of the game and agent performance
- Comprehensive test suite for all components

## Project Structure
```
snake-drl-agent/
├── src/
│   ├── agent/                  # DRL agent implementation
│   │   ├── agents.py           # Agent classes (Random, DQN)
│   │   ├── models.py           # Neural network architectures
│   │   └── replay_buffer.py    # Experience replay implementation
│   ├── game/                   # Game environment
│   │   ├── colour.py           # Color definitions
│   │   ├── direction.py        # Direction enum and utilities
│   │   ├── env.py              # SnakeEnv (gym-like interface)
│   │   ├── food.py             # Food class implementation
│   │   ├── game.py             # Game logic
│   │   ├── snake.py            # Snake class implementation
│   │   └── ui.py               # Tkinter UI implementation
│   ├── utils/                  # Utility functions
│   │   ├── logger.py           # Logger
│   │   └── utils.py            # Utility functions
│   ├── config.py               # Configuration manager
│   ├── data/                   # Directory for game and training data
│   └── models/                 # Directory for saved model checkpoints
├── tests/                      # Test suite
│   ├── conftest.py             # Test fixtures and configuration
│   └── ...                     # Test modules
├── config.yml                  # Main configuration file
├── conftest.py                 # Root pytest configuration
├── main.py                     # Entry point for running the application
├── pyproject.toml              # Project metadata and dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/snake-drl-agent.git
   cd snake-drl-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

## Running the Application

To run the application with default settings:

```bash
python main.py
```

This will start the training process with the DQN agent. The game will be rendered periodically according to the `EPISODES_PER_RENDER` setting in the configuration.

## Configuration

The project uses a YAML-based configuration system (`config.yml`) divided into several sections:

### UI Configuration (`UI_CONFIG`)
Controls the visual appearance of the game:
- `CELL_SIZE_IN_PIXELS`: Size of each cell in the game grid
- `EXTRA_WINDOW_HEIGHT`: Additional height for score display
- `BG_COLOUR`: Background color
- `TITLE`: Settings for the game title
- `SCORE`: Settings for score display
- `FOOD`: Appearance settings for regular and super food
- `BOARD`: Settings for the game board
- `SNAKE`: Appearance settings for snake head and body
- `GAME_OVER_LABEL`: Settings for game over message

### Game Configuration (`GAME_CONFIG`)
Controls the game mechanics:
- `SLEEP_PER_TIMESTEP`: Delay between game steps (seconds)
- `BOARD_DIM`: Size of the game board (number of cells)
- `EPISODES_PER_RENDER`: How often to render the game during training
- `FOOD`: Settings for food generation and behavior
- `SNAKE`: Initial snake configuration
- `SCORE`: Scoring system settings

### Data Configuration (`DATA_CONFIG`)
Defines paths for data storage:
- `DATA_FOLDER_PATH`: Root directory for data
- `MODEL_DATA_FOLDER_PATH`: Directory for model-related data
- `GAME_DATA_FOLDER_PATH`: Directory for game-related data
- `HIGH_SCORE_FILE_PATH`: File to store high scores
- `SCORES_FILE_PATH`: File to store all scores

### Logs Configuration (`LOGS_CONFIG`)
Defines logging settings:
- `LOGS_FOLDER_PATH`: Directory for log files

### Model Configuration (`MODEL_CONFIG`)
Controls the neural network architecture:
- `NUM_ACTIONS`: Number of possible actions
- `MODELS_FOLDER_PATH`: Directory for saved models
- `MODEL_NAME_PREFIX`: Prefix for model filenames
- `IMAGE_INPUT_SIZE`: Input dimensions for the neural network

### Training Configuration (`TRAINING_CONFIG`)
Controls the training process:
- `REWARDS`: Reward values for different game events
- `MAX_TRAINING_EPISODES`: Maximum number of training episodes
- `MAX_TIMESTEPS_PER_EPISODE`: Maximum steps per episode
- `EPISODES_PER_CHECKPOINT`: How often to save model checkpoints
- `LEARNING_RATE`: Learning rate for the optimizer
- `REPLAY_MEMORY_SIZE`: Size of the experience replay buffer
- `GAMMA`: Discount factor for future rewards
- `EPSILON_START`, `EPSILON_END`, `EPSILON_DECAY`: Parameters for exploration strategy
- `TARGET_UPDATE_FREQUENCY`: How often to update the target network
- `BATCH_SIZE`: Batch size for training
- `CLIP_GRADIENTS`: Maximum gradient norm for gradient clipping
- `PRINT_LOSS_EVERY`: How often to print loss values

## Testing

Run the test suite with:

```bash
pytest
```

Test results will be saved in JUnit XML format in the `tests/junit` directory, and coverage reports will be generated in the `tests/coverage.xml` file.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
