from typing import Optional

from dnastack.cli.helpers.iterator_printer import show_iterator
from dnastack.client.data_connect import DataConnectClient


def handle_query(data_connect: DataConnectClient,
                 query: str,
                 decimal_as: str = 'string',
                 no_auth: bool = False,
                 output_format: Optional[str] = None):
    iterator = data_connect.query(query, no_auth=no_auth)
    show_iterator(output_format, iterator, decimal_as=decimal_as, sort_keys=False)