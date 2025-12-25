import pandas as pd

meteo_202023_75 = pd.read_parquet("../data_meteo/2020-2023_75.parquet", engine="pyarrow")
meteo_202425_75 = pd.read_parquet("../data_meteo/2024-2025_75.parquet", engine="pyarrow")

meteo_departementale2024 = pd.read_csv("https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/temperature-quotidienne-departementale/exports/csv?lang=fr&refine=date_obs%3A%222024%22&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B",sep=';')