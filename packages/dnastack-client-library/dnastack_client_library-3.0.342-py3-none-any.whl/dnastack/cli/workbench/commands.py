import click

from dnastack.cli.workbench.runs_commands import runs_command_group


@click.group('workbench')
def workbench_command_group():
    """ Interact with Workbench """


workbench_command_group.add_command(runs_command_group)
