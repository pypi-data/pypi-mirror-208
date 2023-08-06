#!/usr/bin/env python

# -*- coding: utf-8 -*-
# Copyright (C) European Gravitational Observatory (EGO) (2022) and
# Laser Interferometer Gravitational-Wave Observatory (LIGO) (2022)
#
# Author list: Rhys Poulton <poulton@ego-gw.it>
#              Brockill <brockill@uwm.edu>
#
# This file is part of igwn-lldd-common.
#
# igwn-lldd-common is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# igwn-lldd-common is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with igwn-lldd-common.  If not, see <http://www.gnu.org/licenses/>.

# These routines are the Python translation of Kipp Cannon's algorithms
# in GstLAL. In particular, they come from framecpp_igwdparse.cc, which
# in August of 2018 can be found here:
# https://git.ligo.org/lscsoft/gstlal/tree/master/gstlal-ugly/gst/framecpp
import struct
import logging


logger = logging.getLogger(__name__)

# hex dump: hexdump -s SKIP_BYTES -n BYTES_LONG -C, xxd -c 16, hd,
# od -x --skip-bytes=BYTES --read-bytes=BYTES
# xxd -c 32 /dev/shm/llhoft/H1/H-H1_llhoft-1208708235-1.gwf | less

FrameCPPConst = {
    "SIZEOF_FRHEADER": 40,
    "FRHEADER_IDENT": b"IGWD",
    "SIZEOF_FRHEADER_IDENT": len("IGWD"),
    "FRSH_KLASS": 1,
    "FRENDOFFILE_NAME": b"FrEndOfFile",
    "FRAMEH_NAME": b"FrameH",
    # taken from /usr/include/math.h
    "M_PI": 3.14159265358979323846,
}


def frame_length(data):
    """
    Given an array of bytes which represent a frame, find the frame length.
    Uses Kipp Cannon's algorithms as described in framecpp_igwdparse.cc.
    These follow the data specs in the document:
    https://dcc.ligo.org/cgi-bin/DocDB/ShowDocument?docid=329 ."
    """

    frame_info = read_header(data)

    # update pointers to the next thing we'll look at: a table 6
    frame_info["offset"] = FrameCPPConst["SIZEOF_FRHEADER"]
    frame_info["filesize"] = frame_info["offset"] + \
        frame_info["sizeof_table_6"]

    file_start_time = 0
    file_stop_time = 0
    duration = 0

    while frame_info["filesize"] < frame_info["data_len"] and duration == 0:

        file_start_time, file_stop_time, duration = parse_table_6_then_7(
            data,
            frame_info
        )

        # update pointers to start all over again, assuming next thing
        # should be a table 6
        frame_info["offset"] = frame_info["filesize"]
        frame_info["filesize"] += frame_info["sizeof_table_6"]

    return (file_start_time, file_stop_time, duration)


def fr_get_int_8u(data, update_reader, frame_info, pre_skip=0, post_skip=0):
    frame_info["reader"] += pre_skip
    val = struct.unpack(
        frame_info["endianness"]
        + "Q", data[frame_info["reader"]: frame_info["reader"] + 8]
    )[0]
    if update_reader:
        frame_info["reader"] += 8
    frame_info["reader"] += post_skip
    return val


def fr_get_int_4u(data, update_reader, frame_info, pre_skip=0, post_skip=0):
    frame_info["reader"] += pre_skip
    val = struct.unpack(
        frame_info["endianness"]
        + "L", data[frame_info["reader"]: frame_info["reader"] + 4]
    )[0]
    if update_reader:
        frame_info["reader"] += 4
    frame_info["reader"] += post_skip
    return val


def fr_get_int_2u(data, update_reader, frame_info, pre_skip=0, post_skip=0):
    frame_info["reader"] += pre_skip
    val = struct.unpack(
        frame_info["endianness"]
        + "H", data[frame_info["reader"]: frame_info["reader"] + 2]
    )[0]
    if update_reader:
        frame_info["reader"] += 2
    frame_info["reader"] += post_skip
    return val


def fr_get_int_u(data, update_reader, frame_info, pre_skip=0, post_skip=0):
    frame_info["reader"] += pre_skip
    val = struct.unpack(
        frame_info["endianness"]
        + "b", data[frame_info["reader"]: frame_info["reader"] + 1]
    )[0]
    if update_reader:
        frame_info["reader"] += 1
    frame_info["reader"] += post_skip
    return val


def fr_get_uint8(data, update_reader, frame_info, pre_skip=0, post_skip=0):
    frame_info["reader"] += pre_skip
    val = struct.unpack(
        frame_info["endianness"]
        + "B", data[frame_info["reader"]: frame_info["reader"] + 1]
    )[0]
    if update_reader:
        frame_info["reader"] += 1
    frame_info["reader"] += post_skip
    return val


def fr_get_real4(data, update_reader, frame_info, pre_skip=0, post_skip=0):
    frame_info["reader"] += pre_skip
    val = struct.unpack(
        frame_info["endianness"]
        + "f", data[frame_info["reader"]: frame_info["reader"] + 4]
    )[0]
    if update_reader:
        frame_info["reader"] += 4
    frame_info["reader"] += post_skip
    return val


def fr_get_real8(data, update_reader, frame_info, pre_skip=0, post_skip=0):
    frame_info["reader"] += pre_skip
    val = struct.unpack(
        frame_info["endianness"]
        + "d", data[frame_info["reader"]: frame_info["reader"] + 8]
    )[0]
    if update_reader:
        frame_info["reader"] += 8
    frame_info["reader"] += post_skip
    return val


def fr_get_string(
    data,
    length,
    frame_info,
    update_reader,
    pre_skip=0,
    post_skip=0
):
    frame_info["reader"] += pre_skip
    # only grab up  to len-1, do not grab the \0 (=^@) at the end
    val = data[frame_info["reader"]: frame_info["reader"] + length - 1]
    if update_reader:
        frame_info["reader"] += length
    frame_info["reader"] += post_skip
    return val


def read_header(data):

    frame_info = {}
    frame_info["data_len"] = len(data)
    frame_info["reader"] = 5
    frame_info["offset"] = 0
    # Temporarily set the endianness to "<" (little Endian), we will only read
    # bytes for a bit
    frame_info["endianness"] = "<"
    frame_info["version"] = fr_get_int_u(data, True, frame_info, post_skip=1)
    frame_info["sizeof_int_2"] = fr_get_int_u(data, True, frame_info)
    frame_info["sizeof_int_4"] = fr_get_int_u(data, True, frame_info)
    frame_info["sizeof_int_8"] = fr_get_int_u(
        data,
        True,
        frame_info,
        post_skip=1
    )

    #
    # validate
    if fr_get_int_u(data, True, frame_info) != 8:
        logger.info(
            "Did not validate: should have found 8 = sizeof(REAL_8)"
        )

    # read in an int_2u using Little Endian and see what we get
    endian_check = fr_get_int_2u(data, True, frame_info)
    # now see how it came in
    if endian_check == int("0x1234", 16):
        frame_info["endianness"] = "<"
    elif endian_check == int("0x1234", 16):
        frame_info["endianness"] = ">"

    if struct.unpack(
        frame_info["endianness"]
        + "I", data[frame_info["reader"]: frame_info["reader"] + 4]
    )[0] != int("0x12345678", 16):
        logger.error("Failed 0x12345678 check...")
    frame_info["reader"] += 4
    if struct.unpack(
        frame_info["endianness"]
        + "Q", data[frame_info["reader"]: frame_info["reader"] + 8]
    )[0] != int("0x123456789abcdef", 16):
        logger.error("Failed 0x123456789abcdef check...")
    frame_info["reader"] += 8
    #
    # note: rounding error because of
    # https://docs.python.org/2/library/struct.html
    # "For the 'f' and 'd' conversion codes, the packed representation uses
    # the IEEE 754 binary32 (for 'f') or binary64 (for 'd') format,
    # regardless of the floating-point format used by the platform.")
    pi_float = fr_get_real4(data, True, frame_info)
    #
    # Now get a 4-byte version of PI
    # remember that Python "floats" are actually doubles in C
    M_PI_4 = struct.unpack(
        frame_info["endianness"] + "f",
        struct.pack(frame_info["endianness"] + "f", FrameCPPConst["M_PI"]),
    )[0]
    if pi_float != M_PI_4:
        logger.error(
            "Failed float pi check: we got pi=[",
            pi_float,
            "], but should be: [",
            M_PI_4,
            "]",
        )
    pi_double = fr_get_real8(data, True, frame_info)
    if pi_double != FrameCPPConst["M_PI"]:
        logger.error(
            "Failed double pi check: we got pi=[",
            pi_double,
            "], but should be: [",
            FrameCPPConst["M_PI"],
            "]",
        )

    frame_info["sizeof_table_6"] = (
        frame_info["sizeof_int_8"]
        + frame_info["sizeof_int_2"]
        + frame_info["sizeof_int_4"]
    )

    frame_info["eof_klass"] = 0
    frame_info["frameh_klass"] = 0

    return frame_info


def parse_table_6_then_7(data, frame_info):

    # start our reader at the current offset
    frame_info["reader"] = frame_info["offset"]

    #
    # structure_length
    structure_length = fr_get_int_8u(data, True, frame_info)
    #
    # klass
    if frame_info["version"] >= 8:
        klass = fr_get_uint8(
            data, True, frame_info, pre_skip=1
        )  # (skip a byte, chkType)
    else:
        klass = fr_get_int_2u(data, True, frame_info)

    #
    # now that we've parsed a table 6, prepare to parse a table 7
    frame_info["filesize"] = frame_info["offset"] + structure_length

    if frame_info["filesize"] > frame_info["data_len"]:
        logger.error("Err: filesize > data_len")
        return 0, 0, 0

    #
    # now parse the table 7
    if klass == FrameCPPConst["FRSH_KLASS"] and (
        frame_info["eof_klass"] == 0 or frame_info["frameh_klass"] == 0
    ):
        # now parse the table 7
        frame_info["reader"] = frame_info["offset"] \
            + frame_info["sizeof_table_6"]
        name_len = fr_get_int_2u(data, True, frame_info)
        name = fr_get_string(data, name_len, frame_info, True)
        if name == FrameCPPConst["FRENDOFFILE_NAME"]:
            frame_info["eof_klass"] = fr_get_int_2u(data, True, frame_info)
        elif name == FrameCPPConst["FRAMEH_NAME"]:
            frame_info["frameh_klass"] = fr_get_int_2u(data, True, frame_info)
    elif klass == frame_info["frameh_klass"]:
        return parse_table_9(data, frame_info)

    return 0, 0, 0


# table 9 is where we get the start time and the duration
def parse_table_9(data, frame_info):
    frame_info["reader"] = frame_info["offset"] + frame_info["sizeof_table_6"]
    name_len = fr_get_int_2u(data, True, frame_info)
    # The name of the frame
    fr_get_string(
        data,
        name_len,
        frame_info,
        True,
        post_skip=3 * frame_info["sizeof_int_4"]
    )
    # the integer part of the start time
    file_start_time = fr_get_int_4u(data, True, frame_info)
    # now the nanoseconds
    file_start_time += (
        fr_get_int_4u(
            data,
            True,
            frame_info,
            post_skip=frame_info["sizeof_int_2"]
        )
        * 0.000000001
    )
    duration = fr_get_real8(data, True, frame_info)
    file_stop_time = file_start_time + round(duration)
    return file_start_time, file_stop_time, duration
