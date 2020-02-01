# Import the file: ../src/PartialDependency.py
import datarobot as dr
import pandas as pd
import sys
sys.path.append('../src')
import PartialDependency as partd

# DEFINE THE PROJECT AND MODEL WE WANT TO USE
PROJECT_ID = '5e340ee7422fbd2582a5ed88'
MODEL_ID = '5e340fc58ecc14b40c781f28'

# LOAD THE PROJECT AND MODEL
proj = dr.Project.get(project_id=PROJECT_ID)
mod =  dr.Model.get(PROJECT_ID, model_id=MODEL_ID)

# LOAD THE SAMPLE DATA THAT WILL BE USED
data = pd.read_csv('../data/test.csv')

# DEFINE THE RELEVANT COLUMNS WE WILL USE
# product_price,comp_price,price_diff
diffcol = "price_diff"
colone = "product_price"
coltwo = "comp_price"

######################################################################################
# NOW USE THE METHOD THAT GENERATES THE PARTIAL DEPENDENCE PLOT AND SAVES IT

partd.generate_diff_col_pd_plot(proj, mod, data, diffcol, colone, coltwo, "Example.png")

