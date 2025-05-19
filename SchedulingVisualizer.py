# ImprovedCPUScheduler.py
# ======================
# Modern CPU Scheduling Visualization Application with Improved UI

import pygame
import sys
import threading
import time
import re

# ------------------ PYGAME SETUP ------------------
pygame.init()
screen = pygame.display.set_mode((1600, 900))
pygame.display.set_caption("CPU Scheduling Visualizer")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont('Arial', 36)
heading_font = pygame.font.SysFont('Arial', 24)
font = pygame.font.SysFont('Arial', 18)
small_font = pygame.font.SysFont('Arial', 16)

# Colors
BG_COLOR = (245, 242, 236)  # Light beige background
CARD_BG = (255, 255, 255)   # White card background
DROPDOWN_BG = (240, 248, 255)  # Alice Blue for dropdown menu
DROPDOWN_HOVER = (220, 230, 242)  # Lighter blue for dropdown hover
HEADING_COLOR = (139, 0, 0)  # Dark red for headings
TEXT_COLOR = (0, 0, 0)       # Black text
BUTTON_COLOR = (178, 34, 34) # Firebrick red for buttons
BUTTON_HOVER = (205, 92, 92) # Lighter red for hover
TABLE_HEADER = (76, 84, 98)  # Dark slate for table headers
TABLE_ROW_1 = (108, 117, 125) # Darker gray for odd rows
TABLE_ROW_2 = (122, 130, 136) # Lighter gray for even rows
BORDER_COLOR = (200, 200, 200) # Light gray borders
CHART_COLORS = [
    (70, 130, 180),   # Steel Blue
    (106, 90, 205),   # Slate Blue
    (60, 179, 113),   # Medium Sea Green
    (218, 112, 214),  # Orchid
    (255, 165, 0),    # Orange
    (30, 144, 255),   # Dodger Blue
    (255, 99, 71),    # Tomato
    (152, 251, 152),  # Pale Green
]

# ------------------ TASK CLASS ------------------
class Task:
    def __init__(self, name, arrival, burst, deadline=None, period=None):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.deadline = deadline
        self.period = period
        self.start_time = None
        self.finish_time = None
        self.executions = []
        self.waiting_time = 0
        self.turnaround_time = 0

# ------------------ UI COMPONENTS ------------------
class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = BUTTON_HOVER
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, y_offset=0):
        # Create temp rect with possible y offset
        temp_rect = pygame.Rect(self.x, self.y + y_offset, self.width, self.height)
        
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, temp_rect, border_radius=5)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=temp_rect.center)
        screen.blit(text_surf, text_rect)
        
    def check_hover(self, pos, y_offset=0):
        temp_rect = pygame.Rect(self.x, self.y + y_offset, self.width, self.height)
        self.is_hovered = temp_rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event, y_offset=0):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            temp_rect = pygame.Rect(self.x, self.y + y_offset, self.width, self.height)
            return temp_rect.collidepoint(pos)
        return False

class Dropdown:
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.selected = options[0]
        self.is_active = False
        self.option_rects = []
        self.hovered_index = -1
        
        self.update_option_rects()
            
    def update_option_rects(self):
        self.option_rects = []
        for i, option in enumerate(self.options):
            self.option_rects.append(pygame.Rect(self.x, self.y + (i+1) * self.height, self.width, self.height))
            
    def draw(self):
        # Draw main button
        pygame.draw.rect(screen, CARD_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, BORDER_COLOR, self.rect, width=1, border_radius=5)
        text_surf = font.render(self.selected, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        # Draw arrow
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery + 5),
            (self.rect.right - 30, self.rect.centery + 5)
        ]
        pygame.draw.polygon(screen, TEXT_COLOR, arrow_points)
        
        # Draw dropdown if active
        if self.is_active:
            # Draw a semi-transparent overlay behind the dropdown
            overlay = pygame.Surface((self.width + 20, len(self.options) * self.height + 10), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 10))  # Very light shadow
            screen.blit(overlay, (self.x - 10, self.y + self.height - 5))
            
            for i, rect in enumerate(self.option_rects):
                # Use different colors for the dropdown options
                bg_color = DROPDOWN_HOVER if i == self.hovered_index else DROPDOWN_BG
                pygame.draw.rect(screen, bg_color, rect, border_radius=5)
                pygame.draw.rect(screen, BORDER_COLOR, rect, width=1, border_radius=5)
                option_text = font.render(self.options[i], True, TEXT_COLOR)
                option_rect = option_text.get_rect(midleft=(rect.left + 10, rect.centery))
                screen.blit(option_text, option_rect)
    
    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_active = not self.is_active
                return None
            
            if self.is_active:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(pos):
                        self.selected = self.options[i]
                        self.is_active = False
                        return self.selected
                        
            if self.is_active:
                self.is_active = False
        
        # Update hovered option
        if self.is_active:
            self.hovered_index = -1
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    self.hovered_index = i
                    break
        
        return None

class InputField:
    def __init__(self, x, y, width, height, label, placeholder="", is_numeric=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.is_numeric = is_numeric
        self.label_surface = font.render(label, True, TEXT_COLOR)
        self.label_rect = self.label_surface.get_rect(topleft=(x, y - 25))
        
    def draw(self, y_offset=0):
        # Create temporary rectangles with the y_offset applied
        temp_rect = pygame.Rect(self.x, self.y + y_offset, self.width, self.height)
        temp_label_rect = self.label_surface.get_rect(topleft=(self.x, self.y + y_offset - 25))
        
        # Draw label with offset
        screen.blit(self.label_surface, temp_label_rect)
        
        # Draw input field with offset
        pygame.draw.rect(screen, CARD_BG, temp_rect, border_radius=5)
        pygame.draw.rect(screen, BORDER_COLOR if not self.active else BUTTON_COLOR, 
                         temp_rect, width=2, border_radius=5)
        
        # Draw text or placeholder
        if self.text:
            text_surf = font.render(self.text, True, TEXT_COLOR)
        else:
            text_surf = font.render(self.placeholder, True, BORDER_COLOR)
            
        text_rect = text_surf.get_rect(midleft=(temp_rect.left + 10, temp_rect.centery))
        screen.blit(text_surf, text_rect)
        
    def handle_event(self, event, y_offset=0):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Create a temporary rect with the current offset for collision detection
            temp_rect = pygame.Rect(self.x, self.y + y_offset, self.width, self.height)
            self.active = temp_rect.collidepoint(event.pos)
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            else:
                if self.is_numeric:
                    if event.unicode.isdigit() or event.unicode in [',', '.', ' ']:
                        self.text += event.unicode
                else:
                    self.text += event.unicode
        
        return self.text if not self.active and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN else None

# ------------------ SCHEDULING ALGORITHMS ------------------
def parse_input_list(text):
    """Parse comma or space-separated values into a list of integers"""
    if not text.strip():
        return []
    # Replace commas with spaces and split
    parts = re.split(r'[,\s]+', text.strip())
    return [int(p) for p in parts if p.isdigit()]

def fcfs(tasks):
    time = 0
    for task in sorted(tasks, key=lambda t: t.arrival):
        # Wait until task arrives if needed
        time = max(time, task.arrival)
        
        # Set task start time if this is first execution
        if task.start_time is None:
            task.start_time = time
            
        task.waiting_time = time - task.arrival
        task.finish_time = time + task.burst
        task.turnaround_time = task.finish_time - task.arrival
        
        schedule.append((task.name, time, task.finish_time))
        task.executions.append((time, task.finish_time))
        
        time += task.burst

def sjn(tasks):
    time = 0
    ready = []
    left = tasks.copy()
    
    while left or ready:
        # Move arrived tasks to ready queue
        for t in left[:]:
            if t.arrival <= time:
                ready.append(t)
                left.remove(t)
                
        if ready:
            # Select task with shortest burst time
            ready.sort(key=lambda x: x.burst)
            t = ready.pop(0)
            
            # Set task start time if this is first execution
            if t.start_time is None:
                t.start_time = time
                
            t.waiting_time = time - t.arrival
            t.finish_time = time + t.burst
            t.turnaround_time = t.finish_time - t.arrival
            
            schedule.append((t.name, time, t.finish_time))
            t.executions.append((time, t.finish_time))
            
            time += t.burst
        else:
            time += 1

def rr(tasks, time_quantum):
    time = 0
    ready_queue = []
    remaining_tasks = tasks.copy()
    
    while remaining_tasks or ready_queue:
        # Move arrived tasks to ready queue
        for task in remaining_tasks[:]:
            if task.arrival <= time:
                ready_queue.append(task)
                remaining_tasks.remove(task)
                
        if ready_queue:
            current_task = ready_queue.pop(0)
            
            # Set task start time if first execution
            if current_task.start_time is None:
                current_task.start_time = time
                
            # Determine execution time for this quantum
            execution_time = min(time_quantum, current_task.remaining)
            
            # Execute for the quantum
            start_time = time
            time += execution_time
            current_task.remaining -= execution_time
            
            # Record execution interval
            schedule.append((current_task.name, start_time, time))
            current_task.executions.append((start_time, time))
            
            # Check if task is complete
            if current_task.remaining <= 0:
                current_task.finish_time = time
                current_task.turnaround_time = current_task.finish_time - current_task.arrival
                current_task.waiting_time = current_task.turnaround_time - current_task.burst
            else:
                # Put back in ready queue
                ready_queue.append(current_task)
        else:
            # No tasks ready, advance time
            time += 1

def rm(tasks):
    time = 0
    # Sort tasks by period (rate monotonic)
    periodic_tasks = sorted(tasks, key=lambda x: x.period if x.period is not None else float('inf'))
    
    # Continue until all tasks have completed their execution
    while any(x.remaining > 0 for x in periodic_tasks):
        # Get tasks that have arrived and still need execution
        ready = [x for x in periodic_tasks if x.arrival <= time and x.remaining > 0]
        
        if ready:
            # Select highest priority task (lowest period)
            t = ready[0]
            
            # Set task start time if first execution
            if t.start_time is None:
                t.start_time = time
                
            # Execute for one time unit
            start = time
            t.remaining -= 1
            time += 1
            
            # Record execution
            schedule.append((t.name, start, time))
            t.executions.append((start, time))
            
            # Check if task is complete
            if t.remaining == 0:
                t.finish_time = time
                t.turnaround_time = t.finish_time - t.arrival
                t.waiting_time = t.turnaround_time - t.burst
        else:
            # No tasks ready, advance time
            time += 1

def edf(tasks):
    time = 0
    while any(x.remaining > 0 for x in tasks):
        # Get tasks that have arrived and still need execution
        ready = [x for x in tasks if x.arrival <= time and x.remaining > 0]
        
        if ready:
            # Select task with earliest deadline
            t = min(ready, key=lambda x: x.deadline if x.deadline is not None else float('inf'))
            
            # Set task start time if first execution
            if t.start_time is None:
                t.start_time = time
            
            # Execute for one time unit
            start = time
            t.remaining -= 1
            time += 1
            
            # Record execution
            schedule.append((t.name, start, time))
            t.executions.append((start, time))
            
            # Check if task is complete
            if t.remaining == 0:
                t.finish_time = time
                t.turnaround_time = t.finish_time - t.arrival
                t.waiting_time = t.turnaround_time - t.burst
        else:
            # No tasks ready, advance time
            time += 1

# ------------------ METRICS & DRAW ------------------
def calculate_metrics(tasks):
    if not tasks:
        return {}
    
    metrics = {}
    
    # Calculate CPU utilization
    if any(t.finish_time is not None for t in tasks):
        total_time = max((t.finish_time or 0) for t in tasks)
        cpu_time = sum((e[1] - e[0]) for t in tasks for e in t.executions)
        metrics['cpu_utilization'] = (cpu_time / total_time * 100) if total_time > 0 else 0
    else:
        metrics['cpu_utilization'] = 0
    
    # Calculate average waiting and turnaround times
    total_waiting = 0
    total_turnaround = 0
    completed_tasks = 0
    
    for task in tasks:
        if task.finish_time is not None:
            total_waiting += task.waiting_time
            total_turnaround += task.turnaround_time
            completed_tasks += 1
    
    if completed_tasks > 0:
        metrics['avg_waiting'] = total_waiting / completed_tasks
        metrics['avg_turnaround'] = total_turnaround / completed_tasks
    else:
        metrics['avg_waiting'] = 0
        metrics['avg_turnaround'] = 0
    
    return metrics

# Update the Gantt chart drawing to handle text overflow
def draw_gantt_chart(x, y, width, height, max_time):
    # Draw timeline axis
    pygame.draw.line(screen, TEXT_COLOR, (x, y + height + 10), (x + width, y + height + 10), 2)
    
    # Draw time markers
    unit_width = width / max_time if max_time > 0 else width
    for t in range(0, max_time + 1, max(1, max_time // 10)):
        marker_x = x + t * unit_width
        pygame.draw.line(screen, TEXT_COLOR, (marker_x, y + height + 10), (marker_x, y + height + 15), 2)
        time_text = small_font.render(str(t), True, TEXT_COLOR)
        screen.blit(time_text, (marker_x - 5, y + height + 20))
    
    # Draw task executions
    for i, (task_name, start, end) in enumerate(schedule):
        color = CHART_COLORS[i % len(CHART_COLORS)]
        block_x = x + start * unit_width
        block_width = (end - start) * unit_width
        
        # Draw execution block
        pygame.draw.rect(screen, color, (block_x, y, block_width, height), border_radius=3)
        pygame.draw.rect(screen, TEXT_COLOR, (block_x, y, block_width, height), width=1, border_radius=3)
        
        # Draw task name only if block is wide enough
        name_text = small_font.render(task_name, True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(block_x + block_width/2, y + height/2))
        
        # Only draw text if there's enough space
        if block_width > name_rect.width + 4:
            screen.blit(name_text, name_rect)

# Modify the results table to handle overflow with scrolling or pagination
def draw_results_table(x, y, width, height, tasks):
    # Table header
    headers = ["Job", "Arrival Time", "Burst Time", "Finish Time", "Turn Around Time", "Waiting Time"]
    col_width = width / len(headers)
    
    # Calculate max visible rows based on available height
    row_height = 30
    header_height = 40
    max_rows = (height - header_height) // row_height
    
    # Draw table headers
    for i, header in enumerate(headers):
        header_rect = pygame.Rect(x + i * col_width, y, col_width, header_height)
        pygame.draw.rect(screen, TABLE_HEADER, header_rect)
        pygame.draw.rect(screen, TEXT_COLOR, header_rect, width=1)
        
        header_text = small_font.render(header, True, (255, 255, 255))
        header_text_rect = header_text.get_rect(center=header_rect.center)
        screen.blit(header_text, header_text_rect)
    
    # Draw table rows - limit to max visible rows
    sorted_tasks = sorted(tasks, key=lambda t: t.name)
    visible_tasks = sorted_tasks[:max_rows-1]  # Leave space for average row
    
    for i, task in enumerate(visible_tasks):
        row_y = y + header_height + i * row_height
        row_color = TABLE_ROW_1 if i % 2 == 0 else TABLE_ROW_2
        
        # Draw row background
        row_rect = pygame.Rect(x, row_y, width, row_height)
        pygame.draw.rect(screen, row_color, row_rect)
        
        # Task data
        values = [
            task.name,
            str(task.arrival),
            str(task.burst),
            str(task.finish_time if task.finish_time is not None else "-"),
            str(task.turnaround_time if task.finish_time is not None else "-"),
            str(task.waiting_time if task.finish_time is not None else "-")
        ]
        
        # Draw cell values
        for j, value in enumerate(values):
            cell_rect = pygame.Rect(x + j * col_width, row_y, col_width, row_height)
            pygame.draw.rect(screen, TEXT_COLOR, cell_rect, width=1)
            
            cell_text = small_font.render(value, True, (255, 255, 255))
            cell_text_rect = cell_text.get_rect(center=cell_rect.center)
            screen.blit(cell_text, cell_text_rect)
    
    # Show indicator if there are more tasks than can be displayed
    if len(sorted_tasks) > max_rows-1:
        more_text = small_font.render(f"+ {len(sorted_tasks) - (max_rows-1)} more tasks", True, TEXT_COLOR)
        screen.blit(more_text, (x + width - 150, y + header_height + (max_rows-1) * row_height + 5))
    
    # Draw averages row
    if tasks:
        metrics = calculate_metrics(tasks)
        avg_row_y = y + header_height + min(len(visible_tasks), max_rows-1) * row_height
        
        # Draw row background
        avg_rect = pygame.Rect(x, avg_row_y, width, row_height)
        pygame.draw.rect(screen, TABLE_HEADER, avg_rect)
        
        # Create the "Average" text for the first cell
        avg_text = small_font.render("Average", True, (255, 255, 255))
        avg_text_rect = avg_text.get_rect(center=(x + col_width/2, avg_row_y + row_height/2))
        screen.blit(avg_text, avg_text_rect)
        
        # Draw the average cells
        for j in range(len(headers)):
            cell_rect = pygame.Rect(x + j * col_width, avg_row_y, col_width, row_height)
            pygame.draw.rect(screen, TEXT_COLOR, cell_rect, width=1)
            
            # Only add values for turnaround and waiting time columns
            if j == 4:  # Turnaround time column
                value = f"{metrics['avg_turnaround']:.2f}"
                cell_text = small_font.render(value, True, (255, 255, 255))
                cell_text_rect = cell_text.get_rect(center=cell_rect.center)
                screen.blit(cell_text, cell_text_rect)
            elif j == 5:  # Waiting time column
                value = f"{metrics['avg_waiting']:.2f}"
                cell_text = small_font.render(value, True, (255, 255, 255))
                cell_text_rect = cell_text.get_rect(center=cell_rect.center)
                screen.blit(cell_text, cell_text_rect)

# Modify draw_input_panel() to show the relevant inputs based on algorithm
def draw_input_panel():
    # Draw input card background - make it taller to accommodate additional fields
    pygame.draw.rect(screen, CARD_BG, (50, 100, 450, 650), border_radius=10)
    
    # Draw algorithm selector
    algo_label = font.render("Algorithm", True, TEXT_COLOR)
    screen.blit(algo_label, (75, 125))
    
    # Calculate offset for other UI elements based on dropdown state
    y_offset = 0
    if algo_dropdown.is_active:
        # Calculate space needed for dropdown options
        dropdown_height = len(algo_dropdown.options) * algo_dropdown.rect.height
        y_offset = dropdown_height
    
    # Draw input fields with offset if dropdown is active
    arrival_input.draw(y_offset=y_offset if algo_dropdown.is_active else 0)
    burst_input.draw(y_offset=y_offset if algo_dropdown.is_active else 0)
    
    # Draw additional input fields based on selected algorithm
    if algo_dropdown.selected == "Round Robin (RR)":
        quantum_input.draw(y_offset=y_offset if algo_dropdown.is_active else 0)
        # Adjust submit button position
        submit_button.y = 550
    elif algo_dropdown.selected == "Rate Monotonic (RM)":
        period_input.draw(y_offset=y_offset if algo_dropdown.is_active else 0)
        # Adjust submit button position
        submit_button.y = 650
    elif algo_dropdown.selected == "Earliest Deadline First (EDF)":
        deadline_input.draw(y_offset=y_offset if algo_dropdown.is_active else 0)
        # Adjust submit button position
        submit_button.y = 650
    else:
        # For FCFS and SJN, keep submit button at original position
        submit_button.y = 450
    
    # Draw submit button with offset if dropdown is active
    submit_button.draw(y_offset=y_offset if algo_dropdown.is_active else 0)
    
    # Draw dropdown last so it appears on top of everything
    algo_dropdown.draw()

def draw_output_panel():
    # Only draw output panel if there's data to show
    if not tasks:
        return
        
    # Draw output card background
    pygame.draw.rect(screen, (200, 200, 190), (550, 100, 600, 550), border_radius=10)
    
    # Draw output header
    output_header = heading_font.render(f"You chose {algo_dropdown.selected} CPU Scheduling Algorithm", True, TEXT_COLOR)
    screen.blit(output_header, (575, 125))
    
    # Draw Gantt chart
    chart_label = font.render("Gantt Chart", True, TEXT_COLOR)
    screen.blit(chart_label, (575, 165))
    
    # Find maximum time for scaling Gantt chart
    max_time = 1
    if schedule:
        max_time = max(end for _, _, end in schedule)
    
    draw_gantt_chart(575, 195, 550, 40, max_time)
    
    # Draw results table
    table_label = font.render("Results", True, TEXT_COLOR)
    screen.blit(table_label, (575, 265))
    draw_results_table(575, 295, 550, 30 * (len(tasks) + 2), tasks)
    
    # Draw CPU utilization
    metrics = calculate_metrics(tasks)
    util_text = font.render(f"CPU Utilization: {metrics['cpu_utilization']:.2f}%", True, TEXT_COLOR)
    screen.blit(util_text, (575, 225))

# ------------------ MAIN ------------------
# Global variables
tasks = []
schedule = []
current_algorithm = None

# Create UI components
algo_dropdown = Dropdown(75, 150, 400, 40, [
    "First Come First Served (FCFS)", 
    "Shortest Job Next (SJN)", 
    "Round Robin (RR)",
    "Rate Monotonic (RM)",
    "Earliest Deadline First (EDF)"
])

arrival_input = InputField(75, 250, 400, 40, "Arrival Time (comma separated)", 
                          placeholder="e.g. 0, 1, 2, 4")
burst_input = InputField(75, 350, 400, 40, "Burst Time (comma separated)",
                        placeholder="e.g. 5, 4, 3, 2")
quantum_input = InputField(75, 450, 400, 40, "Time Quantum (for RR)",
                          placeholder="2", is_numeric=True)
# Add deadline/period input fields for RM/EDF algorithms
deadline_input = InputField(75, 450, 400, 40, "Deadline (for EDF, comma separated)",
                          placeholder="e.g. 10, 8, 15, 12")
period_input = InputField(75, 550, 400, 40, "Period (for RM, comma separated)",
                          placeholder="e.g. 20, 10, 30, 15")
submit_button = Button(200, 550, 150, 50, "Simulate")

# Update run_simulation() to handle additional parameters
def run_simulation():
    global tasks, schedule
    
    # Clear previous data
    tasks.clear()
    schedule.clear()
    
    # Parse inputs
    arrivals = parse_input_list(arrival_input.text)
    bursts = parse_input_list(burst_input.text)
    
    # Parse additional parameters based on algorithm
    deadlines = []
    periods = []
    
    if algo_dropdown.selected == "Earliest Deadline First (EDF)":
        deadlines = parse_input_list(deadline_input.text)
    
    if algo_dropdown.selected == "Rate Monotonic (RM)":
        periods = parse_input_list(period_input.text)
    
    # Create tasks with appropriate parameters
    for i in range(min(len(arrivals), len(bursts))):
        task_name = chr(65 + i)  # A, B, C, etc.
        deadline = deadlines[i] if i < len(deadlines) else None
        period = periods[i] if i < len(periods) else None
        tasks.append(Task(task_name, arrivals[i], bursts[i], deadline, period))
    
    # Select algorithm
    algorithm = algo_dropdown.selected
    
    # Validate required parameters before running the algorithm
    if algorithm == "Round Robin (RR)" and not quantum_input.text:
        # Show error message or use default
        quantum_input.text = "2"  # Default time quantum
    
    if algorithm == "Earliest Deadline First (EDF)" and not deadline_input.text:
        # Show error message
        return
    
    if algorithm == "Rate Monotonic (RM)" and not period_input.text:
        # Show error message
        return
    
    # Run selected algorithm
    if algorithm == "First Come First Served (FCFS)":
        fcfs(tasks)
    elif algorithm == "Shortest Job Next (SJN)":
        sjn(tasks)
    elif algorithm == "Round Robin (RR)":
        # Get time quantum (default to 2)
        time_quantum = 2
        if quantum_input.text:
            try:
                time_quantum = int(quantum_input.text)
                if time_quantum <= 0:
                    time_quantum = 2  # Use default if invalid
            except ValueError:
                pass
        rr(tasks, time_quantum)
    elif algorithm == "Rate Monotonic (RM)":
        rm(tasks)
    elif algorithm == "Earliest Deadline First (EDF)":
        edf(tasks)

if __name__ == "__main__":
    running = True
    
    while running:
        # Clear screen
        screen.fill(BG_COLOR)
        
        # Handle events
        mouse_pos = pygame.mouse.get_pos()
        
        # Calculate offset for other UI elements based on dropdown state
        y_offset = 0
        if algo_dropdown.is_active:
            # Calculate space needed for dropdown options
            dropdown_height = len(algo_dropdown.options) * algo_dropdown.rect.height
            y_offset = dropdown_height
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Check dropdown interactions
            algo_dropdown.handle_event(event, mouse_pos)
            
            # Input field interactions with appropriate offset
            arrival_input.handle_event(event, y_offset if algo_dropdown.is_active else 0)
            burst_input.handle_event(event, y_offset if algo_dropdown.is_active else 0)
            
            if algo_dropdown.selected == "Round Robin (RR)":
                quantum_input.handle_event(event, y_offset if algo_dropdown.is_active else 0)
            # Update main loop to handle input events for new fields
            # Add to the event handling section in the main loop
            if algo_dropdown.selected == "Earliest Deadline First (EDF)":
                deadline_input.handle_event(event, y_offset if algo_dropdown.is_active else 0)
            elif algo_dropdown.selected == "Rate Monotonic (RM)":
                period_input.handle_event(event, y_offset if algo_dropdown.is_active else 0)
            
            # Submit button interactions with appropriate offset
            submit_button.check_hover(mouse_pos, y_offset if algo_dropdown.is_active else 0)
            if submit_button.is_clicked(mouse_pos, event, y_offset if algo_dropdown.is_active else 0):
                run_simulation()
                
        # Draw title
        title_text = title_font.render("CPU SCHEDULING VISUALIZER", True, HEADING_COLOR)
        title_rect = title_text.get_rect(center=(600, 50))
        screen.blit(title_text, title_rect)
        
        # Draw UI panels
        draw_input_panel()
        draw_output_panel()
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()
    sys.exit()
