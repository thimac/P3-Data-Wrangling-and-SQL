
PROJETO 3 - LIMPANDO DADOS DO OPENSTREETMAP

O projeto é composto pelos seguintes arquivos:

     1 - main.ipynb (arquivo principal com as consultas e o relatório)
     2 - saoPaulo-OSM.osm (arquivo com o xml usado na análise): https://www.openstreetmap.org/export#map=13/-23.5628/-46.6265
     4 - audit.py (arquivo onde foi feito a auditoria dos dados)
     5 - cleaning2csv.py (arquivo onde foi feito a limpeza e extração para CSVs)
     6 - saoPaulo-OSM.db (arquivo de banco de dados)
     7 - schema.sql (arquivo com as tabelas usadas)
     8 - schema.py (arquivo para criação das tabelas)
   
   
Optou-se por deixar o código python nos arquivos audit.py/cleaningtocsv.py e manipulá-lo por aqui para que o relatório ficasse mais simples de seguir.

A cidade escolhida foi São Paulo - Brasil. Apesar de morar em Brasília, optei por São Paulo por ser um cidade mais conhecida (o que provavelmente faça com que ela tenha mais usuários contribuindo) e com uma densidade populacional maior. No entando, ressalte-se que a área não compreende toda cidade de São Paulo, mas a sua região central e arredores, visto que o mapa ficaria inviável em tamnho para executar em um computador pessoal.

A primeira parte desse relatório trata-se da Extração e Limpesa dos Dados, na segunda parte é a Análise dos dados em SQL  e, por último, uma conclusão e possíveis trabalhos futuros.

REFERÊNCIAS: https://gist.github.com/carlward/54ec1c91b62a5f911c42#file-sample_project-md
 


```python
#Código realizado para auditoria
%run audit.py
```


```python
#Conta quantas tags de cada tipo possuem no arquivo xml
test("count_tags")
```

    {'bounds': 1,
     'member': 38131,
     'meta': 1,
     'nd': 2510996,
     'node': 1692838,
     'note': 1,
     'osm': 1,
     'relation': 5428,
     'tag': 903140,
     'way': 240135}
    
     
    
    


```python
#Tipos de tags
test("key_type")
```

    {'lower': 766448, 'lower_colon': 136146, 'other': 546, 'problemchars': 0}
    
     
    
    


```python
#Auditoria no nome das ruas
test("street_audit")
```

    Dr. Jesuíno Maciel => Rua Dr. Jesuíno Maciel
    Azevedo Junior => Rua Azevedo Junior
    Coronel Melo Oliveira => Rua Coronel Melo Oliveira
    Rocha Pombo => Rua Rocha Pombo
    Capital Federal => Rua Capital Federal
    Sapopemba => Avenida Sapopemba
    Pires da Mota => Rua Pires da Mota
    Álvares Penteado => Rua Álvares Penteado
    Saturno => Rua Saturno
    Al. Ribeirão Preto => Alameda Ribeirão Preto
    Al. José Maria Lisboa => Alameda José Maria Lisboa
    Al. Santos => Alameda Santos
    Al. Sarutaiá => Alameda Sarutaiá
    Rue Arthur Azevedo => Rua Arthur Azevedo
    Av. São Miguel Paulista, 9.167 - sp => Avenida São Miguel Paulista, 9.167 - sp
    Av. Liberdade => Avenida Liberdade
    Agissê => Rua Agissê
    Rúa Dom José de Barros => Rua Dom José de Barros
    Espírito Santo => Rua Espírito Santo
    rua Paulo Orozimbo => Rua Paulo Orozimbo
    rua => Rua
    Castro Alves => Rua Castro Alves
    Conselheiro Furtado => Rua Conselheiro Furtado
    Martim Francisco => Rua Martim Francisco
    Bueno de Andrade => Rua Bueno de Andrade
    praça dom josé gaspar => Praça dom josé gaspar
    Alfonso Bovero => Rua Alfonso Bovero
    Manoel Ramos Paiva => Rua Manoel Ramos Paiva
    


```python
#Auditoria do código postal
test("postcode_audit")
```

    postcode error - format is wrong : 03011-001632
    postcode error - format is wrong : 03009-030299
    postcode error - format is wrong : 03009-030299
    postcode error - format is wrong : 03009-030299
    postcode error - format is wrong : 03009-030299
    postcode error - format is wrong : 03009-030299
    postcode error - format is wrong : 01046-020165
    postcode error - format is wrong : 01050-00081
    postcode error - format is wrong : 03162-0302258
    


```python
#Limpeza e extração de dados para os arquivos CSVs
%run cleaning2csv.py
```

DATA WRAGLING - Limpeza e extração dos dados

Foram utilizados três amostras, uma com menos de 1mb de tamanho, utilizada principalmente para testar o código, outra com aproximadamente 12 mb e uma com pouco mais de 100mb.

ANÁLISES

Antes de realizar a limpeza e extração dos dados, foi criado um banco com uma amostra "crua", recém saída do OSM. Visto que foram feitas algumas consultas para conhecer os dados melhor e, procurar por possíveis anomalias nos campos.

1 - A primeira análise foi verificar se existiam alguma anomalidade nas "keys", principalmente através da exitência de problem chars. Como é visto na execução acima, não foram encontrados.

2 - Após isso, e seguindo mais ou menos o roteiro no que foi visto no curso, realizei a auditoria das ruas. Onde foram econtrados alguns erros de abreviação (Av.) e outros de omissão, como Álvares ao invés de Rua Álvares.

3 - O próximo item auditado foram os códigos postais, onde verificou-se que alguns estavam fora do padrão (00000-000 e, no caso de SP 01000-000 a 09999-999). Desta forma, os que estavam fora do padrão, para não confudir, receberam "wrong size" ou "wrong area" como valor. Todos os códigos também foram padronizados em 0xxxx-xxx, a maioria estava nesse formato, mas alguns apresentavam somente o número, sem o hífem.

4 - Além desses itens, também foram padronizados os telefones, que eram escritos de diversas forma (com e sem o código de área ou o código do país, com e sem hífem ou com parentêses delimitando o código de SP). Todos os telefones ficaram com o padrão +55 11xxxxxxxx para telefones fixos e +55 11xxxxxxxxx para telefones celulares.


ANÁLISE DOS DADOS EM SQL

Tamanho dos arquivos

SaoPaulo-RegiaoCentral.osm ......... 398 MB
SaoPaulo-RegiaoCentral.db .......... 229 MB
nodes.csv ............. 148 MB
nodes_tags.csv ........ 8 MB
ways.csv .............. 15 MB
ways_tags.csv ......... 21 MB
ways_nodes.cv ......... 61 MB


Número total de nodes:
sqlite> SELECT COUNT(*) FROM nodes;
1692838

Número total de ways:
sqlite> SELECT COUNT(*) FROM ways;
240135

Número de usuários:
sqlite> SELECT COUNT(DISTINCT(e.uid)) FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
674


Número dos 10 usários que mais contribuíram:
sqlite> SELECT COUNT(*), e.user FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e GROUP BY e.user ORDER BY COUNT(*) DESC LIMIT 10;
1739637,Bonix-Mapper
91123,Bonix-Importer
56691,"O Fim"
4040,MCPicoli
3943,naoliv
3142,AjBelnuovo
2626,ygorre
2328,EduardoGananca
1799,Wololo
1727,Geogast

Como é possível perceber o usuário Bonix-Mapper é responsável por quse 90% dos dados. 


Número de usúario que contribuíram somente uma vez:
sqlite> SELECT COUNT(*) FROM (SELECT e.user FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e GROUP BY e.user HAVING COUNT(*) = 1);
214

Número de ruas mapeadas na análise:
sqlite> SELECT COUNT(DISTINCT(e.value)) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) e GROUP BY e.key HAVING e.key = "street";
1273

São Paulo possui 48623 logadouro, dados de 2016 (fonte: https://super.abril.com.br/cultura/quantas-ruas-existem-em-sao-paulo/), porém como a área foi selecionada manualmente na região central, essa consulta nos mostra que a maioria da cidade não foi coberta.

Como a área foi selecionanda manualmente e São Paulo possui um região metropolitana, convém verificar se a área em questão compreende parte de outras cidades da região metropolitana.

sqlite> SELECT DISTINCT(e.value) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) e WHERE e.key = "city";
São Paulo
Mooca

Mooca pertence à cidade de São Paulo, a consulta também apresentou outas formas de escrita de São Paulo. 

Seleciona as principais "amenities" que compõem o conjunto de dados
slite>SELECT value, COUNT(*) FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) WHERE key='amenity' GROUP BY value ORDER BY COUNT(*) DESC LIMIT 10;
parking|2306
restaurant|798
bank|422
fuel|288
fast_food|285
pub|189
bicycle_rental|185
pharmacy|164
taxi|163
school|157

São Paulo possui uma densidade populacional altíssima e consquentemente um número de veículos assombroso, tanto é que a cidade possuí "rodízio" de placas na semana. Sem surpresas quanto ao número de estacionamentos.

As 10 cozinhas mais comuns na região:
sqlite> SELECT COUNT(*), value FROM nodes_tags JOIN (SELECT id FROM nodes_tags WHERE value="restaurant") as a ON a.id = nodes_tags.id WHERE key = "cuisine" GROUP BY value ORDER BY COUNT(*) DESC LIMIT 10;
83|regional
32|japanese
22|pizza
16|italian
14|burger
12|arab
8|vegetarian
5|brazilian
5|chinese
5|international

Brasileiro gosta muito de comida japonesa, nada estranho aqui.

Os bancos com mais agências na região central:
sqlite> SELECT COUNT(*), value FROM nodes_tags JOIN (SELECT id FROM nodes_tags WHERE value="bank") as a ON a.id = nodes_tags.id WHERE key="name" GROUP BY value ORDER BY COUNT(*) DESC LIMIT 10;
61|Itaú
55|Santander
47|Bradesco
46|Banco do Brasil
31|Caixa Econômica Federal
27|Banco Itaú
23|Banco Bradesco
14|Caixa
13|Bradesco Prime
12|Banco Santander

Aqui, como trabalhos futuros seria necessário excluir a redundância nos nomes. Como é possível perceber são somente 5 bancos diferentes. Um ideia adicional também seria não permitir, no sistema OSM, a inserção de um banco com nome diferentes.


Religiões mais populares
sqlite> SELECT COUNT(*), value FROM nodes_tags JOIN (SELECT id FROM nodes_tags WHERE value="place_of_worship") as a ON a.id = nodes_tags.id WHERE key="religion" GROUP BY value ORDER BY COUNT(*) DESC LIMIT 10;
68|christian
5|buddhist
4|jewish
1|hindu

O Brasil é uma país majoritariamente cristão, sem surpresas.



COMENTÁRIOS E IDEIAS

Alguns pontos podem ser discutidos com essa breve análise. Primeiro, poucos usuário do OpenStreetMap.org são responsáveis por áreas bastante grande, o que o torna não tão colaborativo assim. Segundo, para se ter uma ideia melhor da cidade seria necessário pegar as outras regiões, não somente a região central. Terceiro, muitos campos precisam de uma limpesa maior, como os valores de algumas amenities, exemplo a amenity bank, que possui algumas redundâncias nos nomes. 

Mesmo com as limitações descritas, foi possível utilizar bem os conhecimento do módulos para realizar um bom data wrangling dos dados, praticar a linguagem python e criar um banco de dados SQL do zero e realizar algumas consultas, que mostram um pouco da realidade da cidade de São Paulo no Brasil.


TRABALHO FUTUROS

Como trabalhos futuros, seria interessante pegar toda a cidade de São Paulo e realizar um data wrangling em todos os campos dos quais se pretende analizar melhor. Além disso, seria interessante que o OSM utilizasse ferramentas para tentar amenizar a redundâcia de alguns 'v's nas tags, uma sugestão seria a criação de campos com um padrão definido, por exemplo, quando alguém for inserir um endereço, limitar o sufixo dos mesmos, ou seja, o colaborador poderá adicinar uma "Rua" somente com essa forma de escrita e não com "R." ou "Rúa". Outra sugestão é que ao inserir um campo novo, esse campo ficaria como padrão, por exemplo, ao inserir o nome de um banco, a primeira forma de escrevê-lo ficaria como padrão para as demais. Obviamente, o benefício da implanatação dessas ideias seria gigantesco, visto que o data wrangling ficaria bem menos trabalhoso, porém, as dificuldades seria bastante grandes, pelas complexidade em implementar tal modificações na plataforma do OSM e, também, porque dificultaria mais para os colaboradores inserirem dados, o que poderia  fazer com que alguns desistissem de dar suas contribuições.



