#!/usr/bin/python3

# -*- coding: utf-8 -*-
# Copyright (C) European Gravitational Observatory (2022)
# Author list: Rhys Poulton <poulton@ego-gw.it>
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

import os
import sys
import time
import configargparse
import logging
from collections import deque
import re
from .utils import (
    parse_topics,
    GracefulKiller,
    str2bool,
    # check_crc
)
from .framelen import frame_length
from .framekafkaconsumer import FrameKafkaConsumer
from .io import write_frame

logger = logging.getLogger(__name__)
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)


def main(args=None):

    parser = configargparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        is_config_file=True,
        help="config file path"
    )
    parser.add_argument(
        "-d", "--debug", type=int, help="increase debug level (default 0=off)"
    )
    parser.add_argument(
        "-dw",
        "--debug-wait",
        type=float,
        default=0.0,
        help="wait x seconds between gwf files (used to \
 intentionally break things for debugging)",
    )
    parser.add_argument(
        "-maxt",
        "--max-runtime",
        type=float,
        help="Maximum time to run before exiting (undef=Infinity)",
    )
    parser.add_argument(
        "-b",
        "--bootstrap-servers",
        type=str,
        default="localhost:9092",
        help="specify the Kafka cluster bootstrap servers",
    )
    parser.add_argument(
        "-a",
        "--add-topic-partition",
        type=str,
        action="append",
        required=True,
        help="/topic=LHO_Data/partition=KLHO_Data/nbuf=16/lbuf=1000000 \
/delta-t=4/crc-check=true/",
    )
    parser.add_argument(
        "-x",
        "--exit-if-missing-topics",
        action="store_const",
        const=True,
        default=False,
        help="exit if any topics are missing",
    )
    parser.add_argument(
        "-s",
        "--ssl",
        action="store_const",
        const=True,
        default=False,
        help="use ssl"
    )
    parser.add_argument("-p", "--ssl-password", type=str, help="ssl password")
    parser.add_argument(
        "-ca",
        "--ssl-cafile",
        type=str,
        help="location of ca-cert"
    )
    parser.add_argument(
        "-cf",
        "--ssl-certfile",
        type=str,
        help="location of signed certificate"
    )
    parser.add_argument(
        "-kf", "--ssl-keyfile", type=str, help="location of personal keyfile"
    )
    parser.add_argument("-g", "--group-id", type=str, help="Kafka group ID")
    parser.add_argument(
        "-su",
        "--status-updates",
        action="store_const",
        const=True,
        default=False,
        help="store status updates",
    )
    parser.add_argument(
        "-st",
        "--status-topic",
        type=str,
        help="topic name for status updates"
    )
    parser.add_argument(
        "-sb",
        "--status-bootstrap",
        type=str,
        help="specify the kafka cluster for status updates",
    )
    parser.add_argument(
        "-si",
        "--status-interval",
        type=int,
        default=60,
        help="interval in seconds between status updates",
    )
    parser.add_argument(
        "-sn",
        "--status-nodename",
        type=str,
        help="specify the node name used in status updates",
    )
    parser.add_argument(
        "-ff",
        "--fast-forward",
        type=str2bool,
        default=True,
        help="fast forward if fall behind",
    )
    parser.add_argument(
        "-lkp",
        "--load-kafka-python",
        action="store_const",
        const=True,
        default=False,
        help="load kafka-python rather than confluent-kafka",
    )
    parser.add_argument(
        "-fd",
        "--frame-dir",
        type=str,
        required=True,
        help="Directory where the frames are written out to",
    )
    parser.add_argument(
        "-o",
        "--observatory",
        type=str,
        required=True,
        help="Observatory for the filename (L, V, K) <obs>-<tag>-<gps>-<dt>",
    )
    parser.add_argument(
        "-rn",
        "--ringn",
        type=int,
        default=None,
        help="Number of frame_log files to retain",
    )
    parser.add_argument(
        "-pt",
        "--poll-timeout",
        type=int,
        default=1000,
        help="Timeout when doing consumer.poll() [in ms]. Default: 1000.",
    )
    parser.add_argument(
        "-pr",
        "--poll-max-records",
        type=int,
        default=1,
        help="Max records returned when doing consumer.poll(). Default: 1.",
    )
    parser.add_argument(
        "-pif",
        "--pid-file",
        type=str,
        default=None,
        help="File in which to store PID of main process.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        const=True,
        action="store_const",
        help="verbose log output",
    )

    # Parse the arguments from the command line
    args = parser.parse_args(args)

    # Get the topics from the topic partition
    tp_info = parse_topics(args.add_topic_partition)

    # Startup the frame kafka consumer
    framekafkaconsumer = FrameKafkaConsumer(args, tp_info)

    # Set the filename
    frame_filename_pattern = \
        f"{args.observatory}-%tag%-%timestamp%-%delta_t%.gwf"
    frame_filename_pattern = os.path.join(
        args.frame_dir, frame_filename_pattern
    )

    ringn_topic = {}
    dyn_frame_len = {}
    file_name_dq = {}

    # Setup each of the topic
    for topic in tp_info:

        # Check if topic has ringn
        if "ringn" in tp_info[topic] and tp_info[topic]["ringn"]:
            ringn_topic[topic] = int(tp_info[topic]["ringn"])
            file_name_dq[topic] = deque([], ringn_topic[topic])
        else:
            if args.ringn:
                ringn_topic[topic] = int(args.ringn)
                file_name_dq[topic] = deque([], ringn_topic[topic])
            else:
                ringn_topic[topic] = None
                file_name_dq[topic] = deque([], ringn_topic[topic])

        #
        # do we have to dynamically calculate frame length?
        dyn_frame_len[topic] = False
        if not ("delta_t" in tp_info[topic]) or not tp_info[topic]["delta_t"]:
            if (
                "delta_t_fallback" in tp_info[topic]
                and tp_info[topic]["delta_t_fallback"]
            ):
                dyn_frame_len[topic] = True
        else:
            frame_filename_pattern = re.sub(
                "%delta_t%",
                str(tp_info[topic]["delta_t"]),
                frame_filename_pattern
            )

        if args.debug is not None and args.debug > 0:
            if dyn_frame_len[topic]:
                logger.info(
                    "Dynamically calculating frame lengths for topic [%s]\n"
                    % topic
                )
            else:
                logger.info(
                    "Will NOT be dynamically calculating frame lengths for \
topic [%s]\n" % topic
                )

    # Capture signals in the main thread
    killer = GracefulKiller()

    # Mark start time
    start_time = time.time()

    while not killer.kill_now:

        # Check if the runtime has gone above the max runtime
        runtime = time.time() - start_time
        if args.max_runtime and runtime > args.max_runtime:
            logger.info(
                "Have run for %f seconds stopping" % runtime
            )
            break

        # Run consumer.poll()
        r_poll = framekafkaconsumer.poll_consumer_for_topic()

        # parse the messages
        for topic_partition in r_poll:
            for message in r_poll[topic_partition]:

                # We can check for ^C frequently, it's just a variable
                if killer.kill_now:
                    logger.info("main: ^C while processing messages")
                    break

                # Get the frame buffer from the kafka messgae
                (
                    frame_buffer,
                    payload_info
                ) = framekafkaconsumer.extract_frame_buffer_from_message(
                    message, tp_info
                )

                # Continue if the full frame has not been assembled
                if not frame_buffer:
                    continue

                # come up with a filename
                frame_filename = re.sub(
                    "%timestamp%",
                    "%0.10d" % (payload_info["data_gps_timestamp"]),
                    frame_filename_pattern,
                )
                frame_filename = re.sub(
                    "%tag%",
                    payload_info["topic"],
                    frame_filename,
                )

                # do we have to calculate dynamically the length of the frame?
                if (
                    dyn_frame_len[payload_info["topic"]]
                    or "frame_duration" not in payload_info.keys()
                ):
                    (
                        frame_start_time,
                        frame_stop_time,
                        frame_duration,
                    ) = frame_length(frame_buffer)
                    frame_filename = re.sub(
                        "%delta_t%", str(int(frame_duration)), frame_filename
                    )
                else:
                    frame_filename = re.sub(
                        "%delta_t%",
                        str(int(payload_info["frame_duration"])),
                        frame_filename
                    )

                # now write this to the shared memory partition
                write_frame(
                    frame_filename,
                    frame_buffer,
                    ringn_topic[topic],
                    file_name_dq[topic]
                )

                if args.debug_wait > 0.0:
                    logger.info("WAITING...")
                    time.sleep(args.debug_wait)

    # and close the Kafka connection
    framekafkaconsumer.close()

    if args.pid_file is not None:
        logger.info("Removing old pid file [", args.pid_file, "]")
        os.unlink(args.pid_file)

    # did we exit out on a signal?
    # if so, we've reset the signal handlers, so call the signal
    # again to get the default handling.
    # (If we don't do this, then killing the parent by using "kill"
    # and not "kill -9" will just keep the parent around waiting
    # for the child to terminate, for example.)
    if killer.kill_now:
        os.kill(os.getpid(), killer.signum)


if __name__ == "__main__":
    sys.exit(main())
