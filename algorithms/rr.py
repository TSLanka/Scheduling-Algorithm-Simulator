from .base import SchedulingAlgorithm

class SJN(SchedulingAlgorithm):
    """Shortest Job Next scheduling algorithm"""
    
    def run(self):
        """
        Run SJN scheduling (non-preemptive)
        """
        processes = sorted(self.processes, key=lambda x: x['arrival'])
        current_time = 0
        gantt_chart = []
        metrics = {
            'waiting_times': [0] * len(processes),
            'turnaround_times': [0] * len(processes)
        }
        
        remaining_burst = [p['burst'] for p in processes]
        completed = 0
        n = len(processes)
        
        while completed != n:
            # Find available processes with remaining burst
            available = []
            for i, p in enumerate(processes):
                if p['arrival'] <= current_time and remaining_burst[i] > 0:
                    available.append((i, remaining_burst[i]))
            
            if not available:
                current_time += 1
                continue
            
            # Select process with shortest remaining burst
            proc_idx, burst = min(available, key=lambda x: x[1])
            
            # Execute process to completion
            gantt_chart.append((processes[proc_idx]['name'], current_time, current_time + burst))
            
            # Update metrics
            metrics['turnaround_times'][proc_idx] = current_time + burst - processes[proc_idx]['arrival']
            metrics['waiting_times'][proc_idx] = metrics['turnaround_times'][proc_idx] - processes[proc_idx]['burst']
            
            current_time += burst
            remaining_burst[proc_idx] = 0
            completed += 1
        
        avg_waiting = sum(metrics['waiting_times']) / n if n > 0 else 0
        avg_turnaround = sum(metrics['turnaround_times']) / n if n > 0 else 0
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