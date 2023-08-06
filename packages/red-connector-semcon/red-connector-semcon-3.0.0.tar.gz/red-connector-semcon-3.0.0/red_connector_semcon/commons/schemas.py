from copy import deepcopy


_HTTP_METHODS = ['Get', 'Put', 'Post']
_HTTP_METHODS_ENUMS = deepcopy(_HTTP_METHODS) + [m.lower() for m in _HTTP_METHODS] + [m.upper() for m in _HTTP_METHODS]

_RESOURCE_TYPE_ENUMS = ['id', 'dri', 'schema_dri', 'table']
_OUTPUT_FORMAT_ENUMS = ['plain', 'full', 'meta', 'validation']

_BASE_SCHEMA = {
    'type': 'object',
    'properties': {
        'url': {'type': 'string'},
        'method': {'enum': _HTTP_METHODS_ENUMS},
        'auth': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string'},
                'password': {'type': 'string'},
                'scope': {'type': 'string'}
            },
            'additionalProperties': False,
            'required': ['username', 'password']
        },
        'disableSSLVerification': {'type': 'boolean'}
    },
    'additionalProperties': False,
    'required': ['url']
}

RECEIVE_FILE_SCHEMA = deepcopy(_BASE_SCHEMA)
RECEIVE_FILE_SCHEMA['properties']['resource'] = {
    'type': 'object',
    'properties': {
        'resourceType': {'enum': _RESOURCE_TYPE_ENUMS},
        'resourceValue': {'type': 'string'},
        'key': {'type': 'string'},
        'format': {'enum': _OUTPUT_FORMAT_ENUMS}
    },
    'additionalProperties': False,
    'required': ['resourceType', 'resourceValue']
}

SEND_FILE_SCHEMA = deepcopy(_BASE_SCHEMA)
SEND_FILE_SCHEMA['properties']['resource'] = {
    'type': 'object',
    'properties': {
        'dri': {'type': 'string'},
        'schemaDri': {'type': 'string'},
        'tableName': {'type': 'string'},
        'key': {'type': 'string'}
    },
    'additionalProperties': False
}
