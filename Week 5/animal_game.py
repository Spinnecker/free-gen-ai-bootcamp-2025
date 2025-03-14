"""
Animal Language Game - An educational game for learning animal names in Spanish

This game helps users learn Spanish animal names through an interactive card-matching game.
Features:
- 9 different animals with Spanish translations
- Multiple difficulty levels (Easy, Medium, Hard)
- Text-to-speech for both English and Spanish pronunciations
- Dynamic image loading from Unsplash
- Score tracking system
"""

import pygame
import os
from gtts import gTTS
import tempfile
import threading
import random
import urllib.request
from io import BytesIO
import time

# Initialize Pygame and its audio mixer
pygame.init()
pygame.mixer.init()

#######################
# Game Configuration #
#######################

# Display settings - using standard resolution metrics
INCH_TO_PIXELS = 96  # Standard screen resolution
CARD_WIDTH = int(INCH_TO_PIXELS * 1.35)  # Card size optimized for visibility
CARD_HEIGHT = int(INCH_TO_PIXELS * 1.35)
MARGIN = 25  # Space between cards and window edges
# Window dimensions calculated to fit 2x2 grid of cards plus margins and UI elements
WINDOW_WIDTH = (CARD_WIDTH * 2) + (MARGIN * 3)
WINDOW_HEIGHT = (CARD_HEIGHT * 2) + (MARGIN * 5) + 100

# Color palette for UI elements
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 180, 255)
DARK_BLUE = (20, 40, 80)  # Main background color
LIGHT_BLUE = (200, 230, 255)  # Alternative bright background

# Game difficulty settings and their characteristics
DIFFICULTIES = {
    "Easy": {
        "time_limit": None,        # No time pressure
        "spanish_only": False,     # Show both English and Spanish
        "points_correct": 1,       # Basic scoring
        "points_wrong": 0,         # No penalty
        "color": GREEN,
        "button_text": "Easy"
    },
    "Medium": {
        "time_limit": 10,         # 10 seconds per round
        "spanish_only": False,    # Still show both languages
        "points_correct": 2,      # Double points
        "points_wrong": -1,       # Small penalty
        "color": BLUE,
        "button_text": "Medium"
    },
    "Hard": {
        "time_limit": 5,          # 5 seconds per round
        "spanish_only": True,     # Spanish prompts only
        "points_correct": 3,      # Triple points
        "points_wrong": -2,       # Larger penalty
        "color": RED,
        "button_text": "Hard"
    }
}

# Load game sound effects
incorrect_sound = pygame.mixer.Sound(os.path.join("assets", "incorrect.wav"))

# Initialize game window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Animal Language Game")

# Dictionary of animals with their Spanish translations and image URLs
animals = {
    "Dog": {
        "spanish": "Perro",
        "images": [
            "https://images.unsplash.com/photo-1543466835-00a7907e9de1",
            "https://images.unsplash.com/photo-1587300003388-59208cc962cb",
            "https://images.unsplash.com/photo-1517849845537-4d257902454a",
            "https://images.unsplash.com/photo-1583511655826-05700442b728",
            "https://images.unsplash.com/photo-1477884213360-7e9d7dcc1e48"
        ]
    },
    "Cat": {
        "spanish": "Gato",
        "images": [
            "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba",
            "https://images.unsplash.com/photo-1573865526739-10659fec78a5",
            "https://images.unsplash.com/photo-1495360010541-f48722b34f7d",
            "https://images.unsplash.com/photo-1518791841217-8f162f1e1131",
            "https://images.unsplash.com/photo-1533743983669-94fa5c4338ec"
        ]
    },
    "Bird": {
        "spanish": "Pájaro",
        "images": [
            "https://images.unsplash.com/photo-1444464666168-49d633b86797",
            "https://images.unsplash.com/photo-1452570053594-1b985d6ea890",
            "https://images.unsplash.com/photo-1522926193341-e9ffd686c60f",
            "https://images.unsplash.com/photo-1444554791479-1955c61f0875",
            "https://images.unsplash.com/photo-1492011221367-f47e3ccd77a0"
        ]
    },
    "Fish": {
        "spanish": "Pez",
        "images": [
            "https://images.unsplash.com/photo-1524704796725-9fc3044a58b2",
            "https://images.unsplash.com/photo-1571752726703-5e7d1f6a986d",
            "https://images.unsplash.com/photo-1513040260736-63dd0617fb66",
            "https://images.unsplash.com/photo-1437622368342-7a3d73a34c8f",
            "https://images.unsplash.com/photo-1456846444593-5ff0c6ea8a12"
        ]
    },
    "Horse": {
        "spanish": "Caballo",
        "images": [
            "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a",
            "https://images.unsplash.com/photo-1534773728080-33d31da27ae5",
            "https://images.unsplash.com/photo-1593179449458-e0d43d512595",
            "https://images.unsplash.com/photo-1598974357801-cbca100e65d3",
            "https://images.unsplash.com/photo-1594768816441-1dd241ffaea4"
        ]
    },
    "Rabbit": {
        "spanish": "Conejo",
        "images": [
            "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308",
            "https://images.unsplash.com/photo-1535241749838-299277b6305f",
            "https://images.unsplash.com/photo-1452857297128-d9c29adba80b",
            "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308",
            "https://images.unsplash.com/photo-1518796745738-41048802f99a"
        ]
    },
    "Elephant": {
        "spanish": "Elefante",
        "images": [
            "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46",
            "https://images.unsplash.com/photo-1581852017103-68ac65514cf7",
            "https://images.unsplash.com/photo-1509909756405-be0199881695",
            "https://images.unsplash.com/photo-1564760055775-d63b17a55c44",
            "https://images.unsplash.com/photo-1503286666306-61c7ac3e6cc1"
        ]
    },
    "Lion": {
        "spanish": "León",
        "images": [
            "https://images.unsplash.com/photo-1546182990-dffeafbe841d",
            "https://images.unsplash.com/photo-1614027164847-1b28cfe1df60",
            "https://images.unsplash.com/photo-1585468274952-66591eb14165",
            "https://images.unsplash.com/photo-1534188753412-3e26d0d618d6",
            "https://images.unsplash.com/photo-1552410260-0fd9b577afa6"
        ]
    },
    "Monkey": {
        "spanish": "Mono",
        "images": [
            "https://images.unsplash.com/photo-1540573133985-87b6da6d54a9",
            "https://images.unsplash.com/photo-1554457945-ba5df6648602",
            "https://images.unsplash.com/photo-1463852247062-1bbca38f7805",
            "https://images.unsplash.com/photo-1516636052745-5827f6ca5aa7",
            "https://images.unsplash.com/photo-1463852247062-1bbca38f7805"
        ]
    }
}

class Card:
    """
    Represents a game card containing an animal image and its translations.
    
    Each card manages its own state (flipped/unflipped), image loading,
    and rendering. Images are loaded asynchronously to prevent game freezing.
    
    Attributes:
        rect (pygame.Rect): Position and size of the card
        animal_name (str): English name of the animal
        animal_data (dict): Associated Spanish translation and image URLs
        flipped (bool): Whether the card is showing its front or back
        image (pygame.Surface): The currently loaded animal image
        loading (bool): Whether the card is currently loading its image
        difficulty (str): Current game difficulty affecting card behavior
    """
    
    def __init__(self, x, y, animal_name, difficulty="Easy"):
        """Initialize a new card with position and animal information."""
        self.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        self.animal_name = animal_name
        self.animal_data = animals[animal_name]
        self.flipped = False
        self.image = None
        self.loading = True  # Start as loading
        self.current_image_url = None
        self.difficulty = difficulty
        self.load_new_image()
        
    def load_new_image(self):
        """
        Start loading a new random image for the card.
        Images are loaded asynchronously to prevent game freezing.
        """
        self.image = None
        self.loading = True
        self.current_image_url = random.choice(self.animal_data["images"])
        threading.Thread(target=self._load_image).start()
    
    def _load_image(self):
        """
        Load and process the image in a background thread.
        Handles image downloading, scaling, and conversion to Pygame surface.
        """
        try:
            response = urllib.request.urlopen(self.current_image_url)
            image_data = BytesIO(response.read())
            # Convert to pygame surface in main thread to avoid issues
            def convert_to_surface():
                try:
                    img = pygame.image.load(image_data)
                    # Scale image to fit card while maintaining aspect ratio
                    img_width = img.get_width()
                    img_height = img.get_height()
                    scale = min((CARD_WIDTH - 20) / img_width, (CARD_HEIGHT - 20) / img_height)
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    self.image = pygame.transform.scale(img, (new_width, new_height))
                except Exception as e:
                    print(f"Error converting image: {e}")
                    self.image = None
                self.loading = False
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"convert_image": convert_to_surface}))
        except Exception as e:
            print(f"Error loading image: {e}")
            self.loading = False
            self.image = None
        
    def draw(self, surface):
        """
        Render the card on the given surface.
        Handles different states: loading, flipped, and normal display.
        """
        # Draw card background
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, DIFFICULTIES[self.difficulty]["color"], self.rect, 2)
        
        if not self.flipped:
            if self.loading:
                # Draw loading indicator
                pygame.draw.rect(surface, GRAY, 
                               (self.rect.x + 10, self.rect.y + 10, 
                                CARD_WIDTH - 20, CARD_HEIGHT - 20))
                font = pygame.font.Font(None, 14)  # Reduced font size
                text = font.render("Loading...", True, BLACK)
                text_rect = text.get_rect(center=self.rect.center)
                surface.blit(text, text_rect)
            elif self.image:
                # Center the image on the card
                x = self.rect.x + (CARD_WIDTH - self.image.get_width()) // 2
                y = self.rect.y + (CARD_HEIGHT - self.image.get_height()) // 2
                surface.blit(self.image, (x, y))
            else:
                # Draw placeholder if image failed to load
                pygame.draw.rect(surface, GRAY, 
                               (self.rect.x + 10, self.rect.y + 10, 
                                CARD_WIDTH - 20, CARD_HEIGHT - 20))
                font = pygame.font.Font(None, 14)  # Reduced font size
                if DIFFICULTIES[self.difficulty]["spanish_only"]:
                    text = font.render(self.animal_data["spanish"], True, BLACK)
                else:
                    text = font.render(self.animal_name, True, BLACK)
                text_rect = text.get_rect(center=self.rect.center)
                surface.blit(text, text_rect)
        else:
            # Draw Spanish word when flipped
            font = pygame.font.Font(None, 14)  # Reduced font size
            text = font.render(self.animal_data["spanish"], True, BLACK)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

def play_audio(text, lang='en'):
    """
    Convert text to speech and play it using gTTS.
    
    Args:
        text (str): The text to convert to speech
        lang (str): Language code ('en' for English, 'es' for Spanish)
    """
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
            tts.save(temp_filename)
        
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        # Delete the temporary file after playing
        def cleanup():
            pygame.time.wait(2000)  # Wait for audio to finish
            os.unlink(temp_filename)
        
        threading.Thread(target=cleanup).start()
    except Exception as e:
        print(f"Error playing audio: {e}")

def main():
    """
    Main game loop handling game initialization, event processing, and rendering.
    
    Game Flow:
    1. Initialize game state and UI elements
    2. Create card grid and difficulty buttons
    3. Process user input (mouse clicks, key presses)
    4. Update game state (score, timer, card flips)
    5. Render everything to the screen
    6. Repeat until user exits
    """
    # Initialize game state
    current_difficulty = "Easy"  # Always start in Easy mode
    score = 0
    cards = []
    current_animal = None
    round_start_time = None
    
    # Create difficulty buttons - moved up by half inch
    button_width = 100
    button_height = 30
    button_margin = 10
    difficulty_buttons = {}
    total_buttons_width = (button_width + button_margin) * len(DIFFICULTIES) - button_margin
    start_x = (WINDOW_WIDTH - total_buttons_width) // 2
    buttons_y = WINDOW_HEIGHT - button_height - MARGIN - int(INCH_TO_PIXELS * 0.5)  # Moved up by 0.5 inch
    
    # Create label position above buttons
    label_y = buttons_y - 25  # Position label 25 pixels above buttons
    
    for i, diff_name in enumerate(DIFFICULTIES.keys()):
        x = start_x + i * (button_width + button_margin)
        difficulty_buttons[diff_name] = pygame.Rect(x, buttons_y, button_width, button_height)

    # Create end game button
    end_button = pygame.Rect(
        WINDOW_WIDTH - 100 - MARGIN,
        WINDOW_HEIGHT - button_height - MARGIN,
        100,
        button_height
    )

    # Initialize card positions in 2x2 grid
    available_animals = list(animals.keys())
    current_animals = random.sample(available_animals, 4)  # Select 4 random animals
    
    for i in range(2):  # 2 rows
        for j in range(2):  # 2 columns
            x = MARGIN + j * (CARD_WIDTH + MARGIN)
            y = MARGIN + i * (CARD_HEIGHT + MARGIN)
            animal_idx = i * 2 + j
            cards.append(Card(x, y, current_animals[animal_idx], current_difficulty))
    
    def start_new_round():
        nonlocal current_animal, round_start_time, current_animals, cards
        # Select new set of 4 random animals
        current_animals = random.sample(available_animals, 4)
        cards = []
        
        # Create new cards with new animals
        for i in range(2):
            for j in range(2):
                x = MARGIN + j * (CARD_WIDTH + MARGIN)
                y = MARGIN + i * (CARD_HEIGHT + MARGIN)
                animal_idx = i * 2 + j
                cards.append(Card(x, y, current_animals[animal_idx], current_difficulty))
        
        # Select new animal and play prompt
        current_animal = random.choice(current_animals)
        if DIFFICULTIES[current_difficulty]["spanish_only"]:
            play_audio(animals[current_animal]["spanish"], "es")
        else:
            play_audio(f"Find the {current_animal}")
        
        # Reset timer if needed
        if DIFFICULTIES[current_difficulty]["time_limit"]:
            round_start_time = time.time()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    while running:
        current_time = time.time()
        
        # Check time limit
        if round_start_time and DIFFICULTIES[current_difficulty]["time_limit"]:
            time_left = DIFFICULTIES[current_difficulty]["time_limit"] - (current_time - round_start_time)
            if time_left <= 0 and current_animal:
                score += DIFFICULTIES[current_difficulty]["points_wrong"]
                incorrect_sound.play()
                start_new_round()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.USEREVENT:
                # Handle image conversion in main thread
                if "convert_image" in event.dict:
                    event.dict["convert_image"]()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check difficulty buttons
                for diff_name, button in difficulty_buttons.items():
                    if button.collidepoint(event.pos):
                        current_difficulty = diff_name
                        score = 0
                        start_new_round()
                        break
                
                # Check end game button
                if end_button.collidepoint(event.pos):
                    running = False
                    continue
                
                # Handle card clicks
                for card in cards:
                    if card.rect.collidepoint(event.pos):
                        if not card.flipped and not card.loading:
                            card.flipped = True
                            if card.animal_name == current_animal:
                                score += DIFFICULTIES[current_difficulty]["points_correct"]
                                play_audio(animals[current_animal]["spanish"], "es")
                                pygame.time.wait(1000)  # Wait for pronunciation
                                current_animal = None
                                start_new_round()
                            else:
                                score += DIFFICULTIES[current_difficulty]["points_wrong"]
                                incorrect_sound.play()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not current_animal:
                    start_new_round()
        
        # Draw everything
        screen.fill(DARK_BLUE)  # Use dark blue background
        
        # Draw cards
        for card in cards:
            card.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 14)  # Reduced font size
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (MARGIN, WINDOW_HEIGHT - 50))
        
        # Draw timer if active
        if round_start_time and DIFFICULTIES[current_difficulty]["time_limit"]:
            time_left = max(0, DIFFICULTIES[current_difficulty]["time_limit"] - (current_time - round_start_time))
            timer_text = font.render(f"Time: {time_left:.1f}", True, WHITE)
            screen.blit(timer_text, (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 50))
        
        # Draw difficulty buttons
        font = pygame.font.Font(None, 24)  # Slightly larger font for the label
        label_text = font.render("Select Difficulty Level", True, WHITE)
        label_rect = label_text.get_rect(centerx=WINDOW_WIDTH // 2, y=label_y)
        screen.blit(label_text, label_rect)
        
        font = pygame.font.Font(None, 14)  # Reset font size for buttons
        for diff_name, button in difficulty_buttons.items():
            color = DIFFICULTIES[diff_name]["color"]
            pygame.draw.rect(screen, color, button)
            if diff_name == current_difficulty:
                pygame.draw.rect(screen, WHITE, button, 2)
            
            text = font.render(DIFFICULTIES[diff_name]["button_text"], True, BLACK)
            text_rect = text.get_rect(center=button.center)
            screen.blit(text, text_rect)
        
        # Draw end game button
        pygame.draw.rect(screen, RED, end_button)
        end_text = font.render("Exit", True, WHITE)
        text_rect = end_text.get_rect(center=end_button.center)
        screen.blit(end_text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
