import numpy as np

from . import device
from enum import Enum
from .device import enum_conv, str_conv
import pylabframe.data

# helper definition
visa_property = device.VisaDevice.visa_property


class TektronixScope(device.VisaDevice):
    NUM_CHANNELS = 2

    class RunModes(Enum):
        CONTINUOUS = "RUNST"
        SINGLE = "SEQ"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize channels
        self.channels: list[TektronixScope.Channel] = [self.Channel(i+1, self) for i in range(self.NUM_CHANNELS)]

    # global scpi properties
    record_length = visa_property("horizontal:recordlength", read_conv=int, write_conv=int)
    run_mode = visa_property("acquire:stopafter", read_conv=RunModes, write_conv=enum_conv)
    run_state = visa_property("acquire:state", read_conv=bool, write_conv=int)
    x_scale = visa_property("horizontal:scale", read_conv=float, write_conv=float)

    # waveform transfer properties
    waveform_points = visa_property("wfmoutpre:nr_pt", read_only=True, read_conv=int)
    waveform_y_multiplier = visa_property("wfmoutpre:ymult", read_only=True, read_conv=float)
    waveform_y_offset_levels = visa_property("wfmoutpre:yoff", read_only=True, read_conv=float)
    waveform_y_zero = visa_property("wfmoutpre:yzero", read_only=True, read_conv=float)
    waveform_y_unit = visa_property("wfmoutpre:yunit", read_only=True, read_conv=str_conv)

    waveform_x_increment = visa_property("wfmoutpre:xincr", read_only=True, read_conv=float)
    waveform_x_zero = visa_property("wfmoutpre:xzero", read_only=True, read_conv=float)
    waveform_x_unit = visa_property("wfmoutpre:xunit", read_only=True, read_conv=str_conv)

    def initialize_waveform_transfer(self, channel_id, start=1, stop=None):
        self.visa_instr.write(f"data:source ch{channel_id}")
        self.visa_instr.write(f"data:start {start}")
        if stop is None:
            # default to full waveform
            stop = self.record_length
        self.visa_instr.write(f"data:stop {stop}")
        self.visa_instr.write("data:encdg fast")
        self.visa_instr.write("data:width 2")
        self.visa_instr.write("header 0")

    def do_waveform_transfer(self):
        wfm_raw = self.visa_instr.query_binary_values("curve?", datatype='h', is_big_endian=True, container=np.array)
        wfm_converted = (wfm_raw * self.waveform_y_multiplier) + self.waveform_y_zero
        time_axis = (np.arange(self.waveform_points) * self.waveform_x_increment) + self.waveform_x_zero

        metadata = {
            "x_unit": self.waveform_x_unit,
            "x_label": f"time",
            "y_unit": self.waveform_y_unit,
            "y_label": f"signal",
        }
        data_obj = pylabframe.data.NumericalData(wfm_converted, x_axis=time_axis, metadata=metadata)
        return data_obj

    def get_channel_waveform(self, channel_id, start=1, stop=None):
        self.initialize_waveform_transfer(channel_id, start=start, stop=stop)
        wfm = self.do_waveform_transfer()
        return wfm

    # channel properties
    class Channel:
        def __init__(self, channel, device):
            self.channel_id = channel
            self.query_params = {'channel_id':  channel}
            self.device: "TektronixScope" = device
            self.visa_instr = self.device.visa_instr

        y_scale = visa_property("ch{channel_id}:scale", read_conv=float, write_conv=float)
        offset = visa_property("ch{channel_id}:offset", read_conv=float, write_conv=float)
        termination = visa_property("ch{channel_id}:termination", read_conv=float, write_conv=float)
        inverted = visa_property("ch{channel_id}:invert", read_conv=bool, write_conv=int)

        mean = visa_property("measu:meas{channel_id}:mean", read_only=True, read_conv=float)

        def get_waveform(self, start=1, stop=None):
            return self.device.get_channel_waveform(self.channel_id, start=start, stop=stop)


