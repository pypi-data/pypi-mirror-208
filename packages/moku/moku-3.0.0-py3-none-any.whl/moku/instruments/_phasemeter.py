import json

from moku import Moku
from moku.exceptions import MokuException, StreamException
from moku.instruments._stream import StreamInstrument
from moku.utilities import find_moku_by_serial, validate_range


class Phasemeter(Moku, StreamInstrument):
    """
    Phasemeter instrument object.

    The Phasemeter instrument is used to measure the
    amplitude and change in phase of periodic input
    signals. Using the auto-acquire feature, it can
    automatically lock to input frequencies in the
    range of 2-200MHz and track phase with a
    bandwidth of 10kHz.

    Read more at https://apis.liquidinstruments.com/reference/phasemeter

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 3
        self.operation_group = "phasemeter"

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

    def reacquire(self):
        """
        reacquire.
        """
        operation = "reacquire"
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_frontend(self, channel, impedance, coupling, range, strict=True):
        """
        set_frontend.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type impedance: `string` ['1MOhm', '50Ohm']
        :param impedance: Impedance

        :type coupling: `string` ['AC', 'DC']
        :param coupling: Input Coupling

        :type range: `string` ['Default', '400mVpp', '1Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp']
        :param range: Input Range

        """
        operation = "set_frontend"
        params = dict(
            strict=strict, channel=channel, impedance=validate_range(
                impedance, [
                    '1MOhm', '50Ohm']), coupling=validate_range(
                coupling, [
                    'AC', 'DC']), range=validate_range(
                        range, [
                            'Default', '400mVpp', '1Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp']), )
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

    def set_acquisition_speed(self, speed, strict=True):
        """
        set_acquisition_speed.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type speed: `string` ['37Hz', '150Hz', '596Hz', '2.4kHz', '19.1kHz', '152kHz']
        :param speed: Acquisition Speed

        """
        operation = "set_acquisition_speed"
        params = dict(strict=strict, speed=validate_range(
            speed, ['37Hz', '150Hz', '596Hz', '2.4kHz', '19.1kHz', '152kHz']), )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_pm_loop(
            self,
            channel,
            auto_acquire=False,
            frequency=1e6,
            bandwidth="1kHz",
            strict=True):
        """
        set_pm_loop.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type auto_acquire: `boolean`
        :param auto_acquire: Auto acquire frequency

        :type frequency: `number`
        :param frequency: Initial locking frequency of the designated channel

        :type bandwidth: `string` ['1Hz', '10Hz', '100Hz', '1kHz', '10kHz', '100kHz', '1MHz']
        :param bandwidth: Bandwidth

        """
        operation = "set_pm_loop"
        params = dict(strict=strict,
                      channel=channel,
                      auto_acquire=auto_acquire,
                      frequency=frequency,
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

    def get_pm_loop(self, channel):
        """
        get_pm_loop.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_pm_loop"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_auto_acquired_frequency(self, channel, strict=True):
        """
        get_auto_acquired_frequency.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_auto_acquired_frequency"
        params = dict(
            strict=strict,
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def generate_output(
            self,
            channel,
            signal,
            amplitude=0.5,
            frequency=1e6,
            frequency_multplier=1,
            phase=0,
            phase_locked=False,
            scaling=0.001,
            strict=True):
        """
        generate_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type signal: `string` ['Sine', 'Phase', 'FrequencyOffset', 'Amptitude']
        :param signal: Type of output signal

        :type amplitude: `number`
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number`
        :param frequency: Frequency of the wave

        :type frequency_multplier: `number`
        :param frequency_multplier: Frequency multiplier

        :type phase: `number`
        :param phase: Phase offset of the wave

        :type phase_locked: `boolean`
        :param phase_locked: Locks the phase of the generated sinewave to the measured phase of the input signal

        :type scaling: `number`
        :param scaling: Scaling for phase, frequency offset and amplitude

        """
        operation = "generate_output"
        params = dict(
            strict=strict,
            channel=channel,
            signal=validate_range(
                signal, ['Sine', 'Phase', 'FrequencyOffset', 'Amptitude']),
            amplitude=amplitude,
            frequency=frequency,
            frequency_multplier=frequency_multplier,
            phase=phase,
            phase_locked=phase_locked,
            scaling=scaling,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def disable_output(self, channel, strict=True):
        """
        disable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_output"
        params = dict(
            strict=strict,
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def disable_input(self, channel):
        """
        disable_input.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_input"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def enable_freewheeling(self, enable=True, strict=True):
        """
        enable_freewheeling.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type enable: `boolean`
        :param enable: Enable free wheeling

        """
        operation = "enable_freewheeling"
        params = dict(
            strict=strict,
            enable=enable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def enable_single_input(self, enable=True, strict=True):
        """
        enable_single_input.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type enable: `boolean`
        :param enable: Sends the signal from the first input to all phasemeter channels

        """
        operation = "enable_single_input"
        params = dict(
            strict=strict,
            enable=enable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_phase_wrap(self, value="Off", strict=True):
        """
        set_phase_wrap.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type value: `string` ['Off', '1pi', '2pi', '4pi']
        :param value: Wraps the phase output at a particular value

        """
        operation = "set_phase_wrap"
        params = dict(
            strict=strict,
            value=validate_range(value, ['Off', '1pi', '2pi', '4pi']),
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_auto_reset(self, value="Off", strict=True):
        """
        set_auto_reset.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type value: `string` ['Off', '1pi', '2pi', '4pi']
        :param value: Reset the phase output to zero when it exceeds a particular value

        """
        operation = "set_auto_reset"
        params = dict(
            strict=strict,
            value=validate_range(value, ['Off', '1pi', '2pi', '4pi']),
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

    def start_logging(
            self,
            duration=60,
            delay=0,
            file_name_prefix="",
            comments="",
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

        """
        operation = "start_logging"
        params = dict(
            strict=strict,
            duration=duration,
            delay=delay,
            file_name_prefix=file_name_prefix,
            comments=comments,
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

    def get_acquisition_speed(self):
        """
        get_acquisition_speed.
        """
        operation = "get_acquisition_speed"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def logging_progress(self):
        """
        logging_progress.
        """
        operation = "logging_progress"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def start_streaming(self, duration=None):
        """
        start_streaming.

        :type duration: `integer`
        :param duration: Duration in second(s) to stream for

        """
        operation = "start_streaming"
        params = dict(
            duration=duration
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

    def get_stream_status(self):
        """
        get_stream_status.

        """
        operation = "get_stream_status"

        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation)

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

