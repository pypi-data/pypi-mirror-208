from __future__ import print_function    # (at top of module)
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os
import subprocess
from astropy.io import fits as pf
from astropy.coordinates import SkyCoord

from time import gmtime, strftime
from astropy.table import Table

from astropy.wcs import WCS
from matplotlib.colors import LogNorm

from photutils import CircularAperture
from photutils import aperture_photometry
import xspec
from IPython.display import Image
from IPython.display import display
import shutil
from optimalgrouping.optimalgrouping import execute_binning

from glob import glob


def write_region(fname, ra, dec, src_flag):

    # write a ds9 region file in sky coordinates

    ff = open(fname, 'w')
    ff.write(
        "global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal roman\" select=1 highlite=1 dash=0 "+
        "fixed=0 edit=1 move=1 delete=1 include=1 source=1\nfk5\n")
    if src_flag:
        ff.write("circle(%.4f,%.4f,80\")" % (ra, dec))
    else:
        # This is just a guess
        ra_deg = float(ra) + 0.05
        dec_deg = float(dec) + 0.05
        ff.write("circle(%.4f,%.4f,80\")" % (ra_deg, dec_deg))

    ff.close()


def wrap_run(scw, script_base_name, script_string=None, extension='.sh'):

    #it runs a script as a subprocess
    #scw : folder to access
    #script_base_name : name of the script without extension
    #script_string : if not None, use it as script content
    #extension : defallt is .sh

    script_name = scw + '/' + script_base_name + extension

    if script_string is not None:
        file_h = open(script_name, 'w')
        file_h.write(script_string)
        file_h.close()
        os.chmod(script_name, 0o755)

    time_stamp = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

    logfile_name = scw + '/' + script_base_name + "_%s.log" % (time_stamp)
    logfile = open(logfile_name, 'w')

    cmd = 'cd %s;./%s.sh' % (scw, script_base_name)
    #This is a bookmark, not tested
    try:
        if 'lesta' in os.environ['HOSTNAME']:
            cmd ='cd %s;sbatch -p s1 -J %s -D $PWD -e "/scratch/ferrigno/logs/\%u_\%x_\%j.out" -o "/scratch/ferrigno/logs/\%u_\%x_\%j.out" ./%s.sh'%(scw,script_base_name,script_base_name)
    except:
        pass
    print("Running command '%s'" % (cmd))
    out = subprocess.call(cmd, stdout=logfile, stderr=logfile, shell=True)
    print("Command '%s' finished with exit value %d"%(cmd,out))
    logfile.close()

    return out

def epic_xspec_mcmc_fit(xspec, model_name,
                    pn_spec = "PNsource_spectrum_rbn.pi",
                    mos1_spec = "MOS1source_spectrum_rbn.pi",
                    mos2_spec = "MOS2source_spectrum_rbn.pi",
                    ignore_string=['**-0.5,10.0-**','**-0.5,10.0-**','**-0.5,10.0-**'],
                    outputfiles_basename="gw-mcmc-",
                    load_chain = False, perform_fit=True,
                    set_priors=False,
                    jeffreys_priors=['norm'],
                    burn=6000, runLength=26000,  walkers=20,  save_xcm=True, compute_errors=True, run_chain=True):


    n_spectra, models = epic_load_spectra_set_model(xspec, model_name,
                                            pn_spec,
                                            mos1_spec,
                                            mos2_spec,
                                            ignore_string
                                            )

    chain_name = outputfiles_basename+'chain.fits'

    if load_chain:

        #chain1 = xspec.AllChains(1)
        table_chain = Table.read(chain_name)

        table_chain_pd = table_chain.to_pandas()
        best_fit=table_chain_pd[ table_chain_pd['FIT_STATISTIC'] == table_chain_pd['FIT_STATISTIC'].min() ].head(1)

        #print('In loaded chain, the best fit has statistic %f' %(table_chain_pd['FIT_STATISTIC'].min()))

        table_chain_pd.drop('FIT_STATISTIC', axis=1, inplace=True)

        median_values = table_chain_pd.quantile(0.5)

        key_names = median_values.keys()
        for key_name in key_names:
            par_num = int(key_name.split('__')[-1])
            ind_model = int(np.floor(float(par_num - 1) / float(models[0].nParameters)))

            #print(ind_model, par_num, key_name, par_num - ind_model * models[0].nParameters)
            mm = models[ind_model]
            mm(par_num - ind_model * mm.nParameters).values = median_values[key_name]

            # print(best_fit[key_name])
            # mm(par_num - ind_model * mm.nParameters).values = float(best_fit[key_name])
            print(key_name, float(best_fit[key_name]))

        xspec.AllChains += chain_name

        xspec.AllModels.show()

    else:

        if set_priors:
            for mm in models:
                comp_names = mm.componentNames
                for cc in comp_names:
                    comp = getattr(mm, cc)
                    for par_name in comp.parameterNames:
                        par = getattr(comp, par_name)

                        if par.frozen or par.link != '':
                            print(par_name, ' linked or frozen ')
                            continue

                        if par_name not in jeffreys_priors:
                            par.prior = 'cons'
                            print('uniform prior for %s %s' % (cc, par_name))
                        elif par_name in jeffreys_priors:
                            par.prior = 'jeffreys'
                            print('jeffreys prior for %s %s' % (cc, par_name))
                        else:
                            print('Not setting prior for %s'%par_name)
        if perform_fit:
            xspec.Fit.perform()

        print(chain_name)


        if run_chain:
            try:
                os.remove(chain_name)
                print("Removed chain " + chain_name)
            except:
                pass
            chain1 = xspec.Chain(chain_name, algorithm='gw', burn=burn, runLength=runLength,  walkers=walkers)


        #print(chain_name)
        #chain1.run(False)

    # xspec.Fit.error('2.7 1,2,5')

    # Create and open a log file for XSPEC output
    # This returns a Python file object
    #logFile = xspec.Xset.openLog(log_name)
    # Get the Python file object for the currently opened log
    # logFile = xspec.Xset.log
    #xspec.AllModels.calcFlux("1.0 10.0")

    # Close XSPEC's currently opened log file.
    #xspec.Xset.closeLog()
    print('Cstat=', xspec.Fit.statistic, 'Chi2=', xspec.Fit.testStatistic, 'dof=', xspec.Fit.dof)

    fit_results= plot_save_xcm(xspec, outputfiles_basename, perform_fit, save_xcm, compute_errors)

    return chain_name, fit_results

def goodness_from_chain(xspec, outputfiles_basename, n_sample=100,
                    pn_spec = "PNsource_spectrum_rbn.pi",
                    mos1_spec = "MOS1source_spectrum_rbn.pi",
                    mos2_spec = "MOS2source_spectrum_rbn.pi",
                    ignore_string=['**-0.5,10.0-**', '**-0.55,10.0-**', '**-0.55,10.0-**']):

    chain_name = outputfiles_basename + 'chain.fits'
    table_chain = Table.read(chain_name)
    keys = table_chain.keys()
    keys.remove('FIT_STATISTIC')

    epic_load_spectra_set_model(xspec, outputfiles_basename + 'model.xcm',
                                pn_spec=pn_spec,
                                mos1_spec=mos1_spec,
                                mos2_spec=mos2_spec,
                                ignore_string=ignore_string)

    n_pars = xspec.AllModels(1).nParameters

    set_par_list = []

    if 'bxa' in outputfiles_basename.lower():
        best_fit_ind = np.argmax(table_chain['FIT_STATISTIC'])
    else:
        best_fit_ind = np.argmin(table_chain['FIT_STATISTIC'])

    row=table_chain[best_fit_ind]

    for kk in keys:
        if 'log' in kk:
            no_log_kk = kk.replace('log(', '').replace(')', '')
            par_index = int(no_log_kk.split('__')[1])
            par_value = 10 ** row[kk]
        else:
            par_index = int(kk.split('__')[1])
            par_value = row[kk]

        group = int(np.floor((par_index - 1) / n_pars + 1))
        par_index_in_group = par_index - (group - 1) * n_pars

        # print('new ', par_index, row[kk])
        set_par_list += [xspec.AllModels(group), {par_index_in_group: par_value}]

        # print(set_par_list)
    xspec.AllModels.setPars(*set_par_list)

    sampled_fit_statistics = [xspec.Fit.statistic]

    #print('Best fit statistic in chain is %f at index %d' % (table_chain['FIT_STATISTIC'][best_fit_ind], best_fit_ind))
    print('Best fit statistic in chain is %f' % (xspec.Fit.statistic))

    for row in table_chain[-n_sample:]:

        epic_load_spectra_set_model(xspec, outputfiles_basename + 'model.xcm',
                                          pn_spec=pn_spec,
                                          mos1_spec=mos1_spec,
                                          mos2_spec=mos2_spec,
                                          ignore_string=ignore_string, verbose=False)

        set_par_list = []
        for kk in keys:
            if 'log' in kk:
                no_log_kk = kk.replace('log(', '').replace(')', '')
                par_index = int(no_log_kk.split('__')[1])
                par_value=10**row[kk]
            else:
                par_index = int(kk.split('__')[1])
                par_value=row[kk]

            group = int(np.floor((par_index - 1) / n_pars + 1))
            par_index_in_group = par_index - (group - 1) * n_pars

            # print('new ', par_index, row[kk])
            set_par_list += [xspec.AllModels(group), {par_index_in_group: par_value}]

        # print(set_par_list)
        xspec.AllModels.setPars(*set_par_list)
        xspec.AllData.fakeit(noWrite=True)
        xspec.AllData.ignore('bad')

        n_spectra = xspec.AllData.nGroups
        spectra = [xspec.AllData(j) for j in range(1, n_spectra + 1)]

        for s, ig in zip(spectra, ignore_string):
            s.ignore(ig)



        sampled_fit_statistics.append(xspec.Fit.statistic)

    best_fit_statistic = sampled_fit_statistics[0]
    sorted_sampled_fit_statistics = sorted(sampled_fit_statistics[1:], reverse=True)

    arg_min = np.argmin(np.abs(np.array(sorted_sampled_fit_statistics) - best_fit_statistic))
    goodness = float(arg_min) / float(len(sorted_sampled_fit_statistics) - 1)

    print('%.1f per cent of realization have higher test statistic than the best fit (%.0f/%d)'%( goodness * 100, best_fit_statistic,xspec.Fit.dof))
    print("We used ", n_sample, ' simulated spectra from the chain ', chain_name )

    return sorted_sampled_fit_statistics,best_fit_statistic, goodness


def epic_load_spectra_set_model(xspec, model_name,
                    pn_spec = "PNsource_spectrum_rbn.pi",
                    mos1_spec = "MOS1source_spectrum_rbn.pi",
                    mos2_spec = "MOS2source_spectrum_rbn.pi",
                    ignore_string=['**-0.5,10.0-**', '**-0.55,10.0-**', '**-0.55,10.0-**']
                    , verbose=True):


    xspec.AllData.clear()
    xspec.AllModels.clear()
    xspec.AllChains.clear()

    #This is just for the case that no MOS1 spectrum is present
    spec_number=1

    load_str=''

    for ss in [pn_spec,mos1_spec,mos2_spec]:
        if ss is not 'none':
            load_str +='%d:%d %s '%(spec_number,spec_number,ss)
            spec_number+=1


    xspec.AllData(load_str)

    xspec.AllData.ignore('bad')

    n_spectra = xspec.AllData.nGroups
    spectra = [xspec.AllData(j) for j in range(1, n_spectra + 1)]

    if verbose:
        print("We load %d spectra" % n_spectra)
        print(ignore_string)

    if len(spectra) != len(ignore_string):
        raise RuntimeError('Lentgth of ignore string list is different fromt he number of spectra')

    for s, ig in zip(spectra, ignore_string):
        s.ignore(ig)

    xspec.Xset.restore(model_name)
    #the save command does not store abundances correctly, so we move this here
    xspec.Fit.statMethod = "cstat"
    xspec.Xset.abund = 'wilm'

    models = [xspec.AllModels(j) for j in range(1, n_spectra + 1)]

    mm = models[0]

    if hasattr(mm,'constant'):
        mm.constant.factor = "1,-1"
        for mm in models[1:]:
            mm.constant.factor.untie()
            mm.constant.factor.frozen = False
            mm.constant.factor = ",.01,.1,.1,1.9,1.9"

    return n_spectra, models

def epic_bxa_run(xspec, xspec_model_file,
                    pn_spec = "PNsource_spectrum_rbn.pi",
                    mos1_spec = "MOS1source_spectrum_rbn.pi",
                    mos2_spec = "MOS2source_spectrum_rbn.pi",
                    ignore_string=['**-0.5,10.0-**'],
                    outputfiles_basename = 'bxa-', run_sampling=False, jeffreys_priors=['norm'],
                    sampling_efficiency = 0.3,
                    n_live_points = 400, evidence_tolerance = 0.5, perform_fit=False, save_xcm=True,
                    compute_errors=True):
    import bxa.xspec as bxa
    import pymultinest

    n_spectra,models = epic_load_spectra_set_model(xspec, xspec_model_file,
                                                   pn_spec,
                                                   mos1_spec,
                                                   mos2_spec, ignore_string)

    transformations = []

    for mm in models:

        comp_names = mm.componentNames
        for cc in comp_names:
            comp = getattr(mm, cc)
            for par_name in comp.parameterNames:
                par = getattr(comp, par_name)

                if par.frozen or par.link != '':
                    print(par_name, ' linked or frozen ')
                    continue

                if par_name not in jeffreys_priors:  # 'norm'
                    transformations.append(bxa.create_uniform_prior_for(mm, par))
                    print('uniform prior for %s %s' % (cc, par_name))
                elif par_name in jeffreys_priors:
                    transformations.append(bxa.create_jeffreys_prior_for(mm, par))
                    print('jeffreys prior for %s %s' % (cc, par_name))
                else:
                    raise RuntimeError('cannot define prior for parameter %'%par_name)

    if run_sampling:
        analyzer =bxa.nested_run(transformations,
                       outputfiles_basename=outputfiles_basename,
                       sampling_efficiency=sampling_efficiency,
                       n_live_points=n_live_points, evidence_tolerance=evidence_tolerance,
                       verbose=True,  # show a bit of progress
                       resume=True  # MultiNest supports resuming a crashed/aborted run
                       )
    else:
        analyzer = pymultinest.Analyzer(n_params=len(transformations),
                                    outputfiles_basename=outputfiles_basename)
        xspec.AllChains.clear()
        xspec.AllChains += outputfiles_basename+'chain.fits'



    best_fit= analyzer.get_best_fit()

    print('Best log likelihood is %g'%best_fit['log_likelihood'])

    s = analyzer.get_stats()

    pars=[]

    for t, b, m  in zip(transformations, best_fit['parameters'], s['marginals']):
        if 'log(' in t['name']:
            # t['model'](t['index']).values=10**m['median']

            pars += [t['model'], {t['index']: 10 ** b}]
            print(' %20s: %.3f ' % (t['name'].replace('log(','').replace(')',''), 10 ** b))
            print(' %20s: %.3f  %.3f %.3f ' % (t['name'].replace('log(','').replace(')',''),
                                               10 ** m['median'], 10 ** m['q10%'], 10 ** m['q90%']))

        else:
            pars += [t['model'], {t['index']: b}]
            print(' %20s: %.3f' % (t['name'], b))
            print(' %20s: %.3f  %.3f %.3f ' % (t['name'], m['median'], m['q10%'], m['q90%']))

    xspec.AllModels.setPars(*pars)
    print('Cstat=', xspec.Fit.statistic, 'Chi2=', xspec.Fit.testStatistic, 'dof=', xspec.Fit.dof)

    fit_results=plot_save_xcm(xspec, outputfiles_basename,perform_fit, save_xcm=save_xcm, compute_errors=compute_errors)


    return transformations, fit_results

def plot_save_xcm(xspec, outputfiles_basename, perform_fit=False, save_xcm=True, compute_errors=True):

    if save_xcm:
        xcmfile = outputfiles_basename + 'model.xcm'
        if os.path.exists(xcmfile):
            os.remove(xcmfile)

        xspec.Xset.save(xcmfile, 'a')

    fn = outputfiles_basename+'euf_plot.png'
    xspec.Plot.device = fn + "/png"
    # xspec.Plot.addCommand("setplot en")
    xspec.Plot.xAxis = "keV"
    xspec.Plot("euf del")
    xspec.Plot.device = fn + "/png"

    shutil.move(fn + "_2", fn)

    _ = display(Image(filename=fn, format="png"))

    n_spectra = xspec.AllData.nGroups
    spectra = [xspec.AllData(j) for j in range(1, n_spectra + 1)]
    models = [xspec.AllModels(j) for j in range(1, n_spectra + 1)]

    #When loading the BXA saved chain, the errors are ot computed from the chain
    if(perform_fit):
        xspec.Fit.perform()

    if compute_errors:
        try:
            xspec.Fit.error('1.0 1-%d' % (n_spectra * models[0].nParameters))
        except:
            print("Uncertainties cannot be computed")



    print('Cstat=', xspec.Fit.statistic, 'Chi2=', xspec.Fit.testStatistic, 'dof=', xspec.Fit.dof)
    fit_by_bin = dict(
        rate=[spectra[0].rate[0], spectra[0].rate[0] - spectra[0].rate[1], spectra[0].rate[0] + spectra[0].rate[1]],
        cstat=[xspec.Fit.statistic, xspec.Fit.dof]
    )

    print("\nSpectral parameters:\n")
    for j, m1 in enumerate(models):
        for i in range(1, m1.nParameters + 1):

            if not m1(i).frozen and m1(i).link == '':
                # print( m1(i).name, m1(i).frozen, m1(i).link)
                format_str = get_format_string(m1(i).values[0], m1(i).error[0], m1(i).error[1])
                par_name = '%s__%02d' % (m1(i).name, j * m1.nParameters + i)
                fit_by_bin.update({par_name: [m1(i).values[0], m1(i).error[0], m1(i).error[1]]})
                output_str = "\t%s " + format_str + " %s (" + format_str + "-" + format_str + ")"
                print(output_str % (par_name, m1(i).values[0], m1(i).unit, m1(i).error[0], m1(i).error[1]))
            else:
                # print( m1(i).name, m1(i).frozen, m1(i).link,m1(i).values[0] )
                format_str = get_format_string(m1(i).values[0], m1(i).values[0], m1(i).values[0])
                output_str = "\t%s " + format_str + " %s "
                print(output_str % (m1(i).name, m1(i).values[0], m1(i).unit))

    return fit_by_bin


class pure_pair():
    #class to have pairs without duplications

    def __init__(self, a, b):
        self.pair = (a, b)

    def __eq__(self, other):
        return (self.pair[0] == other.pair[0] and self.pair[1] == other.pair[1]) or (
                    self.pair[0] == other.pair[1] and self.pair[1] == other.pair[0])

    def __hash__(self):
        tmp = sorted(self.pair)
        return hash((tmp[0], tmp[1]))

#This interferes with the purpose of the class
#     def __getitem__(self, i):
#         if i <0 or i>1:
#             raise RuntimeError('pure_pair items defined only for index zero or one')
#         return self.pair[1]
#     def __setitem__(self,i,x):
#         if i <0 or i>1:
#             raise RuntimeError('pure_pair items defined only for index zero or one')
#         self.pair[i]=x

def get_unique_pairs(list_par):
    #lit objects must have a cardinality (strings or numbers)
    # it returns unique pairs, disregadig order

    import itertools

    my_pairs = []

    for perm in itertools.permutations(list_par):
        for a, b in (zip(perm[::2], perm[1::2])):
            my_pairs.append(pure_pair(a, b))

    return set(my_pairs)



default_latex_label_dict = {
    'nH__02': '$n_\mathrm{H}$',
    'nH__03': '$n_\mathrm{H, pc}$',
    'CvrFract__04': 'Cov. Frac.',
    'PhoIndex__05': '$\Gamma$',
    'norm__08': 'Flux (1-10 keV)',
    'nH__2': '$n_\mathrm{H}$',
    'nH__3': '$n_\mathrm{H, pc}$',
    'CvrFract__4': 'Cov. Frac.',
    'PhoIndex__5': '$\Gamma$',
    'norm__8': 'Flux (1-10 keV)',
    'log(nH)__2': '$\log(n_\mathrm{H})$',
    'log(nH)__3': '$\log(n_\mathrm{H, pc})$',
    'log(norm)__8': '$\log$(Flux (1-10 keV))',
    'rate':'Count Rate'
}

def plot_fit_parameters(fit_by_bin, pn, t1, dt1, r, dr, plot_latex=False, latex_label_dict=None, skip_factors=True, save_plot=True):
    from matplotlib import rc

    fit_by_par = rearrange_fit_parameters(fit_by_bin)
    n_pars = len(fit_by_bin[0].keys())-1

    if latex_label_dict==None:
        latex_label_dict = default_latex_label_dict

    old_size = plt.rcParams['figure.figsize']
    plt.rcParams['figure.figsize'] = [8, 10]
    capsize = 0

    if plot_latex:

        rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
        rc('text', usetex=True)

    x = fit_by_par['times']['value']
    dx = fit_by_par['times']['err_p']

    n_factors=0
    if skip_factors:
        for ylabel in fit_by_par.keys():
            if 'factor' in ylabel:
                n_factors+=1

    fig, axes = plt.subplots(n_pars - 1 - n_factors, 1, sharex=True)

    axes[0].errorbar(t1, r, xerr=dt1, yerr=dr, capsize=capsize, linestyle='none', marker='o')
    axes[0].set_ylabel('Cts Rate')
    i = 1
    for ylabel in fit_by_par.keys():
        if ylabel == 'times' or ylabel == 'rate' or ylabel == 'cstat':
            continue
        if skip_factors and 'factor' in ylabel:
            continue

        axes[i].errorbar(x, fit_by_par[ylabel]['value'], xerr=dx,
                         yerr=[fit_by_par[ylabel]['err_m'], fit_by_par[ylabel]['err_p']], capsize=capsize,
                         linestyle='none', marker='o')
        if plot_latex:
            axes[i].set_ylabel(latex_label_dict[ylabel])
        else:
            axes[i].set_ylabel(ylabel)
        i += 1

    axes[i - 1].set_xlabel('Time [s] from %s' % pn.date_obs)
    axes[0].set_title('%s (%s)' % (pn.target, pn.obs_id))

    if save_plot:
        plt.savefig('spec_results_%s.pdf' % pn.obs_id)

    plt.rcParams['figure.figsize'] = old_size

    rc('text', usetex=False)


def plot_corner_from_chain(outputfiles_basename, latex_labels=False, latex_label_dict=None):
    from astropy.table import Table
    import corner
    from matplotlib import rc

    if latex_label_dict==None:
        latex_label_dict = default_latex_label_dict

    chain_name = outputfiles_basename + 'chain.fits'

    table_chain = Table.read(chain_name)
    chain_df = table_chain.to_pandas()

    to_be_dropped = ['FIT_STATISTIC']

    for kk in chain_df.keys():
        if 'factor' in kk:
            to_be_dropped.append(kk)

    try:
        for kk in to_be_dropped:
            chain_df.drop(kk, 1, inplace=True)
    except:
        pass

    labels=chain_df.columns.values.tolist()
    if latex_labels:
        rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
        rc('text', usetex=True)
        plot_labels=[ latex_label_dict[ll] for ll in labels ]
    else:
        rc('text', usetex=False)
        plot_labels=labels
    print(chain_df.quantile([0.16,0.5,0.84]))
    corner_plot = corner.corner(chain_df, bins=20, quantiles=[0.16, 0.5, 0.84], labels=plot_labels )
    corner_plot.savefig(outputfiles_basename + 'corner.pdf')

    rc('text', usetex=False)


def get_format_string(res, ep, em):
    # e_max=np.max(np.abs(ep), np.abs(em))
    e_min = np.min([np.abs(ep), np.abs(em)])
    myformat = "%.2f"

    if res == 0 or e_min == 0:
        return myformat

    decade = np.floor(np.log10(np.abs(res)))
    if e_min != res:
        decade_min = np.floor(np.log10(np.abs(res-e_min)))
    else:
        decade_min = np.floor(np.log10(np.abs(e_min)))

    #print("Getting Format")
    #print(res, em, ep, decade, decade_min)

    if (np.abs(decade) <= 2 and decade_min > 0):
        myformat = "%.0f"
    elif (np.abs(decade) == 0 and decade_min == 0):
        myformat = "%.1f"
    else:
        # print(decade, decade_min)
        if (np.abs(decade) <= 2 and decade_min <= 0):
            myformat = "%." + "%d" % (-decade_min) + "f"
            if np.abs(e_min / 10 ** (decade_min)) < 2:
                myformat = "%." + "%d" % (-decade_min + 1) + "f"
        else:
            myformat = "%." + "%d" % (np.abs(decade_min - decade)) + "e"
            if np.abs(e_min / 10 ** (decade_min)) < 2:
                myformat = "%." + "%d" % (np.abs(decade_min - decade) + 1) + "e"

    return myformat

def load_xcm(filename):

    #This is useless, you can use the xspec.Xset.restore(filename) command

    import xspec
    import re
    '''loads xcm file into pyxspec env'''
    model_flag = False
    model_param_counter = 1
    model_num = 1
    for cmd in open(filename):
        cmd = cmd.replace("\n", "")
        if model_flag == True:
            cmd = re.sub(
                "\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)\s+([\.|\d|\-|\w|\+]+)",
                "\g<1> \g<2> \g<3> \g<4> \g<5> \g<6>", cmd).split(" ")
            m = xspec.AllModels(model_num)
            p = m(model_param_counter)
            if "/" in cmd:
                model_param_counter += 1
                if model_param_counter > m.nParameters:
                    model_num += 1
                    model_param_counter = 1
                    if model_num > xspec.AllData.nGroups:
                        model_flag = False
                continue
            elif "=" in cmd:
                p.link = "".join(cmd).replace("=", "")
            else:
                p.values = [float(z) for z in cmd if not z == '']
                #map(float, [z for z in cmd if not z == ''])
            model_param_counter += 1
            if model_param_counter > m.nParameters:
                model_num += 1
                model_param_counter = 1

                if model_num > xspec.AllData.nGroups:
                    model_flag = False
        else:
            cmd = cmd.split(" ")
            if cmd[0] == "statistic":
                xspec.Fit.statMethod = cmd[1]
            elif cmd[0] == "method":
                xspec.Fit.method = cmd[1]
                xspec.Fit.nIterations = int(cmd[2])
                xspec.Fit.criticalDelta = float(cmd[3])
            elif cmd[0] == "abund":
                xspec.Xset.abund = cmd[1]
            elif cmd[0] == "xsect":
                xspec.Xset.xsect = cmd[1]
            elif cmd[0] == "xset":
                if cmd[1] == "delta":
                    xspec.Fit.delta = float(cmd[2])
            elif cmd[0] == "systematic":
                xspec.AllModels.systematic = float(cmd[1])
            elif cmd[0] == "data":
                xspec.AllData(" ".join(cmd[1:]))
            elif cmd[0] == "ignore":
                xspec.AllData.ignore(" ".join(cmd[1:]))
            elif cmd[0] == "model":
                model_flag = True
                xspec.Model(" ".join(cmd[1:]))
            elif cmd[0] == "newpar":
                m = xspec.AllModels(1)
                npmodel = m.nParameters  # number of params in model
                group = int(np.ceil((float(cmd[1])) / npmodel))

                if not int(cmd[1]) / npmodel == float(cmd[1]) / npmodel:
                    param = int(cmd[1]) - (int(
                        cmd[1]) / npmodel) * npmodel  # int div so effectivly p-floor(p/npmodel)*npmodel
                else:
                    param = npmodel

                print(group, param)

                m = xspec.AllModels(group)
                p = m(param)

                if "=" in cmd[2]:
                    p.link = "".join(cmd[2:]).replace("=", "")
                else:
                    p.values = map(float, cmd[2:])


def rearrange_fit_parameters(fit_by_bin):
    # Just rearrange dictionary to ease plotting

    fit_by_par = {}
    n_bins = len(fit_by_bin)

    for key in fit_by_bin[0].keys():
        fit_by_par[key] = dict(
            value=np.zeros(n_bins),
            err_p=np.zeros(n_bins),
            err_m=np.zeros(n_bins)
        )

        if key != 'cstat' and key != 'times':
            for j in range(n_bins):
                if key in fit_by_bin[j].keys():
                    fit_by_par[key]['value'][j] = fit_by_bin[j][key][0]
                    fit_by_par[key]['err_p'][j] = fit_by_bin[j][key][1] - fit_by_bin[j][key][0]
                    fit_by_par[key]['err_m'][j] = (-fit_by_bin[j][key][2] + fit_by_bin[j][key][0])
                else:
                    fit_by_par[key]['value'][j] = np.nan
                    fit_by_par[key]['err_p'][j] = np.nan
                    fit_by_par[key]['err_m'][j] = np.nan

        if key == 'times':
            for j in range(n_bins):
                fit_by_par[key]['value'][j] = (fit_by_bin[j][key][1] + fit_by_bin[j][key][0]) / 2
                fit_by_par[key]['err_p'][j] = (fit_by_bin[j][key][1] - fit_by_bin[j][key][0]) / 2
                fit_by_par[key]['err_m'][j] = (fit_by_bin[j][key][1] - fit_by_bin[j][key][0]) / 2

        if key == 'cstat':
            for j in range(n_bins):
                fit_by_par[key]['value'][j] = fit_by_bin[j][key][0] / fit_by_bin[j][key][1]
                fit_by_par[key]['err_p'][j] = 0
                fit_by_par[key]['err_m'][j] = 0

    return fit_by_par


def lin_model(p,x):
    a, b = p
    return a+b*x

def lin_residuals(p, data):
    a, b = p
    x, y, ex, ey = data
    w = ey*ey + b*b*ex*ex
    wi = np.sqrt(np.where(w==0.0, 0.0, 1.0/(w)))

    d = wi*(y-lin_model(p,x))
    #d=(y-a-b*x)/ey
    #print(x.shape, y.shape, ex.shape, ey.shape, d.shape)
    return d


def km_fit_confidence_band(x, dfdp, confprob, fitobj, f, abswei=False):
    from kapteyn import kmpfit
    #----------------------------------------------------------
    # Given a value for x, calculate the error df in y = model(p,x)
    # This function returns for each x in a NumPy array, the
    # upper and lower value of the confidence interval.
    # The arrays with limits are returned and can be used to
    # plot confidence bands.
    #
    #
    # Input:
    #
    # x        NumPy array with values for which you want
    #          the confidence interval.
    #
    # dfdp     A list with derivatives. There are as many entries in
    #          this list as there are parameters in your model.
    #
    # confprob Confidence probability in percent (e.g. 90% or 95%).
    #          From this number we derive the confidence level
    #          (e.g. 0.05). The Confidence Band
    #          is a 100*(1-alpha)% band. This implies
    #          that for a given value of x the probability that
    #          the 'true' value of f falls within these limits is
    #          100*(1-alpha)%.
    #
    # fitobj   The Fitter object from a fit with kmpfit
    #
    # f        A function that returns a value y = f(p,x)
    #          p are the best-fit parameters and x is a NumPy array
    #          with values of x for which you want the confidence interval.
    #
    # abswei   Are the weights absolute? For absolute weights we take
    #          unscaled covariance matrix elements in our calculations.
    #          For unit weighting (i.e. unweighted) and relative
    #          weighting, we scale the covariance matrix elements with
    #          the value of the reduced chi squared.
    #
    # Returns:
    #
    # y          The model values at x: y = f(p,x)
    # upperband  The upper confidence limits
    # lowerband  The lower confidence limits
    #
    # Note:
    #
    # If parameters were fixed in the fit, the corresponding
    # error is 0 and there is no contribution to the condidence
    # interval.
    #----------------------------------------------------------
    from scipy.stats import t
    # Given the confidence probability confprob = 100(1-alpha)
    # we derive for alpha: alpha = 1 - confprob/100
    alpha = 1 - confprob/100.0
    prb = 1.0 - alpha/2
    tval = t.ppf(prb, fitobj.dof)

    C = fitobj.covar
    n = len(fitobj.params)              # Number of parameters from covariance matrix
    p = fitobj.params
    N = len(x)
    if abswei:
        covscale = 1.0
    else:
        covscale = fitobj.rchi2_min
    df2 = np.zeros(N)
    for j in range(n):
        for k in range(n):
            df2 += dfdp[j]*dfdp[k]*C[j,k]
    df = np.sqrt(fitobj.rchi2_min*df2)
    y = f(p, x )
    delta = tval * df
    upperband = y + delta
    lowerband = y - delta
    return y, upperband, lowerband


def linear_fit_plot(x, y, xerr, yerr, ax, confprob=90.0):
    fitobj = kmpfit.Fitter(residuals=lin_residuals, data=(x, y, xerr, yerr))
    fitobj.fit(params0=[np.mean(y), -0.5])

    if (fitobj.status <= 0):
        print('error message =', fitobj.errmsg)
        raise SystemExit

    print("\n\n======== Results kmpfit for Y = A + B*X =========")
    print("Params:        ", fitobj.params)
    print("Errors from covariance matrix         : ", fitobj.xerror)
    print("Uncertainties assuming reduced Chi^2=1: ", fitobj.stderr)
    print("Chi^2 min dof:     ", fitobj.chi2_min, len(x) - 2)

    ax.plot(x, lin_model(fitobj.params, x))

    dfdp = [1, x]

    ydummy, upperband, lowerband = km_fit_confidence_band(x, dfdp, confprob, fitobj, lin_model)
    verts = list(zip(x, lowerband)) + list(zip(x[::-1], upperband[::-1]))
    poly = plt.Polygon(verts, closed=True, fc='b', ec='b', alpha=0.3,
                       label="CI (%.0f p.c.) relative weighting in Y" % confprob)
    ax.add_patch(poly)

    return fitobj.chi2_min



from scipy.stats import linregress
from scipy.stats import distributions


def linear_fit_plot_bootstrap(x, y, xerr, yerr, ax=None, confprob=68.0, n_sample=1000, verbose=True):
    results = []

    for i in range(n_sample):
        x0 = np.random.randn(len(x)) * xerr + x
        y0 = np.random.randn(len(y)) * yerr + y
        results.append(linregress(x0, y0))

    slopes = np.array([x[0] for x in results])
    intercepts = np.array([x[1] for x in results])
    r_values = np.array([x[2] for x in results])

    y_out = np.zeros([len(x), n_sample])

    for i in range(n_sample):
        y_out[:, i] = (intercepts[i] + x * slopes[i])

    r = np.percentile(r_values ** 2, [100 - confprob, 50, confprob])
    a=np.percentile(slopes, [100 - confprob, 50, confprob])
    b= np.percentile(intercepts, [100 - confprob, 50, confprob])

    TINY = 1e-20
    df = len(x) - 2
    t = r * np.sqrt(df / ((1.0 - r + TINY) * (1.0 + r + TINY)))
    prob = 2 * distributions.t.sf(np.abs(t), df)

    if verbose:
        print('------ Results from bootstrap are ---------')
        print('(the confidence probability is %d per cent)' % confprob)
        print("slope ", a)
        print("intercept",b)
        print("r_squared", r)
        print("probabilities", prob)
        print("\n\n")

    if ax is not None:
        bands = np.percentile(y_out, [100 - confprob, confprob], axis=1)

        ax.plot(x, intercepts.mean() + x * slopes.mean(), color='orange')

        verts = list(zip(x, bands[0, :])) + list(zip(x[::-1], bands[1, ::-1]))

        poly = plt.Polygon(verts, closed=True, fc='b', ec='b', alpha=0.3,
                           label="CI (%.0f p.c.) relative weighting in Y" % confprob)
        ax.add_patch(poly)

    return prob,r,a,b

def check_correlations(fit_by_bin, threshold=0.2, make_plots=True, verbose=True, n_sample=1000):

    old_size=plt.rcParams['figure.figsize']
    fit_by_par=rearrange_fit_parameters(fit_by_bin)

    list_par = list(fit_by_par.keys())
    to_remove = []
    for pp in list_par:
        # print(pp)
        if 'cstat' in pp or 'factor' in pp or 'times' in pp:
            to_remove.append(pp)

    for pp in to_remove:
        list_par.remove(pp)


    unique_pairs=get_unique_pairs(list_par)

    correlations=[]

    for cc in unique_pairs:
        xlabel = cc.pair[0]
        ylabel = cc.pair[1]

        if verbose:
            print(ylabel + ' vs ' + xlabel)
        x = np.array(fit_by_par[xlabel]['value'])
        y = np.array(fit_by_par[ylabel]['value'])
        xerr = np.array([fit_by_par[xlabel]['err_m'], fit_by_par[xlabel]['err_p']])
        yerr = np.array([fit_by_par[ylabel]['err_m'], fit_by_par[ylabel]['err_p']])
        if make_plots:
            ff = plt.figure()
            plt.rcParams['figure.figsize'] = [6, 4]
            plt.errorbar(x, y, xerr=xerr, yerr=yerr, capsize=0, linestyle='none', marker='o')
            ax = ff.gca()
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
        else:
            ax=None

        s_ind = np.argsort(x)
        prob, r, a, b = linear_fit_plot_bootstrap(x[s_ind], y[s_ind],
                                                        xerr.mean(axis=0)[s_ind], yerr.mean(axis=0)[s_ind],
                                                        n_sample=n_sample, ax=ax, verbose=verbose)
        if prob[1] < threshold:
            print('Found correlation with median probability (%.2f) below the threshold (%.2f)'%(prob[1], threshold) )
            print('Parameters are ' + ylabel + ' vs '+ xlabel)
            correlations.append({'x': xlabel,
                                 'y' : ylabel,
                                 'probability': prob,
                                 'r**2':r,
                                 'a': a,
                                 'b': b})

    plt.rcParams['figure.figsize']=old_size

    return correlations

def pretty_plot_correlation(fit_by_par, xlabel,ylabel,latex_label_dict=default_latex_label_dict, obs_id='', n_sample=1000):

    from matplotlib import rc

    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    rc('text', usetex=True)
    old_size = plt.rcParams['figure.figsize']
    ff = plt.figure()
    plt.rcParams['figure.figsize'] = [6, 4]
    x = np.array(fit_by_par[xlabel]['value'])
    y = np.array(fit_by_par[ylabel]['value'])
    xerr = np.array([fit_by_par[xlabel]['err_m'], fit_by_par[xlabel]['err_p']])
    yerr = np.array([fit_by_par[ylabel]['err_m'], fit_by_par[ylabel]['err_p']])
    plt.errorbar(x, y, xerr=xerr, yerr=yerr, capsize=0, linestyle='none', marker='o')
    ax = ff.gca()
    ax.set_xlabel(latex_label_dict[xlabel])
    ax.set_ylabel(latex_label_dict[ylabel])

    s_ind = np.argsort(x)
    prob, r, a, b = linear_fit_plot_bootstrap(x[s_ind], y[s_ind],
                                              xerr.mean(axis=0)[s_ind], yerr.mean(axis=0)[s_ind],
                                              n_sample=n_sample, ax=ax, verbose=True)

    plt.savefig('correlation_%s_%s_'%(xlabel,ylabel)+obs_id+'.pdf')

    rc('text', usetex=False)
    plt.rcParams['figure.figsize']=old_size


#aperture photometry routine
from photutils import CircularAnnulus

def extract_counts(img, nominal_y,nominal_x, pix_region):

    #nx, ny = img.shape

    #xv,yv = np.meshgrid(np.arange(nx)-nominal_x, np.arange(ny)-nominal_y)

    #print(xv)

    #r = np.sqrt(xv**2+yv**2)

    #ind = r <= pix_region

    #return np.sum(img[ind])

    aperture = CircularAperture((nominal_x,nominal_y), r=pix_region)
    #aperture = CircularAnnulus((nominal_x,nominal_y), r_in=pix_region, r_out=pix_region+1)


    phot_table = aperture_photometry(img, aperture)
    return phot_table['aperture_sum'].data[0] #, aperture.area

def get_utc_from_xmm_seconds(input_time):
    mjdref=50814.0

    from astropy.time import Time
    t=Time(mjdref + input_time / 86400., format='mjd')

    print('MJD =', t.mjd)
    print('ISOT = ', t.isot)

    return t.mjd, t.isot


def get_spec_exp_times(fname):

    spec_file = pf.open(fname)
    exposure = spec_file[1].header['EXPOSURE']

    try:
        select_expr = spec_file[1].header['SLCTEXPR']
        # print(select_expr)
        tmp = select_expr.replace('&&', '').lower().split('time in (')
        # print(tmp)
        tmp1 = tmp[-1].split(':')
        # print(tmp1)
        tstop = float(tmp1[-1].replace(')', ''))
        tstart = float(tmp1[-2])
    except:
        # break
        print("Deriving tstart and tstop from general header, it might not be correct")
        tstart = spec_file[0].header['TSTART']
        tstop = spec_file[0].header['TSTOP']

    spec_file.close()

    return exposure, tstart, tstop






class xmmanalysis(object):

    def __init__(self, workdir='.'):

        self.workdir=workdir

        sas_index=glob(workdir+'/*.SAS')

        #print('CHECK', sas_index)

        self.instrument = 'none'

        if not sas_index:

            print("Start initializing SAS structure")
            status = wrap_run(workdir, 'preamble', self.sas_preamble)
            if status != 0:
                print('Exit status is %d')
                raise RuntimeError

    def get_obs_info(self, ev_name='PN.fits'):
        ev_f = pf.open(ev_name)
        header = ev_f[1].header

        target_raw = header['OBJECT']
        # to solve an issue
        tmp = target_raw.replace('- ', '-')
        target = tmp.replace('+ ', '+')

        obs_id = header['OBS_ID']
        date_obs = header['DATE-OBS']
        date_end = header['DATE-END']
        ra = float(header['RA_OBJ'])
        dec = float(header['DEC_OBJ'])

        ev_f.close()
        return target, obs_id, date_obs, date_end, ra, dec


    def get_spec_info(self, base_name='spectrum', emin=0.5, emax=10.0):
        #For PN
        ch_min=int(emin/5e-3)
        ch_max=int(emax/5e-3)

        fname="%ssource_%s.fits"%(self.instrument, base_name)

        exposure,tstart,tstop=get_spec_exp_times(fname)

        spec_file = pf.open(fname)
        counts = spec_file[1].data['COUNTS'][ch_min:ch_max].sum()
        rate = [counts / exposure, np.sqrt(counts) / exposure]
        spec_file.close()

        bfname = "%sbackground_%s.fits" % (self.instrument, base_name)


        spec_file = pf.open(bfname)

        bcounts = spec_file[1].data['COUNTS'][ch_min:ch_max].sum()
        brate = (bcounts / exposure, np.sqrt(bcounts) / exposure)
        spec_file.close()


        rate[0] = rate[0] - brate[0]

        rate[1] = np.sqrt(rate[1]**2 + brate[1]**2)

        print("Spectrum %s has exposure %.0g s and rate %.2g +/- %.2g"%(fname,exposure,rate[0], rate[1]))
        print("\tTstart = %.1f Tstop=%.1f"%(tstart,tstop))

        return exposure, rate, tstart, tstop


    def get_target_coords_extern(self, input_name=None):
        from astroquery.simbad import Simbad
        from astropy import units as u
        if input_name is None:
            name=self.target
        else:
            name=input_name

        simbad = Simbad.query_object(name)
        c = SkyCoord(simbad['RA'], simbad['DEC'], unit=[u.hour, u.deg])
        c.fk5

        print("Coordinates for %s are RA=%.4f, Dec=%.4f"%(name,c.ra.deg[0], c.dec.deg[0] ) )

        return c.ra.deg[0], c.dec.deg[0]

    def sas_get_extraction_region(self, min_psf=3, max_psf=30, default_psf=1.0,
                             relative_x_offset=-2, relative_y_offset=+2,
                             forced_r_pix=-1, use_max_coord=False,
                             ra_target=np.nan, dec_target=np.nan, input_image=None,
                                  criterion='surface', make_plots=True, input_exp_map=None, delta_r=2,
                                  critical_surface_brightness=1):
        #default
        ra = self.ra
        dec = self.dec

        # input ra and dec
        if np.isfinite(ra_target) and np.isfinite(dec_target):
            if ra_target >= 0 and ra_target <= 360 and dec_target >= -90 and dec_target <= 90:
                ra = ra_target
                dec = dec_target
                print("The header coordinates are RA=%.4f Dec=%.4f"%(self.ra,self.dec))
                self.ra=ra_target
                self.dec=dec_target
                print("The input coordinates are RA=%.4f Dec=%.4f" % (self.ra, self.dec))




        if input_image is None:
            filename=self.workdir+'/PNimage.fits'
            try:
                f_header = pf.open(filename)
            except:
                print ("No file "+filename)
                filename = self.workdir + '/PNimage.img'
                try:
                    f_header = pf.open(filename)
                except:
                    print("No file "+filename)
                    raise FileExistsError
        else:
            filename=input_image
            try:
                f_header = pf.open(filename)
            except:
                print("No file " + filename)
                raise FileExistsError


        hdu = f_header[0]
        my_wcs = WCS(hdu.header)
        image = hdu.data

        if input_exp_map is not None:
            try:
                exp_map_hdu=pf.open(input_exp_map)
            except:
                raise RuntimeError('No exposure map named %s'%input_exp_map)

            exposure_map=exp_map_hdu[0].data
            exposed_image=image.astype(float)

            ind = np.logical_and(image > 0, exposure_map > 1)

            exposed_image[ind] /= exposure_map[ind] / exposure_map.max()

            ind = exposed_image >= 2 * image.max()
            exposed_image[ind] *= 0.0

            exp_map_hdu.close()

            image=exposed_image.copy()




        #makes figure
        if make_plots:
            fig1 = plt.figure()
            ax = plt.subplot(projection=my_wcs)
            plt.imshow(image + 1, norm=LogNorm(), vmin=1, vmax=50)  # , vmin=-2.e-5, vmax=2.e-4, origin='lower')
            plt.colorbar()
            ax.grid(color='white', ls='solid')
            ax.set_xlabel('RA')
            ax.set_ylabel('Dec')
            # overlay = ax.get_coords_overlay('physical')
            # overlay.grid(color='white', ls='dotted')
            # overlay[0].set_axislabel('X')
            # overlay[1].set_axislabel('Y')

        print("Image shape: ", image.shape)

        #Conversion facotors
        REFXLMIN = hdu.header['REFXLMIN']
        REFXLMAX = hdu.header['REFXLMAX']

        REFYLMIN = hdu.header['REFYLMIN']
        REFYLMAX = hdu.header['REFYLMAX']

        xscale = (REFXLMAX - REFXLMIN) / image.shape[0]
        yscale = (REFYLMAX - REFYLMIN) / image.shape[0]

        f_header.close()

        # Checck the maximum of image
        ind_max = np.unravel_index(np.argmax(image, axis=None), image.shape)
        print("Image maximum is at ", my_wcs.wcs_pix2world(ind_max[1], ind_max[0], 0))
        if make_plots:
            ax.scatter(ind_max[1], ind_max[0], s=40, marker='+', color='white')

        # Gets the target coordinates
        if use_max_coord:
            nominal_x = ind_max[1]
            nominal_y = ind_max[0]
        else:
            nominal_x, nominal_y = my_wcs.all_world2pix(ra, dec, 0)



        # gets the scaling of physical coordinates
        scale_matrix = my_wcs.pixel_scale_matrix
        pix_region = default_psf / 60. / scale_matrix[1, 1]
        back_x = nominal_x + relative_x_offset * pix_region
        back_y = nominal_y + relative_y_offset * pix_region

        if make_plots:
            # PLOTS THE default SRC REGION WITH 90% CONFINEMENT
            ax.scatter(nominal_x, nominal_y, s=40, marker='x', color='red')

            circle = plt.Circle([nominal_x, nominal_y], pix_region, color='red', fill=False, linestyle='--')
            ax.add_artist(circle)

            # PLOTS THE defaultBACK REGION WITH 90% CONFINEMENT
            circle = plt.Circle([back_x, back_y], pix_region, color='white', fill=False)
            ax.add_artist(circle)
            ax.set_title(self.target + ' ' + self.obs_id)

        # Physical coordinates

        physical_x = xscale * nominal_x
        physical_y = yscale * nominal_y

        physical_back_x = xscale * back_x
        physical_back_y = yscale * back_y

        # physical_r = pix_region * (xscale+yscale)/2.
        back_counts=extract_counts(image, back_y, back_x, 20)/20**2
        # Computes the PSF
        r_psf=np.linspace(1, 2 * int(np.floor(pix_region)), 2 * int(np.floor(pix_region)))
        #psf = [(x, extract_counts(image, nominal_y, nominal_x, x)) for x in r_psf]
        #apertures = [CircularAperture((nominal_x, nominal_y), r=x) for x in r_psf]
        apertures = [CircularAnnulus((nominal_x, nominal_y), r_in=x, r_out=x+delta_r) for x in r_psf]
        phot_table=aperture_photometry(image, apertures)
        aperture_areas=np.array([aa.area for aa in apertures])
        my_keys=[x for x in phot_table.keys() if 'aperture_sum' in x]
        c_psf = np.array([phot_table[kk][0] for kk in my_keys])

        c_psf /= aperture_areas

        #psf_back = [(x, extract_counts(image, back_y, back_x, x)) for x in r_psf]
        psf_back = [(x, back_counts) for x in r_psf] #*x**2
        # gets and plots the maximum S/N
        #r_psf = [x[0] for x in psf]
        #print(r_psf)
        #c_psf = [x[1] for x in psf]
        r_back = np.array([x[0] for x in psf_back])
        c_back = np.array([x[1] for x in psf_back])

        c_net = np.array(c_psf) - np.array(c_back)
        #scan change of slope
        last_ind=2
        for i in range(2,len(c_net)):
            last_ind = i
            if c_net[i] >= np.mean(c_net[i-2:i-1]):
                print('found change of slope in PSF at index %d'%i)
                break


        real_psf = np.array([extract_counts(image, nominal_y, nominal_x, x) for x in r_psf])
        real_psf_net = real_psf - c_back*r_back**2

        norm_cum_sum = real_psf_net/real_psf_net.max()

        gradient = np.gradient(real_psf_net)
        #back_gradient = np.gradient(c_back)
        gradient /= gradient.max()

        #gradient2 = np.gradient(gradient)
        #gradient2 /= np.max(np.abs(gradient))
        #s_n = c_net * aperture_areas / np.sqrt(c_psf * aperture_areas)
        s_n = real_psf_net/np.sqrt(real_psf)

        if make_plots:
            fig2, ax_2 = plt.subplots(1, 2, sharex=True)
            ax_2[0].plot(r_psf, c_psf, color='blue', label="anulus brillance")
            ax_2[0].plot(r_back, c_back, color='red', label="background brillance")
            ax_2[0].plot(r_back, c_net, color='green', label="anulus net brillance")

            # ax_2[0].plot(r_psf, real_psf, color='blue', label="Cum PSF")
            # ax_2[0].plot(r_back, c_back*r_back**2, color='red', label="background")
            # ax_2[0].plot(r_back, real_psf_net, color='green', label="Net PSF")

            ax_2[0].set_title(self.target + ' ' + self.obs_id)
            ax_2[0].legend()

            ax_2[1].plot(r_psf, norm_cum_sum, color='black', label="Cum PSF")

            ax_2[1].plot(r_psf, gradient, color='blue', label='PSF')
            #ax_2[1].plot(r_psf, back_gradient, color='red', label='back gradient')
            #ax_2[1].plot(r_psf, gradient2, color='green', label='gradient2')

            ax_2[1].plot(r_psf, s_n/s_n.max(), color='cyan', label='S/N')

            ax_2[1].grid(b=True)
            ax_2[1].legend()


        #if criterion.lower() == 's_n':
        ind_95 = int(np.argmin(np.abs(c_net[0:last_ind] - critical_surface_brightness )) + delta_r/2)
        if ind_95 >= len(r_psf):
            ind_95=len(r_psf)-1

        if criterion == '95':
            ind_95 = np.argmin(np.abs(norm_cum_sum - 0.95))

        # if criterion == 'gradient':
        #     ind_95 = np.argmax(gradient)
        #
        # if criterion == 'gradient2':
        #     ind_95 = np.argmax(gradient2)


        if make_plots:
            ax_2[1].scatter(r_psf[ind_95], norm_cum_sum[ind_95], marker='x', color='red')


        r_max = r_psf[ind_95]
        c_max = c_net[ind_95]

        print("Optimal inclusion is r=%.1f +/- %.1f with %.1f cts/pix " % (r_max, delta_r/2, c_max))
        print("Cumulative PSF is %.2f"%norm_cum_sum[ind_95])

        if r_max < min_psf:
            print('r_max is lower than %.1f' % min_psf)
            r_max = min_psf

        if r_max > max_psf:
            print('r_max is larger than %.1f' % max_psf)
            r_max = max_psf

        if forced_r_pix > 0:
            r_max = forced_r_pix
            print("Input forced radius for extraction region at %.1f"%r_max)

        if make_plots:
            # plt.scatter(r_max,c_max,s=60,marker='x', color='red')

            ax_2[0].axvline(r_max, 0, 1, color='black', linestyle='--', linewidth=2)
            ax_2[1].axvline(r_max, 0, 1, color='black', linestyle='--', linewidth=2)

        physical_r_max = r_max * (xscale + yscale) / 2.
        physical_r_back = pix_region * (xscale + yscale) / 2.

        if make_plots:
            circle = plt.Circle([back_x, back_y], pix_region, color='white', fill=False)
            ax.add_artist(circle)
            circle = plt.Circle([nominal_x, nominal_y], r_max, color='red', fill=False)
            ax.add_artist(circle)

            fig1.savefig(self.workdir+'/%s.png'%(filename.split('.')[-2].split('/')[-1]))
            fig2.savefig(self.workdir+'/%s_psf.png'%(filename.split('.')[-2].split('/')[-1]))

        sas_source_coord = 'x_src=%.1f\ny_src=%.1f\nr_src=%.1f\n' % (physical_x, physical_y, physical_r_max)
        sas_back_coord = 'x_bkg=%.1f\ny_bkg=%.1f\nr_bkg=%.1f\n' % (physical_back_x, physical_back_y, physical_r_back)

        print("source physical coordinates\n"+ sas_source_coord)
        print("background physical coordinates\n"+ sas_back_coord)

        return sas_source_coord,sas_back_coord

    def print_infos(self):
        print('We observe the target %s with obs_id=%s, from %s to %s' % (self.target, self.obs_id, self.date_obs, self.date_end))


    def sas_extract_source_events(self, sas_source_coord):

        cmd_extract=self.sas_evt_extraction_cmd%(self.instrument,self.instrument)

        status = wrap_run(self.workdir, '%s_extract_src_events' % (self.instrument),
                          self.sas_init+sas_source_coord+cmd_extract)

        if status != 0:
            print("extract %s lc finished with status %d" % (self.instrument, status))
            raise RuntimeError

    sas_pileup_evt_extraction_cmd = '''    
evselect table=%s.fits withfilteredset=Y \
filteredset=%s_pileup_%s_%04d.fits destruct=Y keepfilteroutput=T \
expression="((X,Y) IN ANNULUS($x_src,$y_src,$r_annulus, $r_src))  && (TIME IN (%.2f:%.2f)) " \
updateexposure=yes filterexposure=yes
'''

    def sas_check_pileup(self, sas_source_coord, n_tests=5, step=50, r_min=0, pileupnumberenergyrange="1000 8000", sigma_threshold=1.5, tmin=0, tmax=1e13, name='test'):

        tmp=sas_source_coord.split('\n')
        for ii in tmp:
            if 'r_src' in ii:
                r_src=float(ii.replace('r_src=',''))

        if step < 0:
            step =  r_src/float( n_tests ) / 2

        results={}
        ok_flag=False
        r_exision=-1
        for i in range(n_tests):

            r_annulus = float(i) * step + r_min

            print('r_annulus = ', r_annulus )

            cmd_extract=self.sas_pileup_evt_extraction_cmd%(self.instrument,self.instrument, name, r_annulus, tmin, tmax)
            cmd_epatplot='\nepatplot set=%s_pileup_%s_%04d.fits plotfile="%s_pileup_%s_%04d.ps" '%(self.instrument, name, r_annulus,
                                                                                                       self.instrument, name, r_annulus)+ \
                'pileupnumberenergyrange="%s"\n'%(pileupnumberenergyrange)
            cmd_convert='\nif [ -f %s_pileup_%s_%04d.ps ]; then\n\tconvert %s_pileup_%s_%04d.ps %s_pileup_%s_%04d.png\nfi\n'%(self.instrument, name, r_annulus,
                                                                                                                              self.instrument, name, r_annulus,
                                                                                     self.instrument, name, r_annulus)
            str_anulus="\nr_annulus=%.1f\n"%(r_annulus)

            status = wrap_run(self.workdir, '%s_%s_pileup_%04d'%(self.instrument, name, r_annulus),
                              self.sas_init+sas_source_coord+str_anulus+cmd_extract+ cmd_epatplot+cmd_convert)



            if status != 0:
                print("extract %s lc finished with status %d" % (self.instrument, status))
                raise RuntimeError

            evt_file_name='%s_pileup_%s_%04d.fits'%(self.instrument, name, r_annulus)

            try:
                evt_file=pf.open(evt_file_name)
                sngl_otm=evt_file[1].header['SNGL_OTM']
                esgl_otm=evt_file[1].header['ESGL_OTM']
                dble_otm=evt_file[1].header['DBLE_OTM']
                edbl_otm = evt_file[1].header['EDBL_OTM']
                evt_file.close()
            except:
                sngl_otm=0
                esgl_otm=0
                dble_otm=0
                edbl_otm=0

            results.update({
                r_annulus: { 'SNGL_OTM': sngl_otm,
                            'ESGL_OTM' : esgl_otm,
                            'DBLE_OTM' : dble_otm,
                            'EDBL_OTM': edbl_otm
                            }
            })

            try:
                _ = display(Image(filename=self.workdir + '/%s_pileup_%s_%04d.png' % (self.instrument, name, r_annulus), format="png"))
            except:
                pass

            if(sngl_otm  == 0.0 or dble_otm == 0.0  ):
                r_exision = 0
                print("r_exision is ", r_exision, ' because of zero values of fitted parameters')
                break


            if ((np.abs(sngl_otm-1.0 )/esgl_otm) < sigma_threshold) and ((np.abs(dble_otm-1.0 )/edbl_otm) < sigma_threshold) and ok_flag is False:
                r_exision = r_annulus
                print("r_exision is ", r_exision, ' with threshold ', sigma_threshold)
                ok_flag=True
                break

            #SNGL_OTM= 9.60719525814056E-01 / 0.5-2.0 keV observed-to-model singles fraction
            # ESGL_OTM= 4.78429794311523E-02 / obs-to-mod singles fraction error
            # DBLE_OTM= 1.09850776195526E+00 / 0.5-2.0 keV observed-to-model doubles fraction
            # EDBL_OTM= 7.24474564194679E-02 / obs-to-mod doubles fraction error

        return results, r_exision

    def sas_hr_lc_extraction(self, sas_source_coord, sas_back_coord, s_n_rebin=8, forced_median=-1, run_sas=False,
                             run_rebin=False,
                             make_plot=True, timebin=1.0, min_pi = 500, max_pi = 10000, tmin=-1, tmax=-1):

        evt_file_name = self.workdir + "/%ssource_events.fits"%self.instrument
        try:
            ev_f = pf.open(evt_file_name)
        except:
            print(evt_file_name + ' does not exist, extracting it.')
            self.sas_extract_source_events(sas_source_coord)
            try:
                ev_f = pf.open(evt_file_name)
            except:
                RuntimeError('Not found %s after extraction.'%evt_file_name)

        # header = ev_f[1].header
        pi = ev_f[1].data['PI']
        times=ev_f[1].data['TIME']
        ev_f.close()

        if tmin <0:
            tmin=times.min()
        if tmax <0:
            tmax=times.max()

        median_pi = np.floor(np.median(pi))

        print('We observe the target %s with obs_id=%s, from %s to %s' % (
        self.target, self.obs_id, self.date_obs, self.date_end))
        print('The median energy of incoming photons is %.2f kev' % (median_pi / 1000))

        if forced_median > 0:
            median_pi = forced_median
            print('User defined limit for HR is %.2f kev' % (median_pi / 1000))

        if make_plot:
            plt.rcParams['figure.figsize'] = [6, 4]
            my_fig=plt.figure()

            hh, eges, patches = plt.hist(pi, bins=100, color='blue')
            ax=my_fig.gca()
            ax.set_xlabel('PI')
            _ = plt.vlines([min_pi, median_pi, max_pi], 0, np.max(hh), color='cyan')
            plt.savefig(self.workdir + '/%s_hist_pi.pdf'%self.instrument)

        e1_str = '%03.0f' % (min_pi / 1e2)
        e2_str = '%03.0f' % (median_pi / 1e2)
        e3_str = '%03.0f' % (max_pi / 1e2)

        soft_lc_root_name = "lc_01s_%s-%s" % (e1_str, e2_str)
        hard_lc_root_name = "lc_01s_%s-%s" % (e2_str, e3_str)
        # expression_soft = '(PI in (%d:%d))' % (min_pi, median_pi)
        # expression_hard = '(PI in (%d:%d))' % (median_pi, max_pi)

        if run_sas:

            soft_lc_name=self.sas_extract_lc(sas_source_coord, sas_back_coord, base_name=soft_lc_root_name,
                                             pimin=min_pi, pimax=median_pi,
                                 run_lccorr=True, timebin=timebin, tmin=tmin, tmax=tmax )

            hard_lc_name=self.sas_extract_lc(sas_source_coord, sas_back_coord, base_name=hard_lc_root_name,
                                             pimin=median_pi, pimax=max_pi,
                                 run_lccorr=True, timebin=timebin , tmin=tmin, tmax=tmax)
        else:
            soft_lc_name='%ssrc_%s.fits'%(self.instrument,soft_lc_root_name)
            hard_lc_name='%ssrc_%s.fits'%(self.instrument,hard_lc_root_name)


        hratio_base_name = "%s_hratio_%s_%s_%s" % (self.instrument, e1_str, e2_str, e3_str)

        if run_rebin:
            rebinned_lc=self.adaptive_lc_rebin(soft_lc_name, hard_lc_name, hratio_base_name, s_n_rebin, e1_str, e2_str, e3_str)
        else:
            rebinned_lc='none'

        return (times[0], times[-1]), soft_lc_name, hard_lc_name, rebinned_lc

    def adaptive_lc_rebin(self, soft_lc_name, hard_lc_name, hratio_base_name, s_n_rebin, e1_str, e2_str, e3_str ):
        timingsuite_command = '''\n${HOME}/Soft/timingsuite/dist/Debug/GNU-MacOSX/timingsuite<<EOF
8
%s
%s
%s.qdp
%.1f
100000
0
10000
100
-1
n
1
1

EOF

qdp lc_%s.qdp<<EOF
screen white
lab title %s
lab f Soft=%s-%s keV Hard=%s-%s keV S/N=%.1f
lab x Time since %s [s]
hard lc_%s.png/PNG
we lc_hratio


quit

EOF
''' % (soft_lc_name,hard_lc_name,hratio_base_name, s_n_rebin, hratio_base_name,
       self.target, e1_str, e2_str, e2_str, e3_str, s_n_rebin,
       self.date_obs.replace('T', ' ')[0:19], hratio_base_name)




        status = wrap_run(self.workdir, 'timingsuite', self.sas_init + timingsuite_command)
        if status != 0:
            print('Rebin with timingsuite failed')
            raise RuntimeError

        _ = display(Image(filename=self.workdir + '/lc_%s.png' % (hratio_base_name), format="png"))

        return "lc_%s.png"%(hratio_base_name)

    def sas_extract_lc(self, sas_source_coord, sas_back_coord, base_name='lc', pimin=500, pimax=10000,
                             run_lccorr=True, tmin=0, tmax=1000, timebin=1.2):

        self.print_infos()

        m = self.instrument

        cmd_str = self.sas_init + sas_source_coord + sas_back_coord \
                  + self.sas_commands_lc_src % (m, m, base_name, pimin, pimax, tmin, tmax, timebin) \
                  + self.sas_commands_lc_back % (m, m, base_name, pimin, pimax, tmin, tmax, timebin)

        if run_lccorr:
            cmd_str += self.sas_commands_lccorr % (m, base_name, m,
                                               m, base_name, m, base_name)

        status = wrap_run(self.workdir, '%s_%s'%(self.instrument, base_name), cmd_str)

        if status != 0:
            print("extract %s lc finished with status %d" %(self.instrument, status))
            raise RuntimeError

        return '%ssrc_%s.fits'%(m,base_name)

    # six arguments: instrument Image_name, low_pi, high_pi, tmin, tmax
    sas_extract_image_pi_time = '''
evselect table=%sbary_clean.fits imagebinning=binSize imageset=%s withimageset=yes \
expression='(PI IN (%d:%d)) && (TIME IN (%.2f:%.2f))' \
xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80
    '''

    ev_filter_expression_base = '(PI IN (500:12000)) && (TIME IN (%.2f:%.2f))'
    # six arguments
    sas_command_exposure_map = '''
eexpmap imageset=%s attitudeset=%s eventset=%s.fits expimageset=%s pimin=%d pimax=%d attrebin=0.020626481
    '''
    sas_preamble = '''#!/bin/bash
#SBATCH
#

if [ -x "$(command -v module)" ]; then
    module use /astro/soft/modulefiles/
    module unuse /etc/modulefiles
    module add astro

    module load hea
    module load heasoft/6.25_anaconda3_hea
    module load xmm_sas/17.0.0
fi

if [ -z "$HEADAS" ]
then 
    export HEADAS=/opt/heasoft/x86_64-pc-linux-gnu-libc2.27;. $HEADAS/headas-init.sh;source /opt/CalDB/software/tools/caldbinit.sh;export RELXILL_TABLE_PATH=/home/user/data/relline_tables/
fi

if [ -z "$SAS_CCFPATH" ]
then
    . /opt/xmmsas/setsas.sh;export SAS_CCFPATH=/opt/CalDB/ccf/
fi

export SAS_ODF=`pwd`/odf
cifbuild
export SAS_CCF=`pwd`/ccf.cif
odfingest
export SAS_ODF=`pwd`/`ls *.SAS`

'''

    sas_init = '''#!/bin/bash
#SBATCH

if [ -x "$(command -v module)" ]; then
    module use /astro/soft/modulefiles/
    module unuse /etc/modulefiles
    module add astro

    module load hea
    module load heasoft/6.25_anaconda3_hea
    module load xmm_sas/17.0.0
fi

if [ -z "$HEADAS" ]
then 
    export HEADAS=/opt/heasoft/x86_64-pc-linux-gnu-libc2.27;. $HEADAS/headas-init.sh;source /opt/CalDB/software/tools/caldbinit.sh;export RELXILL_TABLE_PATH=/home/user/data/relline_tables/
fi

if [ -z "$SAS_CCFPATH" ]
then
    . /opt/xmmsas/setsas.sh;export SAS_CCFPATH=/opt/CalDB/ccf/
fi

export SAS_CCF=`pwd`/ccf.cif
export SAS_ODF=`pwd`/`ls *.SAS`

if [ -f /home/ferrigno/Soft/myVE-py37/bin/activate ]
then
    export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1;source /home/ferrigno/Soft/myVE-py37/bin/activate
fi

'''

    sas_epproc = '''

epproc
cp `ls *EPN*ImagingEvts.ds` PN.fits
evselect table=PN.fits withrateset=Y rateset=ratePN.fits maketimecolumn=Y timebinsize=100 makeratecolumn=Y expression='#XMMEA_EP && (PI>10000&&PI<12000) && (PATTERN==0)'
atthkgen atthkset=attitude.dat

'''

    sas_commands_av_src = '''
evselect table=PNbary_clean.fits energycolumn=PI \
    expression="#XMMEA_EP&&(PATTERN<=4)&& ((X,Y) IN circle($x_src,$y_src,$r_src)) && (PI in [500:10000])" \
    withrateset=yes rateset="PN_source_lightcurve_raw.fits" timebinsize=100 \
    maketimecolumn=yes makeratecolumn=yes

evselect table=PNbary_clean.fits withfilteredset=Y \
    filteredset=PNsource_events.fits destruct=Y keepfilteroutput=T \
    expression="#XMMEA_EP && (PATTERN<=4)&& ((X,Y) IN circle($x_src,$y_src,$r_src)) && (PI IN (500:12000))" \
    updateexposure=yes filterexposure=yes


evselect table=PNbary_clean.fits withspectrumset=yes spectrumset=PNsource_spectrum.fits  \
    energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 \
    expression="#XMMEA_EP&&(PATTERN<=4)&& ((X,Y) IN circle($x_src,$y_src,$r_src))"

backscale spectrumset=PNsource_spectrum.fits badpixlocation=PNbary_clean.fits

'''

    sas_commands_av_back = '''
evselect table=PNbary_clean.fits energycolumn=PI \
    expression="#XMMEA_EP&&(PATTERN<=4)&& ((X,Y) IN circle($x_bkg,$y_bkg,$r_bkg)) && (PI in [500:10000])" \
    withrateset=yes rateset="PNbackground_lightcurve.fits" timebinsize=100 \
    maketimecolumn=yes makeratecolumn=yes


evselect table=PNbary_clean.fits withfilteredset=Y filteredset=PNbackground_events.fits \
    destruct=Y keepfilteroutput=T \
    expression="#XMMEA_EP && (PATTERN<=4)&& ((X,Y) IN circle($x_bkg,$y_bkg,$r_bkg)) && (PI IN (500:12000))" \
    updateexposure=yes filterexposure=yes


evselect table=PNbary_clean.fits withspectrumset=yes spectrumset=PNbackground_spectrum.fits  \
    energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 \
    expression="#XMMEA_EP&&(PATTERN<=4)&& ((X,Y) IN circle($x_bkg,$y_bkg,$r_bkg))"

backscale spectrumset=PNbackground_spectrum.fits badpixlocation=PNbary_clean.fits


'''

    sas_command_lc_corr = '''
epiclccorr srctslist='PN_source_lightcurve_raw.fits' eventlist='PNbary_clean.fits' \
    outset='PN_source_lightcurve.fits' bkgtslist='PNbackground_lightcurve.fits' \
    withbkgset=yes applyabsolutecorrections=yes
'''

    sas_commands_av_rsp = '''

rmfgen spectrumset=PNsource_spectrum.fits rmfset=PN.rmf

arfgen spectrumset=PNsource_spectrum.fits arfset=PN.arf withrmfset=yes rmfset=PN.rmf \
    badpixlocation=PNbary_clean.fits detmaptype=psf

optimal_binning.py PNsource_spectrum.fits -b PNbackground_spectrum.fits -r PN.rmf -a PN.arf -e 0.5 -E 10.5

'''

    hr_lc_extraction_base = '''

evselect table=PNsource_events.fits energycolumn=PI expression="%s" \
    withrateset=yes rateset="%s_raw.fits" timebinsize=0.1 maketimecolumn=yes makeratecolumn=yes

evselect table=PNbackground_events.fits energycolumn=PI expression="%s" \
    withrateset=yes rateset="%s_back.fits" timebinsize=0.1 maketimecolumn=yes makeratecolumn=yes

epiclccorr srctslist='%s_raw.fits' eventlist='PNbary_clean.fits' \
    outset='%s.fits' bkgtslist='%s_back.fits' withbkgset=yes applyabsolutecorrections=yes

'''

    def sas_extract_image(self, image_name='PNimage.fits', pi_min=500, pi_max=11000, tmin=0, tmax=1e12,
                          display_image=False, expo_map_name='none'):


        image_command = self.sas_extract_image_pi_time % (self.instrument, image_name, pi_min, pi_max, tmin, tmax)
        if expo_map_name != 'none':
            image_command += '\natthkgen atthkset=att_%s '%image_name
            if tmax - tmin < 3e5:
                image_command +='withtimeranges=true timebegin=%.1f timeend=%.1f\n' % (tmin, tmax)
            else:
                image_command +='\n'

            image_command += self.sas_command_exposure_map % (image_name, 'att_' + image_name, self.instrument,
                                                            expo_map_name, pi_min, pi_max) + '\n'

        status = wrap_run(self.workdir, '%s_extract_%s' % (self.instrument,
                                                           image_name.split('.')[-2]), self.sas_init + image_command)

        if status != 0:
            print("Error in extracting %s image"%self.instrument)
            raise RuntimeError

        if display_image:
            print("Not implemented")


    def sas_cr_filter(self, typical_level=0.5, quantile=0.7, run_sas=False, make_plot=True,
                            tmin=0,tmax=1e12,apply_rate_filter=True, pi_min=500, pi_max=10000):

        scw=self.workdir

        rate_table = Table.read(scw + '/rate%s.fits'%self.instrument)

        #print('Target coordinates are ra=%.2f dec=%.2f' % (self.ra, self.dec))

        #write_region(scw + '/src.reg', self.ra, self.dec, True)


        if make_plot:
            f, axes = plt.subplots(1, 2)
            axes[0].errorbar(rate_table['TIME'], rate_table['RATE'], yerr=rate_table['ERROR'], linestyle='none')
            axes[0].set_title(self.target + ' ' + self.obs_id)
            axes[0].set_xlabel('Time [s]')
            n_hist, edges, patches = axes[1].hist(rate_table['RATE'], bins=100, normed=1, facecolor='green', alpha=0.75)
        # x=(edges[0:-2]+edges[1:])/2

        ind = rate_table['RATE'] <= np.quantile(rate_table['RATE'], quantile)
        (mu, sigma) = norm.fit(rate_table['RATE'][ind])

        y = norm.pdf(edges, mu, sigma)

        fap = np.min([1. / len(rate_table), 1e-3])

        limit = np.max([typical_level, norm.isf(fap, loc=mu, scale=sigma)])

        print("For %e FAR, we use a limit of %.3f cts/s" % (fap, limit))

        if make_plot:
            _ = axes[1].plot(edges, y, 'r--', linewidth=2)
            _ = axes[1].axvline(limit, 0, 1, color='cyan')
            _ = axes[0].axhline(limit, 0, 1, color='cyan')
            plt.savefig(scw + '/%s_rate_select_%s.pdf'%(scw,self.instrument) )

        if apply_rate_filter:
            gti_filter_expression = 'RATE < %.3f' % (limit)
            gti_sas_command = "tabgtigen table=ratePN.fits expression='%s' gtiset=%sgti.fits\n"%(gti_filter_expression,
                                                                                                 self.instrument)


        #This is specialized in each derived class. it cannot be used from this level (I hope)
        ev_filter_expression=self.ev_filter_expression_base%(tmin,tmax)
        print(ev_filter_expression)

        if apply_rate_filter:
            ev_filter_expression+=' && gti(PNgti.fits,TIME)'

        sas_command = "evselect table=%s.fits withfilteredset=Y filteredset=%sclean.fits destruct=Y "%(self.instrument, self.instrument) + \
                       "keepfilteroutput=T expression='%s' updateexposure=yes filterexposure=yes\n"%(ev_filter_expression)
        sas_command += "cp %sclean.fits %sbary_clean.fits\n"%(self.instrument,self.instrument )
        sas_command += "barycen table='%sbary_clean.fits:EVENTS' timecolumn=TIME withsrccoordinates=yes srcra=%f srcdec=%f\n" % (
            self.instrument,self.ra, self.dec)

        sas_command += "evselect table=%sbary_clean.fits imagebinning=binSize imageset=%simage.fits withimageset=yes "%(self.instrument
                                                                                                                        ,self.instrument) + \
                       "expression='(PI IN (%d:%d))' "%(pi_min,pi_max) + \
                       "xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80\n"

        sas_command += self.sas_command_exposure_map%('%simage.fits'%self.instrument, 'attitude.dat', self.instrument,
                                                      '%sexposure_map.fits'%self.instrument, pi_min, pi_max)

        if run_sas:

            if wrap_run(scw, '%s_filter_flares_barycen'%self.instrument, self.sas_init + gti_sas_command + sas_command) != 0:
                print("ERROR : the script %s_sas_filter_flares_barycen returned with error"%self.instrument)
                raise RuntimeError



        try:
            p_f = pf.open(scw + '/%sgti.fits'%self.instrument)
            data = p_f[1].data

            tstart = data['START']
            tstop = data['STOP']

            ontime = np.sum(tstop - tstart)

            p_f.close()

            print("The sum of GTI for %s is %.3f ks" % (self.instrument, ontime / 1e3))
        except:
            print('%s GTI file does not exist'%self.instrument)

    def filter_with(self, other_instrument, tmin=0, tmax=1e13):

        ev_filter_expression=self.ev_filter_expression_base%(tmin,tmax)
        clean_ev="evselect table=%s.fits "%self.instrument + \
            "withfilteredset=Y filteredset=%sclean.fits "%self.instrument +\
            "destruct=Y keepfilteroutput=T " +\
            "expression='%s && gti(%sgti.fits,TIME)' updateexposure=yes filterexposure=yes\n\n"%(ev_filter_expression,
                                                                                                  other_instrument.instrument)

        clean_ev+="evselect table=%sclean.fits:EVENTS "%self.instrument + \
                      "imagebinning=binSize imageset=%simage.fits "%self.instrument + \
                      "withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80\n\n"

        clean_ev += "cp %sclean.fits %sbary_clean.fits\n"%(self.instrument,self.instrument)
        clean_ev += "barycen table='%sbary_clean.fits:EVENTS' "%self.instrument
        clean_ev += "timecolumn=TIME withsrccoordinates=yes srcra=%f srcdec=%f\n" % (
            self.ra, self.dec)

        status = wrap_run(self.workdir, '%s_filter'%self.instrument, self.sas_init + clean_ev)
        if status != 0:
            print('Exit status is %d')
            raise RuntimeError

######################################################################################################################

class epicmos(xmmanalysis):

    def __init__(self, mosunit, workdir='.'):

        xmmanalysis.__init__(self, workdir)

        self.mosunit=mosunit

        self.evtstring=workdir+'/MOS%d.fits'%self.mosunit

        self.instrument='MOS%d'%mosunit

        try:
            self.target, self.obs_id, self.date_obs, self.date_end, \
            self.ra, self.dec=self.get_obs_info(self.evtstring)

        except:
            print('I run emproc chain, assuming that the directory structure is obsid/odf')

            sas_emproc ="\nemproc "


            status = wrap_run(workdir, 'emproc', self.sas_init + sas_emproc)

            if status != 0:
                print('Exit status is %d')
                raise RuntimeError
            for j in [1,2]:
                mos_events=glob(self.workdir+'/*_EMOS%d_S*Evts.ds'%j)

                #The _S ensures only scheduled exposure is taken
                #This should be generalized

                for i,mm in enumerate(mos_events):
                    if "Timing" in  mm:
                        shutil.copy(mm, "MOS%d_Timing.fits"%j)
                    else:
                        shutil.copy(mm, "MOS%d.fits"%j)

            try:
                self.target, self.obs_id, self.date_obs, self.date_end, self.ra, self.dec = self.get_obs_info(
                    self.evtstring)
            except:
                print("Unable to find the %s, aborting init"%self.evtstring)
                raise FileExistsError


        if not glob(self.workdir + '/rateMOS%d.fits' % self.mosunit):
            extract_rate = "evselect table=MOS%d.fits withrateset=Y rateset=rateMOS%d.fits " % (
                               self.mosunit, self.mosunit) + \
                           "maketimecolumn=Y timebinsize=100 makeratecolumn=Y " + \
                           "expression='#XMMEA_EM && (PI>10000) && (PATTERN==0)'"
            status = wrap_run(workdir, 'rateMOS%d' % self.mosunit, self.sas_init + extract_rate)

            if status != 0:
                print('Exit status is %d')
                raise RuntimeError



    def filter_withPN(self):

        clean_mos_pn="evselect table=MOS%d.fits "%self.mosunit + \
            "withfilteredset=Y filteredset=MOS%dclean.fits "%self.mosunit +\
            "destruct=Y keepfilteroutput=T expression='#XMMEA_EM && (PI IN (500:10000))&& gti(PNgti.fits,TIME)' updateexposure=yes filterexposure=yes\n\n"

        clean_mos_pn+="evselect table=MOS%dclean.fits:EVENTS "%self.mosunit + \
                      "imagebinning=binSize imageset=MOS%dimage.fits "%self.mosunit + \
                      "withimageset=yes xcolumn=X ycolumn=Y ximagebinsize=80 yimagebinsize=80\n\n"

        clean_mos_pn += "cp MOS%dclean.fits MOS%dbary_clean.fits\n"%(self.mosunit,self.mosunit)
        clean_mos_pn += "barycen table='MOS%dbary_clean.fits:EVENTS' "%self.mosunit
        clean_mos_pn += "timecolumn=TIME withsrccoordinates=yes srcra=%f srcdec=%f\n" % (
            self.ra, self.dec)

        status = wrap_run(self.workdir, 'mos%d_filter'%self.mosunit, self.sas_init + clean_mos_pn)
        if status != 0:
            print('Exit status is %d')
            raise RuntimeError

    sas_commands_spec_src_mos = '''

    evselect table=MOS%dbary_clean.fits withspectrumset=yes spectrumset=MOS%dsource_%s.fits  \
        energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 \
        expression="#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN circle($x_src,$y_src,$r_src)) && (TIME in (%.2f:%.2f) )"

    backscale spectrumset=MOS%dsource_%s.fits badpixlocation=MOS%dbary_clean.fits
    '''

    sas_commands_spec_src_mos_annulus = '''

        evselect table=MOS%dbary_clean.fits withspectrumset=yes spectrumset=MOS%dsource_%s.fits  \
            energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 \
            expression="#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN ANNULUS($x_src,$y_src,%d,$r_src)) && (TIME in (%.2f:%.2f) )"

        backscale spectrumset=MOS%dsource_%s.fits badpixlocation=MOS%dbary_clean.fits
        '''

    sas_commands_spec_back_mos = '''
    evselect table=MOS%dbary_clean.fits withspectrumset=yes spectrumset=MOS%dbackground_%s.fits  \
        energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 \
        expression="#XMMEA_EM && (PATTERN<=12)&& ((X,Y) IN circle($x_bkg,$y_bkg,$r_bkg)) && (TIME in (%.2f:%.2f) )"

    backscale spectrumset=MOS%dbackground_%s.fits badpixlocation=MOS%dbary_clean.fits
    '''

    sas_commands_rsp_mos = '''

    rmfgen withenergybins=yes energymin=0.1 energymax=12.0 nenergybins=2400 spectrumset=MOS%dsource_%s.fits rmfset=MOS%d_%s.rmf

    arfgen spectrumset=MOS%dsource_%s.fits arfset=MOS%d_%s.arf withrmfset=yes rmfset=MOS%d_%s.rmf \
        badpixlocation=MOS%dbary_clean.fits detmaptype=psf


    #optimal_binning.py MOS%dsource_%s.fits -b MOS%dbackground_%s.fits -r MOS%d_%s.rmf -a MOS%d_%s.arf -e 0.5 -E 10.0

    '''


    def sas_extract_spectrum(self, sas_source_coord, sas_back_coord, base_name='spectrum', tmin=0, tmax=1e12,
                             run_rmf=True, r_annulus=-1):

        self.print_infos()

        m=self.mosunit

        cmd_str = self.sas_init + sas_source_coord + sas_back_coord \
                  + self.sas_commands_spec_back_mos % (m,m,base_name, tmin, tmax, m, base_name,m)

        if r_annulus <=0:
            cmd_str+= self.sas_commands_spec_src_mos % (m,m,base_name, tmin, tmax, m, base_name,m)
        else:
            cmd_str += self.sas_commands_spec_src_mos_annulus % (m, m, base_name, r_annulus, tmin, tmax, m, base_name, m)

        status = wrap_run(self.workdir, '%s_%s' % (self.instrument, base_name), cmd_str)

        if status != 0:
            print("extract spectrum finished with status %d" % status)
            raise RuntimeError

        spec_name='MOS%dsource_%s.fits'%(m,base_name)
        spec_file=pf.open(spec_name)
        counts=spec_file[1].data['COUNTS']
        tot_counts=np.sum(counts)
        spec_file.close()

        print('Total number of counts in %s is %d'%(spec_name,tot_counts))

        if run_rmf and tot_counts>0:
            cmd_str = self.sas_init + sas_source_coord + sas_back_coord
            cmd_str += self.sas_commands_rsp_mos % (m,base_name, m, base_name,
                                               m, base_name, m, base_name, m, base_name,
                                               m,
                                               m, base_name, m, base_name, m, base_name, m, base_name)
            status = wrap_run(self.workdir, '%s_resp_%s' % (self.instrument, base_name), cmd_str)

            if status != 0:
                print("extract response finished with status %d" % status)
                raise RuntimeError

            execute_binning('MOS%dsource_%s.fits'%(m,base_name), 'MOS%dbackground_%s.fits'%(m,base_name),
                            'MOS%d_%s.rmf'%(m,base_name) , 'MOS%d_%s.arf'%(m,base_name) , 0.5, 10.0)

    ev_filter_expression_base = '#XMMEA_EM && (PI IN (500:12000)) && (PATTERN<=12 ) ' + \
                                '&& (TIME IN (%.2f:%.2f))'

    sas_commands_lc_src = '''
evselect table=%sbary_clean.fits energycolumn=PI withrateset=yes rateset="%sraw_%s.fits" \
expression="#XMMEA_EM&&(PATTERN<=4) && ((X,Y) IN circle($x_src,$y_src,$r_src)) && (PI in (%d:%d))" \
timemin=%.2f timemax=%.2f timebinsize=%.2f maketimecolumn=yes makeratecolumn=yes
'''
    sas_commands_lc_back = '''
evselect table=%sclean.fits energycolumn=PI withrateset=yes rateset="%sback_%s.fits" \
expression="#XMMEA_EM&&(PATTERN<=12) && ((X,Y) IN circle($x_bkg,$y_bkg,$r_bkg)) && (PI in (%d:%d)) " \
timemin=%.2f timemax=%.2f timebinsize=%.2f maketimecolumn=yes makeratecolumn=yes
'''
    sas_commands_lccorr = '''
epiclccorr srctslist=%sraw_%s.fits eventlist=%sbary_clean.fits \
outset=%ssrc_%s.fits bkgtslist=%sback_%s.fits withbkgset=yes applyabsolutecorrections=yes 
'''

    sas_evt_extraction_cmd = '''    
evselect table=%sbary_clean.fits withfilteredset=Y \
filteredset=%ssource_events.fits destruct=Y keepfilteroutput=T \
expression="#XMMEA_EM && (PATTERN<=12) && ((X,Y) IN circle($x_src,$y_src,$r_src)) && (PI IN (500:10000))" \
updateexposure=yes filterexposure=yes
'''

#######################################################################

class epicmos_timing(epicmos):

    def filter_withPN(self):

        #We have also the timing events to filter and image

        super().filter_withPN()

        clean_mos_pn="evselect table=MOS%d_Timing.fits "%self.mosunit + \
            "withfilteredset=Y filteredset=MOS%d_Timing_clean.fits "%self.mosunit +\
            "destruct=Y keepfilteroutput=T expression='#XMMEA_EM && (PI IN (500:10000))&& gti(PNgti.fits,TIME)' updateexposure=yes filterexposure=yes\n\n"

        clean_mos_pn+="evselect table=MOS%d_Timing_clean.fits:EVENTS "%self.mosunit + \
                      "imagebinning=binSize imageset=MOS%d_Timing_image.fits "%self.mosunit + \
                      "withimageset=yes xcolumn=RAWX ycolumn=TIME ximagebinsize=1 yimagebinsize=100\n\n"

        clean_mos_pn += "cp MOS%d_Timing_clean.fits MOS%d_Timing_bary_clean.fits\n"%(self.mosunit,self.mosunit)
        clean_mos_pn += "barycen table='MOS%d_Timing_bary_clean.fits:EVENTS' "%self.mosunit
        clean_mos_pn += "timecolumn=TIME withsrccoordinates=yes srcra=%f srcdec=%f\n" % (
            self.ra, self.dec)

        status = wrap_run(self.workdir, 'mos%d_filter_timing'%self.mosunit, self.sas_init + clean_mos_pn)
        if status != 0:
            print('Exit status is %d')
            raise RuntimeError

    def sas_extract_image(self, image_name='PNimage.fits', pi_min=500, pi_max=11000, tmin=0, tmax=1e12,
                          display_image=False, expo_map_name='none', time_binning=100):

        super().sas_extract_image(image_name=image_name, pi_min=pi_min, pi_max=pi_max, tmin=tmin, tmax=tmax,
                          display_image=display_image, expo_map_name=expo_map_name)

        local_instrument=self.instrument+'_Timing_'

        local_image_name=image_name.split('.')[-2] +'_Timing.fits'

        image_command='''
evselect table=%sbary_clean.fits imagebinning=binSize imageset=%s withimageset=yes \
expression='(PI IN (%d:%d)) && (TIME IN (%.2f:%.2f))' \
withimageset=yes xcolumn=RAWX ycolumn=TIME ximagebinsize=1 yimagebinsize=%d
'''%(local_instrument, local_image_name,pi_min, pi_max, tmin, tmax, time_binning)


        if expo_map_name != 'none' and tmax - tmin < 3e5:
            image_command += '\natthkgen atthkset=att_%s withtimeranges=true timebegin=%.1f timeend=%.1f\n' % (
                image_name,
                tmin, tmax)
            image_command += self.sas_command_exposure_map % (self.instrument, image_name, 'att_' + image_name,
                                                              expo_map_name, pi_min, pi_max) + '\n'
        status = wrap_run(self.workdir, '%sextract_%s' % (local_instrument,
                                                           local_image_name.split('.')[-2]), self.sas_init + image_command)

        if status != 0:
            print("Error in extracting %s image" % local_instrument)
            raise RuntimeError

        if display_image:
            print("Not implemented")

    def sas_get_extraction_region(self, box_width=120, box_height=30,
                                  relative_x_offset=2, relative_y_offset=8,
                                  forced_width=-1,
                                  ra_target=np.nan, dec_target=np.nan, input_images=None,
                                  criterion='95', make_plots=True,
                                  critical_surface_brightness=1):
        # default
        ra = self.ra
        dec = self.dec

        # input ra and dec
        if np.isfinite(ra_target) and np.isfinite(dec_target):
            if ra_target >= 0 and ra_target <= 360 and dec_target >= -90 and dec_target <= 90:
                ra = ra_target
                dec = dec_target

        if input_images is None:
            filename = self.workdir + '/MOS%dimage.fits'%self.mosunit
            try:
                f_header = pf.open(filename)
            except:
                print("No file " + filename)
                raise FileExistsError

            filename_timing = self.workdir + '/MOS%d_Timing_image.fits' % self.mosunit
            try:
                f_header_timing = pf.open(filename_timing)
            except:
                print("No file " + filename_timing)
                raise FileExistsError

        else:
            filename = input_images[0]
            try:
                f_header = pf.open(filename)
            except:
                print("No file " + filename)
                raise FileExistsError

            filename_timing = input_images[1]
            try:
                f_header_timing = pf.open(filename_timing)
            except:
                print("No file " + filename_timing)
                raise FileExistsError

        hdu = f_header[0]
        my_wcs = WCS(hdu.header)
        image = hdu.data

        hdu_timing = f_header_timing[0]

        image_timing = hdu_timing.data


        # makes figure
        if make_plots:
            fig1,ax = plt.subplots(2,2)
            ax[0][0].imshow(image_timing+1, norm=LogNorm(), vmin=1, vmax=image_timing.max())
            ax[0][0].set_xlabel('RAWX')
            ax[0][0].set_ylabel('Time')

            #ax[1].set  subplot(projection=my_wcs)
            ax[0][1].imshow(image + 1, norm=LogNorm(), vmin=1, vmax=image.max())  # , vmin=-2.e-5, vmax=2.e-4, origin='lower')
            #ax[1].colorbar()
            ax[0][1].grid(color='white', ls='solid')
            #ax[1].set_xlabel('RA')
            #ax[1].set_ylabel('Dec')
            # overlay = ax.get_coords_overlay('physical')
            # overlay.grid(color='white', ls='dotted')
            # overlay[0].set_axislabel('X')
            # overlay[1].set_axislabel('Y')


        # Image Conversion factors
        REFXLMIN = hdu.header['REFXLMIN']
        REFXLMAX = hdu.header['REFXLMAX']

        REFYLMIN = hdu.header['REFYLMIN']
        REFYLMAX = hdu.header['REFYLMAX']

        xscale = (REFXLMAX - REFXLMIN) / image.shape[0]
        yscale = (REFYLMAX - REFYLMIN) / image.shape[0]

        f_header.close()
        f_header_timing.close()


        rawx_histo = image_timing.sum(axis=0)
        print(rawx_histo.shape)

        ind_max=np.argmax(rawx_histo[300:330])+300

        max_width=np.min([len(rawx_histo) - ind_max, ind_max])
        region_width=max_width
        all_counts=np.sum(rawx_histo)

        for i in range(max_width):
            enc_counts=np.sum(rawx_histo[ind_max-i:ind_max+i])
            #print(i,float(enc_counts)/float(all_counts)*100. , float(criterion) )
            if float(enc_counts)/float(all_counts)*100. >= float(criterion):
                region_width=i
                break

        print("region maximum and half width are ", ind_max, region_width)
        if region_width > box_width/2:
            region_width=region_width/2
            print('region half width limited to be %d'%region_width)

        if forced_width > 0:
            region_width=forced_width

        nominal_x, nominal_y = my_wcs.all_world2pix(ra, dec, 0)
        print("Image timing shape", image_timing.shape)
        # gets the scaling of physical coordinates
        scale_matrix = my_wcs.pixel_scale_matrix
        pix_region = 1.0 / 60. / scale_matrix[1, 1]
        back_x = nominal_x + relative_x_offset * pix_region
        back_y = nominal_y + relative_y_offset * pix_region

        physical_x = [ind_max - region_width, ind_max + region_width]

        physical_back_x = xscale * back_x
        physical_back_y = yscale * back_y

        if make_plots:
            ax[1][0].plot(np.arange(image_timing.shape[1]), rawx_histo)
            ax[1][0].axvline(x=ind_max, linestyle='--')
            ax[1][0].axvline(x=physical_x[0])
            ax[1][0].axvline(x=physical_x[1])
            # PLOTS THE default SRC REGION WITH 90% CONFINEMENT
            box = plt.Rectangle ( (ind_max-region_width,0), 2*region_width, image_timing.shape[0], color='red', fill=False, linestyle='--')
            ax[0][0].add_artist(box)

            # PLOTS THE defaultBACK REGION WITH 90% CONFINEMENT
            box = plt.Rectangle((back_x, back_y), box_width, box_height, color='white', fill=False)
            ax[0][1].add_artist(box)
            ax[0][1].set_title(self.target + ' ' + self.obs_id)

        # Physical coordinates


        # physical_r = pix_region * (xscale+yscale)/2.
        if make_plots:
            fig1.savefig(self.workdir+'%s_timing.png' % (filename.split('.')[-2]))

        sas_source_coord = 'rawx_min=%.1f\nrawx_max=%.1f\n' % (physical_x[0], physical_x[1])
        sas_back_coord = 'x_bkg=%.1f\ny_bkg=%.1f\nwidth_bkg=%.1f\nheight_bkg=%.1f' % (
        physical_back_x, physical_back_y, box_width*xscale,box_height*yscale)

        print("source physical coordinates\n" + sas_source_coord)
        print("background physical coordinates\n" + sas_back_coord)

        return sas_source_coord, sas_back_coord

    ev_filter_expression_base = '#XMMEA_EM && (PI IN (500:12000)) && (PATTERN<=0) && (FLAG==0) ' + \
                                '&& (TIME IN (%.2f:%.2f))'

    sas_commands_spec_src_mos = '''
evselect table=MOS%d_Timing_bary_clean.fits withspectrumset=yes spectrumset=MOS%dsource_%s.fits \
        energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 \
        expression="(FLAG==0) && (PATTERN<=0) && (RAWX>=$rawx_min) && (RAWX<=$rawx_max)  && (TIME in (%.2f:%.2f) )"
        
    
backscale spectrumset=MOS%dsource_%s.fits badpixlocation=MOS%d_Timing_bary_clean.fits
    
    '''

    sas_commands_spec_back_mos = '''
evselect table=MOS%dbary_clean.fits withspectrumset=yes spectrumset=MOS%dbackground_%s.fits \
energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=11999 \
expression="(FLAG==0) && (PATTERN<=1 || PATTERN==3) && ((X,Y) in BOX($x_bkg,$y_bkg, $width_bkg, $height_bkg,0)) && (TIME in (%.2f:%.2f) )"
    
backscale spectrumset=MOS%dbackground_%s.fits badpixlocation=MOS%dbary_clean.fits
    
    '''

    sas_commands_rsp_mos = '''
    
rmfgen withenergybins=yes energymin=0.1 energymax=12.0 nenergybins=2400 spectrumset=MOS%dsource_%s.fits rmfset=MOS%d_%s.rmf
    
arfgen spectrumset=MOS%dsource_%s.fits arfset=MOS%d_%s.arf withrmfset=yes rmfset=MOS%d_%s.rmf \
            badpixlocation=MOS%d_Timing_bary_clean.fits detmaptype=psf
    
    
#optimal_binning.py MOS%dsource_%s.fits -b MOS%dbackground_%s.fits -r MOS%d_%s.rmf -a MOS%d_%s.arf -e 0.5 -E 10.0
    '''

    sas_commands_lc_src = '''

evselect table=%s_Timing_bary_clean.fits energycolumn=PI withrateset=yes rateset="%sraw_%s.fits" \
expression="#XMMEA_EM && (FLAG==0) && (PATTERN<=0) && (RAWX>=$rawx_min) && (RAWX<=$rawx_max) && (PI in (%d:%d))" \
timemin=%.2f timemax=%.2f timebinsize=%.2f maketimecolumn=yes makeratecolumn=yes
'''
    sas_commands_lc_back = '''
evselect table=%sbary_clean.fits energycolumn=PI withrateset=yes rateset="%sback_%s.fits" \
expression="#XMMEA_EM && (FLAG==0) && (PATTERN<=1 || PATTERN==3) && ((X,Y) in BOX($x_bkg,$y_bkg, $width_bkg, $height_bkg,0)) && (PI in (%d:%d))" \
timemin=%.2f timemax=%.2f timebinsize=%.2f maketimecolumn=yes makeratecolumn=yes
    '''
    sas_commands_lccorr = '''
epiclccorr srctslist=%sraw_%s.fits eventlist=%s_Timing_bary_clean.fits applyabsolutecorrections=yes \
outset=%ssrc_%s.fits 
#bkgtslist=%sback_%s.fits withbkgset=yes
'''
    sas_evt_extraction_cmd = '''    
evselect table=%s_Timing_bary_clean.fits withfilteredset=Y \
filteredset=%ssource_events.fits destruct=Y keepfilteroutput=T \
expression="#XMMEA_EM && (FLAG==0) && (PATTERN<=0) && (RAWX>=$rawx_min) && (RAWX<=$rawx_max) && (PI IN (500:10000))" \
updateexposure=yes filterexposure=yes
'''

class epicpn(xmmanalysis):

    def __init__(self, workdir='.'):

        xmmanalysis.__init__(self, workdir)

        self.workdir=workdir

        self.instrument = 'PN'

        try:
            self.target, self.obs_id, self.date_obs, self.date_end, self.ra, self.dec=self.get_obs_info(workdir+'/PN.fits')
        except:
            print("Cannot open PN.fits")
            print('I run epproc chain, assuming that the directory structure is obsid/odf')
            status=wrap_run(self.workdir, 'epproc', self.sas_init+self.sas_epproc)
            if status != 0:
                print('Exit status is %d')
                raise RuntimeError

            try:
                self.target, self.obs_id, self.date_obs, self.date_end, self.ra, self.dec = self.get_obs_info(workdir + '/PN.fits')
            except:
                print ("Unable to find the PN.fits, aborting init")
                raise FileExistsError


    def rerun_epproc_pileup(self):

        pileup_epproc='\nepproc pileuptempfile=yes runepxrlcorr=yes\n'
        pileup_epproc+='cp `ls *EPN*ImagingEvts.ds` PN.fits'
        status = wrap_run(self.workdir, 'epproc_pileup', self.sas_init + pileup_epproc)
        if status != 0:
            print('Exit status is %d')
            raise RuntimeError


    def sas_cr_filter_image(self, typical_level=0.5, quantile=0.7, run_sas=False, make_plot=True,
                            tmin=0,tmax=1e12,apply_rate_filter=True,
                            pi_min=1000, pi_max=9000):

        self.sas_cr_filter(typical_level=typical_level, quantile=quantile, run_sas=run_sas, make_plot=make_plot,
                             tmin=tmin,tmax=tmax,apply_rate_filter=apply_rate_filter)

        self.sas_extract_image(image_name='%simage.fits'%self.instrument, pi_min=pi_min, pi_max=pi_max,
                               tmin=tmin,tmax=tmax, expo_map_name='%sexposure_map.fits'%self.instrument )


    ev_filter_expression_base = '#XMMEA_EP && (PI IN (500:12000)) && (PATTERN>=0) && (PATTERN<=4) ' + \
                                '&& (TIME IN (%.2f:%.2f))'

    sas_commands_spec_src = '''
evselect table=PNbary_clean.fits withspectrumset=yes spectrumset=PNsource_%s.fits  \
energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 \
expression="#XMMEA_EP&&(PATTERN<=4)&& ((X,Y) IN circle($x_src,$y_src,$r_src)) && (TIME in (%.2f:%.2f) )"

backscale spectrumset=PNsource_%s.fits badpixlocation=PNbary_clean.fits

    '''
    sas_commands_spec_src_annulus = '''
evselect table=PNbary_clean.fits withspectrumset=yes spectrumset=PNsource_%s.fits  \
energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 \
expression="#XMMEA_EP&&(PATTERN<=4)&& ((X,Y) IN ANNULUS($x_src,$y_src,%d,$r_src)) && (TIME in (%.2f:%.2f) )"

backscale spectrumset=PNsource_%s.fits badpixlocation=PNbary_clean.fits

        '''

    sas_commands_spec_back = '''
evselect table=PNbary_clean.fits withspectrumset=yes spectrumset=PNbackground_%s.fits  \
energycolumn=PI spectralbinsize=5 withspecranges=yes specchannelmin=0 specchannelmax=20479 \
expression="#XMMEA_EP&&(PATTERN<=4)&& ((X,Y) IN circle($x_bkg,$y_bkg,$r_bkg)) && (TIME in (%.2f:%.2f) )"

backscale spectrumset=PNbackground_%s.fits badpixlocation=PNbary_clean.fits

'''

    sas_commands_rsp = '''

rmfgen spectrumset=PNsource_%s.fits rmfset=PN_%s.rmf

arfgen spectrumset=PNsource_%s.fits arfset=PN_%s.arf withrmfset=yes rmfset=PN_%s.rmf \
badpixlocation=PNbary_clean.fits detmaptype=psf

#optimal_binning.py PNsource_%s.fits -b PNbackground_%s.fits -r PN_%s.rmf -a PN_%s.arf -e 0.5 -E 10.5

'''

    sas_evt_extraction_cmd = '''
evselect table=%sbary_clean.fits withfilteredset=Y \
filteredset=%ssource_events.fits destruct=Y keepfilteroutput=T \
expression="#XMMEA_EP && (PATTERN<=4)&& ((X,Y) IN circle($x_src,$y_src,$r_src)) && (PI IN (500:12000))" \
updateexposure=yes filterexposure=yes
'''

    sas_commands_lc_src = '''
evselect table=%sbary_clean.fits energycolumn=PI withrateset=yes rateset="%sraw_%s.fits" \
expression="#XMMEA_EP && (PATTERN<=4) && ((X,Y) IN circle($x_src,$y_src,$r_src)) && (PI in (%d:%d))" \
timemin=%.2f timemax=%.2f timebinsize=%.2f maketimecolumn=yes makeratecolumn=yes
    '''
    sas_commands_lc_back = '''
evselect table=%sclean.fits energycolumn=PI withrateset=yes rateset="%sback_%s.fits" \
expression="#XMMEA_EP && (PATTERN<=4) && ((X,Y) IN circle($x_bkg,$y_bkg,$r_bkg)) && (PI in (%d:%d)) " \
timemin=%.2f timemax=%.2f timebinsize=%.2f maketimecolumn=yes makeratecolumn=yes
    '''
    sas_commands_lccorr = '''
epiclccorr srctslist=%sraw_%s.fits eventlist=%sbary_clean.fits \
outset=%ssrc_%s.fits bkgtslist=%sback_%s.fits withbkgset=yes applyabsolutecorrections=yes 
    '''


    def sas_extract_spectrum(self, sas_source_coord, sas_back_coord, base_name='spectrum', tmin=0,tmax=1e12, run_rmf=True, correct_pileup=False, r_annulus=-1):

        self.print_infos()

        cmd_str=self.sas_init + sas_source_coord + sas_back_coord \
                        + self.sas_commands_spec_back%(base_name,tmin,tmax,base_name)

        if r_annulus <= 0:
            cmd_str+= self.sas_commands_spec_src%(base_name,tmin,tmax,base_name)
        else:
            cmd_str += self.sas_commands_spec_src_annulus % (base_name, r_annulus, tmin, tmax, base_name)


        if run_rmf:
            cmd_str+=self.sas_commands_rsp%(base_name,base_name,base_name,base_name,base_name,
                                         base_name,base_name,base_name,base_name)




        status=wrap_run(self.workdir, 'PN_%s'%base_name,cmd_str)

        if run_rmf:
            execute_binning('PNsource_%s.fits' % base_name, 'PNbackground_%s.fits' % base_name, 'PN_%s.rmf' % base_name,
                            'PN_%s.arf' % base_name, 0.5, 10.5)

        if status!=0:
            print("PN extract spectrum finished with status %d"%status)
            raise RuntimeError

        if correct_pileup and r_annulus <= 0:
            evt_file_name = "%ssource_events.fits"%(self.instrument)

            evt_file=pf.open(evt_file_name)
            ccd_nr_evt=evt_file[1].data['CCDNR']
            ccd_nr= int(np.floor(np.mean(ccd_nr_evt)))
            evt_file.close()
            search_str="*%02d_PileupEvts.ds"%ccd_nr

            ccd_evt_file=os.path.basename(glob(self.workdir+'/'+search_str)[0])

            print('Selected event file %s'%ccd_evt_file)

            sas_command = self.sas_init + sas_source_coord
            sas_command += '\nrmfgen spectrumset=PNsource_%s.fits rmfset=PN_pileup_%s.rmf correctforpileup=yes raweventfile=%s\n'%(base_name,base_name,ccd_evt_file)
            #sas_command += '\noptimal_binning.py PNsource_%s.fits -b PNbackground_%s.fits -r PN_pileup_%s.rmf -a PN_%s.arf -e 0.5 -E 10.5\n'%(base_name,base_name,base_name,base_name)

            status = wrap_run(self.workdir, 'PN_pileup_%s' % base_name, sas_command)

            if status != 0:
                print("PN extract rm for pileup finished with status %d" % status)
                raise RuntimeError

            execute_binning('PNsource_%s.fits' % base_name, 'PNbackground_%s.fits' % base_name, 'PN_pileup_%s.rmf' % base_name,
                            'PN_%s.arf' % base_name, 0.5, 10.5)

    def sas_average_products(self, run_sas=False, min_psf=3, max_psf=30, default_psf=1.0,
                             relative_x_offset=-2, relative_y_offset=+2,
                             forced_r_pix=-1, run_xspec=False, use_max_coord=False,
                             ra_target=np.nan, dec_target=np.nan, criterion='s_n'):
        # Default psf is in arcminutes and is about the 90% confinement for PN by default
        # see https://heasarc.nasa.gov/docs/xmm/uhb/onaxisxraypsf.html
        # By default, it takes the target coordnates
        # if use_max_coord=True, it uses the maximum of the image
        # if ra_target and dec_target are defined, it uses these coordinates, unless use_max_coord=True


        # ra=self.ra
        # dec=self.dec
        #
        # # input ra and dec
        # if np.isfinite(ra_target) and np.isfinite(dec_target):
        #     if ra_target >= 0 and ra_target <= 360 and dec_target >= -90 and dec_target <= 90:
        #         ra = ra_target
        #         dec = dec_target
        #
        # filename = get_pkg_data_filename(self.workdir + '/PNimage.img')

        self.print_infos()

        sas_source_coord, sas_back_coord=self.sas_get_extraction_region(min_psf, max_psf, default_psf,
                             relative_x_offset, relative_y_offset,
                             forced_r_pix, use_max_coord,
                             ra_target, dec_target, criterion=criterion)

        if run_sas:
            wrap_run(self.workdir, 'sas_average_products',
                     self.sas_init + sas_source_coord + sas_back_coord + self.sas_commands_av_src + self.sas_commands_av_back
                     + self.sas_command_lc_corr
                     + sas_commands_av_rsp)
        if run_xspec:
            cwd = os.getcwd()
            os.chdir(self.workdir)
            xspec.AllData.clear()

            time_stamp = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
            Xspec_logFile = xspec.Xset.openLog("xspec_log_%s.txt" % (time_stamp))

            xspec.Fit.statMethod = "cstat"
            xspec.Xset.abund = 'wilm'

            spec_file_name = "PNsource_spectrum_rbn.pi"
            print(spec_file_name)
            s = xspec.Spectrum(spec_file_name)
            ig = "**-0.5,10.5-**"
            s.ignore(ig)
            xspec.AllData.ignore('bad')
            m = xspec.Model("TBabs*pegpwrlw")
            m.pegpwrlw.PhoIndex = 1
            m.pegpwrlw.eMin = 1.0
            m.pegpwrlw.eMax = 10.0
            m.pegpwrlw.norm = 100.0
            m.TBabs.nH = 3.

            xspec.Fit.perform()
            # xspec.Fit.error('2.7 1,2,5')
            xspec.Fit.error('2.7 1-5')
            xspec.AllModels.calcFlux("1.0 10.0")

            print("NH = ", m.TBabs.nH.values[0])
            print("PhoIndex=", m.pegpwrlw.PhoIndex.values[0])
            print("The power-law unabsorbed flux is ", m.pegpwrlw.norm.values[0],
                  ' 1e-12 erg/s/cm^2 in %.1f-%.1f keV' % (m.pegpwrlw.eMin, m.pegpwrlw.eMax))
            print("Normalized fit statistics ", xspec.Fit.statistic / xspec.Fit.dof)
            print('Model flux is ', s.flux[0], ' erg/s/cm^2')

            # spec_file_name="PNsource_spectrum_rbn.pi"
            spec_file = pf.open(spec_file_name)
            exposure = spec_file[1].header['EXPOSURE']
            counts = spec_file[1].data['COUNTS'].sum()
            rate = counts / exposure
            spec_file.close()

            print("Exposure = %.1f s Rate=%.3f cts/s" % (exposure, rate))

            fn = "spec.png"
            xspec.Plot.device = fn + "/png"
            # xspec.Plot.addCommand("setplot en")
            xspec.Plot.xAxis = "keV"
            xspec.Plot("ldata del")
            xspec.Plot.device = fn + "/png"
            xspec.Xset.closeLog()

            shutil.move(fn + "_2", fn)

            _ = display(Image(filename=fn, format="png"))
            os.chdir(cwd)
            # break
            # tstart=spec_file[0].header['TSTART']
            # tstop=spec_file[0].header['TSTOP']

        #return r_psf, c_net





