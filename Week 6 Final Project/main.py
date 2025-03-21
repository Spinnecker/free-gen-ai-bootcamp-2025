"""
Sombraportal - A Shadowgate-Inspired Spanish Learning Adventure Game
This game combines point-and-click adventure mechanics with Spanish language learning.
Players explore a mysterious castle while learning Spanish vocabulary and grammar.

Main Features:
- Point-and-click navigation
- Spanish language puzzles
- Interactive objects with Spanish commands
- Bilingual tooltips and descriptions
- Inventory system
"""

import pygame
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Initialize Pygame
pygame.init()

# Game Constants
WINDOW_WIDTH = 800  
WINDOW_HEIGHT = 600  
FPS = 60  

# Color Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
TOOLTIP_BG = (50, 50, 50)
INSTRUCTION_BG = (30, 30, 30)

# Instructions text
INSTRUCTIONS = [
    "Game Instructions:",
    "1. Click on objects to examine them",
    "2. Type Spanish commands in the text box:",
    "   - 'examinar' (examine)",
    "   - 'abrir' (open)",
    "   - 'usar' (use)",
    "   - 'leer' (read)",
    "3. Press H to toggle instructions",
    "4. Press ESC for menu"
]

class TextBox:
    """
    A text input box for entering Spanish commands.
    
    Attributes:
        rect (pygame.Rect): The rectangle defining the textbox's position and size
        text (str): The current text in the textbox
        active (bool): Whether the textbox is currently selected
        font (pygame.font.Font): The font used for rendering text
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initialize a new text input box.
        
        Args:
            x (int): X-coordinate of the box
            y (int): Y-coordinate of the box
            width (int): Width of the box
            height (int): Height of the box
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.font = pygame.font.Font(None, 32)

    def handle_event(self, event) -> Optional[str]:
        """
        Handle input events for the text box.
        
        Args:
            event: The pygame event to process
            
        Returns:
            Optional[str]: The entered text if Enter was pressed, None otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state based on if user clicked the input box
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                # Return the current text and clear the input box
                entered_text = self.text
                self.text = ""
                return entered_text
            elif event.key == pygame.K_BACKSPACE:
                # Remove the last character
                self.text = self.text[:-1]
            else:
                # Add the character to the text
                self.text += event.unicode
        return None

    def draw(self, screen):
        """
        Draw the text box on the screen.
        
        Args:
            screen: The pygame surface to draw on
        """
        # Draw the box outline (white if active, gray if inactive)
        color = WHITE if self.active else GRAY
        pygame.draw.rect(screen, color, self.rect, 2)
        
        # Render and draw the text
        text_surface = self.font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

class Game:
    """
    Main game class handling all game logic and rendering.
    
    Attributes:
        screen: The main game window
        clock: Pygame clock for controlling frame rate
        font/small_font: Fonts for rendering text
        current_room: The current room the player is in
        inventory: List of items the player has collected
        game_state: Current state of the game
        show_tooltip: Whether to show object tooltips
        show_english: Whether to show English translations
    """
    
    def __init__(self):
        """Initialize the game state and setup the display"""
        # Setup display and basic game components
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sombraportal")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state variables
        self.current_room = "entrance"  # Starting room
        self.inventory: List[str] = []  # Player's inventory
        self.game_state = "playing"  # Current game state
        self.show_tooltip = False  # Whether to show tooltips
        self.tooltip_text = ""  # Current tooltip text
        self.tooltip_pos = (0, 0)  # Position of current tooltip
        self.show_instructions = True  # Whether to show instructions
        
        # Load game data from JSON file
        self.load_game_data()
        
        # Create text input for Spanish commands
        self.text_input = TextBox(10, WINDOW_HEIGHT - 40, WINDOW_WIDTH - 20, 30)
        
        # Track solved puzzles
        self.solved_puzzles = set()
        
        # Message system
        self.messages: List[Dict[str, str]] = []
        self.message_timeout = 0

    def load_game_data(self):
        """Load room and object data from the game_data.json file"""
        try:
            with open('game_data.json', 'r', encoding='utf-8') as f:
                self.game_data = json.load(f)
        except FileNotFoundError:
            print("Error: game_data.json not found!")
            sys.exit(1)

    def handle_events(self) -> bool:
        """
        Process all game events (mouse, keyboard, etc.).
        
        Returns:
            bool: False if the game should quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)
                
            if event.type == pygame.MOUSEMOTION:
                self.update_tooltip(event.pos)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_menu()
                elif event.key == pygame.K_h:
                    self.show_instructions = not self.show_instructions
                    
            # Handle text input for Spanish commands
            command = self.text_input.handle_event(event)
            if command:
                self.process_command(command.lower())
                
        return True

    def handle_click(self, pos: Tuple[int, int]):
        """
        Process mouse clicks on game objects.
        
        Args:
            pos: The (x, y) position of the mouse click
        """
        room = self.game_data["rooms"][self.current_room]
        for obj in room["objects"]:
            rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
            if rect.collidepoint(pos):
                self.handle_object_interaction(obj)

    def handle_object_interaction(self, obj: Dict):
        """
        Process interaction with a game object.
        
        Args:
            obj: The object being interacted with
        """
        # Show object description
        desc = obj["interactions"].get("examinar", {})
        self.show_message(desc["text_es"])
        
        # Check for puzzle interactions
        if "puzzle" in obj:
            self.handle_puzzle(obj)

    def handle_puzzle(self, obj: Dict):
        """
        Process puzzle interactions and check for solutions.
        
        Args:
            obj: The puzzle object being interacted with
        """
        puzzle = obj["puzzle"]
        if puzzle["id"] not in self.solved_puzzles:
            if "required_item" in puzzle and puzzle["required_item"] in self.inventory:
                # Puzzle is solved
                self.solved_puzzles.add(puzzle["id"])
                self.show_message(puzzle["success_es"])
                
                # Give reward if any
                if "reward" in puzzle:
                    self.inventory.append(puzzle["reward"])
                    self.show_message(f"¡Has obtenido: {puzzle['reward']}!")
            else:
                # Show hint if puzzle not solved
                self.show_message(puzzle["hint_es"])

    def process_command(self, command: str):
        """
        Process Spanish text commands entered by the player.
        
        Args:
            command: The command text entered by the player
        """
        room = self.game_data["rooms"][self.current_room]
        for obj in room["objects"]:
            if command in obj["interactions"]:
                response = obj["interactions"][command]
                self.show_message(response["text_es"])

    def update_tooltip(self, pos: Tuple[int, int]):
        """
        Update the tooltip text and position based on mouse position.
        
        Args:
            pos: The current mouse position
        """
        room = self.game_data["rooms"][self.current_room]
        self.show_tooltip = False
        
        for obj in room["objects"]:
            rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
            if rect.collidepoint(pos):
                self.show_tooltip = True
                self.tooltip_text = obj['name_es']
                self.tooltip_pos = pos

    def show_message(self, text: str):
        """
        Display a message to the player.
        
        Args:
            text: The message text to display
        """
        self.messages.append({
            "text": text,
            "time": pygame.time.get_ticks()
        })
        if len(self.messages) > 3:  # Keep only last 3 messages
            self.messages.pop(0)

    def draw_instructions(self):
        """
        Draw the instructions panel on the screen.
        """
        if not self.show_instructions:
            return
            
        # Draw semi-transparent background
        instruction_surface = pygame.Surface((300, 250))
        instruction_surface.fill(INSTRUCTION_BG)
        instruction_surface.set_alpha(200)
        self.screen.blit(instruction_surface, (WINDOW_WIDTH - 310, 10))
        
        # Draw instructions text
        y = 20
        for line in INSTRUCTIONS:
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (WINDOW_WIDTH - 300, y))
            y += 25

    def draw_messages(self):
        """
        Draw the messages on the screen.
        """
        current_time = pygame.time.get_ticks()
        y = WINDOW_HEIGHT - 120
        
        for msg in self.messages:
            if current_time - msg["time"] < 5000:  # Show messages for 5 seconds
                text = self.small_font.render(msg["text"], True, WHITE)
                self.screen.blit(text, (10, y))
                y += 20

    def draw(self):
        """
        Render all game elements to the screen.
        """
        self.screen.fill(BLACK)
        
        # Draw room title
        room = self.game_data["rooms"][self.current_room]
        title_text = self.font.render(room["name"], True, WHITE)
        self.screen.blit(title_text, (10, 10))
        
        # Draw room description
        desc_text = self.small_font.render(room["description_es"], True, WHITE)
        self.screen.blit(desc_text, (10, 50))
        
        # Draw interactive objects
        for obj in room["objects"]:
            pygame.draw.rect(self.screen, WHITE, 
                           (obj["x"], obj["y"], obj["width"], obj["height"]), 2)
        
        # Draw tooltip
        if self.show_tooltip:
            tooltip_surface = self.small_font.render(self.tooltip_text, True, WHITE)
            pygame.draw.rect(self.screen, TOOLTIP_BG, 
                           (self.tooltip_pos[0], self.tooltip_pos[1] - 25,
                            tooltip_surface.get_width() + 10, 25))
            self.screen.blit(tooltip_surface, 
                           (self.tooltip_pos[0] + 5, self.tooltip_pos[1] - 20))
        
        # Draw inventory
        inventory_text = "Inventario: " + ", ".join(self.inventory)
        inv_surface = self.small_font.render(inventory_text, True, WHITE)
        self.screen.blit(inv_surface, (10, WINDOW_HEIGHT - 70))
        
        # Draw messages
        self.draw_messages()
        
        # Draw instructions panel
        self.draw_instructions()
        
        # Draw text input
        self.text_input.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        """
        Main game loop.
        """
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)

    def toggle_menu(self):
        """
        Toggle the game menu.
        """
        pass  # Not implemented

def main():
    """
    Entry point of the game.
    """
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
