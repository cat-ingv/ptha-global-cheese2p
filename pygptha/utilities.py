import os
import numpy as np
import pandas as pd
import shapely
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def get_idx_poi(poi_id, pois_file):
    """
    recover idx lon lat from poi id

    poi_id: the poi name (string)
    idx_poi: poi index (integer) 
    lon_poi: poi longitude (float) 
    lat_poi: poi latitude (float) 
    
    """     
    poi_id_file = pd.read_csv(pois_file,
                              sep = r"\s+",
                              header = None,
                              names = ['lon', 'lat', 'id', 'depth'])

    id_lst = poi_id_file['id'].values
    lon_poi_all = poi_id_file['lon'].values
    lat_poi_all = poi_id_file['lat'].values
    depth_poi_all=poi_id_file['depth'].values
    idx_poi = np.where(id_lst==poi_id)[0][0] # check if there a more elegant way to do it
    lon_poi = lon_poi_all[idx_poi]
    lat_poi = lat_poi_all[idx_poi]
    dep_poi= depth_poi_all[idx_poi]
    idx_poi = idx_poi + 1 # correction to be coherent with the counter in the csv file

    return idx_poi, lon_poi, lat_poi, dep_poi


def read_mesh(subd_name, input_path):
    """

    reading quadrilateral mesh
    each line contains the coordinates of the four corners of each subfault
    with the following convention:

    x1 y1 z1 x2 y2 z3 x3 y3 z3 x4 y4 z4

    
     ---- x4y4z4 ---- x3y3z3
            |           |
            |           |
     ---- x1y1z1 ---- x2y2z2
            |           |
            |           |

    subfaults are ordered by strike and then by dip

    """
    
    # subduction path 
    subd_surf = np.loadtxt(os.path.join(input_path, subd_name + '_quadrilateral_coors.dat'))
    info_mesh = np.loadtxt(os.path.join(input_path, subd_name + '_Ntot_Nstrike_Ndip.dat'))

    return subd_surf, info_mesh


def plot_poi_and_sources_on_map(poi, poi_lon, poi_lat, mesh, output_path):
    '''
    '''
    #from mpl_toolkits.basemap import Basemap
    proj = ccrs.PlateCarree(central_longitude=180)
    fig = plt.figure(figsize=(14, 8))

    ax_map = fig.add_subplot(1, 1, 1, projection=proj)
    ax_map.set_global()
    ax_map.coastlines()
    ax_map.gridlines(draw_labels=True)

    for i in range(len(mesh)):
        p = shapely.geometry.Polygon([(mesh[i,0], mesh[i,1]), 
                                      (mesh[i,3], mesh[i,4]), 
                                      (mesh[i,6], mesh[i,7]), 
                                      (mesh[i,9], mesh[i,10])])
        x, y = p.exterior.xy
        line, = plt.plot(x, y, color='#336699', linewidth=1, transform=ccrs.PlateCarree())
        if i == 0:
            line.set_label('kurils-japan')


    ax_map.plot(poi_lon, poi_lat, marker='^', color='r', markersize=10,
                transform=ccrs.PlateCarree())

    ax_map.text(poi_lon, poi_lat, poi, color='#000000', fontsize=14,
                transform=ccrs.PlateCarree())

    #ax_map.set_title(poi)

    # ax_curve = fig.add_subplot(1, 2, 2)
    # plt.legend()
    filename = os.path.join(output_path, poi + '_sources_map.png')
    plt.savefig(filename, format='png', dpi=300, bbox_inches='tight')
    return


