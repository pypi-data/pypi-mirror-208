import requests
import urllib3
import os
import pem
import certifi
import tempfile



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

    cert_data = open(ca_path, "rb").read()
    
    cafile = certifi.where()
    ca_chain = open(cafile, 'rb').read()
    
    bundle_path = os.path.join(tempfile.gettempdir(), "bundle.pem")
    with open(bundle_path,"wb") as f:
        f.write(ca_chain)
        f.write(b'\n')
        f.write(cert_data)
    
    verify = bundle_path

    
def get(url, params=None, **kwargs):
    return requests.get(url,params=params,verify=verify,**kwargs)

def post(url, data=None, json=None, **kwargs):
    return requests.post(url,data=data,json=json, verify=verify,**kwargs)

def put(url, data=None, **kwargs):
    return requests.put(url,data=data,verify=verify,**kwargs)