
import pandas as pd
import numpy as np
import datetime
import random

start = datetime.datetime.strptime("2010-01-01", "%Y-%m-%d")
end = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]
 
seq_len = len(date_generated)

prices = [(95 + 0.0005*x + 5*random.uniform(0, 1)) for x in range(seq_len)]
competitor_price = [(95 + 0.0005*x + 6*random.uniform(0, 1)) for x in range(seq_len)]
 
df = pd.DataFrame({'date':date_generated, 'product_price':prices, 'competitor_price':competitor_price})

df['month'] = df['date'].map(lambda x: x.month)

df['price_diff'] = df['product_price'] - df['competitor_price']

df['base_market'] = [(10000 + x + 10*random.uniform(0, 1)) for x in range(seq_len)]
df['total_market'] = df['base_market'] + 10*random.uniform(0, 1)*df['month']*df['month'] 

df['base_share'] = np.where( df['product_price'] <100,0.48,0.47)
df['is_under'] = np.where( df['product_price'] <100,1,0)

df['comp_base_share'] = np.where( df['competitor_price'] <100,0.47,0.45)

df['contestable'] = 1 - (df['base_share'] + df['comp_base_share'])

df['won'] = df['contestable'] * ((6 - df['price_diff'] + (2*df['is_under']) ) / 14) + df['base_share']

df['sales'] = df['won'] * df['total_market']

columns = ['date', 'product_price', 'competitor_price', 'price_diff', 'sales']

final_data = df.loc[:,columns]

train = final_data[0:2500]
test = final_data[2500:len(final_data)]

train.to_csv('train.csv', index=False, header=True)
test.to_csv('test.csv', index=False, header=True)


