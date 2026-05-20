import re
from datetime import datetime, timezone

import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors

def load_turbidity_data(jaia_h5_path: str, start_time_dt=None, end_time_dt=None) -> pd.DataFrame:
    """
        Function to extract turbidity data from the Jaiabot h5 file.
        Input:
        - jaia_h5_path: path to h5 file with relevant GPS data for this deployment
        - start_time: Start time of Bathybot Mission, i.e. time in water, if known. Python Datetime Object or None
        - end_time: End time of Bathybot Mission, i.e. time out of water, if known. Python Datetime Object or None
        Outputs:
        - pandas dataframe containing all turbidity data: turbidity_df or None if file path or h5 key can't be found
    """
    try:
        jaia_h5 = h5py.File(jaia_h5_path, 'r')
    except IOError:
        print(f"Jaia h5 file {jaia_h5_path} not found. Check the path.")
        return None

    turbidity_utime_path = '/jaiabot::fluorometer/jaiabot.sensor.protobuf.TurnerCFluor/_utime_'
    turbidity_concentration_path = '/jaiabot::fluorometer/jaiabot.sensor.protobuf.TurnerCFluor/concentration'
    turbidity_concentration_voltage_path = '/jaiabot::fluorometer/jaiabot.sensor.protobuf.TurnerCFluor/concentration_voltage'

    try:
        turbidity_utime = jaia_h5[turbidity_utime_path][:]
        turbidity_concentration = jaia_h5[turbidity_concentration_path][:]
        turbidity_concentration_voltage = jaia_h5[turbidity_concentration_voltage_path][:]
    except KeyError:
        print(f"Turbidity data h5 keys not found in the provided h5. Was C-FLUOR sensor installed for this deployment?")
        jaia_h5.close()
        return None

    jaia_h5.close()

    turbidity_dict = {'_utime_': turbidity_utime, 'concentration': turbidity_concentration, 'concentration_voltage': turbidity_concentration_voltage}

    turbidity_df = pd.DataFrame(data=turbidity_dict)

    if start_time_dt is not None:
        start_time_utime = start_time_dt.timestamp() * 1_000_000
        turbidity_df = turbidity_df[(turbidity_df['_utime_'] >= start_time_utime)]
    if end_time_dt is not None:
        end_time_utime = end_time_dt.timestamp() * 1_000_000
        turbidity_df = turbidity_df[(turbidity_df['_utime_'] <= end_time_utime)]

    return turbidity_df.reset_index(drop=True) # 10 hz

def load_pos_data(jaia_h5_path: str, start_time_dt=None, end_time_dt=None) -> pd.DataFrame:
    """
        Function to extract GPS data from the Jaiabot h5 file.
        Input:
        - jaia_h5_path: path to h5 file with relevant GPS data for this deployment
        - start_time: Start time of Bathybot Mission, i.e. time in water, if known. Python Datetime Object or None
        - end_time: End time of Bathybot Mission, i.e. time out of water, if known. Python Datetime Object or None
        Outputs:
        - pandas dataframe containing all pos data: pos_df or None if file path or h5 key can't be found
    """
    try:
        jaia_h5 = h5py.File(jaia_h5_path, 'r')
    except IOError:
        print(f"Jaia h5 file {jaia_h5_path} not found. Check the path.")
        return None

    pos_utime_path = '/goby::middleware::groups::gpsd::tpv/goby.middleware.protobuf.gpsd.TimePositionVelocity/_utime_'
    pos_lat_path = '/goby::middleware::groups::gpsd::tpv/goby.middleware.protobuf.gpsd.TimePositionVelocity/location/lat'
    pos_lon_path = '/goby::middleware::groups::gpsd::tpv/goby.middleware.protobuf.gpsd.TimePositionVelocity/location/lon'

    try:
        pos_utime = jaia_h5[pos_utime_path][:]
        pos_lat = jaia_h5[pos_lat_path][:]
        pos_lon = jaia_h5[pos_lon_path][:]
    except KeyError:
        print(f"GPS data h5 keys not found in the provided h5. Is this a Jaiabot h5?")
        jaia_h5.close()
        return None

    jaia_h5.close()

    pos_dict = {'_utime_': pos_utime, 'lat': pos_lat, 'lon': pos_lon}

    pos_df = pd.DataFrame(pos_dict) # 5hz

    if start_time_dt is not None:
        start_time_utime = start_time_dt.timestamp() * 1_000_000
        pos_df = pos_df[(pos_df['_utime_'] >= start_time_utime)]
    if end_time_dt is not None:
        end_time_utime = end_time_dt.timestamp() * 1_000_000
        pos_df = pos_df[(pos_df['_utime_'] <= end_time_utime)]

    return pos_df.reset_index(drop=True)  # 5 hz

def load_depth_data(jaia_h5_path: str, start_time_dt=None, end_time_dt=None) -> pd.DataFrame:
    """
        Function to extract depth data computed using Jaiabot pressure sensor from the Jaiabot h5 file.
        Filters obviously bad values such as depth < 0.
        Input:
        - jaia_h5_path: path to h5 file with relevant pressure sensor data for this deployment
        - start_time: Start time of Bathybot Mission, i.e. time in water, if known. Python Datetime Object or None
        - end_time: End time of Bathybot Mission, i.e. time out of water, if known. Python Datetime Object or None
        Outputs:
        - pandas dataframe containing all depth data: depth_df or None if file path or h5 key can't be found
    """
    try:
        jaia_h5 = h5py.File(jaia_h5_path, 'r')
    except IOError:
        print(f"Jaia h5 file {jaia_h5_path} not found. Check the path.")
        return None

    depth_utime_path = '/jaiabot::pressure_adjusted/jaiabot.protobuf.PressureAdjustedData/_utime_'
    # using sensor depth as C-FLUOR is mounted at same vertical position as pressure sensor
    depth_sensor_depth_path = '/jaiabot::pressure_adjusted/jaiabot.protobuf.PressureAdjustedData/sensor_depth'

    try:
        depth_utime = jaia_h5[depth_utime_path][:]
        depth_sensor_depth = jaia_h5[depth_sensor_depth_path][:]
    except KeyError:
        print(f"Depth h5 keys not found in the provided h5. Was the pressure sensor installed for this deployment?")
        jaia_h5.close()
        return None

    jaia_h5.close()

    depth_dict = {'_utime_': depth_utime, 'depth': depth_sensor_depth}

    depth_df = pd.DataFrame(data=depth_dict)
    depth_df = depth_df[depth_df['depth'] >= 0]

    if start_time_dt is not None:
        start_time_utime = start_time_dt.timestamp() * 1_000_000
        depth_df = depth_df[(depth_df['_utime_'] >= start_time_utime)]
    if end_time_dt is not None:
        end_time_utime = end_time_dt.timestamp() * 1_000_000
        depth_df = depth_df[(depth_df['_utime_'] <= end_time_utime)]

    return depth_df.reset_index(drop=True) # 10 hz

def load_dive_data(jaia_h5_path: str, start_time_dt=None, end_time_dt=None) -> pd.DataFrame:
    """
        Function to extract dive data computed using task packets from the Jaiabot h5 file.
        Input:
        - jaia_h5_path: path to h5 file with relevant dive data for this deployment
        - start_time: Start time of Bathybot Mission, i.e. time in water, if known. Python Datetime Object or None
        - end_time: End time of Bathybot Mission, i.e. time out of water, if known. Python Datetime Object or None
        Outputs:
        - pandas dataframe containing all dive data: dive_df or None if file path or h5 key can't be found
    """
    try:
        jaia_h5 = h5py.File(jaia_h5_path, 'r')
    except IOError:
        print(f"Jaia h5 file {jaia_h5_path} not found. Check the path.")
        return None

    task_packet_path_pattern = 'jaiabot::task_packet;[0-9]+'
    task_packet_base_path = None

    # iterate over key list to find task_packet key: version number increments after each version update
    for key in list(jaia_h5.keys()):
        if re.match(task_packet_path_pattern, key):
            task_packet_base_path = '/' + key + '/jaiabot.protobuf.TaskPacket/'
            break

    if task_packet_base_path is None:
        print(f"Jaia task packet h5 key not found in the provided h5. Were tasks performed on this deployment?")
        return None

    task_packet_start_time_path = task_packet_base_path + 'start_time'
    task_packet_end_time_path = task_packet_base_path + 'end_time'
    task_packet_type_path = task_packet_base_path + 'type'
    task_packet_lat_path = task_packet_base_path + 'dive/start_location/lat'
    task_packet_lon_path = task_packet_base_path + 'dive/start_location/lon'

    try:
        task_packet_start_time = jaia_h5[task_packet_start_time_path][:]
        task_packet_end_time = jaia_h5[task_packet_end_time_path][:]
        task_packet_type = jaia_h5[task_packet_type_path][:]
        task_packet_lat = jaia_h5[task_packet_lat_path][:]
        task_packet_lon = jaia_h5[task_packet_lon_path][:]
    except KeyError:
        print(f"Jaia task packet h5 keys not found in the provided h5. Were tasks performed on this deployment?")
        return None

    task_packet_dict = {'start_time': task_packet_start_time,
                        'end_time': task_packet_end_time,
                        'type': task_packet_type,
                        'lat': task_packet_lat,
                        'lon': task_packet_lon}

    task_packet_df = pd.DataFrame(data=task_packet_dict)

    # Jaia MissionTask.TaskType Enum defined here: https://github.com/jaiarobotics/jaiabot/blob/2.y/src/lib/messages/mission.proto#L195
    JAIA_MISSIONTASK_TASKTYPE_DIVE_ENUM_VALUE = 1

    dive_df = task_packet_df[task_packet_df.type == JAIA_MISSIONTASK_TASKTYPE_DIVE_ENUM_VALUE]

    if len(dive_df) == 0:
        print(f"Dive data not found. Were dive tasks performed on this deployment?")
        return None

    dive_df = dive_df.drop(columns=['type'])

    if start_time_dt is not None:
        start_time_utime = start_time_dt.timestamp() * 1_000_000
        dive_df = dive_df[(dive_df['start_time'] >= start_time_utime)]
    if end_time_dt is not None:
        end_time_utime = end_time_dt.timestamp() * 1_000_000
        dive_df = dive_df[(dive_df['end_time'] <= end_time_utime)]

    return dive_df.reset_index(drop=True)


def fix_concentration_values(turbidity_df: pd.DataFrame, offset_volts: float, coefficient_NTU_per_volt: float):
    """
        Function to perform inplace correction of concentration values, then removes obviously bad readings (concentration < 0 NTU).
        Correction performed using formula: (concentration_voltage - offset_volts)*coefficient_NTU_per_volt
        Input:
        - turbidity_df: dataframe containing jaia turbidity data from load_turbidity_data()
        - offset_volts: voltage offset for concentration values, representing the sensor's voltage reading at 0 NTU
        - coefficient_NTU_per_volt: Slope at which NTU increases as sensor's voltage reading increases
        Outputs:
        - None. Conversion is performed inplace on the dataframe
    """
    turbidity_df['concentration'] = (turbidity_df['concentration_voltage'] - offset_volts)*coefficient_NTU_per_volt
    turbidity_df.drop(turbidity_df[turbidity_df['concentration'] < 0].index, inplace=True)
    turbidity_df.reset_index(drop=True, inplace=True)
    return

def interp_jaia_h5s(turbidity_df: pd.DataFrame, pos_df: pd.DataFrame, depth_df: pd.DataFrame) -> pd.DataFrame:
    """
        Function to merge Jaiabot turbidity, pos, and depth dataframes into a single dataframe.
        Linearly interpolates turbidity and depth datapoints to approximate these values at each gps data timestamp,
        as this datastream has the lowest publishing rate.
        Input:
        - turbidity_df: dataframe with turbidity sensor data, created by load_turbidity_data() (10hz)
        - pos_df: dataframe with GPS data, created by load_pos_data() (5hz)
        - depth_df: dataframe with depth data, created by load_depth_data() (10hz)
        Outputs:
        - pandas dataframe containing all turbidity, pos, and depth data interpolated to the same time series: turbidity_survey_df
    """
    pos_utime = pos_df['_utime_']
    turbidity_utime = turbidity_df['_utime_']
    depth_utime = depth_df['_utime_']

    turbidity_concentration_interp = np.interp(pos_utime, turbidity_utime, turbidity_df['concentration'], left=np.nan, right=np.nan)
    turbidity_concentration_voltage_interp = np.interp(pos_utime, turbidity_utime, turbidity_df['concentration_voltage'], left=np.nan, right=np.nan)

    depth_sensor_depth_interp = np.interp(pos_utime, depth_utime, depth_df['depth'], left=np.nan, right=np.nan)

    turbidity_survey_df = pd.DataFrame()

    turbidity_survey_df['_utime_'] = pos_utime
    turbidity_survey_df['lat'] = pos_df['lat']
    turbidity_survey_df['lon'] = pos_df['lon']

    turbidity_survey_df['concentration'] = turbidity_concentration_interp
    turbidity_survey_df['concentration_voltage'] = turbidity_concentration_voltage_interp

    turbidity_survey_df['depth'] = depth_sensor_depth_interp

    turbidity_survey_df = turbidity_survey_df.dropna()
    return turbidity_survey_df.reset_index(drop=True)

def plot_ground_track(turbidity_survey_df: pd.DataFrame):
    """
        Function to plot 2D ground track of jaiabot survey, colored by turbidity value.
        Input:
        - turbidity_survey_df: dataframe with turbidity, pos, and depth data, created by load_turbidity_data() (5hz)
        Outputs:
        - 2D ground track turbidity survey plot
    """
    survey_plot_df = turbidity_survey_df.copy()
    survey_plot_df.drop(survey_plot_df[survey_plot_df['lat'] == 0].index, inplace=True) # survey values from pre-GPS fix and during dives

    lat = survey_plot_df['lat']
    lon = survey_plot_df['lon']
    concentration = survey_plot_df['concentration']
    start_time = min(survey_plot_df['_utime_'])

    pc = plt.scatter(lon, lat, c=concentration, cmap='ocean', label=f"Turbidity Data Points: {len(concentration)}")
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Turbidity Map')
    plt.suptitle(f"Jaiabot Turbidity Survey: " + datetime.fromtimestamp(start_time/1_000_000, tz=timezone.utc).strftime("%A, %B %d, %Y %H:%M:%S UTC"))
    plt.colorbar(pc, label='Turbidity (NTU)', location='right')
    plt.legend(loc="upper left")
    ax = plt.gca()
    ax.set_xlim((min(lon) - 0.0001, max(lon) + 0.0001))
    ax.set_ylim((min(lat) - 0.0001, max(lat) + 0.0001))
    ax.set_aspect('equal')
    ax.ticklabel_format(useOffset=False, style='plain')
    plt.tight_layout()
    plt.show()
    plt.clf()

def plot_turbidity_dives(turbidity_survey_df: pd.DataFrame, dives_df: pd.DataFrame):
    survey_plot_df = turbidity_survey_df.copy()

    dive_min_turbidity = 501.0 # sensor max value is 500 NTU
    dive_max_turbidity = -1.0 # sensor min value is 0 NTU

    dive_start_times = []
    dive_end_times = []
    dive_lats = []
    dive_lons = []
    dive_turbidity_dfs = []
    dive_mean_turbiditys = []
    for dive in dives_df.itertuples(index=False): # (start_time, end_time, lat, lon)
        dive_pts_mask = (survey_plot_df["_utime_"] >= dive.start_time) & (survey_plot_df["_utime_"] <= dive.end_time)
        if dive_pts_mask.sum() == 0:
            continue

        dive_start_times.append(dive.start_time)
        dive_end_times.append(dive.end_time)
        dive_lats.append(dive.lat)
        dive_lons.append(dive.lon)

        # create df subset with dive data points only
        curr_turbidity_survey_df = survey_plot_df.copy(deep=True)
        curr_turbidity_survey_df = curr_turbidity_survey_df[dive_pts_mask]
        curr_turbidity_survey_df.reset_index(drop=True, inplace=True)

        if min(curr_turbidity_survey_df['concentration']) < dive_min_turbidity:
            dive_min_turbidity = min(curr_turbidity_survey_df['concentration'])
        if max(curr_turbidity_survey_df['concentration']) > dive_max_turbidity:
            dive_max_turbidity = max(curr_turbidity_survey_df['concentration'])

        dive_turbidity_dfs.append(curr_turbidity_survey_df)
        dive_mean_turbiditys.append(curr_turbidity_survey_df['concentration'].mean())

        # remove dive points from survey_plot_df to not be plotted in 2d tract
        survey_plot_df = survey_plot_df[~dive_pts_mask]
        survey_plot_df.reset_index(drop=True, inplace=True)


    for curr_turbidity_survey_df in dive_turbidity_dfs:
        pc = plt.scatter(curr_turbidity_survey_df['concentration'], curr_turbidity_survey_df['depth'], c=curr_turbidity_survey_df['concentration'], vmin=dive_min_turbidity, vmax=dive_max_turbidity)
        plt.colorbar(pc, label='Turbidity (NTU)', location='right')
        plt.xlabel('Turbidity (NTU)')
        plt.ylabel('Depth (m)')
        plt.title(f'Turbidity Profile at {dive.lat}, {dive.lon}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
        plt.clf()

    survey_plot_df.drop(survey_plot_df[survey_plot_df['lat'] == 0].index,
                        inplace=True)  # survey values from pre-GPS fix and during dives

    lat = survey_plot_df['lat']
    lon = survey_plot_df['lon']
    concentration = survey_plot_df['concentration']
    start_time = min(survey_plot_df['_utime_'])

    survey_min_turbidity = min(concentration)
    survey_max_turbidity = max(concentration)

    pc = plt.scatter(lon, lat, c=concentration, label=f"Turbidity Data Points: {len(concentration)}", vmin=survey_min_turbidity, vmax=survey_max_turbidity, zorder=5)
    plt.scatter(dive_lons, dive_lats, c=dive_mean_turbiditys, marker='s', s=100, edgecolor='k', label=f"Jaiabot Dives, Mean Turbidity", vmin=survey_min_turbidity, vmax=survey_max_turbidity, zorder=10)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(f'Turbidity Map')
    plt.suptitle(
        f"Jaiabot Turbidity Survey: " + datetime.fromtimestamp(start_time / 1_000_000, tz=timezone.utc).strftime(
            "%A, %B %d, %Y %H:%M:%S UTC"))
    plt.colorbar(pc, label='Turbidity (NTU)', location='right')
    plt.legend(loc="upper left")
    ax = plt.gca()
    ax.set_xlim((min(lon) - 0.0001, max(lon) + 0.0001))
    ax.set_ylim((min(lat) - 0.0001, max(lat) + 0.0001))
    ax.set_aspect('equal')
    ax.ticklabel_format(useOffset=False, style='plain')
    plt.tight_layout()
    plt.show()
    plt.clf()

if __name__ == '__main__':
    jaia_h5_path = r"C:\Users\RDCHLMS9\PycharmProjects\jb_turbidity_plotting\data\bot1_fleet14_20260518T132514.h5"
    start_time = "18:00:49" # Format 'HH:MM:SS' in UTC
    end_time = "18:30:00"  # Format 'HH:MM:SS' in UTC
    plot_dive_profiles = True # If true, plots individual dive profiles using plot_turbidity_dives(), else plots ground track using plot_ground_track()

    date = re.findall(r"_\d{8}T", jaia_h5_path)[0][1:-1]
    time = re.findall(r"T\d{6}.", jaia_h5_path)[0][1:-1]


    if start_time is not None:
        start_time_dt = datetime.strptime(date + start_time + "+0000", "%Y%m%d%H:%M:%S%z")
    else:
        start_time_dt = None
    if end_time is not None:
        end_time_dt = datetime.strptime(date + end_time + "+0000", "%Y%m%d%H:%M:%S%z")
    else:
        end_time_dt = None

    turbidity_df = load_turbidity_data(jaia_h5_path, start_time_dt, end_time_dt)
    pos_df = load_pos_data(jaia_h5_path, start_time_dt, end_time_dt)
    depth_df = load_depth_data(jaia_h5_path, start_time_dt, end_time_dt)
    turbidity_survey_df = interp_jaia_h5s(turbidity_df, pos_df, depth_df)

    if plot_dive_profiles:
        dives_df = load_dive_data(jaia_h5_path, start_time_dt, end_time_dt)
        plot_turbidity_dives(turbidity_survey_df, dives_df)
    else:
        plot_ground_track(turbidity_survey_df)