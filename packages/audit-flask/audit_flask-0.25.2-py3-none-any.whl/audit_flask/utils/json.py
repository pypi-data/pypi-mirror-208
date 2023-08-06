import json


def is_serializable(object):
    try:
        json.dump(object)
        return True
    except Exception:
        return False


def serialize_field(value):
    if not is_serializable(value):
        return json.dumps(value, default=str)
    return value


def serializar_dict(dictionary:  dict) -> dict:
    if isinstance(dictionary, dict):
        dictionary_new = dictionary.copy()
        for key, value in dictionary_new.items():
            dictionary_new[key] = serialize_field(value)
        return dictionary_new
    return dictionary
