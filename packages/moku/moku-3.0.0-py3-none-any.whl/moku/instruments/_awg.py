from moku import Moku
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class ArbitraryWaveformGenerator(Moku):
    """
    Arbitrary Waveform Generator instrument object.

    The Arbitrary Waveform Generator takes a time-series of
     voltage values, and generates the corresponding
     waveform at the DACs at a configurable rate.

    Read more at https://apis.liquidinstruments.com/reference/awg

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 15
        self.operation_group = "awg"

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

    def enable_output(self, channel, enable=True, strict=True):
        """
        enable_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enable: `boolean`
        :param enable: Enable the specified output channel

        """
        operation = "enable_output"
        params = dict(
            strict=strict,
            channel=channel,
            enable=enable,
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

    def generate_waveform(
            self,
            channel,
            sample_rate,
            lut_data,
            frequency,
            amplitude,
            phase=0,
            offset=0,
            interpolation=False,
            strict=True):
        """
        generate_waveform.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type sample_rate: `string` ['Auto', '1.25Gs', '1Gs', '625Ms', '500Ms', '312.5Ms', '250Ms', '125Ms', '62.5Ms', '31.25Ms', '15.625Ms']
        :param sample_rate: Defines the output sample rate of the AWG. If you do not specify a mode, the fastest output rate for the given data length will be automatically chosen. This is correct in almost all circumstances.

        :type lut_data: `list`
        :param lut_data: Lookup table coefficients, each coefficient should be in the range of [-1.0, 1.0]

        :type frequency: `number` [1e-3Hz, 10e6Hz]
        :param frequency: Frequency of the waveform

        :type amplitude: `number` [4e-3V, 10V]
        :param amplitude: Waveform peak-to-peak amplitude

        :type phase: `number` [0Deg, 360Deg]  (defaults to 0)
        :param phase: Waveform phase offset

        :type offset: `number` [-5V, 5V]  (defaults to 0)
        :param offset: DC offset applied to the waveform

        :type interpolation: `boolean`  (defaults to False)
        :param interpolation: Enable linear interpolation of LUT entries.

        """
        operation = "generate_waveform"
        params = dict(strict=strict,
                      channel=channel,
                      sample_rate=validate_range(sample_rate,
                                                 ['Auto',
                                                  '1.25Gs',
                                                  '1Gs',
                                                  '625Ms',
                                                  '500Ms',
                                                  '312.5Ms',
                                                  '250Ms',
                                                  '125Ms',
                                                  '62.5Ms',
                                                  '31.25Ms',
                                                  '15.625Ms']),
                      lut_data=lut_data,
                      frequency=frequency,
                      amplitude=amplitude,
                      phase=phase,
                      offset=offset,
                      interpolation=interpolation,
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

    def pulse_modulate(
            self,
            channel,
            dead_cycles=10,
            dead_voltage=0,
            strict=True):
        """
        pulse_modulate.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type dead_cycles: `integer` [1, 262144]  (defaults to 10)
        :param dead_cycles: Number of cycles which show the dead voltage.

        :type dead_voltage: `number` [-5V, 5V]  (defaults to 0)
        :param dead_voltage: Signal level during dead time

        """
        operation = "pulse_modulate"
        params = dict(
            strict=strict,
            channel=channel,
            dead_cycles=dead_cycles,
            dead_voltage=dead_voltage,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def burst_modulate(
            self,
            channel,
            trigger_source,
            trigger_mode,
            burst_cycles=1,
            trigger_level=0,
            input_range=None,
            strict=True):
        """
        burst_modulate.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type trigger_source: `string` ['Input1', 'Input2', 'Input3', 'Input4', 'InputA', 'InputB', 'InputC', 'InputD', 'External']
        :param trigger_source: Trigger source

        :type trigger_mode: `string` ['Start', 'NCycle']
        :param trigger_mode: Burst mode

        :type burst_cycles: `number` [1, 1e6]  (defaults to 1)
        :param burst_cycles: Number of cycles to generate when triggered

        :type trigger_level: `number` [-5V, 5V]  (defaults to 0)
        :param trigger_level: Trigger level

        :type input_range: `string` ['400mVpp', '1Vpp', '4Vpp', '10Vpp', '40Vpp', '50Vpp']
        :param input_range: Input Range

        """
        operation = "burst_modulate"
        params = dict(strict=strict,
                      channel=channel,
                      trigger_source=validate_range(trigger_source,
                                                    ['Input1',
                                                     'Input2',
                                                     'Input3',
                                                     'Input4',
                                                     'InputA',
                                                     'InputB',
                                                     'InputC',
                                                     'InputD',
                                                     'External']),
                      trigger_mode=validate_range(trigger_mode,
                                                  ['Start',
                                                   'NCycle']),
                      burst_cycles=burst_cycles,
                      trigger_level=trigger_level,
                      input_range=input_range,
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)
