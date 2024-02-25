import pandas as pd
import requests
import sqlite3

def dolarizar_montos(df):

    
    response = requests.get("https://api.apis.net.pe/v1/tipo-cambio-sunat")

    tipo_cambio = response.json()["compra"]
    
    df["MONTO DE INVERSION EN DOLARES"] = df["MONTO DE INVERSIÓN"] / tipo_cambio
    df["MONTO DE TRANSFERENCIA EN DOLARES"] = df["MONTO DE TRANSFERENCIA 2020"] / tipo_cambio

    return df

def limpiar_renombrar_columnas(df):

    df_cleaned = df.copy()

    
    df_cleaned.columns = df_cleaned.columns.str.lower() 
    df_cleaned.columns = df_cleaned.columns.str.replace(' ', '_')  
    df_cleaned.columns = (df_cleaned.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))  

    return df_cleaned


df_excel = pd.read_excel("reactiva.xlsx",sheet_name="TRANSFERENCIAS 2020")
df_excel = df_excel.rename(columns={"POBLACION BENEFICIARIA": "POBLACION","CODIGO PAIS": "PAIS"})
df_excel = df_excel.drop(['ID'],axis=1)
df_excel = df_excel.drop(['TIPO MONEDA.1'],axis=1)
df_excel["DISPOSITIVO LEGAL"] = df_excel['DISPOSITIVO LEGAL'].replace({',':''},regex=True)

df_excel = dolarizar_montos(df_excel)

df_excel["Estado"] = df_excel["ESTADO"].replace({
    "Convenio y/o Contrato Resuelto": "Resuelto",
    "En Ejecución": "Ejecucion"
})

df_excel["Puntuacion Estado"] = df_excel["Estado"].map({
    "Actos Previos": 1,
    "Resuelto": 0,
    "Ejecucion": 2,
    "Concluido": 3
})


print(df_excel.head())

base_df = pd.read_excel("reactiva.xlsx", sheet_name="TRANSFERENCIAS 2020")


base_df = base_df[['UBIGEO', 'ESTADO','REGION', 'PROVINCIA', 'DISTRITO','AMBITO']].drop_duplicates()


conn = sqlite3.connect('baseExcel.db')

base_df.to_sql('ubigeos', conn, if_exists='replace', index=False)

for region in base_df['REGION'].unique():
    region_df = base_df[(base_df['REGION'] == region) & (base_df['AMBITO'] == 'URBANO')]
    if len(region_df) == 0:
        continue
    for estado in [1, 2, 3]:
        estado_df = region_df[region_df['ESTADO'] == estado]
        if len(estado_df) == 0:
            continue
        top5_df = estado_df.nlargest(5, 'CostoInversion')
        excel_name = f"Top5_{region}_Estado{estado}.xlsx"
        top5_df.to_excel(excel_name, index=False)


conn.close()




# Llama a la función para limpiar y renombrar columnas
#df_limpiado = limpiar_renombrar_columnas(df)

#print(df_limpiado.head())




