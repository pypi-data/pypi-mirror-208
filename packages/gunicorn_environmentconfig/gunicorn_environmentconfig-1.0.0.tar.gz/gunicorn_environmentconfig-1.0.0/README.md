# gunicorn_environmentconfig

Configure gunicorn completely via environment variables.

gunicorn itself provides environment variable access to only [some of its settings](https://docs.gunicorn.org/en/latest/settings.html).
This package closes the gap, and allows configuring all settings via the environment.

## Usage

Put this into your config file (usually `gunicorn.conf.py`):

```
import gunicorn_environmentconfig
gunicorn_environmentconfig.apply(globals())
```

Set environment variables with the naming scheme `gunicorn.{setting}`,
where `setting` is the name you'd use in the config file, for example:

```
env gunicorn.preload_app=true python -m gunicorn myapp
```

If you append `__literal__` to the variable name, they are evaluated as Python literals,
for example to make gunicorn use the already existing logging configuration
(which might e.g. use a JSON formatter)
and not set up its own formatters, use this:

```
gunicorn.logconfig_dict__literal__={'root': {}, 'loggers': {'gunicorn.error': {'propagate': True}}, 'handlers': {}, 'formatters': {}}
```


## Special case: ini file

To help with transitioning, settings read from a [paste.ini](https://pypi.org/project/PasteDeploy/) configuration file
can be added to the environment (environment takes priority).

To use this, set the `GUNICORN_INI_CONFIG` environment variable to the filename and section name.

```
[app:main]
use = egg:myapp#main

my_app_setting = value1
gunicorn.preload_app = true
```

```
env GUNICORN_INI_CONFIG=paste.ini#app:main python -m gunicorn myapp
```
