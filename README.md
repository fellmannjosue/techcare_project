# TechCare Project

Este repositorio contiene un conjunto de aplicaciones Django para gestionar servicios en un centro educativo. El directorio principal `system_proyect` incluye la configuración de producción y todas las apps, mientras que `django_test` es una copia de pruebas. En `datos/` se encuentran archivos CSV y SQL para poblar la base de datos.

## Estructura general
- **system_proyect/** – Proyecto Django utilizado en despliegue.
- **django_test/** – Entorno de pruebas con un proyecto homónimo.
- **datos/** – Scripts y datos de ejemplo para alimentar las tablas.

## Aplicaciones
### Accounts
Gestión de autenticación y menú principal. Rutas relevantes:
- `/accounts/login/` – inicio de sesión.
- `/accounts/user-login/` – acceso directo a tickets.
- `/accounts/menu/` – menú principal.
- `/accounts/logout/` – cierre de sesión.

### Tickets
Permite crear tickets de soporte y notificar por correo.
- `/tickets/submit_ticket/` – formulario de creación.
- `/tickets/technician_dashboard/` – panel para técnicos.

### Inventario
Control de equipos y materiales con exportación en PDF y vistas por tipo.
- `/inventario/` – panel general y acceso por categorías.
- `/inventario/download_item_pdf/<id>/` – descarga de registros.
- `/inventario/computadoras/` – listado de computadoras.
- `/inventario/televisores/` – listado de televisores.
- `/inventario/impresoras/` – listado de impresoras.
- `/inventario/routers/` – listado de routers.
- `/inventario/datashows/` – listado de datashows.
- `/inventario/por_categoria/` – consulta unificada por categoría.
- `/inventario/registros/` – registro global de equipos.
- `/registros/qr/<tipo>/<pk>/` – código QR del registro.
- `/download/<tipo>/<pk>/` – descarga individual en PDF.

### Mantenimiento
Registro y reporte de mantenimientos.
- `/mantenimiento/` – listado y formulario unificado.
- `/mantenimiento/download/<id>/` – reporte en PDF.

### Citas (Bilingüe)
Agendamiento de citas para el departamento bilingüe.
- `/citas_billingue/user-data_bl/` – datos del usuario.
- `/citas_billingue/dashboard_bl/` – gestión de citas.

### Citas (Colegio)
Sistema similar de citas para el colegio.
- `/citas_colegio/user-data_col/` – datos del usuario.
- `/citas_colegio/dashboard_col/` – gestión de citas.

### Enfermería
Atención médica, inventario de medicamentos e historial en PDF o correo.
- `/enfermeria/` – dashboard principal.
- `/enfermeria/atencion/` – registrar atención médica.
- `/enfermeria/inventario/` – listado de medicamentos.
- `/inventario/nuevo/` – agregar medicamento.
- `/inventario/<pk>/editar/` – editar medicamento.
- `/inventario/uso/` – registrar consumo.
- `/inventario/pdf/<pk>/` – ficha en PDF.
- `/inventario/<pk>/historial/` – historial de uso.
- `/enviar-correo/<atencion_id>/` – envío de atención por correo.
- `/historial/` – consulta de historial médico.
- `/historial/data/` – datos detallados del historial.

### Sponsors
Manejo de padrinos y patrocinadores.
- `/sponsors/dashboard/` – vista principal de patrocinadores.
- Formularios de ciudades, países y registros adicionales.

### Seguridad
Control de cámaras y registros contables.
- `/seguridad/` – dashboard de seguridad.
- Rutas para inventario, contabilidad e identificación de equipos.

### Menu
Muestra un menú básico para usuarios.
- `/menu/` – menú principal tras iniciar sesión.

### Core
Incluye utilidades compartidas como `context_processors.py` para mostrar el año actual en las plantillas.

## Entorno virtual
1. Crear el entorno si no existe:
   ```bash
   python -m venv venv
   ```
2. Activarlo antes de trabajar:
   ```bash
   source venv/bin/activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r system_proyect/requirements.txt
   ```

## Variables de entorno
El archivo `.env` en la raíz define claves y credenciales utilizadas en `system_proyect/system_proyect/settings.py`. Algunos valores esperados son:
- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `MSSQL_DB_NAME`, `MSSQL_DB_USER`, `MSSQL_DB_PASSWORD`, `MSSQL_DB_HOST`, `MSSQL_DB_PORT`
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

## Guía para el Despliegue y Gestión del Proyecto Django

## Acceso al Servidor mediante SSH
  ### "ssh admin2@192.168.10.6"
  - Inicie sesión de forma remota en el servidor utilizando el usuario admin2.
## Obtener Permisos de Root
  ### "sudo su"
  - Adquiera privilegios de administrador (root) para ejecutar comandos del sistema.
## Recopilar Archivos Estáticos
  ### "python manage.py collectstatic --noinput"
  - Transfiera todos los recursos estáticos (CSS, JS, imágenes) al directorio configurado sin solicitar confirmación.
## Reiniciar Apache
  ### "sudo systemctl restart apache2"
  - Reinicie el servidor web Apache para que reconozca los nuevos archivos estáticos y cambios de configuración.
## Acceder al Directorio del Proyecto
  ### "cd techcare_project"
  - Ingrese al directorio raíz de su proyecto Django.
## Activar el Entorno Virtual
  ### "source venv/bin/activate"
  - Acceda al entorno virtual para utilizar las dependencias aisladas del proyecto.
## Navegar a la Carpeta de Pruebas y Luego a la de Producción
  ### "cd django_test"
  ### "cd system_proyect"
  - Dirígete primero al subproyecto de pruebas y luego al despliegue principal.
## Iniciar el Servidor de Desarrollo
  ### "python manage.py runserver" 
  - Lance el servidor local de Django en la IP y puerto especificados para pruebas en red.
## Abrir la Consola Interactiva de Django
  ### "python manage.py shell"
  - Inicie una shell de Python con todo el contexto de su proyecto cargado (modelos, configuraciones, etc.).
## Generar Archivos de Migración
  ### "python manage.py makemigrations"
  - Identifique cambios en los modelos y prepare las migraciones necesarias.
## Ejecutar Migraciones en la Base de Datos
  ### "python manage.py migrate"
  - Realice las migraciones pendientes, creando o modificando tablas de acuerdo a sus modelos.
## Crear un Superusuario
  ### "python manage.py createsuperuser"
  - Establezca un usuario administrador que podrá acceder al panel de administración de Django.
