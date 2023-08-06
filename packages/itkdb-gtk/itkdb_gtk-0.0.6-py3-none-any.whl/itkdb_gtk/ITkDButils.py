"""Utilities for the inteaction with the ITkDB."""
import mimetypes
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import dateutil.parser

# The response of the DB
db_response = ""


# define an Attachment object.
class Attachment(object):
    """Encapsulates Attachment information."""

    def __init__(self, path=None, title=None, desc=None):
        """Initialization."""
        self.path = path
        self.title = title
        self.desc = desc


def is_iterable(obj):
    """Tell if an object is iterable. Strings are not considered iterables."""
    if isinstance(obj, Iterable):
        if isinstance(obj, str) or isinstance(obj, bytes):
            return False
        else:
            return True
    else:
        return False


def get_db_response():
    """Return the DB response.

    It is stores in a global variable. Trust the function if call
    right after your interaction with the DB.
    """
    global db_response
    return db_response


def get_db_date(timestamp=None):
    """Convert a date string into the expected DB format.

    Args:
    ----
        timestamp: A date in string format

    """
    def date2string(the_date):
        out = the_date.isoformat(timespec='milliseconds')
        if out[-1] not in ['zZ']:
            out += 'Z'

        return out
        # return the_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    out = None
    if timestamp is None:
        out = date2string(datetime.now())
    elif isinstance(timestamp, datetime):
        out = date2string(timestamp)
    else:
        try:
            this_date = dateutil.parser.parse(timestamp)
            out = date2string(this_date)
        except Exception:
            out = ""

    return out


def registerPetalCore(client, SN, alias, HC_id=None):
    """Register a Petal Core in the DB.

    Args:
    ----
        SN: Serial Number
        alias: The alias of the Petal
        HC_id: Comma separated list of HC identifiers.

    Returns
    -------
        _type_: _description_

    """
    global db_response
    dto = {
        "project": 'S',
        "subproject": "SE",
        "institution": "AVS",
        "componentType": "CORE_PETAL",
        "type": "CORE_AVS",
        "serialNumber": SN,
        "properties": {'DESY_ID': alias}
    }
    if HC_id is not None:
        dto["properties"]["HC_ID"] = HC_id

    db_response = client.post('registerComponent', json=dto)
    try:
        return db_response['component']

    except KeyError:
        return None


def create_component_attachment(client, SN, file_path, title=None, description="", item_type="component"):
    """Create an attachment to the given component.

    Args:
    ----
        client: The DB client
        SN: The SN of the component.
        file_path: The pat to th efile to be attached.
        title: title of the file
        description: Description of the attachment
        item_type: the type of DB object to attach the information

    """
    global db_response
    db_response = None
    path = Path(file_path).expanduser().resolve()
    filetype = mimetypes.guess_type(path)
    if title is None:
        title = path.name

    if item_type == "component":
        c_item = "component"
        cmmd = "createComponentAttachment"

    elif item_type == "shipment":
        c_item = "shipment"
        cmmd = "createShipmentAttachment"

    else:
        print("Unknown dB object")
        db_response = None
        return

    data = {
        c_item: SN,
        'title': title,
        'description': description,
        'type': 'file',
        'url': path.as_uri(),
    }
    # Get attachment data
    attachment = {'data': (path.name, open(path.as_posix(), 'rb'), filetype)}
    try:
        db_response = client.post(cmmd, data=data, files=attachment)

    except Exception as e:
        print("Error creating attachment\n", e)

    return db_response


def set_component_property(client, SN, property, value):
    """Set the value of an object property.

    Args:
    ----
        client: The DB client
        SN: The object SN
        property: The property name
        value: The property value

    """
    global db_response
    try:
        db_response = client.post('setComponentProperty',
                                  json={'component': SN,
                                        'code': property,
                                        'value': value})
        return db_response

    except Exception as e:
        print("Problems setting {} to {} in {}:\n\t{}".format(
            property, value, SN, str(e)))
        return None


def assemble_component(client, parent, child):
    """Assemble child into parent.

    Args:
    ----
        client: The DB client
        parent: The parent object or container.
        child: The child to be assembled.

    """
    global db_response
    try:
        db_response = client.post("assembleComponent",
                                  json={'parent': parent, 'child': child})
        return db_response

    except Exception as e:
        print("Problems assemblying {} into {}:\n\t{}".format(
            child, parent, str(e)))
        return None


def get_DB_component(client, SN):
    """Get ta component by its serial number."""
    global db_response
    db_response = client.get('getComponent', json={'component': SN})
    return db_response


def upload_test(client, data, attachments=None):
    """Upload a test to the DB.

    Args:
    ----
        client: The DB client
        data (dict): A distionary with all the elements of thee test.
        attachments (Attachments): one or more (in a list) Attachments to the test

    Return:
    ------
        resp: The response of the DB session.

    """
    global db_response
    try:
        db_response = client.post("uploadTestRunResults", json=data)
        if attachments is not None:
            if not isinstance(attachments, Iterable):
                attachments = (attachments)

            for att in attachments:
                path = Path(att.path).expanduser().resolve()
                if not path.exists():
                    print("File {} does not exist".format(path))
                    continue

                data = {"testRun": db_response["testRun"]["id"],
                        "title": att.title if att.title is not None else path.name,
                        "description": att.desc if att.desc is not None else path.name,
                        "type": "file",
                        }
                filetype = mimetypes.guess_type(path.name)
                attachment = {'data': (path.name, open(path.as_posix(), 'rb'), filetype[0])}
                db_response = client.post('createTestRunAttachment',
                                          data=data,
                                          files=attachment)

        return None

    except Exception as e:
        return (str(e))


def create_shipment(session, sender, recipient, items, name=None, send=False, type="domestic",
                    attachment=None, comments=None):
    """Create a chipment.

    Args:
    ----
        session : The itkdb session
        sender : The sender ID
        recipient : The recipient ID
        items : A list of SN of the items to be shipped.
        name: the name of the shipment.
        send: If true, the status of the shipment is updated to inTransit
        type (optional): Type of shipment. Defaults to "domestic".
        attachment (optional): Attachment object.
        comments (optional): comments for the shipment

    """
    global db_response
    if name is None:
        name = "From {} to {}".format(sender, recipient)

    if type not in ["domestic", "intraContinental", "continental"]:
        db_response = "Wrong shipment type."
        return None

    if len(items) == 0:
        db_response = "Empty lit of items"
        return None

    the_comments = None
    if comments is not None:
        if not is_iterable(comments):
            the_comments = [comments]
        else:
            the_comments = comments

    data = {
        "name": name,
        "sender": sender,
        "recipient": recipient,
        "type": type,
        "shipmentItems": items,
    }

    if the_comments:
        data["comments"] = the_comments

    try:
        db_response = session.post("createShipment", json=data)

    except Exception as E:
        db_response = str(E)
        return None

    if not send:
        return db_response

    shipment_id = db_response["id"]
    payload = {
        "shipment": shipment_id,
        "status": "inTransit",
    }

    # The items
    items = []
    for item in db_response["shipmentItems"]:
        the_item = {"code": item['code'], "delivered": True}
        items.append(the_item)

    payload["shipmentItems"] = items

    db_response = None
    try:
        db_response = session.post("setShipmentStatus", json=payload)

    except Exception as E:
        db_response = str(E)
        return None

    if attachment:
        try:
            rc = create_component_attachment(session, shipment_id,
                                             attachment.path,
                                             attachment.title,
                                             attachment.desc,
                                             "shipment")
            db_response = rc

        except Exception:
            db_response = "Could not add the attachment."

    return db_response


def set_shipment_status(client, data):
    """Update shipment status."""
    global db_response
    try:
        db_response = client.post("setShipmentStatus", json=data)
        return db_response

    except Exception:
        return None


def from_full_test_to_test_data(full_test):
    """Conver getTest output to json needed to upload the test."""
    test = {
        "component": None,
        "testType": full_test["testType"]["code"],
        "institution": full_test["institution"]["code"],
        "runNumber": full_test["runNumber"],
        "date": full_test["date"],
        "passed": full_test["passed"],
        "problems": full_test["problems"],
        "properties": {},
        "results": {},
        "comments": [],
        "defects": []
    }

    try:
        test["component"] = full_test["components"][0]["serialNumber"]

    except Exception:
        print("from_full_test_to_test_data\nPossible error: no SN found for component.")
        pass

    for P in full_test["properties"]:
        test["properties"][P["code"]] = P['value']

    for P in full_test["results"]:
        test["results"][P["code"]] = P['value']

    for C in full_test["comments"]:
        test["comments"].append(C["comment"])

    for D in full_test["defects"]:
        test["defects"].append({"name": D["name"],
                                "description": D["description"],
                                "properties": D["properties"]})

    return test


def get_testrun(session, test_id, out_type="object"):
    """Retrieve information about a given test.

    Args:
    ----
        session : The itkdb session
        test_id : The ID of the test.
        out_type (optional): Type of output (full or object). Defaults to "object".

    """
    global db_response
    try:
        db_response = session.get("getTestRun", json={"testRun": test_id})
        return db_response

    except Exception:
        return None


def get_test_skeleton(session, component, test_code, userdef={}, uservalues={}):
    """Get the skeleton of the given test.

    Args:
    ----
        session: The DB session
        component: The component which is tested
        test_code: The test code
        userdef: default values of test parameters, propertines and results.
        uservalues: default values for different types.

    """
    global db_response
    defvalues = {
        "string": "",
        "integer": -9999,
        "float": -9999.0,
        "boolean": True,
    }
    for ky, val in defvalues.items():
        if ky not in uservalues:
            uservalues[ky] = val

    data = {"project": "S", "componentType": component}
    out = session.get("listTestTypes", json=data)
    db_response = out
    the_test = None
    for tst in out:
        # print(tst['code'])
        if tst['code'] == test_code:
            the_test = tst
            break

    if the_test is None:
        print("test {} not found for {}".format(test_code, component))
        return None

    # for prop in the_test["properties"]:
    #     print("{}; {}".format(prop["code"], prop["name"]))

    # for prop in the_test["parameters"]:
    #     print("{}; {}".format(prop["code"], prop["name"]))

    skltn = {
        "component": None,
        "testType": test_code,
        "institution": None,
        "runNumber": "-1",
        "date": get_db_date(),
        "passed": True,
        "problems": False,
        "properties": {},
        "results": {},
        "comments": [],
        "defects": []
    }

    # Set default values
    for key in skltn.keys():
        if key in userdef:
            if isinstance(skltn[key], dict):
                continue

            skltn[key] = userdef[key]

    def get_default(vin, default=None):
        # print(json.dumps(vin, indent=1))
        if vin['valueType'] == "single":
            vtype = vin['dataType']
            val = None
            if vtype in uservalues:
                val = uservalues[vtype]
            else:
                # print("default for data type ", vtype, " not found")
                val = None

        else:
            val = None

        return val

    # SEt the properties
    for prop in the_test['properties']:
        key = prop["code"]
        if 'properties' in userdef and key in userdef['properties']:
            skltn['properties'][key] = userdef['properties'][key]
        else:
            skltn['properties'][key] = get_default(prop)

    # SEt the parameters
    for par in the_test['parameters']:
        key = par["code"]
        if 'results' in userdef and key in userdef['results']:
            skltn['results'][key] = userdef['results'][key]
        else:
            skltn['results'][key] = get_default(par)

    return skltn
