# FEA Friction Calibration GUI

An interactive Streamlit application designed to calibrate Abaqus contact parameters against physical torsional test data. 

## Overview
Implicit FEA solvers using penalty contact methods are highly sensitive to friction coefficients, friction decay over slip distance, and allowable elastic slip tolerances. This tool utilizes a mathematical surrogate model to simulate the moment-rotation response of a joint, allowing engineers to tune these parameters in real-time before submitting expensive FEA jobs.

## Features
* **Live Curve Matching:** Visually align the FEA surrogate curve with empirical TES data.
* **Parameter Sliders:** Instantly adjust static friction, two-stage kinetic decay, and slip tolerance limits.
* **Delta Tracking:** Monitor the deviation in peak moment capacity and early-stage stiffness.

## Installation

1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/fea-friction-calibration.git](https://github.com/YOUR_USERNAME/fea-friction-calibration.git)
   cd fea-friction-calibration
