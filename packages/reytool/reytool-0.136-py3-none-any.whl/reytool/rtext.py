# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 13:18:24
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Text methods.
"""


from typing import Any, List, Literal, Optional
from pprint import pformat as pprint_pformat
from urwid import old_str_util

from .rbase import get_first_notnull, get_name
from .rmonkey import pprint_modify_format_width_judgment
from . import roption


# Based on module pprint.pformat, modify the chinese width judgment.
pprint_modify_format_width_judgment()


def split_text(text: str, man_len: int, by_width: bool = False) -> List[str]:
    """
    `Split` text by max length or not greater than `display width`.

    Parameters
    ----------
    text : Text.
    man_len : max length.
    by_width : Whether by char displayed width count length.

    Returns
    -------
    Split text.
    """

    # Split.
    texts = []

    ## By char displayed width.
    if by_width:
        str_group = []
        str_width = 0
        for char in text:
            char_width = get_width(char)
            str_width += char_width
            if str_width > man_len:
                string = "".join(str_group)
                texts.append(string)
                str_group = [char]
                str_width = char_width
            else:
                str_group.append(char)
        string = "".join(str_group)
        texts.append(string)

    ## By char number.
    else:
        test_len = len(text)
        split_n = test_len // man_len
        if test_len % man_len:
            split_n += 1
        for n in range(split_n):
            start_indxe = man_len * n
            end_index = man_len * (n + 1)
            text_group = text[start_indxe:end_index]
            texts.append(text_group)

    return texts


def get_width(text: str) -> int:
    """
    `Get` text `display width`.

    Parameters
    ----------
    text : Text.

    Returns
    -------
    Text display width.
    """

    # Get width.
    total_width = 0
    for char in text:
        char_unicode = ord(char)
        char_width = old_str_util.get_width(char_unicode)
        total_width += char_width

    return total_width


def fill_width(text: str, char: str, width: int, align: Literal["left", "right", "center"] = "right") -> str:
    """
    Text `fill` character by `display width`.

    Parameters
    ----------
    text : Fill text.
    char : Fill character.
    width : Fill width.
    align : Align orientation.
        - `Literal[`left`]` : Fill right, align left.
        - `Literal[`right`]` : Fill left, align right.
        - `Literal[`center`]` : Fill both sides, align center.

    Returns
    -------
    Text after fill.
    """

    # Check parameters.
    if get_width(char) != 1:
        raise ValueError("parameter `char` value error")

    # Fill width.
    text_width = get_width(text)
    fill_width = width - text_width
    if fill_width > 0:
        if align == "left":
            new_text = "%s%s" % (char * fill_width, text)
        elif align == "right":
            new_text = "%s%s" % (text, char * fill_width)
        elif align == "center":
            fill_width_left = int(fill_width / 2)
            fill_width_right = fill_width - fill_width_left
            new_text = "%s%s%s" % (char * fill_width_left, text, char * fill_width_right)
        else:
            raise ValueError("parameter `align` value error")
    else:
        new_text = text

    return new_text


def print_frame(
    *contents: Any,
    title: Optional[str],
    width: int,
    frame: Literal["full", "half", "plain"]
) -> None:
    """
    `Print` contents and frame.

    Parameters
    ----------
    contents : Print contents.
    title : Print frame title.
        - `None` : No title.
        - `str` : Use this value as the title.

    width : Print frame width.
    frame : Frame type.
        - `Literal[`full`]` : Build with symbol `═╡╞─║╟╢╔╗╚╝`, and content not can exceed the frame.
            When throw `error`, then frame is `half` type.
        - `Literal[`half`]` : Build with symbol `═╡╞─`, and content can exceed the frame.
        - `Literal[`plain`]` : Build with symbol `=|-`, and content can exceed the frame.
    """

    # Handle parameters.
    if title == None or len(title) > width - 6:
        title = ""

    # Generate frame.

    ## Full type.
    if frame == "full":
        if title != "":
            title = f"╡ {title} ╞"
        width_in = width - 2
        _contents = []
        try:
            for content in contents:
                content_str = str(content)
                pieces_str = content_str.split("\n")
                content_str = [
                    "║%s║" % fill_width(line_str, " ", width_in)
                    for piece_str in pieces_str
                    for line_str in split_text(piece_str, width_in, True)
                ]
                content = "\n".join(content_str)
                _contents.append(content)
        except:
            frame_top = fill_width(title, "═", width, "center")
            frame_split = "─" * width
            frame_bottom = "═" * width
            _contents = contents
        else:
            frame_top = "╔%s╗" % fill_width(title, "═", width_in, "center")
            # frame_split = "╠%s╣" % ("═" * width_in)
            frame_split = "╟%s╢" % ("─" * width_in)
            frame_bottom = "╚%s╝" % ("═" * width_in)

    ## Half type.
    elif frame == "half":
        if title != "":
            title = f"╡ {title} ╞"
        frame_top = fill_width(title, "═", width, "center")
        frame_split = "─" * width
        frame_bottom = "═" * width
        _contents = contents

    ## Plain type.
    elif frame == "plain":
        if title != "":
            title = f"| {title} |"
        frame_top = fill_width(title, "=", width, "center")
        frame_split = "-" * width
        frame_bottom = "=" * width
        _contents = contents

    # Print.
    print(frame_top)
    for index, content in enumerate(_contents):
        if index != 0:
            print(frame_split)
        print(content)
    print(frame_bottom)


def rprint(
        *contents: Any,
        title: Optional[str] = None,
        width: Optional[int] = None,
        frame: Optional[Literal["full", "half", "plain"]] = "full",
        format: bool = True
    ) -> None:
    """
    `Print` formatted contents.

    Parameters
    ----------
    contents : Print contents.
    title : Print frame title.
        - `None` : No title.
        - `str` : Use this value as the title.

    width : Print frame width.
        - `None` : Use `print_width` of module `roption`.
        - `int` : Use this value.

    frame : Frame type.
        - `Literal[`full`]` : Use `print_frame_full` of module `roption`.
            Build with symbol `═╡╞─║╟╢╔╗╚╝`, and content not can exceed the frame.
            When throw error, then frame is `half` type.
        - `Literal[`half`]` : Use `print_frame_half` of module `roption`.
            Build with symbol `═╡╞─`, and content can exceed the frame.
        - `Literal[`plain`]` : Use `print_frame_plain` of module `roption`.
            Build with symbol `=|-`, and content can exceed the frame.
    
    format : Whether format data of type list or tuple or dict or set.
    """

    # Get parameters by priority.
    width = get_first_notnull(width, roption.print_width)

    # Handle parameters.
    if title == None:
        titles = get_name(contents)
        if titles != None:
            titles = [title if title[:1] != "`" else "" for title in titles]
            if set(titles) != {""}:
                title = " │ ".join(titles)
    if frame == "full":
        frame = roption.print_frame_full
    elif frame == "half":
        frame = roption.print_frame_half
    elif frame == "plain":
        frame = roption.print_frame_plain

    # Format contents.
    if format:
        if frame == "full":
            _width = width - 2
        else:
            _width = width
        contents = [
            pprint_pformat(content, width=_width, sort_dicts=False)
            if content.__class__ in (list, tuple, dict, set)
            else content
            for content in contents
        ]

    # Print.
    print_frame(*contents, title=title, width=width, frame=frame)