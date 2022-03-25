all:
	javac *.java
	jar cvf Test.jar *.class

clean:
	rm *.class
	rm *.jar
