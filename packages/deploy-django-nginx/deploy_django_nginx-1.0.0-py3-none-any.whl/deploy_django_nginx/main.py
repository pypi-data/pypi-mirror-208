#!/usr/bin/env python
import getpass
from pathlib import Path

import click


from deploy_django_nginx import config, util, version_info


CONTEXT_SETTINGS = dict(help_option_names=['-?', '-h', '--help'])

__epilog__ = click.style('''

\b
example:
    deploy_django_nginx \\
        -b /path/to/api/ \\
        -f /path/to/app/dist/ \\
        -n proj \\
        -p 1080 \\
        -d ./deploy

contact: {author} <{author_email}>
''', fg='cyan').format(**version_info)


@click.command(
    help=click.style(version_info['desc'], fg='green', bold=True),
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
    epilog=__epilog__,
)
@click.option('-f', '--front-end', help='the dist directory of front-end', required=True)
@click.option('-b', '--back-end', help='the directory of back-end', required=True)
@click.option('-n', '--name', help='the name of django project', required=True)
@click.option('-d', '--directory', help='the directory to deploy', default='./deploy', show_default=True)
@click.option('-p', '--port', help='the port number', default=1080, show_default=True)
@click.option('-y', '--force', help='force overwrite directory', is_flag=True)
def cli(**kwargs):

    api_name = kwargs['name']
    proj_dir = Path(kwargs['directory']).resolve()

    if proj_dir.exists():

        if proj_dir.owner() != getpass.getuser():
            click.secho(f'[{proj_dir}]The project path already exists. Please check or replace the project name!', fg='red')
            exit(1)

        if not (kwargs['force'] or click.confirm('The project path already exists. Do you want to overwrite it')):
            exit(1)

    api_root = proj_dir.joinpath('api')
    app_root = proj_dir.joinpath('app')

    front_end_dir = Path(kwargs['front_end'])
    back_end_dir = Path(kwargs['back_end'])

    port = util.check_port(kwargs['port'])

    util.run_cmd(f'mkdir -p {proj_dir}/{{logs,config}}')
    util.run_cmd(f'rsync -luvr --exclude nohup.out {front_end_dir}/* {app_root}')
    util.run_cmd(f'rsync -luvr --exclude nohup.out {back_end_dir}/* {api_root}')

    # util.run_cmd(f'rsync -luvr --exclude nohup.out {back_end_dir}/{{data,db.sqlite3}} {api_root}')
    # build.build_cython(back_end_dir, build=f'{api_root}/build')

    util.write_file(
        proj_dir.joinpath('config', 'nginx.conf'),
        config.nginx.format(PROJ_DIR=proj_dir, PORT=port, API_ROOT=api_root, APP_ROOT=app_root),
    )

    util.write_file(
        proj_dir.joinpath('config', 'uwsgi.ini'),
        config.uwsgi.format(PROJ_DIR=proj_dir, API_ROOT=api_root, API_NAME=api_name),
    )

    util.write_file(
        proj_dir.joinpath('start.sh'),
        config.start_shell.format(PROJ_DIR=proj_dir),
    )

    util.write_file(
        proj_dir.joinpath('stop.sh'),
        config.stop_shell.format(PROJ_DIR=proj_dir),
    )

    util.write_file(
        proj_dir.joinpath('URL'),
        f'Intranet: http://{util.get_intranet_ip()}:{port}\nInternet: http://{util.get_internet_ip()}:{port}',
    )

    click.secho(f'''
        Project Path: \t{proj_dir}
        Start Service: \tsh {proj_dir.joinpath('start.sh')}
    ''', fg='cyan')


def main():
    cli()


if __name__ == '__main__':
    main()
