# Usar una imagen oficial de Python
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto por defecto de Flask
EXPOSE 5000

# Comando para correr la app (ajusta si usas run.py o app.py)
CMD ["python", "run.py"] 