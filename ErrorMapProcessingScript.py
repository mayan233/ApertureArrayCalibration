"""
Processes error map scripts generated by pyNF2fF.py
"""

import FileReading.readFromFile as rff
import numpy as np
import matplotlib.pyplot as plt
import NF2FF.NFFFandFPlotting as plotting
import NF2FF.NF2FF as nf2ff
import csv
import os

def run():
    # Global settings
    global_filename = "Dipole_85deg_400MHz"
    directory = "ErrorFields/"

    # Sweep settings
    planar_loc_error_lim = (200, 4)  # Fraction of wavelength error
    planar_loc_error_steps = 51

    # Error calculation settings
    cutoff_angle = np.deg2rad(60)

    if(False):
        import os
        for filename in os.listdir(directory):
            print(filename)
            theta_grid, phi_grid, error_grid = rff.read_farfield_gain_datafile("ErrorFieldsFinal/"+filename)
            theta_grid, phi_grid, avg_error_grid = rff.read_farfield_gain_datafile(directory+avg_filename)

            plotting.plot_nearfield_2d(theta_grid, phi_grid, 10*np.log10(error_grid), filename, zlim=[-25,0])
        plt.show()
        exit()

    if(True):
        import os
        i = 0
        for error in np.linspace(planar_loc_error_lim[0], planar_loc_error_lim[1], planar_loc_error_steps):
            avg_filename = "error_map_avg_"+global_filename+"_"+str(error)+".dat"
            theta_grid, phi_grid, avg_error_grid = rff.read_farfield_gain_datafile(directory+avg_filename)

            plotting.plot_nearfield_2d(theta_grid, phi_grid, 10*np.log10(avg_error_grid), error, zlim=[-25,0])
            print(error)
            plt.savefig("Animation/"+str(i))
            i += 1
        exit()

    print("Extracting max and avg values from error maps:")
    # Open writer
    with open('error.dat', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        for error in np.linspace(planar_loc_error_lim[0], planar_loc_error_lim[1], planar_loc_error_steps):
            # Load file
            avg_filename = "error_map_avg_"+global_filename+"_"+str(error)+".dat"
            max_filename = "error_map_max_"+global_filename+"_"+str(error)+".dat"
            theta_grid, phi_grid, avg_error_grid = rff.read_farfield_gain_datafile(directory+avg_filename)
            theta_grid, phi_grid, max_error_grid = rff.read_farfield_gain_datafile(directory+max_filename)

            # Integrate over partial sphere to calculate avg-avg and avg-max
            a = np.sin(cutoff_angle)
            h = 1 - np.cos(cutoff_angle)
            sphere_cap = np.pi*(a**2 + h**2)

            avg_error_grid[np.abs(theta_grid) > cutoff_angle] = 0
            avg_error_grid[avg_error_grid == 0] = 0.00000000001
            int_avg_error = nf2ff.calc_radiated_power(theta_grid, phi_grid, avg_error_grid,
                                                      [-cutoff_angle, cutoff_angle], [0, np.pi])/sphere_cap
            max_error_grid[np.abs(theta_grid) > cutoff_angle] = 0
            max_error_grid[max_error_grid == 0] = 0.00000000001
            int_max_error = nf2ff.calc_radiated_power(theta_grid, phi_grid, max_error_grid,
                                                      [-cutoff_angle, cutoff_angle], [0, np.pi])/sphere_cap

            print(str(error)+": "+str(int_avg_error[0])+" "+str(int_max_error[0]))
            writer.writerow([error, int_avg_error[0], int_max_error[0]])

            #Plot field
            if(False):
                plotting.plot_nearfield_2d(theta_grid, phi_grid, 10*np.log10(avg_error_grid), "Avg: "+str(error), zlim=[-25,0])
                plotting.plot_nearfield_2d(theta_grid, phi_grid, 10*np.log10(max_error_grid), "Max: "+str(error), zlim=[-25,0])
                plt.show()

run()
