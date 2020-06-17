from enum import Enum


# constants
MAX_FILE_SIZE = 268435456  # 268MB
DEFAULT_PATH = "/ext_ssd/WBrec/"

V4L2_PIX_FMT_RG12 = 842090322  # v4l2_fourcc('R', 'G', '1', '2')


# Brief:
# This is the enum types for the metadata sizes which will be written.
class MetadataBytes(Enum):
    FileMeta = 256  # 64  # the File metadata is 64 bytes long.
    FrameMeta = 32  # 32  # the frame metadata is 32 bytes long
