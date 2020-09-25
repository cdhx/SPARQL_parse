# SPARQL-parse
Help you get attribute/component of a SPARQL query, and query it (if you have a local endpoint)

```python
#Initial a SPARQL object 
sparql_query='SELECT DISTINCT ?uri WHERE { ?x <http://dbpedia.org/property/international> <http://dbpedia.org/resource/Muslim_Brotherhood> . ?x <http://dbpedia.org/ontology/religion> ?uri  . ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/PoliticalParty>}'
a=SPARQL(sparql_query)

#Get the "former part" of a SPARQL(former part means the string before "WHERE" in SPARQL)
a.former
Out[1]: 'SELECT DISTINCT ?uri'

#Get the "where part" of a SPARQL(where part means the part which store triple)
a.where
Out[2]: 'WHERE {?x <http://dbpedia.org/property/international> <http://dbpedia.org/resource/Muslim_Brotherhood> . ?x <http://dbpedia.org/ontology/religion> ?uri . ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/PoliticalParty>}'

#Get a abbreviation version of SPARQL(e.g. <http://dbpedia.org/property/international> -> dbp:international)
a.abbr_sparql
Out[3]: 'SELECT DISTINCT ?uri WHERE {?x dbp:international dbr:Muslim_Brotherhood . ?x dbo:religion ?uri . ?x rdf:type dbo:PoliticalParty}'

#Get all link in a SPARQL
a.link
Out[4]: 
['<http://dbpedia.org/property/international>',
 '<http://dbpedia.org/resource/Muslim_Brotherhood>',
 '<http://dbpedia.org/ontology/religion>',
 '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
 '<http://dbpedia.org/ontology/PoliticalParty>',
 'rdf:type']

#Generalize SPARQL to get a template
a.template
Out[5]: 'SELECT DISTINCT ?uri WHERE {?x <E/R> <E/R> . ?x <E/R> ?uri . ?x <E/R> <E/R>}'

#Get query type(ASK,COUNT,SELECT)
a.intent
Out[6]: 'SELECT'

#Get triple number in "WHERE PART"
a.triple_num
Out[7]: 3

#Where is the variable we ask(aka the variable that represented answer)
a.firstVar
Out[8]: '?uri'

#All variable appear in SPARQL
a.all_var
Out[9]: ['?uri', '?x']

#Query this SPARQL(automatically get you ip_address, to use this feature please first deploy a Virtuoso local endpoint on you PC)
a.query()
Out[10]: 
['http://dbpedia.org/resource/Sunni_Islam',
 'http://dbpedia.org/resource/Islam']
```
