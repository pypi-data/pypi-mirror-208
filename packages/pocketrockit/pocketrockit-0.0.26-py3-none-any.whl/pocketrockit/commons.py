#!/usr/bin/env python3

"""Shared stuff"""

from dataclasses import dataclass


@dataclass
class MidiEvent:
    """An internal application event"""

    status: int
    data1: int
    data2: int
    data3: int
    timestamp: int
