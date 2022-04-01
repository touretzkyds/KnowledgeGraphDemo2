all: web java

web:
	mkdir -p ../../webapp/ontology
	mkdir -p ../../webapp/ontology/css
	mkdir -p ../../webapp/ontology/fonts
	mkdir -p ../../webapp/ontology/images
	cp ../../webapp/css/* ../../webapp/ontology/css
	cp ../../webapp/fonts/* ../../webapp/ontology/fonts
	cp ../../webapp/images/* ../../webapp/ontology/images
	mkdir -p ../../webapp/data
	mkdir -p ../../webapp/data/css
	mkdir -p ../../webapp/data/fonts
	mkdir -p ../../webapp/data/images
	cp ../../webapp/css/* ../../webapp/data/css
	cp ../../webapp/fonts/* ../../webapp/data/fonts
	cp ../../webapp/images/* ../../webapp/data/images
	python3 ConstructPages.py 

java:
	javac *.java
	jar cvf Test.jar *.class

clean:
	$(RM) *.class
	$(RM) *.jar
	$(RM) -r ../../webapp/ontology
	$(RM) -r ../../webapp/data
