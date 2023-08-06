#!/usr/bin/env python3

"""Shared stuff"""

from dataclasses import dataclass


@dataclass
class Event:
    """An internal application event"""

    type: int | str
