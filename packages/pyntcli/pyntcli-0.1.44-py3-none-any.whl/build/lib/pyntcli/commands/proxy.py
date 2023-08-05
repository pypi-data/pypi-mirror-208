import argparse
from copy import deepcopy
import os
import webbrowser
from http import HTTPStatus
import requests
import time
import tempfile
from subprocess import Popen, PIPE
from functools import partial

from pyntcli.store.store import CredStore
from pyntcli.pynt_docker import pynt_container
from pyntcli.ui import ui_thread
from pyntcli.commands import util, sub_command
from pyntcli.ui import report as cli_reporter


def proxy_usage():
    return ui_thread.PrinterText("Command integration to Pynt. Run a security scan with a given command.") \
        .with_line("") \
        .with_line("Usage:",style=ui_thread.PrinterText.HEADER) \
        .with_line("\tpynt command [OPTIONS]") \
        .with_line("") \
        .with_line("Options:",style=ui_thread.PrinterText.HEADER) \
        .with_line("\t--cmd - The command that runs the functional tests") \
        .with_line("\t--port - Set the port pynt will listen to (DEFAULT: 5001)") \
        .with_line("\t--allow-errors - If present will allow command to fail and continue execution") \
        .with_line("\t--ca-path - The path to the CA file in PEM format") \
        .with_line("\t--proxy-port - Set the port proxied traffic should be routed to (DEFAULT: 6666)") \
        .with_line("\t--report - If present will save the generated report in this path.") \
        .with_line("\t--insecure - use when target uses self signed certificates")


class ProxyCommand(sub_command.PyntSubCommand): 
    def __init__(self, name) -> None:
        super().__init__(name)
        self.scan_id = ""
        self.proxy_sleep_interval = 2
        self.proxy_healthcheck_buffer = 10
        self.proxy_server_base_url = "http://localhost:{}/api"
    
    def print_usage(self, *args):
        ui_thread.print(proxy_usage())

    def add_cmd(self, parent: argparse._SubParsersAction) -> argparse.ArgumentParser:
        proxy_cmd = parent.add_parser(self.name)
        proxy_cmd.add_argument("--port", "-p", help="", type=int, default=5001)
        proxy_cmd.add_argument("--proxy-port", help="", type=int, default=6666) 
        proxy_cmd.add_argument("--cmd", help="", default="", required=True)
        proxy_cmd.add_argument("--allow-errors", action="store_true")
        proxy_cmd.add_argument("--ca-path", type=str, default="")
        proxy_cmd.add_argument("--report", type=str, default="")
        proxy_cmd.print_usage = self.print_usage
        proxy_cmd.print_help = self.print_usage
        return proxy_cmd
    
    def _updated_environment(self, args):
        env_copy = deepcopy(os.environ)
        return env_copy.update({"HTTP_PROXY": "http://localhost:{}".format(args.proxy_port), 
                                "HTTPS_PROXY": "http://localhost:{}".format(args.proxy_port)})
    
    def _start_proxy(self, args):
        res = requests.put(self.proxy_server_base_url.format(args.port) + "/proxy/start")
        res.raise_for_status()
        self.scan_id = res.json()["scanId"]
    
    def _stop_proxy(self, args):
        start = time.time()
        while start + self.proxy_healthcheck_buffer > time.time(): 
            res = requests.put(self.proxy_server_base_url.format(args.port) + "/proxy/stop", json={"scanId": self.scan_id})
            if res.status_code == HTTPStatus.OK: 
                return 
            time.sleep(self.proxy_sleep_interval)
        raise TimeoutError()
        
    def _get_report(self, args,report_format):
        while True: 
            res = requests.get(self.proxy_server_base_url.format(args.port) + "/report?format={}".format(report_format), params={"scanId": self.scan_id})
            if res.status_code == HTTPStatus.OK:
                return res.text
            if res.status_code == HTTPStatus.ACCEPTED:
                time.sleep(self.proxy_sleep_interval)
                continue
            if res.status_code == 517: #pynt did not recieve any requests 
                ui_thread.print(ui_thread.PrinterText(res.json()["message"], ui_thread.PrinterText.WARNING))
                return 
            ui_thread.print("Error in polling for scan report: {}".format(res.text))
            return 

    
    def run_cmd(self, args: argparse.Namespace):
        docker_type, docker_arguments = pynt_container.get_container_with_arguments(pynt_container.PyntDockerPort(args.port, args.port, "--port"), 
                                                                                    pynt_container.PyntDockerPort(args.proxy_port, args.proxy_port, "--proxy-port"))
        
        if "insecure" in args and args.insecure:
            docker_arguments.append("--insecure")

        if "dev_flags" in args:
            docker_arguments += args.dev_flags.split(" ")
        
        mounts = []
        if "ca_path" in args and args.ca_path:
            if not os.path.isfile(args.ca_path):
                ui_thread.print(ui_thread.PrinterText("Could not find the provided ca path, please provide with a valid path", ui_thread.PrinterText.WARNING))
                return

            ca_name = os.path.basename(args.ca_path)
            docker_arguments += ["--ca-path", ca_name]
            mounts.append(pynt_container.create_mount(os.path.abspath(args.ca_path), "/etc/pynt/{}".format(ca_name)))

        creds_path = CredStore().get_path()
        mounts.append(pynt_container.create_mount(creds_path, "/app/creds.json"))

        proxy_docker = pynt_container.PyntContainer(image_name=pynt_container.PYNT_DOCKER_IMAGE, 
                                    tag="proxy-latest", 
                                    mounts=mounts,
                                    detach=True, 
                                    args=docker_arguments)
        proxy_docker.run(docker_type)
        ui_thread.print_generator(proxy_docker.stdout)
        
        util.wait_for_healthcheck("http://localhost:{}".format(args.port))
        self._start_proxy(args) 

        user_process = Popen(args.cmd, shell=True, stdout=PIPE, stderr=PIPE, env=self._updated_environment(args))
        ui_thread.print_generator(user_process.stdout)
        ui_thread.print_generator(user_process.stderr)
        rc = user_process.wait()
        if rc != 0 and not args.allow_errors:
            proxy_docker.stop()
            ui_thread.print(ui_thread.PrinterText("Command finished with error return code {}, If you wish Pynt to run anyway, run with --allow-errors".format(rc)))
            return

        self._stop_proxy(args)
        
        with ui_thread.progress("ws://localhost:{}/progress?scanId={}".format(args.port, self.scan_id),partial(lambda *args: None), "scan in progress...", 100):
            html_report = self._get_report(args,"html")
            html_report_path = os.path.join(tempfile.gettempdir(), "pynt_report_{}.html".format(int(time.time())))

            json_report = self._get_report(args,"json")   
            json_report_path = os.path.join(tempfile.gettempdir(), "pynt_report_{}.json".format(int(time.time())))

            if "report" in args and args.report:
                html_report_path = util.get_user_report_path(args.report,"html")
                json_report_path = util.get_user_report_path(args.report,"json")

            if html_report:
                with open(html_report_path, "w") as html_file:
                    html_file.write(html_report)
                webbrowser.open("file://{}".format(html_report_path))

            if json_report:
                with open(json_report_path, "w") as json_file:
                    json_file.write(json_report)
                cli_reporter.PyntReporter(json_report_path).print_summary()


