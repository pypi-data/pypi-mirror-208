#!/usr/bin/env python3
"""
Read values from the Keithley DMM6500.
"""

import argparse
import sys
import time

from mmcb import common
from mmcb import dmm_interface


##############################################################################
# command line option handler
##############################################################################


def check_arguments():
    """
    handle command line options

    --------------------------------------------------------------------------
    args : none
    --------------------------------------------------------------------------
    returns
        args : <class 'argparse.Namespace'>
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='Reads voltage or current from the Keithley DMM6500.'
    )
    parser.add_argument(
        '-c', '--capacitance',
        action='store_true',
        help='Read capacitance (F)')
    parser.add_argument(
        '--currentac',
        action='store_true',
        help='Read AC current (A)')
    parser.add_argument(
        '-i', '--currentdc',
        action='store_true',
        help='Read DC current (A)')
    parser.add_argument(
        '-r', '--resistance',
        action='store_true',
        help='Read two-wire resistance (\u03a9)')
    parser.add_argument(
        '-t', '--temperature',
        action='store_true',
        help='Read temperature (\u00b0C)')
    parser.add_argument(
        '--voltageac',
        action='store_true',
        help='Read AC voltage (V)')
    parser.add_argument(
        '-v', '--voltagedc',
        action='store_true',
        help='Read DC voltage (V)')

    args = parser.parse_args()

    return args


##############################################################################
# main
##############################################################################


def main():
    """ Read values from the Keithley DMM6500 """

    args = check_arguments()

    dmm = dmm_interface.Dmm6500()
    configure = {
            'capacitance': dmm.configure_read_capacitance,
            'currentac': dmm.configure_read_ac_current,
            'currentdc': dmm.configure_read_dc_current,
            'resistance': dmm.configure_read_resistance,
            'temperature': dmm.configure_read_temperature,
            'voltagedc': dmm.configure_read_dc_voltage,
            'voltageac': dmm.configure_read_ac_voltage,
    }

    # AC quantities sometimes return None on the first attempt
    retries = 3

    for function, required in vars(args).items():
        if not required:
            continue

        configure[function]()

        value = None
        for _ in range(retries):
            value = dmm.read_value()
            if value is not None:
                break
            time.sleep(0.1)

        print(f'{function}, {common.si_prefix(value)}, {value}')


##############################################################################
if __name__ == '__main__':
    sys.exit(main())
