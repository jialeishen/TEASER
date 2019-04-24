#!/usr/bin/env python
# coding=utf-8
"""
Run VDI 6007 test case 1
"""

import os
import numpy as np

from teaser.logic.simulation.vdi_core import VDICore
from teaser.examples.verification.vdi6007_testcases.vdi6007shared import prepare_thermal_zone

def load_res(filename):
    res = np.loadtxt(filename, delimiter=",", skiprows=1)  # Skip time step 0

    # ignore time
    result = res[:, 1:res.shape[1]]

    day1 = result[0:24, :]
    day2 = result[24:48, :]
    day3 = result[48:72, :]

    return (day1, day2, day3)


def run_case1(plot_res=False):
    """
    Run test case 1

    Parameters
    ----------
    plot_res : bool, optional
        Defines, if results should be plotted (default: False)

    Returns
    -------
    result_tuple : tuple (of floats)
        Results tuple with maximal temperature deviations
        (max_dev_1, max_dev_10, max_dev_60)
    """
    # Definition of time horizon
    times_per_hour = 60  # 60 minutes per hour
    timesteps = 24 * 60 * times_per_hour  # 60 days (with minute timestep)

    timesteps_day = int(
        24 * times_per_hour)  # 24 * 60 minute timesteps per day

    tz = prepare_thermal_zone(timesteps)

    calc = VDICore(tz)
    calc.equal_air_temp = np.zeros(timesteps) + 295.15
    calc.solar_rad_in = np.zeros((timesteps, 1))

    calc.t_set_heating = np.zeros(timesteps)  # in Kelvin
    calc.t_set_cooling = np.zeros(timesteps) + 600  # in Kelvin

    calc.heater_limit = np.zeros((timesteps, 3)) + 1e10
    calc.cooler_limit = np.zeros((timesteps, 3)) - 1e10

    q_ig = np.zeros(timesteps_day)
    for q in range(int(6 * timesteps_day / 24), int(18 * timesteps_day / 24)):
        q_ig[q] = 1000
    q_ig = np.tile(q_ig, 60)

    calc.internal_gains = q_ig

    t_air, q_air_hc = calc.simulate()

    # Compute averaged results
    T_air_c = t_air - 273.15
    T_air_mean = np.array(
        [np.mean(T_air_c[i * times_per_hour:(i + 1) * times_per_hour]) for i in
         range(24 * 60)])

    T_air_1 = T_air_mean[0:24]
    T_air_10 = T_air_mean[216:240]
    T_air_60 = T_air_mean[1416:1440]

    this_path = os.path.dirname(os.path.abspath(__file__))
    ref_file = 'case01_res.csv'
    ref_path = os.path.join(this_path, 'inputs', ref_file)

    # Load reference results
    (T_air_ref_1, T_air_ref_10, T_air_ref_60) = load_res(ref_path)

    T_air_ref_1 = T_air_ref_1[:, 0]
    T_air_ref_10 = T_air_ref_10[:, 0]
    T_air_ref_60 = T_air_ref_60[:, 0]

    # Plot comparisons
    def plot_result(res, ref, title="Results day 1"):

        import matplotlib.pyplot as plt

        plt.figure()
        ax_top = plt.subplot(211)
        plt.plot(res, label="Simulation", color="black", linestyle="--")
        plt.plot(ref, label="Reference", color="blue", linestyle="-")
        plt.legend()
        plt.ylabel("Temperature in degC")

        plt.title(title)

        plt.subplot(212, sharex=ax_top)
        plt.plot(res - ref, label="Ref. - Sim.")
        plt.legend()
        plt.ylabel("Temperature difference in K")
        plt.xticks([4 * i for i in range(7)])
        plt.xlim([1, 24])
        plt.xlabel("Time in h")
        plt.show()

    if plot_res:
        plot_result(T_air_1, T_air_ref_1, "Results day 1")
        plot_result(T_air_10, T_air_ref_10, "Results day 10")
        plot_result(T_air_60, T_air_ref_60, "Results day 60")

    max_dev_1 = np.max(np.abs(T_air_1 - T_air_ref_1))
    max_dev_10 = np.max(np.abs(T_air_10 - T_air_ref_10))
    max_dev_60 = np.max(np.abs(T_air_60 - T_air_ref_60))

    print("Max. deviation day 1: " + str(max_dev_1))
    print("Max. deviation day 10: " + str(max_dev_10))
    print("Max. deviation day 60: " + str(max_dev_60))

    return (max_dev_1, max_dev_10, max_dev_60)




if __name__ == '__main__':
    run_case1(plot_res=True)