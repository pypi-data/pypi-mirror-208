from igwn_lldd_common.utils import parse_topics, parse_topics_lsmp


def test_parse_topics():

    # Set the test topics
    topic1 = "test1"
    topic2 = "test2"

    # Create the topic dictionary
    topic_dict = {topic1: {}, topic2: {}}

    # Populate the first topic with relevant values
    topic_dict[topic1]["delta_t"] = int(1)
    topic_dict[topic1]["delta_t_fallback"] = int(2)
    topic_dict[topic1]["crc_check"] = False
    topic_dict[topic1]["max_latency"] = float(4.5)
    topic_dict[topic1]["acceptable_latency"] = float(3.6)
    topic_dict[topic1]["fast_forward_buffer"] = float(3.2)
    topic_dict[topic1]["max_kafka_latency"] = float(30.4)

    # Populate the second topic with relevant values
    topic_dict[topic2]["delta_t"] = int(3)
    topic_dict[topic2]["delta_t_fallback"] = int(4)
    topic_dict[topic2]["crc_check"] = False
    topic_dict[topic2]["max_latency"] = float(6.5)
    topic_dict[topic2]["acceptable_latency"] = float(32.6)
    topic_dict[topic2]["fast_forward_buffer"] = float(45.2)
    topic_dict[topic2]["max_kafka_latency"] = float(70.4)

    # Create a list to contain the topic partition informatin
    topic_partitions = []

    # Loop over the above information turning it into a topic partition
    for topic in topic_dict.keys():

        # Intialise the topic partion woth the topic
        itopic_partition = f"/topic={topic}/"

        # Loop ove the keys in the topic and add them to the partition
        for key in topic_dict[topic].keys():

            # Replace the _ with - so it can be parsed
            ikey = key.replace("_", "-")

            # Append it to the current partition
            itopic_partition += f"{ikey}={topic_dict[topic][key]}/"

        # Append this partition to the list of partitions
        topic_partitions.append(itopic_partition)

    # Attempt to parse the topics
    tp_info = parse_topics(topic_partitions)

    # Compare the two dictionaries for any irregularities
    for topic in topic_dict.keys():
        for key in topic_dict[topic].keys():

            # First check this key exists in tp_info
            if key not in tp_info[topic].keys():
                raise AssertionError(
                    f"The key {key} is not in the topic info "
                    "from parse_topics"
                )

            assert topic_dict[topic][key] == tp_info[topic][key], (
                f"The value for {key} does not match the value in "
                "the topic info from parse_topics:\n"
                f"\t{topic_dict[topic][key]} != {tp_info[topic][key]}"
            )


def test_parse_topics_lsmp():

    # Set the test topics
    topic1 = "test1"
    topic2 = "test2"

    # Create the topic dictionary
    topic_dict = {topic1: {}, topic2: {}}

    # Populate the first topic with relevant values
    topic_dict[topic1]["partition"] = "TestPartition1"
    topic_dict[topic1]["nbuf"] = int(5)
    topic_dict[topic1]["lbuf"] = int(10000)
    topic_dict[topic1]["delta_t"] = int(1)
    topic_dict[topic1]["delta_t_fallback"] = int(2)
    topic_dict[topic1]["ifo"] = "Z1"
    topic_dict[topic1]["crc_check"] = False
    topic_dict[topic1]["max_latency"] = float(4.5)
    topic_dict[topic1]["acceptable_latency"] = float(3.6)
    topic_dict[topic1]["fast_forward_buffer"] = float(3.2)
    topic_dict[topic1]["max_kafka_latency"] = float(30.4)
    topic_dict[topic1]["ringn"] = 154

    # Populate the second topic with relevant values
    topic_dict[topic2]["partition"] = "TestPartition2"
    topic_dict[topic2]["nbuf"] = int(10)
    topic_dict[topic2]["lbuf"] = int(5640)
    topic_dict[topic2]["delta_t"] = int(1)
    topic_dict[topic2]["delta_t_fallback"] = int(2)
    topic_dict[topic2]["ifo"] = "Z1"
    topic_dict[topic2]["crc_check"] = False
    topic_dict[topic2]["max_latency"] = float(4.5)
    topic_dict[topic2]["acceptable_latency"] = float(3.6)
    topic_dict[topic2]["fast_forward_buffer"] = float(3.2)
    topic_dict[topic2]["max_kafka_latency"] = float(30.4)
    topic_dict[topic2]["ringn"] = 35

    # Create a list to contain the topic partition informatin
    topic_partitions = []

    # Loop over the above information turning it into a topic partition
    for topic in topic_dict.keys():

        # Intialise the topic partion woth the topic
        itopic_partition = f"/topic={topic}/"

        # Loop ove the keys in the topic and add them to the partition
        for key in topic_dict[topic].keys():

            # Replace the _ with - so it can be parsed
            ikey = key.replace("_", "-")

            # Append it to the current partition
            itopic_partition += f"{ikey}={topic_dict[topic][key]}/"

        # Append this partition to the list of partitions
        topic_partitions.append(itopic_partition)

    # Attempt to parse the topics
    tp_info = parse_topics_lsmp(topic_partitions)

    # Compare the two dictionaries for any irregularities
    for topic in topic_dict.keys():
        for key in topic_dict[topic].keys():

            # First check this key exists in tp_info
            if key not in tp_info[topic].keys():
                raise AssertionError(
                    f"The key {key} is not in the topic info "
                    "from parse_topics"
                )

            assert topic_dict[topic][key] == tp_info[topic][key], (
                f"The value for {key} does not match the value in "
                "the topic info from parse_topics:\n"
                f"\t{topic_dict[topic][key]} != {tp_info[topic][key]}"
            )
