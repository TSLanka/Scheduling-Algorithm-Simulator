class SchedulingAlgorithm:
    """Base class for all scheduling algorithms"""
    
    def __init__(self, processes):
        """
        Initialize with process list
        
        processes: list of dictionaries with keys:
            - 'name': Process name/ID
            - 'arrival': Arrival time
            - 'burst': Burst/execution time
            - 'deadline': Deadline (optional, for EDF)
            - 'period': Period (optional, for RM/EDF)
        """
        self.processes = processes
        
    def run(self):
        """
        Run the scheduling algorithm
        Returns a dictionary containing:
            - 'gantt_chart': List of tuples (process_name, start_time, end_time)
            - 'total_time': Total execution time
            - 'metrics': Dictionary of performance metrics
        """
        raise NotImplementedError("Subclasses must implement this method")