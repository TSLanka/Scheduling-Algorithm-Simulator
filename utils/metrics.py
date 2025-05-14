def calculate_metrics(simulation_results):
    """
    simulation_results: list of dicts with keys 'pid', 'start', 'finish', 'arrival', 'burst'
    """
    n = len(simulation_results)
    total_waiting = 0
    total_turnaround = 0

    for proc in simulation_results:
        turnaround = proc['finish'] - proc['arrival']
        waiting = turnaround - proc['burst']
        total_waiting += waiting
        total_turnaround += turnaround

    avg_waiting = total_waiting / n if n else 0
    avg_turnaround = total_turnaround / n if n else 0

    # CPU utilization
    if simulation_results:
        first_arrival = min(proc['arrival'] for proc in simulation_results)
        last_finish = max(proc['finish'] for proc in simulation_results)
        total_burst = sum(proc['burst'] for proc in simulation_results)
        cpu_util = (total_burst / (last_finish - first_arrival)) * 100 if last_finish > first_arrival else 0
    else:
        cpu_util = 0

    return {
        'avg_waiting_time': avg_waiting,
        'avg_turnaround_time': avg_turnaround,
        'cpu_utilization': cpu_util
    }
