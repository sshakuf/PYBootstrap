from Modules.Helpers.LogHelper import *
from Modules.V4L.V4L2MidLevel import *
from tools.EngineComponent import *
from tools.Engine import *
from Modules.Helpers.ReadWriteLock import *
from tools.DataStore import *
import time
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredDrawingArea
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import Circle

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
        }
        self.frame_ready = threading.Event()
        self.thread_event = threading.Event()
        self._v4l2_collector_thread = threading.Thread(target=read_data, args=(self, self.thread_event, 0.01,))
        self.drawer_thread = threading.Thread(target=draw, args=(self.frame_ready,))

    # TODO: Change frame size, file save yes/no, data output mode change.

    def onAfterInitialized(self):
        logger.info("Data collector initialized")

    def act_on_record_on(self):
        print("ACTING ON RECORD ON!!!")
        self.record = self.global_props.record_on
        if self.record:
            print("record is true, opening new file")
            self.file = open_file()
            comment = entry_box()  # lock released! "test0"  # build_file_meta will complete the comment with 0 to the desired size.
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
        self.drawer_thread.start()

    def onBeforeStop(self):
        self.global_props.record_on = False  # this will make the readers threads stop recording to files
        self.stopped = True


def read_data(collector, event, timeout):
    if collector.record:
        collector.file = open_file()
        comment = entry_box()  #lock released! "test0"  # build_file_meta will complete the comment with 0 to the desired size.
        write_to_file(collector.file, build_file_meta(time.time(), collector.v4l_mid.width, collector.v4l_mid.height,
                                                 collector.global_props.data_out_type, comment))
    # N = 8
    # M = 8192
    #
    # dr = 0.3
    # r = np.linspace(0, (M - 1) * dr, M).reshape([1, M])
    # az = np.linspace(-4, 4, N).reshape([N, 1])
    #
    # x = r * np.sin(az * np.pi / 180)
    # y = r * np.cos(az * np.pi / 180)
    #
    # z = np.zeros([N - 1, M - 1])
    # data = z

    frame_counter = 0
    timer_start = time.time()

    while True:  # to start animating the graph, uncomment this line
        collector.engine.reader_writer_lock.acquire_read()
        frame = collector.v4l_mid.get_frame().read()
        if not collector.frame_ready.isSet():
            collector.global_params.frame = frame
            print("TAKING FRAME")
            collector.frame_ready.set()
        collector.engine.reader_writer_lock.release_read()
        if event.isSet():  # if collector.record:
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
        time.sleep(0.1)


def draw(frame_event):
    frame = get_global_params().frame
    timer_start = time.time()
    while True:
        frame_event.wait()

        # collector.global_params.frame
        frame_event.clear()
        if time.time() - timer_start >= 1:
            print("DRAWING!")
            # print(str(frame_counter) + " Frames per second.")
            frame_counter = 0
            timer_start = time.time()


""" 
******************
configure graphs
******************
"""
def draw(frame_event):
    global_params = get_global_params()
    global_props = get_global_properties()
    N = global_properties.number_of_beams
    M = 8192

    decim_ratio = int(N / 2)
    num_pt = 1024
    I = np.zeros([num_pt, ])
    Q = np.zeros([num_pt, ])
    # f_data = np.zeros([8192, ])
    f_axis = np.linspace(0, 50 / decim_ratio, 8192)
    fmax = max(f_axis)

    # "RECORDING indicator"
    ada = AnchoredDrawingArea(20, 20, 0, 0, loc='upper left', pad=0., frameon=False)
    p = Circle((5, -2), 5, color='red')
    at = AnchoredText("REC ON", loc='upper left', borderpad=2, frameon=True)
    at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ada.da.add_artist(p)
    ada.da.add_artist(at)

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
    ax1.add_artist(ada)

    spect, = ax2.plot(f_axis, np.zeros([8192, ]), color='blue', linewidth=0.2)
    ax2.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('Magnitude [dB]')
    ax2.set_title(f"spectrum")
    ax2.set_ylim([20, 170])
    ax2.set_xlim([0, fmax])  # 12.5])
    ax2.grid(True)

    def animate(i):  # to start animating the graph, uncomment this line
        global N
        frame_event.wait()
        I, Q = mh.parse_frame(frame=global_params.frame, n_beams=N, mode=global_properties.data_out_type)  # read data
        frame_event.clear()
        iq_complex = np.array(I) + 1j * np.array(Q)
        f_data_db = mh.calc_fft2(iq_complex, return_db=True)

        line_I.set_ydata(I[:num_pt, 2])
        line_Q.set_ydata(Q[:num_pt, 2])
        spect.set_ydata(f_data_db[:, 2])
        txt.set_text(f"Frame {i}")

        return line_I, line_Q, txt, spect, ada

    anim = animation.FuncAnimation(fig, animate, interval=20, blit=True, repeat=False)
    plt.show()
