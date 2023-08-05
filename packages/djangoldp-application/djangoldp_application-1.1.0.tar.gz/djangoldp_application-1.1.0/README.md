# DjangoLDP application package

## Step by step quickstart

1. Installation

- `git clone git@git.startinblox.com:applications/ontochain/application-registry.git /path/to/djangoldp-application`

2. Developpement environnement

In order to test and developp your package, you need to put the package src directory at the same level of a working django ldp app. By exemple, you can clone the sib app data server
`git clone git@git.startinblox.com:applications/ontochain/application-registry.git server /path/to/app`

- The classical way :
  `ln -s /path/to/djangoldp-application/djangoldp_application /path/to/app/djangoldp_application`

- The docker way : in the _volumes_ section, add a line in docker-compose.override.yml. Example

```yaml
volumes:
  - ./:/app
  - /path/to/djangoldp-application/djangoldp_application:/app/djangoldp_application
```

Add your package in settings.py of the app. Now, you can test if your package is imported propefully by doing a
`python manage.py shell` then
from djangoldp_application.models import application

If, no error, it's working.
