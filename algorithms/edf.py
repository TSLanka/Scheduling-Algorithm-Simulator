def edf_scheduler(self):
    processes = self.processes.copy()
    current_time = 0
    gantt_chart = []
    deadline_misses = 0
    total_jobs = 0
    
    max_time = 100  # Simulation duration
    remaining_time = [0] * len(processes)
    next_release = [p['arrival'] for p in processes]
    deadlines = [p['arrival'] + p['period'] for p in processes]
    
    while current_time < max_time:
        # Check for new job releases
        for i, p in enumerate(processes):
            if current_time >= next_release[i]:
                remaining_time[i] = p['burst']
                next_release[i] += p['period']
                deadlines[i] = next_release[i]
                total_jobs += 1
        
        # Find job with earliest deadline among ready jobs
        ready_jobs = [(i, deadlines[i]) for i in range(len(processes)) if remaining_time[i] > 0]
        
        if ready_jobs:
            selected, _ = min(ready_jobs, key=lambda x: x[1])
            
            # Execute for 1 time unit
            gantt_chart.append((processes[selected]['name'], current_time, current_time + 1))
            remaining_time[selected] -= 1
            
            # Check if job completed
            if remaining_time[selected] == 0:
                deadline = deadlines[selected] - processes[selected]['period']
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