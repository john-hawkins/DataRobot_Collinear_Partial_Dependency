"""
Custom Partial Dependency Functions for dealing with collinearity between variables

Created: 30 Jan 2020

@author: john.hawkins
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import subprocess as sp
import datarobot as dr
import pandas as pd
import numpy as np
import base64
import time
import yaml
import io

"""
 LOAD CONFIG DATA
 For running the batch scoring script
"""
config = yaml.safe_load(open('../config.yml'))

API_TOKEN = config['API_TOKEN']
USERNAME = config['USERNAME']
DATAROBOT_KEY = config['DATAROBOT_KEY']
HOST = config['HOST']

# ################################################################################
def get_test_values(data, col):
    """ generate the list of values to test for a specified column """
    vals = data[col].drop_duplicates()
    if len(vals) > 40:
        col_inc = (max(vals)- min(vals))/20
        vals = np.arange(min(vals), max(vals)+col_inc, col_inc)
    return vals

# ################################################################################
def generate_diff_col_pd_plot(proj, mod, data, diffcol, colone, coltwo, filename):
    """ Generate the partial dependency plot for a variable that is defined as a difference between 2 other variables """
    pdep = generate_diff_col_pd_data(proj, mod, data, diffcol, colone, coltwo)

    TARGET=proj.target

    plt1 = pdep[colone]
    plt2 = pdep[coltwo]

    plt.plot( plt1[diffcol], dim1[TARGET], marker='', color='olive', linewidth=2, label=colone)
    plt.plot( plt2[diffcol], dim2[TARGET], marker='', color='olive', linewidth=2, linestyle='dashed', label=colone)
    plt.legend()
    plt.savefig(filename, format='png')

 
# ################################################################################
def generate_diff_col_pd_data(proj, mod, pdata, diffcol, colone, coltwo):
    """ Generate two unique partial dependency plots for a differenced column.
        In each plot one of the reference columns is held unchanged and the other is
        modified to ensure that the difference relationship is maintained.
    """
    PROJECT_ID=proj.id
    MODEL_ID=mod.id
    TARGET=proj.target
    results = {}

    print("Rows in dataset:", len(pdata))
    diffcol_values = get_test_values(pdata, diffcol)
    colone_values = get_test_values(pdata, colone)
    coltwo_values = get_test_values(pdata, coltwo)
    total_variations = len(diffcol_values)
    print("Total Variations: ", total_variations)
    samples = int(30000/total_variations)
    if samples > len(pdata):
        samples = len(pdata)
    print("Number of Samples:", samples)

    """
      WE HAVE TO ADD A RANDOM STATE TO ENSURE THAT THE SAMPLES ARE UNIQUE
      EACH TIME WE EXECUTE. OTHERWISE THERE CAN BE ISSUES WHEN YOU RE_RUN THE SAME DATA
    """
    data_sample = pdata.sample(samples, random_state=round(time.time()) )

    """
      FIRST RUN THE DATA FOR WHICH WE LOOK AT HOLDING colone FIXED
    """
    partial_dependence_dfs = []
    for dif_value in diffcol_values:
        temp_data = data_sample.copy()
        temp_data[diffcol] = dif_value
        temp_data[coltwo] = temp_data[colone] - dif_value
        partial_dependence_dfs.append(temp_data)

    partial_dependence_df = pd.concat(partial_dependence_dfs)
    partial_dependence_df.to_csv('./XX_temp_data_for_scoring.csv', index=False)
    keep_cols = [diffcol]
    # SET UP THE BATCH PROCESS AND RUN
    command = ['batch_scoring',
               '-y',
               '--host', HOST,
               '--user', USERNAME,
               '--api_token', API_TOKEN,
               '--datarobot_key', DATAROBOT_KEY,
               '--keep_cols', ','.join(keep_cols),
               PROJECT_ID,
               MODEL_ID,
               './XX_temp_data_for_scoring.csv']    

    print("EXECUTING COMMAND:", ' '.join(command))
    output = sp.check_output(command, stderr=sp.STDOUT)

    preds = pd.read_csv('./out.csv') 

    pdep = process_scored_records(proj, diffcol, preds)

    # CLEAN UP THE CREATED FILES
    cleanup = ['rm', 'out.csv', 'datarobot_batch_scoring_main.log', 'XX_temp_data_for_scoring.csv']
    output = sp.check_output(cleanup, stderr=sp.STDOUT)

    results[colone] = pdep

    """
     THEN WE RUN THE DATA AGAIN WHERE WE LOOK AT HOLDING coltwo FIXED
    """
    partial_dependence_dfs = []
    for dif_value in diffcol_values:
        temp_data = data_sample.copy()
        temp_data[diffcol] = dif_value
        temp_data[colone] = temp_data[coltwo] + dif_value
        partial_dependence_dfs.append(temp_data)
    
    partial_dependence_df = pd.concat(partial_dependence_dfs)
    partial_dependence_df.to_csv('./XX_temp_data_for_scoring.csv', index=False)
    keep_cols = [diffcol]
    # SET UP THE BATCH PROCESS AND RUN
    command = ['batch_scoring',
               '-y',
               '--host', HOST,
               '--user', USERNAME,
               '--api_token', API_TOKEN,
               '--datarobot_key', DATAROBOT_KEY,
               '--keep_cols', ','.join(keep_cols),
               PROJECT_ID,
               MODEL_ID,
               './XX_temp_data_for_scoring.csv']  
        
    print("EXECUTING COMMAND:", ' '.join(command))
    output = sp.check_output(command, stderr=sp.STDOUT)

    preds = pd.read_csv('./out.csv')

    pdep = process_scored_records(proj, diffcol, preds)

    # CLEAN UP THE CREATED FILES
    cleanup = ['rm', 'out.csv', 'datarobot_batch_scoring_main.log', 'XX_temp_data_for_scoring.csv']
    output = sp.check_output(cleanup, stderr=sp.STDOUT)

    results[coltwo] = pdep

    return results


# ################################################################################
def process_scored_records(proj, diffcol, preds):
    """ Process the records from the batch scoring job """
    preds.loc[preds[diffcol].isna(), diffcol] = 'N/A'
    
    justcols = preds.loc[:,[diffcol,proj.target]]
    if (proj.target_type == 'Classification') :
       justcols = preds.loc[:,[diffcol,'True']]

    return justcols.groupby(diffcol, as_index=False).mean()


# ################################################################################
def generate_diff_field_pd_embedded(proj, mod, pdata, diffcol, colone, coltwo):
    """
      CREATE A PARTIAL DEPENDENCY AND RETURN STRING CODE TO EMBED 
      INSIDE A FLASK WEB APPLICATION
    """
    pdep = generate2WayPD_Data(proj, mod, pdata, colone, coltwo)
    TARGET=proj.target
    dim1 = pdep[colone]
    dim2 = pdep[coltwo]
    dim3 = pdep[TARGET]

    img = io.BytesIO()
    mpl.rcParams['legend.fontsize'] = 10
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot_trisurf(dim1, dim2, dim3, cmap=cm.coolwarm, linewidth=0, antialiased=False)
    ax.set_xlabel(colone)
    ax.set_ylabel(coltwo)
    ax.set_zlabel(TARGET)
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return 'data:image/png;base64,{}'.format(plot_url)


