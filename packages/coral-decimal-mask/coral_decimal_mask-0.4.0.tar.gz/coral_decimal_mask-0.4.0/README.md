# Coral Decimal Mask

Widgets que aplicam mascaras nos forms do django.

## Instalação

```sh
python -m pip install coral-decimal-mask
```

## Como usar

#### Adicione `decimal_mask` em `INSTALLED_APPS`:

```py
INSTALLED_APPS = [
    ...
    "decimal_mask",
]
```

#### Configure seus widgets: 

```py
from django import forms
from decimal_mask.widgets import DecimalMaskWidget, MoneyMaskWidget, PercentMaskWidget


class MyForm(forms.Form):
    value1 = forms.DecimalField(widget=DecimalMaskWidget())
    value2 = forms.DecimalField(
        widget=DecimalMaskWidget(
            decimal_attrs={
                "locales": "pt-BR",
                "decimalPlaces": 2,
                "format": {
                    "style": "currency",
                    "currency": "BRL",
                },
            },
        ),
    ) # ou usar forms.DecimalField(widget=MoneyMaskWidget())
    value3 = forms.DecimalField(widget=PercentMaskWidget())
```

- O parâmetro `decimal_attrs` são algumas opções para construir o objeto javascript [Intl.NumberFormat](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat).

  - `locales` é o primeiro parâmetro de `Intl.NumberFormat` referente a linguagem utilizada na interface do usuário da sua aplicação.

  - `decimalPlaces` é o número de casas decimais que a mascara vai considerar.

  - `format` é um `dict` com as informações do parâmetro `options` de `Intl.NumberFormat`.


## Contribuindo com o projeto

```py
(venv) poetry install
(venv) pytest
```
