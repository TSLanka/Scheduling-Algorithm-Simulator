from .base import SchedulingAlgorithm

class RoundRobin(SchedulingAlgorithm):
    """Round Robin scheduling algorithm"""
    
    def __init__(self, processes, time_quantum=2):
        """
        Initialize with process list and time quantum
        
        processes: list of dictionaries with keys:
            - 'name': Process name/ID
            - 'arrival': Arrival time
            - 'burst': Burst/execution time
        time_quantum: Time slice for each process execution
        """
        super().__init__(processes)
        self.time_quantum = time_quantum
    
    def run(self):
        """
        Run Round Robin scheduling
        """
        processes = sorted(self.processes, key=lambda x: x['arrival'])
        n = len(processes)
        
        # Create working copies
        remaining_burst = [p['burst'] for p in processes]
        completion_time = [0] * n
        waiting_times = [0] * n
        turnaround_times = [0] * n
        
        current_time = 0
        gantt_chart = []
        
        # Continue until all processes are done
        while True:
            done = True
            
            # Go through all processes
            for i in range(n):
                # If process has remaining burst time and has arrived
                if remaining_burst[i] > 0 and processes[i]['arrival'] <= current_time:
                    done = False
                    
                    # Execute for time quantum or remaining time, whichever is smaller
                    execution_time = min(self.time_quantum, remaining_burst[i])
                    
                    # Add to Gantt chart
                    gantt_chart.append((processes[i]['name'], current_time, current_time + execution_time))
                    
                    # Update remaining time
                    remaining_burst[i] -= execution_time
                    current_time += execution_time
                    
                    # If process is complete, update completion time
                    if remaining_burst[i] == 0:
                        completion_time[i] = current_time
                        turnaround_times[i] = completion_time[i] - processes[i]['arrival']
                        waiting_times[i] = turnaround_times[i] - processes[i]['burst']
            
            # If all processes are done, break
            if done:
                break
                
            # If no process is available at current time, advance time
            no_ready_process = True
            for i in range(n):
                if remaining_burst[i] > 0 and processes[i]['arrival'] <= current_time:
                    no_ready_process = False
                    break
            
            if no_ready_process:
                next_arrival = float('inf')
                for i in range(n):
                    if remaining_burst[i] > 0 and processes[i]['arrival'] > current_time:
                        next_arrival = min(next_arrival, processes[i]['arrival'])
                
                if next_arrival != float('inf'):
                    current_time = next_arrival
        
        avg_waiting = sum(waiting_times) / n if n > 0 else 0
        avg_turnaround = sum(turnaround_times) / n if n > 0 else 0
        cpu_utilization = (sum(p['burst'] for p in processes) / current_time) * 100 if current_time > 0 else 0
        
        return {
            'gantt_chart': gantt_chart,
            'total_time': current_time,
            'metrics': {
                'avg_waiting': avg_waiting,
                'avg_turnaround': avg_turnaround,
                'cpu_utilization': cpu_utilization,
                'waiting_times': waiting_times,
                'turnaround_times': turnaround_times
            }
        }