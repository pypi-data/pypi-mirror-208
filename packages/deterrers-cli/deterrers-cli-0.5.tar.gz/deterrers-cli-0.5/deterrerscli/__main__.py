import click
import deterrersapi
import json
import pathlib
import yaml

from deterrerscli.types import IPV4_TYPE

deterrers = None

profiles = click.Choice(
        ('', 'HTTP', 'SSH', 'HTTP+SSH', 'Multipurpose'),
        case_sensitive=False)
host_firewalls = click.Choice(
        ('', 'UFW', 'FirewallD', 'nftables'),
        case_sensitive=False)


def print_format(data, format: str):
    if format == 'yaml':
        print(yaml.dump(data))
    else:
        print(json.dumps(data, indent=4))


@click.group()
def cli():
    global deterrers
    with open(pathlib.Path().home() / '.deterrers.yml', 'r') as f:
        config = yaml.safe_load(f)
    deterrers = deterrersapi.Deterrers(config['url'], config['token'])


@cli.command()
@click.option('--format', default='json', help='Output format (json or yaml)')
def hosts(format):
    '''List all IPs added to DETERRERS.
    '''
    data = deterrers.hosts()
    print_format(data, format)


@cli.command()
@click.option('--format', default='json', help='Output format (json or yaml)')
@click.argument('ipv4', type=IPV4_TYPE)
def get(format, ipv4):
    '''Get information about an IP address in DETERRERS.
    '''
    data = deterrers.get(ipv4)
    print_format(data, format)


@cli.command()
@click.argument('ipv4', type=IPV4_TYPE)
def delete(ipv4):
    '''Delete IP address from DETERRERS.
    '''
    deterrers.delete(ipv4)


@cli.command()
@click.option('--admin', '-a', multiple=True, required=True)
@click.option('--profile', '-p', default='', type=profiles)
@click.option('--firewall', '-f', default='', type=host_firewalls)
@click.argument('ipv4', type=IPV4_TYPE)
def add(ipv4, admin, profile, firewall):
    '''Add IP address to DETERRERS.
    '''
    deterrers.add(ipv4, admin, profile, firewall)


@cli.command()
@click.option('--admin', '-a', default=None, multiple=True)
@click.option('--profile', '-p', default=None, type=profiles)
@click.option('--firewall', '-f', default=None, type=host_firewalls)
@click.argument('ipv4', type=IPV4_TYPE)
def update(ipv4, admin, profile, firewall):
    '''Update IP address in DETERRERS.

    Fields which are not specified will not be changed.
    The option `admin` can be used multiple times.
    '''
    admin = admin or None
    deterrers.update(ipv4, profile, firewall, admin)


@cli.group()
def action():
    '''Activate firewall profile or block IP address in perimeter firewall.
    '''
    pass


@action.command()
@click.argument('ipv4', type=IPV4_TYPE)
def register(ipv4):
    '''Activate profile in perimeter firewall.
    '''
    deterrers.action(ipv4, 'register')


@action.command()
@click.argument('ipv4', type=IPV4_TYPE)
def block(ipv4):
    '''Block IP address perimeter firewall.
    '''
    deterrers.action(ipv4, 'block')


if __name__ == '__main__':
    cli()
