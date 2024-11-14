from fastapi import FastAPI
import pandas as pd

# Actualizar la ruta de los archivos CSV
movies_path = '/app/movies_dataset_transformed.csv'
credits_path = '/app/cleaned_credits.csv'
    
# Cargar los archivos CSV
movies_df = pd.read_csv(movies_path, dtype={
    'budget': 'float64',
    'revenue': 'float64',
    'release_year': 'Int64',
    'return': 'float64'
}, low_memory=False)

credits_df = pd.read_csv(credits_path, dtype={
    'cast_name': 'string',
    'crew_name': 'string',
    'crew_job': 'string',
    'movie_title': 'string'
}, low_memory=False)

# Initialize FastAPI app
app = FastAPI()

# 1. Endpoint: Cantidad de filmaciones por mes
@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes: str):
    # Diccionario para convertir nombres de meses en español a números
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    mes = mes.lower()
    if mes not in meses:
        return {"error": "Mes no válido. Asegúrese de ingresar el mes en español."}
    
    mes_numero = meses[mes]
    cantidad = movies_df[pd.to_datetime(movies_df['release_date'], errors='coerce').dt.month == mes_numero].shape[0]
    
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en el mes de {mes}"}

# 2. Endpoint: Cantidad de filmaciones por día
@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia: str):
    # Diccionario para convertir nombres de días en español a números
    dias = {
        'lunes': 0, 'martes': 1, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sábado': 5, 'domingo': 6
    }
    
    dia = dia.lower()
    if dia not in dias:
        return {"error": "Día no válido. Asegúrese de ingresar el día en español."}
    
    dia_numero = dias[dia]
    cantidad = movies_df[pd.to_datetime(movies_df['release_date'], errors='coerce').dt.dayofweek == dia_numero].shape[0]
    
    return {"mensaje": f"{cantidad} cantidad de películas fueron estrenadas en los días {dia}"}

# 3. Endpoint: Score de una película por título
@app.get('/score_titulo/{titulo_de_la_filmacion}')
def score_titulo(titulo_de_la_filmacion: str):
    resultado = movies_df[movies_df['title'].str.lower() == titulo_de_la_filmacion.lower()]
    if resultado.empty:
        return {"error": "No se encontró la filmación con ese título."}
    
    titulo = resultado.iloc[0]['title']
    anio = resultado.iloc[0]['release_year']
    score = resultado.iloc[0]['vote_average']
    
    return {"mensaje": f"La película {titulo} fue estrenada en el año {anio} con un score/popularidad de {score}"}

# 4. Endpoint: Votos de una película por título
@app.get('/votos_titulo/{titulo_de_la_filmacion}')
def votos_titulo(titulo_de_la_filmacion: str):
    resultado = movies_df[movies_df['title'].str.lower() == titulo_de_la_filmacion.lower()]
    if resultado.empty:
        return {"error": "No se encontró la filmación con ese título."}
    
    votos = resultado.iloc[0]['vote_count']
    promedio_votos = resultado.iloc[0]['vote_average']
    titulo = resultado.iloc[0]['title']
    anio = resultado.iloc[0]['release_year']
    
    if votos < 2000:
        return {"mensaje": f"La película {titulo} fue estrenada en el año {anio}. No cumple con la condición de tener al menos 2000 valoraciones."}
    
    return {"mensaje": f"La película {titulo} fue estrenada en el año {anio}. La misma cuenta con un total de {votos} valoraciones, con un promedio de {promedio_votos}"}

# 5. Endpoint: Información de un actor
@app.get('/get_actor/{nombre_actor}')
def get_actor(nombre_actor: str):
    actor_data = credits_df[credits_df['cast_name'].str.contains(nombre_actor, case=False, na=False)]
    if actor_data.empty:
        return {"error": "No se encontró información sobre el actor."}
    
    peliculas = actor_data['movie_title'].unique() if 'movie_title' in actor_data.columns else []
    cantidad_peliculas = len(peliculas)
    retorno_total = movies_df[movies_df['title'].isin(peliculas)]['return'].sum()
    promedio_retorno = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0
    
    return {"mensaje": f"El actor {nombre_actor} ha participado de {cantidad_peliculas} cantidad de filmaciones, el mismo ha conseguido un retorno de {retorno_total:.2f} con un promedio de {promedio_retorno:.2f} por filmación"}

# 6. Endpoint: Información de un director
@app.get('/get_director/{nombre_director}')
def get_director(nombre_director: str):
    director_data = credits_df[(credits_df['crew_name'].str.contains(nombre_director, case=False, na=False)) & (credits_df['crew_job'] == 'Director')]
    if director_data.empty:
        return {"error": "No se encontró información sobre el director."}
    
    peliculas = director_data['movie_title'].unique() if 'movie_title' in director_data.columns else []
    peliculas_info = []
    for pelicula in peliculas:
        pelicula_data = movies_df[movies_df['title'].str.lower() == pelicula.lower()]
        if not pelicula_data.empty:
            titulo = pelicula_data.iloc[0]['title']
            fecha_lanzamiento = pelicula_data.iloc[0]['release_date']
            retorno = pelicula_data.iloc[0]['return']
            budget = pelicula_data.iloc[0]['budget']
            revenue = pelicula_data.iloc[0]['revenue']
            peliculas_info.append({
                "titulo": titulo,
                "fecha_lanzamiento": fecha_lanzamiento,
                "retorno": retorno,
                "costo": budget,
                "ganancia": revenue
            })
    
    return {"director": nombre_director, "peliculas": peliculas_info}

# Main script to run FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_movies_api:app", host="0.0.0.0", port=8000, reload=True)