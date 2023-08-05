import requests
import urllib3
import os
import pem


class HostCaException(Exception):
    pass

class InvalidPathException(HostCaException):
    pass

class InvalidCertFormat(HostCaException):
    pass

verify = True

def disable_tls_termination():
    global verify
    verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def add_host_ca(ca_path):
    global verify
    if not os.path.isfile(ca_path):
        raise InvalidPathException("{} - No such file".format(ca_path))
    if not pem.parse_file(ca_path):
        raise InvalidCertFormat("{} - Invalid Format".format(ca_path))

    verify = ca_path
        
def get(url, params=None, **kwargs):
    return requests.get(url,params=params,verify=verify,**kwargs)

def post(url, data=None, json=None, **kwargs):
    return requests.post(url,data=data,json=json, verify=verify,**kwargs)

def put(url, data=None, **kwargs):
    return requests.put(url,data=data,verify=verify,**kwargs)