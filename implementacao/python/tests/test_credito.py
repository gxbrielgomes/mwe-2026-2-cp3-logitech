from datetime import timedelta
from decimal import Decimal

import pytest

from garantia.credito import (
    PoliticaDeCredito,
    ResultadoDoCredito,
    calcular_credito,
    registrar_politica,
)


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


# RF03 - Corporativo
@pytest.mark.parametrize(
    "atraso, esperado",
    [(h(2, 1), "60.00"), (h(24, 1), "150.00"), (h(72, 1), "300.00")],
)
def test_ct08_corporativo_percentuais_dobrados(atraso, esperado):
    assert calcular_credito("CORPORATIVO", Decimal("300.00"), atraso).valor == Decimal(esperado)


def test_ct09_corporativo_limitado_ao_teto_de_2000():
    assert calcular_credito("CORPORATIVO", Decimal("5000.00"), h(25)).valor == Decimal("2000.00")


def test_ct10_cortesia_sem_credito_mas_notificado():
    resultado = calcular_credito("CORTESIA", Decimal("0.00"), h(80))
    assert resultado.valor == Decimal("0.00")
    assert resultado.notificar_atraso is True


# RF04 - tipo novo sem alterar os existentes
class PoliticaParceiroStub(PoliticaDeCredito):
    def calcular(self, frete, atraso):
        return ResultadoDoCredito((frete * Decimal("0.05")).quantize(Decimal("0.01")), True)


def test_ct11_novo_tipo_de_cliente_registrado_sem_alterar_existentes():
    registrar_politica("PARCEIRO", PoliticaParceiroStub())
    assert calcular_credito("PARCEIRO", Decimal("100.00"), h(10)).valor == Decimal("5.00")
    assert calcular_credito("VAREJO", Decimal("300.00"), h(2, 1)).valor == Decimal("30.00")
