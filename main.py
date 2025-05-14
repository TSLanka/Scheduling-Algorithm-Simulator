import pygame
import pygame_gui
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.interface import MainWindow

def main():
    """Main entry point for the scheduling algorithms simulator"""
    pygame.init()
    pygame.display.set_caption('CPU Scheduling Algorithms Simulator')
    
    window_size = (1000, 700)
    window_surface = pygame.display.set_mode(window_size)
    background = pygame.Surface(window_size)
    background.fill(pygame.Color('#222831'))
    
    # Create theme file if it doesn't exist
    if not os.path.exists('theme.json'):
        with open('theme.json', 'w') as f:
            f.write('{"defaults": {"colours": {"normal_bg": "#393E46", "hovered_bg": "#00ADB5", "disabled_bg": "#303841", "selected_bg": "#00ADB5", "active_bg": "#00ADB5", "dark_bg": "#222831", "normal_text": "#EEEEEE", "hovered_text": "#EEEEEE", "selected_text": "#EEEEEE", "disabled_text": "#C6C6C6", "active_text": "#EEEEEE", "normal_border": "#00ADB5", "hovered_border": "#00FFF5", "disabled_border": "#303841", "selected_border": "#00FFF5", "active_border": "#00FFF5"}}}')
    
    # Create main window
    main_window = MainWindow(window_size)
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Pass events to the main window
            main_window.handle_event(event)
        
        # Update the UI
        main_window.update(time_delta)
        
        # Draw everything
        window_surface.blit(background, (0, 0))
        main_window.draw(window_surface)
        
        pygame.display.update()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()