# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wagtail_modeltranslation',
 'wagtail_modeltranslation.makemigrations',
 'wagtail_modeltranslation.makemigrations.management',
 'wagtail_modeltranslation.makemigrations.management.commands',
 'wagtail_modeltranslation.management',
 'wagtail_modeltranslation.management.commands',
 'wagtail_modeltranslation.migrate',
 'wagtail_modeltranslation.migrate.management',
 'wagtail_modeltranslation.migrate.management.commands',
 'wagtail_modeltranslation.templatetags',
 'wagtail_modeltranslation.tests',
 'wagtail_modeltranslation.tests.migrations']

package_data = \
{'': ['*'],
 'wagtail_modeltranslation': ['static/wagtail_modeltranslation/css/*',
                              'static/wagtail_modeltranslation/js/*',
                              'templates/*']}

install_requires = \
['Django>=3.2', 'django-modeltranslation>=0.17', 'wagtail>=4.0,<=6.0']

setup_kwargs = {
    'name': 'wagtail-modeltranslation',
    'version': '0.14.0',
    'description': 'Translates Wagtail CMS models using a registration approach.',
    'long_description': 'Wagtail Modeltranslation\n========================\n\nThis app is built using core features of django-modeltranslation: https://github.com/deschler/django-modeltranslation\n\nIt\'s an alternative approach for i18n support on Wagtail CMS websites.\n\nThe wagtail-modeltranslation application is used to translate dynamic content of\nexisting Wagtail models to an arbitrary number of languages, without having to\nchange the original model classes. It uses a registration approach (comparable\nto Django\'s admin app) to add translations to existing or new projects and is\nfully integrated into the Wagtail admin UI.\n\nThe advantage of a registration approach is the ability to add translations to\nmodels on a per-app basis. You can use the same app in different projects,\nwhether or not they use translations, and without touching the original\nmodel class.\n\n\n.. image:: https://github.com/infoportugal/wagtail-modeltranslation/blob/master/screenshot.png?raw=true\n    :target: https://github.com/infoportugal/wagtail-modeltranslation/blob/master/screenshot.png?raw=true\n\n\nFeatures\n========\n\n- Add translations without changing existing models or views\n- Translation fields are stored in the same table (no expensive joins)\n- Supports inherited models (abstract and multi-table inheritance)\n- Handle more than just text fields\n- Wagtail admin integration\n- Flexible fallbacks, auto-population and more!\n- Default Page model fields has translatable fields by default\n- StreamFields are now supported!\n\n\nCaveats\n=======\n\n:code:`wagtail-modeltranslation` patches Wagtail\'s :code:`Page` model with translation fields\n:code:`title_xx`, :code:`slug_xx`, :code:`seo_title_xx`, :code:`search_description_xx` and :code:`url_path_xx` where "xx" represents the language code for each translated language. This\nis done without migrations through command :code:`sync_page_translation_fields`. Since :code:`Page` model belongs to\nWagtail it\'s within the realm of possibility that one day Wagtail may add a conflicting field to :code:`Page` thus interfering with :code:`wagtail-modeltranslation`.\n\nWagtail\'s :code:`slugurl` tag does not work across languages. :code:`wagtail-modeltranslation` provides a drop-in replacement named :code:`slugurl_trans` which by default takes the slug parameter in the default language.\n\nQuick start\n===========\n\n1. Install :code:`wagtail-modeltranslation`::\n\n    pip install wagtail-modeltranslation\n\n2. Add \'wagtail_modeltranslation\' to your ``INSTALLED_APPS`` setting like this (before all apps that you want to translate)::\n\n    INSTALLED_APPS = (\n        ...\n        \'wagtail_modeltranslation\',\n        \'wagtail_modeltranslation.makemigrations\',\n        \'wagtail_modeltranslation.migrate\',\n    )\n\n3. Add \'django.middleware.locale.LocaleMiddleware\' to ``MIDDLEWARE`` on your ``settings.py``::\n\n    MIDDLEWARE = (\n        ...\n        \'django.middleware.locale.LocaleMiddleware\',  # should be after SessionMiddleware and before CommonMiddleware\n    )\n\n4. Enable i18n on ``settings.py``::\n\n    USE_I18N = True\n\n5. Define available languages on ``settings.py``::\n\n    from django.utils.translation import gettext_lazy as _\n\n    LANGUAGES = (\n        (\'pt\', _(\'Portuguese\')),\n        (\'es\', _(\'Spanish\')),\n        (\'fr\', _(\'French\')),\n    )\n\n6. Create ``translation.py`` inside the root folder of the app where the model you want to translate exists::\n\n    from .models import Foo\n    from modeltranslation.translator import TranslationOptions\n    from modeltranslation.decorators import register\n\n    @register(Foo)\n    class FooTR(TranslationOptions):\n        fields = (\n            \'body\',\n        )\n\n7. Run :code:`python manage.py makemigrations` followed by :code:`python manage.py migrate` (repeat every time you add a new language or register a new model)\n\n8. Run :code:`python manage.py sync_page_translation_fields` (repeat every time you add a new language)\n\n9. If you\'re adding :code:`wagtail-modeltranslation` to an existing site run :code:`python manage.py update_translation_fields`\n\n\nSupported versions\n==================\n\n.. list-table:: Title\n   :widths: 25 25 25 25\n   :header-rows: 1\n\n   * - wagtail-modeltranslation release\n     - Compatible Wagtail versions\n     - Compatible Django versions\n     - Compatible Python versions\n   * - 0.10\n     - >= 1.12, < 2.12\n     - >= 1.11\n     - 2.7, 3.4, 3.5, 3.6\n   * - 0.11\n     - >= 2.13, < 3.0\n     - >= 3.0\n     - 3.6, 3.7, 3.8, 3.9\n   * - 0.12\n     - >= 3.0, < 4.0\n     - >= 3.2\n     - 3.7, 3.8, 3.9, 3.10\n   * - 0.13\n     - >= 4.0, < 5.0\n     - >= 3.2\n     - 3.7, 3.8, 3.9, 3.10\n   * - 0.14\n     - >= 5.0\n     - >= 3.2\n     - 3.7, 3.8, 3.9, 3.10, 3.11\n\nUpgrade considerations (v0.10.8)\n================================\n\n- Template tag ``change_lang`` now needs a second parameter, ``page``\n\nUpgrade considerations (v0.8)\n=============================\n\nThis version includes breaking changes as some key parts of the app have been re-written:\n\n- The most important change is that ``Page`` is now patched with translation fields.\n- ``WAGTAILMODELTRANSLATION_ORIGINAL_SLUG_LANGUAGE`` setting has been deprecated.\n\nTo upgrade to this version you need to:\n\n- Replace the ``WagtailTranslationOptions`` with ``TranslationOptions`` in all translation.py files\n- Run :code:`python manage.py sync_page_translation_fields` at least once to create ``Page``\'s translation fields\n- Replace any usages of Wagtail\'s ``{% slugurl ... %}`` for :code:`wagtail-modeltranslation`\'s own ``{% slugurl_trans ... %}``\n- While optional it\'s recommended to add ``\'wagtail_modeltranslation.makemigrations\'`` to your INSTALLED_APPS. This will override Django\'s ``makemigrations`` command to avoid creating spurious ``Page`` migrations.\n\nUpgrade considerations (v0.6)\n=============================\n\nThis version has some important changes as there was a refactoring to include django-modeltranslation as a dependency instead of\nduplicating their code in our version. This allow us to focus on Wagtail admin integration features as django-modeltranslation is\nvery well mantained and is very quickly to fix problems with the latest Django versions. This way we also keep all the django-modeltranslation\nfeatures (if you want you can also customize django-admin, for example). We also provide a new class to create the translation options classes: **WagtailTranslationOptions**\nMost of the changes are related to imports as they change from wagtail-modeltranslation to modeltranslation.\n\nTo upgrade to this version you need to:\n\n- Replace the ``TranslationOptions`` with ``WagtailTranslationOptions`` in all translation.py files\n- The import of the register decorator is now ``from modeltranslation.decorators import register``\n- The import of translator is now ``from modeltranslation.translator import translator``\n\n\nProject Home\n------------\nhttps://github.com/infoportugal/wagtail-modeltranslation\n\nDocumentation\n-------------\nhttp://wagtail-modeltranslation.readthedocs.io/\n',
    'author': 'InfoPortugal S.A.',
    'author_email': 'suporte24@infoportugal.pt',
    'maintainer': 'InfoPortugal S.A.',
    'maintainer_email': 'suporte24@infoportugal.pt',
    'url': 'https://github.com/infoportugal/wagtail-modeltranslation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
