import argparse
import time 

from . import sub_command, util
from pyntcli.pynt_docker import pynt_container
from pyntcli.ui import ui_thread


def postman_usage():
    return ui_thread.PrinterText("Integration with postman, run scan from pynt postman collection") \
        .with_line("") \
        .with_line("Usage:",style=ui_thread.PrinterText.HEADER) \
        .with_line("\tpynt postman [OPTIONS]") \
        .with_line("") \
        .with_line("Options:",style=ui_thread.PrinterText.HEADER) \
        .with_line("\t--port - set the port pynt will listen to (DEFAULT: 5001)") \
        .with_line("\t--insecure - use when target uses self signed certificates") \
        .with_line("\t--host-ca - path to the CA file in PEM format to enable SSL certificate verification for pynt when running through a VPN.")

class PostmanSubCommand(sub_command.PyntSubCommand): 
    def __init__(self, name) -> None:
        super().__init__(name)

    def usage(self, *args):
        ui_thread.print(postman_usage())

    def add_cmd(self, parent_command: argparse._SubParsersAction) -> argparse.ArgumentParser: 
        postman_cmd = parent_command.add_parser(self.name)
        postman_cmd.add_argument("--port", "-p", help="set the port pynt will listen to (DEFAULT: 5001)", type=int, default=5001)
        postman_cmd.print_usage = self.usage
        postman_cmd.print_help = self.usage
        return postman_cmd

    def run_cmd(self, args: argparse.Namespace):
        container = pynt_container.get_container_with_arguments(args ,pynt_container.PyntDockerPort("5001", args.port, name="--port"))        
       
        if util.is_port_in_use(args.port):
            ui_thread.print(ui_thread.PrinterText("Port: {} already in use, please use a different one".format(args.port), ui_thread.PrinterText.WARNING))
            return 

        postman_docker = pynt_container.PyntContainer(image_name=pynt_container.PYNT_DOCKER_IMAGE, 
                                            tag="postman-latest", 
                                            detach=True, 
                                            base_container=container)

        postman_docker.run()
        ui_thread.print_generator(postman_docker.stdout) 
        
        while postman_docker.is_alive():
            time.sleep(1)
