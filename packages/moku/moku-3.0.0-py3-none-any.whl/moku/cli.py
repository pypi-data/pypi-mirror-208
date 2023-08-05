#!/usr/bin/env python
import hashlib
import os
import sys
from argparse import ArgumentParser
from subprocess import Popen

import requests

from moku import MOKU_CLI_PATH, MOKU_DATA_PATH, __version__, \
    check_mokucli_version
from .version import compat_fw

parser = ArgumentParser()
subparsers = parser.add_subparsers(title="action", dest='action',
                                   description="Action to take")
subparsers.required = True


def get_moku_data_url(fw=None):
    return f'http://updates.liquidinstruments.com/static/mokudata-{fw or compat_fw}.tar.gz'


def download(args):
    local_data_path = os.path.join(MOKU_DATA_PATH,
                                   f'mokudata-{args.fw_ver}.tar.gz')
    try:
        r = requests.get(
            get_moku_data_url(args.fw_ver).replace('tar.gz', 'md5'))
        r.raise_for_status()  # Checks for any HTTP errors
        remote_hash = r.text.split(' ')[0]
        if os.path.exists(local_data_path):
            local_hash = hashlib.md5(
                open(local_data_path, 'rb').read()).hexdigest()
            if not args.force and remote_hash == local_hash:
                print(f"Instruments already up to date for firmware"
                      f"version {args.fw_ver}.")
                return
        else:
            os.makedirs(MOKU_DATA_PATH, exist_ok=True)
        print(f'Downloading latest instruments for '
              f'firmware version {args.fw_ver}...')
        with requests.get(get_moku_data_url(args.fw_ver),
                          stream=True) as r:
            r.raise_for_status()  # Check for any HTTP errors
            length = int(r.headers['content-length'])
            recvd = 0
            with open(local_data_path, 'wb+') as f:
                for chunk in r.iter_content(chunk_size=400000):
                    f.write(chunk)
                    recvd = recvd + len(chunk)
                    sys.stdout.write("\r[%-30s] %3d%%" %
                                     (
                                         '#' * int(
                                             30.0 * recvd / length),
                                         (100.0 * recvd / length)))
                    sys.stdout.flush()
                sys.stdout.write('\r[%-30s] Done!\n' % ('#' * 30))

            with open(local_data_path, 'rb') as f:
                print('Verifying download..')
                if hashlib.md5(f.read()).hexdigest() == remote_hash:
                    print('Download complete')
                else:
                    print(
                        'Unable to verify download, please try again')
    except requests.HTTPError as e:
        print("ERROR: Unable to retrieve updates "
              "from server.\n%s" % str(e))
        return
    except Exception as e:
        print("ERROR: Unexpected error.\n%s" % str(e))


parser_dl = subparsers.add_parser('download',
                                  help="Download instrument "
                                       "bitstreams.")
parser_dl.add_argument('--force', action='store_true')
parser_dl.add_argument('--fw_ver', '-v', type=int,
                       help="Firmware version",
                       default=compat_fw)

parser_dl.set_defaults(func=download)


def list(args):
    check_mokucli_version()
    proc = Popen([MOKU_CLI_PATH, "list"], stdout=sys.stdout,
                 stderr=sys.stderr)
    proc.wait()


parser_list = subparsers.add_parser('list',
                                    help="List mokus on the network")
parser_list.set_defaults(func=list)


def main():
    print("Moku Client Version %s" % __version__)
    args = parser.parse_args()
    args.func(args)


# Compatible with direct run and distutils binary packaging
if __name__ == '__main__':
    main()
