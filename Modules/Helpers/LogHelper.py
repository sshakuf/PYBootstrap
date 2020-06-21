import logging
import os
from logging.handlers import RotatingFileHandler
import numpy as np
import pickle
from struct import *
import construct
from Modules.V4L.V4L2Enums import *
from datetime import datetime
from Modules.Helpers.Enums.RxEnums import *
import tkinter as tk
from tkinter import messagebox


# ####################### #
# ----- Construct ------- #
# ####################### #
reserved_size = 184
comment_size = 32

file_meta = construct.Struct(
    "magic" / construct.Int64sb,  # 8 bytes
    "header_size" / construct.Int32sb,  # 4 bytes
    "header_ver" / construct.Float32b,  # 4 bytes
    "width" / construct.Int32sb,  # 4 bytes
    "height" / construct.Int32sb,  # 4 bytes
    "timestamp" / construct.Float64b,  # 8 bytes
    "data_out_type" / construct.Int64sb,  # 8 bytes
    "comment" / construct.Bytes(comment_size),  # 32 bytes
    "reserved" / construct.Array(reserved_size, construct.Byte),  # 256 - 72 = 184 bytes reserved
)

frame_meta = construct.Struct(
    "magic_word" / construct.Int64sb,  # 8 bytes
    "seconds" / construct.Int64sb,  # 8 bytes
    "microsecond" / construct.Int64sb,  # 8 bytes
    "reserved" / construct.Int64sb,  # 8 bytes
)


def build_file_meta(timestamp=0, width=8192, height=32, data_out_type=DataOutType.BeamFormerData, comment=""):
    zero_list = [0]
    reserved = zero_list + [0] * (reserved_size - len(zero_list))
    _comment = comment.ljust(comment_size)  # this will move the string to the left and fill the rest with zeros

    return file_meta.build(dict(magic=0XC0FFEE00, header_size=256, header_ver=0.01, width=width,
                                height=height, timestamp=timestamp, data_out_type=data_out_type.value,
                                comment=file_meta.comment.parse(_comment.encode()), reserved=reserved))


def build_frame_meta(seconds, microsecond):
    return frame_meta.build(dict(magic_word=0xDEADBEEF, seconds=seconds, microsecond=microsecond, reserved=0,
                                 reserved2=0))


# file metadata size is depend on the frame metadata struct.
def get_frame_meta_size():
    return frame_meta.sizeof()


# file metadata size is depend on the file metadata struct.
def get_file_meta_size():
    return file_meta.sizeof()

# ####################### #
# ------------------------#
# ####################### #


# GENERAL FUNCTIONS #

def write_to_file(file, _data):
    file.write(_data)


# add meta data to the beginning of the file which will include: width(16bit), height(16bit), mode(16bit),
# reserved(16bit), add timestamp to each frame read as well.
def open_file(_file="logFile.bin", data_out_type=0):  # DataOutType default is 0 for mipi test data
    file_path = DEFAULT_PATH
    file_prefix = "/ADRS_"
    file_suffix_format = "%d%m%y_%H%M%S"
    str_now = datetime.now().strftime(file_suffix_format)
    _file = f"{file_path}{file_prefix}_{str_now}.bin"
    return open(_file, "wb")


def close_file(file):
    file.close()


def configure_log(use_console=True, name="App", folder='log', logger_name=None,
                  level=logging.DEBUG,
                  message_format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'):
    date_format = "%y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=message_format, datefmt=date_format)
    os.makedirs(folder, exist_ok=True)
    log_file = os.path.join(folder, '%s.log' % name)
    file_handler = RotatingFileHandler(log_file, mode='w', encoding='utf8', maxBytes=20000000, backupCount=3)
    file_handler.setLevel(level)  # TODO from config
    handlers = [file_handler]
    if use_console:
        console_handler = logging.StreamHandler()
        handlers.append(console_handler)
        console_handler.setLevel(level)
    logger = logging.getLogger() if logger_name is None else logging.getLogger(logger_name)
    logger.setLevel(level)  # TODO from config
    for h in handlers:
        h.setFormatter(formatter)
    logger.handlers = handlers
    # logger.addHandler(h)
    return logger


def dump_to_file(filename: str, data: np.ndarray):
    """
    dump data to file
    file is appended on each dump.
    each block is preceded by a header of the form:
        magic word:   int16  "2BED"
        data length:  int16,  counting 16bit words
        data type:    int16,  0-real data, 1 - complex data
        spare:        int16,  0 (constant)
    """

    header = np.zeros(4, dtype='int16')
    header[0] = 0x2bed
    header[3] = 0

    if data.dtype == np.complex:
        header[1] = data.size * 2
        header[2] = 1
        data_struct = np.ndarray([len(data), 2], dtype='int16')

        data_struct[:, 0] = np.real(data)
        data_struct[:, 1] = np.imag(data)

    else:
        header[1] = data.size
        header[2] = 0
        data_struct = data.astype('int16')

    f = open(filename, "ab")
    f.write(header.tobytes())
    f.write(data_struct.tobytes())
    f.close()


def pickle_dump(filename: str, data: np.ndarray):
    pickle.dump(data, open(filename, "wb"))


def dump_complex_to_file(filename: str, data: np.ndarray):
    f = open(filename, "ab")
    f.write(data.real.astype('float64'))
    f.write(data.imag.astype('float64'))
    f.close()


# Please Note, the frame meta is written as follows:
# height (2 bytes), width (2 bytes), data_tpye (2 bytes), reserved (2 bytes).
def read_file_metadata(file, num_of_bytes):
    file_metadata = file.read(num_of_bytes)
    parsed = file_meta.parse(file_metadata)
    return parsed.timestamp, parsed.width, parsed.height, parsed.data_out_type
    # return file_metadata
    # img_height, img_width, data_type = unpack('hhh', file_metadata[:6])  # two reserved bytes are read but ignored
    # return img_width, img_height, data_type


# Please Note, the frame meta is written as follows:
# magic word (8 bytes)
# seconds (8 bytes)
# microseconds (8 bytes)
# reserved (8 bytes)
def read_frame_metadata(file, num_of_bytes: int = 32):
    # print(num_of_bytes)
    frame_metadata = file.read(num_of_bytes)
    if len(frame_metadata) != num_of_bytes:
        return -1, -1, -1  # return -1 when no more data is available
    parsed = frame_meta.parse(frame_metadata)
    return parsed.magic_word, parsed.seconds, parsed.microsecond


# this function checks the file size, and if it is nearing MAX_FILE_SIZE, it closes it and starts a new file
def run_file_manager(file):
    file_size = file.tell()
    if abs(file_size - MAX_FILE_SIZE) < 500000:
        close_file(file)
        return open_file()
    return file


class Menu:
    def __init__(self, master):
        self.master = master
        self.canvas1 = tk.Canvas(self.master, width=400, height=300)
        self.canvas1.pack()
        self.entry1 = tk.Entry(self.master)
        self.canvas1.create_window(200, 140, window=self.entry1)
        self.button1 = tk.Button(text='Save comment', command=self.set_comment)
        self.button1.pack(side=tk.TOP)

        self.value = None
        self.canvas1.create_window(200, 180, window=self.button1)

    def set_comment(self):
        is_empty_ok = True  # on default set to true to enable good input comments
        self.value = self.entry1.get()  # get the text from text box
        # if the comment length is 0, check if we want to proceed with empty comment.
        if len(self.value) == 0:
            proceed = messagebox.askquestion(title="Empty message", message="No comment, do you want to proceed?")
            if proceed == "no":  # messagebox.askquestion returns string
                is_empty_ok = False  # do not receive empty comment.
        if len(self.value) < comment_size and is_empty_ok:
            label1 = tk.Label(self.master, text=self.value)
            self.canvas1.create_window(200, 230, window=label1)
            self.canvas1.destroy()
            self.entry1.destroy()
            self.master.destroy()
        elif len(self.value) > 32:
            messagebox.showwarning(message="Comment is too long, Comment must be 32 bytes or less.")
            print("comment is too long")


# This function opens the comment gui and returns the value
def entry_box():
    root = tk.Tk()
    menu = Menu(root)
    root.mainloop()
    return menu.value


"""
if __name__ == '__main__':
    # Note: do not delete main and these function calls.
    build_file_meta()
    build_frame_meta()
"""
