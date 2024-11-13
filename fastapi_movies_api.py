# Importar las librerías necesarias
import pandas as pd
import numpy as np
import ast
import requests
import os
import gdown
from fastapi import FastAPI

# Inicializar la aplicación FastAPI
app = FastAPI()

# Función para descargar archivos desde Google Drive usando gdown
def descargar_archivo(url, ruta_destino):
    # Crear el directorio de destino si no existe
    directorio = os.path.dirname(ruta_destino)
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    # Descargar el archivo usando gdown
    try:
        gdown.download(url, ruta_destino, quiet=False)
    except Exception as e:
        raise Exception(f"Error al descargar el archivo desde {url}: {str(e)}")

# URLs de descarga directa desde Google Drive
url_movies = 'https://drive.google.com/uc?export=download&id=10x-1RLPD7RAVMtx7h7UVAX1qnMzBQCov'
url_credits = 'https://drive.google.com/uc?export=download&id=1UtaZdWt80Yyx2D69LITUMWyqt4Iuhggt'

# Rutas de destino donde se guardarán los archivos descargados
ruta_movies = '/mnt/data/movies_dataset_transformed.csv'
ruta_credits = '/mnt/data/credits.csv'

# Descargar los archivos antes de usarlos
descargar_archivo(url_movies, ruta_movies)
descargar_archivo(url_credits, ruta_credits)

# Cargar los datos transformados
movies_df = pd.read_csv(ruta_movies, low_memory=False)
credits_df = pd.read_csv(ruta_credits, low_memory=False)

# Definir las funciones de los endpoints de la API
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    """
    Se ingresa un mes en idioma Español. Devuelve la cantidad de películas que fueron estrenadas en el mes consultado.
    """
    # Diccionario para mapear el mes en español al número del mes
    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    
    mes = mes.lower()
    if mes not in meses:
        return {"error": "Mes no válido. Ingrese un mes en español."}
    
    # Filtrar el DataFrame por el mes de lanzamiento
    mes_numero = meses[mes]
    cantidad = movies_df[pd.to_datetime(movies_df['release_date'], errors='coerce').dt.month == mes_numero].shape[0]
    
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en el mes de {mes}"}

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    """
    Se ingresa un día en idioma Español. Devuelve la cantidad de películas que fueron estrenadas en el día consultado.
    """
    # Diccionario para mapear el día en español al número del día de la semana
    dias = {
        "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
        "viernes": 4, "sábado": 5, "domingo": 6
    }
    
    dia = dia.lower()
    if dia not in dias:
        return {"error": "Día no válido. Ingrese un día en español."}
    
    # Filtrar el DataFrame por el día de la semana de lanzamiento
    dia_numero = dias[dia]
    cantidad = movies_df[pd.to_datetime(movies_df['release_date'], errors='coerce').dt.dayofweek == dia_numero].shape[0]
    
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en los días {dia}"}

@app.get("/score_titulo/{titulo_de_la_filmacion}")
def score_titulo(titulo_de_la_filmacion: str):
    """
    Se ingresa el título de una filmación. Devuelve el título, el año de estreno y el score.
    """
    titulo_de_la_filmacion = titulo_de_la_filmacion.lower()
    filtro = movies_df['title'].str.lower() == titulo_de_la_filmacion
    pelicula = movies_df[filtro]
    
    if pelicula.empty:
        return {"error": "No se encontró una película con ese título."}
    
    titulo = pelicula['title'].values[0]
    anio_estreno = pelicula['release_year'].values[0]
    score = pelicula['popularity'].values[0]
    
    return {"mensaje": f"La película {titulo} fue estrenada en el año {anio_estreno} con un score/popularidad de {score}"}

@app.get("/votos_titulo/{titulo_de_la_filmacion}")
def votos_titulo(titulo_de_la_filmacion: str):
    """
    Se ingresa el título de una filmación. Devuelve el título, la cantidad de votos y el valor promedio de las votaciones si cumple la condición de tener al menos 2000 valoraciones.
    """
    titulo_de_la_filmacion = titulo_de_la_filmacion.lower()
    filtro = movies_df['title'].str.lower() == titulo_de_la_filmacion
    pelicula = movies_df[filtro]
    
    if pelicula.empty:
        return {"error": "No se encontró una película con ese título."}
    
    titulo = pelicula['title'].values[0]
    anio_estreno = pelicula['release_year'].values[0]
    cantidad_votos = pelicula['vote_count'].values[0]
    promedio_votos = pelicula['vote_average'].values[0]
    
    if cantidad_votos < 2000:
        return {"mensaje": f"La película {titulo} no cumple con la condición de tener al menos 2000 valoraciones."}
    
    return {"mensaje": f"La película {titulo} fue estrenada en el año {anio_estreno}. La misma cuenta con un total de {cantidad_votos} valoraciones, con un promedio de {promedio_votos}"}

@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    """
    Se ingresa el nombre de un actor. Devuelve la cantidad de películas en las que ha participado, el retorno total y el promedio de retorno.
    """
    nombre_actor = nombre_actor.lower()
    
    # Filtrar las filas del DataFrame de créditos donde el actor esté presente
    actores_filtro = credits_df['cast'].apply(lambda x: nombre_actor in x.lower() if isinstance(x, str) else False)
    peliculas_actor = credits_df[actores_filtro]
    
    if peliculas_actor.empty:
        return {"error": "No se encontró un actor con ese nombre."}
    
    # Obtener los IDs de las películas en las que ha participado el actor
    movie_ids = peliculas_actor['id'].tolist()
    
    # Filtrar el DataFrame de películas por los IDs obtenidos
    peliculas_participadas = movies_df[movies_df['id'].isin(movie_ids)]
    
    # Calcular la cantidad de películas, el retorno total y el promedio de retorno
    cantidad_peliculas = peliculas_participadas.shape[0]
    retorno_total = peliculas_participadas['return'].sum()
    promedio_retorno = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0
    
    return {"mensaje": f"El actor {nombre_actor} ha participado de {cantidad_peliculas} cantidad de filmaciones, el mismo ha conseguido un retorno de {retorno_total} con un promedio de {promedio_retorno} por filmación"}

@app.get("/get_director/{nombre_director}")
def get_director(nombre_director: str):
    """
    Se ingresa el nombre de un director. Devuelve la cantidad de películas, el retorno total y detalles de cada película (nombre, fecha de lanzamiento, retorno, costo y ganancia).
    """
    nombre_director = nombre_director.lower()
    
    # Filtrar las filas del DataFrame de créditos donde el director esté presente
    directores_filtro = credits_df['crew'].apply(lambda x: nombre_director in x.lower() if isinstance(x, str) else False)
    peliculas_director = credits_df[directores_filtro]
    
    if peliculas_director.empty:
        return {"error": "No se encontró un director con ese nombre."}
    
    # Obtener los IDs de las películas dirigidas por el director
    movie_ids = peliculas_director['id'].tolist()
    
    # Filtrar el DataFrame de películas por los IDs obtenidos
    peliculas_dirigidas = movies_df[movies_df['id'].isin(movie_ids)]
    
    # Calcular el retorno total
    retorno_total = peliculas_dirigidas['return'].sum()
    
    # Obtener detalles de cada película
    peliculas_detalles = []
    for _, pelicula in peliculas_dirigidas.iterrows():
        detalles = {
            "titulo": pelicula['title'],
            "fecha_lanzamiento": pelicula['release_date'],
            "retorno": pelicula['return'],
            "costo": pelicula['budget'],
            "ganancia": pelicula['revenue']
        }
        peliculas_detalles.append(detalles)
    
    return {
        "mensaje": f"El director {nombre_director} ha dirigido {len(peliculas_dirigidas)} películas con un retorno total de {retorno_total}",
        "peliculas": peliculas_detalles
    }
