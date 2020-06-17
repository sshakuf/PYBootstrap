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
        logger.debug("init")
        self._v4l2_collector = None
        self._v4l2_collector_thread = None
        self.engine = None
        self.global_params = get_global_params()
        self.global_props = get_global_properties()

    def onBeforeInitialized(self):
        self.engine = GetEngine()

        self._v4l2_collector = self.engine.objectRepository.getInstancesById("V4L2Collector")
        self._v4l2_collector.Initialize()
        self._v4l2_collector_thread = threading.Thread(target=self._v4l2_collector.Start)
        return True

    def onAfterInitialized(self):
        pass

    def onBeforeStart(self):
        self._v4l2_collector_thread.start()  # starting the thread, not the Function!
        return True

    def onAfterStart(self):
        pass

    def onBeforeRun(self):
        logger.info(f"Data collector: Number of active threads - {threading.active_count()}")
        return True

    def onAfterRun(self):
        pass

    def onBeforeStop(self):
        self.global_props.record_on = False  # this will make the readers threads stop recording to files
        # self._v4l2_collector_thread.Stop()
        return True

    def onAfterStop(self):
        pass


class V4l2Collector:
    def __init__(self):
        self.v4l_mid = None
        self.engine = None
        self.file = None
        self.data_reader_lock = None
        self.prop_handler = None
        self.global_props = None
        self.global_params = None
        self.record = False

    def Initialize(self):
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

    # TODO: Change frame size, file save yes/no, data output mode change.

    def onAfterInitialized(self):
        logger.info("Data collector initialized")

    def act_on_record_on(self):
        self.record = self.global_props.record_on
        if self.record:
            self.file = open_file()
        else:
            if self.file is not None:
                close_file(self.file)

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
            func = self.prop_handler[prop["Name"]]
            func()
        except:
            logger.error("Rx: Property is not supported or failed to set.")

    def Start(self):
        if self.record:
            self.file = open_file()
            comment = entry_box()  # "test0"  # build_file_meta will complete the comment with 0 to the desired size.
            write_to_file(self.file, build_file_meta(time.time(), self.v4l_mid.width, self.v4l_mid.height,
                                                     self.global_props.data_out_type, comment))
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
            self.engine.reader_writer_lock.acquire_read()
            frame = self.v4l_mid.get_frame().read()
            self.engine.reader_writer_lock.release_read()
            if self.record:
                write_to_file(self.file, build_frame_meta(self.v4l_mid.frame_sec, self.v4l_mid.frame_usec))
                write_to_file(self.file, frame)

            frame_counter += 1
            if time.time() - timer_start >= 1:
                print(str(frame_counter) + " Frames per second.")
                frame_counter = 0
                timer_start = time.time()
            run_file_manager(self.file)







