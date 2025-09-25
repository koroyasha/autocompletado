Guía Completa de Instalación, Ejecución, Actualización y Solución de Errores del Sistema en Django

Este documento explica paso a paso cómo descargar, instalar, ejecutar y actualizar el sistema desarrollado en Django, así como resolver los errores más comunes que podrían surgir.

Requisitos previos
Antes de comenzar, asegúrate de tener instalados los siguientes programas:

Requisito Descripción Enlace de descarga Python 3.10 o superior Lenguaje de programación necesario para ejecutar Django. https://www.python.org/downloads/

Git Para clonar y actualizar el repositorio. https://git-scm.com/downloads

pipenv Para crear y administrar el entorno virtual. Se instala con: pip install pipenv 2. Descargar o actualizar el proyecto Caso A → Si aún no has descargado el proyecto

Abre una terminal o consola de comandos.

Clona el repositorio desde GitHub:

git clone https://github.com/koroyasha/practica1.git

Ingresa al directorio del proyecto:

cd S:/universidad/noveno/lenguaje_natural/sistema_pln

Caso B → Si ya descargaste el proyecto y quieres la última versión

Si ya tienes el proyecto en tu computadora, no lo vuelvas a clonar. Solo actualízalo:

git pull origin main

🔹 Ejemplo real:

cd S:/universidad/noveno/lenguaje_natural/sistema_pln git pull origin main

Esto descargará solo los cambios recientes.

⚠️ Importante: Si modificaste archivos del proyecto y no quieres perder tus cambios, crea primero una copia de seguridad.

Archivos importantes para la instalación Archivo Función Pipfile Lista de librerías necesarias para el proyecto. Pipfile.lock Versiones exactas de las librerías para garantizar compatibilidad.
⚠️ No borres, edites ni muevas estos archivos, ya que pipenv los usa para instalar todo automáticamente.

Crear y activar el entorno virtual
Instalar dependencias del proyecto:

pipenv install

Activar el entorno virtual:

pipenv shell

(Opcional) Actualizar dependencias:

pipenv update

Configurar el entorno de Django
Si necesitas cambiar idioma o zona horaria, edita el archivo:

proyecto/settings.py

Verifica que tenga estas líneas:

LANGUAGE_CODE = 'es' TIME_ZONE = 'America/Mexico_City' USE_I18N = True USE_TZ = True

Preparar la base de datos
Ejecuta estos comandos para configurar la base de datos local:

python manage.py makemigrations python manage.py migrate

Crear un superusuario
Si deseas acceder al panel de administración:

python manage.py createsuperuser

Sigue las instrucciones y define usuario, correo y contraseña.

Ejecutar el servidor
Para iniciar el servidor local:

python manage.py runserver

Abre tu navegador y visita:

http://127.0.0.1:8000

Uso del sistema 9.1. Subir un archivo
En la página principal, selecciona un archivo .txt y presiona Subir.

9.2. Generar el histograma

Haz clic en Generar histograma.

Se mostrará una tabla con la frecuencia de cada palabra.

Acceso al panel de administración
Si creaste un superusuario, puedes acceder a:

http://127.0.0.1:8000/admin

Detener el servidor y salir del entorno
Detener el servidor:

CTRL + C

Salir del entorno virtual:

exit

Resumen de comandos clave Acción Comando Clonar proyecto git clone Actualizar proyecto git pull origin main Crear entorno virtual pipenv install Activar entorno pipenv shell Migrar base de datos python manage.py migrate Crear superusuario python manage.py createsuperuser Iniciar servidor python manage.py runserver Salir del entorno exit
Solución de errores comunes
Aquí te muestro problemas frecuentes y cómo solucionarlos:

❌ Error 1 → “pipenv no se reconoce como un comando”

Causa: pipenv no está instalado o no está en la variable PATH. Solución:

pip install pipenv

Si el error persiste, prueba:

python -m pip install pipenv

❌ Error 2 → “No se puede activar el entorno virtual”

Causa: Intentas ejecutar pipenv shell fuera de la carpeta del proyecto. Solución:

cd ruta/del/proyecto pipenv shell

❌ Error 3 → “El módulo Django no está instalado”

Causa: No se instalaron las dependencias correctamente. Solución:

pipenv install

Si sigue fallando:

pipenv install django

❌ Error 4 → “Permission denied” o problemas al actualizar

Causa: No tienes permisos para escribir en la carpeta. Solución en Windows:

Abre CMD o Git Bash como Administrador.

Repite el comando git pull.

❌ Error 5 → “Pipfile.lock no coincide con el Pipfile”

Causa: El proyecto actualizó dependencias y tu versión local está desactualizada. Solución:

pipenv install --ignore-pipfile

O bien:

pipenv update

❌ Error 6 → “El puerto 8000 ya está en uso”

Causa: Hay otro servidor corriendo. Solución:

python manage.py runserver 8001

Esto iniciará el proyecto en:

http://127.0.0.1:8001

❌ Error 7 → Problemas con git pull

Causa: Hiciste cambios locales que chocan con la versión remota. Solución rápida:

git stash git pull origin main git stash pop

Recomendaciones finales
✅ Usa siempre pipenv para manejar dependencias. ✅ Antes de actualizar el proyecto, guarda tus cambios. ✅ Si algo falla, borra la carpeta .venv y reinstala todo:

pipenv --rm pipenv install
