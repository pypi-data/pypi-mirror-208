#!/usr/bin/env python
# netcdf_meta.py
import json
import os
import sys

from netCDF4 import Dataset


def print_metadata(nc_file):
    with Dataset(nc_file, 'r') as nc:
        print(f"File: {nc_file}")
        print("Global attributes:")
        for attr in nc.ncattrs():
            print(f"  {attr}: {nc.getncattr(attr)}")

        print("Dimensions:")
        for dim in nc.dimensions.values():
            print(f"  {dim}")

        print("Variables:")
        for var in nc.variables.values():
            print(f"  {var.name} ({','.join(var.dimensions)}): {var.dtype}")
            for attr in var.ncattrs():
                print(f"    {attr}: {var.getncattr(attr)}")

        print("Data (first 3 rows):")
        data = {}
        for var in nc.variables.values():
            data[var.name] = var[:3].tolist()

        print(json.dumps(data, indent=2))
        print("\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m netcdf_meta <nc_file1> <nc_file2> ...")
        sys.exit(1)

    for nc_file in sys.argv[1:]:
        if os.path.isfile(nc_file) and nc_file.endswith(".nc"):
            print_metadata(nc_file)
        else:
            print(f"Error: {nc_file} is not a valid netCDF file")


if __name__ == "__main__":
    main()
