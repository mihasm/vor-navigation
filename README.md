# VOR Navigation

A Python tool for calculating VOR (VHF Omnidirectional Range) navigation routes for aviation. This tool helps pilots plan flight paths using VOR stations and providing METAR/TAF weather reports.

---

## ⚠️ **IMPORTANT SAFETY DISCLAIMER**

**This tool is for FLIGHT SIMULATION AND EDUCATIONAL PURPOSES ONLY.**

**DO NOT use this software for actual flight navigation or planning real-world flights.**

- This software provides approximate route calculations based on simplified aviation data
- Real flight navigation requires certified avionics, current aeronautical charts, and professional pilot judgment
- Weather information is for informational purposes only and should not replace official aviation weather briefings
- Always consult official aviation authorities, current NOTAMs, and certified navigation sources before any flight
- The authors and contributors are not responsible for any accidents, incidents, or damages resulting from the use of this software

**Flying safely requires professional training, current certifications, and adherence to aviation regulations. This tool is not a substitute for proper flight planning and navigation procedures.**

---

## Features

- Calculate optimal flight routes using VOR navigation stations
- METAR/TAF weather reports for airports
- Magnetic variation calculations
- Support for customizable route parameters

## Installation

### Prerequisites

- Python 3.8 or higher

### Install from source

```bash
git clone https://github.com/yourusername/vor-navigation.git
cd vor-navigation
pip install -e .
```

### Dependencies

The package automatically installs all required dependencies.

## Usage

### Command Line Interface

```bash
# Calculate route between two airports
vor-navigation KJFK KLAX

# Use custom parameters
vor-navigation KJFK KLAX --max_deviation 30 --max_turn_angle 60 --cruise 25000

# Generate random route for testing
vor-navigation --random
```

### Parameters

- `departure`: ICAO code of departure airport
- `destination`: ICAO code of destination airport
- `--max_deviation`: Maximum deviation between course to destination and course to next waypoint (default: 45 degrees)
- `--max_turn_angle`: Maximum turn angle between waypoints (default: 90 degrees)
- `--optimum_vor_distance`: Optimum distance between VOR stations (default: 50 NM)
- `--max_wpts`: Maximum number of waypoints before error (default: 100)
- `--random`: Generate random route for fun or testing

### Output

The tool provides:
- Route waypoints with VOR frequencies and magnetic variation
- METAR/TAF reports for airports
- Route statistics

## Running Tests

```bash
python -m pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

