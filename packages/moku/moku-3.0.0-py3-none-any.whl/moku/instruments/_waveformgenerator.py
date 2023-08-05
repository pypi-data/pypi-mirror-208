from moku import Moku
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class WaveformGenerator(Moku):
    """
    Waveform Generator instrument object.

    Supports the generation of Sine, Square and Ramp waves.

     - The output waveforms can also be frequency, phase or
       amplitude modulated.
     - The modulation source can be another
       internally-generated Sinewave, the associated analog
       input channel or the other output channel.
       That other output channel may itself be modulated in
       some way, allowing the creation of very complex
       waveforms

    Read more at https://apis.liquidinstruments.com/reference/waveformgenerator

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 4
        self.operation_group = "waveformgenerator"

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
            type=validate_range(type, ['Off', 'Sine', 'Square', 'Ramp', 'Pulse', 'Noise', 'DC']),
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

    def set_defaults(self):
        """
        set_defaults.
        """
        operation = "set_defaults"
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation)

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

    def set_modulation(
            self,
            channel,
            type,
            source,
            depth=0,
            frequency=10000000,
            strict=True):
        """
        set_modulation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type type: `string` ['Amplitude', 'Frequency', 'Phase', 'PulseWidth']
        :param type: Modulation type

        :type source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'Output1', 'Output2', 'Output3', 'Output4', 'Internal']
        :param source: Modulation source

        :type depth: `number`  (defaults to 0)
        :param depth: Modulation depth (depends on modulation type): Percentage modulation depth, Frequency Deviation/Volt or +/- phase shift/Volt

        :type frequency: `number` [0Hz, 50e6Hz]  (defaults to 10000000)
        :param frequency: Frequency of internally-generated sine wave modulation. This parameter is ignored if the source is set to ADC or DAC.

        """
        operation = "set_modulation"
        params = dict(strict=strict,
                      channel=channel,
                      type=validate_range(type,
                                          ['Amplitude',
                                           'Frequency',
                                           'Phase',
                                           'PulseWidth']),
                      source=validate_range(source,
                                            ['Input1',
                                             'Input2',
                                             'Input3',
                                             'Input4',
                                             'InputA',
                                             'InputB',
                                             'InputC',
                                             'InputD',
                                             'Output1',
                                             'Output2',
                                             'Output3',
                                             'Output4',
                                             'Internal']),
                      depth=depth,
                      frequency=frequency,
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def disable_modulation(self, channel, strict=True):
        """
        disable_modulation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_modulation"
        params = dict(
            strict=strict,
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_burst_mode(
            self,
            channel,
            source,
            mode,
            trigger_level=0,
            burst_cycles=3,
            burst_duration=0.1,
            burst_period=1,
            input_range=None,
            strict=True):
        """
        set_burst_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'Output1', 'Output2', 'Output3', 'Output4', 'OutputA', 'OutputB', 'Internal', 'External']
        :param source: Trigger source

        :type mode: `string` ['Gated', 'Start', 'NCycle']
        :param mode: Burst mode

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger threshold level

        :type burst_cycles: `number` [1, 1e6]  (defaults to 3)
        :param burst_cycles: The integer number of signal repetitions to generate once triggered (NCycle mode only)

        :type burst_duration: `number` [1 cycle periodSec, 1e3Sec]  (defaults to 0.1)
        :param burst_duration: Burst duration

        :type burst_period: `number`
        :param burst_period: Burst Period

        :type input_range: `string` ['400mVpp', '1Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp']
        :param input_range: Input Range

        """
        operation = "set_burst_mode"
        params = dict(strict=strict,
                      channel=channel,
                      source=validate_range(source,
                                            ['Input1',
                                             'Input2',
                                             'Input3',
                                             'Input4',
                                             'InputA',
                                             'InputB',
                                             'InputC',
                                             'InputD',
                                             'Output1',
                                             'Output2',
                                             'Output3',
                                             'Output4',
                                             'OutputA',
                                             'OutputB',
                                             'Internal',
                                             'External']),
                      mode=validate_range(mode,
                                          ['Gated',
                                           'Start',
                                           'NCycle']),
                      trigger_level=trigger_level,
                      burst_cycles=burst_cycles,
                      burst_duration=burst_duration,
                      burst_period=burst_period,
                      input_range=input_range
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_sweep_mode(
            self,
            channel,
            source,
            stop_frequency=30000000,
            sweep_time=1,
            trigger_level=0,
            strict=True):
        """
        set_sweep_mode.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'Output1', 'Output2', 'Output3', 'Output4', 'OutputA', 'OutputB', 'Internal', 'External']
        :param source: Trigger source

        :type stop_frequency: `number` [100Hz, 20e6Hz]  (defaults to 30000000)
        :param stop_frequency: Sweep stop Frequency

        :type sweep_time: `number` [1 cycle periodSec, 1e3Sec]  (defaults to 1)
        :param sweep_time: Duration of sweep

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger threshold level

        """
        operation = "set_sweep_mode"
        params = dict(strict=strict,
                      channel=channel,
                      source=validate_range(source,
                                            ['Input1',
                                             'Input2',
                                             'Input3',
                                             'Input4',
                                             'InputA',
                                             'InputB',
                                             'InputC',
                                             'InputD',
                                             'Output1',
                                             'Output2',
                                             'Output3',
                                             'Output4',
                                             'OutputA',
                                             'OutputB',
                                             'Internal',
                                             'External']),
                      stop_frequency=stop_frequency,
                      sweep_time=sweep_time,
                      trigger_level=trigger_level,
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def sync_phase(self):
        """
        sync_phase.
        """
        operation = "sync_phase"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)
