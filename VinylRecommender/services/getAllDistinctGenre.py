from rdflib import Graph

file_path = '../data/modified_file.ttl'


g = Graph()
g.parse(file_path, format="turtle")

query = """
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX ns1: <http://example.org/>
SELECT DISTINCT ?subject
WHERE {
    ?s a ns1:Album ;
       dcterms:subject ?subject .
}
"""

results = g.query(query)
distinct_subjects = [str(row.subject) for row in results]
print(distinct_subjects)
