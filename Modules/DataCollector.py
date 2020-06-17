from Modules.Helpers.LogHelper import *
from Modules.V4L.V4L2MidLevel import *
from tools.EngineComponent import *
from tools.Engine import *
from Modules.Helpers.ReadWriteLock import *
from tools.DataStore import *
import time
import matplotlib.animation as animation
import matplotlib.pyplot as plt
#from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea
#from matplotlib.offsetbox import AnchoredText
#from matplotlib.patches import Circle

logger = logging.getLogger(__name__)


class DataCollector(EngineComponent):
    def __init__(self):
        super().__init__()
        self.v4l_mid = None
        self.engine = None
        self.file = None
        self.prop_handler = None
        self.global_props = None
        self.global_params = None
        self.record = False
        self._v4l2_collector_thread = False
        self.stopped = False
        self.thread_event = None
        self.frame_ready = None
        self.drawer_thread = None

    def onBeforeInitialized(self):
        self.engine = GetEngine()
        self.global_props = self.engine.props
        self.global_params = get_global_params()

        # ### V4L2 related init ### #
        self.v4l_mid = V4L2MidLevel()
        self.v4l_mid.connect()
        self.v4l_mid.init()

        # ### events and properties related init ### #
        self.engine.eventBroker.subscribeEvent("PropertyChanged", self.property_changed)
        self.engine.eventBroker.subscribeEvent("PropertyBeforeChange", self.property_before_changed)
        self.prop_handler = {
            # "frequency": self.,
            # "new_dbf_ready": self.act_on_dbf,
            # "frame_len_usec": self.config_frame,
            # "number_of_beams:": self.act_on_num_beams, TODO: do not forget this prop for data collector!
            # "bandwidth": ,
            # "chirp_duration": self.func,
            # "decimation_ratio": self.act_on_decimation_ratio,
            # "debug_output_interface": self.,
            # "num_samples_out": self.config_decimator,
            # "num_adc_samples": self.act_on_adc_samples,
            "data_out_type": self.act_on_data_out,
            # "run_mode": self.act_on_run_mode,
            # "beam_spacing": self.func,
            # "beam_stack_center": self.func,
            "record_on": self.act_on_record_on,
            "draw_on": self.act_on_draw,
        }
        self.frame_ready = threading.Event()
        self.thread_event = threading.Event()
        self._v4l2_collector_thread = threading.Thread(target=read_data, args=(self, self.thread_event, 0.01,))
        self.drawer_thread = threading.Thread(target=draw, args=(self.frame_ready,))

    # TODO: Change frame size, file save yes/no, data output mode change.

    def act_on_draw(self):
        if self.global_props.draw_on:
            self.drawer_thread.start()
        # kill or stop the thread when draw_on = false

    def onAfterInitialized(self):
        logger.info("Data collector initialized")

    def act_on_record_on(self):
        print("ACTING ON RECORD ON!!!")
        self.record = self.global_props.record_on
        if self.record:
            print("record is true, opening new file")
            self.file = open_file()
            comment = "test"# entry_box()  # lock released! "test0"  # build_file_meta will complete the comment with 0 to the desired size.
            write_to_file(self.file, build_file_meta(time.time(), self.v4l_mid.width, self.v4l_mid.height,
                                                     self.global_props.data_out_type, comment))
            self.thread_event.set()
        else:
            if self.file is not None:
                print("file is not none and we closing it")
                self.thread_event.clear()
                close_file(self.file)
                self.file = None
            else:
                print("file is none and false was sent")

    # TODO: TEST THIS FUNCTION!!!!
    def act_on_data_out(self):
        if self.file is not None:
            close_file(self.file)
        self.file = open_file()
        comment = entry_box()  # "test0"  # build_file_meta will complete the comment with 0 to the desired size.
        write_to_file(self.file, build_file_meta(time.time(), self.v4l_mid.width, self.v4l_mid.height,
                                                 self.global_props.data_out_type, comment))

    def property_before_changed(self, prop):
        pass

    def property_changed(self, prop):
        try:
            print("PROP CHANEG!")
            func = self.prop_handler[prop["Name"]]
            func()
        except:
            logger.error("Data collector: Property is not supported or failed to set.")

    def onBeforeStart(self):
        self._v4l2_collector_thread.start()  # starting the thread, not the Function!
        # self.drawer_thread.start()

    def onBeforeStop(self):
        self.global_props.record_on = False  # this will make the readers threads stop recording to files
        self.stopped = True


def read_data(collector, event, timeout):
    if collector.record:
        collector.file = open_file()
        comment = entry_box()  #lock released! "test0"  # build_file_meta will complete the comment with 0 to the desired size.
        write_to_file(collector.file, build_file_meta(time.time(), collector.v4l_mid.width, collector.v4l_mid.height,
                                                 collector.global_props.data_out_type, comment))
    global_params = get_global_params()
    frame_counter = 0
    timer_start = time.time()

    while True:  # to start animating the graph, uncomment this line
        collector.engine.reader_writer_lock.acquire_read()
        frame = collector.v4l_mid.get_frame().read()
        if not collector.frame_ready.isSet():
            global_params.frame = frame
            # print("TAKING FRAME")
            collector.frame_ready.set()
        collector.engine.reader_writer_lock.release_read()
        if event.isSet() and collector.file is not None:  # if collector.record:
            write_to_file(collector.file, build_frame_meta(collector.v4l_mid.frame_sec, collector.v4l_mid.frame_usec))
            write_to_file(collector.file, collector.global_params.frame)

        frame_counter += 1
        if time.time() - timer_start >= 1:
            # print(str(frame_counter) + " Frames per second.")
            frame_counter = 0
            timer_start = time.time()
        if collector.file is not None:
            collector.file = run_file_manager(collector.file)
        if collector.stopped:
            break
        time.sleep(0.01)


# def draw(frame_event):
#     frame = get_global_params().frame
#     timer_start = time.time()
#     while True:
#         frame_event.wait()
#
#         # collector.global_params.frame
#         frame_event.clear()
#         if time.time() - timer_start >= 1:
#             print("DRAWING!")
#             # print(str(frame_counter) + " Frames per second.")
#             frame_counter = 0
#             timer_start = time.time()
#

""" 
******************
configure graphs
******************
"""
def draw(frame_event):
    global_params = get_global_params()
    global_props = get_global_properties()
    N = global_props.number_of_beams
    M = 8192

    decim_ratio = int(N / 2)
    num_pt = 1024
    I = np.zeros([num_pt, ])
    Q = np.zeros([num_pt, ])
    # f_data = np.zeros([8192, ])
    f_axis = np.linspace(0, 50 / decim_ratio, 8192)
    fmax = max(f_axis)

    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    ax1.clear()
    ax2.clear()

    line_I, = ax1.plot(I, color='blue', linewidth=0.2)
    line_Q, = ax1.plot(Q, color='red', linewidth=0.2)
    txt = plt.text(0, 0, "frame 0")
    ax1.set_xlabel('Samples')
    ax1.set_ylabel('Amplitude')
    ax1.set_title(f"debug data")
    # ax1.set_ylim([-2000, 2000])
    ax1.set_ylim([-10_000, 10_000])
    ax1.set_xlim([0, 512])  # num_pt])
    ax1.grid(True)

    spect, = ax2.plot(f_axis, np.zeros([8192, ]), color='blue', linewidth=0.2)
    ax2.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('Magnitude [dB]')
    ax2.set_title(f"spectrum")
    ax2.set_ylim([20, 170])
    ax2.set_xlim([0, fmax])  # 12.5])
    ax2.grid(True)

    def animate(i):  # to start animating the graph, uncomment this line
        frame_event.wait()
        I, Q = mh.parse_frame(frame=global_params.frame, n_beams=N, mode=global_props.data_out_type)  # read data
        # print("FRAME DRAWED!")
        frame_event.clear()
        iq_complex = np.array(I) + 1j * np.array(Q)
        f_data_db = mh.calc_fft2(iq_complex, return_db=True)

        line_I.set_ydata(I[:num_pt, 2])
        line_Q.set_ydata(Q[:num_pt, 2])
        spect.set_ydata(f_data_db[:, 2])
        txt.set_text(f"Frame {i}")

        return line_I, line_Q, txt, spect

    anim = animation.FuncAnimation(fig, animate, interval=20, blit=True, repeat=False)
    plt.show()
