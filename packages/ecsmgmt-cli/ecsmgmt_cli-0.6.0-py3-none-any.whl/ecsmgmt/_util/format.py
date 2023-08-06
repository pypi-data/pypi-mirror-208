from typing import Union

import yaml
from tabulate import tabulate


class IndentedListDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super(IndentedListDumper, self).increase_indent(flow, False)


def pretty_table(data: list, headers: Union[list, None] = None, tablefmt: str = 'github') -> str:
    """Tabulate wrapper function with predefined format"""
    if headers is None:
        table = tabulate(data, tablefmt=tablefmt)
    else:
        table = tabulate(data, headers=headers, tablefmt=tablefmt)
    return table


def pretty_info(data: dict) -> str:
    """Print data in a nice form"""
    return str(yaml.safe_dump(data))
