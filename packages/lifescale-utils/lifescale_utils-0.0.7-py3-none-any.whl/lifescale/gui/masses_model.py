"""Masses model class for PyQt's model view architectrue.

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
from PyQt6.QtWidgets import QMessageBox
from PyQt6 import QtGui


NONE_REPRESENTATION_IN_TABLE_VIEW = ''  # Representation of None values in table views in the GUI


class MassesModel(QAbstractTableModel):
    """Model for the masses table view."""

    # Number of decimal pla
    _DECIMAL_PLACES_PER_FLOAT_COLUMN = {
        'Time': 3,
        'Mass': 3,
        'Volume': 3,
        'TransitTime': 3,
        'PressureDrop': 5,
    }

    def __init__(self, df):
        QAbstractTableModel.__init__(self)
        self._data = None
        self._masses = None
        self._current_sample_id = None
        self.load_data(df)

    def load_data(self, df):
        """Load data from pandas dataframe to table model.

        Notes
        -----
        The data is assigned by reference, i.e. all changes in `_masses` will propagate to the data origin (`df`).
        """
        # self._masses = df.copy(deep=True)
        self._masses = df

    def update_view_model(self, sample_id: int):
        """Update the `_data` DataFrame that hold the actual data that is displayed."""
        try:
            df_masses_slice = self._masses.loc[self._masses['SampleID'] == sample_id]
        except KeyError:
            self._current_sample_id = None
            self._data = None
            QMessageBox.critical(self.parent(), 'Error!', f'SampleID "{sample_id}" is not available.')
        else:
            self._current_sample_id = sample_id
            self._data = df_masses_slice

    def rowCount(self, parent=None):
        if self._data is not None:
            return self._data.shape[0]
        else:
            return 0

    def columnCount(self, parent=None):
        if self._data is not None:
            return self._data.shape[1]
        else:
            return 0

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
                if ~self._data.iloc[index.row()].keep:
                    return QtGui.QColor('red')

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
    def get_current_sample_id(self):
        """Return the current sample ID."""
        return self._current_sample_id

