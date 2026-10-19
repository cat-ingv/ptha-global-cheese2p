# here there is a list with all the needed function to perform wf reconstruction from preprocessing files 
# and then linear combination

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
#import netCDF4
import re
import pandas as pd
# read post-processing


def greens_functions_db(poi_idx, gf_path, subduction, n_subfaults, n_timesteps):


    gf_subfaults_path = os.path.join(gf_path, subduction, 'GF2')
    gf_subfaults = [f for f in os.listdir(gf_subfaults_path) if not f.startswith('slip')]
    
    # pattern = r"GF2/slip_taper_geo_(\d+)_hysea"
    # print(pattern)
    # ############# get this parameters from pkls     
    # subdirs = sorted(
    # [d for d in os.listdir(gf_path) if os.path.isdir(os.path.join(gf_path, d))],
    # key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf')
    # )
    # print(subdirs)

    big_eta = np.zeros((n_subfaults, n_timesteps+1), dtype=object)

    # for ii, subdir in enumerate(subdirs):
    for i in range(n_subfaults):

        isb = str(i+1).zfill(3)

        full_path = os.path.join(gf_path, gf_subfaults_path, 'slip_taper_geo_' + isb + '_hysea')
        
        if os.path.isdir(full_path):
            # str_tmp = f"{(m := re.search(pattern, full_path)).group(1)}_{m.group(2)}"
            str_tmp = subduction + '_' + isb
            big_eta[i, 0] = str_tmp
            file_path = os.path.join(full_path, 'out_ts_new_th.pkl')

            if os.path.isfile(file_path):
                 
                with open(file_path, 'rb') as handle:
                    sample_pickle = pickle.load(handle)

                valid_id = sample_pickle['valid_ids']
                mask = np.isin(poi_idx, valid_id)

                if mask == True:
                    crop_time_name = 'crop_time_' + str(poi_idx)
                    crop_time = sample_pickle[crop_time_name]
                    eta_crop = sample_pickle[poi_idx]
                    lec = len(eta_crop)
                    big_eta[i,-lec:] = (eta_crop)

                  
    row_sums = np.sum(big_eta[:, 1:], axis=1)  # shape (17000,)
    mask = row_sums != 0
    big_eta_redux = big_eta[mask, :]
    n_redux, _ = big_eta_redux.shape
    n_removed = n_subfaults - n_redux
    # name_matricione='GF_db/gf_matrix_'+str(my_name_poi)+'.npy'
    # np.save(name_matricione,big_eta3)
    # print(f'N. of removed subfaults with no contribution: {n_removed}/{n_subfaults}')
    print(np.amax(big_eta_redux[:,1:1000]))
    return big_eta_redux
              
                

def calculate_linear_combinations(gf_gb_file, all_ruptures, area_subf, dep_poi, nom_d, output_path, plot, save):
    
    str_eta = gf_gb_file[:,0]

    all_rup_snr_subf = all_ruptures['eve_ids'].values
    all_rup_rates = all_ruptures['annual_rate'].values
    all_rup_snr_str = all_ruptures['scenario'].values  # earthquake scenario name 
    all_rup_snr_area = all_ruptures['area'].values
    all_rup_snr_slip = all_ruptures['slip'].values

    h_max_lst = np.zeros(len(all_rup_snr_subf))
    h_max_lst2 = np.zeros(len(all_rup_snr_subf))
    
    area_mesh = []
    area_oq = []
    
    gl = (abs(dep_poi)/nom_d)**0.25

    for ii, name_rup in enumerate(all_rup_snr_str):
        str_rup_splt = name_rup.split('_')
        subd_rup_name = str_rup_splt[0]
        subf_rup_id = all_rup_snr_subf[ii]

        ## linear combination taking the id of eq scenario (1 or more)    
        ts_combined = None
        for jj in subf_rup_id:
            compl_name = subd_rup_name + '_' + f"{jj:03d}" # complete name to search subfault in gf npy bd
            exst_condition = np.where(str_eta == compl_name)
            
            if exst_condition[0].size > 0:

                my_idx = exst_condition[0]
                my_ts = gf_gb_file[my_idx,1:]
                my_ts_ok = my_ts[0]
                single_area = area_subf[jj-1] 

                if ts_combined is None:
                    ts_combined = np.copy(my_ts_ok)

                else:
                    ts_combined += my_ts_ok
                     

        area_tot_mesh = sum(area_subf[c-1] for c in subf_rup_id)
        area_mesh.append(area_tot_mesh)              
            
        exp_slip = all_rup_snr_slip[ii]
        scaled_slip_tmp = ((exp_slip*all_rup_snr_area[ii])/(area_tot_mesh))/10
 
    
        if ts_combined is not None:
            h_max_lst[ii] = max(ts_combined*scaled_slip_tmp*gl)  
            h_max_lst2[ii] = max(ts_combined)  

    if save:
        # saving areas
        save_areas(area_mesh, output_path)

    if plot:
        plot_area_comparison(area_mesh, all_rup_snr_area, output_path)

    return h_max_lst, h_max_lst2
            
            
def plot_area_comparison(area_mesh, all_rup_snr_area, output_path):
    '''
    '''
    plt.plot(area_mesh,'o', label='mesh subfaults')         
    plt.plot(all_rup_snr_area,'o', label='actual ruptures', alpha=0.5)
    plt.legend()
    plt.grid()
    plt.xlabel(f'Scenarios count')
    plt.ylabel(f'Area (m$^2$)')
    filename = os.path.join(output_path, 'areas_ruptures.png')
    plt.savefig(filename, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    return    


def save_areas(area_mesh, output_path):
    '''
    '''
    data = {
        "area_rup_from_mesh": area_mesh,
    }
    rup_df = pd.DataFrame(data)
    rup_df.to_csv(os.path.join(output_path, 'area_rup_from_mesh_file.csv'))
    return
