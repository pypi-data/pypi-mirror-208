import json

from moku import Moku
from moku.exceptions import MokuException, StreamException
from moku.instruments._stream import StreamInstrument
from moku.utilities import find_moku_by_serial, validate_range


class LockInAmp(Moku, StreamInstrument):
    """
    LockInAmp instrument object.

    The LockInAmp instrument supports dual-phase
    demodulation (XY/Rθ) with integrated  oscilloscope
    and data logger

    Read more at https://apis.liquidinstruments.com/reference/lia

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 8
        self.operation_group = "lockinamp"

        if multi_instrument is None:
            self.slot = 1
            if not any([ip, serial]):
                raise MokuException("IP (or) Serial is required")
            if serial:
                ip = find_moku_by_serial(serial)

            super().__init__(ip=ip, force_connect=force_connect,
                             ignore_busy=ignore_busy,
                             persist_state=persist_state,
                             connect_timeout=connect_timeout,
                             read_timeout=read_timeout,
                             **kwargs)
            self.upload_bitstream(f'01-000')
            self.upload_bitstream(f'01-{self.id:03}-00')
        else:
            self.platform_id = multi_instrument.platform_id
            self.slot = slot
            self.session = multi_instrument.session
            self.firmware_version = multi_instrument.firmware_version
            self.hardware = multi_instrument.hardware
            self.bitstreams = multi_instrument.bitstreams
            self.upload_bitstream(
                f'{self.platform_id:02}-{self.id:03}-{self.slot - 1:02}')
            self.session.get(f"slot{self.slot}", self.operation_group)

        StreamInstrument.__init__(self)

    @classmethod
    def for_slot(cls, slot, multi_instrument):
        return cls(slot=slot, multi_instrument=multi_instrument)

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_frontend(
            self,
            channel,
            coupling,
            impedance,
            attenuation,
            strict=True):
        """
        set_frontend.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type coupling: `string` ['AC', 'DC']
        :param coupling: Input Coupling

        :type impedance: `string` ['1MOhm', '50Ohm']
        :param impedance: Impedance

        :type attenuation: `string` ['-14dB', '-20dB', '-40dB', '0dB', '14dB', '20dB', '40dB']
        :param attenuation: Input attenuation.

        """
        operation = "set_frontend"
        params = dict(
            strict=strict, channel=channel, coupling=validate_range(
                coupling, [
                    'AC', 'DC']), impedance=validate_range(
                impedance, [
                    '1MOhm', '50Ohm']), attenuation=validate_range(
                        attenuation, [
                            '-14dB', '-20dB', '-40dB', '0dB', '14dB', '20dB', '40dB']), )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_frontend(self, channel):
        """
        get_frontend.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_frontend"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_demodulation(self, mode, frequency=1000000, phase=0, strict=True):
        """
        set_demodulation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['Internal', 'External', 'ExternalPLL', 'None']
        :param mode: Demodulation mode

        :type frequency: `number`
        :param frequency: Demodulation signal frequency

        :type phase: `number`
        :param phase: Demodulation signal phase

        """
        operation = "set_demodulation"
        params = dict(
            strict=strict,
            mode=validate_range(
                mode, ['Internal', 'External', 'ExternalPLL', 'None']),
            frequency=frequency,
            phase=phase,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_demodulation(self):
        """
        get_demodulation.
        """
        operation = "get_demodulation"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_filter(self, corner_frequency, slope="Slope6dB", strict=True):
        """
        set_filter.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type corner_frequency: `number`
        :param corner_frequency: Corner frequency of low-pass filter

        :type slope: `string`
        :param slope: Low-pass filter slope

        """
        operation = "set_filter"
        params = dict(
            strict=strict,
            corner_frequency=corner_frequency,
            slope=slope,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_filter(self):
        """
        get_filter.
        """
        operation = "get_filter"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_monitor(self, monitor_channel, source, strict=True):
        """
        set_monitor.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type monitor_channel: `integer`
        :param monitor_channel: Monitor channel

        :type source: `string` ['None', 'Input1', 'ISignal', 'QSignal', 'MainOutput', 'AuxOutput', 'Input2', 'Demod']
        :param source: Monitor channel source.

        """
        operation = "set_monitor"
        params = dict(strict=strict,
                      monitor_channel=monitor_channel,
                      source=validate_range(source,
                                            ['None',
                                             'Input1',
                                             'ISignal',
                                             'QSignal',
                                             'MainOutput',
                                             'AuxOutput',
                                             'Input2',
                                             'Demod']),
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_outputs(self):
        """
        get_outputs.
        """
        operation = "get_outputs"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_outputs(self, main, aux, main_offset=0, aux_offset=0, strict=True):
        """
        set_outputs.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type main: `string` ['X', 'Y', 'R', 'Theta', 'Offset', 'None']
        :param main: Configure main output.

        :type aux: `string` ['Y', 'Theta', 'Demod', 'Aux', 'Offset', 'None']
        :param aux: Configure aux output.

        :type main_offset: `number`
        :param main_offset: Main output offset

        :type aux_offset: `number`
        :param aux_offset: Auxilary output offset

        """
        operation = "set_outputs"
        params = dict(
            strict=strict,
            main=validate_range(
                main, ['X', 'Y', 'R', 'Theta', 'Offset', 'None']),
            aux=validate_range(
                aux, ['Y', 'Theta', 'Demod', 'Aux', 'Offset', 'None']),
            main_offset=main_offset,
            aux_offset=aux_offset,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_aux_output(self, frequency, amplitude, strict=True):
        """
        set_aux_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type frequency: `number`
        :param frequency: Aux Oscillator frequency

        :type amplitude: `number`
        :param amplitude: Aux Oscillator amplitude

        """
        operation = "set_aux_output"
        params = dict(
            strict=strict,
            frequency=frequency,
            amplitude=amplitude,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_aux_output(self):
        """
        get_aux_output.
        """
        operation = "get_aux_output"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_gain(
            self,
            main,
            aux,
            main_invert=False,
            aux_invert=False,
            main_gain_range="0dB",
            aux_gain_range="0dB",
            strict=True):
        """
        set_gain.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type main: `number`
        :param main: Main channel gain

        :type aux: `number`
        :param aux: Auxilary channel gain

        :type main_invert: `boolean`
        :param main_invert: Invert main channel gain

        :type aux_invert: `boolean`
        :param aux_invert: Invert auxilary channel gain

        :type main_gain_range: `string`
        :param main_gain_range: Main Gain Range(Only on Pro)

        :type aux_gain_range: `string`
        :param aux_gain_range: Aux Gain Range(Only on Pro)

        """
        operation = "set_gain"
        params = dict(
            strict=strict,
            main=main,
            aux=aux,
            main_invert=main_invert,
            aux_invert=aux_invert,
            main_gain_range=main_gain_range,
            aux_gain_range=aux_gain_range,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_gain(self):
        """
        get_gain.
        """
        operation = "get_gain"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_polar_mode(self, range, strict=True):
        """
        set_polar_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type range: `string` ['2Vpp', '7.5mVpp', '25uVpp']
        :param range: Polar range.

        """
        operation = "set_polar_mode"
        params = dict(
            strict=strict,
            range=validate_range(range, ['2Vpp', '7.5mVpp', '25uVpp']),
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_polar_theta_range(self):
        """
        get_polar_theta_range.
        """
        operation = "get_polar_theta_range"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_pll(
            self,
            auto_acquire=True,
            frequency=None,
            frequency_multiplier=1,
            bandwidth="1kHz",
            strict=True):
        """
        set_pll.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type auto_acquire: `boolean`
        :param auto_acquire: Auto acquires frequency

        :type frequency: `number`
        :param frequency: External PLL frequency(when auto_acquire is false)

        :type frequency_multiplier: `number`
        :param frequency_multiplier: Frequency multiplier

        :type bandwidth: `string` ['1Hz', '10Hz', '100Hz', '1kHz', '10kHz', '100kHz', '1MHz']
        :param bandwidth: Bandwidth.

        """
        operation = "set_pll"
        params = dict(strict=strict,
                      auto_acquire=auto_acquire,
                      frequency=frequency,
                      frequency_multiplier=frequency_multiplier,
                      bandwidth=validate_range(bandwidth,
                                               ['1Hz',
                                                '10Hz',
                                                '100Hz',
                                                '1kHz',
                                                '10kHz',
                                                '100kHz',
                                                '1MHz']),
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_pll(self):
        """
        get_pll.
        """
        operation = "get_pll"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def use_pid(self, channel, strict=True):
        """
        use_pid.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `string` ['Off', 'Main', 'Aux']
        :param channel: Target LIA channel.

        """
        operation = "use_pid"
        params = dict(
            strict=strict,
            channel=validate_range(channel, ['Off', 'Main', 'Aux']),
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_by_frequency(
            self,
            prop_gain=None,
            int_crossover=None,
            diff_crossover=None,
            int_saturation=None,
            diff_saturation=None,
            strict=True):
        """
        set_by_frequency.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type prop_gain: `number` [-60dB, 60dB]
        :param prop_gain: Proportional gain factor

        :type int_crossover: `number` [31.25e-3Hz, 312.5e3Hz]
        :param int_crossover: Integrator crossover frequency

        :type diff_crossover: `number` [312.5e-3Hz, 3.125e6Hz]
        :param diff_crossover: Differentiator crossover frequency

        :type int_saturation: `number` [-60dB, 60dB]
        :param int_saturation: Integrator gain saturation

        :type diff_saturation: `number` [-60dB, 60dB]
        :param diff_saturation: Differentiator gain saturation

        """
        operation = "set_by_frequency"
        params = dict(
            strict=strict,
            prop_gain=prop_gain,
            int_crossover=int_crossover,
            diff_crossover=diff_crossover,
            int_saturation=int_saturation,
            diff_saturation=diff_saturation,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def pll_reacquire(self):
        """
        pll_reacquire.
        """
        operation = "pll_reacquire"
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_trigger(
            self,
            type="Edge",
            level=0,
            mode="Auto",
            edge="Rising",
            polarity="Positive",
            width=0.0001,
            width_condition="LessThan",
            nth_event=1,
            holdoff=0,
            auto_sensitivity=True,
            noise_reject=False,
            hf_reject=False,
            source="ProbeA",
            strict=True):
        """
        set_trigger.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type type: `string` ['Edge', 'Pulse']
        :param type: Trigger type

        :type level: `number` [-5V, 5V]  (defaults to 0)
        :param level: Trigger level

        :type mode: `string` ['Auto', 'Normal']
        :param mode: Trigger mode

        :type edge: `string` ['Rising', 'Falling', 'Both']
        :param edge: Which edge to trigger on. In Pulse Width modes this specifies whether the pulse is positive (rising) or negative (falling), with the 'both' option being invalid

        :type polarity: `string` ['Positive', 'Negative']
        :param polarity: Trigger pulse polarity (Pulse mode only)

        :type width: `number` [26e-3Sec, 10Sec]  (defaults to 0.0001)
        :param width: Width of the trigger pulse (Pulse mode only)

        :type width_condition: `string` ['GreaterThan', 'LessThan']
        :param width_condition: Trigger pulse width condition (pulse mode only)

        :type nth_event: `integer` [0, 65535]  (defaults to 1)
        :param nth_event: The number of trigger events to wait for before triggering

        :type holdoff: `number` [1e-9Sec, 10Sec]  (defaults to 0)
        :param holdoff: The duration to hold-off Oscilloscope trigger post trigger event

        :type auto_sensitivity: `boolean`
        :param auto_sensitivity: Configure auto or manual hysteresis for noise rejection.

        :type noise_reject: `boolean`
        :param noise_reject: Configure the Oscilloscope with a small amount of hysteresis to prevent repeated triggering due to noise

        :type hf_reject: `boolean`
        :param hf_reject: Configure the trigger signal to pass through a low pass filter to smooths out the noise

        :type source: `string` ['ProbeA', 'ProbeB', 'ProbeC', 'ProbeD']
        :param source: Trigger Source

        """
        operation = "set_trigger"
        params = dict(
            strict=strict,
            type=validate_range(type, ['Edge', 'Pulse']),
            level=level,
            mode=validate_range(mode, ['Auto', 'Normal']),
            edge=validate_range(edge, ['Rising', 'Falling', 'Both']),
            polarity=validate_range(polarity, ['Positive', 'Negative']),
            width=width,
            width_condition=validate_range(
                width_condition, ['GreaterThan', 'LessThan']),
            nth_event=nth_event,
            holdoff=holdoff,
            auto_sensitivity=auto_sensitivity,
            noise_reject=noise_reject,
            hf_reject=hf_reject,
            source=validate_range(
                source, ['ProbeA', 'ProbeB', 'ProbeC', 'ProbeD']),
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_timebase(self, t1, t2, strict=True):
        """
        set_timebase.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen. This may be negative (trigger on-screen) or positive (trigger off the left of screen).

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. after the trigger event)

        """
        operation = "set_timebase"
        params = dict(
            strict=strict,
            t1=t1,
            t2=t2,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_hysteresis(self, hysteresis_mode, value=0, strict=True):
        """
        set_hysteresis.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type hysteresis_mode: `string` ['Absolute', 'Relative']
        :param hysteresis_mode: Trigger sensitivity hysteresis mode

        :type value: `number`
        :param value: Hysteresis around trigger

        """
        operation = "set_hysteresis"
        params = dict(strict=strict, hysteresis_mode=validate_range(
            hysteresis_mode, ['Absolute', 'Relative']), value=value, )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def enable_rollmode(self, roll=True, strict=True):
        """
        enable_rollmode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type roll: `boolean`
        :param roll: Enable roll

        """
        operation = "enable_rollmode"
        params = dict(
            strict=strict,
            roll=roll,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_data(self, timeout=60, wait_reacquire=False):
        """
        get_data.

        :type timeout: `number` Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired


        .. important::
            Default timeout for reading the data is 10 seconds. It
            can be increased by setting the read_timeout property of
            session object.

            Example: ``i.session.read_timeout=100`` (in seconds)

        """
        operation = "get_data"
        params = dict(
            timeout=timeout,
            wait_reacquire=wait_reacquire,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def save_high_res_buffer(self, comments=""):
        """
        save_high_res_buffer.

        :type comments: `string`
        :param comments: Optional comments to be included

        """
        operation = "save_high_res_buffer"
        params = dict(
            comments=comments,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_acquisition_mode(self, mode="Normal", strict=True):
        """
        set_acquisition_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['Normal', 'Precision', 'DeepMemory', 'PeakDetect']
        :param mode: Acquisition Mode

        """
        operation = "set_acquisition_mode"
        params = dict(strict=strict, mode=validate_range(
            mode, ['Normal', 'Precision', 'DeepMemory', 'PeakDetect']), )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_samplerate(self):
        """
        get_samplerate.
        """
        operation = "get_samplerate"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def get_acquisition_mode(self):
        """
        get_acquisition_mode.
        """
        operation = "get_acquisition_mode"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def get_timebase(self):
        """
        get_timebase.
        """
        operation = "get_timebase"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def logging_progress(self):
        """
        logging_progress.
        """
        operation = "logging_progress"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def start_logging(
            self,
            duration=60,
            delay=0,
            file_name_prefix="",
            comments="",
            mode="Normal",
            rate=1000,
            strict=True):
        """
        start_logging.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type duration: `integer` Sec (defaults to 60)
        :param duration: Duration to log for

        :type delay: `integer` Sec (defaults to 0)
        :param delay: Delay the start by

        :type file_name_prefix: `string`
        :param file_name_prefix: Optional file name prefix

        :type comments: `string`
        :param comments: Optional comments to be included

        :type mode: `string` ['Normal', 'Precision', 'DeepMemory', 'PeakDetect']
        :param mode: Acquisition Mode

        :type rate: `number`
        :param rate: Acquisition rate

        """
        operation = "start_logging"
        params = dict(
            strict=strict,
            duration=duration,
            delay=delay,
            file_name_prefix=file_name_prefix,
            comments=comments,
            mode=validate_range(
                mode, ['Normal', 'Precision', 'DeepMemory', 'PeakDetect']),
            rate=rate,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def stop_logging(self):
        """
        stop_logging.
        """
        operation = "stop_logging"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def start_streaming(self, duration=None, mode="Normal", rate=1000):
        """
        start_streaming.

        :type duration: `integer`
        :param duration: Duration in second(s) to stream for

        :type mode: `string` ['Normal', 'Precision', 'DeepMemory', 'PeakDetect']
        :param mode: Acquisition Mode

        :type rate: `number`
        :param rate: Acquisition rate

        """
        operation = "start_streaming"
        params = dict(
            duration=duration,
            mode=validate_range(
                mode, ['Normal', 'Precision', 'DeepMemory', 'PeakDetect']),
            rate=rate,
        )

        response = self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)
        self.stream_id = response["stream_id"]
        self.ip_address = self.session.ip_address
        return response

    def stop_streaming(self):
        """
        stop_streaming.

        """
        operation = "stop_streaming"
        response = self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation)
        self.stream_id = None
        return response

    def get_chunk(self):
        """
        get_chunk.

        """
        result = self.session.post_to_v2_raw(
            "get_chunk", params=dict(stream_id=self.stream_id))

        if result.status_code != 200:
            raise StreamException("Error fetching stream.")

        try:
            error = json.loads(result.content)
            raise StreamException(error.get('error', error))
        except StreamException as e:
            raise e
        except Exception:
            return result.content

    def get_stream_status(self):
        """
        get_stream_status.

        """
        operation = "get_stream_status"

        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation)

