# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 13:11:09
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Common methods.
"""


from .rbase import warn, exc
from .rcompress import rzip
from .rdata import count, flatten, split, unique, ins, mutual_in
from .rdatabase import REngine
from .rdatetime import RDateTimeMark, now, time2str, str2time
from .remail import REmail
from .rfile import read_file, write_file
from .rimage import encode_qrcode, decode_qrcode, compress_image
from .rmultitask import threads
from . import roption
from .rother import digits, randn, sleep, get_paths, n2ch
from .rregular import res_search, res_sub
from .rrequest import request, download
from .rtext import rprint
from .rwrap import runtime, try_exc