from moku import Moku
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class LogicAnalyzer(Moku):
    """
    Logic Analyzer instrument object.

    Instantiating this class will return a new Logic Analyzer
    instrument with the default state. This may raise a
    :any:`moku.exceptions.InvalidRequestException` if there
    is an active connection to the Moku.

    Available states for a pin are:

    =====  ========================
    State  Description
    =====  ========================
    X      Off, Pin is off
    I      Input
    PG1    Pattern Generator 1
    PG2    Pattern Generator 2
    =====  ========================

    =====  ========================
    Override  Description
    =====  ========================
    X      Off, Pin override is off
    H      High, pin is set to 1
    L      Low, pin is set to 0
    =====  ========================

    Read more at https://apis.liquidinstruments.com/reference/logicanalyzer

    """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 17
        self.operation_group = "logicanalyzer"

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

    def get_pins(self):
        """
        get_pins.
        """
        operation = "get_pins"
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_pin(self, pin, state, override="X", strict=True):
        """
        set_pin.

        :type pin: `integer`
        :param pin: Target pin to configure

        :type state: `string` [ 'X', 'I', 'PG1', 'PG2']
        :param state: State of the target pin.

        :type override: `string` ['X', 'H', 'L']
        :param override: Output override for the target pin.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        """
        operation = "set_pin"
        params = dict(
            pin=pin,
            state=validate_range(state, ['X', 'I', 'PG1', 'PG2']),
            override=validate_range(override, ['X', 'H', 'L']),
            strict=strict,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_pins(self, pins, strict=True):
        """
        set_pins.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type pins: `list`
        :param pins: List of pins to configure

        """
        operation = "set_pins"
        params = dict(
            strict=strict,
            pins=pins,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_pin(self, pin):
        """
        get_pin.

        :type pin: `integer`
        :param pin: Target pin to configure

        """
        operation = "get_pin"
        params = dict(
            pin=pin,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def restart_pattern(self, channel):
        """
        restart_pattern.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "restart_pattern"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def disable_pattern_generator(self, channel):
        """
        disable_pattern_generator.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "disable_pattern_generator"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_pattern_generator(
            self,
            channel,
            patterns,
            baud_rate=None,
            divider=None,
            tick_count=8,
            repeat=True,
            iterations=1,
            strict=True):
        """
        set_pattern_generator.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type patterns: `list`
        :param patterns: List of pin to pattern map

        :type baud_rate: `integer`
        :param baud_rate: Baud rate

        :type divider: `integer` [1, 1e6]
        :param divider: Divider to scale down the base frequency of 125 MHz to the tick frequency. Fore example, a divider of 2 provides a 62.5 MHz tick frequency.

        :type tick_count: `integer`
        :param tick_count: Number of ticks

        :type repeat: `boolean`
        :param repeat: Repeat forever

        :type iterations: `integer` [1, 8192]  (defaults to 1)
        :param iterations: Number of iterations, valid when repeat is set to false

        """
        operation = "set_pattern_generator"
        params = dict(
            strict=strict,
            channel=channel,
            patterns=patterns,
            baud_rate=baud_rate,
            divider=divider,
            tick_count=tick_count,
            repeat=repeat,
            iterations=iterations,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_pattern_generator(self, channel):
        """
        get_pattern_generator.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_pattern_generator"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_trigger(
            self,
            pins,
            advanced=False,
            mode="Auto",
            combination="AND",
            nth_event=1,
            holdoff=0,
            strict=True):
        """
        set_trigger.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type pins: `list`
        :param pins: Map of Pin and Edge trigger configurations

        :type advanced: `boolean`
        :param advanced: Toggle advanced triggering mode

        :type mode: `string` ['Auto', 'Normal']
        :param mode: Trigger mode

        :type combination: `string` ['AND', 'OR']
        :param combination: Trigger combination

        :type nth_event: `integer` [0, 65535]  (defaults to 1)
        :param nth_event: The number of trigger events to wait for before triggering

        :type holdoff: `number` [1e-9Sec, 10Sec]  (defaults to 0)
        :param holdoff: The duration to hold off Oscilloscope trigger post trigger event.

        """
        operation = "set_trigger"
        params = dict(
            strict=strict,
            pins=pins,
            advanced=advanced,
            mode=validate_range(mode, ['Auto', 'Normal']),
            combination=validate_range(combination, ['AND', 'OR']),
            nth_event=nth_event,
            holdoff=holdoff,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_trigger(self):
        """
        get_trigger.
        """
        operation = "get_trigger"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_timebase(self, t1, t2, roll_mode=False, strict=True):
        """
        set_timebase.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type t1: `number`
        :param t1: Time from the trigger point to the left of screen.

        :type t2: `number`
        :param t2: Time from the trigger point to the right of screen. (Must be a positive number, i.e. post trigger event)

        :type roll_mode: `boolean`
        :param roll_mode: Enable roll mode

        """
        operation = "set_timebase"
        params = dict(
            strict=strict,
            t1=t1,
            t2=t2,
            roll_mode=roll_mode,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_timebase(self):
        """
        get_timebase.
        """
        operation = "get_timebase"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def get_data(self, timeout=60, wait_reacquire=False, include_pins=None):
        """
        get_data.

        :type timeout: `number` Seconds (defaults to 60)
        :param timeout: Wait for n seconds to receive a data frame

        :type wait_reacquire: `boolean`
        :param wait_reacquire: Wait until new dataframe is reacquired

        :type include_pins: `list`
        :param include_pins: When provided, result will be filtered based on pins requested


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
            include_pins=include_pins,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_decoder(
            self,
            channel,
            protocol,
            data_pin,
            lsb_first=None,
            data_width=8,
            uart_stop_width=1,
            uart_parity="None",
            uart_baud_rate=9600,
            clock_pin=None,
            spi_cs=None,
            spi_cpol=0,
            spi_cpha=0,
            strict=True):
        """
        set_decoder.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type protocol: `string` ['UART', 'SPI', 'I2C']
        :param protocol: Protocol type

        :type data_pin: `integer` [1, 16]
        :param data_pin: Pin number to send/receive data

        :type lsb_first: `boolean`
        :param lsb_first: Bit order for UART/SPI. When null, sets MSB for SPI and LSB for UART

        :type data_width: `integer` [5, 9]  (defaults to 8)
        :param data_width: Number of data bits. Cannot be more than 8 if parity bit is enabled

        :type uart_stop_width: `integer` [1, 2]  (defaults to 1)
        :param uart_stop_width: Number of stop bits.

        :type uart_parity: `string` ['None', 'Even', 'Odd']
        :param uart_parity: Parity

        :type uart_baud_rate: `integer`
        :param uart_baud_rate: Baud Rate

        :type clock_pin: `integer` [1, 16]
        :param clock_pin: Pin number to send clock signal

        :type spi_cs: `integer` [1, 16]
        :param spi_cs: SPI Chip Select

        :type spi_cpol: `integer`
        :param spi_cpol: SPI Clock Polarity (1 for High and 0 for Low)

        :type spi_cpha: `integer`
        :param spi_cpha: SPI Clock Phase (1 for trailing edge and 0 for leading edge

        """
        operation = "set_decoder"
        params = dict(
            strict=strict,
            channel=channel,
            protocol=validate_range(protocol, ['UART', 'SPI', 'I2C']),
            data_pin=data_pin,
            lsb_first=lsb_first,
            data_width=data_width,
            uart_stop_width=uart_stop_width,
            uart_parity=validate_range(uart_parity, ['None', 'Even', 'Odd']),
            uart_baud_rate=uart_baud_rate,
            clock_pin=clock_pin,
            spi_cs=spi_cs,
            spi_cpol=spi_cpol,
            spi_cpha=spi_cpha,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_decoder(self, channel):
        """
        get_decoder.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_decoder"
        params = dict(
            channel=channel,
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
