from .base import SchedulingAlgorithm

class FCFS(SchedulingAlgorithm):
    """First-Come-First-Serve scheduling algorithm"""
    
    def run(self):
        """
        Run FCFS scheduling
        """
        processes = sorted(self.processes, key=lambda x: x['arrival'])
        current_time = 0
        gantt_chart = []
        metrics = {
            'waiting_times': [0] * len(processes),
            'turnaround_times': [0] * len(processes)
        }
        
        for i, p in enumerate(processes):
            if current_time < p['arrival']:
                current_time = p['arrival']
            
            gantt_chart.append((p['name'], current_time, current_time + p['burst']))
            
            metrics['turnaround_times'][i] = current_time + p['burst'] - p['arrival']
            metrics['waiting_times'][i] = current_time - p['arrival']
            
            current_time += p['burst']
        
        avg_waiting = sum(metrics['waiting_times']) / len(processes) if processes else 0
        avg_turnaround = sum(metrics['turnaround_times']) / len(processes) if processes else 0
        cpu_utilization = (sum(p['burst'] for p in processes) / current_time) * 100 if current_time > 0 else 0
        
        return {
            'gantt_chart': gantt_chart,
            'total_time': current_time,
            'metrics': {
                'avg_waiting': avg_waiting,
                'avg_turnaround': avg_turnaround,
                'cpu_utilization': cpu_utilization,
                'waiting_times': metrics['waiting_times'],
                'turnaround_times': metrics['turnaround_times']
            }
        }