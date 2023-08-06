import os
import platform
import psutil
import re
import socket
import subprocess
import uuid

from typing import Optional
from ipaddress import ip_network, ip_address, IPv4Network

from ..file.ini import SensitiveConfigParser


def get_host_name():
    """查看当前主机名"""
    return socket.gethostname()


def get_host_ip():
    """根据主机名称获取当前IP"""
    return socket.gethostbyname(socket.gethostname())


def get_host_ips(only_ipv4: bool = True):
    """获取当前主机IPV4 和IPV6的所有IP地址(所有系统均通用)"""
    addrs = socket.getaddrinfo(get_host_name(), None)
    return [item[4][0] for item in addrs if ':' not in item[4][0]] if only_ipv4 is True else [item[4][0] for item in addrs]


def get_ip_by_net(ip: str):
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        if _ip is not None and net is not None:
            __ip = f"{_ip}/{net}"
            ip_start = ip_address(str(ip_network(__ip, False)).split('/')[0])
            ip_end = ip_network(__ip, False).broadcast_address
            for k, v in psutil.net_if_addrs().items():
                for item in v:
                    if item[0] == 2:
                        item_ip = item[1]
                        if ':' not in item_ip:
                            item_ip = ip_address(item_ip)
                            if ip_start <= item_ip < ip_end:
                                return f"{item_ip}" if port is None else f"{item_ip}:{port}"
    return ip


def check_ip(ip: str) -> bool:
    """检测是否IP"""
    p = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    return False


def get_mac_address() -> str:
    """获取MAC地址"""
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)]).upper()


def get_machine_macs() -> list:
    """获取多网卡Mac地址"""
    macs = []
    for adapter, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family.name in ['AF_LINK', 'AF_PACKET']:
                macs.append(snic.address.upper().replace('-', ':'))
    return macs


def get_machine_nets() -> dict:
    """获取本机网络"""
    nets = {}
    for adapter, snics in psutil.net_if_addrs().items():
        net = {}
        for snic in snics:
            if snic.family.name in ['AF_LINK', 'AF_PACKET']:
                net['mac'] = snic.address.upper().replace('-', ':')
            elif snic.family.name in ['AF_INET']:
                net['ip'] = snic.address
                net['mask'] = snic.netmask
        if len(net) > 0:
            nets[adapter] = net
    return nets


def get_broadcast_by_ip(ip: str):
    """获取广播地址"""
    broadcast = "255.255.255.255"
    for interface, data in psutil.net_if_addrs().items():
        for addr in data:
            if addr.family == 2:
                if addr.address == ip:
                    return IPv4Network(addr.address + '/' + addr.netmask, False).broadcast_address
    return broadcast


def get_networks(ip: str) -> list:
    """获取网段ip"""
    ips = []
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        __ip = f"{_ip}/{net}" if net is not None else f"{_ip}/24"
        ip_start = ip_address(str(ip_network(__ip, False)).split('/')[0])
        num_addresses = ip_network(__ip, False).num_addresses
        for i in range(num_addresses):
            ips.append(str(ip_address(ip_start) + i))
    return ips


def change_local_ip(ip: str) -> str:
    """更改本机地址"""
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        if _ip is not None and net is not None:
            ips = get_networks(ip)

            __ip = f"{_ip}/{net}"
            for k, v in psutil.net_if_addrs().items():
                for item in v:
                    if item[0] == 2:
                        item_ip = item[1]
                        if ':' not in item_ip:
                            item_ip = str(item_ip)
                            if item_ip in ips:
                                return f"{item_ip}:47808" if port is None else f"{item_ip}:{port}"
    return ip


def get_inuse_fun(ip: str, port: int, protocol: str = 'tcp'):

    def is_inuse_windows(_ip, _port, _protocol):
        results = os.popen(f'netstat -p {_protocol} -an | findstr "{_ip}:{_port}"').readlines()
        for result in results:
            if len(result) > 0 and result.find('LISTENING'):
                return True
        return False

    def is_inuse_linux(_ip, _port, _protocol):
        cmd = f'netstat -tl | grep ":{_port}"' if _protocol == 'tcp' else f'netstat -ul | grep ":{_port}"'
        results = os.popen(cmd).readlines()
        for result in results:
            if len(result) > 0 and result.find('LISTEN'):
                return True
        return False

    machine = platform.platform().lower()
    if 'windows-' in machine:
        return is_inuse_windows(ip, port, protocol)
    elif 'linux-' in machine:
        return is_inuse_linux(ip, port, protocol)
    else:
        raise Exception('Error, sorry, platform is unknown')


def check_ip_in_use(ip: str, protocol: str = 'tcp') -> bool:
    """检测端口是否占用"""
    m = re.compile(r"(\d+\.\d+\.\d+\.\d+)(?:/(\d+))?(?::(\d+))?").match(ip)
    if m:
        (_ip, net, port) = m.groups()
        if _ip is not None and port is not None:
            return get_inuse_fun(_ip, int(str(port)), protocol)
    return False


def decode_str(data: bytes, encoding='utf-8') -> str:
    try:
        return data.decode(encoding)
    except Exception:
        pass

    try:
        return data.decode('gb2312')
    except Exception:
        pass

    return data.decode(encoding, 'ignore')


def execute_command(command: str) -> str:
    out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    stdout, stderr = out.communicate()
    stdout, stderr = decode_str(stdout) if stdout else None, decode_str(stderr) if stderr else None
    if stderr or out.returncode != 0:
        raise Exception(f"execute cmd fail(stdout:\n{stdout}\nstderr:\n{stderr})")
    if stdout:
        return stdout.strip()


def ping(host: str, retry: int = 1, check_bool: bool = True):
    if check_bool is True:
        return subprocess.call(['ping', '-n' if platform.system().lower() == 'windows' else '-c', str(retry), host], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
    else:
        return execute_command(f"ping {str(host)} -n {str(retry)}" if platform.system().lower() == 'windows' else f"ping {str(host)} -c {str(retry)}")


def tcp_ping(host: str, port: int, timeout: int = 5) -> bool:
    """测试TCP连接"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(timeout)
        client.connect((host, port))
        return True
    except Exception as e:
        return False


def set_linux_network(host_conf: str, host: Optional[str] = None, gateway: Optional[str] = None):
    if platform.system().lower() == 'linux':
        if os.path.exists(host_conf):
            cfg = SensitiveConfigParser()
            cfg.read(host_conf)

            if isinstance(gateway, str):
                cfg.set('Network', 'Gateway', gateway)

            if isinstance(host, str):
                if str(host).lower() in ['yes', 'no', 'ipv4', 'ipv6']:
                    if cfg.has_option('Network', 'Address'):
                        cfg.remove_option('Network', 'Address')
                    if cfg.has_option('Network', 'Gateway'):
                        cfg.remove_option('Network', 'Gateway')
                    cfg.set('Network', 'DHCP', host)
                else:
                    if cfg.has_option('Network', 'DHCP'):
                        cfg.remove_option('Network', 'DHCP')
                    cfg.set('Network', 'Address', host)

            cfg.write(open(host_conf, 'w'))

            # restart
            os.system("systemctl restart systemd-networkd.service")  # restart
            return True
    return False
