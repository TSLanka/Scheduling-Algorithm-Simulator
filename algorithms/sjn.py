from .base import SchedulingAlgorithm

class SJN(SchedulingAlgorithm):
    """Shortest Job Next scheduling algorithm"""
    
    def run(self):
        """
        Run SJN scheduling (non-preemptive)
        """
        processes = sorted(self.processes.copy(), key=lambda x: x['arrival'])
        current_time = 0
        gantt_chart = []
        n = len(processes)
        
        # Initialize tracking variables
        remaining_burst = [p['burst'] for p in processes]
        waiting_times = [0] * n
        turnaround_times = [0] * n
        completed = 0
        
        while completed != n:
            # Find available processes with remaining burst
            available = []
            for i, p in enumerate(processes):
                if p['arrival'] <= current_time and remaining_burst[i] > 0:
                    available.append((i, remaining_burst[i]))
            
            if not available:
                # No process available at current time, advance time to next arrival
                next_arrival = float('inf')
                for i, p in enumerate(processes):
                    if remaining_burst[i] > 0 and p['arrival'] > current_time:
                        next_arrival = min(next_arrival, p['arrival'])
                
                if next_arrival != float('inf'):
                    current_time = next_arrival
                else:
                    # Should not happen with valid input
                    current_time += 1
                continue
            
            # Select process with shortest remaining burst
            proc_idx, burst = min(available, key=lambda x: x[1])
            
            # Execute process to completion
            gantt_chart.append((processes[proc_idx]['name'], current_time, current_time + burst))
            
            # Update metrics
            turnaround_times[proc_idx] = current_time + burst - processes[proc_idx]['arrival']
            waiting_times[proc_idx] = turnaround_times[proc_idx] - processes[proc_idx]['burst']
            
            current_time += burst
            remaining_burst[proc_idx] = 0
            completed += 1
        
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