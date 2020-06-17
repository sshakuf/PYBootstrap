from Modules.Helpers.LogHelper import *
from Modules.V4L.V4L2MidLevel import *
from tools.EngineComponent import *
from tools.Engine import *
from Modules.Helpers.ReadWriteLock import *
from tools.DataStore import *
import time

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
        self.thread_event = threading.Event()
        self._v4l2_collector_thread = threading.Thread(target=read_data, args=(self, self.thread_event, 0.01,))

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
        collector.engine.reader_writer_lock.release_read()
        time.sleep(0.01)
        if event.isSet():  # if collector.record:
            write_to_file(collector.file, build_frame_meta(collector.v4l_mid.frame_sec, collector.v4l_mid.frame_usec))
            write_to_file(collector.file, frame)

        frame_counter += 1
        if time.time() - timer_start >= 1:
            print(str(frame_counter) + " Frames per second.")
            frame_counter = 0
            timer_start = time.time()
        if collector.file is not None:
            collector.file = run_file_manager(collector.file)

        if collector.stopped:
            break





