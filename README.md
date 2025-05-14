# CPU Scheduling Algorithms Simulator

A visual simulator for common CPU scheduling algorithms used in operating systems. This interactive tool allows you to create processes with various parameters and visualize how different scheduling algorithms handle them.

## Features

- **Multiple Scheduling Algorithms:**
  - First-Come-First-Serve (FCFS)
  - Shortest Job Next (SJN)
  - Round Robin (RR) with configurable time quantum
  - Rate Monotonic (RM) for real-time systems
  - Earliest Deadline First (EDF) for real-time systems

- **Interactive GUI:**
  - Add processes with custom parameters
  - View processes in a table format
  - Visualize scheduling with Gantt charts
  - See performance metrics for each algorithm

- **Performance Metrics:**
  - Average waiting time
  - Average turnaround time
  - CPU utilization
  - Deadline misses (for real-time algorithms)

## Installation

1. Make sure you have Python 3.x installed
2. Install dependencies:
   ```
   pip install pygame pygame-gui
   ```
3. Clone or download this repository
4. Run the simulator:
   ```
   python main.py
   ```

## Usage

1. **Adding Processes:**
   - Enter process details (ID, arrival time, burst time)
   - For real-time algorithms (RM, EDF), also enter deadline and period
   - Click "Add Process" to add the process to the simulation

2. **Running Simulations:**
   - Select the desired scheduling algorithm from the dropdown
   - For Round Robin, set the time quantum
   - Click "Start Simulation" to run the scheduler

3. **Analyzing Results:**
   - View the Gantt chart showing process execution over time
   - Check the metrics at the bottom for performance analysis
   - Compare results across different algorithms

## Algorithm Details

### FCFS (First-Come-First-Serve)
- Non-preemptive algorithm
- Processes are executed in order of arrival
- Simple but can lead to convoy effect

### SJN (Shortest Job Next)
- Non-preemptive algorithm 
- Executes process with shortest burst time
- Optimal for minimizing average waiting time

### Round Robin
- Preemptive algorithm
- Each process gets a small time slice (quantum)
- Good for time-sharing systems

### Rate Monotonic (RM)
- Priority-based preemptive algorithm for periodic tasks
- Higher priority to processes with shorter periods
- Optimal for fixed-priority scheduling

### Earliest Deadline First (EDF)
- Dynamic priority preemptive algorithm for real-time systems
- Assigns highest priority to the process with closest deadline
- Optimal for dynamic-priority scheduling

## Project Structure

```
scheduling-simulator/
├── algorithms/           # Scheduling algorithm implementations
│   ├── __init__.py
│   ├── base.py           # Base algorithm class
│   ├── fcfs.py           # First-Come-First-Serve
│   ├── sjn.py            # Shortest Job Next
│   ├── rr.py             # Round Robin
│   ├── rm.py             # Rate Monotonic
│   └── edf.py            # Earliest Deadline First
├── gui/                  # GUI components
│   ├── __init__.py
│   ├── interface.py      # Main interface
│   └── components.py     # UI components
├── utils/                # Utility functions
│   ├── __init__.py
│   └── metrics.py        # Performance metrics calculation
├── main.py               # Application entry point
└── theme.json            # UI theme configuration
```

## Contributing

Contributions are welcome! You can:
- Add new scheduling algorithms
- Improve the visualization
- Enhance the UI
- Fix bugs or optimize code

## License

This project is released under the MIT License.