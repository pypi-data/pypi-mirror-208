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

import argparse
import signal
import importlib.util
import logging
import time
import gpstime

logger = logging.getLogger(__name__)


class GracefulKiller:
    kill_now = False
    signum = 0

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        # reset the signal handlers
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.kill_now = True
        # save the signal
        self.signum = signum


# check if module exists before importing it
# we'll have to rewrite this for python3, see the following link:
# https://stackoverflow.com/questions/14050281/
# how-to-check-if-a-python-module-exists-without-importing-it
def check_lib_python3(libname):
    logger.info(f"Looking for library [{libname}]...")
    loadlib = importlib.util.find_spec(libname)
    if loadlib is not None:
        return True
    else:
        return False


# Function to parse boolean values in argparse. Taken from:
# https://stackoverflow.com/questions/15008758/
# parsing-boolean-values-with-argparse
def str2bool(v):
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def parse_topics(topic_partitions):

    # for the --add-topic-partition arguments, we then pars e the argument
    # immediatelyfollowing each. Note that we do not use sub parsers
    # (see add_subparsers in argparse)

    #
    # Split up each of the --add-topic-partition arguments and parse them, too
    tp_parser = argparse.ArgumentParser()
    tp_parser.add_argument("-t", "--topic", type=str, help="The topic")
    tp_parser.add_argument(
        "-d",
        "--delta-t",
        type=int,
        help="Make sure each frame comes in at delta_t seconds",
    )
    tp_parser.add_argument(
        "-dfb",
        "--delta-t-fallback",
        type=int,
        help="Dynamically calculate frame length, use this value if cannot be \
found",
    )
    tp_parser.add_argument(
        "-c",
        "--crc-check",
        type=str2bool,
        default=False,
        help="Run a CRC check for each frame",
    )
    tp_parser.add_argument(
        "-ml",
        "--max-latency",
        type=float,
        default=-1,
        help="maximum tolerated latency of data (s) (-1 for infinite)",
    )
    tp_parser.add_argument(
        "-al",
        "--acceptable-latency",
        type=float,
        default=-1.0,
        help="when fast forwarding, first try to see if we can seek to data \
with this latency first before seek_to_end (-1 to ignore).",
    )
    tp_parser.add_argument(
        "-ffp",
        "--fast-forward-buffer",
        type=float,
        default=5.0,
        help="amount to pause before seek_to_end when stream is behind \
max-latency",
    )
    tp_parser.add_argument(
        "-mk",
        "--max-kafka-latency",
        type=float,
        default=-1,
        help="maximum tolerated latency of data through Kafka broker (s) \
(-1 for infinite)",
    )
    tp_info = {}

    # Parse the --add-topic-partition commands separately
    for tp in topic_partitions:
        # print 'topic_partition: [', tp, ']'
        # Inspired by https://stackoverflow.com/questions/7866128/
        # python-split-without-removing-the-delimiter
        tp_new = ["--" + e for e in tp.split(tp[0]) if e]
        tp_args = tp_parser.parse_args(tp_new)
        topic = tp_args.topic
        if not tp_args.topic:
            raise ValueError("Need at least a topic in string [", tp, "]")
        for arg in dir(tp_args):
            # iterate over members of this class to see what we've defined
            val = getattr(tp_args, arg)
            if (
                not arg.startswith("__")
                and not callable(val)
                and not arg == "topic"
            ):
                # Add into the tp_info hash, do it the fast way:
                # https://biggestfool.tumblr.com/post/21247759480/
                # on-the-speed-of-dictionaries-in-python
                try:
                    tp_info[topic][arg] = val
                except KeyError:
                    # First time we've seen this topic.
                    # Create a new subdict first.
                    tp_info[topic] = {}
                    tp_info[topic][arg] = val

    for topic in tp_info.keys():
        tp_info[topic]["extra_info"] = {}
        tp_info[topic]["extra_info_str"] = []

    return tp_info


def parse_topics_lsmp(topic_partitions):

    # for the --add-topic-partition arguments, we then parse the argument
    # immediately following each. Note that we do not use sub parsers
    # (see add_subparsers in argparse)

    #
    # Split up each of the --add-topic-partition arguments and parse them, too
    tp_parser = argparse.ArgumentParser()
    tp_parser.add_argument("-t", "--topic", type=str, help="The topic")
    tp_parser.add_argument("-p", "--partition", type=str, help="The partition")
    tp_parser.add_argument(
        "-n", "--nbuf", type=int, help="The number of LSMP buffers"
    )
    tp_parser.add_argument(
        "-l", "--lbuf", type=int, help="The size of each LSMP buffer"
    )
    tp_parser.add_argument(
        "-d",
        "--delta-t",
        type=int,
        help="Make sure each frame comes in at delta_t seconds",
    )
    tp_parser.add_argument(
        "-dfb",
        "--delta-t-fallback",
        type=int,
        help="Dynamically calculate frame length, use this value if cannot be \
found",
    )
    tp_parser.add_argument(
        "-i", "--ifo", type=str, help="The IFO (H1, L1, V1, etc.)"
    )
    tp_parser.add_argument(
        "-c",
        "--crc-check",
        type=str2bool,
        default=False,
        help="Run a CRC check for each frame",
    )
    tp_parser.add_argument(
        "-ml",
        "--max-latency",
        type=float,
        default=-1,
        help="maximum tolerated latency of data (s) (-1 for infinite)",
    )
    tp_parser.add_argument(
        "-al",
        "--acceptable-latency",
        type=float,
        default=-1.0,
        help="when fast forwarding, first try to see if we can seek to data \
with this latency first before seek_to_end (-1 to ignore).",
    )
    tp_parser.add_argument(
        "-ffp",
        "--fast-forward-buffer",
        type=float,
        default=5.0,
        help="amount to pause before seek_to_end when stream is behind \
max-latency",
    )
    tp_parser.add_argument(
        "-mk",
        "--max-kafka-latency",
        type=float,
        default=-1,
        help="maximum tolerated latency of data through Kafka broker (s) \
(-1 for infinite)",
    )
    tp_parser.add_argument(
        "-rn",
        "--ringn",
        type=int,
        default=None,
        help="Number of frame_log files to retain",
    )

    tp_info = {}

    #
    # Parse the --add-topic-partition commands separately
    for tp in topic_partitions:
        # print 'topic_partition: [', tp, ']'
        # Inspired by https://stackoverflow.com/questions/7866128/
        # python-split-without-removing-the-delimiter
        tp_new = ["--" + e for e in tp.split(tp[0]) if e]
        tp_args = tp_parser.parse_args(tp_new)
        topic = tp_args.topic
        if not tp_args.topic:
            raise ValueError("Need at least a topic in string [", tp, "]")
        partition = tp_args.partition
        if not partition:
            raise ValueError("Need at least a partition in string [", tp, "]")
        for arg in dir(tp_args):
            # iterate over members of this class to see what we've defined
            val = getattr(tp_args, arg)
            if (
                not arg.startswith("__")
                and not callable(val)
                and not arg == "topic"
            ):
                # Add into the tp_info hash, do it the fast way:
                # https://biggestfool.tumblr.com/post/21247759480/
                # on-the-speed-of-dictionaries-in-python
                try:
                    tp_info[topic][arg] = val
                except KeyError:
                    # First time we've seen this topic.
                    # Create a new subdict first.
                    tp_info[topic] = {}
                    tp_info[topic][arg] = val

    for topic in tp_info.keys():
        tp_info[topic]["extra_info"] = {
            "partition": tp_info[topic]["partition"]
        }
        tp_info[topic]["extra_info_str"] = [
            f"partition {tp_info[topic]['partition']}"
        ]

    return tp_info


def check_crc(ShmMemReadWrite, topic, data, timestamp, partition=None):

    # Calculate size of the data
    data_size = len(data)

    # FIXME
    # https://stackoverflow.com/questions/606191/convert-bytes-to-a-string
    # if not writer.has_crc(data.decode('cp437')):
    if not ShmMemReadWrite.has_crc(data):
        if partition is not None:
            logger.info(
                "Topic:[%s] Partition:[%s] %d get %d %d CRC NOT FOUND. \
Dropping.\n"
                % (
                    topic,
                    partition,
                    gpstime.unix2gps(time.time()),
                    timestamp,
                    data_size,
                )
            )
        else:
            logger.info(
                "Topic:[%s] %d get %d %d CRC NOT FOUND. Dropping.\n"
                % (topic, gpstime.unix2gps(time.time()), timestamp, data_size)
            )
        return 1
    else:
        #
        # FIXME
        # if not writer.check_crc(data.decode('cp437')):
        if not ShmMemReadWrite.check_crc(data):
            if partition is not None:
                logger.info(
                    "Topic: [%s] Partition: [%s] %d get %d %d CRC FAILED. \
Dropping.\n"
                    % (
                        topic,
                        partition,
                        gpstime.unix2gps(time.time()),
                        timestamp,
                        data_size,
                    )
                )
            else:
                logger.info(
                    "Topic: [%s] %d get %d %d CRC FAILED. Dropping.\n"
                    % (
                        topic,
                        gpstime.unix2gps(time.time()),
                        timestamp,
                        data_size
                    )
                )
            return 2
    return 0
