# RedTyp
Computational Database for Reduplication

RedTyp is an SQL database of morpho-phonologically reduplicative processes and their corresponding computational implementation: 2-way finite-state transducers.

The utility of the database is twofold:

1) It provides a representative typology of reduplication in natural language, a cross-linguistically common but understudied topic in computational linguistics

2) It provides a computational implementation for the typology of reduplication using 2-way finite-state transducers (2-way FSTs)

Computational morphologists can utilize our database to retrieve computational models for both common and uncommon reduplicative processes. 

Typological morphologists can utilize our database to get a rough picture on the typology of reduplication. 

More information on how 2-way FSTs work can be found in Filiot & Reynier (2016, "Transducers, logic and algebra for functions of finite words").

Author names are anonymous. 

This repository contains the following  files:
1. An SQL file "RedTyp.sql" which is a copy of the SQL database, RedTyp
2. A python file "two_way_interpreter.py" which can interpret the 2-way FST recipes that are found in RedTyp
3. A markdown file "README.md" which is the README file
4. A license file "LICENSE.md"
5. A markdown file "instructions_on_recipe_creation.md" which has instructions on how to read and create 2-way FST recipes that can be interpreted by our python interpreter

The SQL database was created with phpmyadmin and it can imported into any SQL server.

The python file is written in Python 3.0.

# Installing and running RedTyp

In order to see how the SQL database models and implements reduplication using 2-way FSTs, do the following steps:

1. Import the SQL file into an sql server

```bash
 $ mysql -u root -p
 
 mysql> create database redtyp;
 Query OK, 1 row affected (0.01 sec)

mysql> exit

$ mysql redtyp < RedTyp.sql
```

2. Run the following SQL query to get a list of all morphemes that have been modeled so far. The query will return the morpheme's language, its semantic function, and its default shape (initial CV, initial CVC, etc.)

~~~~sql
SELECT `morphemes`.`language`,`morphemes`.`function`,`morphemes`.`default form name`
FROM `morphemes` 
~~~~

3. The above step will return a list of morphemes. For exmaple, the first entry is:

>>		Agta 	diminutive   	Initial C

4. If the user wants to run the 2-way FST for initial C reduplication in Agta, he first need to get the 2-way FST recipe for initial C reduplication.
Do to so, run the following query.		
 
~~~~sql
SELECT `2-way FST`.`FST recipe`
FROM `morphemes`,`matches`,`2-way FST`
WHERE `matches`.`morpheme ID`=`morphemes`.`morpheme ID` AND `matches`.`2-way FST ID`=`2-way FST`.`2-way FST ID` AND `morphemes`.`language`="Agta" AND `morphemes`.`function`="diminutive" AND `morphemes`.`default form name`="Initial C";
~~~~

This returns the "2-way FST recipe" attribute for Agta initial-C reduplication.
The last three conditions in the above WHERE statement can be replaced with any other triple of "language", "function", and "default form name" that the user retrieved from step 3	

5. Given the "2-way	FST recipe" attribute from step 4, copy and save its value as a textfile "FST_recipe.txt". The name can be changed

6. The user must create a textfile "input_strings.txt" which contains input strings for the 2-way FST which will be implement. The name can be changed. This textfile must be encoded with either ANSI or utf-8.
Some 2-way FST recipes require that the input strings have whitespace separate between segments. This is the case when the function of the 2-way FST works over mutlicharacter symbols. The user must read the "Initial comments" section of the 2-way FST recipe file in order to check if this is so
The "instructions_on_recipe_creation.txt" file provides more details on how to read 2-way FST recipes in the next section.
For example for Agta initial-C reduplication, the 2-way FST recipe doesn't require that input symbols be separated by white space. The "input_strings.txt" can contain the following:

>>pata\
patak\
apata\
taka

7. Place the textfiles "FST_recipe.txt" and "input_strings.txt" in the same folder as the python code "two_way_interpreter.py". 

8. In order to run the 2-way FST in the "FST_recipe.txt" file, open the terminal or commandline, and run the following line of code:

		python3 two_way_interpreter.py FST_recipe.txt input_strings.txt 'w'
		
9. The terminal will create the following textfiles: "output_transitions.txt" and "output_strings.txt". The file "output_transitions.txt" contains a list of transition arcs for the 2-way FST. This is not written in shorthand.
The file "output_strings.txt" shows the output of each of the input strings in "input_strings.txt". In case the 2-way FST was not defined for some input string, the reason  why the 2-way FST failed is indicated. For example for the "input_strings.txt" that was run, "output_strings.txt" contains the following:

>>pata	-->	pa\~pata\
pataka	-->	pa\~pataka\
apata	-->	 --- there was an error because couldn't find output state for the input state+input symbol pair (output first C,a)\
taka	-->	ta~taka

10. Users can also create their own 2-way FSTs by writing a list of initial states, final states, and transition arcs as in "output_transitions.txt". To illustrate, rename "output_transitions.txt" to "test_transitions.txt". Open the terminal or commandline, and run the following line of code:

		python3 two_way_interpreter.py test_transitions.txt input_strings.txt 'r'
		
		
# License

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
