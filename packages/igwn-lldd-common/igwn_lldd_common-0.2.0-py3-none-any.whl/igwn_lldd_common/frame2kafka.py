#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# Copyright (C) European Gravitational Observatory (2022)
#
# Author: Rhys Poulton <poulton@ego-gw.it>
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

import sys
import configargparse
import logging
import queue
import ntpath
import time
try:
    from watchdog.observers import Observer
    from .io import FrameFileEventHandler
    watchdog_found = True
except ImportError:
    from .io import monitor_dir_inotify
    import threading
    watchdog_found = False
from .utils import str2bool
from .framekafkaproducer import FrameKafkaProducer

logger = logging.getLogger(__name__)
# right now we're having trouble having these logs go to the pipes
# we set up before: we get a bunch of errors in the logging module
# when it tries to call self.stream.flush(), probably because of
# the O_NONBLOCKING option used when opened
# consoleHandler = logging.StreamHandler(f_log.get_file())
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
        "-d",
        "--debug",
        type=int,
        default=0,
        help="increase debug level (default 0=off)",
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
        help="Specify the Kafka cluster bootstrap servers",
    )
    parser.add_argument(
        "-fd",
        "--frame-directory",
        type=str,
        help="The directory where the frames are written to"
    )
    parser.add_argument("-l", "--log", type=str, help="Standard log file")
    parser.add_argument(
        "-v",
        "--verbose",
        const=True,
        default=False,
        action='store_const',
        help="Verbose log file")
    parser.add_argument("-g", "--group-id", type=str, help="Kafka group ID")
    parser.add_argument(
        "-S",
        "--split-bytes",
        type=int,
        default=100000,
        help="Split messages into this many bytes when adding to Kafka",
    )
    parser.add_argument(
        "-t",
        "--topic",
        type=str,
        required=True,
        help="Kafka topic to write to"
    )
    parser.add_argument(
        "-crc",
        "--crc-check",
        type=str2bool,
        default=True,
        help="Run a CRC check for each frame",
    )
    parser.add_argument(
        "-bs",
        "--batch-size",
        type=int,
        help="Change the batch.size for the producer [default: 16384]",
    )
    parser.add_argument(
        "-bm",
        "--buffer-memory",
        type=int,
        help="Change the buffer.memory for the producer \
[default: 33554432B=32MB]",
    )
    parser.add_argument(
        "-lm",
        "--linger-ms",
        type=int,
        help="Change the linger.ms for the producer [default: 0]",
    )
    parser.add_argument(
        "-a",
        "--acks",
        default=1,
        type=int,
        help="Change the acks for the producer"
    )
    parser.add_argument(
        "-mi",
        "--min-interval",
        default=-1,
        type=float,
        help="Enforce a minimum interval between gwf files",
    )
    parser.add_argument(
        "-su",
        "--status-updates",
        action="store_const",
        const=True,
        default=False,
        help="store status updates",
    )
    parser.add_argument(
        "-st", "--status-topic", type=str, help="topic name for status updates"
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
        "-dt",
        "--delta-t",
        default=1,
        type=int,
        help="Make sure each frame comes in at delta_t seconds",
    )
    # custom libraries
    parser.add_argument(
        "-lkp",
        "--load-kafka-python",
        action="store_const",
        const=True,
        default=False,
        help="load kafka-python rather than confluent-kafka",
    )

    # Parse the arguments from the command line
    args, _ = parser.parse_known_args(args)

    logger.info(f"verbose: [{args.verbose}]")
    logger.info(f"topic: [{args.topic}]")
    logger.info(f"crc_check: [{args.crc_check}]")
    logger.info(f"bootstrap_servers: [{args.bootstrap_servers}]")
    logger.info(f"split_bytes: [{args.split_bytes}]")
    logger.info(f"batch_size: [{args.batch_size}]")
    logger.info(f"linger_ms: [{args.linger_ms}]")
    logger.info(f"min_interval: [{args.min_interval}]")
    logger.info(f"delta_t: [{args.delta_t}]")

    framekafkaproducer = FrameKafkaProducer(args)

    # Setup queue to talk to the observer
    filenamequeue = queue.Queue()

    # Check if the watchdog module was found
    if watchdog_found:

        # Create the event handler
        event_handler = FrameFileEventHandler(filenamequeue)

        # Setup the observer to watch for new frame files
        observer = Observer()
        observer.schedule(
            event_handler,
            path=args.frame_directory,
        )
        observer.daemon = True
        observer.start()
    else:

        # Create the inotify handler
        observer = threading.Thread(
            target=monitor_dir_inotify,
            args=(filenamequeue, args.frame_directory)
        )

        # Start the observer and set the stop attribute
        observer.stop = False
        observer.start()

    # Mark start time
    start_time = time.time()

    while True:

        # Check if the runtime has gone above the max runtime
        runtime = time.time() - start_time
        if args.max_runtime and runtime > args.max_runtime:
            logger.info(
                "Have run for %f seconds stopping" % runtime
            )
            break

        # Check if the queue is empty
        if filenamequeue.empty():
            continue

        # Get the next filename from the queue
        framefilename = filenamequeue.get()

        # Get the contents of the frame
        with open(framefilename, "rb") as f:
            frame_buffer = f.read()

        # Extract timestamp from the filename
        basefilename = ntpath.basename(framefilename)

        # If this is filename is correctly formatted the 3rd part when
        # split by "-" should be the timestamp
        tmp = basefilename.split("-")
        if len(tmp) != 4:
            raise IOError(
                "The frame filename is not correctly formatted"
                "the correct format is: \n"
                "\t <obs>-<tag>-<gps>-<dur>.[gwf,hdf5,h5]"
            )
        try:
            timestamp = int(tmp[2])
        except ValueError:
            raise IOError(
                "Could not turn the gps time in the frame is \
                it correctly formatted. The correct format is: \
                \t <obs>-<tag>-<gps>-<dur>.[gwf,hdf5,h5]"
            )

        # Do the crc check to confirm that this is a frame
        # if args.crc_check:
        #     returncode = check_crc(
        #         reader,
        #         args.topic,
        #         frame_buffer,
        #         timestamp
        #     )

        framekafkaproducer.send_frame(frame_buffer, timestamp)

        if args.verbose:
            logger.info(
                "gps:%i "
                "file timestamp %d "
                "latency:%0.3f "
                "unix:%0.3f "
                "send:%0.3f "
                "flush:%0.3f "
                "send+flush:%0.3f "
                "avg_rate_30s_MBs:%0.3f "
                "data_n:%d\n"
                % (
                    framekafkaproducer.time_after_flush_gps,
                    timestamp,
                    framekafkaproducer.time_after_flush_gps - timestamp,
                    framekafkaproducer.time_after_flush_unix,
                    framekafkaproducer.time_before_flush_unix
                    - framekafkaproducer.time_before_send_unix,
                    framekafkaproducer.time_after_flush_unix
                    - framekafkaproducer.time_before_flush_unix,
                    framekafkaproducer.time_during_send_flush,
                    framekafkaproducer.data_rate,
                    framekafkaproducer.data_n,
                )
            )
    # close
    framekafkaproducer.close()

    # Stop the observer
    if watchdog_found:
        observer.unschedule_all()
        observer.stop()
    else:
        observer.stop = True

    # Join the observer thread and wait for it to finish
    observer.join()


if __name__ == "__main__":
    sys.exit(main())
