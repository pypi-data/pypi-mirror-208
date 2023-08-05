import tarfile
from hashlib import sha256
from os import environ
from pathlib import Path
from shutil import which
from subprocess import Popen, PIPE

from pkg_resources import get_distribution, resource_filename

from moku.exceptions import IncompatibleMokuException
from moku.session import RequestSession
from moku.utilities import validate_range
from moku.version import compat_fw, cli_ver_major, cli_ver_minor, cli_ver_patch

__version__ = get_distribution("moku").version
_data_path = environ.get('MOKU_DATA_PATH',
                         resource_filename("moku", 'data'))
MOKU_DATA_PATH = Path(_data_path).expanduser()

MOKU_CLI_PATH = environ.get('MOKU_CLI_PATH', which("mokucli"))
if MOKU_CLI_PATH:
    MOKU_CLI_PATH = str(Path(MOKU_CLI_PATH).expanduser())


def check_mokucli_version():
    if MOKU_CLI_PATH:
        out, _ = Popen([MOKU_CLI_PATH, "--version"], stdout=PIPE,
                       stderr=PIPE).communicate()
        if out:
            result = out.decode("utf8").split('mokucli')
            if len(result) == 2:
                _ver = result[1].strip().split('.')
                if len(_ver) == 3:
                    _ma, _mi, _pa = map(int, _ver)
                    return _ma >= cli_ver_major and _mi >= cli_ver_minor and _pa >= cli_ver_patch
    raise Exception(
        f"Cannot find mokucli {cli_ver_major}.{cli_ver_minor}.{cli_ver_patch}, please download "
        f"latest version of the CLI from "
        "https://www.liquidinstruments.com/software/utilities/ ")


class Moku:
    def __init__(self, ip, force_connect, ignore_busy,
                 persist_state, connect_timeout,
                 read_timeout, **kwargs):
        self.session = RequestSession(ip, connect_timeout,
                                      read_timeout, **kwargs)
        self.claim_ownership(force_connect, ignore_busy,
                             persist_state)

        props = self.describe()

        if int(props['firmware']) < compat_fw:
            raise IncompatibleMokuException(
                f"Incompatible Moku firmware, this version of "
                f"package supports firmware version"
                f"{compat_fw} or above.")

        self.firmware_version = props['firmware']
        self.hardware = props['hardware'].replace(":", "").lower()
        self.bitstreams = props['bitstreams']

    def _read_and_upload_stream(self, bs_name, chksum):
        bs_path = MOKU_DATA_PATH.joinpath(bs_name)
        if bs_path.exists():
            bs_data = bs_path.read_bytes()
            if not (chksum and sha256(bs_data).hexdigest() == chksum):
                self.upload("bitstreams", bs_name, bs_data)
        else:
            data_file = self._get_data_file(self.firmware_version)
            hw_dir = {"mokupro": "mokupro",
                      "mokugo": "mokugo", 
                      "mokulab": "moku20"}
            with tarfile.open(data_file) as _ts:
                bs_tarinfo = _ts.getmember(
                    f"{hw_dir[self.hardware]}/{bs_name}")
                bs_file = _ts.extractfile(bs_tarinfo)
                bs_data = bs_file.read()
                if not (chksum and sha256(
                        bs_data).hexdigest() == chksum):
                    self.upload("bitstreams", bs_name, bs_data)
                bs_file.close()

    def upload_bitstream(self, name):
        matching = [b for b in self.bitstreams if b["name"] == name]
        chksum = matching[0].get("checksum") if matching else None
        self._read_and_upload_stream(name, chksum)

    def set_connect_timeout(self, value):
        if not isinstance(value, tuple([int, float])):
            raise Exception("set_connect_timeout value should be "
                            "either integer or float")
        self.session.connect_timeout = value

    def set_read_timeout(self, value):
        if not isinstance(value, tuple([int, float])):
            raise Exception("read_timeout value should be either "
                            "integer or float")
        self.session.read_timeout = value

    def platform(self, platform_id):
        operation = f"platform/{platform_id}"
        self.upload_bitstream(f"{platform_id:02}-000")
        for i in range(0, platform_id):
            self.upload_bitstream(f"{platform_id:02}-000-{i:02}")
        return self.session.get("moku", operation)

    @staticmethod
    def _get_data_file(firmware_version):
        file_name = f'mokudata-{firmware_version}.tar.gz'
        path = MOKU_DATA_PATH.joinpath(file_name)
        if not path.exists():
            raise Exception(
                'Instrument files not available, please run '
                '`moku download --fw_ver={}` to '
                'download latest instrument data'.format(
                    firmware_version))
        return path

    def claim_ownership(
            self,
            force_connect=True,
            ignore_busy=False,
            persist_state=False):
        """
        Claim the ownership of Moku.

        :type force_connect: `boolean`
        :param force_connect: Force connection to Moku disregarding any existing connections

        :type ignore_busy: `boolean`
        :param ignore_busy: Ignore the state of instrument including any in progress data logging sessions and proceed with the deployment

        :type persist_state: `boolean`
        :param persist_state: When true, tries to retain the previous state of the instrument(if available)

        """
        operation = "claim_ownership"
        params = dict(
            force_connect=force_connect,
            ignore_busy=ignore_busy,
            persist_state=persist_state,
        )
        return self.session.post("moku", operation, params)

    def relinquish_ownership(self):
        """
        Relinquish the ownership of Moku.
        """
        operation = "relinquish_ownership"
        return self.session.post("moku", operation)

    def name(self):
        """
        name.
        """
        operation = "name"
        return self.session.get("moku", operation)

    def serial_number(self):
        """
        serial_number.
        """
        operation = "serial_number"
        return self.session.get("moku", operation)

    def summary(self):
        """
        summary.
        """
        operation = "summary"
        return self.session.get("moku", operation)

    def describe(self):
        """
        describe.
        """
        operation = "describe"
        return self.session.get("moku", operation)

    def calibration_date(self):
        """
        calibration_date.
        """
        operation = "calibration_date"
        return self.session.get("moku", operation)

    def firmware_version(self):
        """
        firmware_version.
        """
        operation = "firmware_version"
        return self.session.get("moku", operation)

    def get_power_supplies(self):
        """
        get_power_supplies.
        """
        operation = "get_power_supplies"
        return self.session.get("moku", operation)

    def get_power_supply(self, id):
        """
        get_power_supply.

        :type id: `integer`
        :param id: ID of the power supply

        """
        operation = "get_power_supply"
        params = dict(id=id, )
        return self.session.post("moku", operation, params)

    def set_power_supply(self, id, enable=True, voltage=3,
                         current=0.1):
        """
        set_power_supply.

        :type id: `integer`
        :param id: ID of the power supply to configure

        :type enable: `boolean`
        :param enable: Enable/Disable power supply

        :type voltage: `number`
        :param voltage: Voltage set point

        :type current: `number`
        :param current: Current set point

        """
        operation = "set_power_supply"
        params = dict(
            id=id,
            enable=enable,
            voltage=voltage,
            current=current,
        )
        return self.session.post("moku", operation, params)

    def get_external_clock(self):
        """
        get_external_clock.
        """
        operation = "get_external_clock"
        return self.session.get("moku", operation)

    def set_external_clock(self, enable=True):
        """
        set_external_clock.

        :type enable: `boolean`
        :param enable: Switch between external and internal reference clocks

        """
        operation = "set_external_clock"
        params = dict(enable=enable, )
        return self.session.post("moku", operation, params)

    def upload(self, target, file_name, data):
        """
        Upload files to bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Destination where the file should be uploaded to.

        :type file_name: `string`
        :param file_name: Name of the file to be uploaded

        :type data: `bytes`
        :param data: File content

        """
        target = validate_range(target, list(
            ['bitstreams', 'ssd', 'logs', 'persist', 'media']))
        operation = f"upload/{file_name}"
        return self.session.post_file(target, operation, data)

    def delete(self, target, file_name):
        """
        Delete files from bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Destination where the file should be uploaded to.

        :type file_name: `string`
        :param file_name: Name of the file to be deleted

        """
        target = validate_range(target, list(
            ['bitstreams', 'ssd', 'logs', 'persist', 'media']))
        operation = f"delete/{file_name}"
        return self.session.delete_file(target, operation)

    def list(self, target):
        """
        List files at bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Target directory to list files for

        """
        target = validate_range(target, list(
            ['bitstreams', 'ssd', 'logs', 'persist', 'media']))
        operation = "list"
        return self.session.get(target, operation)

    def download(self, target, file_name, local_path):
        """
        Download files from bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, logs, persist, media)
        :param target: Destination where the file should be downloaded from.

        :type file_name: `string`
        :param file_name: Name of the file to be downloaded

        :type local_path: `string`
        :param local_path: Local path to download the file

        """
        target = validate_range(target, list(
            ['bitstreams', 'ssd', 'logs', 'persist', 'media']))
        operation = f"download/{file_name}"
        return self.session.get_file(target, operation, local_path)

    def _modify_config(self, data=None):
        if data is None:
            data = {}
        return self.session.post_to_v2("config", data)

    def _modify_hardware(self, data=None):
        if data is None:
            data = {}
        return self.session.post_to_v2("hwstate", data)

    def _calibrate(self, data=None):
        if data is None:
            data = {}
        return self.session.post_to_v2("calibration", data)
