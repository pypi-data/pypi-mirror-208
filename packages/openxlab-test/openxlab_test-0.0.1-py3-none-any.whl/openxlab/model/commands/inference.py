"""
model inference-cli
"""
from openxlab.types.command_type import *


class Inference(BaseCommand):
    """inference"""

    def get_name(self) -> str:
        return "inference"

    def add_arguments(self, parser: ArgumentParser) -> None:
        pass

    def take_action(self, parsed_args: Namespace) -> int:
        print("model inference")
        return 0
