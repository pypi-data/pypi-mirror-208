import json

from moku import Moku
from moku.exceptions import MokuException, StreamException
from moku.instruments._stream import StreamInstrument
from moku.utilities import find_moku_by_serial, validate_range


class DigitalFilterBox(Moku, StreamInstrument):
    """
    DigitalFilterBox instrument object.

    The Digital Filter Box can interactively design and
    generate different types of infinite impulse  response
    filters with varied sampling rates.

    DigitalFilterBox includes lowpass, highpass, bandpass
    and bandstop filter shapes with different filter types
    including Butterworth, Chebyshev, and Elliptic.

    Read more at https://apis.liquidinstruments.com/reference/dfb

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 6
        self.operation_group = "digitalfilterbox"

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

    def set_control_matrix(
            self,
            channel,
            input_gain1,
            input_gain2,
            strict=True):
        """
        set_control_matrix.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type input_gain1: `number` [-20, 20]
        :param input_gain1: ADC input gain for Channel 1

        :type input_gain2: `number` [-20, 20]
        :param input_gain2: ADC input gain for Channel 2

        """
        operation = "set_control_matrix"
        params = dict(
            strict=strict,
            channel=channel,
            input_gain1=input_gain1,
            input_gain2=input_gain2,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_monitor(self, monitor_channel, source, strict=True):
        """
        set_monitor.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type monitor_channel: `integer`
        :param monitor_channel: Monitor channel

        :type source: `string` ['None', 'Input1', 'Filter1', 'Output1', 'Input2', 'Filter2', 'Output2', 'Input3', 'Filter3', 'Output3', 'Input4', 'Filter4', 'Output4']
        :param source: Monitor channel source.

        """
        operation = "set_monitor"
        params = dict(strict=strict,
                      monitor_channel=monitor_channel,
                      source=validate_range(source,
                                            ['None',
                                             'Input1',
                                             'Filter1',
                                             'Output1',
                                             'Input2',
                                             'Filter2',
                                             'Output2',
                                             'Input3',
                                             'Filter3',
                                             'Output3',
                                             'Input4',
                                             'Filter4',
                                             'Output4']),
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def enable_output(
            self,
            channel,
            signal=True,
            output=True,
            gain_range="0dB",
            strict=True):
        """
        enable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type signal: `boolean`
        :param signal: Enable output signal

        :type output: `boolean`
        :param output: Enable output

        :type gain_range: `string`
        :param gain_range: Enable output

        """
        operation = "enable_output"
        params = dict(
            strict=strict,
            channel=channel,
            signal=signal,
            output=output,
            gain_range=gain_range,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_input_offset(self, channel, offset, strict=True):
        """
        set_input_offset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type offset: `number` [-5V, 5V]
        :param offset: Offset

        """
        operation = "set_input_offset"
        params = dict(
            strict=strict,
            channel=channel,
            offset=offset,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_output_offset(self, channel, offset, strict=True):
        """
        set_output_offset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type offset: `number` [-5V, 5V]
        :param offset: Offset

        """
        operation = "set_output_offset"
        params = dict(
            strict=strict,
            channel=channel,
            offset=offset,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_input_gain(self, channel, gain, strict=True):
        """
        set_input_gain.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type gain: `number` [-40dB, 40dB]
        :param gain: Gain

        """
        operation = "set_input_gain"
        params = dict(
            strict=strict,
            channel=channel,
            gain=gain,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_output_gain(self, channel, gain, strict=True):
        """
        set_output_gain.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type gain: `number` [-40dB, 40dB]
        :param gain: Gain

        """
        operation = "set_output_gain"
        params = dict(
            strict=strict,
            channel=channel,
            gain=gain,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

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

    def set_filter(
            self,
            channel,
            sample_rate,
            shape="Lowpass",
            type="Butterworth",
            low_corner=None,
            high_corner=None,
            pass_band_ripple=None,
            stop_band_attenuation=None,
            order=8,
            strict=True):
        """
        set_filter.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type sample_rate: `string` ['3.906MHz', '488.3kHz', '61.04kHz', '39.06MHz', '4.883MHz', '305.2kHz', '15.625MHz', '1.9531MHz', '122.07kHz']
        :param sample_rate: Sample rate

        :type shape: `string` ['Lowpass', 'Highpass', 'Bandpass', 'Bandstop']
        :param shape: Filter shape

        :type type: `string` ['Butterworth', 'ChebyshevI', 'ChebyshevII', 'Elliptic', 'Cascaded', 'Bessel', 'Gaussian', 'Legendre']
        :param type: Filter type

        :type low_corner: `number`
        :param low_corner: Low corner frequency

        :type high_corner: `number`
        :param high_corner: High corner frequency

        :type pass_band_ripple: `number`
        :param pass_band_ripple: Passband ripple

        :type stop_band_attenuation: `number`
        :param stop_band_attenuation: Stopband attenuation

        :type order: `integer`
        :param order: Filter order

        """
        operation = "set_filter"
        params = dict(strict=strict,
                      channel=channel,
                      sample_rate=validate_range(sample_rate,
                                                 ['3.906MHz',
                                                  '488.3kHz',
                                                  '61.04kHz',
                                                  '39.06MHz',
                                                  '4.883MHz',
                                                  '305.2kHz',
                                                  '15.625MHz',
                                                  '1.9531MHz', 
                                                  '122.07kHz']),
                      shape=validate_range(shape,
                                           ['Lowpass',
                                            'Highpass',
                                            'Bandpass',
                                            'Bandstop']),
                      type=validate_range(type,
                                          ['Butterworth',
                                           'ChebyshevI',
                                           'ChebyshevII',
                                           'Elliptic',
                                           'Cascaded',
                                           'Bessel',
                                           'Gaussian',
                                           'Legendre']),
                      low_corner=low_corner,
                      high_corner=high_corner,
                      pass_band_ripple=pass_band_ripple,
                      stop_band_attenuation=stop_band_attenuation,
                      order=order,
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_custom_filter(
            self,
            channel,
            sample_rate,
            scaling=1,
            coefficients=None,
            strict=True):
        """
        set_custom_filter.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type sample_rate: `string` ['3.906MHz', '488.3kHz', '61.04kHz', '39.06MHz', '4.883MHz', '305.2kHz', '15.625MHz', '1.9531MHz', '122.07kHz']
        :param sample_rate: Sample rate

        :type scaling: `number`
        :param scaling: Output scaling

        :type coefficients: `list`
        :param coefficients: List of filter stages, where each stage should have six coefficients and each coefficient must be in the range [-4.0, 4.0]

        """
        operation = "set_custom_filter"
        params = dict(strict=strict,
                      channel=channel,
                      sample_rate=validate_range(sample_rate,
                                                 ['3.906MHz',
                                                  '488.3kHz',
                                                  '61.04kHz',
                                                  '39.06MHz',
                                                  '4.883MHz',
                                                  '305.2kHz',
                                                  '15.625MHz',
                                                  '1.9531MHz', 
                                                  '122.07kHz']),
                      scaling=scaling,
                      coefficients=coefficients,
                      )
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

    def get_control_matrix(self, channel):
        """
        get_control_matrix.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_control_matrix"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_input_offset(self, channel):
        """
        get_input_offset.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_input_offset"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_output_offset(self, channel):
        """
        get_output_offset.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output_offset"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_input_gain(self, channel):
        """
        get_input_gain.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_input_gain"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_output_gain(self, channel):
        """
        get_output_gain.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output_gain"
        params = dict(
            channel=channel,
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
