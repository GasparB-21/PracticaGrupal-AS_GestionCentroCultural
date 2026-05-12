# PracticaGrupal-AS_GestionCentroCultural
# Plataforma de Gestión para un Centro Cultural

Aplicación web desarrollada con **Django** para la gestión de actividades, usuarios inscritos, monitores y salas de un centro cultural.

El proyecto permite realizar operaciones CRUD sobre las principales entidades del sistema, gestionar inscripciones de usuarios en actividades, asignar monitores, controlar salas principales y secundarias, y aplicar reglas básicas de dominio como el control de plazas disponibles o la prevención de solapamientos de salas.

## Tecnologías utilizadas

- Python
- Django
- SQLite
- HTML
- CSS
- Bootstrap

## Funcionalidades principales

- Gestión de actividades.
- Gestión de usuarios inscritos.
- Gestión de monitores.
- Gestión de salas.
- Inscripción y cancelación de usuarios en actividades.
- Filtros de búsqueda por tipo de actividad, monitor o actividad asociada.
- Control de plazas disponibles.
- Validación de relaciones y restricciones del dominio.
- Tests para comprobar el correcto funcionamiento de los modelos y reglas de negocio.

## Arquitectura

La aplicación sigue la estructura habitual de un proyecto Django, basada en el patrón **MVT**:

- **Models**: definición de entidades y relaciones.
- **Views**: procesamiento de peticiones y lógica de aplicación.
- **Templates**: renderizado de la interfaz web.
- **Forms**: validación y gestión de formularios.

Además, dentro de la carpeta `documentacion/` se puede encontrar documentación adicional sobre la aplicación, su diseño arquitectónico y los diagramas utilizados para justificar la solución.

## Instalación y ejecución

Clonar el repositorio:

```bash
git clone https://github.com/GasparB-21/PracticaGrupal-AS_GestionCentroCultural.git
```

Entrar en la carpeta del proyecto:

```bash
cd PracticaGrupal-AS_GestionCentroCultural
```

Crear y activar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Aplicar las migraciones:

```bash
python manage.py migrate
```

Ejecutar el servidor de desarrollo:

```bash
python manage.py runserver
```

Acceder desde el navegador:

- http://127.0.0.1:8000/home/

## Tests

Para ejecutar los tests del proyecto:

```bash
python manage.py test
```

Los tests comprueban las principales relaciones entre entidades y reglas de dominio, como inscripciones, plazas disponibles, asignación de monitores, salas principales y secundarias, y restricciones de unicidad.

## ESTADO DEL PROYECTO
Proyecto académico desarrollado como práctica final para la asignatura de *Arquitectura del Software*.

