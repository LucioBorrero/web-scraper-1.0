import requests
from bs4 import BeautifulSoup
import mysql.connector
import json
import logging
import os

# Configuración de logging
logging.basicConfig(filename='scraper.log', level=logging.DEBUG)

# Obtener la ruta del directorio actual
current_directory = os.path.dirname(os.path.realpath(__file__))

# Unir la ruta del directorio actual con la ruta del archivo de configuración
config_file_path = os.path.join(current_directory, 'config', 'config.json')

print(f"Current working directory: {current_directory}")
print(f"Config file path: {config_file_path}")

# Cargar configuraciones desde el archivo
try:
    with open(config_file_path) as config_file:
        config = json.load(config_file)
    print("Configuración cargada correctamente.")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{config_file_path}'.")
    config = {}  # Puedes proporcionar un diccionario vacío o manejar la falta de configuración según sea necesario

print("Configuración actual:", config)

# Configuración de MySQL
mysql_config = config.get('mysql', {})  # Obtén el diccionario 'mysql' o un diccionario vacío si no existe

def create_database_connection(config):
    return mysql.connector.connect(**config)

def close_database_connection(connection):
    connection.close()

def store_data_in_database(connection, data):
    cursor = connection.cursor()
    insert_query = "INSERT INTO datos (titulo, descripcion) VALUES (%s, %s)"
    cursor.execute(insert_query, data)
    connection.commit()
    cursor.close()

# Función para extraer datos y almacenarlos en MySQL
def scrape_and_store_data():
    # URL del sitio web a raspar
    url = config.get('url', '')  # Obtén la URL o una cadena vacía si no existe
    connection = None  # Inicializa connection como None

    try:
        # Realizar la solicitud HTTP
        response = requests.get(url)
        
        if response.status_code == 200:
            # Analizar el contenido HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer datos
            titulo_element = soup.find('h1')
            if titulo_element:
                titulo = titulo_element.text.strip()
            else:
                titulo = "No se encontró un título"

            descripcion_element = soup.find('p')
            if descripcion_element:
                descripcion = descripcion_element.text.strip()
            else:
                descripcion = "No se encontró una descripción"

            # Crear conexión a la base de datos
            connection = create_database_connection(mysql_config)

            # Almacenar en MySQL utilizando funciones específicas
            store_data_in_database(connection, (titulo, descripcion))

            logging.info("Datos almacenados con éxito.")
        else:
            logging.error(f"Error al realizar la solicitud HTTP. Código de estado: {response.status_code}")
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
    finally:
        # Cerrar la conexión a la base de datos si existe
        if connection:
            close_database_connection(connection)

# Ejecutar la función de raspado y almacenamiento
scrape_and_store_data()
