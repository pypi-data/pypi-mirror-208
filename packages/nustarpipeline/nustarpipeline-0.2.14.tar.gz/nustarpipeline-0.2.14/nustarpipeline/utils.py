import logging
from numpy import random
import copy
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil

# file_handler = logging.FileHandler(filename='nustar_utils_%s.log' % (strftime("%Y-%m-%dT%H:%M:%S", gmtime())))
# stdout_handler = logging.StreamHandler(sys.stdout)
# handlers = [stdout_handler, file_handler]
#
# logging.basicConfig(level=logging.DEBUG, format=' %(levelname)s - %(message)s', handlers=handlers)
#[%(asctime)s] {%(filename)s:%(lineno)d}
logger = logging.getLogger('')

from subprocess import Popen, PIPE, STDOUT

def log_subprocess_output(pipe):
    for line in iter(pipe.readline, b''): # b'\n'-separated lines
        logging.info(line.decode()[0:-1])

#original
#shell_cmd = os.environ['HOME'] + '/Soft/timingsuite/dist/Debug/GNU-MacOSX/timingsuite <timing_cmd.txt'


shell_cmd = 'timingsuite <timing_cmd.txt'




def run(cmd=shell_cmd):
    logger.info("------------------------------------------------------------------------------------------------\n")
    logger.info("**** running %s ****\n" % cmd)
    #out=subprocess.call(cmd, stdout=logger, stderr=logger, shell=True)
    process = Popen('export DYLD_LIBRARY_PATH=$HEADAS/lib;'+cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    with process.stdout:
        log_subprocess_output(process.stdout)
    out = process.wait()  # 0 means success

    logger.info("------------------------------------------------------------------------------------------------\n")

    logger.info("Command '%s' finished with exit value %d" % (cmd, out))

    return out

def get_obsids(src):
    from astroquery.heasarc import Heasarc
    from astropy.io import ascii
    heasarc = Heasarc()
    payload = heasarc._args_to_payload(mission='numaster', entry=src, radius='10 arcmin')
    table = heasarc.query_async(payload)

    table_body = table.content.decode().split('END')[-1].strip().split('\n')
    table_body_clean = [cc for cc in table_body if 'SCIENCE' in cc and 'archived' in cc]
    logger.info("************************************")
    logger.info(src)
    logger.info("************************************")
    logger.info(table_body_clean)
    logger.info("************************************")

    try:
        data = ascii.read(table_body_clean, format='fixed_width_no_header', delimiter=' ')
        logger.info(data['col5'])
        output = [str(x) for x in data['col5'].data]
    except:
        logger.warning('No OBSIDS')
        output =[]

    return output

def make_basic_fit():
    ff = open('files-auto.xcm', 'w')
    ff.write('stati cstat\n')
    ff.write('data 1:1 FPMA_sr_rbn.pi\n')
    ff.write('data 2:2 FPMB_sr_rbn.pi\n')
    ff.write('ignore bad\n')
    ff.write('ignore *:**-3.0,70.0-**\n')
    ff.write('abun wilm\nmodel tbabs*high*peg')
    ff.write('\n\n\n\n\n3\n70\n1\n\n\n\n\n3\n70\n1,.1\n\n')
    ff.write('query yes\n')
    ff.write('freeze 2,3\nfit\n\n')
    ff.write('tha 2,3\nfit\n\n')
    ff.write('rm -f mod_base.xcm\nsave mod mod_base.xcm\n')
    ff.write('setpl ene\ncpd basic-plot.gif/GIF\nplot ld del\n')
    ff.write('quit\n\n')
    ff.close()

    ff = open('files-iterative.xcm', 'w')
    ff.write('stati cstat\n')
    ff.write('data 1:1 FPMA_sr_rbn.pi\n')
    ff.write('data 2:2 FPMB_sr_rbn.pi\n')
    ff.write('ignore bad\n')
    ff.write('ignore *:**-3.0,70.0-**\n')
    ff.write('@mod_base.xcm\n')
    ff.write('query yes\n')
    ff.write('setpl ene\ncpd /XW\npl ld del\n')
    ff.close()

    #logger.debug(xspec_commands)
    status = run('xspec - files-auto.xcm')
    from IPython.display import Image
    from IPython.display import display
    _ = display(Image(filename='basic-plot.gif_2', format="gif"))
    return status

def plot_periodogram():
    with open('ef_pipe_periodogram_f.qdp') as ff:
        qdp_lines = ff.readlines()
    with open('tmp.qdp', 'w') as ff:
        ff.write(qdp_lines[0])
        ff.write('cpd tmp.gif/GIF\n')
        ff.write('scr white\n')
        ff.write('ma 17 on\n')
        ff.write('time off\n')
        ff.write('lab f\n')
        for ll in qdp_lines[2:]:

            ff.write(ll)
        ff.write('\n')


    run("qdp tmp.qdp")
    from IPython.display import Image
    from IPython.display import display
    _ = display(Image(filename='tmp.gif', format="gif"))
    return


efold_cmd='''14
1
list_evt.txt
%f
%f
ef_pipe
n
%d

%f
%f
1
0
'''

efold_orbit_cmd='''14
1
list_evt.txt
%f
%f
ef_pipe
y
%s
%d

%f
%f
1
0
'''

def get_efold_frequency(nu_min, nu_max, min_en=3., max_en=20., n_bins=32, unit='A',orbitfile=None,
                        actual_search=True):
    """It finds the spin frequency using epoch folding

    Args:
        nu_min (float): the minimum search frequency
        nu_max (float): the maximum search frequency
        min_en (float, optional): the minimum energy of events to be used. Defaults to 3 keV.
        max_en (float, optional):  the maximum energy of events to be used.. Defaults to 20 keV.
        n_bins (int, optional): number of pulse bins to use. Defaults to 32.
        unit (str, optional): the NuSTAR unit to use. Defaults to 'A'.
        orbitfile (str, optional): The orbit file for correction. Defaults to None.
        actual_search (bool, optional): If true it will run the epoch folding, 
                                        if false it will read the output of aprevious search stored in the file ef_pipe_res.dat. 
                                        Defaults to True.

    Raises:
        FileExistsError: FileExistsError in case the orbit file is given but not found

    Returns:
        float: the most probable spin frequency 
    """                        

    if actual_search:
        with open('list_evt.txt', 'w') as ff:
            ff.write('source%s.evt' % unit)

        with open('timing_cmd.txt', 'w') as ff:
            if orbitfile is None:
                ff.write(efold_cmd % (min_en, max_en, n_bins, nu_min, nu_max))
            else:
                if not os.path.isfile(orbitfile):
                    raise FileExistsError('File %s does not exist' % orbitfile)

                ff.write(efold_orbit_cmd % (min_en, max_en, orbitfile, n_bins, nu_min, nu_max))

        run()

    plot_periodogram()

    x = np.loadtxt('ef_pipe_res.dat', dtype=np.double)

    return x[2]

def get_nu_search_limits(filename, freq_search_interval=0.2, plot_filename=None, nyquist_factor=1, min_frequency=1e-4, max_frequency=10.):
    """It uses the Lomb-Scargle periodogram to find a range of spin frequencies to explore
        to find a reliable periodicity

    Args:
        filename (_type_): name of the light curve in fits format to load
        freq_search_interval (float, optional): it will provide a search interval from (1-/+freq_search_interval) of the peak. Defaults to 0.2.
        plot_filename (str, optional): the name of output plot file. Defaults to None to avoid plotting.
        nyquist_factor (int, optional): Lomb Scargle nymquist factor, see https://docs.astropy.org/en/stable/timeseries/lombscargle.html. Defaults to 1.
        min_frequency (float, optional): it will search peaks only above this frequency (to avoid red-noise). Defaults to 1e-4
        max_frequency (float, optional): it will search peaks only below this frequency (to avoid red-noise). Defaults to 10

    Returns:
        nu_start, nu_stop: minimum and maximum frequencies to search
    """    

    import hratio
    lc_unbinned = hratio.light_curve()
    lc_unbinned.read_from_fits(filename=filename)
    from astropy.timeseries import LombScargle
    max_freq = 0.5/lc_unbinned._timedel_
    min_freq = max(1e-4,1./(lc_unbinned._tstop_ - lc_unbinned._tstart_ ))
    #frequencies = np.arange(min_freq, max_freq, min_freq)
    #power = LombScargle(lc_unbinned._times_, lc_unbinned._rates_).power(frequencies)
    frequencies, power = LombScargle(lc_unbinned._times_, lc_unbinned._rates_).autopower(nyquist_factor=nyquist_factor)
    
    mask = (frequencies >= min_frequency) & (frequencies <= max_frequency)
    max_freq = frequencies[mask][np.argmax(power[mask])]
    nu_start = max_freq * (1.-freq_search_interval)
    nu_stop = max_freq * (1.+freq_search_interval)
    logger.info("We suggest to explore from %f to %f Hz" %(nu_start, nu_stop))
    
    if plot_filename is not None:
        plt.figure()
        plt.loglog(frequencies, power) 
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('Power (Lomb-Scargle)')
        plt.axvspan(nu_start, nu_stop, alpha=0.5, color='cyan')
        plt.savefig(plot_filename)

    return nu_start, nu_stop
    

    
    




enphase_cmd='''17
list_evt.txt
none
%s
n
%d
%19.12e
%19.12e
%19.12e
0
n
%f
%f
%f
0
0
0
1000000000
'''

enphase_cmd_binfile='''17
list_evt.txt
none
%s
n
%d
%19.12e
%19.12e
%19.12e
0
y
%s
0
0
0
0
1000000000
'''

enphase_cmd_orbit='''17
list_evt.txt
none
%s
y
%s
%d
%19.12e
%19.12e
%19.12e
0
n
%f
%f
%f
0
0
0
1000000000
'''

enphase_cmd_orbit_binfile='''17
list_evt.txt
none
%s
y
%s
%d
%19.12e
%19.12e
%19.12e
0
y
%s
0
0
0
0
1000000000
'''


xselect_gti_filter='''dummy

read eve %s


filter time file %s
extract events
save events %s
yes


quit
no

'''

def make_enphase(freq,  min_en=3., max_en=70., en_step=0.5, n_bins=32, orbitfile=None, nudot=0, t_ref=0, user_gti=None):
    
    '''
    Wrapper on timingsuite to produce Energy - Phase matrixes for source and background for both FPM units.
    :param freq: spin frequency
    :param min_en: minimum energy (=3 keV
    :param max_en: mximum energy (=70 keV)
    :param en_step: energy step (=0.5 keV)
    :param n_bins: number of phase bins (=32)
    :param orbitfile: orbitfile for orbital correction (timingsuite) if None
    :param nudot: spinn requency derivative (=0)
    :param t_ref: reference time for folding (if <= 0, it takes the first time)
    ;param user_gti : user GTI file (defaults to None to avoid extraction)
    :return: it writes the fits files sourceA_ENPHASE.fits sourceB_ENPHASE.fits
                        backgroundA_ENPHASE.fits backgroundB_ENPHASE.fits
    '''

    for tt in ['source', 'background']:
        for unit in ['A', 'B']:
            with open('list_evt.txt', 'w') as ff:
                if user_gti is not None:
                    with open('gti_select_cmd.txt', 'w') as f2:
                        f2.write(xselect_gti_filter %('%s%s.evt' % (tt, unit), user_gti, '%s%s_filtered.evt' % (tt, unit) ))
                    run('rm -f %s%s_filtered.evt' % (tt, unit))
                    run('xselect < gti_select_cmd.txt')
                    ff.write('%s%s_filtered.evt' % (tt, unit) )
                else:
                    ff.write('%s%s.evt' % (tt, unit))

            if orbitfile is None:
                with open('timing_cmd.txt', 'w') as ff:
                    if type(en_step) == float:
                        ff.write(enphase_cmd % ('%s%s_ENPHASE.fits' % (tt, unit),
                                         n_bins, t_ref, freq, nudot, en_step, min_en, max_en) )
                    else:
                        if not os.path.isfile(en_step):
                            raise FileExistsError('File %s does not exist' % en_step)
                        ff.write(enphase_cmd_binfile % ('%s%s_ENPHASE.fits' % (tt, unit),
                                                n_bins, t_ref, freq, nudot, en_step))
            else:
                if not os.path.isfile(orbitfile):
                    raise FileExistsError('File %s does not exist' % orbitfile)

                with open('timing_cmd.txt', 'w') as ff:
                    if type(en_step) == float:
                        ff.write(enphase_cmd_orbit % ('%s%s_ENPHASE.fits' % (tt, unit), orbitfile,
                                     n_bins, t_ref, freq, nudot, en_step, min_en, max_en) )
                    else:
                        if not os.path.isfile(en_step):
                            raise FileExistsError('File %s does not exist' % en_step)
                        ff.write(enphase_cmd_orbit_binfile % ('%s%s_ENPHASE.fits' % (tt, unit), 
                        orbitfile, n_bins, t_ref, freq, nudot, en_step))
            
            run()
            shutil.copy('%s%s_ENPHASE.fits' % (tt, unit), '%s%s_ENPHASE_%03d.fits' % (tt, unit, n_bins))

            

def pad_matrices_with_zeros(x1_min, x1_max, pp1, dpp1, x2_min, x2_max, pp2, dpp2, tolerance=1e-2):
    '''
    :param x1_min:
    :param x1_max:
    :param pp1:
    :param dpp1:
    :param x2_min:
    :param x2_max:
    :param pp2:
    :param dpp2:
    :param tolerance:
    :return:
    '''
    if len(x1_min) == len(x2_min):
        diff = np.sum(x1_min - x2_min)
        if np.abs(diff) > tolerance:
            logger.warning("vector lower edges have same size but likely different values")
        return x1_min, x1_max, pp1, dpp1, x2_min, x2_max, pp2, dpp2

    if len(x1_min) < len(x2_min):
        new_x1_min, new_x1_max, new_pp1, new_dpp1 = pad_matrix_with_zeros(x1_min, x1_max, pp1, dpp1, x2_min, x2_max)
        return new_x1_min, new_x1_max, new_pp1, new_dpp1, x2_min, x2_max, pp2, dpp2

    if len(x1_min) > len(x2_min):
        new_x2_min, new_x2_max, new_pp2, new_dpp2 = pad_matrix_with_zeros(x2_min, x2_max, pp2, dpp2, x1_min, x1_max)
        return x1_min, x1_max, pp1, dpp1, new_x2_min, new_x2_max, new_pp2, new_dpp2



def pad_matrix_with_zeros(x1_min, x1_max, pp1, dpp1, x2_min, x2_max):
    '''
    returns matrix padded with zeros to fill the gaps
    :param x1_min:
    :param x1_max:
    :param pp1:
    :param dpp1:
    :param x2_min:
    :param x2_max:
    :return:
    '''

    new_x1_min = []
    new_x1_max = []
    new_pp1 = []
    new_dpp1 = []
    n_bins = pp1.shape[1]
    for y, z in zip(x2_min, x2_max):
        found = False
        for i in range(len(x1_min)):
            if x1_min[i] == y:
                new_x1_min.append(x1_min[i])
                new_x1_max.append(x1_max[i])
                new_pp1.append(pp1[i, :])
                new_dpp1.append(dpp1[i, :])
                found = True

        if not found:
            new_x1_min.append(y)
            new_x1_max.append(z)
            new_pp1.append(np.zeros(n_bins))
            new_dpp1.append(np.zeros(n_bins))

    if len(x2_min) != len(new_x1_min):
        raise RuntimeError('Padding matrix with zeros gave wrong sizes !!')

    return np.array(new_x1_min), np.array(new_x1_max), np.array(new_pp1), np.array(new_dpp1)


def read_one_matrix(kind, unit, background_difference_limit=-1, use_counts=False, subtract_background=True):
    '''
    Read matrix from one NuSTAR unit and optionally subtract the background.
    Note that if background_difference_limit>0, the output source and background matrixes might have different shape

    :param kind: 'E' for Energy-Phase, 'T' for Time-Phase
    :param unit: 'A' or 'B' for FPM unit
    :param background_difference_limit:
            =0 does not subtract the background
            <0 subtracts the background after padding background matrix with zeros
            >0  if sizes of source and background matrices differs by more than this value, it will skip subtraction
    :param use_counts: if correcting for the exposure
    :return: x_min lower edge of time or energy bins
             x_min upper edge of time or energy bins,
             pp matrix
             dpp matrix of uncertainties
             pp_b background matrix
             dpp_b matrix of background uncertainties
             
    '''
    import astropy.io.fits as pf

    if not (unit == 'A' or unit == 'B'):
        raise UserWarning('The unit must be A or B, you have %s ' % unit)

    if kind == 'E':
        fname_src = 'source%s_ENPHASE.fits' % unit
        fname_bck = 'background%s_ENPHASE.fits' % unit
        key1 = 'E_MIN'
        key2 = 'E_MAX'
    elif kind == 'T':
        key1 = 'T_START'
        key2 = 'T_STOP'
        fname_src = 'source%s_TPHASE.fits' % unit
        fname_bck = 'background%s_TPHASE.fits' % unit
    else:
        raise UserWarning('The kind of matrix can be E or T, you gave %s' % kind)

    ff = pf.open(fname_src, 'readonly')
    t_minA = ff[1].data[key1]
    t_maxA = ff[1].data[key2]
    ptA = ff[1].data['MATRIX']
    dptA = ff[1].data['ERROR']
    if 'Exposure' in ff[1].data.names:
        exposureA = ff[1].data['Exposure']
    else:
        exposureA = np.ones(ptA.shape)
    ff.close()

    ff = pf.open(fname_bck, 'readonly')
    t_minAb = ff[1].data[key1]
    t_maxAb = ff[1].data[key2]
    ptbA = ff[1].data['MATRIX']
    dptbA = ff[1].data['ERROR']
    if 'Exposure' in ff[1].data.names:
        exposure_bA = ff[1].data['Exposure']
    else:
        exposure_bA = np.ones(ptbA.shape)
    ff.close()

    if use_counts:
        ptA *= exposureA
        dptA *= exposureA
        ptbA *= exposure_bA
        dptbA *= exposure_bA

    if background_difference_limit < 0:
        t_minA, t_maxA, ptA, dptA, t_minAb, t_maxAb, ptbA, dptbA = \
            pad_matrices_with_zeros(t_minA, t_maxA, ptA, dptA, t_minAb, t_maxAb, ptbA, dptbA)
        if subtract_background:
            ptA -= ptbA
            dptA = np.sqrt(dptbA ** 2 + dptA ** 2)
            logger.info('Subtracted the background, possibly padded with zeros')
        else:
            logger.info("Not subtracting the background")
    elif background_difference_limit > 0:
        if np.abs(len(t_minA) - len(t_minAb)) < background_difference_limit and subtract_background:
            indA, indAb = get_ind_combine(t_minA, t_minAb)
            t_minA = t_minA[indA]
            t_maxA = t_maxA[indA]

            ptA = ptA[indA, :] - ptbA[indAb, :]
            dptA = np.sqrt(dptA[indA, :] ** 2 + dptbA[indAb, :] ** 2)
            logger.info('Subtracted the background')
        else:
            logger.info('We do not subtract the background: difference in matrix dimension is %d and subtract_backgroun is %b' %
                        (np.abs(len(t_minA) - len(t_minAb)), subtract_background))


    return t_minA, t_maxA, ptA, dptA, ptbA, dptbA

def read_and_sum_matrixes(kind, background_difference_limit=-1, use_counts=False, subtract_background=True):
    '''
    Reads and sum matrixes fromt he two NuSTAR units
    (Note that if background_difference_limit>0, the method is not tested as the output source and background matrixes might have different shape)
    
    :param kind: 'E' for ENERGY-Phase, 'T'  for 'TIME-Phase
    :param background_difference_limit: if >0 removes at most this number of rows to match background and source matrixes
                                        if <=0 it pads the smalle matrix with zeros (default -1)
    :param subtract background: boolean to subtract the background (default true)
    :return:
    x_min array of minimum times or energies 
    x_max array of maximum times or energies
    pp matrix
    dpp matrix uncertainties
    pp_b backound matrix
    dpp_b background matrix uncertainties
    '''
    t_minA, t_maxA, ptA, dptA, ptbA, dptbA = read_one_matrix(kind, 'A', background_difference_limit=background_difference_limit, use_counts=use_counts
                                                , subtract_background=subtract_background)
    t_minB, t_maxB, ptB, dptB, ptbB, dptbB = read_one_matrix(kind, 'B', background_difference_limit=background_difference_limit, use_counts=use_counts
                                                , subtract_background=subtract_background)

    if background_difference_limit > 0 :
        indA, indB = get_ind_combine(t_minA, t_minB)
        t_min = t_minA[indA]
        t_max = t_maxA[indA]
        pp = ptA[indA, :] + ptB[indB, :]
        dpp = np.sqrt(dptA[indA, :] ** 2 + dptB[indB, :] ** 2)
        pp_b = ptbA[indA, :] + ptbB[indB, :]
        dpp_b = np.sqrt(dptbA[indA, :] ** 2 + dptbB[indB, :] ** 2)
        
    else:
        t_min, t_max, ptA, dptA, t_minB, t_maxB, ptB, dptB = \
            pad_matrices_with_zeros(t_minA, t_maxA, ptA, dptA, t_minB, t_maxB, ptB, dptB)
        _, _, ptbA, dptbA, t_minB, t_maxB, ptbB, dptbB = \
            pad_matrices_with_zeros(t_minA, t_maxA, ptbA, dptbA, t_minB, t_maxB, ptbB, dptbB)
        #print(ptA.shape, ptB.shape, ptbA.shape,  ptbB.shape)
        pp = ptA + ptB
        dpp = np.sqrt(dptA ** 2 + dptB ** 2)
        pp_b = ptbA + ptbB
        dpp_b = np.sqrt(dptbA ** 2 + dptbB ** 2)
        

    logger.info('Matrix for unit A has size %d x %d ' % (ptA.shape[0], ptA.shape[1]))
    logger.info('Matrix for unit B has size %d x %d ' % (ptB.shape[0], ptB.shape[1]))
    logger.info('Background Matrix for unit A has size %d x %d ' % (ptbA.shape[0], ptbA.shape[1]))
    logger.info('Background Matrix for unit B has size %d x %d ' % (ptbB.shape[0], ptbB.shape[1]))
    logger.info('The combined matrix has size %d x %d' % (pp.shape[0], pp.shape[1]))

    return t_min, t_max, pp, dpp, pp_b, dpp_b

def get_ind_combine_engine(x1, x2):
    '''
    Util function to find index of common values in x1 and x2
    :param x1:
    :param x2:
    :return:
    '''
    ind1 = []
    ind2 = []
    n_removed = 0
    for i in range(len(x1)):
        not_found = True
        for j in range(max((i - n_removed), 0), len(x2)):
            if x1[i] == x2[j]:
                ind1.append(i)
                ind2.append(j)
                not_found = False
                logger.debug("Found %d %d" % (i, j))
                break
        if not_found:
            logger.debug("Remove %d" % i)
            n_removed += 1
    return ind1, ind2


def get_ind_combine(t_minA, t_minB):
    '''
    it calls get_ind_combine_engine after sorting for length
    :param t_minA:
    :param t_minB:
    :return:
    '''
    if len(t_minA) == len(t_minB):
        return np.arange(len(t_minA)), np.arange(len(t_minB))
    elif len(t_minA) < len(t_minB):
        return get_ind_combine_engine(t_minA, t_minB)
    else:
        indA, indB =get_ind_combine_engine(t_minB, t_minA)
        return indB, indA


tphase_cmd='''12
list_evt.txt
none
%s
n
%d
%19.12e
%19.12e
%19.12e
0
n
%f
0
0
%f
%f
'''

tphase_cmd_orbit='''12
list_evt.txt
none
%s
y
%s
%d
%19.12e
%19.12e
%19.12e
0
n
%f
0
0
%f
%f
'''

def make_tphase(freq,  min_en=3., max_en=70., t_step=1000, n_bins=32, orbitfile=None, nudot=0, t_ref=0, user_gti=None):
    """It builds the time-phase matrix

    Args:
        freq (float): folding frequency in Hertz
        min_en (float, optional): minimum energy to accumulate the matrix. Defaults to 3..
        max_en (float, optional): maximum energy to accumulate the matrix. Defaults to 70..
        t_step (int, optional): time step. Defaults to 1000.
        n_bins (int, optional): number of bins of the pulse profile. Defaults to 32.
        orbitfile (string, optional): name of the orbit correction file. Defaults to None.
        nudot (int, optional): frequency derivative. Defaults to 0.
        t_ref (int, optional): folding reference time (<=0 it takes the first time). Defaults to 0 to take the first time.
        user_gti (str, optional): file name for user GTI, default None skips the GTI selection

    Raises:
        It writes the time phase matrixes in fits format
    """    
    for tt in ['source', 'background']:
        for unit in ['A', 'B']:
            with open('list_evt.txt', 'w') as ff:
                if user_gti is not None:
                    with open('gti_select_cmd.txt', 'w') as f2:
                        f2.write(xselect_gti_filter %('%s%s.evt' % (tt, unit), user_gti, '%s%s_filtered.evt' % (tt, unit) ))
                    run('rm -f %s%s_filtered.evt' % (tt, unit))
                    run('xselect < gti_select_cmd.txt')
                    ff.write('%s%s_filtered.evt' % (tt, unit) )
                else:
                    ff.write('%s%s.evt' % (tt, unit))

            with open('timing_cmd.txt', 'w') as ff:
                if orbitfile is None:
                    ff.write(tphase_cmd % ('%s%s_TPHASE.fits' % (tt, unit),
                                     n_bins, t_ref, freq, nudot, t_step, min_en, max_en) )
                else:
                    if not os.path.isfile(orbitfile):
                        raise FileExistsError('File %s does not exist' % orbitfile)
                    ff.write(tphase_cmd_orbit % ('%s%s_TPHASE.fits' % (tt, unit), orbitfile,
                                           n_bins, t_ref, freq, nudot, t_step, min_en, max_en))

            run()
            shutil.copy('%s%s_TPHASE.fits' % (tt, unit), '%s%s_TPHASE_%03d.fits' % (tt, unit, n_bins))








def rebin_matrix(e_min_matrix, e_max_matrix, pp_input_matrix, dpp_input_matrix, min_s_n = 50, only_pulsed=False, use_counts=False, background_matrix=None, flip = False):
    '''

    :param e_min_matrix: array with minimum energy of each bin
    :param e_max_matrix: array with maximum energy of each bin
    :param pp_input_matrix: 2-d array with pulse profiles
    :param dpp_input_matrix: 2-d array with pulse profile uncertainties
    :param min_s_n: minimum S/N for rebin
    :param only_pulsed:  it subtracts the average value before rebinning
    ;param background_matrix a couple (background, background_uncertainty)
    :param flip : boolean ; if True rebin matrix from the last channel
    :return:
    new_e_mins rebinned array with minimum energy of each bin
    new_e_maxs rebinned array with maximum energy of each bin
    new_pulses rebinned 2-d array with pulse profiles
    dnew_pulses rebinned 2-d array with pulse profile uncertainties
    (new_background rebinned 2-d array with background pulse profiles
    dnew_background rebinned 2-d array with background pulse profiles uncertainties) - returned only if background is not None !
    '''
    e_min = copy.deepcopy(e_min_matrix)
    e_max = copy.deepcopy(e_max_matrix)
    pp_input = copy.deepcopy(pp_input_matrix)
    dpp_input = copy.deepcopy(dpp_input_matrix)

    if flip:
        logger.info('Rebinning starts from highest energy/time channel')
        e_min = np.flip(e_min)
        e_max = np.flip(e_max)
        pp_input = np.flip(pp_input)
        dpp_input = np.flip(dpp_input)

    new_pulses = []
    dnew_pulses = []
    new_e_mins = []
    new_e_maxs = []
    i1 = 0
    rebinned_index = 0

    pp = copy.deepcopy(pp_input)
    dpp = copy.deepcopy(dpp_input)

    if background_matrix is not None:
        background = [[],[]]
        background[0] = copy.deepcopy(background_matrix[0])
        background[1] = copy.deepcopy(background_matrix[1])
        if flip:
            backk = np.flip(background[0])
            dbackk = np.flip(background[1])
            pp_b = copy.deepcopy(backk)
            dpp_b = copy.deepcopy(dbackk)
        else:
            pp_b = copy.deepcopy(background[0])
            dpp_b = copy.deepcopy(background[1])

        new_pulses_b = []
        dnew_pulses_b = []

    while i1 < len(e_min) - 1:
        p1 = copy.copy(pp[i1, :])
        dp1 = copy.copy(dpp[i1, :])
        if background_matrix is not None:
            p1_b = copy.copy(pp_b[i1, :])
            dp1_b = copy.copy(dpp_b[i1, :])
        logger.debug('%d' % i1)
        for i2 in range(i1 + 1, len(e_min)):

            ind = dp1 > 0
            if only_pulsed:
                s_n = np.sum(np.abs(p1[ind] - np.mean(p1[ind]))) / np.sqrt(np.sum(dp1[ind] ** 2))
            else:
                s_n = np.sum(np.abs(p1[ind])) / np.sqrt(np.sum(dp1[ind] ** 2))

            logger.debug(s_n)
            #print(np.sum(np.abs(p1)), np.sqrt(np.sum(dp1 ** 2)), s_n)
            if s_n >= min_s_n or i2 == len(e_min) - 1:
                if use_counts:
                    new_pulses.append(p1)
                    dnew_pulses.append(dp1)
                else:
                    new_pulses.append(p1/float(i2-i1))
                    dnew_pulses.append(dp1/float(i2-i1))
                if background_matrix is not None:
                    if use_counts:
                        new_pulses_b.append(p1_b)
                        dnew_pulses_b.append(dp1_b)
                    else:
                        new_pulses_b.append(p1_b/float(i2-i1))
                        dnew_pulses_b.append(dp1_b/float(i2-i1))
                if flip:
                    new_e_mins.append(e_min[i2 - 1])
                    new_e_maxs.append(e_max[i1])
                else:
                    new_e_mins.append(e_min[i1])
                    new_e_maxs.append(e_max[i2 - 1])
                logger.debug("Boom %f %d %d " % (s_n, i1, i2))
                # print("Boom", s_n, i1, i2)
                # print(np.mean(p1)/float(i2-i1), np.mean(dp1)/float(i2-i1))
                i1 = i2
                logger.debug('Rebinned index : %d' % rebinned_index)
                # print('Rebinned index : %d' % rebinned_index)
                rebinned_index += 1
                break
            else:
                logger.debug("i2 %d" % i2)

                p1 += pp[i2, :]
                dp1 = np.sqrt(dp1 ** 2 + dpp[i2, :] ** 2)
                if background_matrix is not None:
                    p1_b += pp_b[i2, :]
                    dp1_b = np.sqrt(dp1_b ** 2 + dpp_b[i2, :] ** 2)
                    
                # print("i2", i2)
                # print(np.count_nonzero(p1), np.count_nonzero(pp[i2, :]))
                #It may happen that 1 background photon (negative rate) makes a bin to zero
                # if np.count_nonzero(p1) < old_nonzero:
                #     print(p1)
                #     print(pp[i2, :])
                #old_nonzero = np.count_nonzero(p1)


    logger.info('We rebinned from %d to %d bins at a minimum S/N of %.1f' % (len(e_min), len(new_e_mins), min_s_n))
    # not sure this is a good practice
    if background_matrix is None:
        if flip:
            return np.flip(np.array(new_e_mins)), np.flip(np.array(new_e_maxs)), np.flip(np.array(new_pulses)), np.flip(
                np.array(dnew_pulses))
        else:
            return np.array(new_e_mins), np.array(new_e_maxs), np.array(new_pulses), np.array(dnew_pulses)
    else:
        if flip:
            return np.flip(np.array(new_e_mins)), np.flip(np.array(new_e_maxs)), np.flip(np.array(new_pulses)), np.flip(np.array(dnew_pulses)), np.flip(np.array(new_pulses_b)), np.flip(np.array(dnew_pulses_b))
        else:
            return np.array(new_e_mins), np.array(new_e_maxs), np.array(new_pulses), np.array(dnew_pulses), np.array(new_pulses_b), np.array(dnew_pulses_b)


def pulsed_fraction_area(c, dc, background=None, background_error=None): 
    """It computes the pulsed fraction with the Area method (ref. )
    remember PF is a factor  of about 1.4 the other PFs

    Args:
        c (numpy array): the pulse profile
        dc (numpy array): the pulse profile uncertainty [used for error computation]

    Returns:
       numpy float: the pulsed fraction!
    """
    logger.debug('remember PF is a factor  of about 1.4 the other PFs')
    a0 = 0
    if background is not None and background_error is not None:
        a0 = subtract_background(a0, background,background_error)
    return np.sum((c - a0 ) - (np.min(c - a0) ) ) / np.sum( c-a0 )

def compute_a_b_sigma_a_sigma_b(counts, counts_err, K):
    """auxiliary function for Pf method by Archibald 2014 (and others)

    Args:
        counts (numpy array): the pulse profile
        counts_err (numpy array): the pulse profile uncertainties
        K (int): number of harmonics

    Returns:
        a, b, sigma_a, sigma_b (numpy arrays): these vectors
    """    
    N = np.size(counts)
    A = np.zeros(K)
    B = np.zeros(K)
    a = np.zeros(K)
    b = np.zeros(K)
    sigma2_a = np.zeros(K)
    sigma2_b = np.zeros(K)
    
    for k in range(K):
        
        argsinus = (2 * np.pi * (k + 1) * np.arange(1,N+1, dtype=float)) / N
        
        L = counts * np.cos(argsinus)
        
        M = counts * np.sin(argsinus)
        
        P = counts_err ** 2 * np.cos(argsinus) ** 2
        O = counts_err ** 2 * np.sin(argsinus) ** 2
        #
        A[k] = np.sum(L)
        
        B[k] = np.sum(M)
        
        SIGMA_A = np.sum(P)
        SIGMA_B = np.sum(O)
        #
        a[k] = A[k] / N
        
        b[k] = B[k] / N
        sigma2_a[k] =  SIGMA_A / N**2
        sigma2_b[k] =  SIGMA_B / N**2

    return a, b, sigma2_a, sigma2_b

def pulse_fraction_from_data_rms(counts, counts_err, n_harm=-1, background=None, background_error=None, plot=False, label='', verbose=False,
                                 statistics='cstat', level=0.1):
    
    """pulsed fractio computation
        following Archibald et al (2014) that uses de Jager et al. (1986)
    Args:
        counts (_type_): pulse profile
        counts_err (_type_): pulse profile uncertainty
        n_harm (int, optional): number of used harmonics. If <=0, it determines the optimal number. default -1
        :param level: minimum confidence level to stop number of harmonics (default 0.1, lower values give less harmonics)
        :param n_harm: maximum number of harmonics to use (default -1 takes the size of pulse profile)
        :param plot: plot the pulse profile
        :param label: to save the plot with name "rms_`label`.pdf", if label=='' it does not save the plot
        ;parma verbose (bool): if true it returns both pulsed_frac, n_harm, if false just the pulsed_frac
        ;param background the vector of the background
        ;param backgroun_error the uncertainty vector of the background        
        statistics (str, optional) : the method to compute the optimal number of harmonics (chi2, cstat, archibald) de cstat, see the function get_n_harm

    Returns:
        numppy double: pulsed fraction
    """
    from matplotlib import cm

    a0 = np.mean(counts)
    N = np.size(counts)
 
    if n_harm <= 0:
        K = get_n_harm(counts, counts_err, n_harm_min=2, n_harm_max=-1, statistics=statistics, level=level)
    elif n_harm > N/2:
        K = int(N/2)
    else:
        K = n_harm
   
    a, b, sigma2_a, sigma2_b = compute_a_b_sigma_a_sigma_b(counts, counts_err, K)

    somma = a[0:K] ** 2 + b[0:K] ** 2
    # print(somma)
    differenza = sigma2_a[0:K] + sigma2_b[0:K]
    bla = somma - differenza

    # print('diff: ',differenza)
    logger.debug('Pre background average %f' % a0)
    if background is not None and background_error is not None:
        a0 = subtract_background(a0, background, background_error)
    logger.debug('Post background average %f' % a0)

    summed_bla = np.sum(bla)

    if summed_bla <0 :
        logger.warning('Poissononian correction in pulse_fraction_from_data_rms gives a negative value, resetting it to zero ')
        summed_bla = 0
    PF_rms = np.sqrt( 2* summed_bla) / a0


    col = cm.viridis(np.linspace(0, 1,int(500)))
    if plot:
        import matplotlib.pyplot as plt
        f = np.linspace(0, 1, int(N))
        
        plt.errorbar(f, counts, yerr=counts_err, fmt='.',color=col[K])
        plt.plot(f, counts, linestyle='--', color=col[K])
        #plt.text(0.4,120,str(K)+'  harmonics',color = col[K])
        plt.xlabel('Phase')
        plt.ylabel('Counts')
        #plt.legend()
        if label != '':
            plt.savefig('rms_%s.pdf' % label)

    if verbose:
        return PF_rms, K
    else:
        return PF_rms

def subtract_background(a0, background, background_error):
    """subtracts background from the average

    Args:
        a0 (float): input average
        background (numpy array): vector of background values
        background_error (numpy array): vector of background values uncertainties

    Raises:
        Exception: if the subtracted continuun level is zero should we raise an exception ?

    Returns:
        a0 (loat): background subtracted average
    """
    ind = background_error > 0
    if np.sum(ind)>0:
        background_level = np.sum(background[ind]/background_error[ind]**2) / np.sum(1./background_error[ind]**2)
        logger.debug('Background level %f' % background_level)
        a0_out = a0 - background_level
        if a0 == 0:
            a0_out = background_level
            logger.debug('continuum level is zero')
            #raise Exception
    else:
        a0_out = a0
        logger.warning('Zero background level')
    return a0_out

def get_pulsed_fraction(e_min, e_max, pp, dpp, method_calc_rms='adaptive', output_file=None, force_recompute=False):
    """ thi functions is made to be a wrapper of different 
    methods to compute the pulsed fraction (it is incomplete)

    Args:
        e_min (_type_): _description_
        e_max (_type_): _description_
        pp (_type_): _description_
        dpp (_type_): _description_
        method_calc_rms (str, optional): _description_. Defaults to 'adaptive'.
        output_file (_type_, optional): _description_. Defaults to None.
        force_recompute (bool, optional): _description_. Defaults to False.

    Returns:
       
        output files: 
               1. the fit result
               2. the fit results to be plotted in a file
               3. Figure in pdf

    """
    if output_file is not None:
        filename = output_file
        if os.path.isfile(filename) and (force_recompute is False):
            ee_pulsed, dee_pulsed, pulsed_frac, dpulsed_frac = np.loadtxt(filename, unpack=True, skiprows=1)
            return ee_pulsed, dee_pulsed, pulsed_frac, dpulsed_frac

    ee_pulsed=(e_max+e_min)/2.
    dee_pulsed=(e_max-e_min)/2.
    pulsed_frac=np.zeros(len(e_min))
    dpulsed_frac=np.zeros(len(e_min))

    old_n_harm = pp.shape[1]

    for i in range(0, len(e_min)):
        x = pp[i,:]
        dx = dpp[i,:]
        if method_calc_rms=='minmax':
        #Min/MAX 
            pulsed_frac[i], dpulsed_frac[i] = pulse_fraction_from_data_min_max(x,dx)
        elif method_calc_rms=='fixednharm':
        #RMS with fixed n_harm
            pulsed_frac[i] = pulse_fraction_from_data_rms(x,dx, n_harm=3)
            dpulsed_frac[i] = get_error_from_simul(x,dx, pulse_fraction_from_data_rms, n_harm=3)
        else:
        #RMS with adaptive n_harm
            ## print(e_min[i], e_max[i])
            pulsed_frac[i] = fft_pulsed_fraction(x, dx, level=0.1, n_harm_min=2, n_harm_max=8, plot=False)
            dpulsed_frac[i] = get_error_from_simul(x,dx, fft_pulsed_fraction, level=0.1, n_harm_min=2, 
                                                         n_harm_max=8, verbose=False,  n_simul=300)
            #
    if output_file is not None:
        with open(output_file, 'w') as ff:
            ff.write("Energy Energy_error Pulsed_fraction Pulsed_fraction_Error\n")
            for i in range(0, len(e_min)):
                ff.write("%.2f %.2f %.4f %.4f\n" % (ee_pulsed[i], dee_pulsed[i], 
                            pulsed_frac[i], dpulsed_frac[i]))
    return ee_pulsed, dee_pulsed, pulsed_frac, dpulsed_frac

def elaborate_pulsed_fraction(ee_pulsed, dee_pulsed, pulsed_frac, dpulsed_frac, debug_plots=True, e1=10, e2=20, ylabel = 'PF',
                              stem='', poly_deg=[3, 3], title='', save_plot=True, e_threshold=0.3, 
                              division_derivative_order=2, max_n_high_lines = 2, forced_gaussian_centroids = [],
                              forced_gaussian_amplitudes = [],
                              forced_gaussian_sigmas = [],
                              y_lim=[0,1], 
                              noFe=False, threshold_p_value=5e-2):
    """This function implements the logics to perform a fit of the pulsed fraction.
    It first interpolates the pulsed fraction with a spline to find extremes of the function.
    Then it performs a fit with a polynomial plus gaussians.
    The general idea is to split the pulsed fraction into two regions, based on the flex of the function.
    Then to fit the lower energy checking for a gaussian feature in correspondence of the iron line complex.
    Then we look for minima of the PF in the highe part and inet gussians. 
    If there are too may minima, we reduce them.
    Logic is included to comply with few points.

    Args:
        ee_pulsed (numpy array): energy
        dee_pulsed (numpy array): energy error
        pulsed_frac (numpy array): pulsed fraction
        dpulsed_frac (numpy array): pulsed fraction uncertainty
        debug_plots (bool, optional): plot the derivative and the fits. Defaults to True.
        e1 (int, optional): lower energy to search the flex in this interval. Defaults to 10.
        e2 (int, optional): lower energy to search the flex in this interval. Defaults to 20.
        ylabel (str) : label of the y axis. Default 'PF', first, second for amplitude of 1st and 2nd hamonics, respectively
        Note that if you put e1>=e2, we will use only one interval.
        stem (str, optional): a string in fron of output plot names. Defaults to ''.
        poly_deg (int or list of int, optional): degree of the polynomial. Defaults to 3. If <0, it inreases the value until a p-value of 
                                                at least threshold_p_value is reached
        title (str, optional): title of the plots. Defaults to ''.
        save_plot (bool, optional): if plots should be saved Defaults to True.
        e_threshold (float, optional): if energies of PF minima differ in relative terms less than this values, they are reduced.
                                       ex.: if the algorithm finds minima at 32 and 35 keV, it retains only 32.
                                       This is used also as a range for the centroid search from (1-e_treshold)*e_centroid to 
                                       (1+e_treshold)*e_centroid Defaults to 0.3.
        division_derivative_order (int, optional): order of the derivative to search for the division, if 2 it searches a flex. Defaults to 2.
        max_n_high_lines (int, optional): do not use more gaussians thn this. Defaults to 2.
        forced_gaussian_centroids (list, optional): you can force the initial centroid energies with this parameter. Defaults to [].
        forced_gaussian_amplitudes (list, optional): you can force the initial amplitudes with this parameter, if the length of the list 
                                                    is different from the one of forced_gaussian_centroids, it is unused. Defaults to [].
        forced_gaussian_sigmas (list, optional): you can force the initial sigmas with this parameter, if the length of the list 
                                                 is different from the one of forced_gaussian_centroids, it is unused. Defaults to [].
        y_lim : limits for the plotting. Defaults to [0,1]
        noFe : exclude the 6.4 keV Gaussian feature, defaults to False
        threshold_p_value : defaults to 1e-4 it is the threshold p-value above which the polynomial degree is acceptable
    Returns:
        two fitting objects for the two ranges (the output of utils.fit_pulsed_frac). if only one is used, the second is None.
     """    
    from scipy import interpolate

    if type(poly_deg) is not list:
        poly_deg = [poly_deg]
    else:
        poly_deg = poly_deg

    smoothing = interpolate.UnivariateSpline(ee_pulsed, pulsed_frac, w=1./dpulsed_frac, k=3)
    fake_en = np.linspace(ee_pulsed[0], ee_pulsed[-1], 1000)
    smoothed_pulsed_frac_deriv=smoothing.derivative(1)(fake_en)
    smoothed_pulsed_frac_deriv_2=smoothing.derivative(2)(fake_en)

    def get_zeros(energy,deriv,deriv_2,selection):
        positive = deriv[selection] > 0
        ind_extreme = np.where(np.bitwise_xor(positive[1:], positive[:-1]))
        #print(energy[selection][ind_extreme])
        if deriv_2 is not None:
            ind_zeros = deriv_2[selection][ind_extreme] > 0
            return energy[selection][ind_extreme][ind_zeros]
        else:
            ind_zeros = ind_extreme
            return energy[selection][ind_zeros]

    def get_minimum(energy, deriv, selection):
        ind_min = np.argmin(deriv[selection])
        return energy[selection][ind_min]

    if debug_plots:
        fig,axes = plt.subplots(1,2,sharex=True)
        axes[0].errorbar(ee_pulsed,pulsed_frac, xerr=dee_pulsed, yerr=dpulsed_frac, linestyle='')
        axes[0].set_xlabel('Energy [keV]')
        axes[0].set_ylabel('Pulsed Fraction')
        axes[0].plot(fake_en, smoothing(fake_en))

        pulsed_frac_deriv=np.gradient(pulsed_frac, ee_pulsed)
        axes[1].plot(ee_pulsed, (pulsed_frac_deriv))
        axes[1].plot(fake_en, smoothed_pulsed_frac_deriv)
        axes[1].set_xlabel('Energy [keV]')
        axes[1].set_ylabel('Pulsed Fraction Derivative')

    ind_range1 = (fake_en >= e1) & (fake_en <=e2)
    make_double_fit = True
    if np.sum(ind_range1) <= 0:
        make_double_fit = False

    if noFe:
        center=[]
        sigma =[]
        amplitude=[]
        n_gauss=0 
    else:
        center=[[6.5, 5.5, 7.5]]
        sigma=[[0.2,0,2.0]]
        amplitude=[[0,-1,1]]
        n_gauss=1

    e_turn = 0
    if make_double_fit:
        if division_derivative_order == 2:
            e_turn = get_zeros(fake_en, smoothed_pulsed_frac_deriv_2, None, ind_range1)
        else:
            e_turn = get_zeros(fake_en, smoothed_pulsed_frac_deriv, smoothed_pulsed_frac_deriv_2, ind_range1)
        
        if len(e_turn) == 0:
            logger.info('Using the minimum derivative instead of zero in dividing regimes')
            e_turn = get_minimum(fake_en, smoothed_pulsed_frac_deriv, ind_range1)
        else:
            logger.info('Getting a zero of derivative to divide regimes')
            e_turn = e_turn[0]

        logger.info("We separate PF fit at %f keV" % e_turn)

        if debug_plots:
            axes[0].axvline(e_turn, 0, 1, color='cyan')
            axes[1].axvline(e_turn, 0, 1, color='cyan')

        ind_low = ee_pulsed <= e_turn
        ind_high = ee_pulsed > e_turn
        logger.info('We use %d points in the low-energy' % np.sum(ind_low))
        
    else:
        #all values
        ind_low = ee_pulsed > 0
        #no value
        ind_high = ee_pulsed > 0

        if len(forced_gaussian_centroids) > 0:
            center += [ [ee, (1-e_threshold)*ee, (1+e_threshold)*ee] for ee in forced_gaussian_centroids]
            if len(forced_gaussian_sigmas) == len(forced_gaussian_centroids):
                sigma += [[ee,0,2*ee] for ee in forced_gaussian_sigmas ]
            else:
                sigma = [[1+0*ee,0,3] for ee in forced_gaussian_centroids]
            
            if len(forced_gaussian_amplitudes) == len(forced_gaussian_centroids):
                amplitude += [[ee,-2*ee,4*ee] for ee in forced_gaussian_amplitudes ]
            else:
                amplitude = [[0*ee,-2,2] for ee in forced_gaussian_centroids ]
            n_gauss = len(center)



    pulsed_fit_low = fit_pulsed_frac(ee_pulsed[ind_low],dee_pulsed[ind_low], 
                                        pulsed_frac[ind_low], dpulsed_frac[ind_low], n_gauss=n_gauss, 
                                       center=center,
                                        sigma=sigma,
                                        amplitude=amplitude, ylabel = ylabel,
                                       degree_pol=poly_deg[0], plot_final=True, stem=stem+'low', y_lim=y_lim,
                                       threshold_p_value=threshold_p_value)

    if make_double_fit:

        e_cyc = get_zeros(fake_en, smoothed_pulsed_frac_deriv, smoothed_pulsed_frac_deriv_2, fake_en>e_turn)
        
        if len(e_cyc)>1:
            logger.info("Checking for too close Gaussians in %d elements" % len(e_cyc))
            diff_e_cyc= ( 1- e_cyc[0:-1]/e_cyc[1:] )
            ind_stay = diff_e_cyc > e_threshold
    #         print(e_cyc)
    #         print(diff_e_cyc)
    #         print(ind_stay)
            e_cyc = [e_cyc[0]] + [ee for ee in e_cyc[1:][ind_stay]]
            logger.info("Kept %d gaussians" % len(e_cyc))
        
        n_gauss = len(e_cyc)
        if n_gauss > 0 and max_n_high_lines > 0 and len(forced_gaussian_centroids) == 0:
            center = [ [ee, (1-e_threshold)*ee, (1+e_threshold)*ee] for ee in e_cyc[0:max_n_high_lines]]
            sigma=[[1+0*ee,0,3] for ee in e_cyc]
            amplitude=[[0*ee,-2,2] for ee in e_cyc ]
        elif len(forced_gaussian_centroids) > 0:
            center = [ [ee, (1-e_threshold)*ee, (1+e_threshold)*ee] for ee in forced_gaussian_centroids]

            if len(forced_gaussian_sigmas) == len(forced_gaussian_centroids):
                sigma = [[ee,0,2*ee] for ee in forced_gaussian_sigmas ]
            else:
                sigma = [[1+0*ee,0,3] for ee in forced_gaussian_centroids]
            
            if len(forced_gaussian_amplitudes) == len(forced_gaussian_centroids):
                amplitude = [[ee,-2*ee,4*ee] for ee in forced_gaussian_amplitudes ]
            else:
                amplitude = [[0*ee,-2,2] for ee in forced_gaussian_centroids ]
            n_gauss = len(forced_gaussian_centroids)
        else:
            center = []
            sigma = []
            amplitude = []
            n_gauss = 0
            
        #print(center,sigma,amplitude)
        logger.info('We use %d points in the high-energy' % np.sum(ind_high))
        high_poly_deg = poly_deg[-1]
        
        if np.sum(ind_high) <= high_poly_deg + n_gauss * 3:
            logger.info("Reducing polynomial order")
            while (np.sum(ind_high) <= high_poly_deg + n_gauss * 3) and high_poly_deg >0:
                
                high_poly_deg -= 1
            
            if (np.sum(ind_high) <= high_poly_deg + n_gauss * 3):
                n_gauss = 0
                center = []
                sigma = []
                amplitude = []
                high_poly_deg=1
        
        logger.info('We fit an order %d polynomial in the high-energy section' % high_poly_deg)
        logger.info('We fit %d gaussians in the high-energy section' % n_gauss)
        
        pulsed_fit_high = fit_pulsed_frac(ee_pulsed[ind_high],dee_pulsed[ind_high], 
                                            pulsed_frac[ind_high], dpulsed_frac[ind_high], n_gauss=n_gauss, 
                                        center=center,
                                            sigma=sigma,
                                            amplitude=amplitude,
                                        degree_pol=high_poly_deg, plot_final=True, stem=stem+'high',
                                        y_lim=y_lim,ylabel = ylabel, threshold_p_value=threshold_p_value)
    else:
        pulsed_fit_high = None

    
    from matplotlib.pyplot import cm
    comps_low = pulsed_fit_low.eval_components(x=ee_pulsed[ind_low])
    bb_low = (pulsed_frac[ind_low] - pulsed_fit_low.best_fit) / dpulsed_frac[ind_low]
    if make_double_fit:
        comps_high = pulsed_fit_high.eval_components(x=ee_pulsed[ind_high])
        bb_high = (pulsed_frac[ind_high] - pulsed_fit_high.best_fit) / dpulsed_frac[ind_high]

    col =cm.viridis(np.linspace(0, 1, 6))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.2, 6.0), sharex=True, gridspec_kw={'height_ratios': [3, 1],
                                                                        'hspace': 0.0}
                                )
    ax1.errorbar(ee_pulsed,pulsed_frac, xerr=dee_pulsed, yerr=dpulsed_frac, linestyle=''
                , fmt='.', color=col[4], label='data')
    ax1.plot(ee_pulsed[ind_low], pulsed_fit_low.best_fit, '-', label='best fit (low)', color=col[0])
    ax1.plot(ee_pulsed[ind_low], comps_low['poly_'], '--', label='Polynomial (low)', color=col[1])
    if make_double_fit:
        ax1.plot(ee_pulsed[ind_high], pulsed_fit_high.best_fit, '-', label='best fit (high)', color=col[2])
        ax1.plot(ee_pulsed[ind_high], comps_high['poly_'], '--', label='Polynomial (high)', color=col[3])

    ax1.legend(loc='upper left')
    ax1.set_xscale('log')
    ax2.set_xlabel('E (keV)')
    ax1.set_ylabel(ylabel)
    ax1.set_ylim(y_lim)
    #ax1.set_xlim(x_lim)
    ax1.set_title(title)
    if noFe is False:
        ax1.axvline(6.5, 0,1, linestyle='--', color='cyan')
    for x in forced_gaussian_centroids:
        ax1.axvline(x, 0,1, linestyle='--', color='cyan')

    ax2.set_ylabel('Residuals')
    #ax1.set_ylim(-0.1, 1)
    if make_double_fit:
        ax2.errorbar(ee_pulsed, np.concatenate([bb_low, bb_high]), xerr=dee_pulsed, yerr=1., fmt='.', color=col[2])
    else:
        ax2.errorbar(ee_pulsed, bb_low, xerr=dee_pulsed, yerr=1., fmt='.', color=col[2])

        
    ax2.axhline(y=0, color='k', linestyle='--')
    if save_plot:
        plt.savefig(stem + 'global_pulsed_fitted.pdf')

    return pulsed_fit_low, pulsed_fit_high, e_turn

def fit_pulsed_frac(en, den, pf, dpf, stem=None, degree_pol=4, n_gauss=0, center=[],
                    sigma=[], amplitude=[],
                    plot_final=True, ylabel = 'PF', print_results=True, y_lim=[0,1.1], x_lim=[3,70], threshold_p_value=1e-4):
    '''
    this function will fit an input energy range of the pulse profile.
    the fitting function will be a simple polynomial + gaussian
    the aim is to retrieve basic gaussian parameters to be compared
    to those obtained in spectral analysis around Ecycl.
     output files: 1. the fit result
                   2. the fit results to be plotted in a file
                   3. Figure in pdf
    :param en: input energy
    :param den: input energy uncertainty
    :param pf: pulsed fraction
    :param dpf: pulsed fractio uncertainty
    :param stem: output prefix
    :param degree_pol: degree of the polynomial to fit. If <0, it inreases the value until a p-value of 
                                                at least threshold_p_value is reached
    :param n_gauss: number of gaussian lines
    :param center: array of centers of gaussians [[initial_value, min, max]]
    :param sigma: array of sigmas of gaussians [[initial_value, min, max]]
    :param amplitude: array of amplitude of gaussians [[initial_value, min, max]],
                        use negative values for absorption-like
    :param plot_final: if make a final plot
    :param ylabel: ylabel for the plot (defaults to 'PF')
    :param print_results: if results should be printed out in file
    ;param threshold_p_value: defaults to 1e-4 is the threshold p-value to stop increasing the number of polynomials
    :return:
    '''
    from matplotlib.pyplot import cm
    from lmfit.models import PolynomialModel, GaussianModel
    from scipy.stats import chi2

    if len(center) != n_gauss or len(sigma) != n_gauss or len (amplitude) != n_gauss:
        logger.error("You provided %d centers, %d sigmas, and %d amplitudes for %d gaussians" % (len(center), 
                            len(sigma), len(amplitude), n_gauss))
        return

    col = cm.viridis(np.linspace(0, 1, 6))

    if stem is not None:
        outputfile = open(stem + '_fit_pf.out', 'w')
    else:
        stem = ''
        outputfile = open('fit_pf.out', 'w')

    if degree_pol > 0:
        threshold_p_value = 1e-100
        running_degree_pol = degree_pol
    else:
        running_degree_pol = 1
    
    p_value = 0

    while p_value <= threshold_p_value:
        poly_mod = PolynomialModel(prefix='poly_', degree=running_degree_pol)
        pars = poly_mod.guess(pf, x=en, degree=running_degree_pol)
        mod = poly_mod

        for N in range(1, n_gauss+1):
            logger.debug("%d" % N)
            logger.debug("%g" % center[N - 1][0])
            gauss = GaussianModel(prefix='g' + str(N) + '_')
            pars.update(gauss.make_params())
            pars['g' + str(N) + '_center'].set(value=center[N - 1][0], min=center[N - 1][1], max=center[N - 1][2])
            pars['g' + str(N) + '_sigma'].set(sigma[N - 1][0], min=sigma[N - 1][1], max=sigma[N - 1][2])
            pars['g' + str(N) + '_amplitude'].set(amplitude[N - 1][0], min=amplitude[N - 1][1],
                                                max=amplitude[N - 1][2])
            mod = mod + gauss


        
        #initialfit = mod.eval(pars, x=en)

        out = mod.fit(pf, pars, x=en, weights = 1./dpf)
        p_value = 1 - chi2.cdf(x=out.chisqr, df = out.nfree)
        logger.info('poly_deg %d chi2 %f dof %d p-value %f' % (running_degree_pol , out.chisqr, out.nfree, p_value))
        running_degree_pol += 1
        if running_degree_pol >7:
            logger.info('Reached maximum polynomial degree')
            break

    bb = (pf - out.best_fit) / dpf

    comps = out.eval_components(x=en)
    logger.info(comps)

    if not plot_final:
        fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.8))
        axes[0].errorbar(en, pf, xerr=den, yerr=dpf, fmt='.', color=col[0])
        axes[0].plot(en, out.best_fit, '-', label='best fit', color=col[2])
        axes[0].legend(loc='upper left')
        axes[0].set_xlabel('E [keV]')
        axes[0].set_ylabel(ylabel)
        axes[0].set_ylim(y_lim)
        axes[0].set_xlim(x_lim)
        

        axes[1].errorbar(en, pf, xerr=den, yerr=dpf, fmt='.', color=col[0])
        for N in range(1, n_gauss+1):
            axes[1].plot(en, comps['g%d_' % N], '--', label='Gaussian %d' % N, color=col[3])
            axes[1].axvline(center[N - 1][0], 0, 1, linestyle='--', color='cyan')
        axes[1].plot(en, comps['poly_'], '--', label='Polynomial component', color=col[4])
        axes[1].legend(loc='upper left')
        axes[1].set_xlabel('E [keV]')
        axes[1].set_ylabel(ylabel)
        axes[1].set_ylim(y_lim)
        axes[1].set_xlim(x_lim)
        
        plt.savefig(stem + 'fit_results.pdf')

    #Is it of any use maybe to remove?
    if print_results:
        datafile = open(stem + 'model_components_fit.dat', 'w')
        datafile.write('# fit results \n')
        datafile.write('# E[0]       dE[1]       pf_bestfit[2]          poly[3]            gauss1...N [4]...[N+4] \n')
        for j in range(len(pf)):
            datafile.write(str(round(en[j], 5)).ljust(10) + str(round(den[j], 2)).ljust(10) +
                           str(round(out.best_fit[j], 5)).ljust(15) + str(round(comps['poly_'][j], 5)).ljust(15) + '\t')
            for S in range(1, n_gauss+1):
                datafile.write(str(round(comps['g' + str(S) + '_'][j], 8)).ljust(25) + '\t')
            datafile.write('\n')

        datafile.close()

    if plot_final:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.2, 6.0), sharex=True, gridspec_kw={'height_ratios': [3, 1],
                                                                              'hspace': 0.0}
                                       )
        ax1.errorbar(en, pf, xerr=den, yerr=dpf, fmt='.', color=col[4], label='data')
        ax1.plot(en, out.best_fit, '-', label='best fit', color=col[0])
        ax1.plot(en, comps['poly_'], '--', label='Polynomial', color=col[1])
        ax1.legend(loc='upper left')
        ax1.set_xscale('log')
        ax2.set_xlabel('E (keV)')
        ax1.set_ylabel(ylabel)
        ax1.set_ylim(y_lim)
        ax1.set_xlim(x_lim)
        for N in range(1, n_gauss+1):
            ax1.axvline(center[N - 1][0], 0, 1, linestyle='--', color='cyan')
        
        ax2.set_ylabel('Residuals')
        #ax1.set_ylim(-0.1, 1)
        ax2.errorbar(en, bb, xerr=den, yerr=1., fmt='.', color=col[2])
        ax2.axhline(y=0, color='k', linestyle='--')
        plt.savefig(stem + 'pulsed_fitted.pdf')

    logger.info(str(out.fit_report()))
    outputfile.write(out.fit_report())
    outputfile.close()

    with open(stem+'.json', 'w') as jf:
        out.params.dump(jf)

    return out


def explore_fit_mcmc(model_fitted, pars=[], hm_steps=7000, hm_walkers=2000, hm_jump=500, plot_corner=True, print_file=True,
                     stem='posterior'):
    '''
    this function explore the posterior parameter space obtained with a previous fit
    using mcmc
    outputs: - corner plot
             - Maximum Likelihood Estimation
             - Error @ 1,2,3 sigma  


    Parameters
    ----------
    model_fitted :  lmfit.model.ModelResult
        output of the fit procedure obtained with
        the function 'fit_pulsed_frac'
    pars :  lmfit.parameter.Parameters
        parameters of the fit (if not specified, we derive them from the results)
    hm_steps : INTEGER
        how many steps: number of steps for the MCMC, default = 7000
    hm_walkers : INTEGER
        how many walkers: number of walkers for MCMC, default = 2000
    hm_jump : INTEGER
        how many first step not to consider, default = 500
    plot_corner : BOOLEAN
        if the corner_plot has to be plotted

    Returns
    -------
    explore: lmfit.minimizer.MinimizerResult (result of the minimization using emcee)
    emcee_plot: corner plot of the posterior distribution


    '''
    import corner
    if hm_steps <= hm_jump :
        logger.error(" You almost did it!. However, the number of steps must be higher than the jumped ones:"
                     "hm_steps > hm_jump")

    if pars ==[]:
        pars = model_fitted.params.copy()

    explore = model_fitted.emcee(params=pars, steps=hm_steps, nwalkers=hm_walkers,
                                is_weighted=True, burn=hm_jump)
    if plot_corner:
        emcee_plot = corner.corner(explore.flatchain, labels=explore.var_names, show_titles=True,
                                   plot_datapoints=True,figsize = (16,16))
        emcee_plot.savefig(stem+'_corner.pdf')

    highest_prob = np.argmax(explore.lnprob)
    hp_loc = np.unravel_index(highest_prob, explore.lnprob.shape)
    mle_soln = explore.chain[hp_loc]

    pars2 = {}
    for el in pars.keys():
        if (pars[str(el)]).expr is None:
            pars2[str(el)] = pars[str(el)]

    for i, par in enumerate(pars2):
        pars2[par].value = mle_soln[i]

    fmt = '{:5s} {:11.5f} {:11.5f} {:11.5f}'.format

    logger.info('\nMaximum Likelihood Estimation from emcee ')
    logger.info('-------------------------------------------------')
    logger.info('Parameter MLE Value Median Value Uncertainty')

    for name, param in pars2.items():
        logger.info(fmt(name, param.value, explore.params[name].value, explore.params[name].stderr))

    logger.info('\Error estimates from emcee:')
    logger.info('------------------------------------------------------')
    logger.info('Parameter -3sigma -2sigma -1sigma median +1sigma +2sigma +3sigma')

    if print_file:
        with open(stem+'.json', 'w') as jf:
            explore.params.dump(jf)
        o_f_emcee = open(stem + '.out', 'w')
        o_f_emcee.write('# Maximum Likelihood Estimation from emcee \n#Parameter MLE Value Median Value Uncertainty \n')
        for name, param in pars2.items():
            o_f_emcee.write(fmt(name, param.value, explore.params[name].value, explore.params[name].stderr) + '\n')
        o_f_emcee.write(
            '#\Error estimates from emcee: \n#Parameter -3sigma -2sigma -1sigma median +1sigma +2sigma +3sigma \n')

        for name in pars2.keys():
            quantiles = np.percentile(explore.flatchain[name], [0.135, 2.275, 15.865, 50, 84.135, 97.725, 99.865])
            median = quantiles[3]
            err_m3 = quantiles[0] - median
            err_m2 = quantiles[1] - median
            err_m1 = quantiles[2] - median
            err_p1 = quantiles[4] - median
            err_p2 = quantiles[5] - median
            err_p3 = quantiles[6] - median
            fmt = '{:5s} {:8.4f} {:8.4f} {:8.4f} {:8.4f} {:8.4f} {:8.4f} {:8.4f}'.format
            logger.info(fmt(name, err_m3, err_m2, err_m1, median, err_p1, err_p2, err_p3))
            o_f_emcee.write(fmt(name, err_m3, err_m2, err_m1, median, err_p1, err_p2, err_p3) + '\n')

    o_f_emcee.close()

    from astropy.table import Table
    flatchain= Table.from_pandas(explore.flatchain)
    flatchain.write(stem+'.fits',overwrite=True)

    return explore, emcee_plot


def  error_from_simul_rms(counts, counts_err, n_simul=100, n_harm=3):

    return get_error_from_simul(counts, counts_err, pulse_fraction_from_data_rms,
                                n_simul=n_simul, n_harms=n_harm)

def get_error_from_simul(counts, counts_err, method, n_simul=100, use_poisson=True, background=None,
                         background_error=None, **kwargs):
    '''
    :param counts: vector of input data
    :param counts_err: vector of input data errors
    :param method: a fnction with the method to compute the quantity
    :param n_simul: number of simulations
    ;param background vector of background values
    ;param background_error vector of background errors
    :param kwargs: additional arguments to the function to be computed
    :return:
    '''

    simul_rms = []
    simul_harm = []
    fp_back = background
    fp_back_error = background_error

    if use_poisson:
        logger.debug('We use Poissonian statistics for simulation')
        to_simulate = counts
        if np.sum(counts==0):
            to_simulate[counts==0] = np.min(counts[counts>0])/2.0
            logger.warning("WARNING: some counts are zero in simulation, we use %f instead" % (np.min(counts[counts>0])/2.0) )
            #print(counts)
    else:
        logger.debug('We use Gaussian statistics for simulation')


    for i in range(n_simul):
        if use_poisson:
            fp = random.poisson(to_simulate)
            if background is not None:
                fp_back = random.poisson(np.ones(len(background))*background.mean())
                fp_back_error = np.sqrt(fp_back)
        else:
            fp = random.normal(counts, np.max( [np.ones(len(counts_err)), counts_err], axis=0))
            if background is not None and background_error is not None:
                fp_back = random.normal(background, np.max( [np.ones(len(background_error)), background_error], axis=0))
        if 'verbose' in kwargs and kwargs['verbose']:
            x,y = method(fp, counts_err, background=fp_back, background_error=fp_back_error, **kwargs)
            simul_rms.append(x)
            simul_harm.append(y)
        else:
            simul_rms.append(method(fp, counts_err, background=fp_back, background_error=fp_back_error, **kwargs))

    if 'plot' in kwargs and kwargs['plot']:
        fig, axes = plt.subplots(1,2)
        axes[0].hist(simul_rms, bins=10)
        axes[1].hist(simul_harm, bins=10)

    if 'verbose' in kwargs and kwargs['verbose']:
        return np.std(simul_rms), np.max(simul_harm), np.min(simul_harm)
    else:
        return np.std(simul_rms)

def get_n_harm(x, dx=None, level=0.1, n_harm_min=2, n_harm_max=-1, statistics='cstat'):
    """This returns the number of harmonics necessary to describe the signal in x with uncertainty dx
    at minimal Significance level (=1- confidence level) (note that for lower values, you get lower harmonics)
    Available statistics are: cstat, chi2, archibald.
    cstat is based on Kaastra et al (2017) https://doi.org/10.1051/0004-6361/201629319
    chi2 is a standard implementation
    archibald is from Archibald et al. (2014), appendix A (inaccurate !)

    Args:
        x (numpy array): signal
        dx (numpy array): signal uncertainty, necesssary only for chi2
        level (float, optional): minimum confidence . Defaults to 0.1.
        n_harm_min (int, optional): minimum number of harmonics. Defaults to 2.
        n_harm_max (int, optional): maximum number of harmonics. Defaults to -1.
        statistics (str, optional): methods, see above. Defaults to 'cstat'.

    Returns:
        int: number of necessary harmonics
    """

    if statistics == 'chi2' and dx is None:
        raise Exception('For chi2 statistics, you need to provide uncertaintis')
    
    from scipy.stats import chi2
    from scipy.stats import norm
    import cashstatistic as cstat

    # Quantile (the cumulative probability)
    q = 1 - (level / 2 )
    # Critical z-score, calculated using the percent-point function (aka the
    # quantile function) of the normal distribution
    z_star = norm.ppf(q)
    n = len(x)
    if n_harm_max < n_harm_min or n_harm_max+1 > n/2:
        logger.debug('n_harm max = %d' % n_harm_max)
        n_harm_max = n / 2 - 1

    n = len(x)
    fft = np.fft.fft(x)
    old_chi2_sf = -1.0
    #old_cstat = 1e10
    for n_harm in range(int(n_harm_min), int(n_harm_max)+1):
        mask = np.ones(n, dtype=np.cdouble)
        mask[n_harm:-(n_harm - 1)] = 0 + 0j
        ifft = np.fft.ifft(fft * mask)
        y = np.real(ifft)
        #Necessary to avoid infinite for zero uncertaity
        ind = dx > 0
        #print(ind)
        if statistics == 'chi2':
            chi2_val = np.sum(((x[ind] - y[ind]) / dx[ind]) ** 2)
            dof = max(1, n - (1 + 2 * (n_harm - 1)))
            chi2_sf = chi2.sf(chi2_val, dof)
            logger.debug('%d %f %d %f %f' % (n_harm, chi2_val, dof,  chi2_sf, old_chi2_sf))
            
            #Sometimes, we do ot reach the required level, but we cannot describe the pulse significantly better,
            # so we stop in any case (condition chi2_sf < old_chi2_sf)
            if chi2_sf > level or (chi2_sf < old_chi2_sf and chi2_sf > level/100.):
                logger.debug('chi2_sf = %e (level is %.5f) old_chi2_sf = %e' % (chi2_sf, level, old_chi2_sf))
                break
            old_chi2_sf = chi2_sf
            if n_harm == n_harm_max:
                logger.debug('maximum number of harmonics reached')
        elif statistics=='cstat':
            mask = (y>0) & (x>=0) # the second part should never be needed
            cstat_val = cstat.cash_mod(y[mask],x[mask]).sum()
            c_e, c_v = cstat.cash_mod_expectations(y[mask])
            tmp1 = np.sum(c_e)
            tmp2 = z_star * np.sqrt(np.sum(c_v))
            logger.debug("%d %e %e %e" %(n_harm, cstat_val, tmp1, tmp2 ))
            if  cstat_val < tmp1 + tmp2: 
                # These conditions are harmful
                # or cstat_val > old_cstat: #cstat_val > tmp1 - tmp2 and
                logger.debug('cstat = %e (expected is %e +/- %e) ' % (cstat_val, tmp1, tmp2))
                break
            #old_cstat = cstat_val
            if n_harm == n_harm_max:
                logger.debug('maximum number of harmonics reached')
        elif statistics == 'archibald':
            a,b,sigma_a,sigma_b = compute_a_b_sigma_a_sigma_b(x, dx, int(n_harm_max))
            m4 = 4*np.arange(1,n_harm_max+1)
            cumulative_sum = np.zeros(int(n_harm_max))
            for k in range(1,int(n_harm_max)):
                cumulative_sum[k] = np.sum( (a[0:k]/sigma_a[0:k])**2 + (b[0:k]/sigma_b[0:k])**2)
            #print(cumulative_sum)
            n_harm = np.argmax(cumulative_sum - m4) + 1
            #print("We stop at %d harmonics" % max_harm)
        else:
            raise Exception('Statistics %s is not implemented' % statistics)

    logger.debug("Used %d harmonics for pulse description" % n_harm)

    return n_harm

def fft_pulsed_fraction(x, dx, level=0.1, n_harm_min=2, n_harm_max=-1, plot=False, verbose=False, label='', 
                        background=None, background_error=None, statistics='cstat'):
    '''
    Computes the pulsed fraction using an FFT. It stops as soon as the pulse is described at better than level
    :param x: pulse profile
    :param dx: pulse profile uncertainty
    :param level: minimum confidence level to stop number of harmonics (default 0.1, lower values give less harmonics)
    :param n_harm_min: minimum number of harmonics to use (default 2)
    :param n_harm_max: maximum number of harmonics to use (default -1 takes the size of pulse profile)
    :param plot: plot the pulse profile
    :param lavel: to save the plot with name "rms_`label`.pdf", if label=='' it does not save the plot
    ;parma verbose (bool): if true it returns both pulsed_frac, n_harm, if false just the pulsed_frac
    ;param background the vector of the background
    ;param backgroun_error the uncertainty vector of the background
    ;param statistics : the method to compute the optimal number of harmonics (chi2, cstat, archibald) de cstat, see the function get_n_harm
    :return: pulsed fraction (float)
    '''
    
    from matplotlib import cm
    n = len(x)
    n_harm = get_n_harm(x, dx, level=level, n_harm_min=n_harm_min, n_harm_max=n_harm_max, statistics=statistics)
    fft = np.fft.fft(x)
    a = np.absolute(fft) / n
    if background is not None and background_error is not None:
        a[0] = subtract_background(a[0], background,background_error)
    
    pulsed_frac = np.sqrt(np.sum(a[1:n_harm] ** 2) + np.sum(a[-n_harm + 1:] ** 2)) / a[0]
    col = cm.viridis(np.linspace(0, 1,int(n_harm)+1))
    if plot:
        import matplotlib.pyplot as plt
        f = np.linspace(0, 1, n)
        #plt.errorbar(f, x, yerr=dx, fmt='.', label='data %s' % label, color = col[n_harm])
        #plt.plot(f, y, label='%d harmonics' % n_harm, linestyle='--', color = col[n_harm])
        plt.errorbar(f, x, yerr=dx, fmt='.', color=col[n_harm])
        fft = np.fft.fft(x)
        mask = np.ones(n, dtype=np.cdouble)
        mask[n_harm:-(n_harm - 1)] = 0 + 0j
        ifft = np.fft.ifft(fft * mask)
        y = np.real(ifft)
        plt.plot(f, y, linestyle='--', color=col[n_harm])
        #plt.text(0.4,120,str(n_harm)+'  harmonics',color = col[n_harm])
        plt.xlabel('Phase')
        plt.ylabel('Counts')
        #plt.legend()
        if label != '':
            plt.savefig('rms_%s.pdf' % label)
    if verbose:
        return pulsed_frac, n_harm
    else:
        return pulsed_frac

def pf_rms_counts(x,dx, background=None, background_error=None):
    '''
    param x : pulse profile
    param dx: error on pulse profile
    return: pf_counts
    '''
    avg_cts=np.mean(x)
    dev = (np.array(x)-avg_cts)**2
    devi = np.sum(dev-np.array(dx)**2)
    if background is not None and background_error is not None:
        avg_cts = subtract_background(avg_cts, background, background_error)
    pf_rms_cts = (1./ avg_cts) * np.sqrt( devi/len(x) )
    return pf_rms_cts


def pulse_fraction_from_data_min_max(x,dx):

    i_min = np.argmin(x)
    i_max = np.argmax(x)
    tmp1 = (x[i_min]+x[i_max])
    pulsed_frac = (x[i_max] - x[i_min]) / tmp1
    dpulsed_frac = 2*np.sqrt((x[i_max]/tmp1**2)**2 * dx[i_max]**2 + (x[i_min]/tmp1**2)**2 * dx[i_min]**2)

    return pulsed_frac, dpulsed_frac
import matplotlib.cm

def plot_matrix_as_image(ee, pp, kind='E', normalize=True,outfile=None, cmap=matplotlib.cm.gist_earth,
                         sliders=False, n_levels=30, min_level=None, max_level=None, source_name=None,
                         energy_on_y=True, axis=None, axis_cb=None, colorbar=True):
    '''
    :param ee: y-scale (time or energy)
    :param pp: Energy-Phase or Time-Phase matrix (# of rows must equal len(ee))
    :param kind: * 'E' energy phase
                 * 'T' Time-phase
                 * 'NE' energy phase with energy normalized to the cyclotron energy
    :param normalize: normalize each pulse at its average and divide by the standard deviation
    :param outfile: the file to save the figure as image (optional)
    ;param cmap the colormap of matplotlib, defaults to matplotlib.cm.gist_earth
    ;param sliders if True uses sliders
    ;param n_levels the number of linearly spaced contour levels
    ;param min_level the minimum level for contours
    ;param max_level the maximum level for contours
    ;param source_name if not None, it is used as plot title
    'param energy_on_y (def True) if plotting energy on vertical axis
    :return:
    '''

    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider
    # from matplotlib.widgets import Button

    if pp.shape[0] != len(ee):
        raise ImportError('len(ee) [%d] != # rows pp [%d]' % (len(ee), pp.shape[0]))
    pp1 = pp.copy()
    if normalize:
        for i in range(pp.shape[0]):
            x = pp[i, :]
            m = np.mean(x)
            s = np.std(x)
            pp1[i, :] = (x - m) / s

    phi = np.linspace(0, 1, pp.shape[1])
    if axis is None:
        fig = plt.figure(figsize=(5.5, 4.2))
        axis = plt.gca()
    # if sliders:
    #     plt.subplots_adjust(top=0.82)
    if min_level is None:
        min_level = np.min(pp1)
    if max_level is None:
        max_level = np.max(pp1)
    levels = np.linspace(min_level, max_level, n_levels)
    if energy_on_y:
        cs = axis.contourf(phi, ee, pp1, cmap=cmap, levels=levels,
                           extend="both", zorder=0)
    else:
        cs = axis.contourf(ee, phi, np.transpose(pp1), cmap=cmap, levels=levels,
                           extend="both", zorder=0)
    cs.cmap.set_under('k')
    cs.set_clim(np.min(levels), np.max(levels))
    if colorbar:
        cb = plt.colorbar(cs, ax=axis, cax= axis_cb)

    if energy_on_y:
        axis.set_xlabel('Phase')
        if kind == 'E':
            axis.set_yscale('log')
            axis.set_ylabel('Energy [keV]')
        elif kind == 'T':
            axis.set_ylabel('Time [s]')
        elif kind == 'NE':
            axis.set_yscale('log')
            axis.set_ylabel('$E/E_\\mathrm{Cyc}$')
    else:
        axis.set_ylabel('Phase')
        if kind == 'E':
            axis.set_xscale('log')
            axis.set_xlabel('Energy [keV]')
        elif kind == 'T':
            axis.set_xlabel('Time [s]')
        elif kind == 'NE':
            axis.set_xscale('log')
            axis.set_xlabel('$E/E_\\mathrm{Cyc}$')        

    if source_name is not None:
        axis.set_title(source_name)
    if outfile is not None:
        axis.set_savefig(outfile)

    if sliders:
        # Nice to have : slider
        cmin = plt.axes([0.05, 0.95, 0.3, 0.02])
        cmax = plt.axes([0.65, 0.95, 0.3, 0.02])

        smin = Slider(cmin, 'Min', min_level, max_level, valinit=np.min(levels), orientation='horizontal')
        smax = Slider(cmax, 'Max', min_level, max_level, valinit=np.max(levels), orientation='horizontal')
        # areplot = plt.axes([0.4, 0.88, 0.1, 0.05])
        # bnext = Button(areplot, 'Reset', color='0.55', hovercolor='0.9')
        n_levels = 10

        # def reset(x):
        #     smin.reset()
        #     smax.reset()
        # cid = bnext.on_clicked(reset)

        def update(x):
            if smin.val < smax.val:
                cs.set_clim(smin.val, smax.val)

        smin.on_changed(update)
        smax.on_changed(update)

    return axis




def plot_matrix_as_lines(t, pp, dpp, kind='T', normalize=False, offset=0):
    '''

    :param t: time or energy array
    :param pp: time-phase or energy-phase matrix
    :param dpp: uncertainty on time-phase or energy-phase matrix
    :param kind: 'E' or 'T'
    :param normalize: normalize the pulses to mean and standard deviation
    :param offset: Offset between on profile and the following one
    :return:
    '''

    pt = pp.copy()
    dpt = dpp.copy()
    if normalize:
        for i in range(pp.shape[0]):
            x = pp[i, :]
            dx = dpp[i, :]
            m = np.mean(x)
            s = np.std(x)
            pt[i, :] = (x - m) / s
            dpt[i, :] = dx / s

    import matplotlib.pyplot as plt
    plt.figure()
    phi = np.linspace(0, 2, 2*pt.shape[1])

    plot_pt = np.tile(pt, 2)
    plot_dpt = np.tile(dpt, 2)

    total_offset = 0
    from matplotlib.colors import hsv_to_rgb
    from cycler import cycler
    colors = [hsv_to_rgb([(i * 0.618033988749895) % 1.0, 1, 1])
              for i in range(pt.shape[0])]
    plt.rc('axes', prop_cycle=(cycler('color', colors)))
    for i in range(pt.shape[0]):

        y = plot_pt[i, :]
        dy = plot_dpt[i, :]
        if np.sum(dy) > 0:
            # if np.sum(y) / np.sqrt(np.sum(dy ** 2)) > 10:
            label = "%.0f s" % ( t[i] - t[0])
            if kind == 'E':
                label = "%.1f keV" % t[i]
            ebar = plt.errorbar(phi, y+total_offset, xerr=0.5 / pt.shape[1], yerr=dy, linestyle='-',
                                marker='.', label=label)
            plt.text(phi[int(plot_pt.shape[1]*0.75)], y[int(plot_pt.shape[1]*0.75)]+total_offset, label,
                     color=ebar[0].get_color())
            #print(int(pt.shape[1]/2), phi[int(pt.shape[1]/2)], y[int(pt.shape[1]/2)]+total_offset,)
            total_offset += offset
    plt.ylabel('Rate per bin')
    plt.xlabel('Phase')
    #plt.legend()

def get_fourier_coeff(pulse, n=2):
    """returns the first n Fourier coefficients in polar form

    Args:
        pulse (array): the pulse profile
        n (int, optional): number of harmonics. Defaults to 2.

    Raises:
        IndexError: if n is larger than len(pulse/2)

    Returns:
       a, phi: numpy arrays: amplitudes and phases of the first n Fourier coefficients
    """

    # phi = np.linspace(0, 2 * np.pi, len(pulse))
    # i_c = np.sum(np.cos(phi) * pulse) / np.pi
    # i_s = np.sum(np.sin(phi) * pulse) / np.pi
    # i_c2 = np.sum(np.cos(2 * phi) * pulse) / np.pi
    # i_s2 = np.sum(np.sin(2 * phi) * pulse) / np.pi

    # phi0 = np.arctan2(i_s, i_c) / 2 / np.pi
    # phi0_2 = np.arctan2(i_s2, i_c2) / 2 / np.pi
    # a = np.sqrt(i_c * i_c + i_s * i_s) / len(pulse) / np.mean(pulse)
    # a2 = np.sqrt(i_c2 * i_c2 + i_s2 * i_s2) / len(pulse) / np.mean(pulse)

    ff = np.fft.rfft(pulse)
    if n>len(pulse)/2:
        raise IndexError('get_fourier_coeff: you asked for too many coefficients %d' %n )

    a = np.abs(ff[1:n+1])/ff[0].real
    phi = np.angle(ff[1:n+1])/2/np.pi
    return a, phi

def get_fourier_coeff_error( counts, counts_err, n_simul=1000, use_poisson=False, n=2, debug=False, margin=0.1):
    """ge uncertainty on Fourir coefficients

    Args:
        counts (numpy array): the counts
        counts_err (numpy array): the count encertainties
        n_simul (int, optional): how many bootstra simulation. Defaults to 1000.
        use_poisson (bool, optional): Use Poisson statistics. Defaults to False.
        n (int, optional): how many harmnonics. Defaults to 2.
        debug (bool, optional): If making debug plots. Defaults to False.
        margin (float, optional): option for the phase alignement, see phase_align. Defaults to 0.1.

    Returns:
        two numpy arrays: uncertainties on amplitudes and phases
    """
    sim_a = []
    sim_phi = []
    
    for i in range(n_simul):
        if use_poisson:
            fp = random.poisson(counts)
        else:
            fp = random.normal(counts, counts_err)
        a , phi = get_fourier_coeff(fp, n=n)
        sim_phi.append(phi)
        sim_a.append(a)
    err_a = np.zeros(n)
    err_phi = np.zeros(n)
    for i in range(n):
        y = np.array([x[i] for x in sim_a ])
        err_a[i] = np.std(y)
        y = np.array([x[i] for x in sim_phi ])
        y = align_phases(y, debug=debug, margin=margin)
        err_phi[i] = np.std(y)
        
    return err_a, err_phi

def align_phases(y, nbins=20, debug=False, distance_factor=1.5, margin=0.1, label=None):
    """align_phases: tries to align phases by building an histogram of phases.
    If only one peak is found, it is considered as a phae shiter only if it is 
    - in 0-margin(0.1) phases higher than 0.1+margin are shifted by -1
    - in (1-margin)(0.9)-1. phases lower than 0.9-margin are shifted by +1

    If more than one peak in the interval 0-margin(0.1) or (1-margin)(0.9)-1.0 are found, the higher phases are
    shifted by -1 (these peaks are often artifact of the algorithm)

    Args:
        y (numpy array): the phases to be aligned (in 0.-1.0 interval)
        nbins (int, optional): number of bins of the histogram to be built. Defaults to 20.
        debug (bool, optional): if True makes debug plots. Defaults to False.
        distance_factor (float, optional): if peaks are closer than 1/distace_factor times the maximum span, they are 
                                            rejected. Defaults to 1.5.
        margin (float, optional): . Defaults to 0.1.
        label (str, optional): a label of the debug plot (e.g. the energy). Defaults to None.

    Returns:
        numpy array: the aligned phases
    """    
    hist,bins = np.histogram(y, bins=nbins)
    from scipy.signal import find_peaks
    peaks, properties = find_peaks(np.concatenate(([np.min(hist)],hist, [np.min(hist)])), 
                          distance=nbins/distance_factor, prominence=0)
    peaks-=1
    if(debug):
        fig, ax = plt.subplots()
        ax.bar(bins[:-1], hist, width=np.diff(bins), edgecolor="blue", align="edge")
        for ppp in peaks:
            ax.axvline(bins[ppp+1], color='red')
        if label is not None:
            ax.set_title(label)

    out_method = logger.debug
    if debug:
        out_method = logger.info
            
    out_method(label)
    out_method(hist)
    out_method(bins)
    out_method('Peaks :')
    out_method(peaks)
    out_method(properties['prominences'])
        
    if (len(peaks) == 2):
        ind_division = int((peaks[0]+peaks[1])/2)
        if (peaks[0] > margin*nbins and peaks[0] < (1.-margin)*nbins ) or \
        (peaks[1] > margin*nbins and peaks[1] < (1.-margin)*nbins ) or \
        np.fabs(bins[peaks[1]] - bins[peaks[0]]) < 1./distance_factor:
            out_method("%s %s %s %f", (peaks[0] > margin*nbins and peaks[0] < (1.-margin)*nbins ), \
                       (peaks[1] > margin*nbins and peaks[1] < (1.-margin)*nbins ), \
                        np.fabs(bins[peaks[1]] - bins[peaks[0]]) < 1./distance_factor,
                        np.fabs(bins[peaks[1]] - bins[peaks[0]]))
            out_method("%f %f", margin*nbins,(1-margin)*nbins)
            out_method("No phase shift for two peaks")
            
        else:
            phase_division = bins[ind_division]
            out_method("%f %f", margin*nbins,(1-margin)*nbins)
            out_method("two peaks, phase_Division %f" % phase_division)
            y[y>phase_division]-=1.
    elif len(peaks) == 1:
        if peaks[0] < margin*nbins:
            phase_division = bins[int((0.9-margin)*nbins)]
            out_method("Phase_division minus %f"  % phase_division)
            out_method(np.sum(y>phase_division))
            y[y>phase_division]-=1
        if peaks[0]>(1-margin)*nbins:
            phase_division = bins[int((0.1+margin)*nbins)]
            out_method("Phase_division plus %f " % phase_division)
            out_method(np.sum(y>phase_division))
            y[y<phase_division]+=1
            
    return y

def rate_filter(time, rate, drate, level_down=0, level_up = 1e10, quantile=0.8, make_plot=True, 
                far=1e-4, rate_label='rate', histo_bins=300):
    '''
rate_filter(self, typical_level=0.5, quantile=0.7,  make_plot=True, far=1e-3,
                    tmin=0,tmax=1e12):
This function prepares cleaned events by apllying a standard filter eliminating bins with FAR < far
This is useful if one want to eliminate a peculiar part of an observation.
The filter is controlled in the following way:
- a Gaussian is fitted on LC data within the innner quantile (default=0.8) of the light curve
- a limit is set on FAR, but it can be overrided by using the level_up and level_down parameters, which are the lowest/highest possible limit.
It returns the limits and a handle to the figure (or None)
        '''
        
    print(rate_filter.__doc__)

    f = None
    if make_plot:
        f, axes = plt.subplots(1, 2)
        axes[0].errorbar(time, rate, yerr=drate, linestyle='none')
        axes[0].set_ylabel(rate_label)
        #axes[0].set_title(self.target + ' ' + self.obs_id)
        axes[0].set_xlabel('Time [s]')
        n_hist, edges, patches = axes[1].hist(rate, bins=histo_bins, density=True, facecolor='green',
                                              alpha=0.75)
        axes[1].set_xlabel(rate_label)

    # x=(edges[0:-2]+edges[1:])/2
    from scipy.stats import norm
    ind = (rate <= np.quantile(rate, quantile)) & (rate >= np.quantile(rate, 1.-quantile))
    (mu, sigma) = norm.fit(rate[ind])

    y = norm.pdf(edges, mu, sigma)

    fap = np.min([1. / len(rate), far])
    tmp = norm.isf(fap, loc=mu, scale=sigma)
    limit_up = np.min([level_up, tmp ])
    limit_down = np.max([level_down, 2*mu-tmp])

    if make_plot:
        _ = axes[1].plot(edges, y, 'r--', linewidth=2)
        _ = axes[1].axvline(limit_up, 0, 1, color='cyan')
        _ = axes[0].axhline(limit_up, 0, 1, color='cyan')
        _ = axes[1].axvline(limit_down, 0, 1, color='blue')
        _ = axes[0].axhline(limit_down, 0, 1, color='blue')
        
        
    return limit_down, limit_up, f

def write_orbit_file_from_gbm_page(url, file_name='orbit.dat',
                                   orbital_parameters = ['axsin', 'Eccentricity', 'periastron',
                                                         'T<sub>', 'Orbital Period', 'Period Deriv.']):
    '''
    It writes a file to be used in timingsuite for the orbit starting from the GBM page
    This is tested just for Cen X-3 at the moment and it is very fragile

    :param url: The url of the GBM page of the source
        (e.g. 'https://gammaray.nsstc.nasa.gov/gbm/science/pulsars/lightcurves/cenx3.html')
    :param file_name: the name of output file default 'orbit.dat'
    :param orbital_parameters the orbital parameters to be extracted from the table
        default: ['axsin', 'Eccentricity', 'periastron',
                 'T<sub>', 'Orbital Period', 'Period Deriv.']
    :return: file_name or None
    '''
    import requests
    from bs4 import BeautifulSoup
    import re
    from astropy.time import Time

    #Parses the table with a particular argument (fragile)
    html = requests.get(url).content
    soup = BeautifulSoup(html)
    orbit_table = soup.find('table', attrs={'border': 2})
    trs = orbit_table.find_all('tr')

    #removes the first row as it contains the table title
    trs[0].extract()

    #Find numbers (https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string)
    numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
    rx = re.compile(numeric_const_pattern, re.VERBOSE)

    #for each parmeter it extracts the value as string
    orbit = {}
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) < 2:
            continue
        for k in orbital_parameters:
            if k.lower() in str(tds[0]).lower():
                orbit.update({k: rx.findall(str(tds[1]))[0]})

    if orbital_parameters[0] not in orbit:
        logger.warning('Not able to retrieve the orbital parameters as %s could not be read' % orbital_parameters[0])
        return None
    # it writes the orbit file
    logger.info('Writing the following orbit parameters')
    with open(file_name, 'w') as ff:
        for kk in orbital_parameters:
            if 'T' in kk:
                t_90 = Time(orbit[kk], format='jd')
                # The orbit file contains the longitude of periastron or the lower conjunction
                if float(orbit['Eccentricity']) >= 0.:
                    print('Special eccentricity')
                    ff.write('%f\n' % (t_90.mjd + (float(orbit['periastron']) - 90.)/360. *\
                                       float(orbit['Orbital Period'])))
                else:
                    print('Non Special eccentricity')
                    ff.write('%f\n' % (t_90.mjd - 0.25 * float(orbit['Orbital Period'])))
            else:
                ff.write(orbit[kk] + '\n')
            logger.info('%s %s' % (kk , orbit[kk]))
    return file_name

def get_cross_correlation(pp, plot=False, n_to_fit = 3):
    """makes the cross correlation and lags of a matrix by fitting a Gaussian plus constant to the peak of the 
    correlation vector

    Args:
        pp (numpy array): the nergy or time-phase matrix
        plot (bool, optional): if making debug plots. Defaults to False.
        n_to_fit (int, optional): number of bins to use for the fit on each side of the peak. Defaults to 3.

    Returns:
        numpy arrays: lag, correlation
    """
    
    from lmfit.models import PolynomialModel, GaussianModel
    poly_mod = PolynomialModel(prefix='poly_', degree=0)
    gauss = GaussianModel(prefix='g'  + '_')

    n_pulse=pp.shape[1]
    if n_to_fit > n_pulse/3:
        logger.warning('The pulse has size %s and you try to use % points' %(n_pulse, 2*n_to_fit+1))
    
    correlation = []
    lag = []
    for i in range(pp.shape[0]):

        x = (pp[i, :] - np.mean(pp[i, :])) / np.std(pp[i, :])
        y = np.sum(pp[0:i, :], 0) + np.sum(pp[i + 1:, :], 0)
        y = (y - np.mean(y)) / np.std(y)
        corr = np.correlate(np.tile(x, 2), y) / len(x)

        i_max = np.argmax(corr)
        
        if i_max - n_to_fit >= 0 and i_max + n_to_fit <= len(x) :
            to_fit =  corr[i_max-n_to_fit:i_max+n_to_fit+1]
        elif i_max - n_to_fit < 0:
            logger.debug('First')
            to_fit = np.concatenate([corr[i_max-n_to_fit-1:-1], corr[0:i_max+n_to_fit+1]])
        else:
            logger.debug('Last !')
            to_fit = np.concatenate([corr[i_max-n_to_fit:], corr[1:i_max+n_to_fit-len(x)+1]])
        logger.debug("Check vector %f %f " %( corr[0], corr[-1]) )
        
        x_to_fit = np.arange(i_max-n_to_fit,i_max+n_to_fit+1, dtype=float)
        
        #for aa,bb in zip(x_to_fit, to_fit):
        #    print(aa,bb)
        
        pars = poly_mod.guess(to_fit, x=x_to_fit, degree=0)
        mod = poly_mod
    
        pars.update(gauss.make_params())
        pars['g' +  '_center'].set(value=float(i_max), min=i_max-n_to_fit, max=i_max+n_to_fit)
        pars['g' +  '_sigma'].set(value=1., min=0, max=n_to_fit)
        pars['g' +  '_amplitude'].set(value=np.max(to_fit), min=0.0, max=2*np.max(to_fit))
        mod = mod + gauss
        
        out = mod.fit(to_fit, pars, x=x_to_fit)

        correlation.append(np.max(out.eval(x=np.linspace(x_to_fit[0], x_to_fit[-1], 100))))
        lag.append(out.best_values['g' +  '_center'])

        if plot:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.subplot(1, 2, 1)
            plt.plot(x_to_fit, to_fit, label='X-corr values', color='blue', marker='o', linestyle='')
            plt.plot(np.linspace(x_to_fit[0], x_to_fit[-1],100),
                                 out.eval(x=np.linspace(x_to_fit[0], x_to_fit[-1], 100))
                                 , label='X-corr fit', color='orange')
            
            plt.title('correlation')
            plt.axvline(lag[-1])
            plt.axhline(correlation[-1])
            plt.subplot(1, 2, 2)
            plt.plot(x, label='Pulse', color='blue')
            plt.plot(y, linestyle='--', label='Average', color='orange')
            plt.title('Pulse and average')
            plt.legend()
            

    lag = np.array(lag) / n_pulse

    return lag, np.array(correlation)

def get_cross_correlation_with_error(pp, dpp, ee_pulsed=[], dee_pulsed=[], n_simul=100,
                            use_poisson=False, Feline = None, Ecycl = None, n_to_fit=3, debug_plot=False, stem=None, title='',
                            margin=0.1, debug_indexes=[], distance_factor=1.5):
    """Makes the cross correlation of each pulse in the matrix with the average of the rest of the matrix

    Args:
        pp (numpy array): energ-phase matrix
        dpp (numpy array): energy-phase matrix error
        ee_pulsed (list, optional): energy scale (only for plotting). Defaults to [].
        dee_pulsed (list, optional): energy scale uncertainty (only for plotting). Defaults to [].
        n_simul (int, optional): number of simulations to compute the error. Defaults to 100.
        use_poisson (bool, optional): If using Poisson error. Defaults to False.
        n_to_fit (int, optional): number of bins to fit the peak on each side of the maximum cross correlation. Defaults to 3.
        debug_plot (bool, optional): if making debug plots for correlation. Defaults to False.
        stem (_type_, optional): If not nome, it saves the plot with this prefix adding _lag_correlation.png. Defaults to None.
        title (str, optional): Title of the plot. Defaults to ''.
        margin (float, optional): parameter to realign phases, see align_phases
        ditance_factor (float, optional): parameter to realign phases, see align_phases
        debug_indexes (list, ptional): indexes to perform debug output for phase_align. Defaults to [].

    Raises:
        ValueError: Value Error if the energy scale does not match the matrix when plotting

    Returns:
        numpy arrays: lags, lag_errors, correlations, correlation_errors
    """    

    lags, correlations = get_cross_correlation(pp, n_to_fit=n_to_fit, plot=debug_plot)

    fake_lags = np.empty([n_simul, pp.shape[0]], dtype=float)
    fake_corrs = np.empty([n_simul, pp.shape[0]], dtype=float)

    for i in range(n_simul):
        if use_poisson:
            fake_pp = random.poisson(pp)
        else:
            fake_pp = random.normal(pp, dpp)
        debug = False
        if i in debug_indexes:
            debug=True
        fake_lags[i, :], fake_corrs[i, :] = get_cross_correlation(fake_pp, n_to_fit=n_to_fit, plot= (debug_plot & debug))
    
    
    for i in range(fake_lags.shape[1]):
        debug = False
        if i in debug_indexes:
            debug=True
        fake_lags[:,i] = align_phases(fake_lags[:,i], debug=debug, label='%.1f kev' % (ee_pulsed[i]), margin=margin, 
                                      distance_factor=distance_factor )
        
    
    lag_errors = np.std(fake_lags, 0)
    lag_checks = np.mean(fake_lags, 0)
    correlation_errors = np.std(fake_corrs, 0)
    
    lags[lags>0.5] -= 1.0
    lag_checks[lag_checks>0.5] -= 1.0
    
    lags[lags<-0.5] += 1.0
    lag_checks[lag_checks<-0.5] += 1.0
    
    if debug_plot:
        for i in range(fake_lags.shape[1]):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 8))
            ax1.hist(fake_lags[:,i], bins=int(n_simul/5))
            ax1.set_xlabel('Lags')
            ax1.set_title('%.1f keV' % ee_pulsed[i])
            ax2.hist(fake_corrs[:,i], bins=int(n_simul/5))
            ax1.set_ylabel('Correlations')
        

    if stem is not None:
        if len(ee_pulsed) != len(lags):
            
            raise ValueError('You should provide energy vetcors with size %d to plot, but was %d' % \
                             (len(lags), len(ee_pulsed)))
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(4.5, 7), sharex=True, gridspec_kw={'height_ratios': [1, 1],
                                                                              'hspace': 0.0, 'right':0.99, 'left':0.2})

        cc = iter(plt.cm.viridis(np.linspace(0, 1, 5)))
        ax1.errorbar(ee_pulsed, correlations, xerr=dee_pulsed, yerr=correlation_errors, marker='.', linestyle='',color = next(cc))
        ax1.set_title(title)
        ax1.set_ylabel('Correlation')
        ax2.set_xscale('log')
        ax1.set_xscale('log')
        ax2.errorbar(ee_pulsed, lags, xerr=dee_pulsed, yerr=lag_errors, marker='.', linestyle='',color = next(cc))
        if debug_plot:
            ax2.scatter(ee_pulsed, lag_checks, marker='o', color='green')
        col2 = next(cc)
        if Ecycl is not None and len(Ecycl) > 0:
            ax1.axvspan(Ecycl[0] - Ecycl[1], Ecycl[0] + Ecycl[1], alpha=0.5, color=col2)
            ax2.axvspan(Ecycl[0] - Ecycl[1], Ecycl[0] + Ecycl[1], alpha=0.5, color=col2)

    if Feline is not None and len(Ecycl) > 0:
        col2 = next(cc)
        ax1.axvspan(Feline[0] - Feline[1], Feline[0] + Feline[1], alpha=0.5, color=col2)
        ax2.axvspan(Feline[0] - Feline[1], Feline[0] + Feline[1], alpha=0.5, color=col2)
    ax2.set_ylabel('Lag (phase units)')
    ax2.set_xlabel('Energy [keV]')
    fig.savefig(stem+'_lag_correlation.png' )

    return lags, lag_errors, correlations, correlation_errors

def get_target_coords_extern(input_name):
    from astroquery.simbad import Simbad
    from astropy import units as u
    from astropy.coordinates import SkyCoord

    name = input_name
    simbad = Simbad.query_object(name)
    c = SkyCoord(simbad['RA'], simbad['DEC'], unit=[u.hour, u.deg])
    c.fk5
    logger.info("Coordinates for %s are RA=%.4f, Dec=%.4f" % (name, c.ra.deg[0], c.dec.deg[0]))

    return c.ra.deg[0], c.dec.deg[0]

def lmfit_chain_to_dict(dict_name, my_chain, high_part = False):
    """reformats the mcmc results to be used as
    pysas.dump_latex_table(dict_param, utils.mcmc_latex_dict))
    where dict_param is the output of this function

    Args:
        dict_name (str): name of the disctionary to be put in the table
        my_chain (object): first output of utils.explore_fit_mcmc
        high_part (bool, optional): this flag changes the name of gaussians from gX to ggX. Defaults to True.

    Returns:
        dict: a dictionary of parameters as expected by pysas.dump_latex_table
    """
    quantiles = my_chain.flatchain.quantile([0.32, 0.5, 0.68])
    
    out_dict = { dict_name : {} }
    
    for kk in quantiles.keys():
        
        if high_part:
            key_name = kk.replace('g','gg')
        else:
            key_name = kk
        out_dict[dict_name].update( {key_name: [ quantiles[kk][0.50], quantiles[kk][0.32], quantiles[kk][0.68]]})
    out_dict[dict_name].update({'cstat' : [my_chain.chisqr, my_chain.nfree, my_chain.nfree]})
    return out_dict

mcmc_latex_dict = {
    'poly_c0' : '$c_0$',
    'poly_c1' : '$c_1$',
    'poly_c2' : '$c_2$',
    'poly_c3' : '$c_3$',
    'poly_c4' : '$c_4$',
    'poly_c5' : '$c_5$',
    'poly_c6' : '$c_6$',
    'poly_c7' : '$c_7$',
    'g1_amplitude': '$A_\\mathrm{Fe}$',
    'g1_center': '$E_\\mathrm{Fe}$',
    'g1_sigma': '$\\sigma_\\mathrm{Fe}$',
    'gg1_amplitude': '$A_\\mathrm{Cyc}$',
    'gg1_center': '$E_\\mathrm{Cyc}$',
    'gg1_siggma': '$\\sigma_\\mathrm{Cyc}$',
    'gg2_amplitude': '$A_\\mathrm{Cyc2}$',
    'gg2_center': '$E_\\mathrm{Cyc2}$',
    'gg2_siggma': '$\\sigma_\\mathrm{Cyc2}$',
    'cstat' : '$\\chi^2_\\mathrm{red}$/d.o.f.',
}


def plot_harmonics_all(energy, a1 , phi1, a2, phi2, Feline, Ecycl, xscale = 'log', title = None,stem = ' '):
    """ final visual results of the analysis performed on the harmonics
    Args:
        energy: np.2d-array [energy,denergy]

    Returns:
    """
    fig, ax = plt.subplots(2, 2, sharex=True, figsize=(8, 6),gridspec_kw={'height_ratios': [1, 1],
                                                                              'hspace': 0.0})
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.3)
    if title is not None:
        plt.suptitle(str(title),size = 23)
    color = iter(plt.cm.viridis(np.linspace(0, 1, 7)))
    #col = next(color)
    ax[0][0].errorbar(energy[0], a1[0], xerr=energy[1], yerr=a1[1], linestyle='', marker='.', color=next(color))
    ax[0][0].set_ylabel('$A_1$')
    ax[1][0].errorbar(energy[0], phi1[0], xerr=energy[1], yerr=phi1[1], linestyle='', marker='.',color=next(color))
    ax[1][0].set_ylabel('$\phi_1$')

    ax[0][1].errorbar(energy[0], a2[0], xerr=energy[1], yerr=a2[1], linestyle='', marker='.', color=next(color))
    ax[0][1].set_ylabel('$A_2$')
    ax[1][1].errorbar(energy[0], phi2[0], xerr=energy[1], yerr=phi2[1], linestyle='', marker='.', color=next(color))
    ax[1][1].set_ylabel('$\phi_2$')


    ax[1][0].set_xlabel('Energy [keV]')
    ax[1][1].set_xlabel('Energy [keV]')

    col2 = next(color)
    for [aa, bb] in ax[:][:]:
        aa.set_xscale(xscale)

        aa.axvspan(Ecycl[0] - Ecycl[1], Ecycl[0] + Ecycl[1], alpha=0.5, color=col2)
        bb.axvspan(Ecycl[0] - Ecycl[1], Ecycl[0] + Ecycl[1], alpha=0.5, color=col2)

    if Feline is not None:
        col2 = next(color)
        for [aa, bb] in ax[:][:]:
            aa.axvspan(Feline[0] - Feline[1], Feline[0] + Feline[1], alpha=0.5, color=col2)
            bb.axvspan(Feline[0] - Feline[1], Feline[0] + Feline[1], alpha=0.5, color=col2)


    plt.show()
    if stem is not None:
        plt.savefig(stem+'plot_all.pdf')
    return fig


def plot_matrix_as_image2(ax, ee, pp, kind='E', normalize=True,outfile=None, cmap=matplotlib.cm.gist_earth,
                         sliders=False, n_levels=30, min_level=None, max_level=None, source_name=None,
                         energy_on_y=True):
    '''
    :param ee: y-scale (time or energy)
    :param pp: Energy-Phase or Time-Phase matrix (# of rows must equal len(ee))
    :param kind: * 'E' energy phase
                 * 'T' Time-phase
                 * 'NE' energy phase with energy normalized to the cyclotron energy
    :param normalize: normalize each pulse at its average and divide by the standard deviation
    :param outfile: the file to save the figure as image (optional)
    ;param cmap the colormap of matplotlib, defaults to matplotlib.cm.gist_earth
    ;param sliders if True uses sliders
    ;param n_levels the number of linearly spaced contour levels
    ;param min_level the minimum level for contours
    ;param max_level the maximum level for contours
    ;param source_name if not None, it is used as plot title
    'param energy_on_y (def True) if plotting energy on vertical axis
    :return:
    '''

    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider
    # from matplotlib.widgets import Button

    if pp.shape[0] != len(ee):
        raise ImportError('len(ee) [%d] != # rows pp [%d]' % (len(ee), pp.shape[0]))
    pp1 = pp.copy()
    if normalize:
        for i in range(pp.shape[0]):
            x = pp[i, :]
            m = np.mean(x)
            s = np.std(x)
            pp1[i, :] = (x - m) / s

    phi = np.linspace(0, 1, pp.shape[1])
    fig = plt.figure(figsize=(5.5, 4.2))
    ax = plt.subplots(111)
    # if sliders:
    #     plt.subplots_adjust(top=0.82)
    if min_level is None:
        min_level = np.min(pp1)
    if max_level is None:
        max_level = np.max(pp1)
    levels = np.linspace(min_level, max_level, n_levels)
    if energy_on_y:
        ax.contourf(phi, ee, pp1, cmap=cmap, levels=levels,
                           extend="both", zorder=0)
    else:
        ax.contourf(ee, phi, np.transpose(pp1), cmap=cmap, levels=levels,
                           extend="both", zorder=0)
    ax.cmap.set_under('k')
    ax.set_clim(np.min(levels), np.max(levels))
    cb = plt.colorbar(ax)

    if energy_on_y:
        plt.xlabel('Phase')
        if kind == 'E':
            ax.set_yscale('log')
            ax.set_ylabel('Energy [keV]')
        elif kind == 'T':
            ax.set_ylabel('Time [s]')
        elif kind == 'NE':
            ax.set_yscale('log')
            ax.set_ylabel('$E/E_\\mathrm{Cyc}$')
    else:
        ax.set_ylabel('Phase')
        if kind == 'E':
            ax.set_xscale('log')
            ax.set_xlabel('Energy [keV]')
        elif kind == 'T':
            ax.set_xlabel('Time [s]')
        elif kind == 'NE':
            ax.set_xscale('log')
            ax.set_xlabel('$E/E_\\mathrm{Cyc}$')

    if source_name is not None:
        ax.set_title(source_name)
    if outfile is not None:
        ax.set_savefig(outfile)

    if sliders:
        # Nice to have : slider
        cmin = ax.set_axes([0.05, 0.95, 0.3, 0.02])
        cmax = ax.set_axes([0.65, 0.95, 0.3, 0.02])

        smin = Slider(cmin, 'Min', min_level, max_level, valinit=np.min(levels), orientation='horizontal')
        smax = Slider(cmax, 'Max', min_level, max_level, valinit=np.max(levels), orientation='horizontal')
        # areplot = plt.axes([0.4, 0.88, 0.1, 0.05])
        # bnext = Button(areplot, 'Reset', color='0.55', hovercolor='0.9')
        n_levels = 10

        # def reset(x):
        #     smin.reset()
        #     smax.reset()
        # cid = bnext.on_clicked(reset)

        def update(x):
            if smin.val < smax.val:
                ax.set_clim(smin.val, smax.val)

        smin.on_changed(update)
        smax.on_changed(update)

        #return cs
