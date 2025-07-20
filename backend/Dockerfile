# Usar una imagen oficial de Python
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY backend/ .

# Make startup script executable
RUN chmod +x start.sh

# Variables de entorno para producción
ENV FLASK_ENV=production
ENV PORT=5000

# Exponer el puerto por defecto
EXPOSE 5000

# Comando para correr la app usando el script de inicio
CMD ["./start.sh"] 