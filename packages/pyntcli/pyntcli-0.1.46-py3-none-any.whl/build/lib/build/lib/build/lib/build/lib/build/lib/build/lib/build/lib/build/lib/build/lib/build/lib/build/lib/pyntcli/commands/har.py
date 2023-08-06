import argparse
import time
import os
from functools import partial

from pyntcli.pynt_docker import pynt_container
from pyntcli.ui import ui_thread
from pyntcli.ui.progress import PyntProgress
from pyntcli.commands import sub_command, util



def har_usage():
    return ui_thread.PrinterText("Integration with static har file testing") \
            .with_line("") \
            .with_line("Usage:", style=ui_thread.PrinterText.HEADER) \
            .with_line("\tpynt har [OPTIONS]") \
            .with_line("") \
            .with_line("Options:", style=ui_thread.PrinterText.HEADER) \
            .with_line("\t--har - Path to har file") \
            .with_line("\t--reporters output results to json") \
            .with_line("\t--host-ca - path to the CA file in PEM format to enable SSL certificate verification for pynt when running through a VPN.")

class HarSubCommand(sub_command.PyntSubCommand):
    def __init__(self, name) -> None:
        super().__init__(name)

    def usage(self, *args):
        ui_thread.print(har_usage())

    def add_cmd(self, parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
        har_cmd = parent.add_parser(self.name)
        har_cmd.add_argument("--har", type=str, required=True)
        har_cmd.add_argument("--reporters", action='store_true')
        har_cmd.print_usage = self.usage
        har_cmd.print_help = self.usage
        return har_cmd
    
    def run_cmd(self, args: argparse.Namespace):
        port = str(util.find_open_port())
        container = pynt_container.get_container_with_arguments(args, pynt_container.PyntDockerPort(src=port, dest=port, name="--port"))

        if not os.path.isfile(args.har): 
            ui_thread.print(ui_thread.PrinterText("Could not find the provided har path, please provide with a valid har path", ui_thread.PrinterText.WARNING))
            return

        har_name = os.path.basename(args.har)
        container.docker_arguments += ["--har", har_name]
        container.mounts.append(pynt_container.create_mount(os.path.abspath(args.har), "/etc/pynt/{}".format(har_name)))

        with util.create_default_file_mounts(args) as m:

            container.mounts += m
            
            har_docker = pynt_container.PyntContainer(image_name=pynt_container.PYNT_DOCKER_IMAGE,
                                                     tag="har-latest",
                                                     detach=True,
                                                     base_container=container)

            har_docker.run()

            healthcheck = partial(util.wait_for_healthcheck, "http://localhost:{}".format(port))
            ui_thread.print_generator(ui_thread.AnsiText.wrap_gen(har_docker.stdout))
        
            with ui_thread.progress("ws://localhost:{}/progress".format(port),healthcheck,  "scan in progress...",100):
                while har_docker.is_alive():
                    time.sleep(1)