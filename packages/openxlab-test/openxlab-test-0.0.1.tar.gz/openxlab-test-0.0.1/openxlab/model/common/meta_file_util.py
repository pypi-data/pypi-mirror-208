import yaml
import re


class MetafileParser:
    def __init__(self, filename):
        self.filename = filename
        self.metafile = None

    def parse(self):
        with open(self.filename, 'r') as f:
            self.metafile = yaml.safe_load(f)
        return self.metafile

    def validate(self):
        if not self.metafile.get('Collections'):
            raise ValueError("Error: Collections field is missing or empty.")
        if not self.metafile.get('Models'):
            raise ValueError("Error: Models field is missing or empty.")
        # Add more validation rules as needed

    def parse_and_validate(self) -> dict:
        self.parse()
        self.validate()
        print(f"parse metafile data:{self.metafile}")
        return self.metafile


def get_filename_from_url(url):
    pattern = r"/([^/]+)$"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Can't get weight name")


def get_meta_payload(repository, private, meta_data):
    _name = repository
    _nickname = repository
    _collection = meta_data['Collections'][0]
    _license = _collection['License']
    _github = _collection['Code']['URL']
    _public_status = 0 if private else 1
    _models = [{"name": m['Name'], "weightName": get_filename_from_url(m['Weights']),
                "evaluations": [{"task": e['Task'], "dataset": e['Dataset']} for e in m['Results']]} for m in
               meta_data['Models']]

    payload = {"name": _name, "nickname": _nickname, "license": _license,
               "github": _github, "publicStatus": _public_status, "models": _models}

    print(f"convert to payload:{payload}")
    return payload
