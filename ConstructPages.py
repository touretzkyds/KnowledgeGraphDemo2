import sys
import json
import re
from SPARQLWrapper import SPARQLWrapper, JSON

#localURL = "http://solid.boltz.cs.cmu.edu:3030/Demo"
localURL = "http://localhost:3030/Demo/sparql"
queryPrefix = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX kgo: <http://solid.boltz.cs.cmu.edu:3030/ontology/>
PREFIX boltz: <http://solid.boltz.cs.cmu.edu:3030/data/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX qudt:  <http://qudt.org/schema/qudt/>
PREFIX unit:  <http://qudt.org/vocab/unit/>
PREFIX qkdv: <http://qudt.org/vocab/dimensionvector/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX list: <http://jena.apache.org/ARQ/list#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
"""

preHTML = '''
<!DOCTYPE html>
<html>
  <head>
    <title>Apache Jena Fuseki - documentation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <link href="css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="css/font-awesome.min.css" rel="stylesheet" media="screen">
    <link href="css/codemirror.css" rel="stylesheet" media="screen">
    <link href="css/qonsole.css" rel="stylesheet" media="screen">
    <link href="css/jquery.dataTables.css" rel="stylesheet" media="screen">
    <link href="css/fui.css" rel="stylesheet" media="screen">

    <!--[if lt IE 9]>
      <script src="../js/lib/html5shiv.js"></script>
      <script src="../js/lib/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <nav class="navbar navbar-default" role="navigation">
      <div class="container">
        <div class="row">
          <!-- Brand and toggle get grouped for better mobile display -->
          <div class="navbar-header">
            <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
              <span class="sr-only">Toggle navigation</span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
              <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="index.html">
              <img src="images/jena-logo-notext-small.png" alt="Apache Jena logo" title="Apache Jena" />
              <div>Apache<br />Jena<br /><strong>Fuseki</strong></div>
            </a>
          </div>

          <!-- Collect the nav links, forms, and other content for toggling -->
          <div class="collapse navbar-collapse navbar-ex1-collapse">
            <ul class="nav navbar-nav">
              <li class=""><a href="index.html"><i class="fa fa-home"></i></a></li>
              <li class=""><a href="dataset.html"><i class="fa fa-database"></i> dataset</a></li>
              <li class=""><a href="manage.html"><i class="fa fa-cogs"></i> manage datasets</a></li>
              <!-- JENA-887 not yet implemented
              <li class=""><a href="services.html"><i class="fa fa-wrench"></i> services</a></li>
              -->
              <li class="active"><a href="documentation.html"><i class="fa fa-info-circle"></i> help</a></li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
              <li class="status-indicator">
                <div>Server<br />status:</div>
              </li>
              <li class="status-indicator">
                <a class="" href="#admin/server-log.html" id="server-status-light" title="current server status">
                  <span class="server-up"></span>
                </a>
              </li>
            </ul>
          </div><!-- /.navbar-collapse -->
        </div><!-- /row -->
      </div><!-- /container -->
    </nav>

    <div class="container">
'''

postHTML = '''
    </div>

    <script src="../js/lib/jquery-1.10.2.min.js"></script>
    <script src="../js/lib/bootstrap.min.js"></script>
  </body>
</html>
'''

def queryServer(endpointURL, query):
    userAgent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(endpointURL, agent=userAgent)
    sparql.setCredentials('query', 'querypassword')
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def constructTurtle(ttlFile):
    ontFile = open("../../webapp/data/" + ttlFile[:-4].lower(), "w")
    ontFile.write(preHTML)
    ontFile.write("<pre style=\"word-wrap: break-word; white-space: pre-wrap;\">")
    fullTTL = open(ttlFile, "r")
    ontFile.write(fullTTL.read().replace("<","&lt;").replace(">","&gt;"))
    ontFile.write("</pre>")
    ontFile.write(postHTML)
    ontFile.close()

def constructOntPage(pageName):
    ontFile = open(pageName.replace("http://solid.boltz.cs.cmu.edu:3030","../../webapp"), "w")
    ontFile.write(preHTML)
    ontQuery = queryPrefix + "SELECT DISTINCT ?pred ?obj WHERE { kgo:" + pageName.rsplit('/', 1)[-1] + " ?pred ?obj } ORDER BY (?pred)"
    ontRes = queryServer(localURL, ontQuery)
    ontFile.write("<h1>" + pageName.rsplit('/', 1)[-1] + "</h1><p> ")
    featuresList = ""
    for result in ontRes["results"]["bindings"]:
        if result['pred']['value'] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            ontFile.write("<a href=\""+result['obj']['value']+ "\">" + result['obj']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a> ")
        else:
            featuresList += "<li> <a href=\""+result['pred']['value']+ "\">" + result['pred']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a>: "
            if result['obj']['type'] == 'uri':
                featuresList += "<a href=\""+result['obj']['value']+ "\">" + result['obj']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a></li>"
            else:
                featuresList += "<i>" + result['obj']['value'].rsplit('/', 1)[-1] + "</i></li>"
    ontFile.write("</p><h4>Features</h4><ul>")
    ontFile.write(featuresList)
    ontFile.write("</ul>")
    ontFile.write(postHTML)
    ontFile.close()

def constructDataPage(pageName):
    ontFile = open(pageName.replace("http://solid.boltz.cs.cmu.edu:3030","../../webapp"), "w")
    ontFile.write(preHTML)
    print("-"*60)
    ontQuery = queryPrefix + "SELECT DISTINCT ?pred ?obj ?list ?obj2 ?pred2 WHERE { BIND ( boltz:" + pageName.rsplit('/', 1)[-1] + " as ?Q) ?Q ?pred ?obj. OPTIONAL { ?Q ?pred [ list:index (?pos ?list ) ] } OPTIONAL { ?Q ?pred [ rdf:type qudt:Quantity ]. ?Q ?pred [ ?pred2 ?obj2 ]. } OPTIONAL { ?Q ?pred [ rdf:type kgo:Location ]. ?Q ?pred [ ?pred2 ?obj2 ]. } } ORDER BY ?pred ?pos ?pred2"
    ontRes = queryServer(localURL, ontQuery)
    header = "<h1> "
    altHeader = ""
    subHeader = ""
    featuresList = ""
    bNode = None
    for result in ontRes["results"]["bindings"]:
        print(result['pred']['value'])
        if result['pred']['value'] == "http://www.w3.org/2004/02/skos/core#prefLabel":
            header += result['obj']['value']
        elif result['pred']['value'] == "http://www.w3.org/2004/02/skos/core#altLabel":
            altHeader += result['obj']['value']
        elif result['pred']['value'] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            subHeader += "<a href=\""+result['obj']['value']+ "\">" + result['obj']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a> "
        elif result['obj']['type'] == 'bnode':
            if bNode == None:
                featuresList += "<li> <a href=\""+result['pred']['value']+ "\">" + result['pred']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a>: <ul>"
            elif bNode != result['obj']['value']:
                featuresList += "</ul></li><li> <a href=\""+result['pred']['value']+ "\">" + result['pred']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a>: <ul>"
            bNode = result['obj']['value']
            if 'list' in result:
                featuresList += "<li><a href=\""+result['list']['value']+ "\">" + result['list']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a></li>"
            else:
                featuresList += "<li> <a href=\""+result['pred2']['value']+ "\">" + result['pred2']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a>: "
                if result['obj2']['type'] == 'uri':
                    featuresList += "<a href=\""+result['obj2']['value']+ "\">" + result['obj2']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a></li>"
                else:
                    featuresList += "<i>" + result['obj2']['value'].rsplit('/', 1)[-1] + "</i></li>"

        else:
            if bNode != None:
                bNode = None
                featuresList += "</ul></li>"
            featuresList += "<li> <a href=\""+result['pred']['value']+ "\">" + result['pred']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a>: "
            if result['obj']['type'] == 'uri':
                featuresList += "<a href=\""+result['obj']['value']+ "\">" + result['obj']['value'].rsplit('/', 1)[-1].rsplit('#', 1)[-1] + "</a></li>"
            else:
                featuresList += "<i>" + result['obj']['value'].rsplit('/', 1)[-1] + "</i></li>"
    ontFile.write(header + "</h1><h4> " + pageName.rsplit('/', 1)[-1] + "</h4><i> " +altHeader + "</i><p> "+ subHeader)
    ontFile.write("</p><h4>Features</h4><ul>")
    ontFile.write(featuresList)
    ontFile.write("</ul>")
    ontFile.write(postHTML)
    ontFile.close()


def constructPages():
    nQuery = queryPrefix + "SELECT DISTINCT ?element WHERE { ?element rdf:type ?type }"
    nResults = queryServer(localURL, nQuery)
    for result in nResults["results"]["bindings"]:
        if result['element']['type'] == 'uri':
            if "ontology" in result['element']['value']:
                constructOntPage(result['element']['value'])
            if "data" in result['element']['value']:
                constructDataPage(result['element']['value'])



if __name__ == '__main__':
    constructTurtle("Ontology.ttl")
    # constructTurtle("Data.ttl")
    # constructTurtle("Imports.ttl")
    constructPages()
