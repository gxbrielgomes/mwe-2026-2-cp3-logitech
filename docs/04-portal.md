# 4. Tela do Portal do Cliente (RF10)

## Estados da tela

A tela é uma função do estado: `tela = f(pedido, conexaoAoVivo, saldo)`. O componente raiz calcula o estado a partir desses dados e cada componente filho só desenha o que recebe.

| Estado | Dados disponíveis | O que a tela exibe |
|---|---|---|
| **Carregando** | Só o número do pedido | Esqueleto (placeholder) do mapa, da previsão e do saldo |
| **Erro de carga** | Mensagem de erro | Aviso "Não foi possível carregar o pedido" e botão "Tentar novamente" |
| **Em trânsito, no prazo** | Posição do veículo, previsão de chegada, prazo prometido, saldo | Mapa com o veículo, previsão de chegada em destaque (verde), prazo prometido e saldo de créditos |
| **Em trânsito, com atraso previsto** | Igual ao anterior, com previsão depois do prazo prometido | Mapa, previsão em destaque (laranja) e aviso "Sua entrega pode atrasar. Se atrasar mais de 2 h, você recebe crédito automático" (não aparece para Cortesia) |
| **Entregue no prazo** | Data/hora da entrega, saldo | Selo "Entregue" com data/hora; mapa oculto; saldo |
| **Entregue com atraso, crédito em processamento** | Data/hora da entrega, atraso em horas, saldo antigo | Selo "Entregue com atraso de X h" e aviso "Seu crédito está sendo calculado" |
| **Entregue com atraso, crédito concedido** | Atraso, valor do crédito, número da nota, saldo atualizado | Selo, valor do crédito, número da nota de crédito e saldo atualizado (destacado ao mudar) |
| **Entregue com atraso, sem crédito** | Atraso e motivo (dentro da tolerância, ausência comprovada ou cliente Cortesia) | Selo e explicação do motivo |
| **Destinatário ausente** | Registro de ausência, data/hora | Aviso "Tentamos entregar e não havia ninguém" com a data/hora |
| **Conexão ao vivo perdida** | Últimos dados recebidos, instante da última atualização | Mantém os últimos dados na tela, com o aviso "Reconectando... última atualização às HH:MM" |

## Árvore de componentes

```
<AcompanhamentoPedido pedidoId>
  ├── <CabecalhoPedido numero status />
  ├── <AvisoConexao conectado ultimaAtualizacao />
  ├── <EstadoCarregando />            (só no estado Carregando)
  ├── <EstadoErro mensagem onTentarNovamente />   (só no estado Erro)
  ├── <PainelEntrega>
  │     ├── <MapaVeiculo posicao destino />
  │     ├── <PrevisaoChegada previsao prazoPrometido />
  │     ├── <AvisoAtraso tipoCliente />
  │     └── <SeloEntrega status entregueEm atrasoHoras motivoSemCredito />
  └── <PainelCreditos>
        ├── <SaldoCreditos saldo destacado />
        └── <CreditoDoPedido valor numeroNota emProcessamento />
```

| Componente | Props recebidas | Responsabilidade |
|---|---|---|
| `AcompanhamentoPedido` | `pedidoId` | Busca a carga inicial (HTTP), abre a conexão SSE pelo hook `useAcompanhamento(pedidoId)`, guarda o estado e decide quais filhos mostrar |
| `CabecalhoPedido` | `numero`, `status` | Mostra número do pedido e situação resumida |
| `AvisoConexao` | `conectado`, `ultimaAtualizacao` | Mostra o aviso de reconexão quando a conexão ao vivo cai |
| `EstadoCarregando` | — | Esqueleto da tela |
| `EstadoErro` | `mensagem`, `onTentarNovamente` | Mensagem de erro e botão para recarregar |
| `PainelEntrega` | `pedido` | Agrupa as informações da entrega |
| `MapaVeiculo` | `posicao`, `destino` | Desenha o veículo e o destino no mapa |
| `PrevisaoChegada` | `previsao`, `prazoPrometido` | Mostra a previsão; verde se dentro do prazo, laranja se depois |
| `AvisoAtraso` | `tipoCliente` | Explica a Garantia de Prazo quando há atraso previsto (oculto para Cortesia) |
| `SeloEntrega` | `status`, `entregueEm`, `atrasoHoras`, `motivoSemCredito` | Mostra entregue/ausente/atrasado e o motivo de não haver crédito |
| `PainelCreditos` | `saldo`, `credito` | Agrupa as informações de crédito |
| `SaldoCreditos` | `saldo`, `destacado` | Mostra o saldo; anima quando o valor muda |
| `CreditoDoPedido` | `valor`, `numeroNota`, `emProcessamento` | Mostra o crédito deste pedido ou "em processamento" |

## Origem dos dados

| Dado | Origem | Como chega |
|---|---|---|
| Posição do veículo e previsão de chegada | Telemetria (Rastreamento) | Telemetria → API do Portal (BFF) → navegador por **SSE**, evento `posicao` a cada 30 s |
| Prazo prometido | Frete | Carga inicial por **HTTP** (`GET /pedidos/{id}`) |
| Status da entrega e ausência | Pedidos | Evento no broker → BFF → **SSE**, evento `status` |
| Crédito do pedido e saldo | Garantia de Prazo e Faturamento | Evento `CreditoConcedido` / `SaldoAtualizado` no broker → BFF → **SSE**, evento `saldo` |

Fluxo: ao abrir a tela, o componente raiz faz `GET /pedidos/{id}` para os dados atuais e abre `new EventSource('/pedidos/{id}/eventos')`. Cada evento SSE recebido atualiza o estado, e o React redesenha só o que mudou. Se a conexão cai, o `EventSource` reconecta sozinho e a tela mostra o estado **Conexão ao vivo perdida** até voltar.
