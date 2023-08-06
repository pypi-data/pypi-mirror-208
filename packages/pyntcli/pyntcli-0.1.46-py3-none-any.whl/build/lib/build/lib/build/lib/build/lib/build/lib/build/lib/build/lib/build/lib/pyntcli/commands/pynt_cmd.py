import argparse
from typing import Dict, List
from pyntcli import __version__ as cli_version
from pyntcli.analytics import send as analytics
from pyntcli.transport import pynt_requests
from pyntcli.ui import ui_thread
from distutils.version import StrictVersion

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


VERSION_CHECK_URL = "https://d1efigcr4c19qn.cloudfront.net/cli/version"

def check_is_latest_version(current_version):
    res = pynt_requests.get(VERSION_CHECK_URL) 
    res.raise_for_status()

    latest_versions = res.text.replace("\n","")

    if current_version != latest_versions:
        ui_thread.print(ui_thread.PrinterText("""Pynt CLI new version is available, upgrade now with:
python3 -m pip install --upgrade pyntcli""",ui_thread.PrinterText.WARNING))

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
        
        if "host_ca" in args and args.host_ca:
            pynt_requests.add_host_ca(args.host_ca)
            
        if "insecure" in args and args.insecure:
            pynt_requests.disable_tls_termination()

        check_is_latest_version(cli_version)
        analytics.emit(analytics.CLI_START)
    
        self.base.run_cmd(args)
        self.sub_commands[command].run_cmd(args)
