# 5. Uso de assistentes de IA

Assistente usado: **Claude (Anthropic)**, durante toda a atividade.

| Entrega | O que foi pedido | O que o assistente sugeriu | Decisão da dupla | Motivo |
|---|---|---|---|---|
| Leitura do problema | Explicar o enunciado e o que cada entrega pede | Resumo das 5 entregas e dos conceitos envolvidos (bounded context, protocolo por requisito, padrões, valores-limite, TDD) | Aceito | Ajudou a entender o escopo antes de começar |
| 1. Modelagem | Rascunho completo do `01-dominio.md` | 5 contextos novos/afetados (Garantia de Prazo, Rastreamento, Faturamento, Notificação, Acompanhamento), com Pedidos e Frete como fornecedores; agregados e linguagem ubíqua | Aceito, revisado pela dupla | Cada RF ficou com um único dono. O assistente chegou a considerar RF01 em Pedidos, mas colocou na Garantia porque "atraso" é conceito da Garantia |
| 2. Arquitetura | Rascunho completo do `02-arquitetura.md` | UDP para telemetria, AMQP com fila durável para a confirmação de entrega, HTTP para consultas, SSE para o Portal; Strategy, Adapter, Observer, Retry + DLQ, consumidor idempotente; `SEQUENCE` do PostgreSQL para a numeração | Aceito | Cada protocolo está ligado a um requisito. Não aplicar Chain of Responsibility nas faixas e não usar Singleton no contador foram escolhas para manter o código simples e correto |
| 3. Testes | Rascunho dos casos de teste | 17 casos com valores-limite (2h00/2h01, 24h00/24h01, 72h00/72h01, tetos), dublês justificados e três mutantes | Aceito | Cobre os limites exatos de RF02 e RF03, que são onde o erro de valor é mais provável |
| 4. Portal | Rascunho dos estados e componentes | 10 estados, árvore de componentes React e SSE para atualização ao vivo | Aceito | SSE basta porque o fluxo é só servidor → cliente; WebSocket foi descartado por ser mais complexo sem necessidade |
| 5. Implementação | Implementar RF02–RF04 em TDD | Python + pytest, Strategy por tipo de cliente, `Decimal` para dinheiro, commits `test:` antes de `feat:` | Aceito | Python foi a linguagem mais rápida para a dupla; o histórico mostra o teste falhando antes do código |
