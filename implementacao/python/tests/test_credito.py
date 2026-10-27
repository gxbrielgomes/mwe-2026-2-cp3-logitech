from datetime import timedelta
from decimal import Decimal

import pytest

from garantia.credito import calcular_credito


def h(horas, minutos=0):
    return timedelta(hours=horas, minutes=minutos)


# RF02 - Varejo, frete de R$ 300,00
@pytest.mark.parametrize(
    "caso, atraso, esperado",
    [
        ("CT01 abaixo da tolerância", h(1, 59), "0.00"),
        ("CT02 exatamente na tolerância", h(2), "0.00"),
        ("CT03 logo acima da tolerância", h(2, 1), "30.00"),
        ("CT04 exatamente 24h", h(24), "30.00"),
        ("CT05 logo acima de 24h", h(24, 1), "75.00"),
        ("CT06 exatamente 72h", h(72), "75.00"),
        ("CT06 logo acima de 72h", h(72, 1), "150.00"),
    ],
)
def test_varejo_faixas(caso, atraso, esperado):
    assert calcular_credito("VAREJO", Decimal("300.00"), atraso).valor == Decimal(esperado)


def test_ct07_varejo_limitado_ao_teto_de_500():
    assert calcular_credito("VAREJO", Decimal("1200.00"), h(73)).valor == Decimal("500.00")
