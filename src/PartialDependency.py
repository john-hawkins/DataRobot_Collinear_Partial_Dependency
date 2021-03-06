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


# ################################################################################
def get_test_values(data, col):
    """ generate the list of values to test for a specified column """
    vals = data[col].drop_duplicates()
    if len(vals) > 40:
        col_inc = (max(vals)- min(vals))/20
        vals = np.arange(min(vals), max(vals)+col_inc, col_inc)
    return vals

 
# ################################################################################
def generate_diff_col_pd_data(proj, mod, data, diffcol, colone, coltwo):
    """ Generate two unique partial dependency plots for a differenced column.
        In each plot one of the reference columns is held unchanged and the other is
        modified to ensure that the difference relationship is maintained.
    """
    PROJECT_ID=proj.id
    MODEL_ID=mod.id
    TARGET=proj.target
    results = {}

    print("Rows in dataset:", len(data))
    diffcol_values = get_test_values(data, diffcol)
    colone_values = get_test_values(data, colone)
    coltwo_values = get_test_values(data, coltwo)
    total_variations = len(diffcol_values)
    print("Total Variations: ", total_variations)
    samples = int(30000/total_variations)
    if samples > len(data):
        samples = len(data)
    print("Number of Samples:", samples)

    """
      WE HAVE TO ADD A RANDOM STATE TO ENSURE THAT THE SAMPLES ARE UNIQUE
      EACH TIME WE EXECUTE. OTHERWISE THERE CAN BE ISSUES WHEN YOU RE_RUN THE SAME DATA
    """
    data_sample = data.sample(samples, random_state=round(time.time()) )

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

    dataset = proj.upload_dataset(partial_dependence_df)
    pred_job = mod.request_predictions(dataset.id)
    preds = dr.models.predict_job.wait_for_async_predictions(proj.id, predict_job_id=pred_job.id, max_wait=600)
    temp = partial_dependence_df.reset_index()[diffcol]
    preds[diffcol] = temp
    pdep = process_scored_records(proj, diffcol, preds)

    results[coltwo] = pdep

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

    dataset = proj.upload_dataset(partial_dependence_df)
    pred_job = mod.request_predictions(dataset.id)
    preds = dr.models.predict_job.wait_for_async_predictions(proj.id, predict_job_id=pred_job.id, max_wait=600)
    temp = partial_dependence_df.reset_index()[diffcol]
    preds[diffcol] = temp 
    pdep = process_scored_records(proj, diffcol, preds)
 
    results[colone] = pdep

    return results


# ################################################################################
def process_scored_records(proj, diffcol, preds):
    """ Process the records from the batch scoring job """
    preds.loc[preds[diffcol].isna(), diffcol] = 'N/A'

    if (proj.target_type == 'Binary') :
       justcols = preds.loc[:,[diffcol, 'true']]
       justcols.columns = [diffcol, proj.target]
    else:
       justcols = preds.loc[:,[diffcol, 'prediction']]
       justcols.columns = [diffcol, proj.target]

    pdep = justcols.groupby(diffcol, as_index=False).agg({ proj.target:['mean','std'] }) 
    pdep.columns = [diffcol, proj.target, 'std']
    pdep['lower'] = pdep[proj.target] - pdep['std']
    pdep['upper'] = pdep[proj.target] + pdep['std']
    return pdep

# ################################################################################
def generate_diff_field_pd_embedded(proj, mod, data, diffcol, colone, coltwo):
    """
      CREATE A PARTIAL DEPENDENCY AND RETURN STRING CODE TO EMBED 
      INSIDE A FLASK WEB APPLICATION -- THIS DOES NOT WORK YET
    """

    plt = generate_diff_col_pd_plot(proj, mod, data, diffcol, colone, coltwo)

    img = io.BytesIO()
    mpl.rcParams['legend.fontsize'] = 10
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return 'data:image/png;base64,{}'.format(plot_url)

# ################################################################################
def generate_diff_col_pd_plot(proj, mod, data, diffcol, colone, coltwo):
    """ Generate the partial dependency plot for a variable that is defined as a difference between 2 other variables """
    pdep = generate_diff_col_pd_data(proj, mod, data, diffcol, colone, coltwo )

    TARGET=proj.target

    plt1 = pdep[colone]
    plt2 = pdep[coltwo]

    plt.plot( plt1[diffcol], plt1[TARGET], marker='', color='#1111AA', linewidth=2, label=("Varying: "+colone) )
    plt.plot( plt2[diffcol], plt2[TARGET], marker='', color='#AA1111', linewidth=2, linestyle='dashed', label=("Varying: "+coltwo))
    plt.fill_between( plt1[diffcol], plt1['lower'], plt1['upper'], color='#AAAADD', alpha=0.2)
    plt.fill_between( plt2[diffcol], plt2['lower'], plt2['upper'], color='#DDAAAA', alpha=0.2)
    plt.legend()
    plt.xlabel(diffcol)
    plt.ylabel(TARGET)
    return plt

# ################################################################################
def generate_diff_col_pd_plot_and_save(proj, mod, pdata, diffcol, colone, coltwo, plotpath):
    plt = generate_diff_col_pd_plot(proj, mod, pdata, diffcol, colone, coltwo)
    print("PLOT GENERATED -- SAVING TO: ", plotpath)
    plt.savefig(plotpath, format='png')
    print("SAVED")
    plt.close()

