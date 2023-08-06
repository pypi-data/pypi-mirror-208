import typing as t
from typing import Union

import click
from click.core import Parameter, Context


class TimeParamType(click.ParamType):
    """Convert a duration as a string or integer to a number of seconds.

    If an integer is provided it is treated as seconds and is unchanged.

    String durations can have a suffix of 's', 'm', 'h', 'd', 'w', or 'y'.
    No suffix is treated as seconds.
    """
    name = 'time duration'

    def convert(self, value: Union[int, str], param: t.Optional['Parameter'], ctx: t.Optional['Context']) -> int:
        if isinstance(value, int):
            return value

        if isinstance(value, str) and value.isdigit():
            return int(value)

        second = 1
        minute = 60 * second
        hour = 60 * minute
        day = 24 * hour
        week = 7 * day
        year = 365 * day
        sizes = {'s': second, 'm': minute, 'h': hour, 'd': day, 'w': week, 'y': year}
        suffix = value[-1]

        if suffix in sizes:
            value = value[:-1]
            size = sizes[suffix]
        else:
            self.fail(f'{value!r} is not a valid time duration expression', param, ctx)
        return int(value) * size


TIME = TimeParamType()
