import imports
from tools.Engine import *
import logging
# import Logger
import streamlit as st
import threading
import matplotlib.pyplot as plt
from tools.DataStore import *
import time
from Modules.Helpers.MathHelpers import MathHelper as mh
import matplotlib.animation as animation
import threading
import pandas as pd
from Modules.RadarLogic import RadarLogic
from tools.EngineComponent import EngineComponent
##
# Logger.SetupLogger()

logger = logging.getLogger(__name__)



def draw(frame_event):
    global_params = get_global_params()
    global_props = get_global_properties()
    N = global_props.number_of_beams
    M = 8192

    dr = 150.0 / global_props.bandwidth
    r = 2 * np.linspace(0, (M - 1) * dr, M).reshape([1, M])
    step = 1
    az = np.linspace(-(N / 2) * step, (N / 2) * step, N).reshape([N, 1])
    # az = np.linspace(-4, 4, N).reshape([N, 1])

    x = r * np.sin(az * np.pi / 180)
    y = r * np.cos(az * np.pi / 180)

    z = np.zeros([N - 1, M - 1])
    data = z
    f_data_smooth = np.zeros([M, N], dtype='complex')

    # plot init
    min_val = 50
    max_val = 180
    fig, ax2 = plt.subplots(1, 1)
    quad1 = ax2.pcolorfast(x, y, z, cmap='jet', vmin=min_val, vmax=max_val)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.axis('equal')
    # ax2.set_ylim([0, Rmax])
    # ax2.set_xlim([-50, 50])
    fig.patch.set_facecolor('#E0E0E0')

    z = np.zeros([N - 1, M - 1])
    data = z
    the_plot = st.pyplot(plt)

    while True:
        # global N, min_val, max_val, last_tt, tt, dt, f_data_smooth
        # frame_event.wait()
        I, Q = mh.parse_frame(frame=global_params.frame, n_beams=N, mode=global_props.data_out_type)  # read data
        # print("FRAME DRAWED!")
        # frame_event.clear()
        if len(I) == 0:
            exit(1)

        # 16 msec
        iq_complex = np.array(I) + 1j*np.array(Q)
        f_data = mh.calc_fft2(iq_complex, return_complex=True)
        f_data_db = mh.db(f_data)

        min_val = np.min(f_data_db)
        max_val = np.max(f_data_db)

        data[0:N - 1, 0:M - 1] = f_data_db.T[:-1, :-1]
        quad1.set_array(data.ravel())

        the_plot.pyplot(plt)



if __name__ == "__main__":
    logger.info("________Start_________Main_________")
    global_params = get_global_params()
    global_props = get_global_properties()
    engine = GetEngine()
    engine.LoadConfiguration(imports.currentdir+"/configurations/conf1.xml")

    engine.Initialize()
    drawer_thread = threading.Thread(target=draw, args=(
    engine.objectRepository.getInstancesById("TheOneAndOnly_DataCollector").frame_ready,))
    engine.Start()

    # engine.reader_writer_lock.acquire_write()
    # if key in engine.props:
    #     engine.props[key] = int(value)  # TODO: PLEASE NOTE! we must cast the right type before assignment!
    #
    # engine.reader_writer_lock.release_write()
    global_prop_dict = vars(global_props)
    # for key in global_prop_dict:
    #     global_props[str(key)] = global_prop_dict[key]

    st.title('Radar map')
    tx_on = st.button('TX ON')
    st.write(f"TX state {tx_on}")

    N = 100
    M = 1024

    r = np.linspace(0, (M - 1) * 0.15, M).reshape([1, M])
    az = np.linspace(-10, 10, N).reshape([N, 1])

    x = r * np.sin(az * np.pi / 180)
    y = r * np.cos(az * np.pi / 180)

    z = np.zeros([N - 1, M - 1])
    data = z

    fig, ax2 = plt.subplots(1, 1)
    quad1 = ax2.pcolorfast(x, y, z, cmap='rainbow', vmin=0, vmax=5)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    # ax2.axis('equal')
    ax2.set_xlim([-50, 50])
    ax2.set_ylim([0, 170])
    fig.patch.set_facecolor('#E0E0E0')
    r = 0
    the_plot = st.pyplot(plt)

    # drawer_thread.start()
    while True:
        print("LOOPING")
        data[0:N - 1, 0:8191] = np.random.random([N - 1, M - 1])
        r = (r + 20) % 1200
        data[40:60, r:r + 10] = 5

        quad1.set_array(data.ravel())
        the_plot.pyplot(plt)

        # time.sleep(1)
        # engine.Run()
        # df = global_params.frame
        # st.write("Well")

    engine.Stop()
    print("Bye! thanks for using me")

