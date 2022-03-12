import sys
import json
import re
from SPARQLWrapper import SPARQLWrapper, JSON

localURL = "http://solid.boltz.cs.cmu.edu:3030/Demo"
#localURL = "http://localhost:3030/Demo"
queryPrefix = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX kgo: <http://solid.boltz.cs.cmu.edu:3030/ontology/>
PREFIX boltz: <http://solid.boltz.cs.cmu.edu:3030/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX qudt:  <http://qudt.org/schema/qudt/>
PREFIX unit: <http://qudt.org/vocab/unit/>
"""

#Pulled from alligator3, SPARQL querries the specified server for a JSON
def queryServer(endpointURL, query):
    userAgent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpointURL, agent=userAgent)
    sparql.setCredentials('query', 'querypassword')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


#This function takes a Qid and recursively prints a tree of all Nodes
#   in the tree originating at Qid, with initial depth 'depth'
def findBelowRec(Qid, depth):
    nameQuery = queryPrefix + "SELECT DISTINCT ?name WHERE {boltz:" + Qid + " kgo:taxonName ?name }"
    nameResults = queryServer(localURL, nameQuery)
    print("-"*depth + nameResults["results"]["bindings"][0]["name"]["value"])
    childrenQuery = queryPrefix + "SELECT DISTINCT ?child WHERE {?child kgo:subTaxonOf boltz:" + Qid + "}"
    childrenResults = queryServer(localURL, childrenQuery)
    for result in childrenResults["results"]["bindings"]:
        childQid = re.search("Q\d+",result["child"]["value"]).group()
        findBelowRec(childQid,depth+1)

#This function finds the Qid of a node with prefLabel or taxonName == name
#   then recursively finds the taxonmic tree below it using findBelowRec
def findBelow(name):
    nQuery = queryPrefix + "SELECT DISTINCT ?Q WHERE {?Q kgo:taxonName|skos:prefLabel \"" + name + "\"@en. }"
    nResults = queryServer(localURL, nQuery)
    if (len(nResults["results"]["bindings"])) == 0:
        print("Cannot find a Taxon with name: " + name)
    else:
        for result in nResults["results"]["bindings"]:
            Qid = re.search("Q\d+",result["Q"]["value"]).group()
            findBelowRec(Qid,0)

#This function finds all nodes with prefLabel or taxonName == name
#   then prints the hierarchy from 'Biota' to those Nodes in descending order
def findAbove(name):
    nQuery = queryPrefix + "SELECT DISTINCT ?name ?superName WHERE {?Q kgo:taxonName|skos:prefLabel \"" + name + "\"@en. ?Q kgo:subTaxonOf* ?super . ?super kgo:taxonName ?name . ?super kgo:subTaxonOf [ kgo:taxonName ?superName ] .}"
    nResults = queryServer(localURL, nQuery)
    if (len(nResults["results"]["bindings"])) == 0:
        print("Cannot find a Taxon with name: " + name)
    else:
        hierarchy = []
        pastName = None
        for result in nResults["results"]["bindings"]:
            newName = [result["name"]["value"]]
            if pastName == None or newName[0] == pastName:
                hierarchy += newName
            pastName = result["superName"]["value"]
        hierarchy += [pastName]
        hierarchy.reverse()
        print(" -> ".join(hierarchy))

if __name__ == '__main__':
    # print("FindAbove: Bird")
    # findAbove("Bird")
    # print("\nFindBelow: Bird")
    # findBelow("Bird")
    print("\nFindAbove: Reptilia")
    findAbove("Reptilia")
    # print("\nFindBelow: Biota")
    #findBelow("Biota")
