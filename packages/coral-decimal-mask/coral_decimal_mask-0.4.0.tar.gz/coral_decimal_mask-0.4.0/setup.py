# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['decimal_mask']

package_data = \
{'': ['*'], 'decimal_mask': ['static/decimal_mask/*']}

setup_kwargs = {
    'name': 'coral-decimal-mask',
    'version': '0.4.0',
    'description': 'Django mask decimal fields',
    'long_description': '# Coral Decimal Mask\n\nWidgets que aplicam mascaras nos forms do django.\n\n## Instalação\n\n```sh\npython -m pip install coral-decimal-mask\n```\n\n## Como usar\n\n#### Adicione `decimal_mask` em `INSTALLED_APPS`:\n\n```py\nINSTALLED_APPS = [\n    ...\n    "decimal_mask",\n]\n```\n\n#### Configure seus widgets: \n\n```py\nfrom django import forms\nfrom decimal_mask.widgets import DecimalMaskWidget, MoneyMaskWidget, PercentMaskWidget\n\n\nclass MyForm(forms.Form):\n    value1 = forms.DecimalField(widget=DecimalMaskWidget())\n    value2 = forms.DecimalField(\n        widget=DecimalMaskWidget(\n            decimal_attrs={\n                "locales": "pt-BR",\n                "decimalPlaces": 2,\n                "format": {\n                    "style": "currency",\n                    "currency": "BRL",\n                },\n            },\n        ),\n    ) # ou usar forms.DecimalField(widget=MoneyMaskWidget())\n    value3 = forms.DecimalField(widget=PercentMaskWidget())\n```\n\n- O parâmetro `decimal_attrs` são algumas opções para construir o objeto javascript [Intl.NumberFormat](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat).\n\n  - `locales` é o primeiro parâmetro de `Intl.NumberFormat` referente a linguagem utilizada na interface do usuário da sua aplicação.\n\n  - `decimalPlaces` é o número de casas decimais que a mascara vai considerar.\n\n  - `format` é um `dict` com as informações do parâmetro `options` de `Intl.NumberFormat`.\n\n\n## Contribuindo com o projeto\n\n```py\n(venv) poetry install\n(venv) pytest\n```\n',
    'author': 'Coral Sistemas',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
