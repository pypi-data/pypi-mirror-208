"""Conversion program from xlsm to csv.

Copyright (C) 2022  Andreas Hellerschmied <heller182@gmx.at>

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

from lifescale.models.ls_data import LSData


def ls2csv(xlsm_filename, output_dir, sample_stats=True, sort_by_time=False, verbose=True):
    """Convert lifescale output file (xlsm) to csv files."""
    ls_data = LSData.from_xlsm_file(input_xlsm_filename=xlsm_filename, verbose=verbose)
    if sample_stats:
        ls_data.calc_sample_statistics(verbose=verbose)
    ls_data.export_csv_files(output_dir, sort_by_time=sort_by_time, verbose=verbose)
