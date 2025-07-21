# Usar una imagen oficial de Python
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar el cache de Docker
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/ .

# Exponer el puerto de la aplicación
EXPOSE 8000

# Comando para correr la app
CMD ["python", "run.py"] 