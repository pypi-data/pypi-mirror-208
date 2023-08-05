import argparse
import time
import os
from functools import partial

from pyntcli.pynt_docker import pynt_container
from pyntcli.commands import sub_command, util
from pyntcli.ui import ui_thread
from pyntcli.ui.progress import PyntProgress

def newman_usage():
    return ui_thread.PrinterText("Integration with newman, run scan using postman collection from the CLI") \
            .with_line("") \
            .with_line("Usage:", style=ui_thread.PrinterText.HEADER) \
            .with_line("\tpynt newman [OPTIONS]") \
            .with_line("") \
            .with_line("Options:", style=ui_thread.PrinterText.HEADER) \
            .with_line("\t--collection - Postman collection file name") \
            .with_line("\t--environment - Postman environment file name") \
            .with_line("\t--reporters output results to json")

class NewmanSubCommand(sub_command.PyntSubCommand):
    def __init__(self, name) -> None:
        super().__init__(name)

    def usage(self, *args): 
        ui_thread.print(newman_usage())

    def add_cmd(self, parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
        newman_cmd = parent.add_parser(self.name)
        newman_cmd.add_argument("--collection", type=str, required=True) 
        newman_cmd.add_argument("--environment", type=str, required=False) 
        newman_cmd.add_argument("--reporters", action="store_true",default=False,  required=False) 
        newman_cmd.print_usage = self.usage
        newman_cmd.print_help = self.usage
        return newman_cmd

    def run_cmd(self, args: argparse.Namespace):
        port = str(util.find_open_port())
        docker_type , docker_arguments = pynt_container.get_container_with_arguments(pynt_container.PyntDockerPort(src=port, dest=port, name="--port"))
        mounts = []

        if not os.path.isfile(args.collection): 
            ui_thread.print(ui_thread.PrinterText("Could not find the provided collection path, please provide with a valid collection path", ui_thread.PrinterText.WARNING))
            return
        
        collection_name = os.path.basename(args.collection)
        docker_arguments += ["-c", collection_name]
        mounts.append(pynt_container.create_mount(os.path.abspath(args.collection), "/etc/pynt/{}".format(collection_name)))
         
        if "environment" in args and args.environment:
            if not os.path.isfile(args.environment):
                ui_thread.print(ui_thread.PrinterText("Could not find the provided environment path, please provide with a valid environment path", ui_thread.PrinterText.WARNING))
                return
            
            env_name = os.path.basename(args.environment)
            docker_arguments += ["-e", env_name]
            mounts.append(pynt_container.create_mount(os.path.abspath(args.environment), "/etc/pynt/{}".format(env_name)))

               
        with util.create_default_file_mounts(args) as m:

            mounts += m
        
            if "insecure" in args and args.insecure:
                docker_arguments.append("--insecure")
            
            if "dev_flags" in args: 
                docker_arguments += args.dev_flags.split(" ")
            
            newman_docker = pynt_container.PyntContainer(image_name=pynt_container.PYNT_DOCKER_IMAGE,
                                                     tag="latest",
                                                     detach=True,
                                                     mounts=mounts,
                                                     args=docker_arguments)

            newman_docker.run(docker_type)
            
            healthcheck = partial(util.wait_for_healthcheck, "http://localhost:{}".format(port))
            ui_thread.print_generator(ui_thread.AnsiText.wrap_gen(newman_docker.stdout))
            
            with ui_thread.progress("ws://localhost:{}/progress".format(port),healthcheck,  "scan in progress...",100):
                while newman_docker.is_alive():
                    time.sleep(1)
