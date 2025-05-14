from .base import SchedulingAlgorithm

class FCFS(SchedulingAlgorithm):
    """First-Come-First-Serve scheduling algorithm"""
    
    def run(self):
        """
        Run FCFS scheduling
        """
        # Create a copy to avoid modifying the original
        processes = sorted(self.processes.copy(), key=lambda x: x['arrival'])
        current_time = 0
        gantt_chart = []
        n = len(processes)
        
        waiting_times = [0] * n
        turnaround_times = [0] * n
        
        for i, p in enumerate(processes):
            # If there's a gap between current time and next arrival
            if current_time < p['arrival']:
                current_time = p['arrival']
            
            # Add this execution to gantt chart
            gantt_chart.append((p['name'], current_time, current_time + p['burst']))
            
            # Calculate metrics for this process
            turnaround_times[i] = current_time + p['burst'] - p['arrival']
            waiting_times[i] = turnaround_times[i] - p['burst']
            
            # Update current time
            current_time += p['burst']
        
        # Calculate averages
        avg_waiting = sum(waiting_times) / n if n > 0 else 0
        avg_turnaround = sum(turnaround_times) / n if n > 0 else 0
        
        # Calculate CPU utilization
        busy_time = sum(p['burst'] for p in processes)
        total_time = current_time
        cpu_utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
        
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