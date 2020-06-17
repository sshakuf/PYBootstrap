import logging
import os
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
# import mmap
# import time
# import struct

from logging.handlers import RotatingFileHandler
import numpy as np
import struct


def ExportRefVectorToBinary(ref_vect, pathname, filename):
    if sys.platform == "linux":
        file_path = "/ext_ssd/PrjGL/radar-control/SystemTests/Calibration/REF_files/"
    else:
        file_path = "c:/temp/"

    root = Tk()
    root.path = filedialog.askdirectory(initialdir=file_path, title="Select destination directory")
    if root.path != "":
        fid_I_out = open(root.path + '/REF_I' + filename[8:-4] + '.bin', 'wb')
        fid_Q_out = open(root.path + '/REF_Q' + filename[8:-4] + '.bin', 'wb')
        data_I = np.real(ref_vect).astype(dtype='float32')
        data_Q = np.imag(ref_vect).astype(dtype='float32')
        fid_I_out.write(data_I.tobytes())
        fid_Q_out.write(data_Q.tobytes())
        fid_I_out.close()
        fid_Q_out.close()
        print(f"REF files saved to {root.path}\n")
        resp = messagebox.askyesno(title="Default REFs", message="Save the files also as default?")
        if resp:
            fid_I_out = open(root.path + '/REF_I.bin', 'wb')
            fid_Q_out = open(root.path + '/REF_Q.bin', 'wb')
            fid_I_out.write(data_I.tobytes())
            fid_Q_out.write(data_Q.tobytes())
            fid_I_out.close()
            fid_Q_out.close()
        root.destroy()


def import_ref(path: str):
    #  get directory path as string and import binary REF (CAL vector) files.
    #  return REF as complex float ndarray

    filename_I = f"{path}REF_I.bin"
    filename_Q = f"{path}REF_Q.bin"
    f_I = open(filename_I, "rb")
    f_Q = open(filename_Q, "rb")

    data_I = np.fromfile(f_I, dtype=np.float32)
    data_Q = np.fromfile(f_Q, dtype=np.float32)

    ref = np.ndarray([48, ], dtype='complex')
    ref.real = data_I
    ref.imag = data_Q
    return ref


def import_ref_2(path: str, serial_num: str):
    #  get directory path as string and import binary REF (CAL vector) files.
    #  return REF as complex float ndarray

    filename_I = f"{path}REF_I_{serial_num}.bin"
    filename_Q = f"{path}REF_Q_{serial_num}.bin"
    f_I = open(filename_I, "rb")
    f_Q = open(filename_Q, "rb")

    data_I = np.fromfile(f_I, dtype=np.float32)
    data_Q = np.fromfile(f_Q, dtype=np.float32)

    ref = np.ndarray([48, ], dtype='complex')
    ref.real = data_I
    ref.imag = data_Q
    return ref



def import_bfm(path: str):
    #  get directory path as string and import binary DBF files.
    #  return beamforming matrix (bfm) as ndarray

    filename_I = f"{path}DBF_I.bin"
    filename_Q = f"{path}DBF_Q.bin"
    f_I = open(filename_I, "rb")
    f_Q = open(filename_Q, "rb")

    data_I = np.fromfile(f_I, dtype=np.int16)
    data_Q = np.fromfile(f_Q, dtype=np.int16)

    bfm = np.ndarray([48*64], dtype='complex')
    bfm.real = data_I.astype(dtype=np.float32)
    bfm.imag = data_Q.astype(dtype=np.float32)
    bfm = bfm.reshape([64, 48]).transpose()
    return bfm


# def create_temp_param_file():
#     mode = 3
#     num_beams = 8
#     width = 8192
#
#     fmt = b"BBI"
#     temp_params = struct.pack(fmt, mode, num_beams, width)
#
#     f = open("/tmp/radar_data", "r+b")
#
#     # memory-map the file, size 0 means whole file
#     mm = mmap.mmap(f.fileno(), 0)
#     mm.seek(0)
#     mm.write(temp_params)
#     mm.seek(0)
#
#     return f
#
#
# def update_temp_param_file(file_, mode, num_beams):
#     width = 8192
#     fmt = b"BBI"
#     temp_params = struct.pack(fmt, mode, num_beams, width)
#
#     f = open("/tmp/radar_data", "r+b")
#
#     # memory-map the file, size 0 means whole file
#     mm = mmap.mmap(f.fileno(), 0)
#     mm.seek(0)
#     mm.write(temp_params)
#     mm.seek(0)
#
#     return
#
#
# def get_temp_param_file(file_):
#     mm = mmap.mmap(file_.fileno(), 0)
#     mm.seek(0)
#
#     fmt = b"BBI"
#     mode, num_beams, width = struct.unpack(fmt, mm.read())
#
#     return mode, num_beams, width
