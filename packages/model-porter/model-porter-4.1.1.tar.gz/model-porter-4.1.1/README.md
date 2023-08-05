model-porter
============

Internal tool for seeding content in Django (and Wagtail). Please bear with us while we prepare more detailed documentation.

Compatibility
-------------

`model-porter`' major.minor version number indicates the Django release it is compatible with. Currently this is Django 4.1.

Installation
------------

1. Install using `pip`:
  ```shell
  pip install model-porter
  ```
2. Add
   `model_porter` to your `INSTALLED_APPS` setting:
   ```python
   INSTALLED_APPS = [
     # ...
     'model_porter'
     # ...
   ]
   ```
