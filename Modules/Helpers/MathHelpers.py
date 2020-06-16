import numpy as np
import scipy.constants as const
from scipy.signal import find_peaks, windows

from Modules.Helpers.eNums import *
from Modules.Helpers.Constants import *


class MathHelper:

    # @staticmethod
    def taylor_win(L=48, nbar=5, SLL=-35):

        B = 10**(-SLL / 20)
        A = np.log(B + np.sqrt(B**2 - 1)) / np.pi
        s2 = nbar**2 / (A**2 + (nbar - 0.5)**2)
        ma = np.arange(1, nbar)

        def calc_Fm(m):
            numer = (-1)**(m+1) * np.prod(1 - m**2/s2/(A**2 + (ma - 0.5)**2))
            denom = 2 * np.prod([1 - m**2/j**2 for j in ma if j != m])
            return numer/denom

        Fm = np.array([calc_Fm(m) for m in ma])

        def W(n):
            return 2 * np.sum(Fm * np.cos(2 * np.pi * ma * (n - L / 2 + 1 / 2) / L)) + 1

        w = np.array([W(n) for n in range(L)])

        # normalize (Note that this is not described in the original text)
        scale = 1.0 / W((L - 1) / 2)
        w *= scale
        return w

    # this can be calculated only once upon loading
    taylor_48_5_35 = taylor_win(L=48, nbar=5, SLL=-35)
    taylor_96_5_35 = taylor_win(L=96, nbar=5, SLL=-35)
    taylor_144_5_35 = taylor_win(L=144, nbar=5, SLL=-35)
    taylor_192_5_35 = taylor_win(L=192, nbar=5, SLL=-35)

    @staticmethod
    def normalize_vector(vector: np.ndarray):
        vector /= np.max(np.abs(vector))
        return vector

    @staticmethod
    def calc_STD(data: np.ndarray, dim: int = 0):
        if (dim + 1) > data.ndim:
            print("Incorrect dimensions")
        else:
            if data.ndim == 1:
                return np.std(data)
            else:
                return np.std(data, dim)

    @staticmethod
    def calc_mean(data: np.ndarray, dim: int = 0):
        if (dim + 1) > data.ndim:
            print("Incorrect dimensions")
        else:
            if data.ndim == 1:
                return np.mean(data)
            else:
                return np.mean(data, dim)

    @staticmethod
    def db(data: np.ndarray):
        return 20 * np.log10(np.abs(data) + 1e-16)

    @staticmethod
    def CalcSteerVect(num_channels: int = 48, beam_center: float = 0.0, sll: float = None, fc: float = 76.5e9,
                      dx: float = None):
        dx = 4.2e-3 if dx is None else GlobalConstants.dx  # element spacing
        wavelength = C / fc
        steer_vect = np.ones([num_channels, 1], dtype='complex')
        if sll is None:
            win = windows.boxcar(48)
        else:
            if num_channels == 48:
                win = MathHelper.taylor_48_5_35
            elif num_channels == 96:
                win = MathHelper.taylor_96_5_35
            elif num_channels == 144:
                win = MathHelper.taylor_144_5_35
            elif num_channels == 192:
                win = MathHelper.taylor_192_5_35
            else:
                print("Invalid number of channels")
                win = MathHelper.taylor_48_5_35

        if beam_center != 0:  # steer_vect is already initialized to complex-zeros, so no need to handle that
            dphi = 2 * np.pi * dx * np.sin(beam_center * np.pi / 180) / wavelength
            phi_vect = np.linspace(0, dphi * (num_channels - 1), num_channels)
        else:
            phi_vect = np.zeros([48, ])

        steer_vect = np.exp(1j * phi_vect) * win

        return steer_vect

    @staticmethod
    def CalculateDBF(num_channels: int = 48, num_beams: int = 16, stack_center: float = 0.0, spacing: float = 1.0,
                     sll: int = -35, fc: float = 76000):

        bfm = np.zeros([num_channels, 64], dtype='complex')

        angle_start = -(num_beams - 1) * spacing / 2
        angle_end = (num_beams - 1) * spacing / 2
        beam_centers = np.linspace(angle_start, angle_end, num_beams) + stack_center
        fc = fc * 1E6
        for i, bc in enumerate(beam_centers):
            bfm[:, i] = MathHelper.CalcSteerVect(num_channels, bc, sll, fc) * 16384.0

        return bfm

    @staticmethod
    def ApplyCalibration(steer_vect: np.ndarray([48, 1], dtype='complex'),
                         cal_vect: np.ndarray([48, 1], dtype='complex')):
        return np.multiply(steer_vect, cal_vect)

    @staticmethod
    def FindSpectralPeak(data: np.ndarray, threshold: float = 90):
        # peaks, _ = find_peaks(data.__abs__(), height=threshold)
        # max_peak = np.where(data == max(data[peaks]))
        max_peak_index = np.where(data.__abs__() == max(data.__abs__()))
        if max_peak_index is not None:
            return max_peak_index, data[max_peak_index]
        else:
            return -1, 0

    @staticmethod
    def IQ_correction(data: np.ndarray, fs: float = None):
        fs = GlobalConstants.fs if fs is None else fs
        # calculate scale factor
        scale_factor = np.max(np.abs(data.imag))
        I = data.real / scale_factor
        Q = data.imag / scale_factor

        # find frequency of test signal
        L = 4096
        S = np.abs(np.fft.fft(data, L))
        f_peak_indx = np.where(S[0:2048] == max(S[0: 2048]))
        f_peak = f_peak_indx[0] / L * fs
        T = 1.0 / f_peak  # period
        Tsamples = T * fs  # period in samples clock
        Nperiods = np.floor(len(data) / Tsamples)

        # bias esitmation
        biasI_est = np.mean(I[0:int(Tsamples * Nperiods)])
        biasQ_est = np.mean(Q[0:int(Tsamples * Nperiods)])

        # bias correction
        I1 = I - biasI_est
        Q1 = Q - biasQ_est

        # phase and amp offset estimation
        amp_offset_est = np.sqrt(2 * np.mean(I1 ** 2))
        sin_phi = 2 / amp_offset_est * np.mean(I1 * Q1)
        cos_phi = np.sqrt(1 - sin_phi ** 2)

        M = [[1 / amp_offset_est, 0],
             [-sin_phi / (amp_offset_est * cos_phi), 1 / cos_phi]]

        out = np.matmul(np.array(M), np.array([I1, Q1]))

        Iest = out[0, :] * scale_factor
        Qest = out[1, :] * scale_factor
        Ibias = biasI_est * scale_factor
        Qbias = biasQ_est * scale_factor
        phi = np.arcsin(sin_phi) * 180 / np.pi
        Iscale = amp_offset_est * scale_factor

        return Iest, Qest, Ibias, Qbias, Iscale, phi

    @staticmethod
    def Normalize_MPi_Pi(data: np.ndarray):
        ph = data
        ph[np.where(ph > np.pi)] -= 2 * np.pi
        ph[np.where(ph < -np.pi)] += 2 * np.pi

        return ph

    @staticmethod
    # parse_frame according to operating mode
    def parse_frame(frame, n_beams, mode):
        width = int(len(frame) / 8192 / 2)  # number of 8192 - 16bit vectors in the frame
        frame = np.frombuffer(frame, dtype=np.int16, count=8192 * width)
        n_beams = max(n_beams, 8)  # V4L does not support frames with less than 32 rows (corresponding to
        # 8 beams), therefore n_beams is selected as the maximum of the two

        if mode != 3:
            # arrange frame so that each line is one pixel (32 bit I + 32 bit Q)
            frame = frame.reshape(int(len(frame) / 4), 4)
            i_l = (frame[:, 0] & 0x3ffc) >> 2
            i_h = (frame[:, 1] & 0x3ffc) >> 2
            q_l = (frame[:, 2] & 0x3ffc) >> 2
            q_h = (frame[:, 3] & 0x3ffc) >> 2
            # I = i_l.astype('int32') + (i_h.astype('int32') << 12)  # size: 8192 * n_beams
            # Q = q_l.astype('int32') + (q_h.astype('int32') << 12)  # size: 8192 * n_beams
            I = ((256 * (i_l.astype('uint32') + (i_h.astype('uint32')) * 4096)).astype('int32')) / 256  # Leon's code
            Q = ((256 * (q_l.astype('uint32') + (q_h.astype('uint32')) * 4096)).astype('int32')) / 256  # Leon's code
            if mode == 0:  # DebugMemData
                # return every n-th pixel (n = num_beams)
                I_out = I[0:8192*n_beams:n_beams]  # n_beams]  # every "pixel" is duplicated n_beams times
                Q_out = Q[0:8192*n_beams:n_beams]  # :n_beams]  # every "pixel" is duplicated n_beams times
            else:
                # return a matrix of 8192 range-bins by n_beams
                I_out = I.reshape(8192, n_beams)
                Q_out = Q.reshape(8192, n_beams)

        elif mode == 3:  # RawAdcData
            I_out = np.zeros([256, 48], dtype='float')
            Q_out = I_out
            for kk in range(48):
                ch = 2 * kk if kk % 2 == 0 else 2 * kk - 1
                I_out[:, kk] = (frame[ch:32768:128] & 0x3ffc) >> 2

            I_out[np.where(I_out > 2047)] -= 4096

        return I_out, Q_out

    @staticmethod
    def calc_iq_fft(iq_data: np.ndarray, return_complex: bool = False, return_db: bool = True,
                    decim_ratio: int = 2):
        # calculate frequency response
        length = len(np.real(iq_data))
        ll = 4092
        if decim_ratio == 1:  # if sampling at ADC (or NCO / RAM) no need to scale decimation
            f_scale = np.linspace(0, (GlobalConstants.fs / 1e6), ll)
        else:
            f_scale = np.linspace(0, (GlobalConstants.fs / 1e6) / decim_ratio, ll)
        win = np.hanning(length)
        out = np.fft.fft(np.multiply(iq_data, win), ll)
        out = out + 1e-016
        if return_complex:
            iq_snr = out
        else:
            if return_db:
                iq_snr = 20 * np.log10(np.abs(out) + 1e-16)
            else:
                iq_snr = out.__abs__()

        iq_snr = iq_snr[:ll // 2]
        iq_freq = f_scale[:ll // 2]
        if not return_complex:
            iq_snr = iq_snr.astype(dtype=np.float32)

        iq_freq = iq_freq.astype(dtype=np.float32)
        return iq_freq, iq_snr

    @staticmethod
    def calc_fft2(iq_data: np.ndarray, return_complex: bool = False, return_db: bool = True):
        # calculate frequency response
        length = len(np.real(iq_data))
        ll = length
        # win = np.hanning(length)
        win = np.blackman(length)
        out = np.fft.fft((win * iq_data.T).T, ll, 0)
        # out = np.fft.fft(np.multiply(iq_data, win), ll)
        out = out + 1e-016
        if return_complex:
            spectrum = out
        else:
            if return_db:
                spectrum = 20 * np.log10(np.abs(out))  # + 1e-16)
            else:
                spectrum = out.__abs__()

        # spectrum = spectrum[:ll // 2]
        if not return_complex:
            spectrum = spectrum.astype(dtype=np.float32)

        return spectrum

    @staticmethod
    def fix_spherical_phase(L: int = 48, dx: float = GlobalConstants.dx,  r1: float = 1.8, r2: float = 1000, freq_MHz: float = 76000):
        wavelength = C/(freq_MHz * 1e6)
        x = np.linspace(-float(L)*dx/2, float(L)*dx/2, L)
        dr1 = np.sqrt(x**2+r1**2)-r1
        dr2 = np.sqrt(x**2+r2**2)-r2
        dp1 = 2*np.pi*dr1/wavelength
        dp2 = 2*np.pi*dr2/wavelength
        dp = dp2 - dp1

        correction = np.exp(1j * dp)
        return correction

# import matplotlib.pyplot as plt
#
# mh = MathHelper()
# res = mh.fix_spherical_phase(L=48, r1=1.8, r2=1000)
# patt1 = 20*np.log10(np.abs(np.fft.fftshift(np.fft.fft(np.ones([48, ]),1024))))
# patt2 = 20*np.log10(np.abs(np.fft.fftshift(np.fft.fft(res,1024))))
# plt.plot(np.arange(1024),patt1, np.arange(1024),patt2)
# plt.show()
# print(res)
