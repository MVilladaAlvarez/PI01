# Imagen base de Python
FROM python:3.9-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY . /app

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8000 para acceder a la API
EXPOSE 8000

# Comando para ejecutar la aplicación FastAPI
CMD ["uvicorn", "fastapi_movies_api:app", "--host", "0.0.0.0", "--port", "8000"]
