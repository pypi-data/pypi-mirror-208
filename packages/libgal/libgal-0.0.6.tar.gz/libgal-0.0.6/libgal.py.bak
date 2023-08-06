# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 15:22:35 2022

@author: Jean M. Gonzalez M.
@Legajo: L1000310
@version: 1.0
@Description: Se utilizará como librería que contendrá procesos comunes para desarrolladores del Banco Galicia
@last_update: 2022-03-25
"""


try:
    
    import logging #Libreria para logs
    import os
    from pathlib import Path
    
    #Selenium
    from selenium import webdriver
    from selenium.webdriver.firefox.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.select import Select
        
    from bs4 import BeautifulSoup

    #Teradata
    import teradatasql
    
except ImportError as imp_err:
    # Freno ejecucion y devuelvo codigo de error
    raise ImportError(f"Error al importar libreria: {imp_err}")

def variables_entorno(path_env_file=Path(os.path.dirname(__file__)) / '.env'):

    """
    Descripción: Toma las variables de entorno del archivo .env o del SO
    Parámetro:
    - path_env_file (String): 
    """
    
    try:
        from dotenv import load_dotenv
        load_dotenv(path_env_file)
    except:
        print("Únicamente para pruebas en entorno local será necesario instalar la libreria dotenv mediante la siguiente instrucción: pip install python-dotenv")
        pass
    
    return dict(os.environ)
    
    
def logger(format_output="JSON", app_name=__name__):
    
    """
    Descripción: Crea un nuevo logger 
    Parámetro:
    - format_output (String): Tipo de Salida del Log (JSON, CSV)
    - app_name (String): Nombre de la aplicación para el log
    """
    
    
    # Create a custom logger
    logger = logging.getLogger(app_name)
    
    ##Cierra las conexiones de logueo activos Handler
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
        
    logger.setLevel(logging.INFO)
    
    # Create handlers
    c_handler = logging.StreamHandler()
    
    # Create formatters and add it to handlers
    
    if format_output.lower()=='json':
        c_format = logging.Formatter("{'time':'%(asctime)s', 'name': '%(name)s','level': '%(levelname)s', 'message': '%(message)s'}", datefmt='%m/%d/%Y %I:%M:%S %p')
    elif format_output.lower()=='csv':
        c_format= logging.Formatter('%(asctime)s;%(name)s;%(levelname)s;%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    else:
        raise Exception("Tipo de formato de Log inválido. Formatos soportados (JSON y CSV).")
        
    c_handler.setFormatter(c_format)
    
    # Add handlers to the logger
    logger.addHandler(c_handler)
    
    return logger

def shutdown_logger():
    
    """
    Descripción: Cierra el log 
    
    """
    
    if logger:
        logging.shutdown()
        
def firefox(webdriver_path, browser_path, url, hidden=False):

    """
    Descripción: Crea un cliente web para pruebas y automatizaciones 
    Parámetro:
    - format_output (String): Tipo de Salida del Log (JSON, CSV)
    - app_name (String): Nombre de la aplicación para el log
    """
    
    options = webdriver.FirefoxOptions()
    options.binary_location = browser_path
    options.headless = hidden

    driver_service=Service(webdriver_path)

    web_browser = webdriver.Firefox(service=driver_service, options=options)
    web_browser.get(url)
    
    return web_browser
    
def html_parser(html):

    """
    Descripción: Parsea el código HTML para encontrar etiquetas específicas
    Parámetro:
    - html (String): código html a parsear
    """
    
    soup = BeautifulSoup(html, 'html.parser')
    
    return soup

def teradata(host,user,password):
    
    # Funcion que permite la conexion hacia el sgdb
    
    """
    Descripción: Permite la conexion hacia el sgdb de Teradata
    Parámetro:
    - host (String): uri del servidor de base de datos
    - user (String): Usuario que autentica la conexión a la base de datos
    - password (String): Contraseña para la autenticación de la connexión de la base de datos
    """
    
    td_connection = teradatasql.connect(host=host, user=user, password=password,logmech="LDAP")

    return td_connection
