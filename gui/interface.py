import pygame
import pygame_gui

class SchedulingSimulatorGUI:
    def __init__(self, manager, window_size):
        self.manager = manager
        self.window_size = window_size

        # Algorithm selection dropdown
        self.algorithms = ['FCFS', 'SJN', 'RR', 'RM', 'EDF']
        self.algorithm_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.algorithms,
            starting_option='FCFS',
            relative_rect=pygame.Rect((30, 30), (200, 40)),
            manager=self.manager
        )

        # Input fields for process/task info
        self.input_fields = {
            'Process ID': pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((30, 90), (100, 30)), manager=self.manager),
            'Arrival Time': pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((140, 90), (100, 30)), manager=self.manager),
            'Burst Time': pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((250, 90), (100, 30)), manager=self.manager),
            # Add more fields as needed (e.g., Deadline, Period)
        }

        # Buttons
        self.add_process_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((370, 90), (120, 30)),
            text='Add Process',
            manager=self.manager
        )
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((30, 140), (150, 40)),
            text='Start Simulation',
            manager=self.manager
        )

        # Visualization area (could be a surface or a placeholder rect)
        self.visualization_rect = pygame.Rect((30, 200), (900, 400))

        # Data
        self.processes = []
        self.selected_algorithm = 'FCFS'
        self.simulation_results = None

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.add_process_button:
                self.add_process()
            elif event.ui_element == self.start_button:
                self.start_simulation()
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.algorithm_dropdown:
                self.selected_algorithm = event.text

    def add_process(self):
        # Collect input, validate, and append to self.processes
        pid = self.input_fields['Process ID'].get_text()
        arrival = self.input_fields['Arrival Time'].get_text()
        burst = self.input_fields['Burst Time'].get_text()
        # Add validation here
        self.processes.append({'pid': pid, 'arrival': int(arrival), 'burst': int(burst)})
        # Clear fields if desired

    def start_simulation(self):
        # Import and run the selected algorithm from algorithms/
        from utils.metrics import calculate_metrics
        from algorithms import fcfs, sjn, rr, rm, edf

        algo_map = {
            'FCFS': fcfs.run,
            'SJN': sjn.run,
            'RR': rr.run,
            'RM': rm.run,
            'EDF': edf.run,
        }
        algorithm = algo_map[self.selected_algorithm]
        self.simulation_results = algorithm(self.processes)
        # Optionally, calculate metrics
        self.metrics = calculate_metrics(self.simulation_results)

    def draw(self, surface):
        # Draw the visualization area (e.g., Gantt chart)
        pygame.draw.rect(surface, (50, 50, 50), self.visualization_rect)
        if self.simulation_results:
            self.draw_gantt_chart(surface)

    def draw_gantt_chart(self, surface):
        # Implement your Gantt chart drawing here
        pass
