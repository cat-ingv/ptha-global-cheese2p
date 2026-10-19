####################### this code is able to run the entire workflow chain ###########
import os
import sys
import argparse
import pickle
import ast
#import netCDF4
import numpy as np
import pandas as pd

import pygptha.utilities
import pygptha.linear_combinations as pygptha_lc
import pygptha.hazard_curves as pygptha_hc


# Arguments of the script
parser = argparse.ArgumentParser(description='Script and input.')
parser.add_argument('--oq', action='store_true', help='activate openquake usage to define ruptures')
parser.add_argument('--save', action='store_true', help='save intermediate results')
parser.add_argument('--plot', action='store_true', help='activate the creation of automatic figures')
parser.add_argument('--subd', type=str, help='please, put subduction name', required=True)
parser.add_argument('--poi', type=str, help='please, put the poi id', required=True)
parser.add_argument('--input_path', type=str, help='please, put the path of your input folder', required=True)
parser.add_argument('--output_path', type=str, help='please, put the path of your output folder', required=True)
parser.add_argument('--gf_path', type=str, help='please, put the path of your greens function local folder', required=True)

args = parser.parse_args()

# get arguments
oq = args.oq
save = args.save
subd = args.subd
poi = args.poi
input_path = args.input_path
output_path = args.output_path
gf_path = args.gf_path
plot = args.plot

# these variable should be moved in a separate input file or in argparse
fmd_file = os.path.join(input_path, 'frequency_magnitude_distribution.npy')
pois_file = os.path.join(input_path, 'POI_lon_lat_ID_depth.txt')
mih_thresholds_file = os.path.join(input_path, 'mih_thresholds.npy')
ruptures_list_file = os.path.join(input_path, 'list_eq_scenario_kurilsjapan.csv')
n_timesteps = 17281

# get pois index and coordinates
poi_idx, poi_lon, poi_lat, poi_dep = pygptha.utilities.get_idx_poi(poi, pois_file)
print(f'poi name: {poi}, lon: {poi_lon}, lat: {poi_lat}, index: {poi_idx}', 'depth=', poi_dep)

# reading the meshes
# WARNING now it works for ONE subduction only
subd_surf, info_mesh = pygptha.utilities.read_mesh(subd, input_path)
n_subfaults =  int(info_mesh[0])
n_strike = int(info_mesh[1])        # n. of subfaults along strike
n_dip = int(info_mesh[2])           # n. of subfaults along dip

if plot:
    #pass
    pygptha.utilities.plot_poi_and_sources_on_map(poi, poi_lon, poi_lat, subd_surf, output_path)

# Creation of the earthquakes ruptures' list
if oq:
    # with OpenQuake

    # importing the module with openquake functions
    import pygptha.openquake_interface as pygptha_oq

    # fmd definition
    fmd = pygptha_oq.fmd(fmd_file, output_path, plot)

    # edge creation
    mesh_ids, mesh_subd, area_subf, lines = pygptha_oq.define_mesh_edges(subd_surf, n_strike, n_dip, output_path, subd, plot, save)

    # oq source creation    NB!!!!! WE HAVE TO UPDATE OQ
    oq_src = pygptha_oq.define_source(fmd, lines)

    # creation of ruptures' list 
    rup_lst = pygptha_oq.ruptures_lists(oq_src, subd, mesh_subd, mesh_ids, output_path, save)

    # rates 
    rates = rup_lst['annual_rate'].values
    print(f'n. of ruptures: {oq_src.count_ruptures()} - n. of rates: {len(rates)}')

else:
    # from external files (without OpenQuake)

    # with open(os.path.join(input_path, 'list_eq_scenario_kurilsjapan.pkl'), 'rb') as f:
    #     rup_lst = pickle.load(f)
    rup_lst = pd.read_csv(ruptures_list_file, index_col=0)
    rup_lst['eve_ids'] = [ast.literal_eval(item) for item in rup_lst['eve_ids'].values]
    rates = rup_lst['annual_rate'].values
    # area_subf = rup_lst['area'].values
    area_subf_file = os.path.join(input_path, 'list_area_subfaults_' + subd + '.csv')
    area_subf = np.loadtxt(area_subf_file)



# GF Linear Combination
nom_d = 1.
gf_db_poi = pygptha_lc.greens_functions_db(poi_idx, gf_path, subd, n_subfaults, n_timesteps)

lin_comb_hmax_sc, lin_comb_hmax_not_sc = pygptha_lc.calculate_linear_combinations(gf_db_poi, rup_lst, area_subf, poi_dep, nom_d, output_path, plot, save)

# Hazard Calculation

# loading mih thresholds
mih_thresholds = np.load(mih_thresholds_file, allow_pickle=True)
# print(f'mih thresholds: , {mih_thresholds}')

hc = pygptha_hc.calculate_hazard_curve(mih_thresholds, lin_comb_hmax_sc, rates, poi, output_path, plot)

