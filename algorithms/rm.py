from .base import SchedulingAlgorithm

class RateMonotonic(SchedulingAlgorithm):
    """Rate Monotonic scheduling algorithm"""
    
    def run(self):
        """
        Run Rate Monotonic scheduling
        """
        # Sort by period (priority)
        processes = sorted(self.processes, key=lambda x: x['period'])
        current_time = 0
        gantt_chart = []
        deadline_misses = 0
        total_jobs = 0
        
        # We'll simulate for LCM of periods or a fixed time (here 100 for simplicity)
        max_time = 100
        remaining_time = [0] * len(processes)
        next_release = [p['arrival'] for p in processes]
        
        while current_time < max_time:
            # Check for new job releases
            for i, p in enumerate(processes):
                if current_time >= next_release[i]:
                    remaining_time[i] = p['burst']
                    next_release[i] += p['period']
                    total_jobs += 1
            
            # Find highest priority ready job
            selected = None
            for i in range(len(processes)):
                if remaining_time[i] > 0:
                    selected = i
                    break
            
            if selected is not None:
                # Execute for 1 time unit
                gantt_chart.append((processes[selected]['name'], current_time, current_time + 1))
                remaining_time[selected] -= 1
                
                # Check if job completed
                if remaining_time[selected] == 0:
                    deadline = next_release[selected] - processes[selected]['period'] + processes[selected]['deadline']
                    if current_time + 1 > deadline:
                        deadline_misses += 1
            else:
                current_time += 1
                continue
            
            current_time += 1
        
        miss_rate = (deadline_misses / total_jobs) * 100 if total_jobs > 0 else 0
        
        return {
            'gantt_chart': gantt_chart,
            'total_time': current_time,
            'metrics': {
                'deadline_misses': deadline_misses,
                'total_jobs': total_jobs,
                'miss_rate': miss_rate
            }
        }