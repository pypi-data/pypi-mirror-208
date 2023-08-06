"""
create model repository-cli
"""
from openxlab.types.command_type import *
from openxlab.model import create


class Create(BaseCommand):
    """create"""

    def get_name(self) -> str:
        return "create"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('-r', '--model-repo', required=True,
                            help='model repository address. format:username/repository.')
        parser.add_argument('-prt', '--private', type=bool, default=False,
                            help='set repository visibility.')

    def take_action(self, parsed_args: Namespace) -> int:
        create(parsed_args.model_repo, parsed_args.private)
        return 0
