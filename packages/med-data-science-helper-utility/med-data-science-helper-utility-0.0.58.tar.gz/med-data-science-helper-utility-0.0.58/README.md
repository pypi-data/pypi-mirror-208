med-data-science-helper
==============================

 <h2>1. Organización del proyecto </h2>

    ├── README.md                   <- README principal para los desarrolladores usando este proyecto.
    ├── config                      <- Archivos de configuración.
    ├── data
    │   ├── external                <- Datos de terceras fuentes.
    │   ├── interim                 <- Datos intermedios que ya han sido transformados.
    │   ├── processed               <- Datos en forma final, listo para modelamiento.
    │   └── raw                     <- Datos originales, datos inmutable sin ninguna transformación.
    │
    ├── docs                        <- Documentación del proyecto, ver detalles.
    │
    ├── models                      <- Modelos entrenados y serializados, predicción de los modelos y resúmenes.
    │
    ├── references                  <- Diccionarios de datos, manuales y todos material que explique los datos.
    │
    ├── reports                     <- Análisis generado puede ser como HTML, PDF, LaTex, etc.
    │   └── figures                 <- Gráficos y figuras generados usados en los reports.
    │
    ├── med_data_science_helper     <- Carpeta principal para el uso del proyecto donde se encuentran los códigos.
    │   ├── __init__.py                 <- Convierte al folder en un modulo de Python.
    │   │
    │   ├── helper_acces_db.py          <- Exploración inicial para entender el negocio.
    │   │
    │   ├── helper_common.py            <- Exploración para entender los datos y sus disponibilidad.
    │   │
    │   ├── helper_constantes.py        <- Seleccionar, ordenar, agrupar, remover, etc. los datos para alcanzar los 
    │   │
    │   ├── helper_integracion.py       <- Scripts para generación del modelo y afinamiento de parámetros.
    │   │
    │   ├── helper_siagie_kpi_old.py    <- Scripts para evaluación de resultados establecidos al inicio del proyecto.
    │   │
    │   ├── helper_siagie_kpi.py        <- Scripts para evaluación de resultados establecidos al inicio del proyecto.
    │   │
    │   └── helper_terceros_kpi.py      <- Scripts para el despliegue y pase a producción.
    │   
    ├── enviroment.yml             <- Listado de los paquetes necesarios para reproducir el entorno de análisis.
    │
    ├── 00.create_env.bat          <- Ejecutable para crear el entorno virtual con los parámetros del archivo "enviroment.yml".
    │
    └── 01.update_enviroment.bat   <- Ejecutable para actualizar el archivo "enviroment.yml" antes de ser compartido.

--------
<h2>2. med-data-science-helper documentacion</h2>



