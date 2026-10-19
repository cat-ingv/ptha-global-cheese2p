import os 
import sys

import numpy as np
import pandas as pd
from shapely.geometry import Polygon

# import netCDF4
# from pyproj import Proj, Transformer
import matplotlib.pyplot as plt

##### OQ libraries ######################
from openquake.hazardlib.source import ComplexFaultSource
from openquake.hazardlib.geo import Point
from openquake.hazardlib.mfd import ArbitraryMFD
from openquake.hazardlib.scalerel.strasser2010 import StrasserInterface
from openquake.hazardlib.tom import PoissonTOM
from openquake.hazardlib.geo.line import Line
from openquake.hazardlib.geo.surface.complex_fault import ComplexFaultSurface


def define_mesh_edges(subd_surf, n_strike, n_dip, output_path, subduction, plot, save):
    """

    """
    
    # Vertices 
    x1 = subd_surf[:,0]
    y1 = subd_surf[:,1]

    x2 = subd_surf[:,3]
    y2 = subd_surf[:,4]

    x3 = subd_surf[:,6]
    y3 = subd_surf[:,7]

    x4 = subd_surf[:,9]
    y4 = subd_surf[:,10]

    z1 = (abs(subd_surf[:,2])/1000)
    z2 = (abs(subd_surf[:,5])/1000)
    z3 = (abs(subd_surf[:,8])/1000)
    z4 = (abs(subd_surf[:,11])/1000)

    mesh_subd = []
    areas = [] 

    for i in np.arange(len(x1)):

        mesh_rect = Polygon([(x1[i], y1[i]), (x2[i], y2[i]), (x3[i], y3[i]), (x4[i], y4[i])])
        mesh_subd.append(mesh_rect)
        
        top_edg = []
        bot_edg = []
        top_edg1 = np.array([x1[i], y1[i], z1[i]])
        top_edg2 = np.array([x4[i], y4[i], z4[i]])
    
        top_edg.append(top_edg1)
        top_edg.append(top_edg2)
        top_edg = np.array(top_edg)
        bot_edg1 = np.array([x2[i], y2[i], z2[i]])
        bot_edg2 = np.array([x3[i], y3[i], z3[i]])

        bot_edg.append(bot_edg1)
        bot_edg.append(bot_edg2)
        bot_edg = np.array(bot_edg)
        points = []
        for coo in top_edg:
           points.append((Point(coo[0], coo[1], coo[2])))

        top_line = Line(points)  

        points = []
        for coo in bot_edg:
            points.append((Point(coo[0], coo[1], coo[2])))            
        
        bot_line = Line(points)

        # Lines
        list_lines = [top_line, bot_line]
        whole_subf_surface = ComplexFaultSurface.from_fault_data(list_lines, 50)
        subf_area = whole_subf_surface.get_area()
        areas.append(subf_area)
        ### area calculation

    if save:
        np.savetxt(os.path.join(output_path, 'list_area_subfaults_' + subduction + '.csv'), np.array(areas).transpose(), fmt='%.6f')

    mesh_ids = list(range(1, len(mesh_subd) + 1))
    

    ###### OpenQuake Edge Creation ################################################

    n_edges = n_dip + 1

    all_edges = []

    # edge_1_x = x2[0:step-1]
    # edge_1_y = y2[0:step-1]
    # edge_1_z = z2[0:step-1]
    
    # creating empty edge
    edge_1_x = np.zeros((n_strike+1))
    edge_1_y = np.zeros((n_strike+1))
    edge_1_z = np.zeros((n_strike+1))

    # filling the first edge
    edge_1_x[1:n_strike+1] = x2[0:n_strike]
    edge_1_y[1:n_strike+1] = y2[0:n_strike]
    edge_1_z[1:n_strike+1] = z2[0:n_strike]
    
    # adding corner top-right 
    edge_1_x[0] = x3[0]
    edge_1_y[0] = y3[0]
    edge_1_z[0] = z3[0]

    all_edges.append([edge_1_x, edge_1_y, edge_1_z])

    lim1 = 0
    for kk in range(n_edges-1):
        # lim2 = lim1 + n_strike -1
        lim2 = lim1 + n_strike
        # print(kk, lim1, lim2, n_strike)
    
        # edge_1_x = x1[lim1:lim2]
        # edge_1_y = y1[lim1:lim2]
        # edge_1_z = z1[lim1:lim2]
    
        edge_1_x = np.zeros((n_strike+1))
        edge_1_y = np.zeros((n_strike+1))
        edge_1_z = np.zeros((n_strike+1))

        edge_1_x[1:n_strike+1] = x1[lim1:lim2]
        edge_1_y[1:n_strike+1] = y1[lim1:lim2]
        edge_1_z[1:n_strike+1] = z1[lim1:lim2]

        edge_1_x[0] = x4[lim1]
        edge_1_y[0] = y4[lim1]
        edge_1_z[0] = z4[lim1]

        all_edges.append([edge_1_x, edge_1_y, edge_1_z])
        lim1 = lim1 + n_strike
    
    lines = []
    for i in range(n_edges):
    
        sel_edge = np.array(all_edges[i])
        points = []
        for coo in np.arange(len(sel_edge[0,:])):

            points.append(Point(sel_edge[0][coo], sel_edge[1][coo], sel_edge[2][coo]))
        
        edg1_line = Line(points)     # cr
        lines.append(edg1_line)
        

    if plot:
        plot_mesh_grid_edges(mesh_subd, lines, output_path)

    return mesh_ids, mesh_subd, areas, lines


def plot_mesh_grid_edges(mesh, lines, output_path):
    '''
    '''
    for ip, p in enumerate(mesh):
        x, y = p.exterior.xy
        line, = plt.plot(x, y, color='#aaaaaa', linewidth=2)
        if ip == 0:
            line.set_label('mesh')


    for i in range(len(lines)): 
        xl = lines[i].coo[:,0]
        yl = lines[i].coo[:,1]
        # plt.plot(all_edges[i][0], all_edges[i][1], 
        #          linewidth=0, marker="o", markerfacecolor="#00ff00")
        line, = plt.plot(xl, yl, color='#ff0000')
        if i == 0:
            line.set_label('lines')

    plt.legend()
    plt.savefig(os.path.join(output_path, 'mesh_grid_lines.png'), format='png', dpi=300, bbox_inches='tight')
    plt.close()



def fmd(fmd_file, output_path, plot_fmd):
    """
    frequency magnitude distribution
    """
 
    gr_gar = np.load(fmd_file)
    #mws = gr_gar[0]
    #lambda_agg = gr_gar[1]
    mws = (gr_gar[0,1:] - gr_gar[0,:-1]) / 2 + gr_gar[0,:-1]
    lambda_agg = gr_gar[1,:-1] - gr_gar[1,1:] 
    fmd = ArbitraryMFD(magnitudes = mws, 
                          occurrence_rates = lambda_agg)

    if plot_fmd:
        plt.plot(mws, lambda_agg)
        plt.grid()
        plt.xlabel('Magnitude')
        plt.ylabel('Exceedance Rate (events/year)')
        plt.yscale('log')
        plt.savefig(os.path.join(output_path, 'frequency_magnitude_distribution.png'), format='png', bbox_inches='tight')
        plt.close()

    return fmd

"""
def fmd_from_nc(the_path):
   all_earth_scen_FAUS=netCDF4.Dataset(the_path)
   mag_rup=np.array(all_earth_scen_FAUS.variables['Mw'])
   ann_rate=np.array(all_earth_scen_FAUS.variables['annual_rate'])

"""

def define_source(fmd, list_lines):
    '''
    openquake earthquake sources

    temporal occurrence model
     --> here is 1 yr NOT USED FOR SOURCE CREATION BUT MANDATORY PARAMETER
     
    '''

    src1 = ComplexFaultSource(
         source_id = '1',
         name = 'source1',
         tectonic_region_type = 'Subduction Interface',
         mfd = fmd,
         rupture_mesh_spacing = 50.0,
         magnitude_scaling_relationship = StrasserInterface(),
         rupture_aspect_ratio = 1.0,
         temporal_occurrence_model = PoissonTOM(1.0),
         edges = list_lines,
         rake = 90.0)
    
    return src1




############## Rupture list creation part ####################################



###### function used to infer the ID of the subfault to be used in linear combination
#### they are based on the overlapping
def find_overlapping_rectangles(floating_rect, mesh_rectangles, mesh_ids):
    overlapping_ids = []
    for mesh_id, mesh_rect in zip(mesh_ids, mesh_rectangles):
        if floating_rect.intersects(mesh_rect):
            overlapping_ids.append(mesh_id)
    return overlapping_ids


def find_significant_overlapping_rectangles(floating_rect, mesh_rectangles, mesh_ids, threshold=0.3):
    significant_overlapping_ids = []
    for mesh_id, mesh_rect in zip(mesh_ids, mesh_rectangles):
        intersection_area = floating_rect.intersection(mesh_rect).area
        mesh_area = mesh_rect.area
        if intersection_area / mesh_area >= threshold:
            significant_overlapping_ids.append(mesh_id)
        

    return significant_overlapping_ids


def ruptures_lists(oq_sorce, my_subd, mesh_subd, mesh_ids, output_path, save):
     
    # Setting for expected slip estimate
    # Rigidity, Lame's constant, for slip estimate 
    mu_h = 3.3000e+10;  

    i_rup = oq_sorce.count_ruptures()
     
    ## empty object, separate but merged in the end 
    eve_id_all=[]
    str_all=[]
    ann_rate_all=[]
    area_rup=[]
    slip_rup=[]
    mag_rup=[]


    for i_rup,rup in enumerate(oq_sorce.iter_ruptures()):

        ### parameters direcly from oq 
        
        mag_rup.append(rup.mag)                   # magnitude 
        area_rup.append(rup.surface.get_area())   # area 
        ann_rate_all.append(rup.occurrence_rate)  #  
        
        
        #### inferred parameter 
        
        ############ Slip ##################################
        m_zero=10**((1.5*rup.mag)+9.1)
        aver_slip=m_zero/(mu_h*rup.surface.get_area()*1e6)
                
        slip_rup.append(aver_slip) 
        
        ##### snr_name
        snr_name=my_subd+'_'+str(i_rup)
        str_all.append(snr_name)
        
        #### Overlap Rupture and Subduction Mesh 
        
        # Boundary of the rupture
        rup_bound = rup.surface.get_surface_boundaries_3d()
        
        # Create polygon of the rupture
        rup_poly = Polygon(list(zip(rup_bound[0], rup_bound[1])))
        
        # # find overlapping reclangles 
        # overlapping_ids = find_overlapping_rectangles(rup_poly, mesh_subd, mesh_ids)
        
        # find overlapping reclangles with a percentage of coverage
        significant_overlapping_ids = find_significant_overlapping_rectangles(rup_poly, mesh_subd, mesh_ids)
        
        if len(significant_overlapping_ids)==0: 
            print('no overlap')
            significant_overlapping_ids = find_overlapping_rectangles(rup_poly, mesh_subd, mesh_ids)
            significant_overlapping_ids = significant_overlapping_ids[0]
            print(significant_overlapping_ids)
            

        eve_id_all.append(significant_overlapping_ids)
            
        
        
    # save DF 
    data = {
        "scenario": str_all,
        "annual_rate": ann_rate_all,
        "magnitude": mag_rup,
        "area": area_rup,
        "slip": slip_rup,
        "eve_ids": eve_id_all
    }

    rup_df = pd.DataFrame(data)
    # print(rup_df.head())
     

    if save:
        rup_df.to_pickle(os.path.join(output_path, 'list_eq_scenario_kurilsjapan.pkl'))
        rup_df.to_csv(os.path.join(output_path, 'list_eq_scenario_kurilsjapan.csv'))
    
    return rup_df












