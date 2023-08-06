import igwn_lldd_common.messageparser as mepa


# Create a random bytestring
message = b"jagfiygflwavkfiCSALCMShoiwbsjcajWSAKSC"
timestamp = 0
split_bytes = 10


def test_message_parser():

    # Create a instance of the message funnel producer
    messagefunnelproducer = mepa.MessageFunnelProducer()

    # Use the message funnel producer to creat the payload
    payload = messagefunnelproducer.create_payloads(
        message, timestamp, split_bytes
    )

    # Create a instance of the messagefunnel consumer to
    # reassemble the message
    messagefunnelconsumer = mepa.MessageFunnelConsumer()

    # Now take this payload and try to reassemble it
    for chunk in payload:

        # Put the chunk into the message funnel
        complete, mess_reas, evt_id = mepa.extract_frame_buffer_from_funnel(
            chunk, messagefunnelconsumer, "TestTopic"
        )

    # Check if the message was successfully reassembled
    if not complete:
        raise SystemExit("The message was not sucessfully reassembled")

    # Check it does match
    assert message == mess_reas, "Error: the reassembled message is not \
    the same as the orginal message"
