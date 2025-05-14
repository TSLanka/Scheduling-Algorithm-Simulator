def rr_scheduler(self, time_quantum=4):
    processes = sorted(self.processes, key=lambda x: x['arrival'])
    ready_queue = []
    current_time = 0
    gantt_chart = []
    metrics = {'waiting_times': [0]*len(processes), 'turnaround_times': [0]*len(processes)}
    
    remaining_burst = [p['burst'] for p in processes]
    completed = 0
    n = len(processes)
    
    while completed != n:
        # Add arriving processes to ready queue
        for i, p in enumerate(processes):
            if p['arrival'] <= current_time and remaining_burst[i] > 0 and i not in [q[0] for q in ready_queue]:
                ready_queue.append((i, remaining_burst[i]))
        
        if not ready_queue:
            current_time += 1
            continue
        
        # Get next process
        proc_idx, burst = ready_queue.pop(0)
        exec_time = min(time_quantum, burst)
        
        # Record execution
        gantt_chart.append((processes[proc_idx]['name'], current_time, current_time + exec_time))
        
        # Update remaining burst
        remaining_burst[proc_idx] -= exec_time
        current_time += exec_time
        
        # Update waiting times for other processes
        for i, _ in enumerate(processes):
            if i != proc_idx and processes[i]['arrival'] <= current_time and remaining_burst[i] > 0:
                metrics['waiting_times'][i] += exec_time
        
        # Re-add to queue if not finished
        if remaining_burst[proc_idx] > 0:
            ready_queue.append((proc_idx, remaining_burst[proc_idx]))
        else:
            completed += 1
            metrics['turnaround_times'][proc_idx] = current_time - processes[proc_idx]['arrival']
    
    # Calculate averages
    avg_waiting = sum(metrics['waiting_times']) / n
    avg_turnaround = sum(metrics['turnaround_times']) / n
    cpu_utilization = (sum(p['burst'] for p in processes) / current_time) * 100
    
    return {
        'gantt_chart': gantt_chart,
        'total_time': current_time,
        'metrics': {
            'avg_waiting': avg_waiting,
            'avg_turnaround': avg_turnaround,
            'cpu_utilization': cpu_utilization
        }
    }