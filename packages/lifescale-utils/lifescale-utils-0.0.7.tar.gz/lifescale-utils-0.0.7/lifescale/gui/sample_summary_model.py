"""Sample model class for PyQt's model view architectrue.

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

from PyQt6.QtCore import QAbstractTableModel, Qt
from PyQt6 import QtGui


NONE_REPRESENTATION_IN_TABLE_VIEW = ''  # Representation of None values in table views in the GUI


class SampleSummaryModel(QAbstractTableModel):
    """Model for the panel metadata table view."""

    # Number of decimal pla
    _DECIMAL_PLACES_PER_FLOAT_COLUMN = {
        'Concentration': 1,
        'StartTime': 3,
        'EndTime': 3,
        'MeanMass': 3,
        'MassContent': 5,
        'MeasuredVolume': 3,
        'MeasuredVolume': 3,
        'ResonantFrequency': 3,
        'Mass_median': 3,
        'Mass_std': 3,
        'Mass_q25': 3,
        'Mass_q75': 3,
        'Mass_iqr': 3,
        'keep_max_mass': 3,
        'keep_min_mass': 3,
        'DetectedParticles_keep': 0,
        'Mass_mean_keep': 3,
        'Mass_median_keep': 3,
        'Mass_std_keep': 3,
        'Mass_q25_keep': 3,
        'Mass_q75_keep': 3,
        'Mass_iqr_keep': 3,
        'Mass_rCV_keep': 3,
        'Mass_rCV': 3,
    }

    def __init__(self, df):
        QAbstractTableModel.__init__(self)
        self._data = None
        self.load_data(df)

    def load_data(self, df):
        """Load data from pandas dataframe to table model."""
        self._data = df

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():

            value = self._data.iloc[index.row(), index.column()]
            column_name = self.get_colum_names[index.column()]

            if role == Qt.ItemDataRole.DisplayRole:

                # Custom formatter (string is expected as return type):
                if value is None:  #
                    return NONE_REPRESENTATION_IN_TABLE_VIEW
                elif isinstance(value, float):
                    if value != value:  # True, if value is "NaN"
                        return NONE_REPRESENTATION_IN_TABLE_VIEW
                    else:
                        if column_name in self._DECIMAL_PLACES_PER_FLOAT_COLUMN.keys():
                            num_dec_places = self._DECIMAL_PLACES_PER_FLOAT_COLUMN[column_name]
                            return '{1:.{0}f}'.format(num_dec_places, value)
                        else:
                            return str(value)
                else:  # all other
                    return str(value)

            if role == Qt.ItemDataRole.TextAlignmentRole:
                # value = self._data.iloc[index.row(), index.column()]
                if isinstance(value, int) or isinstance(value, float):
                    # Align right, vertical middle.
                    return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignRight

            if role == Qt.ItemDataRole.BackgroundRole:
                if (self._data.iloc[index.row()].keep_max_mass is not None) or (self._data.iloc[index.row()].keep_min_mass is not None):
                    return QtGui.QColor('green')

            # if role == Qt.BackgroundRole:
            #     if column_name == 'is_datum':
            #         if value:
            #             return QtGui.QColor('red')
            #
            #     is_observed_flag = self._data.iloc[index.row(), 7]  # is_observed
            #     if is_observed_flag:
            #         return QtGui.QColor('cyan')

            # if role == Qt.CheckStateRole:
            #     try:
            #         if column_name == 'is_datum':
            #             keep_obs_flag = self._data.iloc[index.row(), self._data_column_names.index('is_datum')]
            #             if keep_obs_flag:
            #                 return Qt.Checked
            #             else:
            #                 return Qt.Unchecked
            #     except Exception:
            #         return None
        return None

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if self._data is not None:
                if orientation == Qt.Orientation.Horizontal:
                    # return self._SHOW_COLUMNS_IN_TABLE_DICT[str(self._data.columns[section])]
                    return str(self._data.columns[section])
                if orientation == Qt.Orientation.Vertical:
                    return str(self._data.index[section])

    def flags(self, index):
        """Enable editing of table items."""
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemFlag.ItemIsSelectable
        flags |= Qt.ItemFlag.ItemIsEnabled
        flags |= Qt.ItemFlag.ItemIsDragEnabled
        flags |= Qt.ItemFlag.ItemIsDropEnabled
        return flags

    @property
    def get_data(self):
        return self._data

    @property
    def get_colum_names(self):
        """Return a list with all columns."""
        if self._data is not None:
            return self._data.columns.to_list()
        else:
            return None

    @property
    def get_sample_ids(self):
        """Return a list with all sample IDs."""
        if self._data is not None:
            return self._data['SampleID'].to_list()
        else:
            return None

    @property
    def get_sample_list_tags(self):
        """Return a list of sample tags with sample IDs and number of detected particles."""
        if self._data is not None:
            return (self._data['SampleID'].astype(str) + ': ' + self._data['DetectedParticles'].astype(str)).to_list()
        else:
            return None


