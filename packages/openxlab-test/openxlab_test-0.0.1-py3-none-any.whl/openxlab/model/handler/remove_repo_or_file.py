"""
remove repository
"""
import re

from openxlab.model.clients.openapi_client import OpenapiClient
from openxlab.model.common.constants import endpoint, token


def remove(model_repo) -> None:
    """
    remove repository
    """
    try:
        # split params
        username, repository = _split_repo(model_repo)
        client = OpenapiClient(endpoint, token)
        client.remove_repository(repository)
        print(f"repository:{repository} removed successfully.")
    except ValueError as e:
        print(f"Error: {e}")
        return


def _split_repo(model_repo) -> (str, str):
    """
    Split a full repository name into two separate strings: the username and the repository name.
    """
    # username/repository format check
    pattern = r'^[a-zA-Z0-9]+\/[a-zA-Z0-9\-_]+$'
    if not re.match(pattern, model_repo):
        raise ValueError("The input string must be in the format 'didi12/test-d-1'")

    values = model_repo.split('/')
    return values[0], values[1]


def _parse_check():

    pass
