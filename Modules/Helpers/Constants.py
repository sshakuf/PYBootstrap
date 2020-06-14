# physical and mathematical convenience constants

C = 299792458  # speed of light
PI = 3.141592653589793
time2rng = C / 2
rng2time = 2 / C
dx = 4.2e-3  # Rx element spacing

class RxVgaGain:
    db_2 = 0
    db_4 = 1
    db_10 = 2
    db_16 = 3
    db_22 = 4


class GlobalConstants:
    system_clk = 1.00E+08


class RxConstants:
    rx_sync_delay = 0
    hilbert_q_multiplier = 1.28
    latency_fir1 = 0
    latency_fir2 = 80
    latency_fir3 = 0
    latency_fir4 = 0
    latency_fir5 = 0
    latency_fir6 = 0
    rx_dac_bias = [0, 0, 0, 0, 0, 0, 0]
    RxVgaGain = RxVgaGain()


class TxConstants:
    tx_sync_delay = 0

# class SyntConstants:
