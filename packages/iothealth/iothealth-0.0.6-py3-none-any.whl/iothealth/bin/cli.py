# Copyright © 2020 by IoT Spectator. All rights reserved.

"""IoT Health CLI."""

import click

from iothealth import device_health


@click.group()
def cli():
    """CLI entry point."""
    pass


@click.command()
def summary():
    """Command for the health summary."""
    click.echo(device_health.DeviceHealth().summary())


@click.command()
def platform():
    """Command for platform info."""
    click.echo(device_health.DeviceHealth().device_platform())


@click.command()
def processor_arch():
    """Command for the CPU info."""
    click.echo(device_health.DeviceHealth().processor_architecture())


@click.command()
def os_info():
    """Command for OS info."""
    click.echo(device_health.DeviceHealth().operating_system())


@click.command()
def processors():
    """Command for processors info."""
    click.echo(device_health.DeviceHealth().processors())


@click.command()
def memory():
    """Command for the memory info."""
    click.echo(device_health.DeviceHealth().memory())


@click.command()
def capacity():
    """Command for the device capacity."""
    click.echo(device_health.DeviceHealth().capacity())


@click.command()
def temperature():
    """Command for the device temperature."""
    click.echo(device_health.DeviceHealth().temperature())


@click.command()
def cameras():
    """Command for the cameras info."""
    click.echo(device_health.DeviceHealth().cameras())


cli.add_command(summary)
cli.add_command(platform)
cli.add_command(processor_arch)
cli.add_command(os_info)
cli.add_command(processors)
cli.add_command(memory)
cli.add_command(capacity)
cli.add_command(temperature)
cli.add_command(cameras)


def main():
    """Entry point for the CLI."""
    cli()
