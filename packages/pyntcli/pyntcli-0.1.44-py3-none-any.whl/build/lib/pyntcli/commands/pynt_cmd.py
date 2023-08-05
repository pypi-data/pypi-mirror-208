import argparse
from typing import Dict, List

from . import postman, root, sub_command, id_command, proxy , newman, har

avail_sub_commands = [
    postman.PostmanSubCommand("postman"),
    id_command.PyntShowIdCommand("pynt-id"),
    newman.NewmanSubCommand("newman"),
    har.HarSubCommand("har"),
    proxy.ProxyCommand("command"),
]

class PyntCommandException(Exception):
    pass

class BadArgumentsException(PyntCommandException):
    pass

class NoSuchCommandException(PyntCommandException):
    pass


class PyntCommand: 
    def __init__(self) -> None:
        self.base: root.BaseCommand = root.BaseCommand()
        self.sub_commands: Dict[str, sub_command.PyntSubCommand] = {sc.get_name(): sc for sc in avail_sub_commands}
        self._start_command()

    def _start_command(self):
        self.base.cmd()
        for sc in self.sub_commands.values():
            self.base.add_base_arguments(sc.add_cmd(self.base.get_subparser()))

    def parse_args(self, args_from_cmd: List[str]): 
        return self.base.cmd().parse_args(args_from_cmd)

    def run_cmd(self, args: argparse.Namespace):
        if not "command" in args:
            raise BadArgumentsException()
        
        command = getattr(args, "command") 
        if not command in self.sub_commands:
            raise NoSuchCommandException()
    
        self.base.run_cmd(args)
        self.sub_commands[command].run_cmd(args)
