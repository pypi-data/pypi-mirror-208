"""
get model list of repository-cli
"""
from openxlab.types.command_type import *
from openxlab.model import list


class List(BaseCommand):
    """list"""

    def get_name(self) -> str:
        return "list"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('-r', '--model-repo', required=True,
                            help='model repository address. format:username/repository.')
        parser.add_argument('-i', '--metafile', type=bool, required=False,
                            help='get meta data.')

    def take_action(self, parsed_args: Namespace) -> int:
        list(parsed_args.model_repo, parsed_args.metafile)
        return 0
