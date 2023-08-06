#!/usr/bin/env python3

from pocketrockit import Env, midiseq, player, track

# fmt: off

@track
def track_name(env: Env):
    """Put a little poem here"""

    # @env object contains some global stuff like (currently: only) bpm
    env.bpm = 60

    key = "C4"

    @player
    def metronome():
        yield from midiseq("x x x x", channel=128, note=37)
