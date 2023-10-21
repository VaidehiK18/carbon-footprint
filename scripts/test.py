import pandas as pd
from codecarbon import track_emissions
# import corsheader

@track_emissions()
def track():
    df = pd.read_csv('../CarbonEmission1India.csv')
    print(df)
    print(df[df['States']=='West Bengal'])
    for row in df.iterrows():
        if row[0] == 'West Bengal':
            print(row)    
    print(df['per capita CO2 (kg per person)'].mean())
track()