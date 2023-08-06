# -*- coding: utf-8 -*-
# Copyright (C) European Gravitational Observatory (2022) and
#               University of Wisconsin-Milwaukee (2022)
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

import logging
import time

logger = logging.getLogger(__name__)


class MessageFunnelProducer:
    def __init__(self):
        self.part_id = 0

    def create_payloads(self, data, evt_id, split_len):

        ############################################################
        # Split up payloads
        ############################################################
        # https://stackoverflow.com/questions/9475241/split-string-every-nth-character
        evt_len = len(data)
        chunks = [
            data[i: i + split_len] for i in range(0, evt_len, split_len)
        ]
        part_tot = len(chunks)
        part_num = 0
        part_off = 0
        payloads = []
        for chunk in chunks:
            part_len = len(chunk)
            # print('chunk: [', chunk, ']')
            payload = (
                bytes(
                    "PART"
                    + ",part_id="
                    + ("%012d" % self.part_id)
                    + ",part_num="
                    + ("%012d" % part_num)
                    + ",part_tot="
                    + ("%012d" % part_tot)
                    + ",evt_id="
                    + ("%012d" % evt_id)
                    + ",evt_len="
                    + ("%012d" % evt_len)
                    + ",part_off="
                    + ("%012d" % part_off)
                    + ",part_len="
                    + ("%012d" % part_len)
                    + "\0",
                    "utf-8",
                )
                + chunk
            )
            # print('payload: [', payload, ']')
            part_num += 1
            part_off += part_len
            payloads.append(payload)
        self.part_id += 1
        return payloads


class MessageFunnelConsumer(object):
    "This function stitches together objects retrieved from Kafka"

    def __init__(self):
        self.current_payloads = {}

    def add_payload(self, header_fields, chunk):
        req_fields = ["part_id", "part_num", "part_tot", "evt_id"]
        missing_fields = []
        for f in req_fields:
            if f not in header_fields:
                missing_fields.append(f)

        if missing_fields:
            logger.info(
                "%s Missing fields [%s] in header. Not adding payload."
                % (time.asctime(), ",".join(missing_fields))
            )

        part_id = int(header_fields["part_id"])
        part_num = int(header_fields["part_num"])
        part_tot = int(header_fields["part_tot"])
        evt_id = int(header_fields["evt_id"])

        if part_id not in self.current_payloads:
            # print('Found a new part_id: [', part_id, ']')
            # delete any old payloads
            # we use list(...) because we will be deleting keys. See e.g.:
            # https://stackoverflow.com/questions/11941817/how-to-avoid-runtimeerror-dictionary-changed-size-during-iteration-error
            for p_id in list(self.current_payloads):
                logger.info(
                    "%s Removing old part_id: [%d]" % (time.asctime(), p_id)
                )
                p_num_recv = []
                for p_num in self.current_payloads[p_id]["part_num"]:
                    p_num_recv.append(str(p_num))
                logger.info(
                    " Received (%d out of %d): [%s]"
                    % (
                        len(p_num_recv),
                        self.current_payloads[p_id]["part_tot"],
                        ",".join(p_num_recv),
                    )
                )
                self.current_payloads.pop(p_id, None)

            # now add the new one
            self.current_payloads[part_id] = {}
            self.current_payloads[part_id]["part_tot"] = part_tot
            self.current_payloads[part_id]["evt_id"] = evt_id
            self.current_payloads[part_id]["part_num"] = {}
        else:
            pass  # noop
            # print 'part_id: [', part_id, '] already in self.current_payloads'

        if part_num not in self.current_payloads[part_id]["part_num"]:
            self.current_payloads[part_id]["part_num"][part_num] = {}
            self.current_payloads[part_id]["part_num"][part_num][
                "chunk"
            ] = chunk
        else:
            logger.info(
                f"part_num: [{part_num}] of part_id: [{part_id}] already in \
list. Ignoring."
            )

    def extract_frame_buffer(self, header_fields, topic):
        part_id = int(header_fields["part_id"])

        if part_id not in self.current_payloads:
            logger.info(f"part_id: [{part_id}] not in self.current_payloads")
            return (False, [])

        req_fields = ["part_num", "part_tot", "evt_id"]
        missing_fields = []
        for f in req_fields:
            if f not in self.current_payloads[part_id]:
                missing_fields.append(f)

        if missing_fields:
            logger.info(
                "Missing keys [{missing_fields}] in \
self.current_payloads[{part_id}]"
            )

        part_tot = int(self.current_payloads[part_id]["part_tot"])

        # Get a sorted list of the part_id into part_ids
        # https://stackoverflow.com/questions/8953627/python-dictionary-keys-error
        part_nums = list(self.current_payloads[part_id]["part_num"])
        part_nums.sort()
        # print('keys: [', part_nums, ']')

        # see if this is now complete
        # https://stackoverflow.com/questions/18131741/python-find-out-whether-a-list-of-integers-is-coherent
        logger.debug(
            f"Recieved {part_nums} out of {part_tot} messages: topic: {topic} \
            gps: {header_fields['evt_id']}"
        )
        if part_nums == list(range(0, part_tot)):
            # print('Good to go')
            # Now add the chunks together to get the binary data
            binary_data = b""
            for part_num in part_nums:
                binary_data += self.current_payloads[part_id]["part_num"][
                    part_num
                ]["chunk"]
            # remove from the dictionary
            self.current_payloads.pop(part_id, None)
            return (True, binary_data)
        else:
            return (False, [])

    @staticmethod
    def parse_header(header):
        r = {}
        # At this point, could use e.g.
        # https://stackoverflow.com/questions/2175080/sscanf-in-python
        # input = '1:3.0 false,hello'
        # (a, b, c, d) = [t(s) for t,s in zip((int,float,bool,str),
        # re.search('^(\d+):([\d.]+) (\w+),(\w+)$',input).groups())]

        # Split up the header using commas
        header_statements = header.split(b",")

        for header_statement in header_statements:

            h_split = header_statement.split(b"=", 1)
            if len(h_split) != 2:
                continue

            (header_key, header_value) = h_split
            if header_value.isdigit() is False:
                logger.info(
                    "Error: in [{header_key}] value is not solely made up of \
digits: [{header_value}]. Ignored.",
                )
                continue

            if header_key == b"part_id":
                r["part_id"] = header_value
            elif header_key == b"part_num":
                r["part_num"] = header_value
            elif header_key == b"part_tot":
                r["part_tot"] = header_value
            elif header_key == b"evt_id":
                r["evt_id"] = header_value
            elif header_key == b"evt_len":
                pass
            elif header_key == b"part_off":
                pass
            elif header_key == b"part_len":
                pass
            else:
                logger.warning(
                    "Unknown header_key: [", header_key, "]. Ignored."
                )

        req_fields = ["part_id", "part_num", "part_tot", "evt_id"]
        missing_fields = []
        for f in req_fields:
            if f not in r:
                missing_fields.append(f)

        return (r, missing_fields)


def extract_frame_buffer_from_funnel(payload, message_funnel, topic):
    # Grab the header up to the null byte using an iterator, see e.g.
    # https://stackoverflow.com/questions/8162021/analyzing-string-input-until-it-reaches-a-certain-letter-on-python

    # Extract the header from the payload
    header = (payload.split(b"\x00"))[0]
    header_length = len(header)
    (header_fields, missing_fields) = message_funnel.parse_header(header)

    # Check for any fields that are missing
    if missing_fields:
        logger.info(
            "%s Missing fields [%s] in header [%s]. Ignoring this chunk."
            % (time.asctime(), ",".join(missing_fields), header)
        )
        return False, "", {}

    # Extract the frame chunk from the payload and add it to the funnel
    chunk = payload[header_length + 1: len(payload)]
    message_funnel.add_payload(header_fields, chunk)

    # Check if the frame is complete if so return full frame
    (complete, frame_buffer) = message_funnel.extract_frame_buffer(
        header_fields, topic
    )

    return complete, frame_buffer, header_fields["evt_id"]
