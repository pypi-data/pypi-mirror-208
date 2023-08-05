import requests
import time
import socket
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
import webbrowser

from pyntcli.pynt_docker import pynt_container
from pyntcli.store import CredStore
from pyntcli.ui import report
from pyntcli.ui import ui_thread


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_open_port() -> int:
    with socket.socket() as s:
        s.bind(('', 0))            
        return s.getsockname()[1] 

HEALTHCHECK_TIMEOUT = 10
HEALTHCHECK_INTERVAL = 0.1

def wait_for_healthcheck(address): 
    start = time.time()
    while start + HEALTHCHECK_TIMEOUT > time.time(): 
        try:
            res = requests.get(address + "/healthcheck")
            if res.status_code == 418:
                return 
        except: 
            time.sleep(HEALTHCHECK_INTERVAL)
    raise TimeoutError()

def get_user_report_path(path,file_type):
    path = Path(path)
    if path.is_dir():
        return os.path.join(path, "pynt_results_{}.{}".format(int(time.time()),file_type))
    
    return os.path.join(str(path.parent), path.stem + ".{}".format(file_type))
    
@contextmanager
def create_default_file_mounts(args):
    html_report_path = os.path.join(tempfile.gettempdir(), "results.html")
    json_report_path = os.path.join(tempfile.gettempdir(), "results.json")

    if "reporters" in args and args.reporters: 
        html_report_path = os.path.join(os.getcwd(), "pynt_results.html")
        json_report_path = os.path.join(os.getcwd(), "pynt_results.json")

    mounts = []
    with open(html_report_path, "w"), open(json_report_path, "w"):    
        mounts.append(pynt_container.create_mount(json_report_path, "/etc/pynt/results/results.json"))
        mounts.append(pynt_container.create_mount(html_report_path, "/etc/pynt/results/results.html"))
    
    mounts.append(pynt_container.create_mount(CredStore().get_path(), "/app/creds.json"))

    yield mounts
    
    if os.stat(html_report_path).st_size == 0:
        ui_thread.print(ui_thread.PrinterText("An Unexpected Error Occurred",style=ui_thread.PrinterText.WARNING) \
                        .with_line("") \
                            .with_line("Please tell us about it in our community channel and we will help you figure it out:",style=ui_thread.PrinterText.HEADER) \
                                .with_line("https://join.slack.com/t/pynt-community/shared_invite/zt-1mvacojz5-WNjbH4HN8iksmKpCLTxOiQ",style=ui_thread.PrinterText.HEADER))
        return 
    
    webbrowser.open("file://{}".format(html_report_path))

    if os.stat(html_report_path).st_size > 0:
        report.PyntReporter(json_report_path).print_summary()   