# 🤖 EcoSort EV3: Autonomous Recycling Robot

**An intelligent Lego Mindstorms EV3 robotics system designed to navigate a facility track, identify trash materials, and sort them into dedicated recycling stations.**

## 🚀 Overview

EcoSort is a precision-engineered robotics solution built using the Pybricks MicroPython framework. The robot operates on a closed-loop track, utilizing a combination of PID-style line following and ultrasonic distance sensing to interact with its environment.

The system features a custom-built dual-motor "Lift & Clamp" mechanism. When an object is detected, the robot executes a sophisticated sampling routine—using reflection and color data to distinguish between plastic, paper, and other materials—before navigating to the correct station for autonomous offloading.

## ✨ Key Features

- 🛤️ **Strict Line Navigation**: Advanced reflection-based steering with dynamic corner detection and "white-space" calibration.
- 🏗️ **Dual-Stage Actuation**: Motorized arm and clamp system with stall-detection for secure object handling.
- 🔍 **Material Identification**: A multi-sample "majority vote" algorithm to accurately categorize trash (Plastic vs. Paper) based on a configurable database.
- 📍 **Dynamic Map Awareness**: Intelligent station tracking that uses "corners passed" and sensor confirmation counts to identify drop-off zones.
- 🛡️ **Fail-Safe Initialization**: Self-calibrating startup sequence that resets arm positions and tests clamp force.
- 📊 **Diagnostic Tooling**: Integrated data loggers and sensor test scripts for real-time environment calibration.

## 🛠️ Tech Stack

- **Platform**: Lego Mindstorms EV3
- **Language**: MicroPython (ev3dev)
- **Library**: Pybricks API
- **IDE**: VS Code (with EV3 MicroPython extension)

## 📦 Installation

### 1. Prerequisites
- Ensure your EV3 Brick is running the [ev3dev-lang-python](https://www.ev3dev.org/docs/getting-started/) bootable microSD image.
- Install the **Lego Education EV3 MicroPython** extension in VS Code.

### 2. Clone the Repository
```bash
git clone [https://github.com/your-username/recycling-robot.git](https://github.com/your-username/recycling-robot.git)
cd recycling-robot

```

### 3. Workspace Setup

Open the folder in VS Code. The `.vscode/settings.json` is pre-configured to handle the MicroPython interpreter and deployment settings.

## 🏃‍♂️ How to Run

1. **Connect**: Link your EV3 Brick to your computer via USB, Bluetooth, or Wi-Fi.
2. **Deploy**: Press **F5** or use the "Download and Run" button in the EV3 Device Browser tab in VS Code.
3. **Calibrate**:
* Run `calibrate_arm.py` to set the physical zero-point for the lift.
* Run `data_logger.py` to verify the reflection thresholds for your specific track lighting.


4. **Execute**: Start `main.py` and press the **Center Button** on the brick to begin the mission.

## 📖 Usage Guide

1. **Startup**: The robot will announce "Initialize" and move the arm to a safe height.
2. **Line Following**: Place the robot on the black line. It uses a `TURN_GAIN` of -1.2 to stay centered on the edge.
3. **Object Detection**: Place a "trash" item within 50mm of the front ultrasonic sensor. The robot will stop, pick up the item, and identify it.
4. **Sorting**: The robot continues until it detects the color/reflection signature of the matching station (Red, Blue, or Orange).
5. **Unloading**: Upon arrival, it executes the `unload_sequence`, nudging forward to ensure the item clears the bin before returning to the line.

## 📂 Project Structure

```text
.
├── extract_files/           # Modularized logic for hardware and actions
├── old/                     # Legacy test scripts and backup logic
├── actions.py               # core logic for picking, dropping, and identifying
├── calibrate_arm.py         # Utility to manually set the arm's zero position
├── config.py                # PID gains, sensor thresholds, and trash database
├── data_logger.py           # Real-time sensor output for track calibration
├── hardware.py              # Port definitions (A-D, S1-S4) and DriveBase setup
├── main.py                  # Primary mission control loop
├── test01_sensors.py        # Quick-start script to verify sensor wiring
├── test02_drive.py          # Isolated line-following test
└── info.txt                 # Hardware mapping and brainstorming notes

```
