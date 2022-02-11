import sys
import json
import re
from SPARQLWrapper import SPARQLWrapper, JSON

localURL = "http://localhost:3030/Demo"
queryPrefix = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX kgo: <http://solid.boltz.cs.cmu.edu:3030/ontology#>
PREFIX boltz: <http://solid.boltz.cs.cmu.edu:3030/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

def queryServer(endpointURL, query):
    userAgent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpointURL, agent=userAgent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def findBelowRec(Qid, depth):
    nameQuery = queryPrefix + "SELECT DISTINCT ?name WHERE {boltz:" + Qid + " kgo:taxonName ?name }"
    nameResults = queryServer(localURL, nameQuery)
    print("-"*depth + nameResults["results"]["bindings"][0]["name"]["value"])
    childrenQuery = queryPrefix + "SELECT DISTINCT ?child WHERE {?child kgo:subTaxonOf boltz:" + Qid + "}"
    childrenResults = queryServer(localURL, childrenQuery)
    for result in childrenResults["results"]["bindings"]:
        childQid = re.search("Q\d+",result["child"]["value"]).group()
        findBelowRec(childQid,depth+1)

def findBelow(name):
    nQuery = queryPrefix + "SELECT DISTINCT ?Q WHERE {?Q kgo:taxonName|skos:prefLabel \"" + name + "\"@en. }"
    nResults = queryServer(localURL, nQuery)
    if (len(nResults["results"]["bindings"])) == 0:
        print("Cannot find a Taxon with name: " + name)
    else:
        for result in nResults["results"]["bindings"]:
            Qid = re.search("Q\d+",result["Q"]["value"]).group()
            findBelowRec(Qid,0)

def findAbove(name):
    nQuery = queryPrefix + "SELECT DISTINCT ?Q WHERE {?Q kgo:taxonName|skos:prefLabel \"" + name + "\"@en. }"
    nResults = queryServer(localURL, nQuery)
    if (len(nResults["results"]["bindings"])) == 0:
        print("Cannot find a Taxon with name: " + name)
    else:
        for result in nResults["results"]["bindings"]:
            Qid = re.search("Q\d+",result["Q"]["value"]).group()
            hierarchy = []
            while(Qid != None):
                nameQuery = queryPrefix + "SELECT DISTINCT ?name WHERE {boltz:" + Qid + " kgo:taxonName ?name }"
                nameResults = queryServer(localURL, nameQuery)
                hierarchy += [nameResults["results"]["bindings"][0]["name"]["value"]]
                parentQuery = queryPrefix + "SELECT DISTINCT ?parent WHERE {boltz:" + Qid + " kgo:subTaxonOf ?parent}"
                parentResult = queryServer(localURL, parentQuery)
                if (len(parentResult["results"]["bindings"])) == 0:
                    hierarchy.reverse()
                    print(" -> ".join(hierarchy))
                    break
                else:
                    Qid = re.search("Q\d+",parentResult["results"]["bindings"][0]["parent"]["value"]).group()





if __name__ == '__main__':
    # findBelow("Tetrapoda")
    #findBelow("Biota")

    findAbove("Bird")
    findBelow("Bird")
