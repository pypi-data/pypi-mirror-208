"""
download model file|meta file|log file|readme file-cli
"""
from openxlab.types.command_type import *
from openxlab.model import download


class Download(BaseCommand):
    """download"""

    def get_name(self) -> str:
        return "download"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('-r', '--model-repo', required=True,
                            help='model repository address. format:username/repository.')
        parser.add_argument('-f', '--file', required=True,
                            help='target file to be download.')
        parser.add_argument('-p', '--path', required=False,
                            help='setting download path.')
        parser.add_argument('-o', '--overwrite', action='store_true',
                            help='force overwriting local files.')

    def take_action(self, parsed_args: Namespace) -> int:
        download(parsed_args.model_repo, parsed_args.file, parsed_args.path, parsed_args.overwrite)
        return 0
