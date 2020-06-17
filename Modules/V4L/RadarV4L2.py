""""
**********************************************************
    RadarV4L2.py

    Author: Gil Klar
    Date: 10/05/2020
    Description:
        This class implements the MIPI interface to the radar
        using the V4L2 driver. It is an intermediate implementation
        until a full CUDA-based processing will be implemented

**********************************************************
 NIART (ELTA) CONFIDENTIAL

 All Rights Reserved.

 * NOTICE:  All information contained herein is, and remains
 * the property of ELTA Systems Incorporated and its suppliers,
 * if any.  The intellectual and technical concepts contained
 * herein are proprietary to ELTA Systems and its suppliers and may be
 * covered by Israeli and Foreign Patents, patents in process,
 * and are protected by trade secret or copyright law.
 * Dissemination of this information or reproduction of this material
 * is strictly forbidden unless prior written permission is obtained
 * from ELTA Systems.
**********************************************************
"""

from v4l2 import *
import fcntl
import mmap
import select
import time
from HWModules.V4L import V4L2Enums


class RadarV4L2:
    def __init__(self):
        self.height = 32
        self.width = 8192
        self.vid = None

        print("request buffer")
        self.req = v4l2_requestbuffers()
        self.req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        self.req.memory = V4L2_MEMORY_MMAP  # V4L2_MEMORY_MMAP V4L2_MEMORY_USERPTR
        self.req.count = 1  # number of buffer frames
        self.buf_type = v4l2_buf_type(V4L2_BUF_TYPE_VIDEO_CAPTURE)

        self.frame_sec = 0
        self.frame_usec = 0

        print("\r")

    def cleanup(self):
        # todo: close video object
        pass

    def connect(self):
        self.vid = open('/dev/video0', 'rb+', buffering=0)
        # flag = fcntl.fcntl(self.vid.fileno(), fcntl.F_GETFL)
        # fcntl.fcntl(self.vid.fileno(), fcntl.F_SETFL, flag | os.O_NONBLOCK)

    def init(self, width=8192, height=32):
        self.width = width if width is not None else self.width
        self.height = height if height is not None else self.height
        print("FD: " + str(self.vid.fileno()))
        print(">> get device capabilities")
        cp = v4l2_capability()
        fcntl.ioctl(self.vid.fileno(), VIDIOC_QUERYCAP, cp)

        print("Driver:", "".join((chr(c) for c in cp.driver)))
        print("Name:", "".join((chr(c) for c in cp.card)))
        print("Is a video capture device?", bool(cp.capabilities & V4L2_CAP_VIDEO_CAPTURE))
        print("Supports read() call?", bool(cp.capabilities & V4L2_CAP_READWRITE))
        print("Supports streaming?", bool(cp.capabilities & V4L2_CAP_STREAMING))

        print("Configure v4l2 format")
        fmt = v4l2_format()
        fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        fmt.fmt.pix.width = self.width
        fmt.fmt.pix.height = self.height
        fmt.fmt.pix.pixelformat = V4L2Enums.V4L2_PIX_FMT_RG12
        fmt.fmt.pix.field = V4L2_FIELD_NONE
        fmt.fmt.pix.bytesperline = 0

        fcntl.ioctl(self.vid.fileno(), VIDIOC_S_FMT, fmt)  # set whatever default settings we got before

        print(">> init mmap capture")
        fcntl.ioctl(self.vid.fileno(), VIDIOC_REQBUFS, self.req)  # tell the driver that we want some buffers

        for ind in range(self.req.count):
            print(f"allocate MMAP buffer {ind}")
            buf = v4l2_buffer()
            buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            buf.memory = V4L2_MEMORY_MMAP
            buf.index = ind
            buf.reserved = 0
            buf.flags = 0
            # queue the buffer for capture
            ret = fcntl.ioctl(self.vid.fileno(), VIDIOC_QBUF, buf)  # prints 0 on success.
            if ret != 0:
                print("Could not allocate buffers!!!")
                return -1

        fcntl.ioctl(self.vid.fileno(), VIDIOC_QUERYBUF, buf)
        print(f"BEFORE: buffer flags: 0x{buf.flags: 04x}")
        if buf.flags & 1:
            print(f"BEFORE buffer state: MAPPED")
        if buf.flags & 2:
            print(f"BEFORE buffer state: QUEUED")
        if buf.flags & 4:
            print(f"BEFORE buffer state: DONE")

        print(">> Start streaming")
        buf_type = v4l2_buf_type(V4L2_BUF_TYPE_VIDEO_CAPTURE)
        print(fcntl.ioctl(self.vid.fileno(), VIDIOC_STREAMON, buf_type))
        print("\r")
        return 0

    def get_frame(self):
        dbuf = v4l2_buffer()
        dbuf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
        dbuf.memory = V4L2_MEMORY_MMAP

        frames = []

        for ind in range(1):  # self.req.count-2):

            # wait till buffer is ready for reading
            t0 = time.time()
            max_t = 5
            ready_to_read, ready_to_write, in_error = ([], [], [])
            while len(ready_to_read) == 0 and time.time() - t0 < max_t:
                ready_to_read, ready_to_write, in_error = select.select([self.vid.fileno()], [], [], max_t)

            # read (de-queue) buffer
            ret = fcntl.ioctl(self.vid.fileno(), VIDIOC_DQBUF, dbuf)  # get image from the driver queue
            self.frame_sec = dbuf.timestamp.secs
            self.frame_usec = dbuf.timestamp.usecs
            if ret == -1:
                print("DQBUF error")
                return -1

            # copy memory block
            mm = mmap.mmap(self.vid.fileno(), dbuf.length, mmap.MAP_SHARED, mmap.PROT_WRITE | mmap.PROT_READ,
                           offset=dbuf.m.offset)
            frames.append(mm)

            # re-queue the buffer for capture
            ret = fcntl.ioctl(self.vid.fileno(), VIDIOC_QBUF, dbuf)  # prints 0 on success.
            if ret != 0:
                print("Could not allocate buffers!!!")
                return -1

        # print(self.frame_sec)
        return frames[0]

    def disconnect(self):
        print(">> Stop streaming")
        fcntl.ioctl(self.vid.fileno(), VIDIOC_STREAMOFF, self.buf_type)
        self.vid.close()

#
# def get_epoch_time_shift():
#     current_time = time.time()
#     clk_time = time.clock_gettime(time.CLOCK_REALTIME)
#     uptime_ms = clk_time * 1000 + round(clk_time/time.time_ns())
#     epoch_ms = current_time * 1000 + round(current_time/1000)
#
#     return epoch_ms - uptime_ms
#
# # import v4l2
# #
# # timev = v4l2.timeval()
#
# bf = v4l2_buffer()
#
# # bf.timestamp.secs=2
# # bf.timestamp.usecs=3
# print(bf.timestamp.secs)
# print(bf.timestamp.usecs)
#
# while True:
#     print(time.time_ns()/1000000)
#     time.sleep(0.2)
#
