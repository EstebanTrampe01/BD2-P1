import pandas as pd

# Leer archivo original
df = pd.read_csv("grupos.csv")


df = df.rename(columns={
    "mundial": "id_mundial",      
    "seleccion": "id_seleccion",  
    "grupo": "grupo",           
    "posicion": "posicion",      
    "pj": "pj",                 
    "pg": "pg",                  
    "pe": "pe",                  
    "pp": "pp",                  
    "gf": "gf",                  
    "gc": "gc",                   
    "dif": "dif",                
    "pts": "pts",                 
    "clasificado": "clasificado"  
})


df["id_seleccion"] = df["id_seleccion"].astype(str).str.strip()


df["id_mundial"] = pd.to_numeric(df["id_mundial"], errors='coerce')
df["id_seleccion"] = pd.to_numeric(df["id_seleccion"], errors='coerce')

df_final = df[
    [
        "id_mundial",
        "grupo",
        "id_seleccion",
        "posicion",
        "pj",
        "pg",
        "pe",
        "pp",
        "gf",
        "gc",
        "dif",
        "pts",
        "clasificado"
    ]
]


df_final.to_csv("grupos_transformado.csv", index=False, encoding="utf-8")