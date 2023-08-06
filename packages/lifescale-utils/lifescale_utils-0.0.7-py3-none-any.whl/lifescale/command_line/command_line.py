"""Command line interface of lifescale utils.

Copyright (C) 2023  Andreas Hellerschmied <heller182@gmx.at>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from lifescale.scripts.ls2csv import ls2csv as ls2csv_main
from lifescale.scripts.run_gui import run_gui as run_gui_main
import argparse
import os


def is_file(filename):
    """Check, whether the input string is the path to an existing file."""
    if os.path.isfile(filename):
        return filename
    raise argparse.ArgumentTypeError("'{}' is not a valid file.".format(filename))


def is_dir(pathname):
    """Check, whether the input string is a valid and existing filepath."""
    if os.path.exists(pathname):
        return pathname
    raise argparse.ArgumentTypeError("'{}' is not a valid directory.".format(pathname))


def ls2csv():
    """Command line interface including argument parser for the lifescale2csv converter."""
    parser = argparse.ArgumentParser(prog="ls2csv",
                                     description="Conversion from lifescale xlsm output to csv files",
                                     epilog="The ls2csv converter loads and parses xlsm files created by the lifescale "
                                            "unit. It writes several csv files to the output directory that contain "
                                            "extracted data from the input xlsm file in an easily readable way.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input-xlsm", type=is_file, required=True, help="Path and name of the input xlsm file "
                                                                                "created by "
                                                                                "lifescale.")
    parser.add_argument("-o", "--out-dir", type=is_dir, required=True, help="Output directory for the CSV files.")
    parser.add_argument("-nv", "--not-verbose", required=False, help="Disable command line status messages.",
                        action='store_true')
    parser.add_argument("-s", "--sample-stats", required=False, help="Calculate sample statistics of masses (median, "
                                                                     "std. deviation, quartiles, interquartile range) "
                                                                     "and add them to the "
                                                                     "SampleSummary output CSV file (columns: "
                                                                     "Mass_median, Mass_std, Mass_q25, Mass_q75,"
                                                                     "Mass_iqr).",
                        action='store_true')
    parser.add_argument("-t", "--sort-masses-by-time", required=False, help="Sort data in the Masses CSV file by "
                                                                            "acquisition time.",
                        action='store_true')

    args = parser.parse_args()
    verbose = not args.not_verbose

    return ls2csv_main(xlsm_filename=args.input_xlsm,
                       output_dir=args.out_dir,
                       sample_stats=args.sample_stats,
                       sort_by_time=args.sort_masses_by_time,
                       verbose=verbose)


def lsgui():
    """Start lifescale utils gui."""
    parser = argparse.ArgumentParser(prog="lsgui",
                                     description="Starts lifescale utils gui.",
                                     epilog="Start the graphical user interface (gui) of lifescale utils.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    args = parser.parse_args()

    return run_gui_main()


if __name__ == '__main__':
    """Main function for debugging and testing."""
    ls2csv()
