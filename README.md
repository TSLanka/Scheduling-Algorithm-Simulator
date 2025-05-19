## 🖥️ CPU Scheduling Visualizer

An interactive Python-based GUI application to simulate and visualize various CPU scheduling algorithms. This tool is designed for educational purposes and supports:

* **First Come First Served (FCFS)**
* **Shortest Job Next (SJN)**
* **Round Robin (RR)**
* **Rate Monotonic (RM)**
* **Earliest Deadline First (EDF)**

---

### 📦 Requirements

Ensure you have Python and Pygame installed:

```bash
pip install pygame
```

---

### 🚀 How to Run

1. Clone or download this repository.
2. Navigate to the folder containing the `SchedulingVisualizer.py` file.
3. Run the application:

```bash
python SchedulingVisualizer.py
```

The GUI window will open and allow you to:

* Choose a scheduling algorithm from a dropdown.
* Enter arrival times, burst times, and (if required) deadlines, periods, or time quantum.
* Click **Simulate** to visualize the Gantt chart, metrics, and task details.

---

### ✏️ Input Format

* **Arrival Time** and **Burst Time** must be comma or space-separated integers.
  Example: `0, 1, 2, 3`

* **Time Quantum** (for RR): a single integer.
  Example: `2`

* **Deadline** (for EDF): comma-separated values.
  Example: `10, 8, 12`

* **Period** (for RM): comma-separated values.
  Example: `20, 10, 30`

---

### 📊 Output Features

* Dynamic **Gantt Chart**
* CPU **Utilization**
* Average **Turnaround** and **Waiting Time**
* Scrollable **Task Table**

---

### 🧠 Educational Use

This visualizer is a great learning tool for students and educators in operating systems or real-time systems courses.

---

### 🛠️ Built With

* Python 🐍
* Pygame 🎮

---

### 📜 License

This project is open-source and available under the MIT License.

---

Let me know if you'd like to generate this as a file or customize it for packaging (e.g., as a `.exe`).
