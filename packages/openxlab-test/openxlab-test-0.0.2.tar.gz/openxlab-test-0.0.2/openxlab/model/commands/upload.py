"""
upload model file|meta file|log file|readme file-cli
"""
from openxlab.types.command_type import *
from openxlab.model import upload


class Upload(BaseCommand):
    """upload"""

    def get_name(self) -> str:
        return "upload"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('-r', '--model-repo', required=True,
                            help='model repository address. format:username/repository.')
        parser.add_argument('-ft', '--file-type', type=str, default='metafile', required=False,
                            help='upload file type, metafile/other.')
        parser.add_argument('-s', '--source', type=str, required=True,
                            help='metafile address or file address.')
        parser.add_argument('-t', '--target', type=str, required=False,
                            help='remote file address, only used when file type is other.')

    def take_action(self, parsed_args: Namespace) -> int:
        upload(parsed_args.model_repo, parsed_args.file_type, parsed_args.source, parsed_args.target)
        return 0
