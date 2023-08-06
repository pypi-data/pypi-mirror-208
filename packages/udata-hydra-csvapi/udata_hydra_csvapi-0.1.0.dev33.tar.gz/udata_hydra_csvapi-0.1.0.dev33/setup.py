# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['udata_hydra_csvapi']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.3,<4.0.0', 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'udata-hydra-csvapi',
    'version': '0.1.0.dev33',
    'description': 'API for CSV converted by udata-hydra',
    'long_description': '# udata-hydra-csvapi\n\nThis connects to [udata-hydra](https://github.com/etalab/udata-hydra) and serves the converted CSVs as an API.\n\n## Run locally\n\nStart [udata-hydra](https://github.com/etalab/udata-hydra) via `docker compose`.\n\nLaunch this project:\n\n```shell\ndocker compose up\n```\n\nYou can now access the raw postgrest API on http://localhost:8080.\n\nNow you can launch the proxy (ie the app):\n\n```\npoetry install\npoetry run adev runserver -p8005 udata_hydra_csvapi/app.py\n```\n\nAnd query postgrest via the proxy using a `resource_id`, cf below. Test resource_id is `27d469ff-9908-4b7e-a2e0-9439bb38a395`\n\n## API\n\n### Meta informations on resource\n\n```shell\ncurl http://localhost:8005/api/resources/27d469ff-9908-4b7e-a2e0-9439bb38a395/\n```\n\n```json\n{\n  "created_at": "2023-02-11T11:44:03.875615+00:00",\n  "url": "https://data.toulouse-metropole.fr//explore/dataset/boulodromes/download?format=csv&timezone=Europe/Berlin&use_labels_for_header=false",\n  "links": [\n    {\n      "href": "/api/resources/27d469ff-9908-4b7e-a2e0-9439bb38a395/profile/",\n      "type": "GET",\n      "rel": "profile"\n    },\n    {\n      "href": "/api/resources/27d469ff-9908-4b7e-a2e0-9439bb38a395/data/",\n      "type": "GET",\n      "rel": "data"\n    }\n  ]\n}\n```\n\n### Profile (csv-detective output) for a resource\n\n```shell\ncurl http://localhost:8005/api/resources/27d469ff-9908-4b7e-a2e0-9439bb38a395/profile/\n```\n\n```json\n{\n  "profile": {\n    "header": [\n        "geo_point_2d",\n        "geo_shape",\n        "ins_nom",\n        "ins_complexe_nom_cplmt",\n        "ins_codepostal",\n        "secteur",\n        "..."\n    ]\n  },\n  "...": "..."\n}\n```\n\n### Data for a resource (ie resource API)\n\n```shell\ncurl http://localhost:8005/api/resources/27d469ff-9908-4b7e-a2e0-9439bb38a395/data/?limit=1\n```\n\n```json\n[\n  {\n    "__id": 1,\n    "geo_point_2d": "43.58061543292057,1.401751073689455",\n    "geo_shape": {\n      "coordinates": [\n        [\n          1.401751073689455,\n          43.58061543292057\n        ]\n      ],\n      "type": "MultiPoint"\n    },\n    "ins_nom": "BOULODROME LOU BOSC",\n    "ins_complexe_nom_cplmt": "COMPLEXE SPORTIF DU MIRAIL",\n    "ins_codepostal": 31100,\n    "secteur": "Toulouse Ouest",\n    "quartier": 6.3,\n    "acces_libre": null,\n    "ins_nb_equ": 1,\n    "ins_detail_equ": "",\n    "ins_complexe_nom": "",\n    "ins_adresse": "",\n    "ins_commune": "",\n    "acces_public_horaires": null,\n    "acces_club_scol": null,\n    "ins_nom_cplmt": "",\n    "ins_id_install": ""\n  }\n]\n```\n\nOn this endpoint you can use every neat stuff postgrest provides. Here we only want the `ins_nom` column where it icontains "maurice":\n\n```shell\ncurl "http://localhost:8005/api/resources/27d469ff-9908-4b7e-a2e0-9439bb38a395/data/?select=ins_nom&ins_nom=ilike.*maurice*"\n```\n\n```json\n[\n  {\n    "ins_nom": "BOULODROME MAURICE BECANNE"\n  }\n]\n```\n',
    'author': 'Etalab',
    'author_email': 'opendatateam@data.gouv.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
