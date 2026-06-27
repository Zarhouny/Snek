import tkinter as tk
import random
from ai import Agent, Network, get_state, reward



brain = Network(input_size=24, hidden_size=512, output_size=3)
agent = Agent(model=brain, lr=0.0003, gamma=0.9)
games_count = agent.loaded_games_count

# GAME CONFIG ----------------------------------------
WIDTH, HEIGHT = 500, 500       
SPACE_SIZE = 20                
show_grid = True               
SNAKE_COLOR = "#00ff00"
FOOD_COLOR = "#ff0000"
BACKGROUND_COLOR = "#ffffff"
GRID_COLOR = "#cccccc"
AI_ENABLED = False             
SPEED_STEP = 2
infinite_space = False     
OUROBOROS_MODE = False         
# -------------------------------------------------

def invert_hex_color(hex_color):
    hex_color = hex_color.lstrip('#')
    color_int = int(hex_color, 16)
    inverted_int = 0xFFFFFF - color_int
    return f"#{inverted_int:06x}"


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title('Snek')
        self.root.resizable(False, False)
        
        self.canvas = tk.Canvas(root, bg='black', width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack()
        
        self.score_label = tk.Label(root, text="Score: 0", font=("Times New Roman", 14))
        self.score_label.pack()
        
        self.highest_score_ever = agent.loaded_high_score
        
        self.root.bind('<Left>', lambda event: self.change_direction('Left'))
        self.root.bind('<Right>', lambda event: self.change_direction('Right'))
        self.root.bind('<Up>', lambda event: self.change_direction('Up'))
        self.root.bind('<Down>', lambda event: self.change_direction('Down'))
        self.root.bind("<Return>", lambda event: self.start_game())
        self.root.bind("<space>", lambda event: self.reset())
        self.root.bind("<Escape>", lambda event: self.toggle_pause()) 
        
        self.loop_id = None 
        self.game_state = "MENU"
        self.start_menu()

    def check_win(self):
        max_score = (WIDTH // SPACE_SIZE) * (HEIGHT // SPACE_SIZE) - 3
        if self.score >= max_score:
            self.game_state = "GAME_OVER"
            self.canvas.create_text(WIDTH/2, HEIGHT/2 - 20, text='YOU WIN!', fill=invert_hex_color(BACKGROUND_COLOR), font=("Arial", 30, "bold"))
            self.canvas.create_text(WIDTH/2, HEIGHT/2 + 30, text="Press ENTER to Play Again", fill="gray", font=("Arial", 14))
            return True
        return False

    def start_menu(self):
        self.canvas.delete("all")
        self.game_state = "MENU"
        self.canvas.create_text(WIDTH/2, HEIGHT/2 - 30, text="Snek", fill="white", font=("Arial", 34, "bold"))
        self.canvas.create_text(WIDTH/2, HEIGHT/2 + 30, text="Press ENTER to Start", fill="white", font=("Arial", 16))

    def cancel_active_loop(self):
        if self.loop_id is not None:
            self.root.after_cancel(self.loop_id)
            self.loop_id = None

    def start_game(self):
        if self.game_state in ["MENU", "GAME_OVER"]:
            self.cancel_active_loop() 

            self.snake = [(100, 100), (100 - SPACE_SIZE, 100), (100 - 2 * SPACE_SIZE, 100)]
            self.direction = "Right"
            self.last_moved_direction = "Right" 
            self.input_queue = []
            
            self.score = 0
            self.steps_without_food = 0  
            self.score_label.config(text=f"Score: {self.score}")
            self.game_state = "PLAYING"
            
            self.spawn_food()
            self.game_loop()

    def reset(self):
        if self.game_state in ["PLAYING", "PAUSED"]:
            self.cancel_active_loop() 
            self.game_state = "MENU"
            self.start_game()

    def toggle_pause(self):
        if self.game_state == "PLAYING":
            self.game_state = "PAUSED"
            self.cancel_active_loop() 
            self.canvas.create_text(WIDTH/2, HEIGHT/2, text="PAUSED", fill=invert_hex_color(BACKGROUND_COLOR), font=("Arial", 30, "bold"), tags="pause_ui")
        elif self.game_state == "PAUSED":
            self.game_state = "PLAYING"
            self.canvas.delete("pause_ui")
            self.game_loop() 

    def draw_background(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BACKGROUND_COLOR, outline="")
        if show_grid:
            for x in range(0, WIDTH, SPACE_SIZE):
                self.canvas.create_line(x, 0, x, HEIGHT, fill=GRID_COLOR)
            for y in range(0, HEIGHT, SPACE_SIZE):
                self.canvas.create_line(0, y, WIDTH, y, fill=GRID_COLOR)

    def change_direction(self, new_dir):
        if self.game_state != "PLAYING" or AI_ENABLED:
            return

        if len(self.input_queue) >= 2:
            return

        reference_dir = self.input_queue[-1] if self.input_queue else self.direction
        opposites = {"Left": "Right", "Right": "Left", "Up": "Down", "Down": "Up"}
        if new_dir != opposites.get(reference_dir):
            self.input_queue.append(new_dir)

    def spawn_food(self):
        while True:
            x = random.randint(0, (WIDTH - SPACE_SIZE) // SPACE_SIZE) * SPACE_SIZE
            y = random.randint(0, (HEIGHT - SPACE_SIZE) // SPACE_SIZE) * SPACE_SIZE
            if (x, y) not in self.snake:
                self.food = (x, y)
                break

    def move(self):
        global games_count
        self.check_win()

        if AI_ENABLED:
            self.old_state = get_state(self.snake, self.direction, self.food, WIDTH, HEIGHT, SPACE_SIZE)
            self.final_move = agent.get_action(self.old_state, games_counter=games_count)
            
            clock_directions = ["Up", "Right", "Down", "Left"]
            current_idx = clock_directions.index(self.direction)
            
            if self.final_move == [1, 0, 0]:      
                next_dir = clock_directions[current_idx]
            elif self.final_move == [0, 1, 0]:    
                next_dir = clock_directions[(current_idx + 1) % 4]
            else:                                 
                next_dir = clock_directions[(current_idx - 1) % 4]
                
            self.direction = next_dir
        else:
            if self.input_queue:
                self.direction = self.input_queue.pop(0)

        head_x, head_y = self.snake[0]
        if self.direction == "Left": head_x -= SPACE_SIZE
        elif self.direction == "Right": head_x += SPACE_SIZE
        elif self.direction == "Up": head_y -= SPACE_SIZE
        elif self.direction == "Down": head_y += SPACE_SIZE

        self.last_moved_direction = self.direction
        
        if infinite_space:
            if head_x < 0: head_x = WIDTH - SPACE_SIZE
            elif head_x >= WIDTH: head_x = 0
            if head_y < 0: head_y = HEIGHT - SPACE_SIZE
            elif head_y >= HEIGHT: head_y = 0

        new_head = (head_x, head_y)
        self.snake.insert(0, new_head)

        self.ate_food = False
        if new_head == self.food:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.check_win()
            self.spawn_food()
            self.ate_food = True
            self.steps_without_food = 0
        else:
            self.snake.pop()
            if AI_ENABLED:
                self.steps_without_food += 1

    def check_collisions(self):
        head_x, head_y = self.snake[0]
        if not infinite_space:
            if head_x < 0 or head_x >= WIDTH or head_y < 0 or head_y >= HEIGHT:
                return True
        if not OUROBOROS_MODE and (head_x, head_y) in self.snake[1:]:
            return True
        return False

    def draw(self):
        self.canvas.delete("all")
        self.draw_background()
        
        fx, fy = self.food
        self.canvas.create_rectangle(fx, fy, fx+SPACE_SIZE, fy+SPACE_SIZE, fill=FOOD_COLOR)
        
        for x, y in self.snake[1:]:
            self.canvas.create_rectangle(x, y, x+SPACE_SIZE, y+SPACE_SIZE, fill=SNAKE_COLOR)
            
        hx, hy = self.snake[0]
        self.canvas.create_rectangle(hx, hy, hx+SPACE_SIZE, hy+SPACE_SIZE, fill=SNAKE_COLOR)
        
        eye_size = 3
        if self.direction == "Right":
            eye_coords = (hx + SPACE_SIZE - 6, hy + 4, hx + SPACE_SIZE - 6 + eye_size, hy + 4 + eye_size)
        elif self.direction == "Left":
            eye_coords = (hx + 6, hy + 4, hx + 6 + eye_size, hy + 4 + eye_size)
        elif self.direction == "Up":
            eye_coords = (hx + SPACE_SIZE - 6, hy + 6, hx + SPACE_SIZE - 6 + eye_size, hy + 6 + eye_size)
        elif self.direction == "Down":
            eye_coords = (hx + SPACE_SIZE - 6, hy + SPACE_SIZE - 6, hx + SPACE_SIZE - 6 + eye_size, hy + SPACE_SIZE - 6 + eye_size)

        self.canvas.create_rectangle(eye_coords, fill='black', outline="")

    def update_difficulty(self):
        if AI_ENABLED:
            return 1
        base_delay = 100
        speed_boost = (self.score // SPEED_STEP) * 10
        return max(40, base_delay - speed_boost)

    def game_loop(self):
        global games_count
        if self.game_state == "PLAYING":
            self.move()
            
            time_out = self.steps_without_food > 400
            crashed = self.check_collisions() or (AI_ENABLED and time_out)
            
            if AI_ENABLED:
                new_state = get_state(self.snake, self.direction, self.food, WIDTH, HEIGHT, SPACE_SIZE)
                
                step_reward = reward(self.snake[1], self.snake[0], self.food, crashed, self.ate_food, self.steps_without_food)
                if time_out:
                    step_reward = -10.0 
                
                agent.remember(self.old_state, self.final_move, step_reward, new_state, crashed)
                agent.agent_step(self.old_state, self.final_move, step_reward, new_state, crashed)

            if crashed:
                if AI_ENABLED:
                    games_count += 1
                    
                    # only train if we actually have enough memories in the ram to eliminate restart slump
                    if len(agent.memory) >= 1000:
                        agent.train_long_memory() 
                    else:
                        print(f"📥 Bootstrapping RAM Buffer... ({len(agent.memory)}/1000 steps gathered)")
                    
                    if self.score >= self.highest_score_ever:
                        self.highest_score_ever = self.score
                        agent.save(games_count, self.highest_score_ever)  
                        print(f"Game: {games_count} | 🏆 NEW ALL-TIME HIGH: {self.score} | Brain Locked! 💾")
                    else:
                        print(f"Game: {games_count} | Score: {self.score} | Target: {self.highest_score_ever}")
                    
                    self.game_state = "GAME_OVER"
                    self.start_game()
                else:
                    self.game_state = "GAME_OVER"
                    self.canvas.create_text(WIDTH/2, HEIGHT/2 - 20, text='GAME OVER', fill=invert_hex_color(BACKGROUND_COLOR), font=("Arial", 30, "bold"))
                    self.canvas.create_text(WIDTH/2, HEIGHT/2 + 30, text="Press ENTER to Play Again", fill="gray", font=("Arial", 14))
            else:
                self.draw()
                self.loop_id = self.root.after(self.update_difficulty(), self.game_loop)

window = tk.Tk()
game = Game(window)
window.mainloop()