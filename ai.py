from collections import deque
import random
import torch
import torch.nn as nn
import torch.optim as optim
import os
import math

# -------------------------------------------------
def reward(old_head: tuple, new_head: tuple, food: tuple, crashed: bool, ate_food: bool, steps_without_food: int = 0) -> float:
    if crashed:
        return -10.0
    if ate_food:
        return 10.0
    
    # progressive penalty for looping in circles without eating
    if steps_without_food > 60:
        return -0.5
        
    old_dist = abs(old_head[0] - food[0]) + abs(old_head[1] - food[1])
    new_dist = abs(new_head[0] - food[0]) + abs(new_head[1] - food[1])
    
    if new_dist < old_dist:
        return 0.15  
    else:
        return -0.25

# -------------------------------------------------
def get_state(snake: list, direction: str, food: tuple, width: int, height: int, space_size: int) -> list:
    head_x, head_y = snake[0]
    
    # base vectors
    DIR_UP    = (0, -space_size)
    DIR_DOWN  = (0, space_size)
    DIR_LEFT  = (-space_size, 0)
    DIR_RIGHT = (space_size, 0)
    
    if direction == "Up":
        forward, backward, left, right = DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
    elif direction == "Down":
        forward, backward, left, right = DIR_DOWN, DIR_UP, DIR_RIGHT, DIR_LEFT
    elif direction == "Left":
        forward, backward, left, right = DIR_LEFT, DIR_RIGHT, DIR_DOWN, DIR_UP
    elif direction == "Right":
        forward, backward, left, right = DIR_RIGHT, DIR_LEFT, DIR_UP, DIR_DOWN

    # Relative 8-directional layout:
    relative_directions = [
        forward,
        backward,
        left,
        right,
        (forward[0]+left[0], forward[1]+left[1]),
        (forward[0]+right[0], forward[1]+right[1]),
        (backward[0]+left[0], backward[1]+left[1]),
        (backward[0]+right[0], backward[1]+right[1])
    ]
    
    state = []
    for dx, dy in relative_directions:
        wall_dist = 0.0
        tail_dist = 0.0
        food_found = 0.0
        
        current_x = head_x
        current_y = head_y
        distance = 0.0
        found_tail = False
        
        while True:
            current_x += dx
            current_y += dy
            distance += 1.0 
            
            # wall hit
            if current_x < 0 or current_x >= width or current_y < 0 or current_y >= height:
                wall_dist = 1.0 / distance
                break
                
            # tail hit
            if not found_tail and (current_x, current_y) in snake[1:]:
                tail_dist = 1.0 / distance
                found_tail = True
                
            # yummers
            if (current_x, current_y) == food:
                food_found = 1.0
                
        state.extend([wall_dist, tail_dist, food_found])
        
    return state

# ---------------------------------------------------
class Network(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.linear3 = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.linear1(x))
        x = torch.relu(self.linear2(x))
        return self.linear3(x)
    
# ---------------------------------------------------
class Agent:
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr          
        self.gamma = gamma    
        self.memory = deque(maxlen=100_000) 
        
        self.loaded_games_count = 0 
        self.loaded_high_score = 0  
        
        if os.path.exists("snake_brain.pth"):
            try:
                checkpoint = torch.load("snake_brain.pth", weights_only=True)
                if isinstance(checkpoint, dict) and "model_state" in checkpoint:
                    self.model.load_state_dict(checkpoint["model_state"])
                    self.loaded_games_count = checkpoint.get("games_count", 0)
                    self.loaded_high_score = checkpoint.get("high_score", 0)
                else:
                    self.model.load_state_dict(checkpoint)
                    
                self.model.eval()
                print(f"🧠 Brain Loaded! Resuming from Game {self.loaded_games_count} | All-Time High Score Target: {self.loaded_high_score}")
            except Exception as e:
                print(f"Starting clean layout architecture model layer: {e}")
        else:
            print("🚀 Initialize a clean 24-input brain sequence.")
        
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def get_action(self, state, epsilon=80, games_counter=0):
        move = [0, 0, 0]
        
        
        if games_counter > 300:
            epsilon = 0 
            
        if random.randint(0, 200) < (epsilon - games_counter):
            move_idx = random.randint(0, 2)
            move[move_idx] = 1
        else:
            self.model.eval()  
            with torch.no_grad():  
                state_tensor = torch.tensor(state, dtype=torch.float)
                prediction = self.model(state_tensor)
                move_idx = torch.argmax(prediction).item()
                move[move_idx] = 1
                
        return move

    def agent_step(self, state, action, reward, next_state, done):
        self.model.train()
        if not isinstance(done, list) and not isinstance(done, tuple):
            state = [state]
            next_state = [next_state]
            action = [action]
            reward = [reward]
            done = [done]

        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        
        pred = self.model(state)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            action_idx = torch.argmax(action[idx]).item()
            target[idx][action_idx] = Q_new
            
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        self.optimizer.step()

    def train_long_memory(self, batch_size=1000):
        if len(self.memory) < batch_size:
            print(f"📦 Buffering memory bank... ({len(self.memory)}/{batch_size} states cached)")
            return
        mini_sample = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.agent_step(states, actions, rewards, next_states, dones)

    def save(self, games_count, high_score, filename="snake_brain.pth"):
        checkpoint = {
            "model_state": self.model.state_dict(),
            "games_count": games_count,
            "high_score": high_score  
        }
        torch.save(checkpoint, filename)