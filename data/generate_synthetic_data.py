
import pandas as pd
import numpy as np
import datetime
import random

start = datetime.datetime.strptime("2010-01-01", "%Y-%m-%d")
end = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]

df['month'] = df['date'].map(lambda x: x.month)
 
seq_len = len(date_generated)

prices = [(95 + 0.0005*x + 5*random.uniform(0, 1)) for x in range(seq_len)]
comp_price = [(95 + 0.0005*x + 6*random.uniform(0, 1)) for x in range(seq_len)]
 
df = pd.DataFrame({'date':date_generated, 'product_price':prices, 'comp_price':comp_price})

df['price_diff'] = df['product_price'] - df['comp_price']

df['base_market'] = [(10000 + x + 10*random.uniform(0, 1)) for x in range(seq_len)]
df['total_market'] = df['base_market'] + 10*df['month']

df['base_share'] = np.where( df['product_price'] <100,0.49,0.48)

df['comp_base_share'] = np.where( df['comp_price'] <100,0.49,0.48)

df['contestable'] = 1 - (df['base_share'] + df['comp_base_share'])

df['won'] = df['contestable'] * ((6 - df['price_diff']) / 12) + df['base_share']

df['sales'] = df['won'] * df['total_market']

columns = ['date', 'product_price', 'comp_price', 'price_diff', 'sales']

final_data = df.loc[:,columns]

train = final_data[0:2500]
test = final_data[2500:len(final_data)]

train.to_csv('train.csv', index=False, header=True)
test.to_csv('test.csv', index=False, header=True)


