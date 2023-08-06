#!/usr/bin/env python3
"""Check tha a given JSon is valid."""
from pathlib import Path
import json

try:
    import ITkDBlogin
    import ITkDButils
except ModuleNotFoundError:
    from itkdb_gtk import ITkDBlogin, ITkDButils


def checkJSOn(session, ifile):
    """Check teh validity of a JSon test file

    Args:
        fname (): File or data.
    """
    fnam = Path(ifile).expanduser().resolve()
    with open(fnam, 'r') as fin:
        user_file = json.load(fin)

    test_type = user_file["testType"]
    component = ITkDButils.get_DB_component(session, user_file["component"])

    skeleton = ITkDButils.get_test_skeleton(session,
                                            component["componentType"]["code"],
                                            test_type)

    for key in skeleton.keys():
        if key in ["comments", "defects"]:
            continue

        if key not in user_file:
            print("Missing key {}".format(key))
            if key == "institution":
                sites = session.get("listInstitutions", json={})
                print(sites)


if __name__ == "__main__":
    import sys
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    try:
        checkJSOn(client, sys.argv[1])

    except Exception as ex:
        print(ex)

    dlg.die()
