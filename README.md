---
title: Light QGis Repo
tags: studies, programming, python, django, QGis
use: Project, Repository
languages: Python
dependences: Django, QGis
---

> [!NOTE]
> This repository is based in three different implementations, I've built using the Django Framework only because I'm more familiar with it, here are the references:
> - [QGIS-Django](https://github.com/qgis/QGIS-Django/tree/master)
> - [qgis-plugins-xml](https://github.com/planetfederal/qgis-plugins-xml)
> - [phpQGISrepository](https://gitlab.com/GIS-projects/phpQGISrepository)
___

> I'll add more informations, but for now, just focused on the main tasks (see the `TODO.md` file)

## File Sctructures

Example Plugin Structure
```bash
ExamplePlugin
$ tree .
.
├── __init__.py
├── example_plugin.py
├── example_plugin_dialog.py
├── example_plugin_dialog_base.ui
├── icon.png
├── metadata.txt
├── resources.py
├── resources.qrc
└── resources3.py
```

This Project Structure
```bash
BASE_DIR
├───core
│   └───__pycache__
└───qgs_plugins
    ├───migrations
    │   └───__pycache__
    ├───plugins
    ├───templates
    └───__pycache__
```