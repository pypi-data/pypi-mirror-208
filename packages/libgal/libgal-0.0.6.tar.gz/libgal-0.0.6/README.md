
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- PROJECT LOGO -->

<div align="center">

  <h1 align="center">LibGal</h1>

  <p align="center">
    Librería para agilizar el desarrollo de nuestros programadores en el Banco Galicia
    <br />
    <br />
    <a href="https://github.com/Banco-Galicia/libgal"><strong>Explorar el proyecto»</strong></a>
    <br />
    <br />
    <a href="https://github.com/Banco-Galicia/libgal/issues">Reportar error</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Tabla de Contenidos</summary>
  <ol>
    <li>
      <a href="#descripción-general">Descripción General</a>
    </li>
    <li>
      <a href="#instalalación">Instalación</a>
    </li>
    <li>
      <a href="#funcionalidades">Funcionalidades</a>
      <ul>
        <li><a href="#variables-de-entorno">Variables de Entorno</a></li>
        <li><a href="#registro-de-logs">Registro de Logs</a></li>
        <li><a href="#selenium-web-browser-firefox">Selenium Web Browser Firefox</a></li>
        <li><a href="#teradata">Teradata</a></li>
      </ul>
    </li>
    <li><a href="#contacto">Contacto</a></li>
  </ol>
</details>

<br/>

<!-- ABOUT THE LIBRARY -->

## **Descripción General** 
<br>
Esta librería python fue desarrollada desde el CoE Data Driven del Banco Galicia con la finalidad de agilizar el desarrollo de aplicaciones con funciones configurables minimizando de esta forma el código de nuestra aplicación permitiendonos centrarnos en la funcionalidad principal de la aplicación a desarrollar.

<p align="right">(<a href="#readme-top">Ir arriba</a>)</p>

<!-- INSTALACIÓN -->
## **Instalación**
<br>

La instación de esta librería se hace mediante siguiente sentencia:

```python
pip install libgal
```

<p align="right">(<a href="#readme-top">Ir arriba</a>)</p>

<!-- FUNCIONALIDADES -->
## **Funcionalidades**
<br>
Para hacer uso de las diferentes funcionalidades de esta librería basta con importar la misma en nuestro código con la siguiente sentencia:

<br>

```python
import libgal
```

<br>

Una vez importada la librería solo nos queda instanciar en una variable la función que necesitemos tal como se muestra a continuación.

<br>

```python
browser=libgal.variables_entorno()
```

<!-- FUNCIONALIDAD - Variables de Entorno -->
### **Variables de Entorno**

<br>

Para poder usar las variables de entorno de forma local con esta librería será necesario crear un archivo de texto cuyo nombre y extensión será “.env”. Por defecto esta librería tomará el archivo “.env” que se encuentra ubicado en la raíz de nuestro ejecutable python. Dentro de este mismo archivo “.env” podemos especificar todas las variables secrets y configmap que utilizará nuestra aplicación, tal como se muestra en el siguiente ejemplo:

<br>

```sh
#SECRETS
USERNAME = usuario@correo.com
PASSWORD = contraseña

#CONFIGMAP
API_PREDICT=https://url.com/predict
API_AUDIENCIAS=https://url.com/audiencias
CANT_POST=10 #Cantidad de últimos posts a descargar
```

Es importante mencionar que al momento de desplegar nuestra aplicación no se debe subir este archivo “.env” ya que solo es para ejecuciones y pruebas en modo local que simula estar en openshift.  

Ahora bien, para poder usar estas variables dentro de nuestro código solo será necesario importar la librería LIBGAL e instanciar en una variable la función VARIABLES_ENTORNO y así poder acceder a las variables de entorno mediante la misma, tal cómo se muestra en el siguiente ejemplo:  

```python
import libgal

ve=libgal.variables_entorno()

api_predict=ve['API_PREDICT']
api_audiencias=ve['API_AUDIENCIAS']
```

<br>

Nótese que para invocar los nombres de las variables es necesario escribirlas en mayúscula.

<br>

En caso de que el archivo “.env” se encuentre en otra ruta o se necesite manejar varios varios archivos “.env” para simular entornos separados como, por ejemplo: .env.desa, .env.qa, etc. En este caso será necesario indicar la ruta y nombre del archivo “.env” al instanciar la variable, tal como se muestra a continuación:

<br>

```python
ve=libgal.variables_entorno('ruta/del/archivo/.env.nombre')
```

<!-- Registro de Logs -->
### **Registro de Logs**  

<br>

Haciendo uso de esta librería no nos tenemos que preocupar por la configuración de nuestros registros logs, ya que la misma se encarga de ello mediante unos pocos pasos. Para hacer esto, solo debemos llamar la función LOGGER de la librería y asignarla a una variable para poder usar en el resto de nuestro código.

<br>

La función LOGGER consta de dos parámetros de configuración de tipo string:

<br>

*	**format_output:** *(Requerido, Tipo String)* Indica el tipo de formato para el registro log de nuestra aplicación. Por los momentos consta de dos tipos: “JSON” usado para los logs dentro del entorno Openshift y “CSV” para generar el log en una sola línea separados por coma (,).

<br>

*	**app_name:** *(Requerido, Tipo String)* En este parámetro especificaremos el nombre de nuestra aplicación. Recordemos que nuestro archivo Python principal deberá llamar APP.PY.

<br>

Para crear un registro log mediante esta función en nuestra aplicación solo debemos hacer uso de nuestra variable tipo LOGGER de forma muy similar al “print” de Python pero con un agregado adicional y es que podemos definir el nivel de Log para cada registro, tal como lo veremos en el siguiente código de ejemplo:

<br>

```python
Import libgal

log=libgal.logger(format_output="JSON", app_name="Instagram")

log.info("Esto es un registro informativo")
log.error("Esto es un registro de error")
log.warning("Esto es un registro de advertencia")
log.critical("Esto es un registro de error crítico")
log.exception("Esto es un registro de excepción")
log.log("Esto es un registro de log")
```

<p align="right">(<a href="#readme-top">ir arriba</a>)</p>



<!-- Selenium Web Browser Firefox -->
### **Selenium Web Browser Firefox**

<br>

Mediante la librería podemos hacer la invocación un Web Browser de Selenium para nuestras automatizaciones, test y/o extracciones de datos de cualquier página web. Esto se logra invocando la función Firefox de la librería e instanciándola a una variable. 

<br>

La función consta de 4 parámetros de configuración:

<br>

*	**webdriver_path:** *(Requerido, Tipo String)*  Ruta del driver geckodriver utilizado para levantar e invocar el Web Browser de Firefox.

<br>

*	**browser_path:** *(Requerido, Tipo String)* Ruta del ejecutable Firefox.exe del servidor o equipo local necesario para levantar el Web Browser.

<br>

*	**url:** *(Requerido, Tipo String)* Dirección Web con la que vamos a mediante el Web Browser.

<br>

* Hidden: (Opcional, Tipo Booleano) Indica si el Web Browser se oculta durante su ejecución. False predeterminado.

<br>

Ejemplo:

```python
import libgal

browser=libgal.firefox(webdriver_path=r"C:\webdrivers\geckodriver.exe",browser_path=r"C:\Program Files\Mozilla Firefox\firefox.exe",url="https://bolsar.info/Cauciones.php")
```
<p align="right">(<a href="#readme-top">ir arriba</a>)</p>

### **Teradata**

<br>

Para simplificar un poco las conexiones a Teradata se agregó esta nueva funcionalidad.

La misma consta de solo 3 parámetros:

*	**Host:** *(Requerido, Tipo String)* Indica el servidor de base de datos al cual nos deseamos conectar.

*	**User:** *(Requerido, Tipo String)* Usuario necesario para la conexión al servidor de base de datos.

*	**Password:** *(Requerido, Tipo String)* Contraseña con la que se autentica el usuario para poderse conectar a la base de datos.

<br>

Un ejemplo de su uso puede ser el siguiente:

```python
import libgal

con=libgal.teradata(host='servidor', user='tu_user', password='tu_password')
```

<p align="right">(<a href="#readme-top">Ir arriba</a>)</p>

### **HTML_Parser**

<br>

Está función hacer búsquedas rápidas de etiquetas y textos dentro de un código HTML mediante funciones de Beautiful Soup. Para esto solo será necesario instanciar la función en una variable pasándole por parámetro un string o variable tipo string contentiva del código HTML a trabajar, tal cómo se muestra a continuación:

<br>

```python
import libgal

html='<html><head></head><body>Sacré bleu!</body></html>'

soup=libgal.html_parser(html)
```

<p align="right">(<a href="#readme-top">Ir arriba</a>)</p>

<!-- CONTACTO-->
## Contacto

<br>

Jean González - [@jeanmgonzalez](https://github.com/jeanmgonzalez)

[![LinkedIn][linkedin-shield]][linkedin-url-jean]

<br>

Julian Girandez - [@julgiraldez](https://github.com/JuLGiraldez)

[![LinkedIn][linkedin-shield]][linkedin-url-juli]

<br>

Link del proyecto: [https://github.com/Banco-Galicia/libgal](https://github.com/Banco-Galicia/libgal)

<br>


<p align="right">(<a href="#readme-top">ir arriba</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/Banco-Galicia/libgal/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]:https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url-jean]: https://www.linkedin.com/in/bidata/
[linkedin-url-juli]: https://www.linkedin.com/in/julian-leandro-giraldez/
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 