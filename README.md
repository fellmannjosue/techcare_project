Guía para el Despliegue y Gestión del Proyecto Django

- Acceso al Servidor mediante SSH
  - ssh admin2@192.168.10.6
  - Inicie sesión de forma remota en el servidor utilizando el usuario admin2.

- Obtener Permisos de Root
  - sudo su
  - Adquiera privilegios de administrador (root) para ejecutar comandos del sistema.

- Recopilar Archivos Estáticos
  - python manage.py collectstatic --noinput
  - Transfiera todos los recursos estáticos (CSS, JS, imágenes) al directorio configurado sin solicitar confirmación.

- Reiniciar Apache
  - sudo systemctl restart apache2
  - Reinicie el servidor web Apache para que reconozca los nuevos archivos estáticos y cambios de configuración.

- Acceder al Directorio del Proyecto
  - cd techcare_project
  - Ingrese al directorio raíz de su proyecto Django.

- Activar el Entorno Virtual
  - source venv/bin/activate
  - Acceda al entorno virtual para utilizar las dependencias aisladas del proyecto.

- Navegar a la Carpeta de Pruebas y Luego a la de Producción
  - cd django_test
  - cd system_proyect
  - Dirígete primero al subproyecto de pruebas y luego al despliegue principal.

- Iniciar el Servidor de Desarrollo
  - python manage.py runserver 192.168.10.6:8000
  - Lance el servidor local de Django en la IP y puerto especificados para pruebas en red.

- Abrir la Consola Interactiva de Django
  - python manage.py shell
  - Inicie una shell de Python con todo el contexto de su proyecto cargado (modelos, configuraciones, etc.).

- Generar Archivos de Migración
  - python manage.py makemigrations
  - Identifique cambios en los modelos y prepare las migraciones necesarias.

- Ejecutar Migraciones en la Base de Datos
  - python manage.py migrate
  - Realice las migraciones pendientes, creando o modificando tablas de acuerdo a sus modelos.

- Crear un Superusuario
  - python manage.py createsuperuser
  - Establezca un usuario administrador que podrá acceder al panel de administración de Django.
