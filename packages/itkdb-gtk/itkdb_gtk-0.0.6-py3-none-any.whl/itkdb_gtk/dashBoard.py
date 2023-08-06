#!/usr/bin/env python3
"""Test dashboard."""
import sys

try:
    import dbGtkUtils
    import getShipments
    import groundingTest
    import ITkDBlogin
    import sendShipments
    import uploadTest
    import GlueWeight

except Exception:
    from itkdb_gtk import dbGtkUtils, getShipments, groundingTest, ITkDBlogin, sendShipments, uploadTest, GlueWeight

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DashWindow(dbGtkUtils.ITkDBWindow):
    """Dashboard class."""

    def __init__(self, session):
        """Initialization."""
        super().__init__(title="ITkDB Dashboard", session=session)
        self.mask = 0

        # set border width
        self.set_border_width(10)

        # Prepare dashboard
        lbl = Gtk.Label()
        lbl.set_markup("<big><b>ITkDB available commands.</b></big>")
        self.mainBox.pack_start(lbl, True, True, 0)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        self.mainBox.pack_start(grid, False, True, 5)

        irow = 0
        lbl = Gtk.Label()
        lbl.set_markup("<b>Tests</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        btnTest = Gtk.Button(label="Upload Test (json)")
        btnTest.connect("clicked", self.upload_test)
        grid.attach(btnTest, 0, irow, 1, 1)

        btnGnd = Gtk.Button(label="Petal VI/GND")
        btnGnd.connect("clicked", self.petal_gnd)
        grid.attach(btnGnd, 1, irow, 1, 1)

        irow += 1
        btnWeight = Gtk.Button(label="GlueWeight")
        btnWeight.connect("clicked", self.glue_weight)
        grid.attach(btnWeight, 0, irow, 1, 1)

        irow += 1
        grid.attach(Gtk.Label(), 0, irow, 1, 1)

        irow += 1
        lbl = Gtk.Label()
        lbl.set_markup("<b>Shipments</b>")
        lbl.set_xalign(0)
        grid.attach(lbl, 0, irow, 1, 1)

        irow += 1
        sendS = Gtk.Button(label="Create Shipment")
        sendS.connect("clicked", self.create_shipment)
        grid.attach(sendS, 0, irow, 1, 1)

        recS = Gtk.Button(label="Receive Shipment")
        recS.connect("clicked", self.receive_shipment)
        grid.attach(recS, 1, irow, 1, 1,)

        self.mainBox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, True, 5)

        self.show_all()

    def upload_test(self, *args):
        """Launch upload test."""
        bitn = 1
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = uploadTest.UploadTest(self.session)
        W.connect("destroy", self.app_closed, bitn)

    def create_shipment(self, *args):
        """Launch sendShipment."""
        bitn = 2
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = sendShipments.SendShipments(self.session)
        W.connect("destroy", self.app_closed, bitn)

    def receive_shipment(self, *args):
        """Launch getShipments."""
        bitn = 3
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = getShipments.ReceiveShipments(self.session)
        W.connect("destroy", self.app_closed, bitn)

    def petal_gnd(self, *args):
        """Petal GND/VI test."""
        bitn = 4
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = groundingTest.GroundingTest(self.session)
        W.connect("destroy", self.app_closed, bitn)

    def glue_weight(self, *args):
        """Glue Weight test."""
        bitn = 5
        bt = 1 << bitn
        if self.mask & bt:
            return

        self.mask |= bt
        W = GlueWeight.GlueWeight(self.session)
        W.connect("destroy", self.app_closed, bitn)

    def app_closed(self, *args):
        """Application window closed. Clear mask."""
        bt = 1 << args[1]
        self.mask &= ~bt
        print(bt, self.mask)


def main():
    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    dashW = DashWindow(client)
    dashW.connect("destroy", Gtk.main_quit)
    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()


if __name__ == "__main__":
    main()
