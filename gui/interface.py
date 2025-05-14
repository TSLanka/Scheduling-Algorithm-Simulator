import pygame
import pygame_gui
from gui.components import ProcessTable, CustomButton
from algorithms import FCFS, SJN, RoundRobin, RateMonotonic, EarliestDeadlineFirst

class MainWindow:
    """Main application window for the Scheduling Simulator"""
    
    def __init__(self, window_size=(1000, 700)):
        self.window_size = window_size
        self.manager = pygame_gui.UIManager(window_size, theme_path='theme.json')
        
        # Initialize data structures
        self.processes = []
        self.selected_algorithm = 'FCFS'
        self.simulation_results = None
        self.time_quantum = 2  # Define time_quantum before setup_layout
        
        # Set up the main UI components
        self._setup_layout()
    
    def _setup_layout(self):
        """Set up the layout for the simulator interface"""
        # Header section
        self.header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((20, 10), (500, 30)),
            text="CPU Scheduling Algorithm Simulator",
            manager=self.manager
        )
        
        # Algorithm selection panel
        self.algorithm_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 50), (300, 100)),
            manager=self.manager
        )
        
        self.algorithm_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (280, 30)),
            text="Select Algorithm:",
            manager=self.manager,
            container=self.algorithm_panel
        )
        
        self.algorithm_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=['FCFS', 'SJN', 'Round Robin', 'Rate Monotonic', 'EDF'],
            starting_option='FCFS',
            relative_rect=pygame.Rect((10, 50), (280, 30)),
            manager=self.manager,
            container=self.algorithm_panel
        )
        
        # Process input panel
        self.process_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((330, 50), (650, 100)),
            manager=self.manager
        )
        
        self.process_id_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (80, 20)),
            text="Process ID:",
            manager=self.manager,
            container=self.process_panel
        )
        
        self.process_id_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((90, 10), (70, 20)),
            manager=self.manager,
            container=self.process_panel
        )
        
        self.arrival_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((170, 10), (100, 20)),  # Increased width to fix warning
            text="Arrival Time:",
            manager=self.manager,
            container=self.process_panel
        )
        
        self.arrival_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((270, 10), (70, 20)),  # Adjusted position
            manager=self.manager,
            container=self.process_panel
        )
        
        self.burst_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((350, 10), (80, 20)),  # Adjusted position
            text="Burst Time:",
            manager=self.manager,
            container=self.process_panel
        )
        
        self.burst_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((430, 10), (70, 20)),  # Adjusted position
            manager=self.manager,
            container=self.process_panel
        )
        
        self.deadline_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 40), (80, 20)),
            text="Deadline:",
            manager=self.manager,
            container=self.process_panel
        )
        
        self.deadline_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((90, 40), (70, 20)),
            manager=self.manager,
            container=self.process_panel
        )
        
        self.period_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((170, 40), (80, 20)),
            text="Period:",
            manager=self.manager,
            container=self.process_panel
        )
        
        self.period_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((250, 40), (70, 20)),
            manager=self.manager,
            container=self.process_panel
        )
        
        # Quantum input for Round Robin
        self.quantum_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((330, 40), (120, 20)),  # Increased width to fix warning
            text="Time Quantum:",
            manager=self.manager,
            container=self.process_panel,
            visible=False
        )
        
        self.quantum_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((450, 40), (70, 20)),  # Adjusted position
            manager=self.manager,
            container=self.process_panel,
            visible=False
        )
        self.quantum_input.set_text(str(self.time_quantum))
        
        # Add Process Button
        self.add_button = CustomButton(
            relative_rect=pygame.Rect((530, 10), (110, 50)),  # Adjusted position and size
            text="Add Process",
            manager=self.manager,
            container=self.process_panel,
            action_callback=self.add_process
        )
        
        # Process table
        self.process_table = ProcessTable(
            rect=pygame.Rect((20, 160), (960, 200)),
            manager=self.manager
        )
        
        # Simulation controls
        self.start_button = CustomButton(
            relative_rect=pygame.Rect((20, 370), (200, 40)),
            text="Start Simulation",
            manager=self.manager,
            action_callback=self.start_simulation
        )
        
        self.clear_button = CustomButton(
            relative_rect=pygame.Rect((230, 370), (200, 40)),
            text="Clear All",
            manager=self.manager,
            action_callback=self.clear_data
        )
        
        # Visualization area
        self.visualization_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((20, 420), (960, 260)),
            manager=self.manager
        )
        
        self.visualization_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (940, 20)),
            text="Visualization - Run simulation to see results",
            manager=self.manager,
            container=self.visualization_panel
        )
        
        # Results area inside visualization panel
        self.results_area = pygame.Rect((10, 40), (940, 210))
    
    def add_process(self):
        """Add a process to the simulation"""
        try:
            # Basic validation
            pid = self.process_id_input.get_text().strip()
            arrival = self.arrival_input.get_text().strip()
            burst = self.burst_input.get_text().strip()
            
            if not pid or not arrival or not burst:
                self._show_error("All fields must be filled")
                return
            
            # Convert to appropriate types
            arrival_time = int(arrival)
            burst_time = int(burst)
            
            if arrival_time < 0 or burst_time <= 0:
                self._show_error("Invalid time values")
                return
            
            # Create process data
            process_data = {
                'name': pid,  # Using 'name' as the key to match algorithm expectations
                'arrival': arrival_time,
                'burst': burst_time
            }
            
            # Check for real-time algorithms
            if self.selected_algorithm in ['Rate Monotonic', 'EDF']:
                deadline = self.deadline_input.get_text().strip()
                period = self.period_input.get_text().strip()
                
                if not deadline or not period:
                    self._show_error("Deadline and Period required for RM/EDF")
                    return
                
                deadline_time = int(deadline)
                period_time = int(period)
                
                if deadline_time <= 0 or period_time <= 0:
                    self._show_error("Deadline and Period must be positive")
                    return
                
                process_data['deadline'] = deadline_time
                process_data['period'] = period_time
            
            # Add the process to our list
            self.processes.append(process_data)
            
            # Update the process table
            self.process_table.add_process(process_data)
            
            # Clear input fields
            self.process_id_input.set_text("")
            self.arrival_input.set_text("")
            self.burst_input.set_text("")
            self.deadline_input.set_text("")
            self.period_input.set_text("")
            
        except ValueError:
            self._show_error("Invalid input: please enter numeric values for times")
    
    def start_simulation(self):
        """Start the scheduling simulation"""
        if not self.processes:
            self._show_error("No processes to simulate")
            return
        
        # Create appropriate algorithm instance
        algorithm = None
        if self.selected_algorithm == 'FCFS':
            algorithm = FCFS(self.processes)
        elif self.selected_algorithm == 'SJN':
            algorithm = SJN(self.processes)
        elif self.selected_algorithm == 'Round Robin':
            try:
                time_quantum = int(self.quantum_input.get_text())
                if time_quantum <= 0:
                    self._show_error("Time quantum must be positive")
                    return
                algorithm = RoundRobin(self.processes, time_quantum)
            except ValueError:
                self._show_error("Invalid time quantum")
                return
        elif self.selected_algorithm == 'Rate Monotonic':
            # Check if all processes have period defined
            for process in self.processes:
                if 'period' not in process or 'deadline' not in process:
                    self._show_error("All processes must have period and deadline for RM")
                    return
            algorithm = RateMonotonic(self.processes)
        elif self.selected_algorithm == 'EDF':
            # Check if all processes have deadline defined
            for process in self.processes:
                if 'deadline' not in process or 'period' not in process:
                    self._show_error("All processes must have deadline and period for EDF")
                    return
            algorithm = EarliestDeadlineFirst(self.processes)
        
        # Run the simulation
        self.simulation_results = algorithm.run()
        
        # Refresh the display
        self._update_visualization()
    
    def clear_data(self):
        """Clear all data and reset the simulation"""
        self.processes = []
        self.process_table._rebuild_table()
        self.simulation_results = None
        self.visualization_label.set_text("Visualization - Run simulation to see results")
    
    def _update_visualization(self):
        """Update the visualization area with simulation results"""
        if not self.simulation_results:
            return
        
        # Clear the visualization area
        self.visualization_label.set_text("Simulation Results:")
        
        # We'll need to draw directly onto the pygame surface
        # This can be done in the main loop using this data
    
    def _show_error(self, message):
        """Show an error message"""
        # In a real implementation, this would show a popup
        print(f"Error: {message}")
    
    def handle_event(self, event):
        """Handle pygame events"""
        self.manager.process_events(event)
        
        # Handle dropdown changes
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.algorithm_dropdown:
                self.selected_algorithm = event.text
                
                # Show/hide quantum input for Round Robin
                if self.selected_algorithm == 'Round Robin':
                    self.quantum_label.show()
                    self.quantum_input.show()
                else:
                    self.quantum_label.hide()
                    self.quantum_input.hide()
        
        # Handle button clicks
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.add_button.handle_event(event)
            self.start_button.handle_event(event)
            self.clear_button.handle_event(event)
        
        # Handle process table events
        self.process_table.handle_event(event)
    
    def update(self, time_delta):
        """Update the UI"""
        self.manager.update(time_delta)
    
    def draw(self, surface):
        """Draw the UI to the given surface"""
        self.manager.draw_ui(surface)
        
        # If we have simulation results, draw the Gantt chart
        if self.simulation_results:
            self._draw_gantt_chart(surface)
    
    def _draw_gantt_chart(self, surface):
        """Draw a Gantt chart of the simulation results"""
        # Get the gantt chart data
        gantt_data = self.simulation_results.get('gantt_chart', [])
        metrics = self.simulation_results.get('metrics', {})
        
        if not gantt_data:
            return
        
        # Prepare the chart area
        chart_area = pygame.Rect(
            self.visualization_panel.relative_rect.left + self.results_area.left,
            self.visualization_panel.relative_rect.top + self.results_area.top,
            self.results_area.width,
            self.results_area.height * 0.7
        )
        
        # Calculate the total duration for scaling
        total_time = self.simulation_results.get('total_time', 0)
        if total_time <= 0:
            total_time = max([end for _, _, end in gantt_data])
        
        # Calculate the scale for the time axis
        time_scale = chart_area.width / max(total_time, 1)
        
        # Draw the time axis
        pygame.draw.line(
            surface,
            pygame.Color(200, 200, 200),
            (chart_area.left, chart_area.bottom),
            (chart_area.right, chart_area.bottom),
            2
        )
        
        # Draw time markers
        font = pygame.font.Font(None, 20)
        for t in range(0, int(total_time) + 1, max(1, int(total_time // 10))):
            x = chart_area.left + t * time_scale
            pygame.draw.line(
                surface,
                pygame.Color(200, 200, 200),
                (x, chart_area.bottom),
                (x, chart_area.bottom + 5),
                1
            )
            time_text = font.render(str(t), True, pygame.Color(200, 200, 200))
            surface.blit(time_text, (x - 5, chart_area.bottom + 10))
        
        # Get unique process names
        process_names = set()
        for name, _, _ in gantt_data:
            process_names.add(name)
        
        # Generate colors for each process
        colors = {}
        for i, name in enumerate(process_names):
            # Generate a unique color for each process
            r = (i * 100 + 50) % 256
            g = (i * 150 + 100) % 256
            b = (i * 200 + 150) % 256
            colors[name] = pygame.Color(r, g, b)
        
        # Draw the Gantt chart bars
        bar_height = min(30, chart_area.height / max(len(process_names), 1))
        y_positions = {}
        
        current_y = chart_area.top
        for name in process_names:
            y_positions[name] = current_y
            
            # Draw process name
            name_text = font.render(name, True, pygame.Color(255, 255, 255))
            surface.blit(name_text, (chart_area.left - 50, current_y + bar_height / 2 - 10))
            
            current_y += bar_height + 5
        
        # Draw the execution bars
        for name, start, end in gantt_data:
            if name in y_positions:
                bar_rect = pygame.Rect(
                    chart_area.left + start * time_scale,
                    y_positions[name],
                    (end - start) * time_scale,
                    bar_height
                )
                
                pygame.draw.rect(surface, colors[name], bar_rect)
                pygame.draw.rect(surface, pygame.Color(255, 255, 255), bar_rect, 1)
                
                # If the bar is wide enough, show the time range
                if (end - start) * time_scale > 30:
                    time_text = font.render(f"{start}-{end}", True, pygame.Color(0, 0, 0))
                    text_rect = time_text.get_rect(center=bar_rect.center)
                    surface.blit(time_text, text_rect)
        
        # Draw metrics
        metrics_y = chart_area.bottom + 40
        metrics_text = []
        
        if 'avg_waiting' in metrics:
            metrics_text.append(f"Average Waiting Time: {metrics['avg_waiting']:.2f}")
        if 'avg_turnaround' in metrics:
            metrics_text.append(f"Average Turnaround Time: {metrics['avg_turnaround']:.2f}")
        if 'cpu_utilization' in metrics:
            metrics_text.append(f"CPU Utilization: {metrics['cpu_utilization']:.2f}%")
        if 'deadline_misses' in metrics:
            metrics_text.append(f"Deadline Misses: {metrics['deadline_misses']}")
            metrics_text.append(f"Miss Rate: {metrics.get('miss_rate', 0):.2f}%")
        
        for i, text in enumerate(metrics_text):
            label = font.render(text, True, pygame.Color(255, 255, 255))
            surface.blit(label, (chart_area.left, metrics_y + i * 25))