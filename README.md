# Traffic Sim 🚗💨

A Python-based physics simulation engine for modeling vehicle dynamics, driver reaction behaviors, and sector-based congestion on circular tracks. Includes interactive real-time 2D Matplotlib visualizers for kinematics, traffic flow, and live speed/congestion histograms.

---

## 🌟 Key Features

* **Modular Track Generation:** Create custom tracks with distinct road segments (`highway`, `road`, `city`, `school`, `construction`) each possessing unique speed limits, lengths, and visual styles.
* **Realistic Physics Engine:**
  * **Car-Following Model:** Computes reaction distances and inter-vehicle acceleration based on dynamic gaps ($s_{diff}$) and safe distance thresholds ($s_{min}$).
  * **Sector Compliance:** Models speed adjustments based on upcoming sector limits using smooth reaction functions.
  * **Numerical Integration:** Uses Euler integration (`ei_s`, `ei_v`) to track exact positions and velocities across discrete time steps ($\Delta t$).
* **Real-Time Interactive Animation (`Animation` class):**
  * **Track View:** Circular map showing real-time car positions and distinct color-coded road segments.
  * **Live Congestion Histogram:** Displays segment-by-segment vehicle speeds alongside static sector speed limits (`--` target line).
  * **Dynamic Congestion Highlighting:** Bars dynamically shift color based on flow condition:
    * 💙 **Sky Blue:** Free-flowing traffic ($\ge 70\%$ sector limit)
    * 🟧 **Orange:** Moderate congestion ($35\%\text{--}70\%$ sector limit)
    * 🔴 **Crimson Red:** Severe congestion / stopped traffic ($<35\%$ sector limit or $<0.5\text{ m/s}$)
* **Kinematic Profiling:** Matplotlib plot function to review full time-series history ($s(t)$ and $v(t)$) for every car.

---

## 📁 Project Structure

```text
drive_sim/
├── examples/            # Example scripts and usage demonstrations
│   └── example.py
├── traffic_sim/        # Main simulation package
│   ├── __init__.py     # Package exports
│   ├── animation.py    # Matplotlib animation & plotting engine
│   ├── cars.py         # Vehicle state tracking & reaction properties
│   ├── constants.py    # Enums for road types, constants, and indexes
│   ├── geometry.py     # Distance calculations & track segment mapping
│   ├── physics.py      # Acceleration models & Euler integration
│   ├── road.py         # Base road definition
│   └── track.py        # Linked-list road track builder & management
├── tests/              # Test suite
│   └── test_traffic_sim.py
├── pyproject.toml      # Project configuration & build dependencies
└── README.md           # Project documentation

## 🚀 Installation

### Requirements
* Python $\ge 3.9$
* `numpy`, `matplotlib`, `pandas`

### Install locally in editable mode
```bash
git clone [https://github.com/matijalakner/traffic-simulator](https://github.com/matijalakner/traffic-simulator)
cd drive_sim

# Activate your virtual environment (if using the project venv)
source venv/bin/activate

# Install package in editable mode with dev tools
pip install -e .[dev].
```

---

## 💡 Quick Start

```python
from traffic_sim import Cars

# Initialize simulation
# 10 cars, starting speed = 15 m/s, time-step dt = 0.1s
sim = Cars(number_of_cars=10, v_initial=15.0, dt=0.1, name="Ring Track Test")

# Execute animation window
sim.animate_cars()
```

---

## 📊 Segment Types & Speed Limits

| Segment Type | Speed Limit (m/s) | Default Length (m) | Symbol |
| :--- | :---: | :---: | :---: |
| **Highway** | 36 | 800 | 🟩 |
| **Road** | 25 | 500 | 🟨 |
| **City** | 14 | 250 | 🟧 |
| **School Zone** | 8 | 50 | 🟥 |
| **Construction** | 2 | 10 | 🟪 |

---

## 🛠️ Configuration & Customization

You can dynamically adjust sector speed limits during runtime or simulation callbacks:

```python
# Change speed limit of sector index 2 to 10 m/s
sim.change_speed_limit(segment=2, new_speed=10.0)
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
