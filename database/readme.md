# Set-Based & Bulk Operations
- Um dos maiores problemas em relação a banco de dados é o que chamamos de `Row by agonizing row (RBAR)` e `N+1 Problem`. São problemas que podem explodir memória, número de conexões e tempo de processamento, gerando maior latência e menor throughput.

- Os problemas podem ser evitados se puderem ser expressos eficientemente em SQL e realizados dentro do banco de dados. Esse é o princípio `Data Locality`. Todo N+1 gera comportamento RBAR, mas nem todo RBAR é N+1.

- O `Set-Based` é o paradigma responsável por descrever o que fazer com o conjunto. É a descrição do resultado desejado após a execução. Já o `Bulk Operations` é a parte operacional do banco de dados, pegando múltiplos registros e processando de uma vez. O banco de dados passa a otimizar a execução, utilizar índices e minimizar IO.

- Bancos de dados são motores vetorizados, não foram feitos para receber milhares de comandos pequenos, mas sim operar sobre conjuntos grandes. SQL é baseado em álgebra relacional, por isso sempre devemos pensar em conjuntos, filtros, transformações e agregações. O principal objetivo é eliminar `round-trips`, movimentações desnecessárias e processamento no lugar errado.

# Paginação
- Consiste em limitar um conjunto grande de dados em partes menores, para que o client receba apenas um subconjunto dos registros, em vez de trazer todos os dados para a memória da aplicação.

- A tradicional `Page-Based Pagination` utiliza em SQL `LIMIT` e `OFFSET` para leituras. Por exemplo, `LIMIT 10 OFFSET 20`, significa que será retornado no máximo 10 registros, a partir do registro 20. Dessa maneira, é possível entregar os dados de maneira incremental. A desvantagem acontece em grandes volumes de dados, porque o banco de dados sempre precisa percorrer os registros, ou seja, se tivermos `OFFSET 20`, o banco precisaria percorrer todos os primeiros 20 registros, para só então entregar os próximos, e o mesmo acontece se tivermos `OFFSET 999999`. O cálculo para páginas funciona como `OFFSET = (Pag - 1) * LIMIT`, assim temos o registro inicial.

- A `Cursor/Keyset Pagination` utiliza uma chave de ordenação como base, assim o banco de dados consegue usar essa chave sem precisar percorrer todos os registros anteriores, se tornando mais eficiente. A `Seek Pagination` é a maneira de implementar a `Cursor/Keyset Pagination`, utilizando um datetime + ID para buscar registros na condição `WHERE`. Ambas utilizam de um ponto inicial, algo como `LAST_ID` uma quantidade máxima de registros `LIMIT`, e o próximo ponto inicial.

- A melhor maneira de pensar é se perguntar qual problema o usuário quer resolver. Se o usuário quer acessar uma página em específico, então seria melhor utilizar `Page-Based Pagination`, porque não temos um registro para dar sequência nos próximos registros. Porém se o usuário quer acessar dados a partir de algum registro em diante, então `Cursor/Keyset Pagination` é a melhor escolha, porque temos um registro e conseguimos buscar os próximos baseado nesse registro.

# Processamento em Lotes
- Consiste em processar dados em `Batch` e `Chunk` ao invés de tudo de uma vez, particionando registros grandes em menores, facilitando o processamento dos dados.

- `Batch Process` é o processo de agrupar operações em lotes. Em vez de processar o registro 1, 2 e 3, fazemos o processamento de 10K registros de uma única vez. `Chunking Process` é o processo de particionar os dados. Em vez 1M registros, fazemos a divisão em 100 chunks de 10K.

- Ambas as abordagens lidam com processamento em lotes. Por exemplo, `Leia/Escreva 1000 > Leia/Escreva 1000 > Leia/Escreva 1000`, continuamente. Pode ser feito utilizando `Offset` e `Cursor/Keyset`, sendo as vantagens e desvantagens também verdadeiras, com o Offset sendo mais lento e ambos controlando a memória da aplicação.

- Enquanto a paginação devolve dados limitados e específicos baseados em página ou cursor/keyset, o processamento em lotes lê ou escreve continuamente até que todos os dados sejam processados, evitando que a memória da aplicação exploda. Também é importante em cenários de grandes volumes de dados ou execução de lógica, porque longos locks, transaction logs, bloqueios e rollbacks se tornam caros demais.

- `Streaming` faz o processamento continuamente, os dados chegam e são processados. Não existe necessariamente um fim, apenas `Evento > Processamento`.

- `Windowing` realiza o processamento em janelas, processando todos os eventos dos últimos 5 minutos, ou 1000 eventos por vez etc.
