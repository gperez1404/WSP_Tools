# -*- coding: utf-8 -*-
"""
Created on Thrisday 13th of June 2024

# This script generates interactive plots to compare 
# streamflow data

@author: Gabriel Perez Murillo
         Project Water Resources Engineer
         Mine Services
         WSP Australia Pty Limited
         Gabriel.Perez@wsp.com
"""
#####################################################################################################################
# Libraries
#####################################################################################################################
#%%
import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
from scipy.stats import linregress

import plotly.graph_objs as go
import plotly.express as px

from plotly.subplots import make_subplots

print('Libraries loaded successfully...')
#%%
#####################################################################################################################
#    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^     End of libraries
#####################################################################################################################

#####################################################################################################################
# Inputs
#####################################################################################################################

#%%
# locations of input and output files
current_execution_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_execution_path)

# These are the names of the folders  realtive to the root path:

input_data_folder  =r"inputs"
results_folder     = r'outputs'

# This is the name oif the fie with the inputs 

# the file has two sheets :
                # sheet #1 : data published
                # sheet #2 : data obtaiend after field visits 
                
input_file =r'G9290006-Angurugu River US of Groote Eylandt Mission Stream flow.xlsx'

title_plot_1 = r'Streamflow [m3/sec] at G9290006-Angurugu River US of Groote Eylandt Mission'
result_file_name_1 =  r'Comparison_streamflow_at_G9290006.html'

title_plot_2 = r'Streamflow [m3/sec] at G9290006-Angurugu River US of Groote Eylandt Mission'
result_file_name_2 =  r'Comparison_streamflow_at_G9290006_points.html'

# !!!!!!!!!!!!!!!!!!!!!!!!!!
# warning: 
# !!!!!!!!!!!!!!!!!!!!!!!!!!

#if you change the name of the columns or sheets in the input file
#you need to change the following inputs to match those names:

sheet_name_published_data ='G9290006_p'
sheet_name_visits_data = 'G9290006_v'

col_name_dates_data_p = 'Date'
col_name_dates_data_v = 'Date'

col_name_stremaflow_data_p = 'Stream_Discharge_cumecs'
col_name_stremaflow_data_v = 'Stream_Discharge_cumecs'

print('inputs loaded successfully !')
#%%
#####################################################################################################################
#    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^     End Inputs
#####################################################################################################################


#####################################################################################################################
# Functions
#####################################################################################################################
#%%
    
# Generates a Line plot grouping elements by attribute defined by user

def Gen_line_plot_grouped_by_item(df_to_plot,
                                  column_to_filter,
                                  column_dates,
                                  column_to_plot,
                                  plot_title,
                                  Xaxis_plot,
                                  Yaxis_plot):
    
    # Filter data for unique item values to create a plot for each one of them
    unique_item_list = df_to_plot [column_to_filter].unique()

    # Create a Plotly figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    print(r'Generating plot, please wait...')

    # Loop through each unique item and add a line plot to the figure
    for item in unique_item_list:
        # Filter the dataframe for the current item
        df_filtered = df_to_plot[df_to_plot[column_to_filter] == item]
        
        # Add a trace for the station
        fig.add_trace(go.Scatter(x=df_filtered[column_dates], 
                                 y=df_filtered[column_to_plot],
                                 mode='lines',
                                 name=item),
                      secondary_y=False)
    
    # Update the layout of the figure
    fig.update_layout(title_text=plot_title,
                      xaxis_title=Xaxis_plot,
                      yaxis_title=Yaxis_plot)
    print('Figure generated successfully...')
    return fig


#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Generates a Line plot  with points on top of lines grouping elements 
# by attribute defined by user
# this only plots the same type of data in the Y axis

def Gen_lines_plot_with_sample_points_grouped_by_item(df_to_plot_as_lines,
                                                      df_to_plot_as_points,
                                                      column_to_group_line_data,
                                                      column_to_group_point_data,
                                                      column_dates_line_data,
                                                      column_dates_point_data,
                                                      column_to_plot_line_data,
                                                      column_to_plot_point_data,
                                                      colors_lines,
                                                      colors_points,
                                                      points_shape,
                                                      plot_title,
                                                      Xaxis_plot,
                                                      Yaxis_plot):
    
    # Filter data for unique item values to create a plot for each one of them
    unique_lines_item_list = df_to_plot_as_lines [column_to_group_line_data].unique()
    unique_points_item_list = df_to_plot_as_points [column_to_group_point_data].unique()

    # Create a Plotly figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    print(r'Generating plot, please wait...')

    # Loop through all the data sets that are supposed to be plot as lines
    for item in unique_lines_item_list:
        # Filter the dataframe for the current item
        df_filtered = df_to_plot_as_lines[df_to_plot_as_lines[column_to_group_line_data] == item]
        
        # Add a trace for the station
        fig.add_trace(go.Scatter(x=df_filtered[column_dates_line_data], 
                                 y=df_filtered[column_to_plot_line_data],
                                 mode='lines',
                                 name=item,
                                 line=dict(color=colors_lines.get(item))),
                      secondary_y=False)
    
    # Loop through all the data sets that are supposed to be plot as points
    for item in unique_points_item_list:
        # Filter the dataframe for the current item
        df_points_filtered = df_to_plot_as_points[df_to_plot_as_points[column_to_group_point_data] == item]
        
        # Add a trace for the station
        fig.add_trace(go.Scatter(x=df_points_filtered[column_dates_point_data], 
                                 y=df_points_filtered[column_to_plot_point_data],
                                 mode='markers',
                                 name=item,
                                 marker=dict(color=colors_points.get(item), symbol=points_shape.get(item))),
                      secondary_y=False)
    
    # Update the layout of the figure
    fig.update_layout(title_text=plot_title,
                      xaxis_title=Xaxis_plot,
                      yaxis_title=Yaxis_plot)
    print('Figure generated successfully...')
    return fig

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


print('Functions compiled successfully...')
#%%
#####################################################################################################################
#     ^     ^     ^     ^     ^     ^     ^     ^     ^     ^     ^     ^     ^     ^     ^     ^       End Functions
#####################################################################################################################

    
#####################################################################################################################
# Main
#####################################################################################################################

# Load data provided by the client:
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#%%

#create paths
input_files_path = os.path.join(root_path,input_data_folder)
output_files_path =os.path.join(root_path,results_folder)

print('reading files with input data...')

file_to_read = os.path.join(input_files_path,input_file)

df_streamflow_p = pd.read_excel(file_to_read,
                                sheet_name=sheet_name_published_data,
                                dtype={col_name_dates_data_p: str, col_name_stremaflow_data_p: float,'type': str})
                                
df_streamflow_v = pd.read_excel(file_to_read,
                                sheet_name=sheet_name_visits_data,
                                dtype={col_name_dates_data_v: str,col_name_stremaflow_data_v: float,'type': str})

# Convert the 'Date' column from string to datetime
df_streamflow_p[col_name_dates_data_p] = pd.to_datetime(df_streamflow_p [col_name_dates_data_p], errors='coerce')
df_streamflow_v[col_name_dates_data_v] = pd.to_datetime(df_streamflow_v [col_name_dates_data_v], errors='coerce')

# Combine the dataframes
# you need to rename the columns to amke evrything consistent:
df_p =df_streamflow_p.copy()
df_p.rename(columns={col_name_dates_data_p: 'Date',col_name_stremaflow_data_p: 'Stream_Discharge'}, inplace=True)

df_v =df_streamflow_v.copy()
df_v.rename(columns={col_name_dates_data_v: 'Date',col_name_stremaflow_data_v: 'Stream_Discharge'}, inplace=True)

df_streamflow = pd.concat([df_p, df_v], ignore_index=True)

print('Data loaded successfully !! :D ')
#%%
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Generate the interactive plots 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#%%

#Plot 1

dict_color_codes_Streamflow = {'Published': '#0099C6',
                               'Visits': '#316395'}


label_Y_axis =  r'Streamflow [m^3/sec]'

Figure= Gen_line_plot_grouped_by_item(df_to_plot=df_streamflow,
                                      column_to_filter = 'type',
                                      column_dates= 'Date',
                                      column_to_plot= 'Stream_Discharge',
                                      plot_title = title_plot_1,
                                      Xaxis_plot = 'Date',
                                      Yaxis_plot = label_Y_axis)
    

# Save the figure as an HTML file
result_fig = os.path.join(output_files_path, result_file_name_1)
Figure.write_html(result_fig)

# Display the figure
Figure.show()

# :::::::::::::::::::::::::::::::::::::::::::::
#Plot 2

# generate figure with points on top of the lines

color_dic_lines = {'published': '#1C8356'}
color_dic_points = {'visits': '#620042'}
dict_points_shape = {'visits': 'circle'}

label_X=  r'Date'
label_Y=  r'Streamflow [m^3/sec]'


Figure = Gen_lines_plot_with_sample_points_grouped_by_item(df_to_plot_as_lines= df_streamflow_p,
                                                           df_to_plot_as_points = df_streamflow_v,
                                                           column_to_group_line_data='type',
                                                           column_to_group_point_data = 'type',
                                                            column_dates_line_data = 'Date',
                                                            column_dates_point_data = 'Date',
                                                            column_to_plot_line_data = 'Stream_Discharge_cumecs',
                                                            column_to_plot_point_data = 'Stream_Discharge_cumecs',
                                                            colors_lines =color_dic_lines,
                                                            colors_points=color_dic_points,
                                                            points_shape=dict_points_shape,
                                                            plot_title= title_plot_2,
                                                            Xaxis_plot =label_X,
                                                            Yaxis_plot=label_Y)

# Save the figure as an HTML file
result_fig = os.path.join(output_files_path, result_file_name_2)
Figure.write_html(result_fig)

# Display the figure
Figure.show()
#%%
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#####################################################################################################################
#    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^    ^     ^     End  Main
#####################################################################################################################

