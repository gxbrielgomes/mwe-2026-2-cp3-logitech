"""Regra de cálculo do crédito da Garantia de Prazo (RF02, RF03 e RF04).

Cada tipo de cliente tem a sua PoliticaDeCredito (padrão Strategy). Um tipo novo
é uma classe nova registrada com `registrar_politica`, sem alterar as existentes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

TOLERANCIA = timedelta(hours=2)
CENTAVO = Decimal("0.01")


@dataclass(frozen=True)
class FaixaDeAtraso:
    ate: timedelta | None  # limite superior inclusivo; None = sem limite
    percentual: Decimal


@dataclass(frozen=True)
class ResultadoDoCredito:
    valor: Decimal
    notificar_atraso: bool


class PoliticaDeCredito(ABC):
    @abstractmethod
    def calcular(self, frete: Decimal, atraso: timedelta) -> ResultadoDoCredito: ...


class PoliticaPorFaixas(PoliticaDeCredito):
    def __init__(self, faixas: list[FaixaDeAtraso], teto: Decimal):
        self.faixas = faixas
        self.teto = teto

    def calcular(self, frete: Decimal, atraso: timedelta) -> ResultadoDoCredito:
        if atraso <= TOLERANCIA:
            return ResultadoDoCredito(Decimal("0.00"), notificar_atraso=False)
        percentual = next(
            f.percentual for f in self.faixas if f.ate is None or atraso <= f.ate
        )
        valor = min(frete * percentual, self.teto)
        return ResultadoDoCredito(
            valor.quantize(CENTAVO, ROUND_HALF_UP), notificar_atraso=True
        )


FAIXAS_VAREJO = [
    FaixaDeAtraso(timedelta(hours=24), Decimal("0.10")),
    FaixaDeAtraso(timedelta(hours=72), Decimal("0.25")),
    FaixaDeAtraso(None, Decimal("0.50")),
]


class PoliticaVarejo(PoliticaPorFaixas):
    def __init__(self):
        super().__init__(FAIXAS_VAREJO, teto=Decimal("500.00"))


class PoliticaCorporativo(PoliticaPorFaixas):
    """Percentuais do Varejo em dobro, teto de R$ 2.000 (RF03)."""

    def __init__(self):
        faixas = [FaixaDeAtraso(f.ate, f.percentual * 2) for f in FAIXAS_VAREJO]
        super().__init__(faixas, teto=Decimal("2000.00"))


class PoliticaCortesia(PoliticaDeCredito):
    """Frete zero: nunca há crédito, mas o cliente é notificado do atraso (RF03)."""

    def calcular(self, frete: Decimal, atraso: timedelta) -> ResultadoDoCredito:
        return ResultadoDoCredito(Decimal("0.00"), notificar_atraso=atraso > TOLERANCIA)


_POLITICAS: dict[str, PoliticaDeCredito] = {
    "VAREJO": PoliticaVarejo(),
    "CORPORATIVO": PoliticaCorporativo(),
    "CORTESIA": PoliticaCortesia(),
}


def registrar_politica(tipo_cliente: str, politica: PoliticaDeCredito) -> None:
    _POLITICAS[tipo_cliente] = politica


def calcular_credito(
    tipo_cliente: str, frete: Decimal, atraso: timedelta
) -> ResultadoDoCredito:
    return _POLITICAS[tipo_cliente].calcular(frete, atraso)
