from ipaddress import *
import socket
from socket import *
from typing import Tuple, Any

import requests


IPINFO = "https://ipinfo.io/{ip}?token=030d073439a554"
SHODAN = "https://api.shodan.io/shodan/host/{ip}?key=O2wmufm88UYx2k6bvc4Ty6bHr6DMhRZp"

MECHANISM_ERROR = {'OK': 0, 'waf': 0, 'moved': 0, "error": 0, "net_rest": 0, "captcha": 0, 'ssl': 0}
HTTP_ERROR = {0x1: "Critical error: maybe need domain to fuzzing or headers invalid!, "
                   "click on `setting` to edit headers"
                   "\nserver return 301",
              0x2: "Critical error: server return 403, \nmaybe you denied!",
              0x3: "Critical error: server return 503/500\nmaybe server crashed or Unavailable!",
              0x4: "Critical error: server close all sockets with your address,"
                   "\nmaybe your AV close this socket or remote address, or url invalid!",
              0x5: "error!:, server moved you to captcha?, can't fuzzing!\nset cookies to bypass captcha!"}


def clsAddress(url: str, proto=False):
    port = None
    protocol = "https://" if ("https" in url or proto) else "http://"
    indexes = "/"
    if "//" in url:
        url = url[url.find("://")+3:]
        if "/" in url:
            url, indexes = url.split("/")[0],  "/"+"/".join(url.split("/")[1::])
    if ":" in url:
        try:
            url, port = url.split(":")
        except ValueError:
            pass
    # fuck it
    return url, port or 443 or 80, protocol, indexes or "/"


def domainExist(url: str) -> bool | tuple[int, Any | None, str, str | Any, str, str]:
    sock = socket()
    sock.settimeout(1)
    try:
        dns_name, port, protocol, indexes = clsAddress(url)
        ip = gethostbyname(dns_name)
    except OSError:
        # /* failed */
        return False
    except UnicodeError:
        # /* invalid ip */
        return False
    # /* success */
    return not sock.connect_ex((ip, int(port))), port, ip, dns_name, protocol, indexes


def ipIsValid(ip):
    try:
        IPv4Address(ip)
    except AddressValueError:
        return False

    return True


def get_IpInfo(ip: str) -> dict:
    """

    :param ip: address of remote channel
    :return:
    """
    if ipIsValid(ip):
        try:
            req = requests.get(IPINFO.format(ip=ip))
            res: dict = req.json()
        except Exception as err:
            return 0
        if "status" in res.keys():
            return 0

        return res

    return 0


def get_Shodan(ip: str):
    if ipIsValid(ip):
        try:
            req = requests.get(SHODAN.format(ip=ip))
            res: dict = req.json()
        except Exception as err:
            return 0

        # /* errors? */
        if res.keys().__len__() == 1:return res

        del res['data']
        del res['longitude']
        del res['latitude']

        return res

    return 0

