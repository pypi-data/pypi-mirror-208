import json

from google.protobuf.json_format import MessageToJson
from google.protobuf.message import Message


def message_to_json_dict(message: Message, toCamelCase: bool = False):
    return json.loads(
        MessageToJson(
            message,
            including_default_value_fields=True,
            preserving_proto_field_name=not toCamelCase,
        )
    )
