#%%
import pandas as pd
import numpy as np
from typing import List


# %%
data = pd.read_csv(r'Data/data.csv')

# %%
np.random.randint(50, 90, data.shape[0])

# %%
np.random.choice(['new', 'return'], data.shape[0])
# %%
data.columns
# %%
data['conversion_rate'] = np.random.randint(50, 90, data.shape[0])
# %%

def generate_values(data: pd.DataFrame, columns: List[str], 
                    start_value: int, end_value: int) -> pd.DataFrame:
    if columns:
        if isinstance(columns, list):
            for name in columns:
                data[name] = np.random.randint(start_value, end_value, data.shape[0])
        else:
            data[columns] = np.random.randint(start_value, end_value, data.shape[0])
    else:
        columns= data.columns
        for name in columns:
                data[name] = np.random.randint(start_value, end_value, data.shape[0])
                
    return data
        
# %%
generate_values(data = data, columns='bounce_rate', start_value=5, 
                end_value=20)
# %%
generate_values(data, columns='new_user', start_value=20,
                end_value=500)
# %%
generate_values(data, columns='return_user', start_value=100,
                end_value=300)
# %%
generate_values(data=data, columns='new_user_con_rate',
                start_value=50, end_value=70)
# %%
generate_values(data=data, columns='return_user_con_rate',
                start_value=70, end_value=95)

# %%
generate_values(data=data, columns='new_user_bounce_rate',
                start_value=10, end_value=30)
# %%
generate_values(data=data, columns='return_user_bounce_rate',
                start_value=5, end_value=10)
# %%

data.to_csv('Data/new_data.csv')




# %%
