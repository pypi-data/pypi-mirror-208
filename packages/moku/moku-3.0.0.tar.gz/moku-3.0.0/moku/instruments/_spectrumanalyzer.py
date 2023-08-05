from moku import Moku
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class SpectrumAnalyzer(Moku):
    """
    Spectrum Analyzer instrument object.

    Spectrum Analyzer provides frequency-domain analysis of
    input signals. It features switchable window functions,
    resolution bandwidth, averaging modes and more.

    Read more at https://apis.liquidinstruments.com/reference/specan

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 2
        self.operation_group = "spectrumanalyzer"

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
            f"slot{self.slot}/{self.operation_group}", operation, params=params)

    def sa_output(self, channel, amplitude, frequency, strict=True):
        """
        sa_output.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type amplitude: `number`
        :param amplitude: Waveform peak-to-peak amplitude

        :type frequency: `number` [0Hz, 30e6Hz]
        :param frequency: Frequency of the wave

        """
        operation = "sa_output"
        params = dict(
            strict=strict,
            channel=channel,
            amplitude=amplitude,
            frequency=frequency,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_rbw(self):
        """
        get_rbw.
        """
        operation = "get_rbw"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_rbw(self, mode, rbw_value=5000, strict=True):
        """
        set_rbw.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mode: `string` ['Auto', 'Manual', 'Minimum']
        :param mode: Desired resolution bandwidth (Hz)

        :type rbw_value: `number`
        :param rbw_value: RBW value (only in manual mode)

        """
        operation = "set_rbw"
        params = dict(
            strict=strict,
            mode=validate_range(mode, ['Auto', 'Manual', 'Minimum']),
            rbw_value=rbw_value,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_span(self):
        """
        get_span.
        """
        operation = "get_span"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_span(self, frequency1, frequency2, strict=True):
        """
        set_span.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type frequency1: `number` [0Hz, 30e6Hz]
        :param frequency1: Left-most frequency

        :type frequency2: `number` [0Hz, 30e6Hz]
        :param frequency2: Right-most frequency

        """
        operation = "set_span"
        params = dict(
            strict=strict,
            frequency1=frequency1,
            frequency2=frequency2,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def sa_measurement(
            self,
            channel,
            frequency1,
            frequency2,
            rbw="Auto",
            rbw_value=5000,
            window="BlackmanHarris",
            strict=True):
        """
        sa_measurement.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type frequency1: `number` [0Hz, 30e6Hz]
        :param frequency1: Left-most frequency

        :type frequency2: `number` [0Hz, 30e6Hz]
        :param frequency2: Right-most frequency

        :type rbw: `string` ['Auto', 'Manual', 'Minimum']
        :param rbw: Desired resolution bandwidth (Hz)

        :type rbw_value: `number`
        :param rbw_value: RBW value (only in manual mode)

        :type window: `string` ['BlackmanHarris', 'FlatTop', 'Rectangular', 'Bartlett', 'Hamming', 'Hann', 'Nuttall', 'Gaussian', 'Kaiser']
        :param window: Window Function

        """
        operation = "sa_measurement"
        params = dict(strict=strict,
                      channel=channel,
                      frequency1=frequency1,
                      frequency2=frequency2,
                      rbw=validate_range(rbw,
                                         ['Auto',
                                          'Manual',
                                          'Minimum']),
                      rbw_value=rbw_value,
                      window=validate_range(window,
                                            ['BlackmanHarris',
                                             'FlatTop',
                                             'Rectangular',
                                             'Bartlett',
                                             'Hamming',
                                             'Hann',
                                             'Nuttall',
                                             'Gaussian',
                                             'Kaiser']),
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_window(self, window, strict=True):
        """
        set_window.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type window: `string` ['BlackmanHarris', 'FlatTop', 'Rectangular', 'Bartlett', 'Hamming', 'Hann', 'Nuttall', 'Gaussian', 'Kaiser']
        :param window: Window Function

        """
        operation = "set_window"
        params = dict(strict=strict,
                      window=validate_range(window,
                                            ['BlackmanHarris',
                                             'FlatTop',
                                             'Rectangular',
                                             'Bartlett',
                                             'Hamming',
                                             'Hann',
                                             'Nuttall',
                                             'Gaussian',
                                             'Kaiser']),
                      )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_window(self):
        """
        get_window.
        """
        operation = "get_window"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

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

    def get_data(
            self,
            timeout=60,
            wait_reacquire=False,
            units="dBm",
            psdUnits=False,
            strict=True):
        """
        get_data.

        :type timeout: `number` Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type units: `string` ['dBm', 'Vrms', 'Vpp', 'dBV']
        :param units: Units

        :type psdUnits: `boolean`
        :param psdUnits: PSD Units


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
            strict=strict,
            units=validate_range(units, ['dBm', 'Vrms', 'Vpp', 'dBV']),
            psdUnits=psdUnits,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)
