import socket
import subprocess as sp
from pathlib import Path

import click
from webrequests import WebRequest


def check_port(port):
    """
    Check if the specified port is occupied, if it is being used, then add 1
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        while True:
            if s.connect_ex(('localhost', port)) == 0:
                click.secho(f'port is alreay in use: {port}', fg='yellow')
                port += 1
            else:
                click.secho(f'port is available: {port}', fg='green')
                return port


def run_cmd(cmd):
    click.secho(f'>>> run cmd: {cmd}', fg='cyan')
    res = sp.run(cmd, shell=True, capture_output=True)
    if res.returncode != 0:
        raise Exception(f'ERR: {res.stderr}')
    return res.stdout


def write_file(file, content):
    with Path(file).open('w') as out:
        out.write(content.strip() + '\n')
    click.secho(f'>>> write file: {file}')


def get_intranet_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip


def get_internet_ip():
    soup = WebRequest.get_soup('http://cip.cc')
    ip = soup.select_one('.data pre').text.split('\n')[0].split()[-1]
    return ip
