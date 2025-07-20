# Usar una imagen oficial de Python
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Variables de entorno para producción
ENV FLASK_ENV=production
ENV PORT=5000

# Exponer el puerto por defecto de Flask
EXPOSE 5000

# Comando para correr la app con gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--timeout", "120"] 