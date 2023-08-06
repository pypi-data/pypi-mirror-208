from . import dashBoard


def dash_board():
    """Launches the dash board."""
    dashBoard.main()


def getShipments():
    """getShipments."""
    from .getShipments import main
    main()


def glueWeight():
    """glue weight."""
    from .GlueWeight import main
    main()


def groundingTest():
    """GND/VI tests."""
    from .groundingTest import main
    main()


def sendShipments():
    """Send items."""
    from .sendShipments import main
    main()


def uploadTest():
    """Upload tests."""
    from .uploadTest import main
    main()