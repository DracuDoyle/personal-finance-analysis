# SECCION 1 : Importaciones y configuración


import pandas as pd
from sqlalchemy import create_engine

# URL = postgresql+psycopg2://usuario:contraseña@servidor/base_de_datos
engine = create_engine( 'postgresql+psycopg2://postgres:admin123@localhost/personal_finance' )




# SECCION 2 : Extract

df = pd.read_excel( 'data/personal_transactions.xlsx' )

print( df.shape )
print( df.head() )




# SECCION 3 : Transform


# Parte 1. Convertir Date a formato fecha simple

df[ 'Date' ] = pd.to_datetime( df[ 'Date' ] )


# Parte 2. Extraer mes, año y trimestre

df[ 'anio' ] = df[ 'Date' ].dt.year
df[ 'mes' ] = df[ 'Date' ].dt.month
df[ 'trimestre' ] = df[ 'Date' ].dt.quarter
df[ 'anio_mes' ] = df[ 'Date' ].dt.to_period( 'M' ).astype( str )


# Parte 3. Clasificar cada transaccion

# credit  +  Paycheck             →  ingreso
# credit  +  Credit Card Payment  →  transferencia (excluir del análisis)
# debit   +  cualquier categoria  →  gasto

def clasificar( row ):
    
    if row[ 'Transaction Type' ] == 'credit' and row[ 'Category' ] == 'Paycheck':
        return 'ingreso'
    
    elif row[ 'Transaction Type' ] == 'credit' and row[ 'Category' ] == 'Credit Card Payment':
        return 'transferencia'
    
    elif row[ 'Transaction Type' ] == 'debit':
        return 'gasto'
    
    else:
        return 'desconocido'

df[ 'tipo_real' ] = df.apply( clasificar, axis = 1 )


# Parte 4. Crear tablas de dimensiones

dim_categoria = df[ [ 'Category' ] ].drop_duplicates().reset_index( drop = True )
dim_categoria[ 'id_categoria' ] = dim_categoria.index + 1

dim_cuenta = df[ [ 'Account Name' ] ].drop_duplicates().reset_index( drop = True )
dim_cuenta[ 'id_cuenta' ] = dim_cuenta.index + 1


# Parte 5. Verificar

print( df[ [ 'Date', 'anio', 'mes', 'trimestre', 'tipo_real', 'anio_mes' ] ].head( 10 ) )
print( '\nCategorias:\n', dim_categoria )
print( '\nCuentas:\n', dim_cuenta )




# SECCION 4 : Load

# Cargar dimensiones primero por buena practica y por si se deben de crear foreign keys

dim_categoria.to_sql( 'dim_categoria', engine, if_exists = 'replace', index = False )
dim_cuenta.to_sql( 'dim_cuenta', engine, if_exists = 'replace', index = False )

# Cargar tabla de hechos
df.to_sql( 'hechos_transacciones', engine, if_exists = 'replace', index = False )

print( '\nDatos cargados exitosamente a PostgreSQL' )
