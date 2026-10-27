# 3. Plano de testes

## Pirâmide de testes

| Nível | Quantidade de casos | O que cobre |
|---|---|---|
| Unidade | 12 (CT01 a CT12) | Regra do crédito (RF02, RF03, RF04), cálculo do atraso em horas (RF01, implícito em todos) e regra da ausência comprovada (RF05). Funções puras, rápidas, com todos os valores-limite |
| Integração | 4 (CT13 a CT16) | Idempotência com banco real (RF09), numeração concorrente (RNF03), retentativa e fila de falhas (RF08), adaptador do WhatsApp (RF07) |
| Ponta a ponta | 1 (CT17) | Fluxo completo confirmação → crédito → nota → notificação, dentro de 5 min (RNF02) |

**Por que essa proporção:** o maior risco da Garantia de Prazo é **pagar o valor errado**, e isso está numa regra pura cheia de limites (2 h, 24 h, 72 h, tetos). Essa regra é testada em massa na base da pirâmide, onde o teste é barato e roda em milissegundos. Os problemas que só aparecem com infraestrutura real (duplicação, concorrência, falha de rede) ficam na integração. Ponta a ponta é caro e lento, então fica um único caso que prova que as peças estão ligadas e o prazo de 5 min é cumprido.

## Casos de teste

| ID | Requisito | Pré-condição | Entrada | Resultado esperado | Nível | Dublê | Justificativa do dublê |
|---|---|---|---|---|---|---|---|
| CT01 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 1h59 | Crédito de R$ 0,00 | Unidade | Nenhum | Regra pura, sem dependência externa |
| CT02 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de exatamente 2h00 | Crédito de R$ 0,00 (limite superior da tolerância) | Unidade | Nenhum | Regra pura |
| CT03 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 2h01 | Crédito de R$ 30,00 (10%) | Unidade | Nenhum | Regra pura |
| CT04 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de exatamente 24h00 | Crédito de R$ 30,00 (10%, limite da faixa) | Unidade | Nenhum | Regra pura |
| CT05 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de 24h01 | Crédito de R$ 75,00 (25%) | Unidade | Nenhum | Regra pura |
| CT06 | RF02 | Cliente Varejo, frete de R$ 300,00 | Atraso de exatamente 72h00 e de 72h01 | R$ 75,00 (25%) e R$ 150,00 (50%) | Unidade | Nenhum | Regra pura |
| CT07 | RF02 | Cliente Varejo, frete de R$ 1.200,00 | Atraso de 73h | Crédito de R$ 500,00 (50% = R$ 600, limitado ao teto) | Unidade | Nenhum | Regra pura |
| CT08 | RF03 | Cliente Corporativo, frete de R$ 300,00 | Atrasos de 2h01, 24h01 e 72h01 | R$ 60,00 (20%), R$ 150,00 (50%) e R$ 300,00 (100%) | Unidade | Nenhum | Regra pura |
| CT09 | RF03 | Cliente Corporativo, frete de R$ 5.000,00 | Atraso de 25h | Crédito de R$ 2.000,00 (50% = R$ 2.500, limitado ao teto) | Unidade | Nenhum | Regra pura |
| CT10 | RF03 | Cliente Cortesia, frete de R$ 0,00 | Atraso de 80h | Crédito de R$ 0,00 e indicação de que o cliente deve ser notificado do atraso | Unidade | Nenhum | Regra pura |
| CT11 | RF04 | Registro de políticas com Varejo, Corporativo e Cortesia | Registrar uma política de teste "Parceiro" (5% fixo acima de 2 h) e calcular frete R$ 100,00, atraso 10h | Crédito de R$ 5,00, e os casos CT01 a CT10 continuam passando sem alteração no código das políticas existentes | Unidade | Stub | A política "Parceiro" é um stub que devolve um percentual fixo: o teste verifica que o mecanismo de registro aceita um tipo novo, não a regra dele |
| CT12 | RF05 | Telemetria registra o veículo parado a 200 m do endereço das 10h00 às 10h10; ausência registrada às 10h10 | Confirmação com atraso de 30h | Sem crédito. Variações: a 201 m ou parado por 9 min 59 s → crédito normal | Unidade | Stub | O histórico de posições vem de um stub da Telemetria: só fornece dados de entrada, o teste não verifica chamadas |
| CT13 | RF09 | Banco da Garantia vazio (PostgreSQL real em contêiner) | Mesma mensagem de confirmação (mesmo `IdConfirmacao`) consumida duas vezes, inclusive em paralelo | Exatamente 1 crédito gravado e 1 evento `CreditoConcedido` publicado | Integração | Stub (Frete e Telemetria) | Frete e Telemetria só fornecem prazo e "sem ausência"; o que se verifica é o banco real, porque a garantia está na restrição `UNIQUE` |
| CT14 | RNF03, RF06 | Banco do Faturamento real em contêiner | 1.000 emissões de nota concorrentes (várias threads) | 1.000 notas com 1.000 números distintos | Integração | Nenhum | A unicidade depende da sequence do banco; um dublê esconderia exatamente o que se quer testar |
| CT15 | RF08 | Cliente com canal preferido WhatsApp | Envio em que a API do parceiro falha 4 vezes seguidas (original + 3 retentativas) | 4 chamadas feitas ao parceiro; mensagem publicada na fila de falhas (DLQ). Variação: falha 2 vezes e passa na 3ª → sem DLQ | Integração | Mock | O que se verifica é a **interação**: número de chamadas ao parceiro e publicação na DLQ. O mock do cliente HTTP do parceiro registra e confere as chamadas |
| CT16 | RF07 | Cliente com canal preferido WhatsApp | Notificação interna `{cliente, mensagem}` | O adaptador envia ao parceiro o JSON no formato dele (campos, telefone com DDI) | Integração | Spy | O spy deixa o envio acontecer e captura a requisição, para conferir o formato convertido pelo Adapter |
| CT17 | RNF02, RF06 | Todos os serviços no ar via `docker compose up`, cliente Varejo, frete R$ 300,00 | Publicar confirmação de entrega com atraso de 30h | Em até 5 min: nota de crédito de R$ 75,00 emitida, notificação enviada e saldo do Portal atualizado | Ponta a ponta | Stub (só o parceiro WhatsApp e o e-mail externo) | Serviços externos à LogiTech não podem ser chamados em teste; todo o resto é real |

## Mutante que o plano detecta

| Mutante | Caso que o detecta | Por quê |
|---|---|---|
| Trocar `atraso > 2` por `atraso >= 2` na verificação da tolerância | CT02 | Com exatamente 2h00, o código mutado passa a conceder 10% (R$ 30,00) e o CT02 espera R$ 0,00 |
| Trocar `atraso <= 24` por `atraso < 24` na primeira faixa | CT04 | Com exatamente 24h00, o mutante aplica 25% (R$ 75,00) e o CT04 espera 10% (R$ 30,00) |
| Remover o `min(credito, teto)` | CT07 e CT09 | O crédito sai R$ 600,00 / R$ 2.500,00 em vez do teto |
