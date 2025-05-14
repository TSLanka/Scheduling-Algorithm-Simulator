import pygame
import pygame_gui

class ProcessTable:
    """A table to display processes and their properties"""
    
    def __init__(self, rect, manager):
        self.rect = rect
        self.manager = manager
        self.processes = []
        
        # Container panel
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=rect,
            manager=manager
        )
        
        # Headers
        headers = ["ID", "Arrival", "Burst", "Deadline", "Period", "Remove"]
        header_width = rect.width / len(headers)
        
        for i, header in enumerate(headers):
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (i * header_width, 0),
                    (header_width, 30)
                ),
                text=header,
                manager=manager,
                container=self.panel
            )
        
        # Initial empty state message
        self.empty_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (0, 40),
                (rect.width, 30)
            ),
            text="No processes added yet",
            manager=manager,
            container=self.panel
        )
        
        self.delete_buttons = []
        self.row_height = 30
        self.header_height = 30
    
    def add_process(self, process):
        """Add a process to the table"""
        self.processes.append(process)
        self._rebuild_table()
    
    def remove_process(self, index):
        """Remove a process from the table"""
        if 0 <= index < len(self.processes):
            del self.processes[index]
            self._rebuild_table()
    
    def _rebuild_table(self):
        """Rebuild the entire table display"""
        # Remove empty label if present
        if hasattr(self, 'empty_label') and self.empty_label is not None:
            self.empty_label.kill()
            self.empty_label = None
        
        # Remove all existing rows
        for button in self.delete_buttons:
            button.kill()
        self.delete_buttons = []
        
        # If no processes, show empty message and return
        if not self.processes:
            self.empty_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (0, 40),
                    (self.rect.width, 30)
                ),
                text="No processes added yet",
                manager=self.manager,
                container=self.panel
            )
            return
        
        # Create new rows
        headers = ["ID", "Arrival", "Burst", "Deadline", "Period", "Remove"]
        col_width = self.rect.width / len(headers)
        
        for i, process in enumerate(self.processes):
            row_y = self.header_height + (i * self.row_height)
            
            # Process ID
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (0, row_y),
                    (col_width, self.row_height)
                ),
                text=str(process.get('pid', process.get('name', 'N/A'))),
                manager=self.manager,
                container=self.panel
            )
            
            # Arrival time
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (col_width, row_y),
                    (col_width, self.row_height)
                ),
                text=str(process.get('arrival', 'N/A')),
                manager=self.manager,
                container=self.panel
            )
            
            # Burst time
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (col_width * 2, row_y),
                    (col_width, self.row_height)
                ),
                text=str(process.get('burst', 'N/A')),
                manager=self.manager,
                container=self.panel
            )
            
            # Deadline (if applicable)
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (col_width * 3, row_y),
                    (col_width, self.row_height)
                ),
                text=str(process.get('deadline', '-')),
                manager=self.manager,
                container=self.panel
            )
            
            # Period (if applicable)
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (col_width * 4, row_y),
                    (col_width, self.row_height)
                ),
                text=str(process.get('period', '-')),
                manager=self.manager,
                container=self.panel
            )
            
            # Delete button
            delete_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (col_width * 5, row_y),
                    (col_width, self.row_height)
                ),
                text="X",
                manager=self.manager,
                container=self.panel,
                object_id=f"delete_button_{i}"
            )
            self.delete_buttons.append(delete_button)
    
    def handle_event(self, event):
        """Handle events for the table"""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for i, button in enumerate(self.delete_buttons):
                if event.ui_element == button:
                    self.remove_process(i)
                    return True
        return False
    
    def get_processes(self):
        """Get the current list of processes"""
        return self.processes


class CustomButton(pygame_gui.elements.UIButton):
    """A custom button with additional functionality"""
    
    def __init__(self, relative_rect, text, manager, action_callback=None, **kwargs):
        super().__init__(relative_rect=relative_rect, text=text, manager=manager, **kwargs)
        self.action_callback = action_callback
    
    def handle_event(self, event):
        """Handle button click event"""
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self:
            if self.action_callback:
                try:
                    # First try to call with event parameter
                    return self.action_callback(event)
                except TypeError:
                    # Fall back to calling without parameters if the callback doesn't accept them
                    return self.action_callback()
        return False