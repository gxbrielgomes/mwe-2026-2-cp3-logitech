# 5. Implementação em TDD

Implementem a regra de cálculo do crédito (RF02, RF03 e RF04) em **uma** linguagem à
escolha da dupla: Java, C#, Python ou TypeScript. O Codespace deste repositório já traz
as quatro.

## Como trabalhar

1. Escrevam um teste para um caso do plano (`docs/03-testes.md`) e confirmem que ele
   **falha**. Façam o commit: `test: CT01 atraso abaixo da tolerância não gera crédito`.
2. Escrevam o mínimo de código que faz o teste passar. Façam o commit:
   `feat: calcula crédito zero dentro da tolerância`.
3. Se for preciso, refatorem com os testes passando. Façam o commit: `refactor: ...`.
4. Repitam para o próximo caso.

O histórico de commits é a evidência do TDD: o commit de teste vem antes do commit de
código que o faz passar.

## O que registrar aqui

- Linguagem e framework de teste: Python 3 com pytest. Código em `implementacao/python/garantia/credito.py`, testes em `implementacao/python/tests/test_credito.py`
- Comando para executar os testes: `cd implementacao/python && python -m pytest -v`
- Casos do plano implementados (IDs): CT01 a CT11 (RF02, RF03 e RF04)
- Saída da última execução dos testes:

```
test_credito.py::test_varejo_faixas[CT01 abaixo da toler\xe2ncia-atraso0-0.00] PASSED [  7%]
test_credito.py::test_varejo_faixas[CT02 exatamente na toler\xe2ncia-atraso1-0.00] PASSED [ 14%]
test_credito.py::test_varejo_faixas[CT03 logo acima da toler\xe2ncia-atraso2-30.00] PASSED [ 21%]
test_credito.py::test_varejo_faixas[CT04 exatamente 24h-atraso3-30.00] PASSED [ 28%]
test_credito.py::test_varejo_faixas[CT05 logo acima de 24h-atraso4-75.00] PASSED [ 35%]
test_credito.py::test_varejo_faixas[CT06 exatamente 72h-atraso5-75.00] PASSED [ 42%]
test_credito.py::test_varejo_faixas[CT06 logo acima de 72h-atraso6-150.00] PASSED [ 50%]
test_credito.py::test_ct07_varejo_limitado_ao_teto_de_500 PASSED   [ 57%]
test_credito.py::test_ct08_corporativo_percentuais_dobrados[atraso0-60.00] PASSED [ 64%]
test_credito.py::test_ct08_corporativo_percentuais_dobrados[atraso1-150.00] PASSED [ 71%]
test_credito.py::test_ct08_corporativo_percentuais_dobrados[atraso2-300.00] PASSED [ 78%]
test_credito.py::test_ct09_corporativo_limitado_ao_teto_de_2000 PASSED [ 85%]
test_credito.py::test_ct10_cortesia_sem_credito_mas_notificado PASSED [ 92%]
test_credito.py::test_ct11_novo_tipo_de_cliente_registrado_sem_alterar_existentes PASSED [100%]
============================== 14 passed in 0.02s ==============================
```

Desenho: cada tipo de cliente é uma `PoliticaDeCredito` (Strategy). Varejo e Corporativo
usam a mesma tabela de faixas, com percentuais dobrados e teto maior no Corporativo;
Cortesia nunca dá crédito, mas sinaliza `notificar_atraso`. Um tipo novo entra com
`registrar_politica`, sem alterar as classes existentes (RF04, verificado no CT11).
Valores em `Decimal` para não ter erro de arredondamento com dinheiro.
