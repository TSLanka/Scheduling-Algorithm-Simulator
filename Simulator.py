import pygame
import sys
import threading
import heapq
import time
import math
from collections import deque
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CPU Scheduling Algorithm Visualizer")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Task colors
TASK_COLORS = [
    (255, 99, 71),    # Tomato
    (50, 205, 50),    # Lime Green
    (65, 105, 225),   # Royal Blue
    (255, 215, 0),    # Gold
    (138, 43, 226),   # Blue Violet
    (0, 206, 209),    # Dark Turquoise
    (255, 69, 0),     # Orange Red
    (34, 139, 34),    # Forest Green
    (0, 191, 255),    # Deep Sky Blue
    (255, 140, 0),    # Dark Orange
]

# Font
FONT_SMALL = pygame.font.SysFont("Arial", 16)
FONT_MEDIUM = pygame.font.SysFont("Arial", 20)
FONT_LARGE = pygame.font.SysFont("Arial", 24)
FONT_TITLE = pygame.font.SysFont("Arial", 30, bold=True)

class Task:
    def __init__(self, id, arrival_time, execution_time, deadline=None, period=None, priority=None):
        self.id = id
        self.arrival_time = arrival_time
        self.execution_time = execution_time
        self.remaining_time = execution_time
        self.deadline = deadline if deadline is not None else float('inf')
        self.period = period if period is not None else float('inf')
        self.priority = priority if priority is not None else 0
        
        # For metrics
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.color = TASK_COLORS[id % len(TASK_COLORS)]
        
        # For periodic tasks
        self.absolute_deadline = self.arrival_time + self.deadline if deadline is not None else float('inf')
        self.instances = []
        self.next_release = self.arrival_time
        
    def reset(self):
        self.remaining_time = self.execution_time
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.next_release = self.arrival_time
        self.absolute_deadline = self.arrival_time + self.deadline if self.deadline is not None else float('inf')
        self.instances = []

    def create_instance(self, release_time):
        instance = Task(
            self.id,
            release_time,
            self.execution_time,
            self.deadline,
            self.period,
            self.priority
        )
        instance.absolute_deadline = release_time + self.deadline if self.deadline is not None else float('inf')
        return instance

class TaskInstance:
    def __init__(self, task, release_time, instance_id):
        self.task = task
        self.id = task.id
        self.instance_id = instance_id
        self.release_time = release_time
        self.execution_time = task.execution_time
        self.remaining_time = task.execution_time
        self.deadline = task.deadline
        self.absolute_deadline = release_time + task.deadline if task.deadline is not None else float('inf')
        self.completion_time = 0
        self.color = task.color
    
    def __lt__(self, other):
        # For priority queue in EDF
        return self.absolute_deadline < other.absolute_deadline

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = FONT_MEDIUM.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = GRAY
        self.color_active = BLUE
        self.color = self.color_inactive
        self.text = text
        self.placeholder = placeholder
        self.txt_surface = FONT_MEDIUM.render(text, True, BLACK)
        self.active = False
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.unicode.isdigit() or event.unicode == '.':
                        self.text += event.unicode
                self.txt_surface = FONT_MEDIUM.render(self.text, True, BLACK)
                
    def update(self):
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width
        
    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
        if not self.text and not self.active:
            placeholder_surface = FONT_MEDIUM.render(self.placeholder, True, DARK_GRAY)
            screen.blit(placeholder_surface, (self.rect.x + 5, self.rect.y + 5))
    
    def get_value(self):
        try:
            if '.' in self.text:
                return float(self.text)
            else:
                return int(self.text) if self.text else 0
        except:
            return 0

class Checkbox:
    def __init__(self, x, y, text, checked=False):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.text = text
        self.checked = checked
        
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        if self.checked:
            pygame.draw.line(screen, BLACK, (self.rect.x + 4, self.rect.y + 10), 
                            (self.rect.x + 8, self.rect.y + 16), 3)
            pygame.draw.line(screen, BLACK, (self.rect.x + 8, self.rect.y + 16), 
                            (self.rect.x + 16, self.rect.y + 4), 3)
        
        text_surface = FONT_MEDIUM.render(self.text, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 30, self.rect.y))
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.checked = not self.checked
                return True
        return False

class Dropdown:
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected = options[0] if options else ""
        self.is_open = False
        self.option_rects = []
        
        for i, option in enumerate(options):
            self.option_rects.append(pygame.Rect(x, y + height * (i + 1), width, height))
            
    def draw(self, screen):
        # Draw dropdown box
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Draw selected option
        text_surface = FONT_MEDIUM.render(self.selected, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw arrow
        pygame.draw.polygon(screen, BLACK, [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 15, self.rect.centery + 5)
        ])
        
        # Draw options if dropdown is open
        if self.is_open:
            for i, option_rect in enumerate(self.option_rects):
                pygame.draw.rect(screen, WHITE, option_rect)
                pygame.draw.rect(screen, BLACK, option_rect, 2)
                
                option_text = FONT_MEDIUM.render(self.options[i], True, BLACK)
                option_text_rect = option_text.get_rect(center=option_rect.center)
                screen.blit(option_text, option_text_rect)
    
    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_open = not self.is_open
                return True
            
            if self.is_open:
                for i, option_rect in enumerate(self.option_rects):
                    if option_rect.collidepoint(pos):
                        self.selected = self.options[i]
                        self.is_open = False
                        return True
                
                # Click outside dropdown
                self.is_open = False
                return True
        
        return False
    

class Scheduler:
    def __init__(self):
        self.tasks = []
        self.task_instances = []  # For real-time algorithms with periodic tasks
        self.timeline = []  # List of (time, task_id) tuples
        self.current_time = 0
        self.cpu_utilization = 0
        self.total_wait_time = 0
        self.total_turnaround_time = 0
        self.missed_deadlines = 0
        self.quantum = 2  # For Round Robin
        
    def add_task(self, task):
        self.tasks.append(task)
        
    def reset(self):
        self.current_time = 0
        self.timeline = []
        self.cpu_utilization = 0
        self.total_wait_time = 0
        self.total_turnaround_time = 0
        self.missed_deadlines = 0
        self.task_instances = []
        
        for task in self.tasks:
            task.reset()
            
    def calculate_metrics(self):
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return 0, 0, 0, 0
        
        idle_time = 0
        for i in range(len(self.timeline) - 1):
            current_end = self.timeline[i][0] + self.timeline[i][2]
            next_start = self.timeline[i + 1][0]
            if next_start > current_end:
                idle_time += next_start - current_end
        
        makespan = self.timeline[-1][0] + self.timeline[-1][2] if self.timeline else 0
        self.cpu_utilization = ((makespan - idle_time) / makespan) * 100 if makespan > 0 else 0
        
        for task in self.tasks:
            if task.completion_time > 0:  # Task was completed
                task.turnaround_time = task.completion_time - task.arrival_time
                task.waiting_time = task.turnaround_time - task.execution_time
                self.total_wait_time += task.waiting_time
                self.total_turnaround_time += task.turnaround_time
        
        avg_wait_time = self.total_wait_time / total_tasks
        avg_turnaround_time = self.total_turnaround_time / total_tasks
        
        return self.cpu_utilization, avg_wait_time, avg_turnaround_time, self.missed_deadlines
        
    def run_fcfs(self):
        self.reset()
        ready_queue = []
        completed_tasks = 0
        
        # Sort tasks by arrival time
        sorted_tasks = sorted(self.tasks, key=lambda x: x.arrival_time)
        
        while completed_tasks < len(sorted_tasks):
            # Check for newly arrived tasks
            for task in sorted_tasks:
                if task.arrival_time <= self.current_time and task.remaining_time > 0 and task not in ready_queue:
                    ready_queue.append(task)
            
            if ready_queue:
                current_task = ready_queue[0]
                execution_time = current_task.remaining_time
                
                # Add to timeline
                self.timeline.append((self.current_time, current_task.id, execution_time))
                
                # Update times
                self.current_time += execution_time
                current_task.remaining_time = 0
                current_task.completion_time = self.current_time
                
                # Remove from ready queue
                ready_queue.pop(0)
                completed_tasks += 1
            else:
                # No tasks ready, advance time to next arrival
                next_arrival = min([t.arrival_time for t in sorted_tasks if t.remaining_time > 0])
                self.current_time = max(self.current_time, next_arrival)
        
        return self.calculate_metrics()
    
    def run_sjn(self):
        self.reset()
        ready_queue = []
        completed_tasks = 0
        
        # Sort tasks by arrival time initially
        sorted_tasks = sorted(self.tasks, key=lambda x: x.arrival_time)
        
        while completed_tasks < len(sorted_tasks):
            # Check for newly arrived tasks
            for task in sorted_tasks:
                if task.arrival_time <= self.current_time and task.remaining_time > 0 and task not in ready_queue:
                    ready_queue.append(task)
            
            if ready_queue:
                # Sort ready queue by execution time (shortest job next)
                ready_queue.sort(key=lambda x: x.execution_time)
                
                current_task = ready_queue[0]
                execution_time = current_task.remaining_time
                
                # Add to timeline
                self.timeline.append((self.current_time, current_task.id, execution_time))
                
                # Update times
                self.current_time += execution_time
                current_task.remaining_time = 0
                current_task.completion_time = self.current_time
                
                # Remove from ready queue
                ready_queue.pop(0)
                completed_tasks += 1
            else:
                # No tasks ready, advance time to next arrival
                next_arrival = min([t.arrival_time for t in sorted_tasks if t.remaining_time > 0])
                self.current_time = max(self.current_time, next_arrival)
        
        return self.calculate_metrics()
    
    def run_round_robin(self):
        self.reset()
        ready_queue = deque()
        completed_tasks = 0
        
        # Sort tasks by arrival time initially
        sorted_tasks = sorted(self.tasks, key=lambda x: x.arrival_time)
        
        while completed_tasks < len(sorted_tasks):
            # Check for newly arrived tasks
            for task in sorted_tasks:
                if task.arrival_time <= self.current_time and task.remaining_time > 0 and task not in ready_queue:
                    ready_queue.append(task)
            
            if ready_queue:
                current_task = ready_queue.popleft()
                execution_time = min(self.quantum, current_task.remaining_time)
                
                # Add to timeline
                self.timeline.append((self.current_time, current_task.id, execution_time))
                
                # Update times
                self.current_time += execution_time
                current_task.remaining_time -= execution_time
                
                if current_task.remaining_time > 0:
                    # Check for any new arrivals during this quantum
                    for task in sorted_tasks:
                        if (task.arrival_time > self.current_time - execution_time and 
                            task.arrival_time <= self.current_time and 
                            task.remaining_time > 0 and 
                            task not in ready_queue and 
                            task != current_task):
                            ready_queue.append(task)
                    
                    # Put back in queue
                    ready_queue.append(current_task)
                else:
                    current_task.completion_time = self.current_time
                    completed_tasks += 1
            else:
                # No tasks ready, advance time to next arrival
                remaining_tasks = [t for t in sorted_tasks if t.remaining_time > 0]
                if remaining_tasks:
                    next_arrival = min([t.arrival_time for t in remaining_tasks])
                    self.current_time = max(self.current_time, next_arrival)
                else:
                    break  # All tasks completed
        
        return self.calculate_metrics()

    def run_rate_monotonic(self, simulation_time=100):
        self.reset()
        
        # Check schedulability condition for RM
        n = len(self.tasks)
        utilization = sum(task.execution_time / task.period for task in self.tasks)
        utilization_bound = n * (2**(1/n) - 1)
        is_schedulable = utilization <= utilization_bound
        
        if not is_schedulable:
            print(f"Warning: Task set may not be schedulable under RM. Utilization: {utilization}, Bound: {utilization_bound}")
        
        # Initialize task instances
        active_tasks = []
        
        # Simulation loop
        while self.current_time < simulation_time:
            # Check for new task releases
            for task in self.tasks:
                if self.current_time >= task.next_release:
                    # Create a new instance
                    instance = TaskInstance(task, task.next_release, len(task.instances))
                    task.instances.append(instance)
                    active_tasks.append(instance)
                    # Schedule next release
                    task.next_release += task.period
            
            # Sort active tasks by period (rate monotonic)
            active_tasks.sort(key=lambda x: x.task.period)
            
            if active_tasks:
                # Select task with shortest period
                current_instance = active_tasks[0]
                
                # Determine how long this task runs
                time_to_next_release = float('inf')
                for task in self.tasks:
                    if task.next_release > self.current_time:
                        time_to_next_release = min(time_to_next_release, task.next_release - self.current_time)
                
                execution_time = min(current_instance.remaining_time, time_to_next_release)
                
                # Add to timeline
                self.timeline.append((self.current_time, current_instance.id, execution_time))
                
                # Update times
                self.current_time += execution_time
                current_instance.remaining_time -= execution_time
                
                # Check if instance completed
                if current_instance.remaining_time <= 0:
                    current_instance.completion_time = self.current_time
                    active_tasks.remove(current_instance)
                    
                    # Check if deadline was missed
                    if current_instance.completion_time > current_instance.absolute_deadline:
                        self.missed_deadlines += 1
            else:
                # Find next release time
                next_release = min([task.next_release for task in self.tasks])
                self.current_time = next_release
        
        return self.calculate_metrics()
    
    def run_edf(self, simulation_time=100):
        self.reset()
        
        # Check schedulability condition for EDF
        utilization = sum(task.execution_time / task.period for task in self.tasks)
        is_schedulable = utilization <= 1.0
        
        if not is_schedulable:
            print(f"Warning: Task set may not be schedulable under EDF. Utilization: {utilization}")
        
        # Priority queue for EDF (sorted by absolute deadline)
        active_tasks = []
        
        # Simulation loop
        while self.current_time < simulation_time:
            # Check for new task releases
            for task in self.tasks:
                if self.current_time >= task.next_release:
                    # Create a new instance
                    instance = TaskInstance(task, task.next_release, len(task.instances))
                    task.instances.append(instance)
                    heapq.heappush(active_tasks, instance)  # Push to priority queue
                    # Schedule next release
                    task.next_release += task.period
            
            if active_tasks:
                # Get task with earliest deadline
                current_instance = heapq.heappop(active_tasks)
                
                # Determine how long this task runs
                time_to_next_release = float('inf')
                for task in self.tasks:
                    if task.next_release > self.current_time:
                        time_to_next_release = min(time_to_next_release, task.next_release - self.current_time)
                
                execution_time = min(current_instance.remaining_time, time_to_next_release)
                
                # Add to timeline
                self.timeline.append((self.current_time, current_instance.id, execution_time))
                
                # Update times
                self.current_time += execution_time
                current_instance.remaining_time -= execution_time
                
                # Check if instance completed
                if current_instance.remaining_time <= 0:
                    current_instance.completion_time = self.current_time
                    
                    # Check if deadline was missed
                    if current_instance.completion_time > current_instance.absolute_deadline:
                        self.missed_deadlines += 1
                else:
                    # Put back in queue
                    heapq.heappush(active_tasks, current_instance)
            else:
                # Find next release time
                next_release = min([task.next_release for task in self.tasks])
                self.current_time = next_release
        
        return self.calculate_metrics()

class SchedulerVisualizer:
    def __init__(self):
        self.scheduler = Scheduler()
        self.current_algorithm = "FCFS"
        self.task_count = 0
        self.simulation_speed = 1
        self.is_simulating = False
        self.simulation_thread = None
        self.simulation_complete = False
        self.comparison_mode = False
        self.comparison_results = {}
        
        # UI state
        self.state = "MAIN_MENU"  # MAIN_MENU, TASK_INPUT, SIMULATION, COMPARISON
        
        # Task input fields
        self.arrival_time_input = InputBox(350, 200, 100, 30, "", "Arrival Time")
        self.execution_time_input = InputBox(350, 250, 100, 30, "", "Execution Time")
        self.deadline_input = InputBox(350, 300, 100, 30, "", "Deadline")
        self.period_input = InputBox(350, 350, 100, 30, "", "Period")
        self.priority_input = InputBox(350, 400, 100, 30, "", "Priority")
        self.quantum_input = InputBox(350, 450, 100, 30, str(self.scheduler.quantum), "Quantum")
        
        # Input fields for comparison
        self.sim_time_input = InputBox(600, 400, 100, 30, "100", "Sim Time")
        
        # Buttons
        self.add_task_button = Button(500, 320, 150, 40, "Add Task", BLUE, CYAN)
        self.start_sim_button = Button(500, 400, 200, 40, "Start Simulation", GREEN, (100, 255, 100))
        self.back_button = Button(50, HEIGHT - 70, 120, 40, "Back", GRAY, LIGHT_GRAY)
        self.compare_button = Button(WIDTH - 200, HEIGHT - 70, 150, 40, "Compare Algorithms", ORANGE, (255, 200, 0))
        self.reset_button = Button(WIDTH // 2 - 60, HEIGHT - 70, 120, 40, "Reset", RED, (255, 100, 100))
        
        # Algorithm selection
        self.algorithm_dropdown = Dropdown(50, 120, 200, 40, ["FCFS", "SJN", "Round Robin", "Rate Monotonic", "EDF"])
        
        # Checkboxes for comparison
        self.fcfs_checkbox = Checkbox(50, 200, "FCFS", True)
        self.sjn_checkbox = Checkbox(50, 240, "SJN", True)
        self.rr_checkbox = Checkbox(50, 280, "Round Robin", True)
        self.rm_checkbox = Checkbox(50, 320, "Rate Monotonic", True)
        self.edf_checkbox = Checkbox(50, 360, "EDF", True)
        
        # Timeline visualization params
        self.timeline_start_x = 50
        self.timeline_start_y = 500
        self.timeline_width = WIDTH - 100
        self.timeline_height = 50
        self.timeline_max_time = 50  # Adjustable based on tasks
        self.zoom_level = 1.0
        
    def add_task(self):
        arrival_time = self.arrival_time_input.get_value()
        execution_time = self.execution_time_input.get_value()
        deadline = self.deadline_input.get_value() if self.deadline_input.text else None
        period = self.period_input.get_value() if self.period_input.text else None
        priority = self.priority_input.get_value() if self.priority_input.text else None
        
        if execution_time <= 0:
            return False
        
        task = Task(self.task_count, arrival_time, execution_time, deadline, period, priority)
        self.scheduler.add_task(task)
        self.task_count += 1
        
        # Clear input fields
        self.arrival_time_input.text = ""
        self.arrival_time_input.txt_surface = FONT_MEDIUM.render("", True, BLACK)
        self.execution_time_input.text = ""
        self.execution_time_input.txt_surface = FONT_MEDIUM.render("", True, BLACK)
        self.deadline_input.text = ""
        self.deadline_input.txt_surface = FONT_MEDIUM.render("", True, BLACK)
        self.period_input.text = ""
        self.period_input.txt_surface = FONT_MEDIUM.render("", True, BLACK)
        self.priority_input.text = ""
        self.priority_input.txt_surface = FONT_MEDIUM.render("", True, BLACK)
        
        return True
    
    def start_simulation(self):
        if not self.scheduler.tasks:
            return
        
        self.scheduler.quantum = int(self.quantum_input.get_value()) if self.quantum_input.text else 2
        self.current_algorithm = self.algorithm_dropdown.selected
        self.is_simulating = True
        self.simulation_complete = False
        
        # Start simulation in a separate thread
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def run_simulation(self):
        if self.current_algorithm == "FCFS":
            self.scheduler.run_fcfs()
        elif self.current_algorithm == "SJN":
            self.scheduler.run_sjn()
        elif self.current_algorithm == "Round Robin":
            self.scheduler.run_round_robin()
        elif self.current_algorithm == "Rate Monotonic":
            sim_time = int(self.sim_time_input.get_value()) if self.sim_time_input.text else 100
            self.scheduler.run_rate_monotonic(sim_time)
        elif self.current_algorithm == "EDF":
            sim_time = int(self.sim_time_input.get_value()) if self.sim_time_input.text else 100
            self.scheduler.run_edf(sim_time)
        
        self.simulation_complete = True
        self.timeline_max_time = max([segment[0] + segment[2] for segment in self.scheduler.timeline]) if self.scheduler.timeline else 50
    
    def run_comparison(self):
        sim_time = int(self.sim_time_input.get_value()) if self.sim_time_input.text else 100
        self.comparison_results = {}
        
        if self.fcfs_checkbox.checked:
            self.scheduler.reset()
            cpu_util, avg_wait, avg_turnaround, missed = self.scheduler.run_fcfs()
            self.comparison_results["FCFS"] = {
                "CPU Utilization": cpu_util,
                "Average Wait Time": avg_wait,
                "Average Turnaround Time": avg_turnaround,
                "Missed Deadlines": missed
            }
        
        if self.sjn_checkbox.checked:
            self.scheduler.reset()
            cpu_util, avg_wait, avg_turnaround, missed = self.scheduler.run_sjn()
            self.comparison_results["SJN"] = {
                "CPU Utilization": cpu_util,
                "Average Wait Time": avg_wait,
                "Average Turnaround Time": avg_turnaround,
                "Missed Deadlines": missed
            }
            
        if self.rr_checkbox.checked:
            self.scheduler.reset()
            cpu_util, avg_wait, avg_turnaround, missed = self.scheduler.run_round_robin()
            self.comparison_results["Round Robin"] = {
                "CPU Utilization": cpu_util,
                "Average Wait Time": avg_wait,
                "Average Turnaround Time": avg_turnaround,
                "Missed Deadlines": missed
            }
            
        if self.rm_checkbox.checked:
            self.scheduler.reset()
            cpu_util, avg_wait, avg_turnaround, missed = self.scheduler.run_rate_monotonic(sim_time)
            self.comparison_results["Rate Monotonic"] = {
                "CPU Utilization": cpu_util,
                "Average Wait Time": avg_wait,
                "Average Turnaround Time": avg_turnaround,
                "Missed Deadlines": missed
            }
            
        if self.edf_checkbox.checked:
            self.scheduler.reset()
            cpu_util, avg_wait, avg_turnaround, missed = self.scheduler.run_edf(sim_time)
            self.comparison_results["EDF"] = {
                "CPU Utilization": cpu_util,
                "Average Wait Time": avg_wait,
                "Average Turnaround Time": avg_turnaround,
                "Missed Deadlines": missed
            }
        
        self.state = "COMPARISON"
        
    def draw_main_menu(self, screen):
        # Title
        title = FONT_TITLE.render("CPU Scheduling Algorithm Visualizer", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        # Instructions
        instructions = FONT_MEDIUM.render("Select an algorithm and add tasks to simulate", True, BLACK)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 80))
        
        # Algorithm selector
        alg_label = FONT_MEDIUM.render("Algorithm:", True, BLACK)
        screen.blit(alg_label, (50, 120 - 30))
        self.algorithm_dropdown.draw(screen)
        
        # Task list
        tasks_title = FONT_MEDIUM.render("Task List:", True, BLACK)
        screen.blit(tasks_title, (50, 200))
        
        if not self.scheduler.tasks:
            no_tasks = FONT_MEDIUM.render("No tasks added yet", True, DARK_GRAY)
            screen.blit(no_tasks, (50, 230))
        else:
            y_offset = 230
            for i, task in enumerate(self.scheduler.tasks):
                task_text = f"Task {task.id}: Arrival={task.arrival_time}, Exec={task.execution_time}"
                if task.deadline is not None:
                    task_text += f", Deadline={task.deadline}"
                if task.period is not None:
                    task_text += f", Period={task.period}"
                if task.priority is not None:
                    task_text += f", Priority={task.priority}"
                    
                task_surface = FONT_SMALL.render(task_text, True, BLACK)
                screen.blit(task_surface, (50, y_offset))
                y_offset += 25
        
        # Add task section
        add_task_title = FONT_MEDIUM.render("Add New Task:", True, BLACK)
        screen.blit(add_task_title, (350, 160))
        
        arrival_label = FONT_SMALL.render("Arrival Time:", True, BLACK)
        screen.blit(arrival_label, (350, 200 - 20))
        self.arrival_time_input.draw(screen)
        
        execution_label = FONT_SMALL.render("Execution Time:", True, BLACK)
        screen.blit(execution_label, (350, 250 - 20))
        self.execution_time_input.draw(screen)
        
        deadline_label = FONT_SMALL.render("Deadline (optional):", True, BLACK)
        screen.blit(deadline_label, (350, 300 - 20))
        self.deadline_input.draw(screen)
        
        period_label = FONT_SMALL.render("Period (optional):", True, BLACK)
        screen.blit(period_label, (350, 350 - 20))
        self.period_input.draw(screen)
        
        priority_label = FONT_SMALL.render("Priority (optional):", True, BLACK)
        screen.blit(priority_label, (350, 400 - 20))
        self.priority_input.draw(screen)
        
        # Only show quantum input for Round Robin
        if self.algorithm_dropdown.selected == "Round Robin":
            quantum_label = FONT_SMALL.render("Time Quantum:", True, BLACK)
            screen.blit(quantum_label, (350, 450 - 20))
            self.quantum_input.draw(screen)
        
        # Only show simulation time for real-time algorithms
        if self.algorithm_dropdown.selected in ["Rate Monotonic", "EDF"]:
            sim_time_label = FONT_SMALL.render("Simulation Time:", True, BLACK)
            screen.blit(sim_time_label, (600, 400 - 20))
            self.sim_time_input.draw(screen)
        
        # Buttons
        self.add_task_button.draw(screen)
        self.start_sim_button.draw(screen)
        self.compare_button.draw(screen)
        
    def draw_simulation(self, screen):
        # Title with algorithm name
        title = FONT_TITLE.render(f"{self.current_algorithm} Simulation", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        # Timeline visualization
        self.draw_timeline(screen)
        
        # Metrics
        if self.simulation_complete:
            cpu_util, avg_wait, avg_turnaround, missed_deadlines = self.scheduler.calculate_metrics()
            
            metrics_y = 100
            cpu_text = FONT_MEDIUM.render(f"CPU Utilization: {cpu_util:.2f}%", True, BLACK)
            screen.blit(cpu_text, (50, metrics_y))
            
            wait_text = FONT_MEDIUM.render(f"Average Wait Time: {avg_wait:.2f}", True, BLACK)
            screen.blit(wait_text, (50, metrics_y + 30))
            
            turnaround_text = FONT_MEDIUM.render(f"Average Turnaround Time: {avg_turnaround:.2f}", True, BLACK)
            screen.blit(turnaround_text, (50, metrics_y + 60))
            
            if self.current_algorithm in ["Rate Monotonic", "EDF"]:
                deadline_text = FONT_MEDIUM.render(f"Missed Deadlines: {missed_deadlines}", True, BLACK)
                screen.blit(deadline_text, (50, metrics_y + 90))
        elif self.is_simulating:
            simulating_text = FONT_MEDIUM.render("Simulating...", True, BLACK)
            screen.blit(simulating_text, (50, 100))
        
        # Buttons
        self.back_button.draw(screen)
        self.reset_button.draw(screen)
    
    def draw_timeline(self, screen):
        # Draw timeline axis
        pygame.draw.line(screen, BLACK, 
                        (self.timeline_start_x, self.timeline_start_y), 
                        (self.timeline_start_x + self.timeline_width, self.timeline_start_y), 
                        3)
        
        # Draw ticks and labels
        visible_time_range = self.timeline_max_time / self.zoom_level
        tick_interval = max(1, int(visible_time_range / 20))  # Adjust based on zoom
        
        for i in range(0, int(visible_time_range) + tick_interval, tick_interval):
            x_pos = self.timeline_start_x + (i / visible_time_range) * self.timeline_width
            
            # Draw tick
            pygame.draw.line(screen, BLACK, (x_pos, self.timeline_start_y - 5), (x_pos, self.timeline_start_y + 5), 2)
            
            # Draw label
            time_label = FONT_SMALL.render(str(i), True, BLACK)
            screen.blit(time_label, (x_pos - time_label.get_width() // 2, self.timeline_start_y + 10))
        
        # Draw timeline segments
        for segment in self.scheduler.timeline:
            start_time, task_id, duration = segment
            
            # Calculate position
            x_start = self.timeline_start_x + (start_time / visible_time_range) * self.timeline_width
            width = (duration / visible_time_range) * self.timeline_width
            
            # Get task color
            color = TASK_COLORS[task_id % len(TASK_COLORS)]
            
            # Draw segment
            pygame.draw.rect(screen, color, 
                            (x_start, self.timeline_start_y - self.timeline_height, width, self.timeline_height))
            pygame.draw.rect(screen, BLACK, 
                            (x_start, self.timeline_start_y - self.timeline_height, width, self.timeline_height), 1)
            
            # Draw task ID
            task_label = FONT_SMALL.render(f"T{task_id}", True, BLACK)
            if width > task_label.get_width() + 10:  # Only if there's enough space
                screen.blit(task_label, 
                        (x_start + width // 2 - task_label.get_width() // 2, 
                        self.timeline_start_y - self.timeline_height // 2 - task_label.get_height() // 2))
        
        # Draw task legend
        legend_x = self.timeline_start_x
        legend_y = self.timeline_start_y + 40
        
        legend_title = FONT_MEDIUM.render("Task Legend:", True, BLACK)
        screen.blit(legend_title, (legend_x, legend_y))
        
        for i, task in enumerate(self.scheduler.tasks):
            y_pos = legend_y + 30 + i * 25
            
            # Draw color box
            pygame.draw.rect(screen, task.color, (legend_x, y_pos, 20, 20))
            pygame.draw.rect(screen, BLACK, (legend_x, y_pos, 20, 20), 1)
            
            # Draw task info
            task_text = f"Task {task.id}: Arrival={task.arrival_time}, Exec={task.execution_time}"
            if task.deadline is not None:
                task_text += f", Deadline={task.deadline}"
            
            task_info = FONT_SMALL.render(task_text, True, BLACK)
            screen.blit(task_info, (legend_x + 30, y_pos + 2))
        
    def draw_comparison(self, screen):
        # Title
        title = FONT_TITLE.render("Algorithm Comparison", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        # Results table
        if self.comparison_results:
            # Draw table headers
            headers = ["Algorithm", "CPU Util (%)", "Avg Wait", "Avg Turnaround", "Missed Deadlines"]
            col_widths = [200, 150, 150, 200, 200]
            total_width = sum(col_widths)
            
            start_x = (WIDTH - total_width) // 2
            header_y = 100
            
            for i, header in enumerate(headers):
                header_text = FONT_MEDIUM.render(header, True, BLACK)
                header_x = start_x + sum(col_widths[:i]) + (col_widths[i] - header_text.get_width()) // 2
                screen.blit(header_text, (header_x, header_y))
            
            # Draw horizontal line
            pygame.draw.line(screen, BLACK, 
                           (start_x, header_y + 30), 
                           (start_x + total_width, header_y + 30), 
                           2)
            
            # Draw data rows
            row_y = header_y + 40
            for i, (alg_name, metrics) in enumerate(self.comparison_results.items()):
                # Algorithm name
                alg_text = FONT_MEDIUM.render(alg_name, True, BLACK)
                alg_x = start_x + (col_widths[0] - alg_text.get_width()) // 2
                screen.blit(alg_text, (alg_x, row_y))
                
                # CPU Utilization
                cpu_text = FONT_MEDIUM.render(f"{metrics['CPU Utilization']:.2f}", True, BLACK)
                cpu_x = start_x + col_widths[0] + (col_widths[1] - cpu_text.get_width()) // 2
                screen.blit(cpu_text, (cpu_x, row_y))
                
                # Average Wait Time
                wait_text = FONT_MEDIUM.render(f"{metrics['Average Wait Time']:.2f}", True, BLACK)
                wait_x = start_x + col_widths[0] + col_widths[1] + (col_widths[2] - wait_text.get_width()) // 2
                screen.blit(wait_text, (wait_x, row_y))
                
                # Average Turnaround Time
                turnaround_text = FONT_MEDIUM.render(f"{metrics['Average Turnaround Time']:.2f}", True, BLACK)
                turnaround_x = start_x + sum(col_widths[:3]) + (col_widths[3] - turnaround_text.get_width()) // 2
                screen.blit(turnaround_text, (turnaround_x, row_y))
                
                # Missed Deadlines
                missed_text = FONT_MEDIUM.render(f"{metrics['Missed Deadlines']}", True, BLACK)
                missed_x = start_x + sum(col_widths[:4]) + (col_widths[4] - missed_text.get_width()) // 2
                screen.blit(missed_text, (missed_x, row_y))
                
                row_y += 40
            
            # Draw bar chart
            self.draw_comparison_chart(screen)
        else:
            no_results = FONT_MEDIUM.render("No comparison results available. Please run a comparison.", True, BLACK)
            screen.blit(no_results, (WIDTH // 2 - no_results.get_width() // 2, 150))
        
        # Buttons
        self.back_button.draw(screen)
    
    def draw_comparison_chart(self, screen):
        if not self.comparison_results:
            return
            
        # Bar chart for average wait time and turnaround time
        chart_title = FONT_MEDIUM.render("Performance Comparison", True, BLACK)
        screen.blit(chart_title, (WIDTH // 2 - chart_title.get_width() // 2, 350))
        
        # Chart dimensions
        chart_x = 100
        chart_y = 400
        chart_width = WIDTH - 200
        chart_height = 250
        
        # Draw axes
        pygame.draw.line(screen, BLACK, (chart_x, chart_y), (chart_x, chart_y + chart_height), 2)
        pygame.draw.line(screen, BLACK, (chart_x, chart_y + chart_height), 
                       (chart_x + chart_width, chart_y + chart_height), 2)
        
        # Determine max value for scaling
        max_value = 0
        for metrics in self.comparison_results.values():
            max_value = max(max_value, metrics["Average Wait Time"], metrics["Average Turnaround Time"])
        
        # Add some headroom
        max_value = max_value * 1.2 if max_value > 0 else 10
        
        # Draw y-axis labels
        for i in range(6):
            value = max_value * i / 5
            y_pos = chart_y + chart_height - (i * chart_height / 5)
            
            # Draw tick
            pygame.draw.line(screen, BLACK, (chart_x - 5, y_pos), (chart_x, y_pos), 2)
            
            # Draw label
            label = FONT_SMALL.render(f"{value:.1f}", True, BLACK)
            screen.blit(label, (chart_x - 10 - label.get_width(), y_pos - label.get_height() // 2))
        
        # Draw bars
        num_algorithms = len(self.comparison_results)
        bar_width = (chart_width - 100) / (num_algorithms * 2)  # 2 bars per algorithm
        spacing = 10
        
        for i, (alg_name, metrics) in enumerate(self.comparison_results.items()):
            # Wait time bar
            wait_height = (metrics["Average Wait Time"] / max_value) * chart_height if max_value > 0 else 0
            wait_x = chart_x + 50 + i * (bar_width * 2 + spacing)
            wait_y = chart_y + chart_height - wait_height
            
            pygame.draw.rect(screen, BLUE, (wait_x, wait_y, bar_width, wait_height))
            pygame.draw.rect(screen, BLACK, (wait_x, wait_y, bar_width, wait_height), 1)
            
            wait_label = FONT_SMALL.render("Wait", True, BLACK)
            screen.blit(wait_label, (wait_x + bar_width // 2 - wait_label.get_width() // 2, 
                                  chart_y + chart_height + 5))
            
            # Turnaround time bar
            turnaround_height = (metrics["Average Turnaround Time"] / max_value) * chart_height if max_value > 0 else 0
            turnaround_x = wait_x + bar_width
            turnaround_y = chart_y + chart_height - turnaround_height
            
            pygame.draw.rect(screen, GREEN, (turnaround_x, turnaround_y, bar_width, turnaround_height))
            pygame.draw.rect(screen, BLACK, (turnaround_x, turnaround_y, bar_width, turnaround_height), 1)
            
            turnaround_label = FONT_SMALL.render("TAT", True, BLACK)
            screen.blit(turnaround_label, (turnaround_x + bar_width // 2 - turnaround_label.get_width() // 2, 
                                        chart_y + chart_height + 20))
            
            # Algorithm name under both bars
            alg_label = FONT_SMALL.render(alg_name, True, BLACK)
            label_x = wait_x + bar_width - alg_label.get_width() // 2
            screen.blit(alg_label, (label_x, chart_y + chart_height + 40))
    
    def draw_comparison_setup(self, screen):
        # Title
        title = FONT_TITLE.render("Algorithm Comparison Setup", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
        
        # Instructions
        instructions = FONT_MEDIUM.render("Select algorithms to compare:", True, BLACK)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 80))
        
        # Draw checkboxes
        self.fcfs_checkbox.draw(screen)
        self.sjn_checkbox.draw(screen)
        self.rr_checkbox.draw(screen)
        self.rm_checkbox.draw(screen)
        self.edf_checkbox.draw(screen)
        
        # Real-time simulation settings
        rt_title = FONT_MEDIUM.render("Real-time Simulation Settings:", True, BLACK)
        screen.blit(rt_title, (400, 200))
        
        sim_time_label = FONT_SMALL.render("Simulation Time:", True, BLACK)
        screen.blit(sim_time_label, (400, 250))
        self.sim_time_input.rect.x = 550
        self.sim_time_input.rect.y = 250
        self.sim_time_input.draw(screen)
        
        # Round Robin settings
        rr_title = FONT_MEDIUM.render("Round Robin Settings:", True, BLACK)
        screen.blit(rr_title, (400, 300))
        
        quantum_label = FONT_SMALL.render("Time Quantum:", True, BLACK)
        screen.blit(quantum_label, (400, 350))
        self.quantum_input.rect.x = 550
        self.quantum_input.rect.y = 350
        self.quantum_input.draw(screen)
        
        # Task list
        tasks_title = FONT_MEDIUM.render("Current Tasks:", True, BLACK)
        screen.blit(tasks_title, (700, 200))
        
        if not self.scheduler.tasks:
            no_tasks = FONT_MEDIUM.render("No tasks added yet", True, DARK_GRAY)
            screen.blit(no_tasks, (700, 230))
        else:
            y_offset = 230
            for i, task in enumerate(self.scheduler.tasks):
                task_text = f"Task {task.id}: Arrival={task.arrival_time}, Exec={task.execution_time}"
                if task.deadline is not None:
                    task_text += f", Deadline={task.deadline}"
                if task.period is not None:
                    task_text += f", Period={task.period}"
                    
                task_surface = FONT_SMALL.render(task_text, True, BLACK)
                screen.blit(task_surface, (700, y_offset))
                y_offset += 25
        
        # Start comparison button
        compare_button = Button(WIDTH // 2 - 100, HEIGHT - 150, 200, 50, "Run Comparison", GREEN, (100, 255, 100))
        compare_button.draw(screen)
        
        # Back button
        self.back_button.draw(screen)
        
        return compare_button
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Handle mouse movement for button hover effects
            if event.type == pygame.MOUSEMOTION:
                if self.state == "MAIN_MENU":
                    self.add_task_button.check_hover(mouse_pos)
                    self.start_sim_button.check_hover(mouse_pos)
                    self.compare_button.check_hover(mouse_pos)
                elif self.state in ["SIMULATION", "COMPARISON", "COMPARISON_SETUP"]:
                    self.back_button.check_hover(mouse_pos)
                    if self.state == "SIMULATION":
                        self.reset_button.check_hover(mouse_pos)
            
            # Handle button clicks and other interactions
            if self.state == "MAIN_MENU":
                # Algorithm dropdown
                self.algorithm_dropdown.handle_event(event, mouse_pos)
                
                # Input fields
                self.arrival_time_input.handle_event(event)
                self.execution_time_input.handle_event(event)
                self.deadline_input.handle_event(event)
                self.period_input.handle_event(event)
                self.priority_input.handle_event(event)
                self.quantum_input.handle_event(event)
                self.sim_time_input.handle_event(event)
                
                # Add task button
                if self.add_task_button.is_clicked(mouse_pos, event):
                    self.add_task()
                
                # Start simulation button
                if self.start_sim_button.is_clicked(mouse_pos, event):
                    if self.scheduler.tasks:
                        self.state = "SIMULATION"
                        self.start_simulation()
                
                # Compare button
                if self.compare_button.is_clicked(mouse_pos, event):
                    if self.scheduler.tasks:
                        self.state = "COMPARISON_SETUP"
            
            elif self.state == "SIMULATION":
                # Back button
                if self.back_button.is_clicked(mouse_pos, event):
                    self.state = "MAIN_MENU"
                    self.is_simulating = False
                
                # Reset button
                if self.reset_button.is_clicked(mouse_pos, event):
                    self.scheduler.reset()
                    self.is_simulating = False
                    self.simulation_complete = False
                    self.start_simulation()
                
                # Mouse wheel for zooming
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # Zoom in
                        self.zoom_level *= 1.1
                    else:  # Zoom out
                        self.zoom_level /= 1.1
                    self.zoom_level = max(0.1, min(10, self.zoom_level))
            
            elif self.state == "COMPARISON":
                # Back button
                if self.back_button.is_clicked(mouse_pos, event):
                    self.state = "COMPARISON_SETUP"
            
            elif self.state == "COMPARISON_SETUP":
                # Back button
                if self.back_button.is_clicked(mouse_pos, event):
                    self.state = "MAIN_MENU"
                
                # Checkboxes
                self.fcfs_checkbox.is_clicked(mouse_pos, event)
                self.sjn_checkbox.is_clicked(mouse_pos, event)
                self.rr_checkbox.is_clicked(mouse_pos, event)
                self.rm_checkbox.is_clicked(mouse_pos, event)
                self.edf_checkbox.is_clicked(mouse_pos, event)
                
                # Input fields
                self.quantum_input.handle_event(event)
                self.sim_time_input.handle_event(event)
                
                # Run comparison button
                compare_button = Button(WIDTH // 2 - 100, HEIGHT - 150, 200, 50, "Run Comparison", GREEN, (100, 255, 100))
                compare_button.check_hover(mouse_pos)
                if compare_button.is_clicked(mouse_pos, event):
                    if self.scheduler.tasks:
                        self.run_comparison()
    
    def update(self):
        self.arrival_time_input.update()
        self.execution_time_input.update()
        self.deadline_input.update()
        self.period_input.update()
        self.priority_input.update()
        self.quantum_input.update()
        self.sim_time_input.update()
    
    def draw(self, screen):
        screen.fill(WHITE)
        
        if self.state == "MAIN_MENU":
            self.draw_main_menu(screen)
        elif self.state == "SIMULATION":
            self.draw_simulation(screen)
        elif self.state == "COMPARISON":
            self.draw_comparison(screen)
        elif self.state == "COMPARISON_SETUP":
            self.draw_comparison_setup(screen)
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        
        while True:
            self.handle_events()
            self.update()
            self.draw(SCREEN)
            clock.tick(60)

# Main function
def main():
    visualizer = SchedulerVisualizer()
    visualizer.run()

if __name__ == "__main__":
    main()