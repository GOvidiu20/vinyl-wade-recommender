# from rdflib import Graph, Literal, Namespace, URIRef, XSD
# from rdflib.namespace import DCTERMS, RDF
#
# file_path = '../data/vinyl.ttl'
#
#
# g = Graph()
# g.parse(file_path, format="turtle")
#
# ns1 = Namespace("http://example.org/")
#
# for subject, predicate, obj in g:
#     if predicate == DCTERMS.subject:
#         current_subject = obj.value
#         new_subject = current_subject.replace(" music", "")
#         g.remove((subject, predicate, obj))
#         g.add((subject, predicate, Literal(new_subject, datatype=XSD.string)))
#
# output_file_path = 'modified_file.ttl'
# g.serialize(output_file_path, format='turtle')