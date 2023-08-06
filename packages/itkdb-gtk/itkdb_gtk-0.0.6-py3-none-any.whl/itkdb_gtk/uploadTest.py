#!/usr/bin/env python3
"""GUI to upload tests."""
import argparse
import json
import sys
from pathlib import Path

try:
    import dbGtkUtils
    import ITkDBlogin
    import ITkDButils
except ModuleNotFoundError:
    from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

# Check if Gtk can be open
gtk_runs, gtk_args = Gtk.init_check()


def check_data(data):
    """Checks validity of JSon data.

    Args:
    ----
        data (): The json data

    Returns
    -------
        boolean: True if valid, False otherwise.

    """
    errors = []
    missing = []
    if "component" not in data:
        errors.append("Need reference to component, hex string")
        missing.append("component")

    if "testType" not in data:
        errors.append("Need to know test type, short code")
        missing.append("testType")

    if "institution" not in data:
        errors.append("Need to know institution, short code")
        missing.append("institution")

    if "results" not in data:
        errors.append("Need some test results")
        missing.append("results")

    return errors, missing


class UploadTest(dbGtkUtils.ITkDBWindow):
    """Collects informatio to upload a test and its attachments."""

    def __init__(self, session, payload=None, attachment=None):
        """Initialization.

        Args:
        ----
            session: ITkDB session
            payload: path of test file
            attachment: an Attachment object.

        """
        self.payload = payload
        self.data = None
        self.attachments = []
        if attachment is not None:
            if isinstance(attachment, ITkDButils.Attachment):
                if attachment.path is not None:
                    self.attachments.append(attachment)
            else:
                print("Wrong attachment: {}".format(attachment))

        global gtk_runs
        if gtk_runs:
            super().__init__(session=session, title="Upload Test", gtk_runs=gtk_runs)
            self.init_window()

    def init_window(self):
        """Creates the Gtk window."""
        # Initial tweaks
        self.set_border_width(10)

        # Prepare HeaderBar
        self.hb.props.title = "Upload Tests"

        # Active buttin in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload test")
        button.connect("clicked", self.upload_test_gui)
        self.hb.pack_end(button)

        # Data panel
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, True, False, 0)

        # The test file widgets
        lbl = Gtk.Label(label="Test file")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)

        self.testF = Gtk.FileChooserButton()
        self.testF.set_tooltip_text("Click to select JSon test file.")

        grid.attach(self.testF, 1, 0, 1, 1)
        self.testF.connect("file-set", self.on_test_file)
        if self.payload:
            the_path = Path(self.payload).expanduser().resolve()
            if the_path.exists():
                ifile = Path(self.payload).expanduser().resolve().as_posix()
                self.testF.set_filename(ifile)
                self.on_test_file(self.testF)

            else:
                print("Input file does not exists: {}".format(self.payload))

        # This is to show/edit the test file data
        btn = Gtk.Button()
        icon = Gio.ThemedIcon(name="view-paged-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        btn.add(image)
        btn.set_tooltip_text("Click to view/edit test data.")
        btn.connect("clicked", self.show_data)
        grid.attach(btn, 2, 0, 1, 1)

        # Object Data
        lbl = Gtk.Label(label="Serial Number")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 1, 1, 1)

        self.entrySN = Gtk.Entry()
        grid.attach(self.entrySN, 1, 1, 1, 1)

        # Test type
        lbl = Gtk.Label(label="Test Type")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 2, 1, 1)

        self.entryTest = Gtk.Entry()
        grid.attach(self.entryTest, 1, 2, 1, 1)

        # The "Add attachment" button.
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mainBox.pack_start(box, False, False, 0)

        dbGtkUtils.add_button_to_container(box, "Add attachment",
                                           "Click to add a new attachment.",
                                           self.add_attachment)

        dbGtkUtils.add_button_to_container(box, "Remove attachment",
                                           "Click to remove selected attachment.",
                                           self.remove_attachment)

        dbGtkUtils.add_button_to_container(box, "Upload Test",
                                           "Click to upload test.",
                                           self.upload_test_gui)

        # Paned object
        paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        paned.set_size_request(-1, 200)
        self.mainBox.pack_start(paned, True, True, 0)

        # the list of attachments
        tree_view = self.create_tree_view()
        paned.add1(tree_view)

        # The text view
        frame = self.create_text_view()
        paned.add2(frame)

        self.show_all()

    def create_tree_view(self, size=150):
        """Creates the tree vew with the attachments."""
        model = Gtk.ListStore(str, str, str, str)
        self.tree = Gtk.TreeView(model=model)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.tree)
        scrolled.set_size_request(-1, size)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Attachment", renderer, text=0)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", renderer, text=1)
        self.tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Description", renderer, text=2)
        self.tree.append_column(column)

        return scrolled

    def get_test_institute(self):
        """Select an institue."""
        dlg = Gtk.Dialog(title="Select Institution.", flags=0)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        area = dlg.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        area.add(box)

        box.pack_start(Gtk.Label(label="Select an Institute"), False, True, 0)

        combo = self.create_institute_combo()
        box.pack_start(combo, False, True, 5)

        dlg.show_all()
        rc = dlg.run()

        out = None
        if rc == Gtk.ResponseType.OK:
            out = self.get_institute_from_combo(combo)

        dlg.hide()
        dlg.destroy()
        return out

    def on_test_file(self, fdlg):
        """Test file browser clicked."""
        fnam = fdlg.get_filename()

        # The file exists by definition
        try:
            self.data = json.loads(open(fnam).read())
            errors, missing = check_data(self.data)

            if len(missing):
                self.write_message("Some keys are missing in the JSon file.\n")
                self.write_message("{}\n".format("\n".join(['\t'+line for line in missing])))

                if "institution" in missing and len(missing) == 1:
                    site = self.get_test_institute()
                    if site:
                        self.data["institution"] = site
                        self.write_message("Setting Institution to {}\n".format(self.data["institution"]))

                else:
                    dbGtkUtils.complain("Invalid JSON file\n{}".format('\n'.join(errors)), fnam)

            self.entrySN.set_text(self.data["component"])
            self.entryTest.set_text(self.data["testType"])

        except Exception as E:
            self.data = None
            self.write_message("Cannot load file {}\n".format(fnam))
            self.write_message("{}\n".format(str(E)))

    def show_data(self, *args):
        """Show data button clicked."""
        if self.data is None:
            return

        dlg = Gtk.Dialog(title="Test Data")
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)

        dlg.set_property("height-request", 500)
        box = dlg.get_content_area()
        value = dbGtkUtils.DictDialog(self.data)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(value)
        box.pack_start(scrolled, True, True, 10)

        dlg.show_all()

        rc = dlg.run()
        if rc == Gtk.ResponseType.OK:
            self.data = value.values

        dlg.hide()
        dlg.destroy()

    def add_attachment_dialog(self):
        """Create the add attachment dialog."""
        dlg = Gtk.Dialog(title="Add Attachment")
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OK, Gtk.ResponseType.OK)
        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        box = dlg.get_content_area()
        box.add(grid)

        lbl = Gtk.Label(label="File")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)

        lbl = Gtk.Label(label="Title")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 1, 1, 1)

        lbl = Gtk.Label(label="Description")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 2, 1, 1)

        dlg.fC = Gtk.FileChooserButton()
        grid.attach(dlg.fC, 1, 0, 1, 1)

        dlg.att_title = Gtk.Entry()
        grid.attach(dlg.att_title, 1, 1, 1, 1)

        dlg.att_desc = Gtk.Entry()
        grid.attach(dlg.att_desc, 1, 2, 1, 1)

        dlg.show_all()
        return dlg

    def add_attachment(self, *args):
        """Add Attachment button clicked."""
        dlg = self.add_attachment_dialog()
        rc = dlg.run()
        model = self.tree.get_model()
        if rc == Gtk.ResponseType.OK:
            path = Path(dlg.fC.get_filename())
            name = path.name
            T = dlg.att_title.get_text().strip()
            D = dlg.att_desc.get_text().strip()
            model.append([name, T, D, path.as_posix()])

            T = T if len(T) else None
            D = D if len(D) else None
            att = ITkDButils.Attachment(path.as_posix(), T, D)
            self.attachments.append(att)

        dlg.hide()
        dlg.destroy()

    def remove_attachment(self, *args):
        """Remove selected attachment."""
        select = self.tree.get_selection()
        model, iter = select.get_selected()
        if iter:
            values = model[iter]
            for a in self.attachments:
                if a.path == values[3]:
                    rc = dbGtkUtils.ask_for_confirmation("Remove this attachment ?",
                                                         "{} - {}\n{}".format(a.title, a.desc, values[0]))
                    if rc:
                        self.attachments.remove(a)
                        model.remove(iter)

                    break

    def upload_test_gui(self, *args):
        """Uploads test and attachments."""
        self.upload_test()

    def upload_test(self):
        """Uploads test and attachments."""
        if self.data is None:
            self.write_message("No data available to upload\n")
            return

        rc = ITkDButils.upload_test(self.session, self.data, self.attachments)
        if rc:
            ipos = rc.find("The following details may help:")
            msg = rc[ipos:]
            dbGtkUtils.complain("Failed uploading test", msg)

        else:
            self.write_message("Upload successfull")
            dbGtkUtils.ask_for_confirmation("Upload successfull", "")


def main():
    """Main entry."""
    parser = argparse.ArgumentParser()

    parser.add_argument("--test-file", help="Name of json file with test data")
    parser.add_argument("--component-id", help="Override component code")
    parser.add_argument("--raw_data", help="Raw data file", default=None)
    parser.add_argument("--attachment", help="Attachment to upload with the test", default=None)
    parser.add_argument("--attach_title", default=None, type=str, help="The attachment description")
    parser.add_argument("--attach_desc", default="", type=str, help="The attachment description")
    parser.add_argument("--verbose", action="store_true", help="Print what's being sent and received")

    args = parser.parse_args()

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    # Start GUI
    UpT = UploadTest(client,
                     payload=args.test_file,
                     attachment=ITkDButils.Attachment(args.attachment,
                                                      args.attach_title,
                                                      args.attach_desc))

    if gtk_runs:
        UpT.present()
        UpT.connect("destroy", Gtk.main_quit)
        try:
            Gtk.main()

        except KeyboardInterrupt:
            print("Arrrgggg!!!")

    else:
        # Think
        pass

    dlg.die()


if __name__ == "__main__":
    main()
