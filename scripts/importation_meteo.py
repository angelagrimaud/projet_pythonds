import pandas as pd

meteo_202023_75 = pd.read_parquet("../data_meteo/2020-2023_75.parquet", engine="pyarrow")
meteo_202425_75 = pd.read_parquet("../data_meteo/2024-2025_75.parquet", engine="pyarrow")