#!/usr/bin/env python3

"""API for fancy decorator based track definitions"""

# pylint: disable=too-many-locals

import logging
import re
from collections.abc import Callable, MutableSequence, Sequence
from contextlib import suppress
from itertools import count
from typing import Union

from pocketrockit.engine import EMPTY_COMMAND, Env, MidiCmd, Player, Stage, run
from pocketrockit.misc import error, throw

NestedStringSequence = MutableSequence[Union[str, "NestedStringSequence"]]

stage = Stage()

__all__ = ["track", "player", "midiseq"]


def logger() -> logging.Logger:
    """Named logger"""
    return logging.getLogger("pr.decorated")


def run_engine(initial_track: str) -> bool:
    """If engine is not yet running, run it and never return"""
    if stage.active:
        return False

    stage.active = True
    stage.file_to_track = initial_track
    run()
    return True


def track(track_definition_fn: Callable[[Env], None]) -> None:
    """Creates a track (a list of note generators called players) by running provided
    @track_definition_fn
    Only effective starting from second run."""
    if run_engine(track_definition_fn.__globals__["__file__"]):
        return

    logger().info("define track '%s'", track_definition_fn.__name__)
    stage.new_track = {}
    env = Env(bpm=stage.env.bpm)
    try:
        # create the new track model
        track_definition_fn(env)
    except Exception as exc:  # pylint: disable=broad-except
        if not stage.verified:
            raise
        error(f"exception in build: {exc}")
        # In case of errors we abort loading the track, keeping the currently loaded one
        return

    stage.players, stage.new_track, stage.env = stage.new_track, None, env

    # initialize note generators (and also trigger eventual bugs!)
    for name, stream in stage.players.items():
        logger().info("initialize player %s with tick=%d", name, stage.tick)
        try:
            if not len(next(stream)) == 3:
                raise RuntimeError(f"Player '{name}' didn't return valid command")
            stream.send(stage.tick + 1)
        except Exception as exc:  # pylint: disable=broad-except
            if not stage.verified:
                raise
            # In case of errors we only skip the affected player, accepting all others
            error(f"exception in player init: {exc}")

    stage.verified = True


def player(player_definition_fn: Callable[[], Player]) -> None:
    """Adds generator created from @player_definition_fn to new track definition"""
    name = player_definition_fn.__name__
    logger().info("define player %r", name)
    assert stage.new_track is not None
    stage.new_track[name] = player_definition_fn()


# @contextmanager
# def FX(name, controller):
# try:
# print(f"enter FX {name}")
# yield "bla"

# finally:
# print("exit")


# def apply(ctx_manager):
# return ctx_manager


def midi_scale(key: str) -> Sequence[int]:
    """Create a major or minor scale based on @key. @key can be any element of NOTES. Alphabetic
    notes ('C', 'C#', 'Db', etc.) without an octave identifier default to octave 4.
    E.g. 'C' => 'C4', etc.
    Numeric values will be directly interpreted as MIDI values
    """
    base = key.strip("-")
    minor = key[-1] == "-"
    octave = "" if any(base[i] in {"0123456789"} for i in (0, -1)) else "4"
    base_tone = NOTES.get(f"{base}{octave}", NOTES[base])

    return [
        base_tone + e for e in ([0, 2, 3, 5, 7, 8, 10, 12] if minor else [0, 2, 4, 5, 7, 9, 11, 12])
    ]


def base_note(note_str: str) -> tuple[None | str, ...]:
    """Dissects a note written in one of all possible ways into its (optional) components"""
    if match := re.match(
        r"^("
        "(((n|t)([1-8]))|([iv]{1,4}))"
        "|((a|b|c|d|e|f|g|a|h)(#|b|is|es|s)?([0-9]|[’|']*)?)"
        "|([0-9]{1,3}))"
        "([><+-]*)$",
        note_str,
        re.IGNORECASE,
    ):
        # return tuple(match.groups())
        return tuple(match.group(5, 6, 7, 11, 12))
    raise RuntimeError(note_str)


def resolve(note_str: str | int, scale: Sequence[int]) -> int:
    """Not in the mood to write a comment"""
    if isinstance(note_str, int):
        return note_str
    with suppress(ValueError):
        return int(note_str)
    degree, rom_degree, note, num_note, modifier = base_note(note_str)
    shift = (
        sum(
            12 if e == ">" else -12 if e == "<" else 1 if e == "+" else -1 if e == "-" else 0
            for e in modifier
        )
        if modifier
        else 0
    )
    tone = (
        scale[
            int(degree) - 1
            if degree is not None
            else ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"].index(rom_degree.lower())
            if rom_degree is not None
            else throw(RuntimeError())
        ]
        if degree or rom_degree
        else NOTES[note or num_note or throw(RuntimeError())]
    )

    return tone + shift


def midi_commands(
    string: str, channel: int, force_note: None | str | int, scale: Sequence[int], velocity: int
) -> Sequence[MidiCmd]:
    """Turns something like '60', 'c', 'c,d,e' or 't1,t2,t3' into MIDI commands"""
    try:
        return (
            []
            if string == "."
            else [
                (
                    channel,
                    resolve(
                        force_note if force_note is not None and element == "x" else element, scale
                    ),
                    velocity,
                )
                for element in string.split(",")
            ]
        )
    except Exception as exc:  # pylint: disable=broad-except
        if not Stage().verified:
            raise
        error(f"could not turn '{string}' into note ({exc})")

    return []


def parenthetic_contents(string: str) -> NestedStringSequence:
    """Generate parenthesized contents in string as pairs (level, contents).
    >>> list(parenthetic_contents(" a  b"))
    ['a', 'b']
    >>> list(parenthetic_contents(" ab (cd)ef( gh )if  (kl(mn))op"))
    ['ab', ['cd'], 'ef', ['gh'], 'if', ['kl', ['mn']], 'op']
    """
    back_pointer, has_content = 0, False
    current: NestedStringSequence
    current = []
    stack: MutableSequence[NestedStringSequence] = [current]

    for i, char in enumerate(string):
        if char == " ":
            if has_content:
                has_content = False
                current.append(string[back_pointer:i])
        elif char == "(":
            if has_content:
                current.append(string[back_pointer:i])
            has_content = False
            stack.append(current)
            new_element: NestedStringSequence = []
            current.append(current := new_element)
        elif char == ")":
            if has_content:
                current.append(string[back_pointer:i])
            has_content = False
            current = stack.pop()
        else:
            if not has_content:
                back_pointer, has_content = i, True
    if has_content:
        current.append(string[back_pointer:])

    # print(string, stack[0])
    return stack[0]


def quantized_pattern(
    nested_pattern: NestedStringSequence, resolution: int
) -> Sequence[tuple[int, str]]:
    """Assigns a line-relative tick number to every note"""
    result: MutableSequence[tuple[int, str]] = []
    # assert len(nested_pattern)
    # assert depth(nested_pattern)
    # assert sizes are modules

    step_size = resolution // len(nested_pattern)
    for i, elem in enumerate(nested_pattern):
        if isinstance(elem, str):
            result.append((i * step_size, elem))
        else:
            sub_step_size = step_size // len(elem)
            for j, sub_elem in enumerate(elem):
                result.append((i * step_size + j * sub_step_size, str(sub_elem)))
    # print(result)
    return result


def pattern_list_from(
    *pattern_definition: str | Sequence[str],
) -> Sequence[Sequence[Sequence[tuple[int, str]]]]:
    """Turns various pattern definition styles into"""

    def block(pattern: str) -> Sequence[Sequence[tuple[int, str]]]:
        return [
            quantized_pattern(parenthetic_contents(line), Stage().env.step_size)
            for line in pattern.split("|")
            if line.strip()
        ]

    if all(isinstance(p, str) for p in pattern_definition):
        # only one string or a tuple of strings
        return [block(str(p)) for p in pattern_definition]

    if isinstance(pattern_definition[0], (list, tuple)) and len(pattern_definition) == 1:
        return [block(p) for p in pattern_definition[0]]

    raise RuntimeError(f"Did not understand pattern definition {pattern_definition}")


def midiseq(
    *pattern: str | Sequence[str],
    channel: int = 0,
    note: None | int | str = None,
    key: str | Sequence[str] = "C",
    velocity: int = 30,
    **_kwargs: str | int,
) -> Player:
    """A minimal MIDI sequencer"""
    pattern_blocks = pattern_list_from(*pattern)
    step_size = Stage().env.step_size
    loop_size = step_size * sum(len(elements) for elements in pattern_blocks)

    reset_tick: None | int = None
    keys = key.split(",") if isinstance(key, str) else key

    while True:
        if reset_tick is not None:
            logger().debug("reset to %d", reset_tick)
            yield EMPTY_COMMAND

        start_loop = (reset_tick or 0) // loop_size
        skip = (reset_tick or 0) % loop_size
        tick_iter = count((reset_tick or 0) - skip)
        reset_tick = None

        for loop_nr, block_nr, block_key, scale, line_nr, (next_relative_tick, next_element) in (
            (_loop_nr, _block_nr, _key, _scale, _line_nr, _element)
            for _loop_nr in count(start_loop)
            for _line_nr, (_block_nr, _key, _scale, _line) in enumerate(
                (__block_nr, __key, __scale, __line)
                for __block_nr, __lines in enumerate(pattern_blocks)
                for __key in (keys[(_loop_nr * len(pattern_blocks) + __block_nr) % len(keys)],)
                for __scale in (midi_scale(__key),)
                for __line in __lines
            )
            for _element in _line
        ):

            next_tick = loop_nr * loop_size + line_nr * step_size + next_relative_tick
            logger().debug(
                "loop: %d block: %d key: %s line: %d next_tick: %d => %s",
                loop_nr,
                block_nr,
                block_key,
                line_nr,
                next_tick,
                next_element,
            )
            for tick in tick_iter:
                play = tick == next_tick

                if skip:
                    skip -= 1
                else:
                    assert next_tick >= tick
                    reset_tick = yield (
                        (
                            (loop_nr, block_nr, tick),
                            next_element,
                            midi_commands(next_element, channel, note, scale, velocity),
                        )
                        if play
                        else EMPTY_COMMAND
                    )

                if play:
                    break

            if reset_tick is not None:
                break


# B2!!
# A2!!
NOTES = {
    name: midi
    for midi, names, freq in (
        (21, {"21", "A0"}, 27.5),  # A2!!
        (22, {"Bb0", "22", "Ais2", "A#0"}, 29.14),
        (23, {"B0", "23", "H2"}, 30.87),
        (24, {"24", "B#0", "C1"}, 32.7),
        (25, {"C#1", "Cis1", "Des1", "Db1", "25"}, 34.65),
        (26, {"26", "D1"}, 36.71),
        (27, {"Es1", "27", "Dis1", "D#1", "Eb1"}, 38.89),
        (28, {"E1", "28"}, 41.2),
        (29, {"F1", "E#1", "29"}, 43.65),
        (30, {"F#1", "Gb1", "Fis1", "Ges1", "30"}, 46.25),
        (31, {"G1", "31"}, 49.0),
        (32, {"Gis1", "As1", "Ab1", "G#1", "32"}, 51.91),
        (33, {"33", "A1"}, 55.0),
        (34, {"b1", "A#1", "Bb1", "34", "Ais1"}, 58.27),
        (35, {"B1", "35", "H1"}, 61.74),
        (36, {"C", "C2", "B#1", "36"}, 65.41),
        (37, {"37", "C#2", "Db2", "Cis", "Des"}, 69.3),
        (38, {"D", "38", "D2"}, 73.42),
        (39, {"Eb2", "D#2", "Dis", "Es", "39"}, 77.78),
        (40, {"E2", "E", "40"}, 82.41),
        (41, {"F", "E#2", "41", "F2"}, 87.31),
        (42, {"F#2", "Ges", "42", "Gb2", "Fis"}, 92.5),
        (43, {"G2", "G", "43"}, 98.0),
        (44, {"44", "G#2", "Ab2", "As", "Gis"}, 103.83),
        (45, {"A", "45", "A2"}, 110.0),
        (46, {"Ais", "A#2", "Bb2", "B", "46"}, 116.54),
        (47, {"47", "H", "B2"}, 123.47),
        (48, {"C3", "B#2", "c", "48"}, 130.81),
        (49, {"Db3", "cis", "C#3", "49", "des"}, 138.59),
        (50, {"D3", "d", "50"}, 146.83),
        (51, {"es", "dis", "D#3", "51", "Eb3"}, 155.56),
        (52, {"E3", "e", "52"}, 164.81),
        (53, {"f", "E#3", "53", "F3"}, 174.61),
        (54, {"ges", "Gb3", "54", "fis", "F#3"}, 185.0),
        (55, {"55", "g", "G3"}, 196.0),
        (56, {"56", "G#3", "as", "gis", "Ab3"}, 207.65),
        (57, {"57", "A3", "a"}, 220.0),
        (58, {"Bb3", "b", "58", "A#3", "ais"}, 233.08),
        (59, {"h", "B3", "59"}, 246.94),
        (60, {"c’", "60", "B#3", "C4"}, 261.63),  # Middle C
        (61, {"Db4", "C#4", "des’", "cis’", "61"}, 277.18),
        (62, {"D4", "d’", "62"}, 293.66),
        (63, {"es’", "D#4", "63", "Eb4", "dis’"}, 311.13),
        (64, {"e’", "64", "E4"}, 329.63),
        (65, {"f’", "65", "E#4", "F4"}, 349.23),
        (66, {"fis’", "ges’", "Gb4", "F#4", "66"}, 369.99),
        (67, {"g’", "67", "G4"}, 392.0),
        (68, {"Ab4", "as’", "68", "gis’", "G#4"}, 415.3),
        (69, {"69", "A4", "a’"}, 440.0),
        (70, {"70", "A#4", "Bb4", "ais’", "b’"}, 466.16),
        (71, {"h’", "71", "B4"}, 493.88),
        (72, {"72", "c’’", "B#4", "C5"}, 523.25),
        (73, {"C#5", "cis’’", "73", "Db5", "des’’"}, 554.37),
        (74, {"D5", "74", "d’’"}, 587.33),
        (75, {"dis’’", "Eb5", "es’’", "D#5", "75"}, 622.25),
        (76, {"e’’", "76", "E5"}, 659.26),
        (77, {"f’’", "77", "E#5", "F5"}, 698.46),
        (78, {"fis’’", "ges’’", "F#5", "78", "Gb5"}, 739.99),
        (79, {"79", "G5", "g’’"}, 783.99),
        (80, {"as’’", "gis’’", "80", "Ab5", "G#5"}, 830.61),
        (81, {"81", "A5", "a’’"}, 880.0),
        (82, {"A#5", "82", "b’’", "ais’’", "Bb5"}, 932.33),
        (83, {"h’’", "83", "B5"}, 987.77),
        (84, {"c’’’", "84", "B#5", "C6"}, 1046.5),
        (85, {"cis’’’", "des’’’", "C#6", "Db6", "85"}, 1108.73),
        (86, {"D6", "86", "d’’’"}, 1174.66),
        (87, {"D#6", "dis’’’", "87", "Eb6", "es’’’"}, 1244.51),
        (88, {"E6", "88", "e’’’"}, 1318.51),
        (89, {"f’’’", "F6", "E#6", "89"}, 1396.91),
        (90, {"fis’’’", "F#6", "ges’’’", "Gb6", "90"}, 1479.98),
        (91, {"91", "g’’’", "G6"}, 1567.98),
        (92, {"as’’’", "gis’’’", "G#6", "Ab6", "92"}, 1661.22),
        (93, {"A6", "a’’’", "93"}, 1760.0),
        (94, {"A#6", "94", "Bb6", "b’’’", "ais’’’"}, 1864.66),
        (95, {"95", "h’’’", "B6"}, 1975.53),
        (96, {"c’’’’", "C7", "B#6", "96"}, 2093.0),
        (97, {"97", "Db7", "C#7", "des’’’’", "cis’’’’"}, 2217.46),
        (98, {"d’’’’", "98", "D7"}, 2349.32),
        (99, {"D#7", "dis’’’’", "Eb7", "99", "es’’’’"}, 2489.02),
        (100, {"E7", "100", "e’’’’"}, 2637.02),
        (101, {"f’’’’", "E#7", "F7", "101"}, 2793.83),
        (102, {"fis’’’’", "ges’’’’", "Gb7", "F#7", "102"}, 2959.96),
        (103, {"103", "g’’’’", "G7"}, 3135.96),
        (104, {"Ab7", "G#7", "as’’’’", "104", "gis’’’’"}, 3322.44),
        (105, {"105", "a’’’’", "A7"}, 3520.0),
        (106, {"106", "Bb7", "ais’’’’", "A#7", "b’’’’"}, 3729.31),
        (107, {"h’’’’", "107", "B7"}, 3951.07),
        (108, {"c’’’’’", "108", "B#7", "C8"}, 4186.01),
        (109, {"109", "Db8", "des’’’’’", "cis’’’’’", "C#8"}, 4434.92),
        (110, {"d’’’’’", "D8", "110"}, 4698.64),
        (111, {"dis’’’’’", "Eb8", "D#8", "111", "es’’’’’"}, 4978.03),
        (112, {"112", "e’’’’’", "E8"}, 5274.04),
        (113, {"F8", "E#8", "113", "f’’’’’"}, 5587.65),
        (114, {"Gb8", "F#8", "ges’’’’’", "fis’’’’’", "114"}, 5919.91),
        (115, {"g’’’’’", "G8", "115"}, 6271.93),
        (116, {"116", "Ab8", "as’’’’’", "G#8", "gis’’’’’"}, 6644.88),
        (117, {"117", "a’’’’’", "A8"}, 7040.0),
        (118, {"Bb8", "b’’’’’", "A#8", "118", "ais’’’’’"}, 7458.62),
        (119, {"119", "h’’’’’", "B8"}, 7902.13),
        (120, {"c’’’’’’", "C9", "B#8", "120"}, 8372.02),
        (121, {"Db9", "121", "C#9", "des’’’’’’", "cis’’’’’’"}, 8869.84),
        (122, {"d’’’’’’", "122", "D9"}, 9397.27),
        (123, {"dis’’’’’’", "es’’’’’’", "123", "D#9", "Eb9"}, 9956.06),
        (124, {"E9", "e’’’’’’", "124"}, 10548.08),
        (125, {"F9", "E#9", "f’’’’’’", "125"}, 11175.3),
        (126, {"fis’’’’’’", "126", "ges’’’’’’", "Gb9", "F#9"}, 11839.82),
        (127, {"G9", "g’’’’’’", "127"}, 12543.85),
    )
    for name in names
}
