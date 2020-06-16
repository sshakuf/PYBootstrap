import imports
from tools.Engine import *
import logging
import Logger
from Modules.RadarLogic import RadarLogic
from tools.EngineComponent import EngineComponent
#
Logger.SetupLogger()

logger = logging.getLogger(__name__)


def show_menu(menu_item, param):
    if menu_item is None:
        print("\r")
        print("Synthesizer control interface")
        print("=============================")
        print("Select option:")
        print("f - set frequency [MHz]")
        print("b - set bandwidth [MHz]")
        print("r - set ramp type")
        print("t - set chirp time [usec]")
        print("T - set frame duration [usec]")
        print("S - sampling window width [usec] ")
        print("\r")
        print("v to view current parameters, q to quit the program")
    elif menu_item == 'f':
        val = input("Enter start frequency (in MHz):")
        if val.isnumeric():
            if 76000 <= int(val) <= 80000:
                print(f"Setting frequency to {val} MHz")
                param.frequency = int(val)
            else:
                print("frequency out of range")
    # elif menu_item == 'b':
    #     val = input("Enter chirp bandwidth (in MHz):")
    #     if val.isnumeric():
    #         if 0 <= int(val) <= 1000:
    #             print(f"Setting bandwidth to {val} MHz")
    #             bw = int(val)
    #         else:
    #             print("bandwidth out of range")
    # elif menu_item == 'r':
    #     val = input("Select ramp type (0-Sawtooth, 1-Triangle):")
    #     if val == "0":
    #         ramp_type = RampType.Sawtooth
    #     elif val == "1":
    #         ramp_type = RampType.Triangle
    #     else:
    #         print("Invalid ramp type")
    # elif menu_item == 't':
    #     val = input("Enter chirp length (in usec):")
    #     if val.isnumeric():
    #         if 10 <= int(val) <= 100000:
    #             print(f"Setting chirp length to {val} usec")
    #             chirp_len_usec = int(val)
    #         else:
    #             print("chirp length out of range")
    # elif menu_item == 'T':
    #     val = input("Enter frame length (in usec):")
    #     if val.isnumeric():
    #         if 100 <= int(val) <= 1000000:
    #             print(f"Setting frame length to {val} usec")
    #             frame_len_usec = int(val)
    #         else:
    #             print("frame length out of range")
    #
    #         if frame_len_usec < chirp_len_usec:
    #             print("WARNING: frame is shorter than chirp length!")
    # elif menu_item == 'S':
    #     val = input("Enter sampling window length (in usec):")
    #     if val.isnumeric():
    #         if 100 <= int(val) <= 1000000:
    #             print(f"Setting sampling window length to {val} usec")
    #             adc_win_usec = int(val)
    #         else:
    #             print("sampling window length out of range")
    #
    #         if adc_win_usec > frame_len_usec:
    #             print("WARNING: sampling window is longer than frame!")
    elif menu_item == 'v':
        show_params()
        show_menu(None, param)


# def show_params():
#     global freq, bw, chirp_len_usec, frame_len_usec, adc_win_usec
#
#     print("\r")
#     print("Current parameters:")
#     print(f"\t frequency: {freq}")
#     print(f"\t bandwidth: {bw}")
#     print(f"\t ramp type: {ramp_type.name}")
#     print(f"\t frame length: {frame_len_usec} usec")
#     print(f"\t chirp length: {chirp_len_usec} usec")
#     print(f"\t sampling window: {adc_win_usec} usec")



if __name__ == "__main__":
    logger.info("________Start_________Main_________")
    # TODO: Get file name from args    https://www.geeksforgeeks.org/command-line-arguments-in-python/?ref=leftbar-rightbar
    engine = GetEngine()
    engine.LoadConfiguration(imports.currentdir+"/configurations/conf1.xml")

    # engine.eventBroker.subscribeEvent("PropertyBeforeChange", param_change)
    # print(engine.objectRepository.getInstancesByType(EngineComponent))
    engine.Initialize()
    engine.Start()

    menu_options = {"f", "b", "t", "T", "S", "q", "r", "v"}

    val = None

    while val != "q":
        val = input("Selected option?")
        if val == 'q':
            break
        if "=" in val:
            key = val.split("=")[0].strip()

            value = val.split("=")[1].strip()
            if key in engine.props:
                engine.props[key] = int(value)  # TODO: PLEASE NOT! we must cast the right type before assignment!
        if "?" in val:
            key = val.split("?")[0].strip()
            if key in engine.props:
                print(key + ": " + str(engine.props[key]))

        val = None
        engine.Run()

    engine.Stop()
    print("Bye! thanks for using me")
    # engine.objectRepository.instances.eventBroker.fireEvent('Test')
    # engine.objectRepository.instances.eventBroker.fireEvent('Test2')

    # test the usage
    # print(engine.props.frequency)
    # engine.props.rx_FrameGen_N_Samples = 112
    # engine.props.frequency = 32132
    # print(engine.props.frequency)

    # engine.props["s"] = 11
    # print(engine.props.get("s"))
    # engine.props.eventBroker.subscribeEvent("p", pp)
    # print(engine.props.eventBroker.fireEvent("p"))
    # print("S property: " + str(engine.props["s"]))

    x = 5
    x = x+3
