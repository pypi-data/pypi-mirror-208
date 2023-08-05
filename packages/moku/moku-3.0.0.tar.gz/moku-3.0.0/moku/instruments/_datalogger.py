import json

from moku import Moku
from moku.exceptions import MokuException, StreamException
from moku.instruments._stream import StreamInstrument
from moku.utilities import find_moku_by_serial, validate_range


class Datalogger(Moku, StreamInstrument):
    """
    Datalogger instrument object.

    The Data logger instrument provides file logging of
    time-series voltage data. It contains a built-in
    Waveform Generator that can  control the analog outputs
    as well.

    Read more at https://apis.liquidinstruments.com/reference/datalogger

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 7
        self.operation_group = "datalogger"

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

    def set_frontend(self, channel, impedance, coupling, range,
                     strict=True):
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
                    'Default', '400mVpp', '1Vpp', '4Vpp', '10Vpp',
                    '40Vpp', '50Vpp']), )
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
            mode,
            ['Normal', 'Precision', 'DeepMemory', 'PeakDetect']), )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_acquisition_mode(self):
        """
        get_acquisition_mode.
        """
        operation = "get_acquisition_mode"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_samplerate(self, sample_rate, strict=True):
        """
        set_samplerate.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type sample_rate: `number` [10, 1e6]
        :param sample_rate: Target samples per second

        """
        operation = "set_samplerate"
        params = dict(
            strict=strict,
            sample_rate=sample_rate,
        )
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

    def disable_channel(self, channel, disable=True, strict=True):
        """
        disable_channel.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type disable: `boolean`
        :param disable: Boolean value to enable/disable

        """
        operation = "disable_channel"
        params = dict(
            strict=strict,
            channel=channel,
            disable=disable,
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


        .. important::
            It is recommended **not** to relinquish the ownership of the
            device until logging session is completed

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

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def generate_waveform(
            self,
            channel,
            type,
            amplitude=1,
            frequency=10000,
            offset=0,
            phase=0,
            duty=None,
            symmetry=None,
            dc_level=None,
            edge_time=None,
            pulse_width=None,
            strict=True):
        """
        generate_waveform.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type type: `string` ['Off', 'Sine', 'Square', 'Ramp', 'Pulse', 'Noise', 'DC']
        :param type: Waveform type

        :type amplitude: `number` [4e-3V, 10V]  (defaults to 1)
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number` [1e-3Hz, 20e6Hz]  (defaults to 10000)
        :param frequency: Waveform frequency

        :type offset: `number` [-5V, 5V]  (defaults to 0)
        :param offset: DC offset applied to the waveform

        :type phase: `number` [0Deg, 360Deg]  (defaults to 0)
        :param phase: Waveform phase offset

        :type duty: `number` [0.0%, 100.0%]
        :param duty: Duty cycle as percentage (Only for Square wave)

        :type symmetry: `number` [0.0%, 100.0%]
        :param symmetry: Fraction of the cycle rising

        :type dc_level: `number`
        :param dc_level: DC Level. (Only for DC waveform)

        :type edge_time: `number` [16e-9, pulse width]
        :param edge_time: Edge-time of the waveform (Only for Pulse wave)

        :type pulse_width: `number`
        :param pulse_width: Pulse width of the waveform (Only for Pulse wave)

        """
        operation = "generate_waveform"
        params = dict(
            strict=strict,
            channel=channel,
            type=validate_range(
                type,
                ['Off', 'Sine', 'Square', 'Ramp', 'Pulse', 'Noise',
                 'DC']),
            amplitude=amplitude,
            frequency=frequency,
            offset=offset,
            phase=phase,
            duty=duty,
            symmetry=symmetry,
            dc_level=dc_level,
            edge_time=edge_time,
            pulse_width=pulse_width,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_output_load(self, channel, load, strict=True):
        """
        set_output_load.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type load: `string` ['1MOhm', '50Ohm']
        :param load: Output load

        """
        operation = "set_output_load"
        params = dict(
            strict=strict,
            channel=channel,
            load=validate_range(load, ['1MOhm', '50Ohm']),
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_output_load(self, channel):
        """
        get_output_load.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_output_load"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

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
            duration=duration,
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
