#!/usr/bin/env python
# netcdf_to_csv.py
import sys
import os
import csv
from netCDF4 import Dataset

def netcdf_to_csv(nc_file):
    with Dataset(nc_file, 'r') as nc:
        print(f"Converting {nc_file} to CSV...")

        # Get variable names and dimensions
        var_names = [var.name for var in nc.variables.values()]
        dimensions = nc.dimensions

        # Iterate through each variable, get data, and flatten it
        data = []
        for name in var_names:
            var = nc.variables[name][:]
            var_data = var.flatten().tolist()
            data.append(var_data)

        # Transpose data to get rows for CSV file
        data = list(zip(*data))

        # Write data to CSV file
        csv_file = os.path.splitext(nc_file)[0] + ".csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(var_names)
            writer.writerows(data)

        print(f"CSV file created: {csv_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m netcdf_to_csv <nc_file1> <nc_file2> ...")
        sys.exit(1)

    for nc_file in sys.argv[1:]:
        if os.path.isfile(nc_file) and nc_file.endswith(".nc"):
            netcdf_to_csv(nc_file)
        else:
            print(f"Error: {nc_file} is not a valid netCDF file")

if __name__ == "__main__":
    main()