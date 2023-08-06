# Shopcloud-Django-Authenticator

Single Sign In from Shopcloud

## Quickstart

```
pip3 istall shopcloud-django-authenticator
```

1. Add "authenticator" to your INSTALLED_APPS setting like this::

```py
INSTALLED_APPS = [
    ...
    'authenticator',
]
```

```py
AUTHENTICATOR_KEY = os.environ.get('AUTHENTICATOR_KEY', 'DEV-KEY')
```

To generate a key use `pwgen -s $1 64`

2. Include the polls URLconf in your project urls.py like this::

```
path('authenticator/', include('authenticator.urls')),
```

3. Run `python manage.py migrate` to create the polls models.


4. Install custom Tags for Login Button

```
{% load tower_tags %}
{% tower_login request 'QYG69GK' %}
```

## Release

```sh
$ rm -rf build dist
$ pip3 install wheel twine
$ python3 setup.py sdist bdist_wheel
$ twine upload dist/*
```
