from fabric import task
from .utils.tailscale_api import TailscaleAPI
from . import vpn_cmd


@task
def generate_ssh_config(c):
    """Print an SSH config file with all the Steinwurf VPN clients."""
    api = TailscaleAPI(url=c.config.tailscale.url, api_key=c.config.tailscale.api_key)
    credentials = c.config.tailscale.credentials
    print(vpn_cmd.generate_ssh_config(api, credentials))


@task
def list(c, all_devices=False):
    """Show the VPN clients."""
    api = TailscaleAPI(url=c.config.tailscale.url, api_key=c.config.tailscale.api_key)
    print(vpn_cmd.list(api, all_devices))


@task
def update_tailscale(c):
    """Update tailscale on the vpn clients."""
    api = TailscaleAPI(url=c.config.tailscale.url, api_key=c.config.tailscale.api_key)
    credentials = c.config.tailscale.credentials
    vpn_cmd.update_tailscale(api, credentials)
