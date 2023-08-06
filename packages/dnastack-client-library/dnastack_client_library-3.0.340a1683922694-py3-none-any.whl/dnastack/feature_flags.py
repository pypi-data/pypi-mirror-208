import sys
from dnastack.common.environments import flag

# For more details about environment variables, please check out dev-configuration.md.

dev_mode = flag('DNASTACK_DEV')
in_global_debug_mode = flag('DNASTACK_DEBUG')
in_interactive_shell = sys.__stdout__ and sys.__stdout__.isatty()
cli_show_list_item_index = flag('DNASTACK_SHOW_LIST_ITEM_INDEX')
detailed_error = flag('DNASTACK_DETAILED_ERROR')
