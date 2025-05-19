# ImprovedCPUScheduler.py
# ======================
# Modern CPU Scheduling Visualization Application with Improved UI

import pygame
import sys
import threading
import time
import re
import math
import queue
from copy import deepcopy

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
        self.dropdown_surface = None
        
        self.update_option_rects()
            
    def update_option_rects(self):
        self.option_rects = []
        for i, option in enumerate(self.options):
            # Store positions relative to the dropdown surface
            self.option_rects.append(pygame.Rect(0, i * self.height, self.width, self.height))
            
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
            # Create a separate surface for the dropdown to ensure it appears on top
            dropdown_height = len(self.options) * self.height
            self.dropdown_surface = pygame.Surface((self.width, dropdown_height), pygame.SRCALPHA)
            
            # Draw a shadow effect for the dropdown
            shadow_surface = pygame.Surface((self.width + 10, dropdown_height + 10), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 30))  # Semi-transparent shadow
            screen.blit(shadow_surface, (self.x - 5, self.y + self.height - 5))
            
            # Draw each option on the dropdown surface
            for i, rect in enumerate(self.option_rects):
                bg_color = DROPDOWN_HOVER if i == self.hovered_index else DROPDOWN_BG
                pygame.draw.rect(self.dropdown_surface, bg_color, rect, border_radius=5)
                pygame.draw.rect(self.dropdown_surface, BORDER_COLOR, rect, width=1, border_radius=5)
                option_text = font.render(self.options[i], True, TEXT_COLOR)
                option_rect = option_text.get_rect(midleft=(rect.left + 10, rect.centery))
                self.dropdown_surface.blit(option_text, option_rect)
            
            # Blit the dropdown surface to the screen, ensuring it appears on top
            screen.blit(self.dropdown_surface, (self.x, self.y + self.height))
    
    def handle_event(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                self.is_active = not self.is_active
                return None
            
            if self.is_active:
                # Calculate relative position for dropdown options
                relative_pos = (pos[0] - self.x, pos[1] - (self.y + self.height))
                
                # Check if click is within dropdown area
                dropdown_rect = pygame.Rect(self.x, self.y + self.height, 
                                           self.width, len(self.options) * self.height)
                
                if dropdown_rect.collidepoint(pos):
                    # Find which option was clicked
                    option_index = relative_pos[1] // self.height
                    if 0 <= option_index < len(self.options):
                        self.selected = self.options[option_index]
                        self.is_active = False
                        return self.selected
                else:
                    # Click outside dropdown area - close it
                    self.is_active = False
        
        # Update hovered option
        if self.is_active:
            self.hovered_index = -1
            dropdown_rect = pygame.Rect(self.x, self.y + self.height, 
                                       self.width, len(self.options) * self.height)
            
            if dropdown_rect.collidepoint(pos):
                relative_pos = (pos[0] - self.x, pos[1] - (self.y + self.height))
                option_index = relative_pos[1] // self.height
                if 0 <= option_index < len(self.options):
                    self.hovered_index = option_index
        
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
    """First Come First Served Algorithm"""
    result_tasks = deepcopy(tasks)
    result_schedule = []
    
    time = 0
    for task in sorted(result_tasks, key=lambda t: t.arrival):
        # Wait until task arrives if needed
        time = max(time, task.arrival)
        
        # Set task start time if this is first execution
        if task.start_time is None:
            task.start_time = time
            
        task.waiting_time = time - task.arrival
        task.finish_time = time + task.burst
        task.turnaround_time = task.finish_time - task.arrival
        
        result_schedule.append((task.name, time, task.finish_time))
        task.executions.append((time, task.finish_time))
        
        time += task.burst
        
    return result_tasks, result_schedule

def sjn(tasks):
    """Shortest Job Next Algorithm"""
    result_tasks = deepcopy(tasks)
    result_schedule = []
    
    time = 0
    ready = []
    left = result_tasks.copy()
    
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
            
            result_schedule.append((t.name, time, t.finish_time))
            t.executions.append((time, t.finish_time))
            
            time += t.burst
        else:
            time += 1
            
    return result_tasks, result_schedule

def rr(tasks, time_quantum):
    """Round Robin Algorithm"""
    result_tasks = deepcopy(tasks)
    result_schedule = []
    
    time = 0
    ready_queue = []
    remaining_tasks = result_tasks.copy()
    
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
            result_schedule.append((current_task.name, start_time, time))
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
            
    return result_tasks, result_schedule

def rm(tasks):
    """Rate Monotonic Algorithm"""
    result_tasks = deepcopy(tasks)
    result_schedule = []
    
    time = 0
    # Sort tasks by period (rate monotonic)
    periodic_tasks = sorted(result_tasks, key=lambda x: x.period if x.period is not None else float('inf'))
    
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
            result_schedule.append((t.name, start, time))
            t.executions.append((start, time))
            
            # Check if task is complete
            if t.remaining == 0:
                t.finish_time = time
                t.turnaround_time = t.finish_time - t.arrival
                t.waiting_time = t.turnaround_time - t.burst
        else:
            # No tasks ready, advance time
            time += 1
            
    return result_tasks, result_schedule

def edf(tasks):
    """Earliest Deadline First Algorithm"""
    result_tasks = deepcopy(tasks)
    result_schedule = []
    
    time = 0
    while any(x.remaining > 0 for x in result_tasks):
        # Get tasks that have arrived and still need execution
        ready = [x for x in result_tasks if x.arrival <= time and x.remaining > 0]
        
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
            result_schedule.append((t.name, start, time))
            t.executions.append((start, time))
            
            # Check if task is complete
            if t.remaining == 0:
                t.finish_time = time
                t.turnaround_time = t.finish_time - t.arrival
                t.waiting_time = t.turnaround_time - t.burst
        else:
            # No tasks ready, advance time
            time += 1
            
    return result_tasks, result_schedule

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

def draw_gantt_chart(x, y, width, height, max_time, current_schedule):
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
    for i, (task_name, start, end) in enumerate(current_schedule):
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

def draw_results_table(x, y, width, height, current_tasks):
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
    sorted_tasks = sorted(current_tasks, key=lambda t: t.name)
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
    if current_tasks:
        metrics = calculate_metrics(current_tasks)
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

# ------------------ NEW COMPONENTS FOR ALGORITHM COMPARISON ------------------
def draw_bar_chart(x, y, width, height, data, title, colors):
    """Draw a bar chart to compare algorithm performance"""
    pygame.draw.rect(screen, CARD_BG, (x-10, y-40, width+20, height+60), border_radius=10)
    
    # Draw title
    title_surf = heading_font.render(title, True, TEXT_COLOR)
    title_rect = title_surf.get_rect(midtop=(x + width/2, y-30))
    screen.blit(title_surf, title_rect)
    
    # Draw Y axis
    pygame.draw.line(screen, TEXT_COLOR, (x, y), (x, y+height), 2)
    
    # Calculate max value for scaling
    max_value = max(data.values()) if data else 0
    if max_value == 0:
        max_value = 1  # Avoid division by zero
    
    # Number of algorithms
    num_algorithms = len(data)
    if num_algorithms == 0:
        return
    
    # Bar width and spacing
    bar_width = (width - 40) / num_algorithms
    spacing = 10
    
    # Draw bars
    for i, (algo, value) in enumerate(data.items()):
        bar_height = (value / max_value) * (height - 20)
        bar_x = x + 20 + i * (bar_width + spacing)
        bar_y = y + height - bar_height
        
        color = colors[i % len(colors)]
        pygame.draw.rect(screen, color, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, TEXT_COLOR, (bar_x, bar_y, bar_width, bar_height), width=1)
        
        # Draw algorithm name
        algo_name = small_font.render(algo, True, TEXT_COLOR)
        algo_rect = algo_name.get_rect(midtop=(bar_x + bar_width/2, y + height + 5))
        screen.blit(algo_name, algo_rect)
        
        # Draw value on top of bar
        value_text = small_font.render(f"{value:.2f}", True, TEXT_COLOR)
        value_rect = value_text.get_rect(midbottom=(bar_x + bar_width/2, bar_y - 5))
        screen.blit(value_text, value_rect)
    
    # Draw X axis
    pygame.draw.line(screen, TEXT_COLOR, (x, y+height), (x+width, y+height), 2)

def draw_back_button(x, y):
    """Draw a back button for returning from comparison view"""
    back_button = Button(x, y, 120, 40, "Back")
    back_button.draw()
    return back_button

def draw_comparison_view(comparison_results):
    """Draw the comparison view with all algorithm metrics"""
    # Clear screen
    screen.fill(BG_COLOR)
    
    # Draw title
    title_text = title_font.render("ALGORITHM COMPARISON", True, HEADING_COLOR)
    title_rect = title_text.get_rect(center=(800, 50))
    screen.blit(title_text, title_rect)
    
    if not comparison_results:
        # Show message if no results
        msg = heading_font.render("No comparison data available", True, TEXT_COLOR)
        msg_rect = msg.get_rect(center=(800, 450))
        screen.blit(msg, msg_rect)
        return draw_back_button(20, 20)
    
    # Extract metrics for each algorithm
    waiting_times = {}
    turnaround_times = {}
    cpu_utilization = {}
    
    for algo, (tasks, _) in comparison_results.items():
        metrics = calculate_metrics(tasks)
        waiting_times[algo] = metrics['avg_waiting']
        turnaround_times[algo] = metrics['avg_turnaround']
        cpu_utilization[algo] = metrics['cpu_utilization']
    
    # Draw three bar charts side by side
    chart_width = 400
    chart_height = 300
    padding = 60
    
    # Waiting time chart
    draw_bar_chart(100, 150, chart_width, chart_height, 
                   waiting_times, "Average Waiting Time", CHART_COLORS)
    
    # Turnaround time chart
    draw_bar_chart(100 + chart_width + padding, 150, chart_width, 
                   chart_height, turnaround_times, "Average Turnaround Time", CHART_COLORS)
    
    # CPU Utilization chart
    draw_bar_chart(100 + 2 * (chart_width + padding), 150, chart_width, 
                   chart_height, cpu_utilization, "CPU Utilization (%)", CHART_COLORS)
    
    # Draw back button
    return draw_back_button(20, 20)

# ------------------ MULTITHREADED EXECUTION ------------------
class SchedulingThread(threading.Thread):
    """Thread class for running scheduling algorithms without blocking UI"""
    def __init__(self, algorithm, tasks, time_quantum=None):
        super().__init__()
        self.algorithm = algorithm
        self.tasks = tasks
        self.time_quantum = time_quantum
        self.result = None
        
    def run(self):
        try:
            if self.algorithm == "FCFS":
                self.result = fcfs(self.tasks)
            elif self.algorithm == "SJN":
                self.result = sjn(self.tasks)
            elif self.algorithm == "Round Robin":
                self.result = rr(self.tasks, self.time_quantum)
            elif self.algorithm == "Rate Monotonic":
                self.result = rm(self.tasks)
            elif self.algorithm == "EDF":
                self.result = edf(self.tasks)
        except Exception as e:
            print(f"Error in scheduling thread: {e}")
            self.result = None

class AlgorithmComparer:
    """Class to manage comparison of multiple scheduling algorithms"""
    def __init__(self):
        self.results = {}
        self.running = False
        self.threads = []
        self.is_complete = False
        
    def start_comparison(self, tasks, algorithms, time_quantum=None):
        """Start comparing multiple algorithms with the same task set"""
        self.results = {}
        self.running = True
        self.is_complete = False
        self.threads = []
        
        for algo in algorithms:
            if algo == "Round Robin" and time_quantum is not None:
                thread = SchedulingThread(algo, tasks, time_quantum)
            else:
                thread = SchedulingThread(algo, tasks)
            thread.start()
            self.threads.append((algo, thread))
        
    def check_progress(self):
        """Check if all algorithms have completed"""
        if not self.running:
            return False
            
        all_done = True
        for algo, thread in self.threads:
            if thread.is_alive():
                all_done = False
            elif algo not in self.results and thread.result is not None:
                self.results[algo] = thread.result
                
        if all_done and len(self.results) == len(self.threads):
            self.running = False
            self.is_complete = True
            
        return self.is_complete
    
    def get_results(self):
        """Get the results of the comparison"""
        return self.results

# ------------------ MAIN APP CLASS ------------------
class SchedulingApp:
    """Main application class to manage the CPU scheduling visualizer"""
    def __init__(self):
        # Input fields
        self.task_names_field = InputField(50, 200, 200, 40, "Task Names (P1, P2, ...)")
        self.arrival_times_field = InputField(50, 280, 200, 40, "Arrival Times", is_numeric=True)
        self.burst_times_field = InputField(50, 360, 200, 40, "Burst Times", is_numeric=True)
        self.deadline_field = InputField(50, 440, 200, 40, "Deadlines (Only for EDF)", is_numeric=True)
        self.period_field = InputField(50, 520, 200, 40, "Periods (Only for RM)", is_numeric=True)
        self.time_quantum_field = InputField(50, 600, 200, 40, "Time Quantum (only for RR)", "1", is_numeric=True)
        
        # Buttons
        self.run_button = Button(300, 600, 150, 40, "Run Algorithm")
        self.compare_button = Button(480, 600, 150, 40, "Compare All")
        self.clear_button = Button(660, 600, 150, 40, "Clear All")
        
        # Dropdown menu for algorithm selection
        self.algorithm_dropdown = Dropdown(300, 520, 250, 40, [
            "FCFS", "SJN", "Round Robin", "Rate Monotonic", "EDF"
        ])
        
        # State variables
        self.current_tasks = []
        self.current_schedule = []
        self.max_time = 0
        self.comparison_results = {}
        self.view_mode = "main"  # 'main' or 'comparison'
        
        # Threading related
        self.scheduler_thread = None
        self.algorithm_comparer = AlgorithmComparer()
        
        # Scroll position for task table
        self.scroll_y = 0
        self.max_scroll = 0
        
        # Precomputed results
        self.metrics = {}
        
        # Status message
        self.status_message = ""
        self.status_time = 0
        
        # Z-index management
        self.dropdown_active = False
        
    def show_status(self, message, duration=3000):
        """Show a status message for a certain duration"""
        self.status_message = message
        self.status_time = pygame.time.get_ticks() + duration
        
    def create_tasks_from_input(self):
        """Create task objects from input fields"""
        # Get input values
        task_names = self.task_names_field.text.split(',')
        task_names = [name.strip() for name in task_names if name.strip()]
        
        arrival_times = parse_input_list(self.arrival_times_field.text)
        burst_times = parse_input_list(self.burst_times_field.text)
        deadlines = parse_input_list(self.deadline_field.text)
        periods = parse_input_list(self.period_field.text)
        
        # Validate inputs
        if not task_names or not arrival_times or not burst_times:
            self.show_status("Please enter task names, arrival times, and burst times")
            return []
            
        if len(task_names) != len(arrival_times) or len(task_names) != len(burst_times):
            self.show_status("Number of tasks, arrival times, and burst times must match")
            return []
            
        # Create tasks
        tasks = []
        for i in range(len(task_names)):
            deadline = deadlines[i] if i < len(deadlines) else None
            period = periods[i] if i < len(periods) else None
            
            tasks.append(Task(
                task_names[i],
                arrival_times[i],
                burst_times[i],
                deadline,
                period
            ))
            
        return tasks
        
    def run_algorithm(self):
        """Run the selected scheduling algorithm"""
        # Get tasks from input
        tasks = self.create_tasks_from_input()
        if not tasks:
            return
            
        # Get selected algorithm
        algorithm = self.algorithm_dropdown.selected
        
        # Get time quantum for Round Robin
        time_quantum = 1
        if algorithm == "Round Robin":
            try:
                time_quantum = int(self.time_quantum_field.text or "1")
                if time_quantum <= 0:
                    self.show_status("Time quantum must be positive")
                    return
            except ValueError:
                self.show_status("Invalid time quantum")
                return
                
        # Reset current results
        self.current_tasks = []
        self.current_schedule = []
        self.max_time = 0
        
        # Start algorithm in a separate thread
        self.show_status(f"Running {algorithm}...")
        self.scheduler_thread = SchedulingThread(algorithm, tasks, time_quantum)
        self.scheduler_thread.start()
        
    def run_comparison(self):
        """Run comparison of all scheduling algorithms"""
        # Get tasks from input
        tasks = self.create_tasks_from_input()
        if not tasks:
            return
            
        # Get time quantum for Round Robin
        time_quantum = 1
        try:
            time_quantum = int(self.time_quantum_field.text or "1")
            if time_quantum <= 0:
                self.show_status("Time quantum must be positive")
                return
        except ValueError:
            self.show_status("Invalid time quantum")
            return
            
        # Start comparison
        self.show_status("Running comparison...")
        algorithms = ["FCFS", "SJN", "Round Robin", "Rate Monotonic", "EDF"]
        self.algorithm_comparer.start_comparison(tasks, algorithms, time_quantum)
        
    def clear_all(self):
        """Clear all input fields and results"""
        self.task_names_field.text = ""
        self.arrival_times_field.text = ""
        self.burst_times_field.text = ""
        self.deadline_field.text = ""
        self.period_field.text = ""
        self.time_quantum_field.text = "1"
        
        self.current_tasks = []
        self.current_schedule = []
        self.max_time = 0
        self.comparison_results = {}
        self.metrics = {}
        
        self.show_status("All data cleared")
        
    def handle_events(self):
        """Handle input events"""
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # Handle scrolling for task table
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_y += event.y * 20
                self.scroll_y = max(min(self.scroll_y, 0), -self.max_scroll)
                
            # Handle view mode specific events
            if self.view_mode == "main":
                # Handle input fields
                self.task_names_field.handle_event(event)
                self.arrival_times_field.handle_event(event)
                self.burst_times_field.handle_event(event)
                self.deadline_field.handle_event(event)
                self.period_field.handle_event(event)
                self.time_quantum_field.handle_event(event)
                
                # Handle algorithm dropdown
                self.algorithm_dropdown.handle_event(event, mouse_pos)
                
                # Handle buttons
                if self.run_button.is_clicked(mouse_pos, event):
                    self.run_algorithm()
                elif self.compare_button.is_clicked(mouse_pos, event):
                    self.run_comparison()
                    if self.algorithm_comparer.running:
                        self.view_mode = "comparison"
                elif self.clear_button.is_clicked(mouse_pos, event):
                    self.clear_all()
                    
            elif self.view_mode == "comparison":
                # In comparison view, only handle back button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    back_button_rect = pygame.Rect(20, 20, 120, 40)
                    if back_button_rect.collidepoint(mouse_pos):
                        self.view_mode = "main"
                        
        # Check hover state for buttons
        if self.view_mode == "main":
            self.run_button.check_hover(mouse_pos)
            self.compare_button.check_hover(mouse_pos)
            self.clear_button.check_hover(mouse_pos)
                
        return True
        
    def update(self):
        """Update application state"""
        # Check if scheduler thread is running
        if self.scheduler_thread and not self.scheduler_thread.is_alive() and self.scheduler_thread.result:
            self.current_tasks, self.current_schedule = self.scheduler_thread.result
            self.max_time = max([end for _, _, end in self.current_schedule]) if self.current_schedule else 0
            self.metrics = calculate_metrics(self.current_tasks)
            self.scheduler_thread = None
            self.show_status("Algorithm execution completed")
            
        # Check if comparison is running
        if self.view_mode == "comparison" and self.algorithm_comparer.running:
            if self.algorithm_comparer.check_progress():
                self.comparison_results = self.algorithm_comparer.get_results()
                self.show_status("Comparison completed")
                
        # Clear status message after timeout
        if self.status_message and pygame.time.get_ticks() > self.status_time:
            self.status_message = ""
            
    def draw_main_view(self):
        """Draw the main application view"""
        # Draw title
        title_text = title_font.render("CPU SCHEDULING VISUALIZER", True, HEADING_COLOR)
        title_rect = title_text.get_rect(center=(800, 50))
        screen.blit(title_text, title_rect)
        
        # Draw panel for input fields
        panel_rect = pygame.Rect(30, 120, 240, 540)
        pygame.draw.rect(screen, CARD_BG, panel_rect, border_radius=10)
        panel_title = heading_font.render("Task Configuration", True, HEADING_COLOR)
        screen.blit(panel_title, (panel_rect.centerx - panel_title.get_width()//2, 130))
        
        # Draw input fields
        self.task_names_field.draw()
        self.arrival_times_field.draw()
        self.burst_times_field.draw()
        self.deadline_field.draw()
        self.period_field.draw()
        self.time_quantum_field.draw()
        
        # Draw algorithm selection panel
        algo_panel = pygame.Rect(300, 450, 510, 130)
        pygame.draw.rect(screen, CARD_BG, algo_panel, border_radius=10)
        algo_title = heading_font.render("Algorithm Selection", True, HEADING_COLOR)
        screen.blit(algo_title, (algo_panel.centerx - algo_title.get_width()//2, 460))
        
        # Draw results panel
        results_panel = pygame.Rect(300, 120, 1270, 310)
        pygame.draw.rect(screen, CARD_BG, results_panel, border_radius=10)
        results_title = heading_font.render("Gantt Chart", True, HEADING_COLOR)
        screen.blit(results_title, (results_panel.centerx - results_title.get_width()//2, 130))
        
        # Draw Gantt chart
        if self.current_schedule:
            draw_gantt_chart(320, 170, 1230, 60, self.max_time, self.current_schedule)
            
            # Draw metrics
            metrics_y = 280
            if self.metrics:
                cpu_util = self.metrics.get('cpu_utilization', 0)
                avg_wait = self.metrics.get('avg_waiting', 0)
                avg_turn = self.metrics.get('avg_turnaround', 0)
                
                metrics_text = heading_font.render(f"CPU Utilization: {cpu_util:.2f}%", True, TEXT_COLOR)
                screen.blit(metrics_text, (320, metrics_y))
                
                metrics_text = heading_font.render(f"Avg Waiting Time: {avg_wait:.2f}", True, TEXT_COLOR)
                screen.blit(metrics_text, (620, metrics_y))
                
                metrics_text = heading_font.render(f"Avg Turnaround Time: {avg_turn:.2f}", True, TEXT_COLOR)
                screen.blit(metrics_text, (920, metrics_y))
        else:
            no_data = heading_font.render("No data to display. Run an algorithm to see results.", True, TEXT_COLOR)
            screen.blit(no_data, (results_panel.centerx - no_data.get_width()//2, 190))
            
        # Draw task results table panel
        table_panel = pygame.Rect(840, 450, 730, 400)
        pygame.draw.rect(screen, CARD_BG, table_panel, border_radius=10)
        table_title = heading_font.render("Results Table", True, HEADING_COLOR)
        screen.blit(table_title, (table_panel.centerx - table_title.get_width()//2, 460))
        
        # Draw results table
        if self.current_tasks:
            draw_results_table(860, 500, 690, 330, self.current_tasks)
        else:
            no_table = heading_font.render("No tasks to display", True, TEXT_COLOR)
            screen.blit(no_table, (table_panel.centerx - no_table.get_width()//2, 550))
        
        # Draw buttons
        self.run_button.draw()
        self.compare_button.draw()
        self.clear_button.draw()
        
        # Draw algorithm dropdown - draw last to appear on top of buttons
        self.algorithm_dropdown.draw()
        
        # Draw status message if present
        if self.status_message:
            status_bg = pygame.Rect(0, 870, 1600, 30)
            pygame.draw.rect(screen, (50, 50, 50), status_bg)
            status_text = font.render(self.status_message, True, (255, 255, 255))
            screen.blit(status_text, (10, 875))
            
    def run(self):
        """Main application loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update application state
            self.update()
            
            # Clear screen
            screen.fill(BG_COLOR)
            
            # Draw appropriate view
            if self.view_mode == "main":
                self.draw_main_view()
            elif self.view_mode == "comparison":
                back_button = draw_comparison_view(self.comparison_results)
                back_button.check_hover(pygame.mouse.get_pos())
                
                # Draw status message if present
                if self.status_message:
                    status_bg = pygame.Rect(0, 870, 1600, 30)
                    pygame.draw.rect(screen, (50, 50, 50), status_bg)
                    status_text = font.render(self.status_message, True, (255, 255, 255))
                    screen.blit(status_text, (10, 875))
                    
                # Draw loading indicator if comparison is still running
                if self.algorithm_comparer.running:
                    running_text = heading_font.render("Running comparison...", True, TEXT_COLOR)
                    screen.blit(running_text, (800 - running_text.get_width()//2, 450))
            
            # Update display
            pygame.display.flip()
            clock.tick(60)

# ------------------ MAIN EXECUTION ------------------
if __name__ == "__main__":
    try:
        app = SchedulingApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()