# Import the file: ../src/PartialDependency.py
import datarobot as dr
import pandas as pd
import sys
sys.path.append('../src')
import PartialDependency as partd

# DEFINE THE PROJECT AND MODEL WE WANT TO USE

PROJECT_ID = '5e3565db79dd6b1936771628'
MODEL_ID = '5e35665d5143d8794be38896'
 
# LOAD THE PROJECT AND MODEL
proj = dr.Project.get(project_id=PROJECT_ID)
mod =  dr.Model.get(PROJECT_ID, model_id=MODEL_ID)

# LOAD THE SAMPLE DATA THAT WILL BE USED
data = pd.read_csv('../data/test.csv')

# DEFINE THE RELEVANT COLUMNS WE WILL USE
# product_price, competitor_price, price_diff
#
diffcol = "price_diff"
colone = "product_price"
coltwo = "competitor_price"

######################################################################################
# NOW USE THE METHOD THAT GENERATES THE PARTIAL DEPENDENCE PLOT AND SAVES IT
 
plt = partd.generate_diff_col_pd_plot(proj, mod, data, diffcol, colone, coltwo, "../config.yml")

plt.savefig("Example.png", format='png')

