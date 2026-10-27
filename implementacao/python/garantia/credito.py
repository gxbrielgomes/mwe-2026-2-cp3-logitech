from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

TOLERANCIA = timedelta(hours=2)
CENTAVO = Decimal("0.01")


@dataclass(frozen=True)
class ResultadoDoCredito:
    valor: Decimal
    notificar_atraso: bool


def calcular_credito(tipo_cliente: str, frete: Decimal, atraso: timedelta) -> ResultadoDoCredito:
    if atraso <= TOLERANCIA:
        return ResultadoDoCredito(Decimal("0.00"), notificar_atraso=False)
    if atraso <= timedelta(hours=24):
        percentual = Decimal("0.10")
    elif atraso <= timedelta(hours=72):
        percentual = Decimal("0.25")
    else:
        percentual = Decimal("0.50")
    valor = min(frete * percentual, Decimal("500.00"))
    return ResultadoDoCredito(valor.quantize(CENTAVO, ROUND_HALF_UP), notificar_atraso=True)
