from pathlib import Path
from igwn_lldd_common.framelen import frame_length


TEST_DATA_DIR = Path(__file__).parent / 'data'
TEST_GWF_FILE = TEST_DATA_DIR / 'Z-igwn_lldd_common_test-1000000000-1.gwf'


# Read the data from the frame file
with open(TEST_GWF_FILE, "rb") as f:
    FRAME_DATA = f.read()


def test_framelen():

    file_start_time, file_stop_time, duration = frame_length(FRAME_DATA)

    assert file_start_time == 1000000000, \
        "The start time of the frame is incorrect"

    assert file_stop_time == 1000000001, \
        "The start time of the frame is incorrect"

    assert duration == 1.0, \
        "The start time of the frame is incorrect"
