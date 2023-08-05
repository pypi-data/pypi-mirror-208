from moku import Moku
from moku.exceptions import MokuException
from moku.utilities import find_moku_by_serial
from moku.utilities import validate_range


class CloudCompile(Moku):
    """
               Cloud Compile - Custom Instrument

               """

    def __init__(self, ip=None, serial=None, force_connect=False,
                 ignore_busy=False, persist_state=False,
                 connect_timeout=15, read_timeout=30, slot=None,
                 multi_instrument=None, **kwargs):
        self.id = 255
        self.operation_group = "cloudcompile"

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

    def set_controls(self, controls, strict=True):
        """
        set_controls.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type controls: `list`
        :param controls: List of control map(pair of id, value)

        """
        operation = "set_controls"
        params = dict(
            strict=strict,
            controls=controls,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def set_control(self, idx, value, strict=True):
        """
        set_control.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type idx: `integer`
        :param idx: Control ID(0 indexed)

        :type value: `integer`
        :param value: Register value

        """
        operation = "set_control"
        params = dict(
            strict=strict,
            idx=idx,
            value=value,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_control(self, idx, strict=True):
        """
        get_control.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type idx: `integer`
        :param idx: Control ID(0 indexed)

        """
        operation = "get_control"
        params = dict(
            strict=strict,
            idx=idx,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_controls(self):
        """
        get_controls.
        """
        operation = "get_controls"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)

    def set_interpolation(self, channel, enable=True, strict=True):
        """
        set_interpolation.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type channel: `integer`
        :param channel: Target channel

        :type enable: `boolean`
        :param enable: Enable/disable interpolation on specified channel

        """
        operation = "set_interpolation"
        params = dict(
            strict=strict,
            channel=channel,
            enable=enable,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def sync(self, mask, strict=True):
        """
        sync.

        :type strict: `boolean`
        :param strict: Disable all implicit conversions and coercions.

        :type mask: `integer`
        :param mask: Mask value

        """
        operation = "sync"
        params = dict(
            strict=strict,
            mask=mask,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def get_interpolation(self, channel):
        """
        get_interpolation.

        :type channel: `integer`
        :param channel: Target channel

        """
        operation = "get_interpolation"
        params = dict(
            channel=channel,
        )
        return self.session.post(
            f"slot{self.slot}/{self.operation_group}",
            operation,
            params)

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get(
            f"slot{self.slot}/{self.operation_group}", operation)
