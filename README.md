# Jaiabot Turbidity Survey Plotting Utility

This script parses and processes turbidity data collected by Jaiabot vehicle sensors. 
It extracts turbidity, GPS coordinates, and depth readings from mission H5 files (`bot#_fleet#_YYmmddTHHMMSS.h5`), 
aligns the datastreams using linear interpolation, 
and generates detailed 2D survey maps and optional vertical profile plots.

---

### Installation & Setup

To run this utility in your mission support environment, ensure you have the required Python dependencies installed.

| Step | Action                     | Details / Command                                                                                                         |
|:-----|:---------------------------|:--------------------------------------------------------------------------------------------------------------------------|
| 1    | Install Required Libraries | Ensure all required dependencies are installed using the provided requirements file:<br>`pip install -r requirements.txt` |
| 2    | Verify Script Access       | Place `jb_turbidity_plotting.py` and your mission `.h5` files in an accessible workspace directory.                       |
| 3    | Execute Utility            | Run the script from your terminal using Python 3:<br>`python3 jb_turbidity_plotting.py path/to/jaia.h5`                   |

---

### Command Line Interface (CLI) Arguments

You can run the script via terminal. The CLI interface allows you to filter specific windows of a mission and configure visualization outputs without modifying any code.

| Argument             | Input Type            | Default Value             | Description                                                                                                                     |
|:---------------------|:----------------------|:--------------------------|:--------------------------------------------------------------------------------------------------------------------------------|
| `jaia_h5_path`       | Positional (Required) | *None*                    | Absolute or relative path to the Jaiabot H5 data file (e.g., `data/bot1_fleet14_20260518T132514.h5`).                           |
| `--start-time`       | Option (Optional)     | `None`                    | Crop datastreams to start at this time in UTC (Format: `HH:MM:SS`). If omitted, processing starts at the beginning of the file. |
| `--end-time`         | Option (Optional)     | `None`                    | Crop datastreams to end at this time in UTC (Format: `HH:MM:SS`). If omitted, processing continues to the end of the file.      |
| `--no-dive-profiles` | Flag (Optional)       | *False (Profiles Active)* | Disable plotting individual 1D depth/turbidity profiles and generate only a 2D survey ground track plot instead.                |
| `--save-dir`         | Option (Optional)     | `"."` (Current Directory) | Destination folder path for generated `.png` plot outputs. Defaults to the directory where the script is run.                   |

---

### Mission Use Cases & Commands

Below is a guide to executing common visualization tasks with this utility:

| Mission Objective           | Example CLI Command                                                                                         | Expected Visual Outputs                                                                                                                                                  |
|:----------------------------|:------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Full Mission Profile**    | `python jb_turbidity_plotting.py bot1_fleet14_20260518T132514.h5`                                           | Generates and saves separate vertical turbidity profile plots for every dive event found throughout the full duration of the `.h5` log, saving to the current directory. |
| **Ground Track Survey Map** | `python jb_turbidity_plotting.py bot1_fleet14_20260518T132514.h5 --no-dive-profiles`                        | Generates a 2D map of coordinates, color-coded by turbidity values, showing spatial distribution across the water surface.                                               |
| **Targeted Time-Window**    | `python jb_turbidity_plotting.py bot1_fleet14_20260518T132514.h5 --start-time 18:00:49 --end-time 18:30:00` | Filters out sensor data outside of the 18:00:49 to 18:30:00 UTC time frame. Highly useful if the vehicle spent pre-mission time on deck or post-mission transit.         |
| **Output Redirection**      | `python jb_turbidity_plotting.py bot1_fleet14_20260518T132514.h5 --save-dir ./mission_reports/figs`         | Outputs all generated graphics directly to a designated sub-folder instead of cluttering your root directory.                                                            |

---
