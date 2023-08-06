## Commons 

Este repositorio de código se crea para implementar la microservicio `Commons` de la infraestructura de Klopp.

A continuación se proporciona una descripción de la estructura de los archivos y directorios más importantes:

## Template

- `setup.py`
- [`Notebook`]
- `test`
- `requirements.txt`
    - Blibliotecas necesarias para reproducir el entorno

## Estructura del proyecto

```
├── LICENSE
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── docs               <- A default Sphinx project; see sphinx-doc.org for details
├── models             <- Trained and serialized models, model predictions, or model summaries
├── experiments 
│   ├── notebooks      <- Jupyter notebooks. Naming convention is a number (for ordering),
│   │    └── mlflow    <- Metretrics and model management 
│   ├── references     <- Data dictionaries, manuals, and all other explanatory materials.
│   ├── processed      <- The final, canonical data sets for modeling. 
│   └── data  
│     ├── external       <- Data from third party sources.
│     ├── interim        <- Intermediate data that has been transformed.
│     ├── processed      <- The final, canonical data sets for modeling.
│     └── raw            <- The original, immutable data dump.
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
├── setup.py           <- Run this project 
├── pipeline           <- Source pipeline for load, preprocessing, training and test 
│   ├── __init__.py    <- Makes src a Python module
│   ├── data           <- Scripts to download or generate data
│   │   └── make_dataset.py
│   ├── features       <- Scripts to turn raw data into features for modeling
│   │   └── build_features.py
│   ├── models         <- Scripts to train models and then use trained models to make
│   │   │                 predictions
│   │   ├── predict_model.py
│   │   └── train_model.py
│   └── visualization  <- Scripts to create exploratory and results oriented visualizations
│       └── visualize.py
├── categorization     <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   ├── categorization.py <- class and method run() for app running 
│   ├── classifier.py   <- Class for model ML
│   ├── consumer.py  <- class for Kafka consumer 
│   ├── controller_dynamo_db.py <- class for management CRUD 
│   ├── controller_ml_fow.py   <- Class for management models
│   ├── controller_posgrest_db.py  <- class for managemen CRUD  
│   ├── producer.py <- class for Kafka producer
│   ├── nicknames.py   <- Class 
│   ├── merchantnames.py  <- class 
│   └── logs       <- folder for logs files 
└── tox.ini            <- tox file with settings for running tox;(automate and standardize testing)
```


## Reproducir proyectos 

## Software necesario

El proyecto se desarrollo con los siguientes requisitos a primer nivel :

Python 3.10.4

Se recomienda a nivel de desarrollo utilizar un entorno virtual administrado por conda.

`conda create -n categorization python=3.10.4` 

Use sólo pip como gestor de paquetería después de crear en entorno virtual con conda.
Los requisitos de las bibliotecas necesarias se pueden pasar a pip a través del archivo `requiremets.txt`

pip install -r requirements.txt

Ver pagína de [python](https://requirements-txt.readthedocs.io/en/latest/#:~:text=txt%20installing%20them%20using%20pip.&text=The%20installation%20process%20include%20only,That's%20it.&text=Customize%20it%20the%20way%20you,allow%20or%20disallow%20automated%20requirements)


Otra opcíon es utilizar un docker oficial de python con la versión cómo  3.10 como mínima. Esta es sólo si utilizas Linux o Windows como sistema operativo, existe problemas de compatibilidad para MacBooks M1


[Docker Hub de Python](https://hub.docker.com/_/python)

- Para el entorno local se utiliza [Jupyer Notebook] como entorno de experimentación
- Para administrar los modelos de ML se utiliza [MLFlow]() con Posgrestdb
- Como gestor de bases de datos relacional se utiliza PosgrestDB
- Para almacenar información no estructurada se utiliza DynamoDB
- Para versionamiento de los dataset se utiliza [DVC]
- Para autoformatting se utilizan los paquetes [`Back`](), [Flake8]()  y [autopep8] () 
- Para pruebas unitarias se utiliza el paquete estándar de python `unittest` 