# CPU Scheduling Visualizer

A modern, interactive application to visualize and compare various CPU scheduling algorithms in operating systems.


## Overview

This application provides a graphical interface to visualize how different CPU scheduling algorithms work, allowing users to understand their operation and compare their performance metrics. The visualizer supports the following scheduling algorithms:

- **First Come First Served (FCFS)**
- **Shortest Job Next (SJN)**
- **Round Robin (RR)**
- **Rate Monotonic (RM)**
- **Earliest Deadline First (EDF)**

## Features

- **Interactive Visualization**: See how processes are scheduled in real-time with a Gantt chart
- **Multithreaded Execution**: Algorithms run in background threads, keeping the UI responsive
- **Algorithm Comparison**: Compare multiple scheduling algorithms side by side
- **Detailed Metrics**: View CPU utilization, average waiting time, and average turnaround time
- **Custom Task Creation**: Define your own process sets with custom parameters
- **Real-time Feedback**: Status messages and progress indicators for long operations

## Requirements

- Python 3.7+
- Pygame 2.0.0+

## Installation

1. Clone this repository or download the source code
2. Make sure you have Python installed on your system
3. Install the required packages:

```bash
pip install pygame
```

## Running the Application

To run the application, simply execute the main Python file:

```bash
python ImprovedCPUScheduler.py
```

## Usage Guide

### Task Configuration

1. **Task Names**: Enter comma-separated task names (e.g., P1, P2, P3)
2. **Arrival Times**: Enter comma-separated arrival times for each task
3. **Burst Times**: Enter comma-separated burst/execution times for each task
4. **Deadlines** (optional): Enter deadlines for tasks if using EDF algorithm
5. **Periods** (optional): Enter periods for tasks if using Rate Monotonic algorithm
6. **Time Quantum**: Enter the time quantum value for Round Robin algorithm

### Running Algorithms

1. Select the desired scheduling algorithm from the dropdown menu
2. Click "Run Algorithm" to visualize the selected algorithm
3. View the Gantt chart and results table to understand the scheduling
4. Click "Compare All" to run all algorithms and see comparative metrics
5. Click "Clear All" to reset the application

### Reading the Results

- **Gantt Chart**: Shows the timeline of task execution
- **Results Table**: Shows detailed metrics for each task:
  - Arrival Time: When the task enters the ready queue
  - Burst Time: Total execution time required
  - Finish Time: When the task completes execution
  - Turnaround Time: Time from arrival to completion
  - Waiting Time: Time spent waiting in the ready queue

- **Comparison Charts**: When comparing algorithms, view:
  - Average Waiting Time
  - Average Turnaround Time
  - CPU Utilization (%)

## Algorithm Descriptions

### First Come First Served (FCFS)
- Processes are executed in the order they arrive
- Non-preemptive scheduling algorithm
- Simple but can cause long waiting times for short processes

### Shortest Job Next (SJN)
- Processes with shortest burst time are executed first
- Non-preemptive scheduling algorithm
- Optimizes average waiting time but may cause starvation

### Round Robin (RR)
- Each process gets a small unit of CPU time (time quantum)
- After time quantum expires, the process is preempted and added to the end of the ready queue
- Provides good response time for interactive systems

### Rate Monotonic (RM)
- Assigns priorities based on process periods (shorter period = higher priority)
- Preemptive priority-based scheduling algorithm
- Commonly used in real-time systems

### Earliest Deadline First (EDF)
- Assigns priorities based on absolute deadlines
- Preemptive priority-based scheduling algorithm
- Optimal for meeting deadlines if system is not overloaded

## Troubleshooting

- **No visualization appears**: Ensure you've entered valid task data and selected an algorithm
- **Application feels slow**: Reduce the number of tasks or simplify the task set
- **Invalid inputs**: Ensure all numeric inputs are valid numbers separated by commas

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Pygame

