import pygame
import pygame_gui

from gui.interface import SchedulingSimulatorGUI

def main():
    pygame.init()
    pygame.display.set_caption('Scheduling Algorithms Simulator')
    window_size = (1000, 700)
    window_surface = pygame.display.set_mode(window_size)
    background = pygame.Surface(window_size)
    background.fill(pygame.Color('#222831'))

    manager = pygame_gui.UIManager(window_size)
    clock = pygame.time.Clock()

    gui = SchedulingSimulatorGUI(manager, window_size)

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            gui.process_event(event)

            manager.process_events(event)

        manager.update(time_delta)
        window_surface.blit(background, (0, 0))
        gui.draw(window_surface)
        manager.draw_ui(window_surface)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
