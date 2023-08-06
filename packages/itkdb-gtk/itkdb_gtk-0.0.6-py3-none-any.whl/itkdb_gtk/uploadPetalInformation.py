#!/usr/bin/env python3
"""Uploads data from AVS pdf."""
import json
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path

import dateutil.parser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

try:
    import readAVSdata
    import ITkDBlogin
    import ITkDButils

    from dbGtkUtils import replace_in_container, complain, DictDialog, ask_for_confirmation

except ModuleNotFoundError:
    from itkdb_gtk import readAVSdata, ITkDBlogin, ITkDButils
    from itkdb_gtk.dbGtkUtils import replace_in_container, complain, DictDialog, ask_for_confirmation
    

def create_scrolled_dictdialog(the_dict, hidden=("component", "testType")):
    """Create a DictDialog within a scrolled window.

    Return:
    ------
        scrolled: the scrolled window
        gM: the DictDialog

    """
    gM = DictDialog(the_dict, hidden)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled.add(gM)
    return scrolled, gM


class AVSPanel(Gtk.Window):
    """Dialog for interaction with DB."""

    def __init__(self, session, options):
        """Initialization."""
        super().__init__(title="Upload AVS Data")
        self.db_session = session
        self.test_uploaded = {}
        self.test_list = []
        self.test_index = {}
        self.test_panel = {}
        self.test_map = {}
        self.petal_core = None
        self.petal_weight = -1
        # self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #
        # Prepare HeaderBar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "DB Upload Petal Data"
        self.set_titlebar(hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test shown in notebook.")
        button.connect("clicked", self.upload_current_test)
        hb.pack_end(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="emblem-documents-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload AVS files.")
        button.connect("clicked", self.upload_avs_files)
        hb.pack_end(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="system-search-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to search SN in data base.")
        button.connect("clicked", self.query_db)
        hb.pack_end(button)

        self.userLabel = Gtk.Label()
        self.userLabel.set_text(session.user.name)
        hb.pack_start(self.userLabel)

        #
        # Crete man contentt box
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.mainBox)

        # PS file entry and search button
        self.btnPSF = Gtk.FileChooserButton()
        self.btnPSF.connect("file-set", self.on_psf_set)
        if options.PS:
            ifile = Path(options.PS).expanduser().resolve().as_posix()
            self.btnPSF.set_filename(ifile)
            self.on_psf_set()

        # FAT file entry and seach buttin
        self.btnFAT = Gtk.FileChooserButton()
        self.btnFAT.connect("file-set", self.on_fat_set)
        if options.FAT:
            ifile = Path(options.FAT).expanduser().resolve().as_posix()
            self.btnFAT.set_filename(ifile)

        # The Serial number
        self.SN = Gtk.Entry()
        # self.SN.connect("changed", self.SN_changed)
        if options.SN:
            self.SN.set_text(options.SN)

        # Put the 3 objects in a Grid
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, False, True, 0)

        grid.attach(Gtk.Label(label="Serial No."), 0, 0, 1, 1)
        grid.attach(self.SN, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Prod. Sheet"), 0, 1, 1, 1)
        grid.attach(self.btnPSF, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="FAT file"), 0, 2, 1, 1)
        grid.attach(self.btnFAT, 1, 2, 1, 1)

        # Add a Separator
        self.mainBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, True, 0)

        # The notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.mainBox.pack_start(self.notebook, True, True, 20)

        # Create the Notebook pages
        defaults = {
            "institution": "AVS",
            "runNumber": 1,
        }

        self.manufacture = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.db_session, "CORE_PETAL", "MANUFACTURING", defaults),
            "manufacture", "Manufacture")

        self.weights = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.db_session, "CORE_PETAL", "WEIGHING", defaults),
            "weights", "Weights")

        self.delamination = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.db_session, "CORE_PETAL", "DELAMINATION", defaults),
            "delamination", "Delamination")

        self.grounding = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.db_session, "CORE_PETAL", "GROUNDING_CHECK", defaults),
            "grounding", "Grounding")

        self.metrology = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.db_session, "CORE_PETAL", "METROLOGY_AVS", defaults),
            "metrology", "Metrology")

        self.visual_inspection = self.create_test_window(
            ITkDButils.get_test_skeleton(
                self.db_session, "CORE_PETAL", "VISUAL_INSPECTION", defaults),
            "visual_inspection", "Visual Inspection")

        # List componentes
        self.components = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.components.set_border_width(5)
        self.notebook.append_page(self.components, Gtk.Label(label="Components"))

        # The button box
        btnBox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)

        btn = Gtk.Button(label="Reload AVS files")
        btn.connect("clicked", self.read_avs_files)
        btnBox.add(btn)

        btn = Gtk.Button(label="Query DB")
        btn.connect("clicked", self.query_db)
        btnBox.add(btn)

        btn = Gtk.Button(label="Assemble")
        btn.connect("clicked", self.on_assembly)
        btnBox.add(btn)

        btn = Gtk.Button(label="Upload Tests")
        btn.connect("clicked", self.on_upload)
        btnBox.add(btn)

        btn = Gtk.Button(label="Quit")
        btn.connect("clicked", Gtk.main_quit)
        btnBox.add(btn)

        self.mainBox.pack_start(btnBox, False, True, 0)
        self.connect("destroy", Gtk.main_quit)

    def create_test_window(self, test_json, test_name, label):
        """Create the dialog for a DB test and add it to the notebook.

        Args:
        ----
            test_json: The JSon-like dict with the values
            test_name: The name of the test for internal indexing
            label: The label for the Notebook

        Return:
        ------
            The box containing the data.

        """
        scrolled, gM = create_scrolled_dictdialog(test_json)
        self.test_list.append(gM)
        self.test_index[test_name] = len(self.test_list) - 1
        self.test_map[test_json["testType"]] = test_name

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)
        box.pack_end(scrolled, True, True, 0)
        box.dict_dialog = gM
        gM.box = box
        self.test_panel[test_name] = box
        self.notebook.append_page(box, Gtk.Label(label=label))

        return box

    def update_scroll_window(self, key, data):
        """Update panel for a given test."""
        scrolled, gM = create_scrolled_dictdialog(data, ("component", "testType"))
        self.test_list[self.test_index[key]] = gM
        replace_in_container(self.test_panel[key], scrolled)

    def check_register_petal(self, SN):
        """Register teal core in DB.

        Args:
        ----
            SN: The petal Serial Number.

        """
        if self.petal_core:
            return

        self.find_petal(SN, silent=True)
        if self.petal_core:
            return

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            text="Register Petal Core\n{}".format(SN)
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                           Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_border_width(10)
        dialog.format_secondary_text("Enter Petal Core Alias")
        alias = Gtk.Entry()
        box = dialog.get_content_area()
        box.add(alias)
        dialog.show_all()
        out = dialog.run()
        if out == Gtk.ResponseType.OK:
            petal_alias = alias.get_text()
            rc = ITkDButils.registerPetalCore(self.db_session, SN, petal_alias)
            if rc is None:
                complain("Could not Register petal {} ({})".format(SN, petal_alias))

        dialog.hide()
        dialog.destroy()

    def get_app_petal_serial_number(self):
        """Get the SN from the text box."""
        txt_SN = self.SN.get_text().strip()
        return txt_SN

    def check_petal_serial_number(self, SN):
        """Check tha the given SN is consistent."""
        txt_SN = self.get_app_petal_serial_number()
        if txt_SN and len(txt_SN):
            if txt_SN != SN.strip():
                return False

            else:
                return True

        else:
            self.check_register_petal(SN)
            self.SN.set_text(SN)
            return True

    def on_psf_set(self, *args):
        """Production Sheet file selected."""
        PSF = self.btnPSF.get_filename()
        if PSF is None or not Path(PSF).exists():
            complain("Could not find Production File", PSF, parent=self)
            return

        try:
            manuf_json, weights_json, self.DESY_comp = readAVSdata.readProductionSheet(self.db_session, PSF, "SNnnnn")
            if self.petal_weight > 0:
                weights_json["results"]["WEIGHT_CORE"] = self.petal_weight

        except readAVSdata.AVSDataException as E:
            complain("Wrong Production Sheet file", str(E))
            self.btnPSF.unselect_all()
            return

        SN = manuf_json["component"]
        if not self.check_petal_serial_number(SN):
            complain("Inconsistent Serial number found.",
                     "Wrong Serial number extracted from the Production Sheet document.\n{}".format(PSF))
            self.btnPSF.unselect_all()
            return

        scrolled, gM = create_scrolled_dictdialog(manuf_json, ("component", "testType"))
        self.test_list[self.test_index["manufacture"]] = gM
        replace_in_container(self.manufacture, scrolled)

        scrolled, gM = create_scrolled_dictdialog(weights_json, ("component", "testType"))
        self.test_list[self.test_index["weights"]] = gM
        replace_in_container(self.weights, scrolled)

        gD = DictDialog(self.DESY_comp)
        replace_in_container(self.components, gD)

        # Check if we need to assemble the module
        self.check_assembly(self.DESY_comp)

    def on_fat_set(self, *args):
        """FAT file selected."""
        FAT = self.btnFAT.get_filename()
        if FAT is None or not Path(FAT).exists():
            complain("Could not find FAT File", FAT, parent=self)

        try:
            SN = self.get_app_petal_serial_number()
            if SN and not SN.startswith("20USEBC"):
                SN = None

            j_vi, j_del, j_gnd, j_mtr, batch, self.petal_weight = readAVSdata.readFATfile(self.db_session, FAT, SN)
            self.test_list[self.test_index["weights"]].set_value("results.WEIGHT_CORE", self.petal_weight)

        except readAVSdata.AVSDataException as E:
            complain("Wrong FAT file", str(E))
            self.btnFAT.unselect_all()
            return

        SN = j_vi["component"]
        if not self.check_petal_serial_number(SN):
            complain("Inconsistent Serial number found.",
                     "Wrong Serial number extracted from the FAT document.\n{}".format(FAT))
            self.btnFAT.unselect_all()
            return

        self.update_scroll_window("visual_inspection", j_vi)
        self.update_scroll_window("delamination", j_del)
        self.update_scroll_window("grounding", j_gnd)
        self.update_scroll_window("metrology", j_mtr)

    def read_avs_files(self, widgets):
        """Read AVS files."""
        PSF = self.btnPSF.get_filename()
        if PSF is not None:
            self.on_psf_set(None)

        FAT = self.btnFAT.get_filename()
        if FAT is not None:
            self.on_fat_set(None)

        return

    def find_petal(self, SN, silent=False):
        """Finds petal with given SN."""
        try:
            self.petal_core = ITkDButils.get_DB_component(self.db_session, SN)

        except Exception as E:
            if not silent:
                complain("Could not find Petal Core in DB", str(E))

            self.petal_core = None
            return

        try:
            if self.petal_core["type"]["code"] != "CORE_AVS":
                complain("Wrong component type", "This is not an AVS petal core")

            if self.petal_core["currentStage"]["code"] != "ASSEMBLY":
                complain("Wrong component stage", "Wrong stage: {}".format(self.petal_core["currentStage"]["code"]))

            print(json.dumps(self.petal_core, indent=3))

        except KeyError:
            # Petal is not there
            self.petal_core = None

    def query_db(self, widget=None, silent=False):
        """Called when QueryDB button clicked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            complain("Empty Serial number",
                     "You should enter a valid Serial number for the petal core.",
                     parent=self)
            self.petal_core = None
            return

        # if not checkSerialNumber(SN):
        #     complain("Wrong Serial number",
        #              "You should enter a valid Serial number for the petal core.",
        #              parent=self)
        #     return
        self.find_petal(SN, silent=silent)

        if self.btnFAT.get_filename() is None and self.btnPSF.get_filename() is None:
            # update tests from DB
            for test in self.petal_core["tests"]:
                latest = None
                latest_time = datetime.datetime(year=1, month=1, day=1, tzinfo=datetime.timezone.utc)
                testType = test["code"]
                for T in test["testRuns"]:
                    test_date = dateutil.parser.parse(T["cts"])
                    if test_date > latest_time:
                        latest_time = test_date
                        latest = T["id"]

                dbT = ITkDButils.get_testrun(self.db_session, latest)
                testDB = ITkDButils.from_full_test_to_test_data(dbT)
                self.update_scroll_window(self.test_map[testType], testDB)

    def check_assembly(self, components):
        """Check if we need to assemble components to core."""
        if self.petal_core is None:
            self.query_db()
            if self.petal_core is None:
                return

        comp_map = {
            "BT_PETAL_FRONT": "FacingFront",
            "BT_PETAL_BACK": "FacingBack",
            "COOLING_LOOP_PETAL": "CoolingLoop",
            "THERMALFOAMSET_PETAL": "AllcompSet"
        }
        missing = []
        for child in self.petal_core["children"]:
            if child["component"] is None:
                if child["type"] is not None:
                    ctype = child["type"]["code"]
                else:
                    ctype = child["componentType"]["code"]

                missing.append(ctype)

        if len(missing) == 0:
            return

        error_txt = []
        txt = "Click OK to add\n\t{}".format("\n\t".join(missing))
        if ask_for_confirmation("Missing components", txt, parent=self):
            this_petal = self.SN.get_text()
            for cmp in missing:
                SN = components[comp_map[cmp]]
                if SN[0:5] == "20USE":
                    rc = ITkDButils.assemble_component(self.db_session, this_petal, SN)
                    if rc is None:
                        error_txt.append("Problem assembling {} into Petal\n".format(cmp))

            # Check for HonneyComb set
            for P in self.petal_core["properties"]:
                if P["code"] == "HC_ID" and P["value"] is None:
                    rc = ITkDButils.set_component_property(self.db_session,
                                                           this_petal,
                                                           "HC_ID",
                                                           components["HoneyCombSet"])
                    if rc is None:
                        error_txt.append("Problems setting HoneCombSet ID.\n")

                    break

            if len(error_txt):
                complain("Assembly of {} could not be completeed:".format(this_petal),
                         "\n".join(error_txt))

    def upload_current_test(self, *args):
        """Called with upload button clcked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            complain("Petal SN is empty")
            return

        def find_children(W):
            try:
                for c in W.get_children():
                    if "DictDialog" in c.get_name():
                        return c

                    else:
                        return find_children(c)

            except Exception:
                return None

            return None

        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        dctD = find_children(page)
        if dctD is None:
            return

        values = dctD.values
        values["component"] = SN
        print(json.dumps(values, indent=2))
        rc = ITkDButils.upload_test(self.db_session, values)
        if rc is not None:
            complain("Could not upload test", rc)

        else:
            ask_for_confirmation("Test uploaded.",
                                 "{} - {}".format(values["component"], values["testType"]))

    def upload_avs_files(self, *args):
        """Called when upload AVS files clicked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            complain("Petal SN is empty")
            return

        def upload_file(file_path, title, desc):
            if file_path is not None:
                if not Path(file_path).exists():
                    complain("Could not find {}".format(title))

                else:
                    try:
                        ITkDButils.create_component_attachment(self.db_session, SN, file_path, description=desc)

                    except Exception as e:
                        complain("Could not Upload {}".format(desc), str(e))

        PSF = self.btnPSF.get_filename()
        upload_file(PSF, "Production File", "AVS Production file")

        FAT = self.btnFAT.get_filename()
        upload_file(FAT, "FAT file", "AVS FAT file")

    def on_assembly(self, widget):
        """Assembly button clicked."""
        self.check_assembly(self.DESY_comp)

    def on_upload(self, widget):
        """Upload tests to DB."""
        if self.petal_core is None:
            self.query_db()
            if self.petal_core is None:
                return

        for test in self.test_list:
            values = test.values
            print(values["testType"])
            res = ITkDButils.upload_test(self.db_session, values)
            if res is not None:
                complain("Could not upload test {}".format(values["testType"]), res)


if __name__ == "__main__":
    # Parse command line options
    parser = ArgumentParser()
    parser.add_argument('files', nargs='*', help="Input files")
    parser.add_argument("--SN", dest="SN", type=str, default=None,
                        help="Module serial number")
    parser.add_argument("--PS", dest="PS", type=str, default=None,
                        help="Produc tion Sheet file")
    parser.add_argument("--FAT", dest="FAT", type=str, default=None,
                        help="FAT file")

    options = parser.parse_args()

    # ITk_PB authentication
    dlg = ITkDBlogin.ITkDBlogin()
    session = dlg.get_client()

    # Start the Application
    win = AVSPanel(session, options)
    win.show_all()
    win.set_accept_focus(True)
    win.present()
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("Arrggggg !!!")

    print("Bye !!")
    dlg.die()
    sys.exit()
