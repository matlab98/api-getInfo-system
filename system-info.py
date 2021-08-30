from flask import Flask, request, jsonify
import psutil
import platform
from datetime import datetime
import json
import os
import configparser
import ast

config = configparser.ConfigParser()
config.read('configuration.properties')

def convert(variable, conf):
    return ast.literal_eval((config.get(os.environ[variable], conf)))

app = Flask(__name__)
app.config['DEBUG'] = convert('APP_SETTINGS', "DEBUG") 
app.config['TESTING'] = convert('APP_SETTINGS', "TESTING")
print(app.config)
info = {}
info['data'] = []

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def network():
    if_addrs = psutil.net_if_addrs()
    net_io = psutil.net_io_counters()
    network = {}
    network['networks'] = []
    network['network'] = []
    for interface_name, interface_addresses in if_addrs.items():
        family = ""
        ip = ""
        net = ""
        broadcast = ""

        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                family = str(address.family)
                ip = str(address.address)
                net = str(address.netmask)
                broadcast = str(address.broadcast)
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                family = str(address.family)
                ip = str(address.address)
                net = str(address.netmask)
                broadcast = str(address.broadcast)

        network['networks'].append({
            'name': str(interface_name),
            'family': family,
            'IP': ip,
            'Netmask': net,
            'Broadcast': broadcast
        })

    network['network'].append({
        "sentBytes": str(get_size(net_io.bytes_sent)),
        "ReceivedBytes": str(get_size(net_io.bytes_recv))
    })
    info['data'].append(network)

def disk():
    partitions = psutil.disk_partitions(all=False)
    disk = {}
    disk['disks'] = []
    for partition in partitions:
        try:
           partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        if partition.fstype == "NTFS" or partition.fstype == "apfs":
            disk['disks'].append({
                'device': str(partition.device),
                'mountpoint': str(partition.mountpoint),
                'systemtype': str(partition.fstype),
                'totalSize': str(get_size(partition_usage.total)),
                'used': str(get_size(partition_usage.used)),
                'free': str(get_size(partition_usage.free)),
                'percentage': f"{partition_usage.percent} %"
            })
    info['data'].append(disk)

def memory():
    memory = {}
    memory['memory'] = []
    svmem=psutil.virtual_memory()
    memory['memory'].append({
        'total': str(get_size(svmem.total)),
        'available': str(get_size(svmem.available)),
        'used': str(get_size(svmem.used)),
        'percentage': f"{svmem.percent} %"
    })
    info['data'].append(memory)

def system():
    system = {}
    system['system'] = []
    uname=platform.uname()
    system['system'].append({
        'system': str(uname.system),
        'nodeName': str(uname.node),
        'release': str(uname.release),
        'version': str(uname.version),
        'machine': str(uname.machine),
        'processor': str(uname.processor)
    })
    info['data'].append(system)

def cpu():
    cpu = {}
    cpu['cpu'] = []
    cpu['cores'] = []
    cpufreq=psutil.cpu_freq()

    cpu['cpu'].append({
        'processor':{
        'cores': str(psutil.cpu_count(logical=False)),
        'totalCores': str(psutil.cpu_count(logical=True)),
        'maxFreq': f"{cpufreq.max:.2f} Mhz",
        'minFreq': f"{cpufreq.min:.2f} Mhz",
        'currentFreq': f"{cpufreq.current:.2f} Mhz"
    }})

    for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
        cpu['cores'].append({
            'core': i+1,
            'percentage': f"{percentage} %"
        })
    cpu['cpu'].append({
        'all':{
        'usage': f"{psutil.cpu_percent()} %"
    }})
    info['data'].append(cpu)

network()
disk()
memory()
system()
cpu()

@app.route('/api/v1/resources/info/all', methods=['GET'])
def api_all():
    return jsonify(info)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="666")