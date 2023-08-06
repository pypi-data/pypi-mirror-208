"""
remove repository
"""
from openxlab.types.command_type import *
from openxlab.model import remove


class Remove(BaseCommand):
    """remove"""

    def get_name(self) -> str:
        return "remove"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('-r', '--model-repo', required=True,
                            help='model repository address. format:username/repository.')

    def take_action(self, parsed_args: Namespace) -> int:
        remove(parsed_args.model_repo)
        return 0
