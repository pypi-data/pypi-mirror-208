"""
model repository init-cli
"""
from openxlab.types.command_type import *
from openxlab.model import download_metafile_template


class Init(BaseCommand):
    """init"""

    def get_name(self) -> str:
        return "init"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('-p', '--path',
                            help='Specify the download path for the metafile.')

    def take_action(self, parsed_args: Namespace) -> int:
        download_metafile_template(parsed_args.path)
        return 0
