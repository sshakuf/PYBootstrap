""""
**********************************************************
    V4L2MidLevel.py

    Author: Nadav Yaakobi
    Date: 12/05/2020
    Description:
        This is a higher level (mid level) of the RadarV4L2 class.
        this class implements data frame parsing and saving the data files.
        It is an intermediate implementation
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


from Modules.V4L.RadarV4L2 import *
from datetime import datetime
from Modules.Helpers.MathHelpers import MathHelper as mh
from Modules.V4L.V4L2Enums import *
from Modules.Helpers.LogHelper import *
from Modules.Helpers.Enums.RxEnums import DataOutType
from tools.DataStore import *


# this whole class needs to be implemented at the rx mid lvl
class V4L2MidLevel(RadarV4L2):
    def __init__(self):
        super().__init__()

    # move this function to the RxMidLevel.
    def read_iq_data(self, num_samples: int = None, return_complex: bool = False, return_db: bool = True):
        num_samples = num_samples if num_samples is not None else 8192

        # length = 8192  # complex values (16bit + 16bit)
        # length = self.RxParam.rx_FrameGen_N_Samples//(2**self.RxParam.rx_DecimationRatio)
        # length = num_samples  # check why its here. it is not used.

        i_data, q_data = mh.parse_frame(self.get_frame(), n_beams=8, mode=DataOutType.DebugMemData)
        i_data = i_data.astype(dtype=np.float32)
        q_data = q_data.astype(dtype=np.float32)
        iq_data = np.array(i_data, dtype=complex)
        iq_data.real = i_data
        iq_data.imag = q_data
        iq_freq, iq_snr = mh.calc_iq_fft(iq_data, return_complex, return_db)
        return iq_data, iq_freq, iq_snr

    def get_frame(self):
        return super().get_frame()  # call the low level get_frame


# # *****************
# # usage example:
# # *****************
#
# if __name__ == '__main__':
#     params.v4l = V4L2MidLevel()
#     params.v4l.connect()
#     params.v4l.init()
#     file = open_file()
#     comment = "test0"  # build_file_meta will complete the comment with 0 to the desired size.
#     write_to_file(file, build_file_meta(time.time(), params.v4l.width, params.v4l.height,
#                                         DataOutType.BeamFormerData, comment))
#     # v4l2_mid_rx.open_file()  # _file='/ext_ssd/PrjGL/logs/raw.bin')
#
#     num_pt = 8192
#     I = np.zeros([num_pt, ])
#     Q = np.zeros([num_pt, ])
#     # f_data = np.zeros([8192, ])
#     f_axis = np.linspace(0, 25, 8192)
#
#     fig = plt.figure()
#     ax1 = fig.add_subplot(2, 1, 1)
#     ax2 = fig.add_subplot(2, 1, 2)
#     ax1.clear()
#     ax2.clear()
#
#     line_I, = ax1.plot(I, color='blue', linewidth=0.2)
#     line_Q, = ax1.plot(Q, color='red', linewidth=0.2)
#     txt = plt.text(100, 2000, "frame 0")
#     ax1.set_xlabel('Samples')
#     ax1.set_ylabel('Amplitude')
#     ax1.set_title(f"debug data")
#     ax1.set_ylim([-2000, 2000])
#     ax1.set_xlim([0, num_pt])
#     ax1.grid(True)
#
#     spect, = ax2.plot(f_axis, np.zeros([8192, ]), color='blue', linewidth=0.2)
#     ax2.set_xlabel('Frequency [MHz]')
#     ax2.set_ylabel('Magnitude [dB]')
#     ax2.set_title(f"spectrum")
#     ax2.set_ylim([0, 150])
#     ax2.set_xlim([0, 12.5])
#     ax2.grid(True)
#
#     def animate(i):  # to start animating the graph, uncomment this line
#         # Notice: get_frame() can save frames to log file. default is False
#         frame = v4l2_mid_rx.get_frame().read()
#         write_to_file(file, build_frame_meta(v4l2_mid_rx.frame_sec, v4l2_mid_rx.frame_usec))
#         write_to_file(file, frame)
#         I, Q = mh.parse_frame(frame, n_beams=8, mode=1)  # mode=1: Beamform out
#         iq_complex = np.array(I) + 1j * np.array(Q)
#         f_data_db = mh.calc_fft2(iq_complex, return_db=True)
#         line_I.set_ydata(I[:, 0])
#         line_Q.set_ydata(Q[:, 0])
#         spect.set_ydata(f_data_db[:, 0])
#         txt.set_text(f"Frame {i}")
#         return line_I, line_Q, txt, spect
#
#
#     # for fast drawings set the blit flag to True
#     ani = animation.FuncAnimation(fig, animate, interval=20, blit=True)  # to stop animating the graph, comment line.
#     plt.show()  # to stop animating the graph, comment this line.

