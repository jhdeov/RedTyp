This file describes how a user can create their own 2-way FST recipe in such that a way that our python implementation can interpret it.

The structure of a 2-way FST is simple. Consider the following 2-way FST recipe for Initial-C reduplication:

>> #First C copying with epenthesis
		#If the word starts with C, then that C is reduplicated 
		#A morphologically or phonologically specified string is cross-linguistically often placed between the two consonants
		#I model this epenthetic string as [a]
		#The function is not defined for an input which starts with anything other than C 
		#e.g. patak --> pa~patak, ata --> undefined
		#alphabet type = char

>>what type of alphabet will you use = keyboard ipa

>>functions  = 0	

>>#states type = string
		states = ['start', 'output first C', 'return', 'continue output', 'end']
		initial states = [ 'start' ] 
		initial value = ''	
		final states = [ 'end' ]
>>('start', '#') =  ('output first C', '', 1)
		('output first C', \consonants) =  ('return', \ID, 1)
		('return', \alphabet)  = ('return', '', -1)
		('return','#') =  ('continue output', 'a~',1)
		('continue output', \alphabet) =  ('continue output', \ID, 1)
		('continue output', '%') =  ('end', '', 1)

1. Initial comments: the first few lines of the 2-way FST recipe are comments which describe the function modeled by the 2-way FST

>>	#First C copying with epenthesis
		#If the word starts with C, then that C is reduplicated 
		#A morphologically or phonologically specified string is cross-linguistically often placed between the two consonants
		#I model this epenthetic string as [a]
		#The function is not defined for an input which starts with anything other than C 
		#e.g. patak --> pa~patak, ata --> undefined
		#alphabet type = char
	
	
In the case of initial-C reduplication, the 2-way FST recipe describes how the function will repeat the word-initial consonant and add a pre-specified vowel 'a' between the two copies

2. Alphabet: the alphabet can be either defined as "keyboard ipa" or "user". For now let us describe what  "keyboard ipa" is.

>>	what type of alphabet will you use = keyboard ipa
		
The "keyboard ipa" consists of segments which can be found on a QWERTY keyboard. It consists of the following subalphabets:

>>	consonants = [ 'p', 't', 'k', 'b', 'd', 'g', 'm', 'n', 'f', 'v', 's', 'z', 'x', 'h', 'r', 'l', 'w', 'j', 'c', 'q']
		vowels = [ 'a', 'e', 'i', 'o', 'u', 'y', '\`a', '\`e', '\`i', '\`o', '\`u', '\`y',  '\`a:', '\`e:',' \`i:', '\`o:', '\`u:', '\`y:', 'a:','e:','i:','o:','u:','y:']  
		long_vowels = [ '\`a:', '\`e:', '\`i:', '\`o:', '\`u:', '\`y:',  'a:', 'e:', 'i:', 'o:', 'u:', 'y:']
		short_vowels = [ 'a', 'e', 'i', 'o', 'u', 'y', '\`a', '\`e', '\`i', '\`o', '\`u', '\`y' ]
		stressed_vowels = [ '\`a', '\`e', '\`i', '\`o', '\`u', '\`y',  '\`a:', '\`e:', '\`i:', '\`o:', '\`u:', '\`y:']
		unstressed_vowels =[ 'a', 'e', 'i', 'o', 'u', 'y',   'a:', 'e:', 'i:', 'o:', 'u:', 'y:' ]
		boundaries = [ '+', '.' ]

The alphabet is the union of the above subalphabets.	
Note that the above list of subalphabet is not and CANNOT be listed in the 2-way FST recipe when our type of alphabet is set to "keyboard ipa"	
Note how stressed_vowels and long_vowels use \` and : to mark stress and length. A stressed long vowel '\`a:' is a multicharacter symbol.
		
3. Functions: some reduplicative processes carry out specific transformations over specific input symbols, e.g. nasalization, vowel lengthening, etc. 
Our example 2-way FST recipe for Initial-C reduplication doesn't any use any such functions so set number of functions is to 0

>> functions  = 0	
		
Note that 0 is a misnomer. Every 2-way FST recipe comes with an implicit identity function ID which maps an input string to itself in the output. This is described this in part 5.

4. State description: The states are listed and described here. The first line is a comment which for now doesn't play any role.

>>#states type = string

The second line lists all states used by the 2-way FST. Note that an individual state CANNOT include a parenthesis symbol '(', ')' or comma ','. This is because of the way we've designed our python interpreter.

>>states = ['start', 'output first C', 'return', 'continue output', 'end']

The third line lists the initial states
		
>>initial states = [ 'start' ] 

The fourth line lists the initial value. 

>>	initial value = ''	

The fifth line lists the final states
		
>>final states = [ 'end' ] 

5. Tranisitons: The transitional arcs for the 2-way FST are written using the following format:

>>	(input state, input symbol) = (output state, output string, direction)
		
For example in the case of our Initial-C reduplication recipe, it has following transitional arcs:

>>	('start', '#') =  ('output first C', '', 1)
		('output first C', \consonants) =  ('return', \ID, 1)
		('return', \alphabet)  = ('return', '', -1)
		('return','#') =  ('continue output', 'a~',1)
		('continue output', \alphabet) =  ('continue output', \ID, 1)
		('continue output', '%') =  ('end', '', 1)
		
The input state and output state must be a string flanked by the single quotation marks: 'start' or 'output fisrt C'

The input symbol can either be an individual symbol flanked by single quotation marks: '#' or '%'
Note that the symbols '#' and '%' are used to mark the left and right edge of an input.

Or it can be a subalphabet like the ones described in part 2. A subalphabet always starts with a backslash symbol: \consonants is for any consonant in our alphabet, \alphabet for any symbol in our alphabet

The output string can either be the empty string '', or a string of characters 'a~' or a function \ID.

A function must start with a backslash '\'. Its name must either be ID (short for the identity function) or one of the functions described or listed in part 3.
The identity function ID maps a string to itself.
More examples of functions are provided later.

Note that final state can only be  reached after the right-edge boundary '%' has been read.

6. User defined alphabets: A user can create his own 2-way FST recipe using a different alphabet which can include IPA symbols. 
In the case of our initial-C reduplication example, the following can be changed from:

>>	what type of alphabet will you use = keyboard ipa

into:

>>	what type of alphabet will you use = user
		alphabet = ['p','t','k','a']
		subalphabets = 2
		consonants = ['p','t','k']
		vowels = ['a']
		
The lines above are explained as follows.

The user has to define his complete alphabet:

>>	alphabet = ['p','t','k','a']

The user must specify the number of subalphabets he wants to create

>>	subalphabets = 2

The user must write the name of each subalphabet and its entries

>>	consonants = ['p','t','k']
		vowels = ['a']

With the above user-defined alphabet, the 2-way FST recipe will still model initial-C reduplication but with a much smaller alphabet consisting of only three consonants and one vowel.

7. User defined functions: Some reduplicative processes may involve changes to input segments, such as voicing a consonant in the reduplicant.

For example in the case of initial-C reduplication, the following line can be changed from: 

>> functions  = 0	

into:
	
>>	functions = 1
		voice = { ('p', 'b'),('t','d'), ('k','g') }

The first line specifies the number of user-defined functions, while the second line lists pairs of input symbols and output strings that the input symbols (e.g. 'p') undergo the function (voicing) to output a string ('b')

To see how this function can be used in the transitions, change the following line:

>>('output first C', \consonants) =  ('return', \ID, 1)

into:

>>	('output first C', \consonants) =  ('return', \voice, 1)

Note how the function voice needs to be written after a backslash symbol \
With this altered transitional arc, the 2-way FST will now voice the initial consonant in the reduplicant. For example for the input strings:

>>pata
patak
apata
taka

 		
The python interpreter will implement the modified 2-way FST recipe and create a "output_strings.txt" file which contains the following:

>> pata	-->	ba~pata
		pataka	-->	ba~pataka
		apata	-->	 --- there was an error because couldn't find output state for the input state+input symbol pair (output first C,a)
		taka 	--> da~taka
		
The output string portion of a transition arc can also combine both strings and functions. For example the transition ar 

>>	('output first C', \consonants) =  ('return', \voice, 1)
		
into:

>>	('output first C', \consonants) =  ('return', [\voice 'i' \ID], 1)
		
Note how the output string portion of the arc has to be flanked by brackets []

With this altered transitional arc, the 2-way FST will now voice the initial consonant, add a vowel 'i', and make another copy of the consonant without voicing it.For example for the input strings:

>>pata
		pataka
		apata
		taka

The python interpreter will implement the modified 2-way FST recipe and create a "output_strings.txt" file which contains the following:

>> pata	-->	bipa~pata
		pataka	-->	bipa~pataka
		apata	-->	 --- there was an error because couldn't find output state for the input state+input symbol pair (output first C,a)
		taka	-->	dita~taka
		
8. Set differences in input symbols: The input symbol can be written in the recipe's transition arcs as either an individual character (e.g. '#') or as a set of characters (a subalphabet, e.g. consonants).
In some cases, set differences may be needed, e.g. the 2-way FST will go from an input state 'q' to an ouput state 'p' and output a string 'o' if the input symbol was any consonant EXCEPT for p.
For example in the case of initial-C reduplication, the following line can be changed from:

>>('output first C', \consonants) =  ('return', [\voice 'i' \ID], 1)

into:

>>('output first C', {\consonants - 't'}) =  ('return', [\voice 'i' \ID], 1)

With this altered transitional arc, the 2-way FST will now voice the initial consonant, add a vowel 'i', and make another copy of the consonant without voicing it.
However it will crash for an input which starts with 't'.
For example for the input strings:

>>pata
		pataka
		apata
		taka

The python interpreter will implement the modified 2-way FST recipe and create a "output_strings.txt" file which contains the following:

>>pata	-->	bipa~pata
		pataka	-->	bipa~pataka
		apata	-->	 --- there was an error because couldn't find output state for the input state+input symbol pair (output first C,a)
		taka	-->	 --- there was an error because couldn't find output state for the input state+input symbol pair (output first C,t)
