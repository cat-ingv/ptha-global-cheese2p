###### functions used for hazard calculation 
import os
import numpy as np
import matplotlib.pyplot as plt


def calculate_hazard_curve(mih_thresholds, h_max_lst, exc_rates, poi, output_path, plot):
    '''
    '''
    
    h_max_lst = np.transpose(h_max_lst)
    mask_exceed = h_max_lst[:, None] >= mih_thresholds[None, :]
    weighted_exceed = mask_exceed * exc_rates[:, None]
    hc = np.sum(weighted_exceed, axis=0)
    # save hazard curve results
    np.savetxt(os.path.join(output_path, 'hc_mean_rate_' + poi + '.txt'), np.c_[hc])
    
    if plot:
        plot_hazard_curve(mih_thresholds, hc, poi, output_path)

    return hc 


def plot_hazard_curve(mih_thresholds, hc, poi, output_path):
    '''
    plot hazard
    '''

    plt.plot(mih_thresholds, hc,'--m', label='',linewidth=2)
    plt.xlabel('Tsunami Maximum Amplitude (m)', fontsize=14, labelpad=10)
    plt.ylabel('Mean Annual Rate of Exceedance', fontsize=14, labelpad=10)
    plt.yscale('log')
    plt.xscale('log')
    plt.ylim(10e-6, 1)
    plt.grid()
    plt.title(poi)
    # plt.legend(fontsize=12, loc="best", frameon=True)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()

    filename = os.path.join(output_path, 'hc_mean_rate_' + poi + '.png')
    plt.savefig(filename, format='png', dpi=300, bbox_inches='tight')
    return



