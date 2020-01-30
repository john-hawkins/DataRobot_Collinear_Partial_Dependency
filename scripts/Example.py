# Import the file: ../src/PartialDependency.py
sys.path.append('../src')
import PartialDependency as partd
import datarobot as dr
import pandas as pd

# DEFINE THE PROJECT AND MODEL WE WANT TO USE
PROJECT_ID = '5b63acf20c609e426492fecc'
MODEL_ID = '5b63afa50b701902c9747ae5'

# LOAD THE PROJECT AND MODEL
proj = dr.Project.get(project_id=PROJECT_ID)
mod =  dr.Model.get(PROJECT_ID, model_id=MODEL_ID)

# LOAD THE SAMPLE DATA THAT WILL BE USED
data = pd.read_csv('data/test.csv')

# DEFINE THE RELEVANT COLUMNS WE WILL USE
diffcol = "price_diff"
colone = "product_price"
coltwo = "competitor_price"

######################################################################################
# NOW USE THE METHOD THAT GENERATES THE PARTIAL DEPENDENCE PLOT AND SAVES IT

partd.generate_diff_col_pd_plot(proj, mod, data, difcol, colone, coltwo, "Example.png")

