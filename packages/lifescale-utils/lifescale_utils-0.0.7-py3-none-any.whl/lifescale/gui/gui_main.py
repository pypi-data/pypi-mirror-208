"""Main GUI model for lifescale_uitls.

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
import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog
from PyQt6.QtCore import pyqtSlot, QDir, Qt
import numpy as np
import pyqtgraph as pg

from lifescale.gui.MainWindow import Ui_MainWindow
from lifescale.gui.dialog_about import Ui_Dialog_about
from lifescale.models.ls_data import LSData
from lifescale.gui.panel_metadata_model import PanelMetadataModel
from lifescale.gui.sample_summary_model import SampleSummaryModel
from lifescale.gui.masses_model import MassesModel
from lifescale.gui import resources
from lifescale import __version__, __author__, __git_repo__, __email__, __copyright__, __pypi_repo__

# https://numpy.org/doc/stable/reference/generated/numpy.histogram_bin_edges.html#numpy.histogram_bin_edges
NUMPY_HISTOGRAM_BIN_EDGES_OPTIONS = {
    'auto': 'Maximum of the ‘sturges’ and ‘fd’ estimators. Provides good all around performance.',
    'fd': 'Freedman Diaconis Estimator: Robust (resilient to outliers) estimator that takes into account data variability and data size.',
    'doane': 'An improved version of Sturges’ estimator that works better with non-normal datasets.',
    'scott': 'Estimator based on leave-one-out cross-validation estimate of the integrated squared error. Can be regarded as a generalization of Scott’s rule.',
    'rice': 'Estimator does not take variability into account, only data size. Commonly overestimates number of bins required.',
    'sturges': 'R’s default method, only accounts for data size. Only optimal for gaussian data and underestimates number of bins for large non-gaussian datasets.',
    'sqrt': 'Square root (of data size) estimator, used by Excel and other programs for its speed and simplicity.',
    'Num. of bins': 'User defined number of bins (max. 1000).'
}


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main Window of the application."""

    def __init__(self):
        """Initializer."""

        # Attributes:
        # - GUI objects:
        self.sample_list = None
        self.glw_sample_histogram = None
        self.sample_histogram = None
        self.masses_region = None
        self.hist_marker_mean_all = None
        self.hist_marker_mean_selected = None
        self.hist_marker_median_selected = None
        self.hist_marker_median_all = None
        self.hist = None
        # - other objects:
        self.ls_data = None
        self.settings = {
            'hist_number_of_bins': None,
            'hist_bin_mode': 'auto',
        }

        # GUI:
        super().__init__()
        self.setupUi(self)

        # Connect signals and slots:
        self.action_Exit.triggered.connect(self.exit_application)
        self.actionLoad_xlsm_file.triggered.connect(self.on_menu_file_load_xlsm_file)
        self.action_About.triggered.connect(self.on_menu_help_about)
        self.action_csvFiles.triggered.connect(self.on_action_csvFiles)
        self.listWidget_Samples.itemSelectionChanged.connect(self.on_selection_changed_sample_list)
        self.checkBox_MassesShowTable.stateChanged.connect(self.on_checkBox_MassesShowTable_stateChanged)
        self.comboBox_histMethod.currentIndexChanged.connect(self.on_histogram_bin_method_currentIndexChanged)
        self.checkBox_plotMedian.stateChanged.connect(self.on_checkBox_plotMedian_stateChanged)
        self.checkBox_plotMean.stateChanged.connect(self.on_checkBox_plotMean_stateChanged)
        self.comboBox_histMethod.currentIndexChanged.connect(self.on_selection_changed_sample_list)
        self.spinBox_histBins.valueChanged.connect(self.on_selection_changed_sample_list)

        # Set up GUI items and widgets:
        self.status = self.statusBar()
        self.set_up_sample_histogram()
        self.set_up_sample_list()
        self.set_up_hist_method_comboBox()

        # GUI dialogs:
        self.dlg_about = DialogAbout()
        self.dlg_about.label_version.setText(__version__)
        self.dlg_about.label_git_repo.setText(__git_repo__)
        self.dlg_about.label_pypi_repo.setText(__pypi_repo__)
        self.dlg_about.label_email.setText(__email__)
        self.dlg_about.label_copyright.setText(__copyright__)
        self.dlg_about.label_author.setText(__author__)

        # Init models:
        self.panel_metadata_model = None
        self.sample_summary_model = None
        self.masses_model = None

    @pyqtSlot()
    def on_action_csvFiles(self):
        """Invoked when pressing Export CSV files."""
        if self.ls_data is None:
            QMessageBox.warning(self, 'Warning!', 'No data available!')
            return

        if (self.ls_data.df_panel_data is None) and (self.ls_data.df_panel_data is None) and (self.ls_data.df_masses is None):
            QMessageBox.warning(self, 'Warning!', 'No LifeScale data available!')
            return
        self.export_csv()

    def export_csv(self):
        """Export ls data to csv files."""

        # Get output directory:
        output_dir_name = QFileDialog.getExistingDirectory(self,
                                                           caption='Select an output directory',
                                                           directory=self.get_work_dir(),
                                                           options=QFileDialog.Option.ShowDirsOnly)
        # Write files
        try:
            self.ls_data.export_csv_files(output_dir_name, sort_by_time=False)
        except Exception as e:
            QMessageBox.critical(self, 'Error!', str(e))
            self.statusBar().showMessage(f'No LS data exportet.')
        else:
            self.status.showMessage(f'Exported CSV files to: {output_dir_name}')

    @pyqtSlot()
    def on_checkBox_plotMedian_stateChanged(self):
        """Invoked whenever the state changes."""
        if self.sample_histogram is not None:
            if self.masses_model is not None:
                self.plot_hist_mean_median_marker(self.masses_model.get_current_sample_id)

    @pyqtSlot()
    def on_checkBox_plotMean_stateChanged(self):
        """Invoked whenever the state changes."""
        if self.sample_histogram is not None:
            if self.masses_model is not None:
                self.plot_hist_mean_median_marker(self.masses_model.get_current_sample_id)

    @pyqtSlot()
    def on_pushButton_resetMassLimits_pressed(self):
        """Invoked whenever the button `pushButton_resetMassLimits` is pressed."""
        self.ls_data.reset_flag_masses(self.masses_model.get_current_sample_id)
        self.ls_data.calc_sample_statistics(selection_only=True)
        self.plot_masses_histogram(self.masses_model.get_current_sample_id)
        self.print_sample_statistics(self.masses_model.get_current_sample_id)

    def set_up_sample_histogram(self):
        """Set up `self.GraphicsLayoutWidget_stations_map` widget."""
        self.glw_sample_histogram = self.GraphicsLayoutWidget_SampelHistogram
        self.glw_sample_histogram.setBackground('w')  # white background color
        # Create sub-plots:
        self.sample_histogram = self.glw_sample_histogram.addPlot(0, 0, name='sample_histogram')
        self.sample_histogram.setLabel(axis='left', text='Number of Samples')
        self.sample_histogram.setLabel(axis='bottom', text='Mass')
        self.sample_histogram.setTitle('Sample Histogram')
        # self.stations_map.addLegend()
        self.sample_histogram.setMouseEnabled(y=False)

    def set_up_hist_method_comboBox(self):
        """Set up the histogram method combo box."""
        self.comboBox_histMethod.addItems(list(NUMPY_HISTOGRAM_BIN_EDGES_OPTIONS.keys()))
        # self.histogram_bin_method_selection(0)  # default: i. item in dict

    @pyqtSlot()
    def on_histogram_bin_method_currentIndexChanged(self):
        """Select bin determination method."""
        self.settings['hist_bin_mode'] = self.comboBox_histMethod.currentText()
        self.settings['hist_number_of_bins'] = self.spinBox_histBins.value()
        self.label_histBinMethodDescription.setText(NUMPY_HISTOGRAM_BIN_EDGES_OPTIONS[self.settings['hist_bin_mode']])
        if self.settings['hist_bin_mode'] == 'Num. of bins':
            self.label_numberOfBins.setEnabled(True)
            self.spinBox_histBins.setEnabled(True)
        else:
            self.label_numberOfBins.setEnabled(False)
            self.spinBox_histBins.setEnabled(False)

    def get_hist_bin_method(self):
        """Get selected bin method from GUI."""
        bins = self.comboBox_histMethod.currentText()
        if bins == 'Num. of bins':
            bins = self.spinBox_histBins.value()
        return bins

    @pyqtSlot(int)
    def on_checkBox_MassesShowTable_stateChanged(self, state):
        """Invoked whenever the state of the shoe massed checkbox changes."""
        self.set_model_tableView_Masses_based_on_checkbox_state()

    def set_model_tableView_Masses_based_on_checkbox_state(self):
        """Connect/disconnect the model of the masses table view based on checkbox state."""
        if self.checkBox_MassesShowTable.isChecked():
            self.tableView_Masses.setModel(self.masses_model)
        else:
            self.tableView_Masses.setModel(None)

    @pyqtSlot()
    def on_menu_file_load_xlsm_file(self):
        """Launch file selection dialog to load data from an xlsm file."""

        if self.ls_data is not None:
            reply = QMessageBox.question(self,
                                         'Message',
                                         f'Overwrite data from: {self.ls_data.run_name}',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
            self.reset_gui()  # Clear and reset all items

        xlsm_filename, _ = QFileDialog.getOpenFileName(self,
                                                       caption='Select LifeScale data file (xlsm format)',
                                                       directory=self.get_work_dir(),
                                                       filter="LifeScale data file (*.xlsm)")

        if xlsm_filename:
            xlsm_filename = QDir.toNativeSeparators(xlsm_filename)
            try:
                ls_data = LSData.from_xlsm_file(xlsm_filename)
                ls_data.calc_sample_statistics()
            except Exception as e:
                QMessageBox.critical(self, 'Error!', str(e))
                self.statusBar().showMessage(f"No LS data loaded.")
            else:
                self.ls_data = ls_data
                self.status.showMessage(f'Loaded: {ls_data}')
                self.setWindowTitle(self.ls_data.run_name)
                self.set_up_panel_metadata_view_model()
                self.set_up_sample_summary_view_model()
                self.set_up_masses_view_model()
                self.update_sample_list()
        else:
            self.statusBar().showMessage(f"No LS data loaded.")

    def set_up_sample_list(self):
        """Set up sample list widget"""
        self.sample_list = self.listWidget_Samples

    def print_sample_statistics(self, sample_id):
        """Print sample statistics in GUI."""
        sample_data = self.ls_data.df_interval_analysis.loc[self.ls_data.df_interval_analysis['SampleID'] == sample_id]
        if len(sample_data) == 0:
            raise IndexError(f'No sample dataset found for sample ID = {sample_id}')

        self.label_median.setText(
            f'{sample_data["Mass_median"].item():.3f} ({sample_data["Mass_median_keep"].item():.3f})')
        self.label_mean.setText(f'{sample_data["MeanMass"].item():.3f} ({sample_data["Mass_mean_keep"].item():.3f})')
        self.label_std.setText(f'{sample_data["Mass_std"].item():.3f} ({sample_data["Mass_std_keep"].item():.3f})')
        self.label_iqr.setText(f'{sample_data["Mass_iqr"].item():.3f} ({sample_data["Mass_iqr_keep"].item():.3f})')
        self.label_rcv.setText(
            f'{sample_data["Mass_rCV"].item():.3f} ({sample_data["Mass_rCV_keep"].item():.3f})')
        if sample_data["keep_min_mass"].isna().item() and sample_data["keep_max_mass"].isna().item():
            self.label_selectionLimits.clear()
            self.label_SelectedMasse.setText('No selection')
        else:
            self.label_selectionLimits.setText(
                f'[{sample_data["keep_min_mass"].item():.3f}, {sample_data["keep_max_mass"].item():.3f}]')
            num_selected = sample_data['DetectedParticles_keep'].item()
            num_all = sample_data['DetectedParticles'].item()
            selected_percent = (num_selected / num_all) * 100
            self.label_SelectedMasse.setText(f'{num_selected:.0f} of {num_all:.0f} ({selected_percent:.3f} %)')

    def update_sample_list(self):
        """Update sample list widget and add """
        # TODO: SampleDescription zu jedem Sample hinzufügen, siehe: ls_data.df_panel_data.SampleDescription
        self.sample_list.clear()
        # self.sample_list.addItems(self.ls_data.get_sample_ids)
        self.sample_list.addItems(self.sample_summary_model.get_sample_list_tags)

    @pyqtSlot()
    def on_selection_changed_sample_list(self):
        """Invoked whenever the item selection changed."""
        items = self.sample_list.selectedItems()
        if len(items) == 1:
            sample_id = items[0].text().split(':')[0]  # Extract sample ID from tag
            # TODO: Update gui models, plots, tables and statistics!
            self.update_masses_table_view(sample_id)
            self.status.showMessage(f'{len(self.masses_model.get_data)} mass(es) in sample {sample_id}.')
            self.plot_masses_histogram(sample_id)
            self.print_sample_statistics(sample_id)

        else:
            print('No or multiple items selected!')

    def plot_masses_histogram(self, sample_id, bins='auto'):
        """Create a histogram of masses of a single sample."""
        # ## compute standard histogram
        # y, x = np.histogram(vals, bins=np.linspace(-3, 8, 40))
        #
        # ## notice that len(x) == len(y)+1
        # ## We are required to use stepMode=True so that PlotCurveItem will interpret this data correctly.
        # curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80))
        # plt1.addItem(curve)
        #
        # Get min and max mass threshold:
        tmp_filter = self.ls_data.df_interval_analysis['SampleID'] == sample_id
        keep_min_mass = self.ls_data.df_interval_analysis.loc[tmp_filter, 'keep_min_mass'].item()
        keep_max_mass = self.ls_data.df_interval_analysis.loc[tmp_filter, 'keep_max_mass'].item()

        # Get bin method:
        bins = self.get_hist_bin_method()

        self.sample_histogram.clear()
        masses = self.masses_model.get_data['Mass']
        y, x = np.histogram(masses, bins=bins)
        self.hist = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 80))
        self.sample_histogram.addItem(self.hist)

        # Get region limits:
        if keep_min_mass is None:
            x_min = x.min()
        else:
            x_min = keep_min_mass
        if keep_max_mass is None:
            x_max = x.max()
        else:
            x_max = keep_max_mass

        # Linear Reagions:
        pen = pg.mkPen(color='r', width=10)
        # https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/linearregionitem.html
        self.masses_region = pg.LinearRegionItem([x_min, x_max],
                                                 # bounds=[x.min(), x.max()],  # use clipItem instead
                                                 swapMode='block',
                                                 clipItem=self.hist,
                                                 hoverPen=pen)
        self.masses_region.setZValue(-10)
        self.sample_histogram.addItem(self.masses_region)
        self.masses_region.sigRegionChangeFinished.connect(self.on_masses_region_sigRegionChangeFinished)

        # Mean and median marker:
        self.plot_hist_mean_median_marker(sample_id)

    def plot_hist_mean_median_marker(self, sample_id: str):
        """Plot mean and median marker to the histogram plot."""
        if self.sample_histogram.legend is not None:
            self.sample_histogram.legend.clear()
        if self.hist_marker_mean_all is not None:
            self.hist_marker_mean_all.clear()
        if self.hist_marker_mean_selected is not None:
            self.hist_marker_mean_selected.clear()
        if self.hist_marker_median_all is not None:
            self.hist_marker_median_all.clear()
        if self.hist_marker_median_selected is not None:
            self.hist_marker_median_selected.clear()

        if self.checkBox_plotMean.isChecked() or self.checkBox_plotMedian.isChecked():

            self.sample_histogram.addLegend()

            tmp_filter = self.ls_data.df_interval_analysis['SampleID'] == sample_id
            mean_all = self.ls_data.df_interval_analysis.loc[tmp_filter, 'MeanMass'].item()
            mean_keep = self.ls_data.df_interval_analysis.loc[tmp_filter, 'Mass_mean_keep'].item()
            median_all = self.ls_data.df_interval_analysis.loc[tmp_filter, 'Mass_median'].item()
            median_keep = self.ls_data.df_interval_analysis.loc[tmp_filter, 'Mass_median_keep'].item()

            # y_max = self.sample_histogram.getAxis('left').range[1]
            y_max = self.hist.getData()[1].max()

            if self.checkBox_plotMean.isChecked():
                pen = pg.mkPen(color='b', width=1)
                self.hist_marker_mean_all = self.sample_histogram.plot([mean_all, mean_all], [0.0, y_max],
                                                                       name=f'Mean (all)',
                                                                       pen=pen)
                pen = pg.mkPen(color='r', width=1)
                self.hist_marker_mean_selected = self.sample_histogram.plot([mean_keep, mean_keep], [0.0, y_max],
                                                                            name=f'Mean (selected)',
                                                                            pen=pen)
            if self.checkBox_plotMedian.isChecked():
                pen = pg.mkPen(color='b', width=1, style=Qt.PenStyle.DotLine)
                self.hist_marker_median_all = self.sample_histogram.plot([median_all, median_all], [0.0, y_max],
                                                                         name=f'Median (all)',
                                                                         pen=pen)
                pen = pg.mkPen(color='r', width=1, style=Qt.PenStyle.DotLine)
                self.hist_marker_median_selected = self.sample_histogram.plot([median_keep, median_keep], [0.0, y_max],
                                                                              name=f'Median (selected)',
                                                                              pen=pen)

    @pyqtSlot()
    def on_masses_region_sigRegionChangeFinished(self):
        """Invoked whenever the masses selection region changed."""
        [min_mass, max_mass] = self.masses_region.getRegion()
        print(f'Mass selection changed: min={min_mass:.3f}, max={max_mass:.3f}')
        info_string = self.ls_data.flag_masses(min_mass,
                                               max_mass,
                                               sample_id=self.masses_model.get_current_sample_id)  # Set flag in ls_data object
        self.status.showMessage(info_string)
        self.update_masses_table_view(sample_id=self.masses_model.get_current_sample_id)
        self.ls_data.calc_sample_statistics(selection_only=True)
        self.print_sample_statistics(self.masses_model.get_current_sample_id)
        self.plot_hist_mean_median_marker(self.masses_model.get_current_sample_id)

    def reset_gui(self):
        """Clean and reset all GUI items, e.g. when loading new data."""
        self.sample_list.clear()

    def set_up_panel_metadata_view_model(self):
        """Set up the panel metadata table view model."""
        try:
            self.panel_metadata_model = PanelMetadataModel(self.ls_data.df_panel_data)
        except AttributeError:
            QMessageBox.warning(self, 'Warning!', 'No panel metadata available!')
        except Exception as e:
            QMessageBox.critical(self, 'Error!', str(e))
        else:
            self.tableView_PanelMetadata.setModel(self.panel_metadata_model)
            self.tableView_PanelMetadata.resizeColumnsToContents()

    def set_up_sample_summary_view_model(self):
        """Set up the sample summary table view model."""
        try:
            self.sample_summary_model = SampleSummaryModel(self.ls_data.df_interval_analysis)
        except AttributeError:
            QMessageBox.warning(self, 'Warning!', 'No sample summary data available!')
        except Exception as e:
            QMessageBox.critical(self, 'Error!', str(e))
        else:
            self.tableView_SampleSummary.setModel(self.sample_summary_model)
            self.tableView_SampleSummary.resizeColumnsToContents()

    def update_sample_summary_view_model(self):
        """Update the sample summary table view after changing the model."""
        pass

    def set_up_masses_view_model(self):
        """Set up the masses table view model."""
        try:
            self.masses_model = MassesModel(self.ls_data.df_masses)
        except AttributeError:
            QMessageBox.warning(self, 'Warning!', 'No masses data available!')
        except Exception as e:
            QMessageBox.critical(self, 'Error!', str(e))
        else:
            self.set_model_tableView_Masses_based_on_checkbox_state()
            self.tableView_Masses.resizeColumnsToContents()
            # self.masses_model.dataChanged.connect(self.on_masses_model_data_changed)

    def update_masses_table_view(self, sample_id: int):
        """Update the masses table view according to the sample selection"""
        self.masses_model.update_view_model(sample_id)
        self.masses_model.layoutChanged.emit()  # Show changes in table view
        # Workaround: https://stackoverflow.com/questions/8199747/sizing-to-fit-rows-and-columns-in-a-qtableview-is-very-slow
        # self.tableView_Masses.resizeColumnsToContents()  # Takes a very long time to execute!

    def closeEvent(self, event):
        """Ask the user whether to close the main window or not!"""
        reply = QMessageBox.question(self,
                                     'Message',
                                     "Are you sure to quit?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def exit_application(self):
        """Exit the application."""
        reply = QMessageBox.question(self,
                                     'Message',
                                     "Are you sure to quit?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            sys.exit()

    def get_work_dir(self):
        """Returns the current working directory for file dialogs"""
        return os.getcwd()

    @pyqtSlot()
    def on_menu_help_about(self):
        """Launch the about dialog."""
        return_value = self.dlg_about.exec()


class DialogAbout(QDialog, Ui_Dialog_about):
    """About dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Run the .setupUi() method to show the GUI
        self.setupUi(self)


def main():
    """Main program to start the GUI."""
    # Create the application
    app = QApplication(sys.argv)

    # Create and show the application's main window
    main_window = MainWindow()
    main_window.show()
    # Run the application's main loop:
    sys.exit(
        app.exec())  # exit or error code of Qt (app.exec_) is passed to sys.exit. Terminates pgm with standard
    # python method


if __name__ == "__main__":
    """Main Program."""
    main()
