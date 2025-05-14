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
        # Collect input and validate
        try:
            pid = self.input_fields['Process ID'].get_text()
            arrival = self.input_fields['Arrival Time'].get_text()
            burst = self.input_fields['Burst Time'].get_text()
            
            # Basic validation
            if not pid or not arrival or not burst:
                print("All fields must be filled")
                return
                
            # Convert to appropriate types
            arrival_time = int(arrival)
            burst_time = int(burst)
            
            if arrival_time < 0 or burst_time <= 0:
                print("Invalid time values: times must be non-negative and burst time must be positive")
                return
                
            # Check for additional fields based on algorithm
            process_data = {'pid': pid, 'arrival': arrival_time, 'burst': burst_time}
            
            if self.selected_algorithm in ['RM', 'EDF']:
                if 'Deadline' in self.input_fields and 'Period' in self.input_fields:
                    deadline = self.input_fields['Deadline'].get_text()
                    period = self.input_fields['Period'].get_text()
                    
                    if not deadline or not period:
                        print("Deadline and Period required for RM/EDF")
                        return
                        
                    process_data['deadline'] = int(deadline)
                    process_data['period'] = int(period)
                    
                    if process_data['deadline'] <= 0 or process_data['period'] <= 0:
                        print("Deadline and Period must be positive")
                        return
                else:
                    print("Deadline and Period fields required for RM/EDF")
                    return
                    
            # Add the process
            self.processes.append(process_data)
            
            # Clear input fields
            for field in self.input_fields.values():
                field.set_text("")
                
            print(f"Added process {pid}")
            
        except ValueError:
            print("Invalid input: please enter numeric values for times")
        except Exception as e:
            print(f"Error adding process: {str(e)}")

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
        if not self.simulation_results:
            return
            
        # Constants for drawing
        chart_x = self.visualization_rect.left + 20
        chart_y = self.visualization_rect.top + 20
        chart_width = self.visualization_rect.width - 40
        chart_height = 300
        
        # Find the total time to scale the chart
        total_time = max([p['completion_time'] for p in self.simulation_results])
        
        # Calculate time scale (pixels per time unit)
        time_scale = chart_width / max(total_time, 1)
        
        # Draw timeline
        pygame.draw.line(surface, (200, 200, 200), 
                         (chart_x, chart_y + chart_height + 10),
                         (chart_x + chart_width, chart_y + chart_height + 10), 2)
        
        # Draw processes
        job_height = 30
        job_spacing = 10
        
        for i, process in enumerate(self.simulation_results):
            color = [(50, 150, 255), (255, 100, 100), (100, 255, 100), 
                     (255, 255, 100), (255, 100, 255)][i % 5]
            
            y_pos = chart_y + i * (job_height + job_spacing)
            
            # Draw process label
            font = pygame.font.SysFont(None, 24)
            label = font.render(f"P{process['pid']}", True, (255, 255, 255))
            surface.blit(label, (chart_x - 40, y_pos + job_height // 2 - 10))
            
            # Draw execution blocks
            for execution in process['execution_intervals']:
                start_time, end_time = execution
                x_start = chart_x + start_time * time_scale
                width = (end_time - start_time) * time_scale
                
                pygame.draw.rect(surface, color, 
                                (x_start, y_pos, width, job_height))
                pygame.draw.rect(surface, (255, 255, 255), 
                                (x_start, y_pos, width, job_height), 1)
                
                # Draw time markers
                if width > 30:  # Only draw labels if there's enough space
                    time_label = font.render(f"{start_time}-{end_time}", True, (0, 0, 0))
                    surface.blit(time_label, (x_start + 5, y_pos + 5))
        
        # Draw metrics if available
        if hasattr(self, 'metrics'):
            metrics_y = chart_y + chart_height + 30
            font = pygame.font.SysFont(None, 24)
            metrics_text = [
                f"Average Waiting Time: {self.metrics['avg_waiting_time']:.2f}",
                f"Average Turnaround Time: {self.metrics['avg_turnaround_time']:.2f}",
                f"Average Response Time: {self.metrics['avg_response_time']:.2f}"
            ]
            
            for i, text in enumerate(metrics_text):
                label = font.render(text, True, (255, 255, 255))
                surface.blit(label, (chart_x, metrics_y + i * 25))
