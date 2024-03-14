import numpy as np
import os
import csv
import sys

def simulate_panels(stdev_percentage, num_panels=10000, mean_panel_power=430, num_cells=144, tolerance=0.06):
    mean_cell_power = mean_panel_power / num_cells
    stdev = mean_cell_power * (stdev_percentage / 100)
    tolerance_range = (mean_panel_power * (1 - tolerance), mean_panel_power * (1 + tolerance))

    # Generate cell powers
    cell_powers = np.random.normal(mean_cell_power, stdev, size=(num_panels, num_cells))

    # Panel Type 1 calculation
    weakest_first_half = np.min(cell_powers[:, :num_cells // 2], axis=1)
    weakest_second_half = np.min(cell_powers[:, num_cells // 2:], axis=1)
    panel_powers_type1 = ((weakest_first_half + weakest_second_half) / 2) * num_cells

    # Panel Type 2 calculation
    panel_powers_type2 = []
    for i in range(0, num_cells, 12):
        weakest_in_section = np.min(cell_powers[:, i:i+12], axis=1)
        panel_powers_type2.append(weakest_in_section)
    panel_powers_type2 = (np.mean(panel_powers_type2, axis=0)) * num_cells

    # Calculate percentages within tolerance
    within_tolerance_type1 = np.mean((panel_powers_type1 >= tolerance_range[0]) & (panel_powers_type1 <= tolerance_range[1])) * 100
    within_tolerance_type2 = np.mean((panel_powers_type2 >= tolerance_range[0]) & (panel_powers_type2 <= tolerance_range[1])) * 100

    # Calculate difference in power as a percentage of 430W
    diff_percentage = ((panel_powers_type2 - panel_powers_type1) / panel_powers_type1) * 100
    avg_diff_percentage = np.mean(diff_percentage)

    return within_tolerance_type1, within_tolerance_type2, avg_diff_percentage

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <stdev_percentage> <# runs>")
        sys.exit(1)

    stdev_percentage = float(sys.argv[1])
    num_runs = int(sys.argv[2])

    if (stdev_percentage > 100.0 or stdev_percentage < 0.0):
      print("<stdev_percentage> must be between 0%% and 100%%")
      sys.exit(1)

    result_path = './sim_results'
    run_number = 0
    if not os.path.exists(result_path):
      os.mkdir(result_path)
      print("%s directory created to store simulation results." % result_path[2:])
    else:
      run_number = len(os.listdir(result_path))

    results = result_path + '/panel_mism_output_' + str(run_number) + '.csv'

    print("Running simulation...")

    avg_panels_within = 0.0
    avg_opt_within = 0.0

    with open(results, 'w', newline='') as output:
      sim_writer = csv.writer(output, delimiter=',')
      sim_writer.writerow(['Run #', '% within 6%', 'Optivolt within 6%', 'Avg. Optivolt Power Advantage'])
      for run in range(num_runs):
        type_1, type_2, avg_diff = simulate_panels(stdev_percentage)
        avg_panels_within += type_1
        avg_opt_within += type_2
        sim_writer.writerow([run, round(type_1, 2), round(type_2, 2), round(avg_diff, 2)])
      avg_panels_within /= num_runs
      avg_opt_within /= num_runs
      sim_writer.writerow([''])
      sim_writer.writerow(['Cell STDEV', stdev_percentage])
      sim_writer.writerow(['# panels per simulated batch', 10000])
      sim_writer.writerow(['% panels within 6% tolerance', f"{avg_panels_within:.2f}%"])
      sim_writer.writerow(['% Optivolt panels within 6% tolerance', f"{avg_opt_within:.2f}%"])

    print("Simulation complete. Results stored in " + results)

    print('    Summary:')
    print('\tCell STDEV: ', f'{stdev_percentage:.2f}%')
    print('\t# panels per simulated batch: 10000')
    print('\t% panels within 6% tolerance: ', f'{avg_panels_within:.2f}%')
    print('\t% Optivolt panels within 6% tolerance: ', f'{avg_opt_within:.2f}%')

if __name__ == "__main__":
    main()
