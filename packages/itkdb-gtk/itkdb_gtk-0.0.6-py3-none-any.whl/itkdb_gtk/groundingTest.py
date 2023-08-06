#!/usr/bin/env python3
"""Test dashboard."""
import json
import sys

try:
    import dbGtkUtils
    import ITkDBlogin
    import ITkDButils
except ModuleNotFoundError:
    from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class GroundingTest(dbGtkUtils.ITkDBWindow):
    """Dashboard class."""

    def __init__(self, session):
        """Initialization."""
        super().__init__(title="ITkDB Dashboard",
                         session=session,
                         show_search="Find object with given SN.")

        # Members
        self.dbObject = None

        # action button in header
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-send-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.set_tooltip_text("Click to upload tests.")
        button.connect("clicked", self.upload_tests)
        self.hb.pack_end(button)

        grid = Gtk.Grid(column_spacing=5, row_spacing=1)
        self.mainBox.pack_start(grid, False, False, 5)

        lbl = Gtk.Label(label="Serial Number")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 0, 1, 1)

        self.SN = Gtk.Entry()
        grid.attach(self.SN, 1, 0, 1, 1)

        lbl = Gtk.Label(label="Institute")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, 1, 1, 1)

        self.institute = "IFIC"
        inst = self.create_institute_combo()
        inst.connect("changed", self.new_institute)
        inst.set_tooltip_text("Select the Institute.")
        grid.attach(inst, 1, 1, 1, 1)
        self.inst_cmb = inst

        # The "Add/Remove/Send Item" buttons.
        box = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_layout(Gtk.ButtonBoxStyle.END)
        self.mainBox.pack_start(box, False, False, 0)
        dbGtkUtils.add_button_to_container(box, "Add Defect", "Click to add a defect", self.add_defect)
        dbGtkUtils.add_button_to_container(box, "Add Comment", "Click to add a comment", self.add_comment)

        # The notebook
        self.notebook = Gtk.Notebook()
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.notebook.set_size_request(-1, 250)
        self.mainBox.pack_start(self.notebook, True, True, 0)

        # Create the Notebook pages
        self.create_test_box("Visual Inspection", "VISUAL_INSPECTION")
        self.create_test_box("Grounding", "GROUNDING_CHECK")

        # The text view
        frame = self.create_text_view()
        self.mainBox.pack_end(frame, True, True, 5)

        self.show_all()

    def create_test_box(self, label, test_name, institute="IFIC"):
        """Create and add to notebook a test dialog.

        Args:
        ----
            label: The label for the Notebook
            test_name: The DB name of the test
            institute: The institute.

        """
        defaults = {
            "institution": institute,
            "runNumber": "1",
        }
        dto = ITkDButils.get_test_skeleton(self.session, "CORE_PETAL", test_name, defaults)
        if test_name == "VISUAL_INSPECTION":
            scrolled, gM = dbGtkUtils.create_scrolled_dictdialog(dto, ("component", "testType", "results"))
        else:
            scrolled, gM = dbGtkUtils.create_scrolled_dictdialog(dto)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_border_width(5)
        box.pack_end(scrolled, True, True, 0)
        box.dict_dialog = gM
        gM.box = box

        self.notebook.append_page(box, Gtk.Label(label=label))

        return gM

    def query_db(self, *args):
        """Search button clicked."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Empty Serial number",
                                "You should enter a valid Serial number for the petal core.",
                                parent=self)

        try:
            self.dbObject = ITkDButils.get_DB_component(self.session, SN)

        except Exception as E:
            self.write_message(str(E))
            dbGtkUtils.complain("Could not find object in DB", str(E))
            self.dbObject = None
            return

        print(json.dumps(self.dbObject, indent=3))

    def add_defect(self, btn):
        """Add a new defect."""
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        values = dbGtkUtils.get_a_list_of_values("Insert new defect", ("Type", "Description/v"))
        if len(values):
            defect = {"name": values[0], "description": values[1]}
            page.dict_dialog.values["defects"].append(defect)
            page.dict_dialog.refresh()

    def add_comment(self, btn):
        """Add a new comment."""
        page = self.notebook.get_nth_page(self.notebook.get_current_page())
        comment = dbGtkUtils.get_a_value("Insert new comment", is_tv=True)
        if comment:
            page.dict_dialog.values["comments"].append(comment)
            page.dict_dialog.refresh()

    def new_institute(self, combo):
        """A new institute has been selected."""
        inst = self.get_institute_from_combo(combo)
        if inst:
            self.institute = inst

            npages = self.notebook.get_n_pages()
            for i in range(npages):
                page = self.notebook.get_nth_page(i)
                page.dict_dialog.values["institution"] = self.institute
                page.dict_dialog.refresh()

    def upload_tests(self, *args):
        """Upload the current test."""
        SN = self.SN.get_text()
        if len(SN) == 0:
            dbGtkUtils.complain("Petal SN is empty")
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
        rc = ITkDButils.upload_test(self.session, values)
        if rc is not None:
            dbGtkUtils.complain("Could not upload test", rc)

        else:
            dbGtkUtils.ask_for_confirmation("Test uploaded.",
                                            "{} - {}".format(values["component"], values["testType"]))

def main():
    """Main entry."""
    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    gTest = GroundingTest(client)

    gTest.present()
    gTest.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()


if __name__ == "__main__":
    main()