import click

from dnastack.alpha.cli.auth import alpha_auth_command_group
from dnastack.alpha.cli.data_connect import alpha_data_connect_command_group
from dnastack.alpha.cli.wes import alpha_wes_command_group
from dnastack.alpha.cli.workbench.commands import alpha_workbench_command_group


@click.group("alpha")
def alpha_command_group():
    """
    Interact with experimental commands.

    Warning: Commands in the alpha group are still under development and are being made available for testing and
    feedback. These commands may change incompatibly or be removed entirely at any time.
    """


alpha_command_group.add_command(alpha_auth_command_group)
alpha_command_group.add_command(alpha_wes_command_group)
alpha_command_group.add_command(alpha_data_connect_command_group)
alpha_command_group.add_command(alpha_workbench_command_group)