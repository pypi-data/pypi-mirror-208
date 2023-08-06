""" Command-line scripts for iCCF """

import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import argparse

from tqdm import tqdm

from . import iCCF
from . import meta_ESPRESSO
from .utils import get_ncores
# from .meta_ESPRESSO import calculate_ccf as calculate_ccf_ESPRESSO
from astropy.io import fits


def _parse_args_fits_to_rdb():
    desc = """
    This script takes a list of CCF fits files and outputs CCF activity 
    indicators to stdout, in rdb format.
    """
    parser = argparse.ArgumentParser(
        description=desc,
        prog='iccf-fits-to-rdb',
    )
    # parser.add_argument('column', nargs=1, type=int,
    #                     help='which column to use for histogram')
    parser.add_argument('--hdu', type=int, help='HDU number')
    parser.add_argument('--sort', action='store_true', default=True,
                        help='sort the output by the MJD-OBS keyword')
    parser.add_argument('--bis-harps', action='store_true', default=True,
                        help='do the bisector calculation as in HARPS')
    # parser.add_argument('--code', nargs=1, type=str,
    #                     help='code to generate "theoretical" samples '\
    #                          'to compare to the prior. \n'\
    #                          'Assign samples to an iterable called `samples`. '\
    #                          'Use numpy and scipy.stats as `np` and `st`, respectively. '\
    #                          'Number of prior samples in sample.txt is in variable `nsamples`. '\
    #                          'For example: samples=np.random.uniform(0,1,nsamples)')

    args = parser.parse_args()
    return args, parser


def fits_to_rdb():
    args, _ = _parse_args_fits_to_rdb()
    # print(args)

    bisHARPS = args.bis_harps
    hdu_number = args.hdu

    if sys.stdin.isatty():
        print('pipe something (a list of CCF fits files) into this script')
        sys.exit(1)
    else:
        files = [line.strip() for line in sys.stdin]
        # print(files)
        iCCF.indicators_from_files(files, hdu_number=hdu_number,
                                   sort_bjd=args.sort, BIS_HARPS=bisHARPS)


def _parse_args_make_CCF():
    desc = """
    This script takes a list of S2D or S1D fits files and calculates the CCF for
    a given RV array and a given mask. If no mask is provided, it uses the same
    as specified in the S2D/S1D file.
    """
    parser = argparse.ArgumentParser(description=desc, prog='iccf-make-ccf')

    help_mask = 'Mask (G2, G9, K6, M2, ...). '\
                'A file called `ESPRESSO_mask.fits` should exist.'
    parser.add_argument('-m', '--mask', type=str, help=help_mask)

    parser.add_argument('-rv', type=str,
                        help='RV array, in the form start:end:step [km/s]')

    default_ncores = get_ncores()
    help_ncores = 'Number of cores to distribute calculation; '\
                  f'default is all available ({default_ncores})'
    parser.add_argument('--ncores', type=int, help=help_ncores)

    help_ssh = 'An SSH user and host with which the script will try to find' \
               'required calibration files. It uses the `locate` and `scp`' \
               'commands to find and copy the file from the host'
    parser.add_argument('--ssh', type=str, metavar='user@host', help=help_ssh)

    parser.add_argument('--skip-flux-corr', action='store_true', default=False,
                        help='Skip the flux correction step')

    parser.add_argument('--s1d', action='store_true', default=False,
                        help='Whether the files are S1D')

    parser.add_argument('-s', '--safe', action='store_true', default=False,
                        help='Do not replace output CCF file if it exists')


    parser.add_argument('-q', '--quiet', action='store_true', default=False,
                        help='Do not print status messages')

    args = parser.parse_args()
    return args, parser


def make_CCF():
    args, _ = _parse_args_make_CCF()
    # print(args)

    if sys.stdin.isatty():
        print('pipe something (a list of S2D fits files) into this script')
        print('example: ls *S2D* | iccf-make-ccf [options]')
        sys.exit(1)
    else:
        files = [line.strip() for line in sys.stdin]

        for file in files:
            if not args.quiet:
                print('Calculating CCF for', file)
            header = fits.open(file)[0].header

            if args.rv is None:
                try:
                    OBJ_RV = header['HIERARCH ESO OCS OBJ RV']
                    start = header['HIERARCH ESO RV START']
                    step = header['HIERARCH ESO RV STEP']
                    end = OBJ_RV + (OBJ_RV - start)
                    if not args.quiet:
                        print('Using RV array from file:',
                              f'{start} : {end} : {step} km/s')
                    rvarray = np.arange(start, end + step, step)
                except KeyError:
                    print('Could not find RV start and step in file.',
                          'Please use the -rv argument.')
                    sys.exit(1)
            else:
                start, end, step = map(float, args.rv.split(':'))
                rvarray = np.arange(start, end + step, step)
                if not args.quiet:
                    print('Using provided RV array:',
                          f'{start} : {end} : {step} km/s')

            mask = args.mask
            if mask is None:
                try:
                    mask = header['HIERARCH ESO QC CCF MASK']
                except KeyError:
                    try:
                        mask = header['HIERARCH ESO PRO REC1 CAL25 NAME']
                        if 'ESPRESSO_' in mask:
                            mask = mask[9:11]
                    except KeyError:
                        print('Could not find CCF mask in file.',
                              'Please use the -m argument.')
                        sys.exit(1)
                if not args.quiet:
                    print('Using mask from file:', mask)

            inst = header['INSTRUME']

            # if 'BLAZE' in file: # these files are not de-blazed
            #     ignore_blaze = True
            # else:
            #     ignore_blaze = False

            if inst == 'ESPRESSO':
                meta_ESPRESSO.calculate_ccf(
                    file, mask=mask, rvarray=rvarray, ncores=args.ncores,
                    ssh=args.ssh, skip_flux_corr=args.skip_flux_corr,
                    s1d=args.s1d,
                    clobber=not args.safe, verbose=not args.quiet)

            elif inst == 'HARPS':
                print('dont know what to do with HARPS! sorry')


def _parse_args_compare():
    desc = """This script compared two CCF fits files"""
    parser = argparse.ArgumentParser(description=desc, prog='iccf-compare')

    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    return args, parser


def compare_ccfs():
    args, parser = _parse_args_compare()
    print(args)

    width = max(len(f) for f in args.files)
    I = [iCCF.Indicators.from_file(f) for f in args.files]
    print(width * ' ', end='  ')
    print(f"{'RV':11s}  {'RV error':10s}  {'FWHM':11s}")

    for file, i in zip(args.files, I):
        print(f'{file:{width}s}', end='')
        print(f'  {i.RV:10.7f}  {i.RVerror:10.7f}  {i.FWHM:10.7f}')

    fig, ax = I[0].plot()
    if len(I) > 1:
        for i in I[1:]:
            i.plot(ax)
    plt.show()

    # def check(self, verbose=False):
    #     """ Check if calculated RV and FWHM match the pipeline values """
    #     try:
    #         val1, val2 = self.RV, self.pipeline_RV
    #         if verbose:
    #             print('comparing RV calculated/pipeline:', end=' ')
    #             print(f'{val1:.{self._nEPS}f} / {val2:.{self._nEPS}f}')
    #         np.testing.assert_almost_equal(val1, val2, self._nEPS, err_msg='')
    #     except ValueError as e:
    #         no_stack_warning(str(e))

    #     try:
    #         val1, val2 = self.RVerror, self.pipeline_RVerror
    #         if verbose:
    #             print('comparing RVerror calculated/pipeline:', end=' ')
    #             print(f'{val1:.{self._nEPS}f} / {val2:.{self._nEPS}f}')
    #         np.testing.assert_almost_equal(val1, val2, self._nEPS, err_msg='')
    #     except ValueError as e:
    #         no_stack_warning(str(e))

    #     try:
    #         val1, val2 = self.FWHM, self.pipeline_FWHM
    #         if verbose:
    #             print('comparing FWHM calculated/pipeline:', end=' ')
    #             print(f'{val1:.{2}f} / {val2:.{2}f}')
    #             no_stack_warning(
    #                 'As of now, FWHM is only compared to 2 decimal places')
    #         np.testing.assert_almost_equal(val1, val2, 2, err_msg='')
    #     except ValueError as e:
    #         no_stack_warning(str(e))

    #     return True  # all checks passed!
