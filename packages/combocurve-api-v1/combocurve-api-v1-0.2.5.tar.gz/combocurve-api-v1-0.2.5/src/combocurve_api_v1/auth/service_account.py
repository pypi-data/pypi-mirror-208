import json
from dataclasses import dataclass, fields


@dataclass
class ServiceAccount:
    client_email: str
    client_id: str
    private_key: str
    private_key_id: str

    @staticmethod
    def from_file(path: str) -> 'ServiceAccount':

        def filter_fields(d: dict):
            field_names = {f.name for f in fields(ServiceAccount)}
            return {k: d[k] for k in d if k in field_names}

        with open(path, 'r') as f:
            return json.load(f, object_hook=lambda d: ServiceAccount(**filter_fields(d)))
