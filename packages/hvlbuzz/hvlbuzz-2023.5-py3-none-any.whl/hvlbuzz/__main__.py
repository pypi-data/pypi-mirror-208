"""Entry point of the program"""

import os

# disable logging before loading kivy, otherwise the packaged version will crash
os.environ['KIVY_NO_CONSOLELOG'] = '1'  # fmt: skip

# pylint: disable=wrong-import-position
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle

from kivy import Config
from kivy.app import App
from kivy.properties import ObjectProperty  # pylint: disable=no-name-in-module
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.settings import SettingsWithSidebar
from kivy.logger import Logger
from kivy.resources import resource_add_path

if os.name == "nt":
    import win32api  # pylint: disable=import-error

from hvlbuzz.libs.config.toolbar import ConfigToolbar
from hvlbuzz.libs.config.systemselector import SystemSelector
from hvlbuzz.libs.config.layout import ConfigLayout
from hvlbuzz.libs.config.systemaddpopup import SystemAddPopup
from hvlbuzz.libs.data.layout import DataTabbedPanel
from hvlbuzz.libs.physics.tower import Tower

from hvlbuzz.libs.util.input import FloatInput, IntegerInput
from hvlbuzz.libs.util.settingsparser import SettingsParser
from hvlbuzz.libs.data.layout import LINE_TYPES
from hvlbuzz.libs.data.output import settings_data_rows

from hvlbuzz import __version__, MODULE_DIR

# pylint: enable=wrong-import-position

Config.set("graphics", "multisamples", "0")
Config.set("input", "mouse", "mouse,disable_multitouch")

SETTINGS_DIR = os.path.join(MODULE_DIR, "settings")

# Need to be in globals for buzz.kv, otherwise unused import:
_custom_widgets = (FloatInput, IntegerInput)


def main():
    """Main routine"""
    resource_add_path(MODULE_DIR)
    BuzzApp().run()


class BuzzNewDialog(FloatLayout):
    """BuzzNewDialog is a layout on a popup which allows users to clear the
    current tower geometry.
    """

    clear_tower = ObjectProperty(None)
    cancel = ObjectProperty(None)


class BuzzLoadDialog(FloatLayout):
    """BuzzLoadDialog is a layout on a popup which allows users to load the
    tower geometry from a JSON file.
    """

    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    load_filechooser = ObjectProperty(None)
    text_input = ObjectProperty(None)
    drive_spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings_parser = SettingsParser()

        # set the current working directory as starting path of filechooser
        load_path = settings_parser.get_load_path()
        if os.path.isdir(load_path):
            self.load_filechooser.path = load_path
            self.text_input.text = load_path
        else:
            self.load_filechooser.path = os.getcwd()
            self.text_input.text = os.getcwd()

        if os.name == "nt":
            drives = win32api.GetLogicalDriveStrings()
            self.drive_spinner.values = drives.split("\000")[:-1]

        else:
            self.drive_spinner.values = []


class BuzzSaveDialog(FloatLayout):
    """BuzzSaveDialog is a layout on a popup which allows users to save the
    current tower geometry as a JSON file.
    """

    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    save_filechooser = ObjectProperty(None)
    text_input = ObjectProperty(None)
    text_input_dir = ObjectProperty(None)
    drive_spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        settings_parser = SettingsParser()

        # set the current working directory as starting path of filechooser
        if os.path.isdir(settings_parser.get_save_path()):
            self.save_filechooser.path = settings_parser.get_save_path()
            self.text_input_dir.text = settings_parser.get_save_path()
        else:
            self.save_filechooser.path = os.getcwd()
            self.text_input_dir.text = os.getcwd()

        if os.name == "nt":
            drives = win32api.GetLogicalDriveStrings()
            self.drive_spinner.values = drives.split("\000")[:-1]

        else:
            self.drive_spinner.values = []


class ExportCSVDialog(FloatLayout):
    """ExportCSVDialog is a layout on a popup which allows users to save the
    plot and table data in a CSV file.
    """

    export_csv = ObjectProperty(None)
    cancel = ObjectProperty(None)
    export_csv_filechooser = ObjectProperty(None)
    text_input = ObjectProperty(None)
    text_input_dir = ObjectProperty(None)
    drive_spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        settings_parser = SettingsParser()

        # set the current working directory as starting path of filechooser
        if os.path.isdir(settings_parser.get_ecsv_path()):
            self.export_csv_filechooser.path = settings_parser.get_ecsv_path()
            self.text_input_dir.text = settings_parser.get_ecsv_path()
        else:
            self.export_csv_filechooser.path = os.getcwd()
            self.text_input_dir.text = os.getcwd()

        if os.name == "nt":
            drives = win32api.GetLogicalDriveStrings()
            self.drive_spinner.values = drives.split("\000")[:-1]

        else:
            self.drive_spinner.values = []


class ExportPDFDialog(FloatLayout):
    """ExportPDFDialog is a layout on a popup which allows users to save the
    plots and tables in a PDF file.
    """

    export_pdf = ObjectProperty(None)
    cancel = ObjectProperty(None)
    export_pdf_filechooser = ObjectProperty(None)
    text_input = ObjectProperty(None)
    text_input_dir = ObjectProperty(None)
    drive_spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        settings_parser = SettingsParser()

        # set the current working directory as starting path of filechooser
        if os.path.isdir(settings_parser.get_epdf_path()):
            self.export_pdf_filechooser.path = settings_parser.get_epdf_path()
            self.text_input_dir.text = settings_parser.get_epdf_path()
        else:
            self.export_pdf_filechooser.path = os.getcwd()
            self.text_input_dir.text = os.getcwd()

        if os.name == "nt":
            drives = win32api.GetLogicalDriveStrings()
            self.drive_spinner.values = drives.split("\000")[:-1]

        else:
            self.drive_spinner.values = []


class ExportPNGDialog(FloatLayout):
    """ExportPNGDialog is a layout on a popup which allows users to save a
    specific plot as a PNG image file.
    """

    export_png = ObjectProperty(None)
    cancel = ObjectProperty(None)
    dropdown_button = ObjectProperty(None)
    export_png_filechooser = ObjectProperty(None)
    text_input = ObjectProperty(None)
    text_input_dir = ObjectProperty(None)
    drive_spinner = ObjectProperty(None)

    options = ["Audible Noise", "Electric Field", "Magnetic Field"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        settings_parser = SettingsParser()

        # set the current working directory as starting path of filechooser
        if os.path.isdir(settings_parser.get_epng_path()):
            self.export_png_filechooser.path = settings_parser.get_epng_path()
            self.text_input_dir.text = settings_parser.get_epng_path()
        else:
            self.export_png_filechooser.path = os.getcwd()
            self.text_input_dir.text = os.getcwd()

        if os.name == "nt":
            drives = win32api.GetLogicalDriveStrings()
            self.drive_spinner.values = drives.split("\000")[:-1]
        else:
            self.drive_spinner.values = []

        # create a dropdown for the plot options
        self.plot_dropdown = DropDown()
        self.setup_dropdown()

    def setup_dropdown(self):
        """This method sets up the dropdown and handles the method bindings."""
        for option in self.options:
            btn = Button(text=option, size_hint_y=None, height=44)
            btn.bind(  # pylint: disable=no-member
                on_release=lambda btn: self.plot_dropdown.select(btn.text)
            )
            self.plot_dropdown.add_widget(btn)
        self.dropdown_button.bind(on_release=self.plot_dropdown.open)
        self.plot_dropdown.bind(  # pylint: disable=no-member
            on_select=lambda instance, x: self.set_option(x)
        )

    def set_option(self, option):
        """This method changes the dropdown button text when a dropdown option
        is chosen.
        """
        self.dropdown_button.text = option + " \u25BC"


class HelpDoc(FloatLayout):
    """HelpDoc is a layout on a popup which shows the users the help
    documentation as an RST document.
    """

    rst_doc = ObjectProperty(None)
    close = ObjectProperty(None)

    doc_sources = {
        "E-field CSM": os.path.join(MODULE_DIR, "helpdocs", "ef.rst"),
        "B-field": os.path.join(MODULE_DIR, "helpdocs", "bf.rst"),
        "EPRI AN": os.path.join(MODULE_DIR, "helpdocs", "epri.rst"),
        "BPA AN": os.path.join(MODULE_DIR, "helpdocs", "bpa.rst"),
        "CRIEPI AN": os.path.join(MODULE_DIR, "helpdocs", "criepi.rst"),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rst_doc.source = os.path.join(MODULE_DIR, "helpdocs", "ef.rst")

    def change_rst_source(self, text):
        """This method changes the RST document content depending on the button
        pressed.
        """
        self.rst_doc.source = self.doc_sources[text]


class MainLayout(BoxLayout):
    """MainLayout is the foundation layout of the application and brings all
    the different layouts together. MainLayout also handles the functionalities
    of the popup classes.
    """

    data_tabbed_panel = ObjectProperty(None)
    config_layout = ObjectProperty(None)
    selector_and_toolbar = ObjectProperty(None)

    _loadedJSON = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Tower instance on which all methods work on
        self.tower = Tower()

        # add the DataTabbedPanel widget
        self.dtp = DataTabbedPanel(self.tower)
        self.data_tabbed_panel.add_widget(self.dtp)

        # add the ConfigLayout widget
        self.cl = ConfigLayout(self.tower)
        self.config_layout.add_widget(self.cl)

        # create a SystemSelector instance
        self.ss = SystemSelector(self.tower, self.cl)
        self.selector_and_toolbar.add_widget(self.ss)

        # create a SystemAddPopup instance
        self.sap = SystemAddPopup(self.tower, self.ss, self.dtp)

        # add the ConfigToolbar widget
        self.ct = ConfigToolbar(self.tower, self.dtp, self.sap, self.cl, self.ss)
        self.selector_and_toolbar.add_widget(self.ct)

        self._popup = None

    def reset_settings_parser(self):
        """This method prompts the settings parser belonging to the plots to
        reload the settings from the buzz.ini file.
        """
        self.dtp.reset_settings_parser()

    def show_new(self):
        """This method shows the BuzzNewDialog popup."""
        content = BuzzNewDialog(clear_tower=self.clear_tower, cancel=self.dismiss_popup)
        self._popup = Popup(title="New Tower Configuration", content=content, size_hint=(0.9, 0.3))
        self._popup.open()

    def clear_tower(self):
        """This method clears the tower configuration and resets all layouts."""
        self.tower.reset_systems()
        self.ss.setup_system_select()
        self.cl.remove_active_system()
        self.dtp.update_plots()
        self.dismiss_popup()

    def show_export_csv(self):
        """This method shows the ExportCSVDialog popup."""
        content = ExportCSVDialog(export_csv=self.export_csv, cancel=self.dismiss_popup)
        self._popup = Popup(title="Export CSV", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def export_csv(self, path, filename):
        """This method saves the plot and table data into a CSV file.

        input variable(s):

        * path: the directory path to save the CSV file in
        * filename: the name of the CSV file
        """
        # do not do anything if filename is still empty
        if filename == "":
            return

        config = App.get_running_app().config
        config.set("Export", "ecsv_path", os.path.dirname(os.path.join(path, filename)))
        config.write()

        try:
            self.dtp.export_csv(path, filename, self._loadedJSON)
        except PermissionError:
            file_path = os.path.join(path, filename)
            Logger.exception("Export CSV: Permission denied to: %s", file_path)
        self.dismiss_popup()

    def show_export_pdf(self):
        """This method shows the ExportPDFDialog popup."""
        content = ExportPDFDialog(export_pdf=self.export_pdf, cancel=self.dismiss_popup)
        self._popup = Popup(title="Export PDF", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def export_pdf(self, path, filename):
        """This method creates a PDF file with current plots and table.

        input variable(s):

        * path: the directory path to save the PDF file in
        * filename: the filename of the PDF file
        """
        # do not do anything if filename is still empty
        if filename == "":
            return

        config = App.get_running_app().config
        config.set("Export", "epdf_path", os.path.dirname(os.path.join(path, filename)))
        config.write()

        # create a temporary path for PNG images
        temp_path = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_path, exist_ok=True)

        try:
            # save audible image plot as PNG image
            an_img = self._create_image(temp_path, "Audible Noise")
            # save electric field plot as PNG image
            ef_img = self._create_image(temp_path, "Electric Field")
            # save magnetic field plot as PNG image
            mf_img = self._create_image(temp_path, "Magnetic Field")

            # create a PDF file
            if not filename.endswith(".pdf"):
                filename += ".pdf"
            c = canvas.Canvas(os.path.join(path, filename), pagesize=A4)

            # get page sizes
            width, height = A4
            yspace = (height - width) / 4

            # create an instance of SettingsParser to get the settings
            settings_parser = SettingsParser()

            settings_data = [["Settings", "Values"]] + settings_data_rows(
                str(self._loadedJSON), settings_parser
            )

            # define table styling
            settings_table = Table(
                settings_data,
                2 * [40 * mm],
                len(settings_data) * [7 * mm],
                style=TableStyle(
                    [
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ]
                ),
            )

            # draw table on the bottom of first page
            settings_table.wrapOn(c, width, height)
            settings_table.drawOn(c, width / 2 - 40 * mm, height / 2 + 2 * yspace)

            # newpage
            c.showPage()  # added because sometimes config_table would overlap with settings_table

            config_data = []
            for system in self.tower.systems:
                config_data += system_geometry_data(system)

            # define table styling
            config_table = Table(
                config_data,
                7 * [20 * mm],
                len(config_data) * [7 * mm],
                style=TableStyle(
                    [
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                    ]
                ),
            )

            # draw table on the bottom of first page
            config_table.wrapOn(c, width, height)
            config_table.drawOn(c, width / 2 - 70 * mm, yspace)

            # end the first page
            c.showPage()

            # insert audible noise table headers
            headers = [
                "Line",
                "Coordinates",
                "AC E-Field",
                "DC E-Field",
                "AC EPRI",
                "AC BPA",
                "DC EPRI",
                "DC BPA",
                "DC CRIEPI",
            ]
            units = [
                "",
                "in m",
                "in kV/cm",
                "in kV/cm",
                "in " + settings_parser.get_an_unit(),
                "in " + settings_parser.get_an_unit(),
                "in " + settings_parser.get_an_unit(),
                "in " + settings_parser.get_an_unit(),
                "in " + settings_parser.get_an_unit(),
            ]

            an_data = [headers, units] + [
                entry for entry in system_em_entries(system) for system in self.tower.systems
            ]
            # define table styling
            an_table = Table(
                an_data,
                9 * [22.5 * mm],
                len(an_data) * [7 * mm],
                style=TableStyle(
                    [
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ]
                ),
            )

            # draw table on the bottom of first page
            an_table.wrapOn(c, width, height)
            an_table.drawOn(c, 3.75 * mm, yspace)

            # draw audible noise image of top of first page
            c.drawImage(an_img, width / 4, height / 2, width=width / 2, height=width / 2)

            # end the second page
            c.showPage()

            # draw the electric field image on the left of second page
            c.drawImage(ef_img, 0, width / 2, width=width / 2, height=width / 2)
            # draw the magnetic field image on the right of first page
            c.drawImage(mf_img, width / 2, width / 2, width=width / 2, height=width / 2)

            # end the third page
            c.showPage()

            #  save the PDF file
            c.save()

        except PermissionError as e:
            print(e)

        self.dismiss_popup()

    def _create_image(self, tmp_dir: str, caption: str) -> ImageReader:
        """Draw an image of a plot in memory (via a temp file)."""
        filename = caption.replace(" ", "").lower() + ".png"
        path = os.path.join(tmp_dir, filename)
        self.dtp.export_png(tmp_dir, filename, caption)
        return ImageReader(path)

    def show_helpdoc(self):
        """This method shows the HelpDoc popup."""
        content = HelpDoc(close=self.dismiss_popup)
        self._popup = Popup(title="Help", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def show_aboutbox(self):
        """Shows the about box popup."""
        content = Label(
            text=f"""Version {__version__}

Originally, HVLBuzz was developped by Aldo Tobler under the supervision of
Christian M. Franck, Sören Hedtke and support by Mikołaj Rybiński at
ETH Zurich's High Voltage Laboratory.

Currently, it is maintained by FKH Zürich.

Further Information at https://gitlab.com/ethz_hvl/hvlbuzz and
https://hvl.ee.ethz.ch/publications-and-awards/Software.html


Press ESC to dismiss"""
        )
        self._popup = Popup(title="About HVLBuzz", content=content)
        self._popup.open()

    def show_export_png(self):
        """This method shows the ExportPNGDialog popup."""
        content = ExportPNGDialog(export_png=self.export_png, cancel=self.dismiss_popup)
        self._popup = Popup(title="Export PNG", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def export_png(self, path, filename, option):
        """This method saves the chosen plot as a PNG image file.

        input variable(s):

        * path: the directory path to save the PNG image file in
        * filename: the name of the PNG image file
        * option: the plot chosen to be saved
        """
        # do not do anything if filename is still empty
        if filename == "":
            return

        config = App.get_running_app().config
        config.set("Export", "epng_path", os.path.dirname(os.path.join(path, filename)))
        config.write()
        option = option[:-2]
        if option in ["Audible Noise", "Electric Field", "Magnetic Field"]:
            if ".png" not in filename:
                filename += ".png"
            self.dtp.export_png(path, filename, option)
            self.dismiss_popup()

    def show_load(self):
        """This method shows the BuzzLoadDialog popup."""
        content = BuzzLoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(
            title="Load a Tower Configuration JSON File",
            content=content,
            size_hint=(0.9, 0.9),
        )
        self._popup.open()

    def load(self, path, selection):
        """This method handles the loading of the tower configuration from a
        JSON file.

        input variable(s):

        * path: the directory path where the JSON file is to be found
        * selection: the filenames selected
        """
        if len(selection) > 0 or path.endswith(".json"):
            if path.endswith(".json"):
                selection = [os.path.basename(path)]
                path = os.path.dirname(path)
            try:
                config = App.get_running_app().config
                config.set(
                    "Export",
                    "load_path",
                    os.path.dirname(os.path.join(path, selection[0])),
                )
                config.write()
                self._loadedJSON = os.path.basename((os.path.join(path, selection[0])))

                load_file = os.path.join(path, selection[0])
                self.tower.load_tower_config(load_file)
            except KeyError:
                Logger.exception("Buzz Error: cannot open %s", load_file)
                self.dismiss_popup()
                return
            self.ss.setup_system_select()
            self.cl.remove_active_system()
            self.dtp.update_plots()
            self.dismiss_popup()

    def show_save(self):
        """This method shows the BuzzSaveDialog popup."""
        content = BuzzSaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(
            title="Save the Current Tower Configuration as a JSON File",
            content=content,
            size_hint=(0.9, 0.9),
        )
        self._popup.open()

    def save(self, path, filename):
        """This method handles the saving of the tower configuration to a JSON
        file.

        input variable(s):

        * path: the directory path where the JSON file is to be found
        * selection: the filenames selected
        """
        self.cl.set_params()
        if len(filename) > 0:
            config = App.get_running_app().config
            config.set("Export", "save_path", os.path.dirname(os.path.join(path, filename)))
            config.write()
            self.tower.save_tower_config(os.path.join(path, filename + ".json"))
            self.dismiss_popup()

    def dismiss_popup(self):
        """This method closes the active popup."""
        self._popup.dismiss()


def system_geometry_data(system):
    """Assemble info about the geometry of a system in table format (nested list of strings)."""
    return (
        [
            [
                "System Type:",
                system.system_type.upper(),
                "Voltage [kV]:",
                f"{system.voltage / 1000:.2f}",
                "Current [kA]:",
                f"{system.current / 1000:.3f}",
                "",
            ],
            [
                "Line Type",
                "X-Coord [m]",
                "Y-Coord [m]",
                "# Conductors",
                "r_con [mm]",
                "r_bundle [mm]",
                "alpha [°]",
            ],
        ]
        + [
            [
                line.line_type,
                f"{line.line_x:.2f}",
                f"{line.line_y:.2f}",
                line.num_con,
                f"{line.con_radius * 1000:.2f}",
                f"{line.bundle_radius * 1000:.2f}",
                f"{line.con_angle_offset:.2f}",
            ]
            for line in system.lines
        ]
        + [["", "", "", "", "", "", ""]]
    )


def system_em_entries(system):
    """Assemble info about the currents and voltages of a system in table format (nested list of strings)."""
    for line in system.lines:
        row_entry = [
            LINE_TYPES[line.line_type],
            # line coordinates
            f"({line.line_x}, {line.line_y})",
        ]
        # get the average maximum electric fields
        try:
            row_entry += [f"{line.E_ac:.2f}", f"{line.E_dc:.2f}"]
        except AttributeError:
            row_entry += ["", ""]
        try:
            row_entry += [
                f"{line.AC_EPRI_L_w50:.2f}",
                f"{line.AC_BPA_L_w50:.2f}",
            ]
        except AttributeError:
            row_entry += ["", ""]
        try:
            row_entry += [
                f"{line.DC_EPRI_L_w50:.2f}",
                f"{line.DC_BPA_L_w50:.2f}",
                f"{line.DC_CRIEPI_L_w50:.2f}",
            ]
        except AttributeError:
            row_entry += ["", "", ""]
        yield row_entry


class BuzzApp(App):
    """BuzzApp is the root application. BuzzApp handles the settings and returns
    MainLayout as the user interface.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_layout = None
        # change the icon from default Kivy logo
        self.icon = os.path.join(MODULE_DIR, "images", "buzz_logo.png")
        # define the style of the settings
        self.settings_cls = SettingsWithSidebar

    def build(self):
        # return the MainLayout
        self.main_layout = MainLayout()
        return self.main_layout

    def build_config(self, config):
        """This method sets up the settings page."""

        # define the default values for tower geometry settings
        config.setdefaults(
            "Tower Geometry",
            {
                "radius_mult": 15,
                "auto_axis": False,
                "lower_axis": 20,
                "upper_axis": 80,
                "ac_con_color": "blue",
                "dc_pos_con_color": "red",
                "dc_neg_con_color": "green",
                "dc_neut_con_color": "black",
                "gnd_con_color": "black",
            },
        )

        # define the default values for audible noise settings
        config.setdefaults(
            "Audible Noise",
            {
                "ground_points_start": -60,
                "ground_points_end": 60,
                "ground_points_n": 121,
                "auto_axis": False,
                "lower_axis": 20,
                "upper_axis": 80,
                "an_unit": "dB over 1 pW/m",
                "altitude": 0,
                "ac_epri_bool": 1,
                "ac_epri_weather": "Foul",
                "ac_epri_offset": 0,
                "ac_epri_rain_corr": "0.8",
                "ac_bpa_bool": 1,
                "ac_bpa_weather": "Foul",
                "ac_bpa_offset": 0,
                "dc_epri_bool": 1,
                "dc_epri_weather": "Fair",
                "dc_epri_season": "Summer",
                "dc_bpa_bool": 1,
                "dc_bpa_weather": "Fair",
                "dc_bpa_season": "Summer",
                "dc_criepi_bool": 1,
            },
        )

        # define the default values for electric field settings
        config.setdefaults(
            "Electric Field",
            {
                "electric_field_num_contour": 0.0,
                "height_above_ground": 1.5,
                "ground_points_start": -60,
                "ground_points_end": 60,
                "ground_points_n": 121,
                "auto_axis": True,
                "lower_axis": 0,
                "upper_axis": 20,
            },
        )

        # define the default values for magnetic field settings
        config.setdefaults(
            "Magnetic Field",
            {
                "height_above_ground": 1.5,
                "ground_points_start": -60,
                "ground_points_end": 60,
                "ground_points_n": 121,
                "auto_axis": True,
                "lower_axis": 0,
                "upper_axis": 100,
            },
        )

        # define the default values for export settings
        config.setdefaults(
            "Export",
            {
                "csv_delimiter": ";",
                "csv_decimal": ".",
                "load_path": "default load path",
                "save_path": "default save path",
                "ecsv_path": "default ecsv path",
                "epdf_path": "default epdf path",
                "epng_path": "default epng path",
            },
        )

    def build_settings(self, settings):
        """This method loads the settings layout from the corresponding
        JSON files.
        """

        # load tower geometry settings
        settings.add_json_panel(
            "Tower Geometry",
            self.config,
            os.path.join(SETTINGS_DIR, "tower_geometry.json"),
        )
        # load audible noise settings
        settings.add_json_panel(
            "Audible Noise",
            self.config,
            os.path.join(SETTINGS_DIR, "audible_noise.json"),
        )
        # load electric field settings
        settings.add_json_panel(
            "Electric Field",
            self.config,
            os.path.join(SETTINGS_DIR, "electric_field.json"),
        )
        # load magnetic field settings
        settings.add_json_panel(
            "Magnetic Field",
            self.config,
            os.path.join(SETTINGS_DIR, "magnetic_field.json"),
        )
        # load export settings
        settings.add_json_panel("Export", self.config, os.path.join(SETTINGS_DIR, "export.json"))

    def on_config_change(self, _config, _section, _key, _value):
        """This method prompts the settings parser belonging to the plot to
        reload the settings from the buzz.ini file.
        """
        self.main_layout.reset_settings_parser()


if __name__ == "__main__":
    main()
