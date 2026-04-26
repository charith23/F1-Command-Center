import fastf1
import pandas as pd

def get_f1_data(year, race_name):
    
    fastf1.Cache.enable_cache('cache') 
    
    session = fastf1.get_session(year, race_name, 'R')
    session.load()
    
    results = session.results
    data = []
    
    for _, row in results.iterrows():
        data.append({
            'Driver': row['Abbreviation'],
            'Team': row['TeamName'],
            'GridPosition': row['GridPosition'],
            'FinishPosition': row['ClassifiedPosition'],
            'Status': row['Status']
        })
    
    return pd.DataFrame(data)