# -*- coding: utf-8 -*-

"""
   An interpreter for the 2-way FST recipes used by RedTyp.
   Copyright (C) 2018 Authors
   
   This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. 
   To view a copy of this license, visit http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
   """


import re
import sys
import io
import codecs

def simplifyLines (lines):
	"""Removes lines which start with a comment symbol %, or which are just whitespace/empty lines"""
	newlines=[]
	for line in lines:
		temp=line.strip()
		if len(temp)>0 and temp[0]!='#':
			newlines.append(temp)
	return newlines
	
def breakLineofForm_Alphabet_type_eq_IntStrChar(line):
	"""A lot of inputs are of the form "variable = value" where value ranges from a string to an integer
	We just need to see whats on the right of the equation symbol
	This will extract that"""
	return line.split('=')[1].strip()

def getListofItems(line):
	"""A lot of inputs are of the form "variable = [ 'a', 'b', 'c'] where the value is a list of strings. 
	We need that list. This extracts that list.
	I assume the list values do not include [] or '' or "" """
	rightpart=line.split(']')[0].split('[')[1].split(',')
	refinedRightPart=[]
	for mid in rightpart:
		refinedRightPart.append(mid.strip()[1:-1])
	return refinedRightPart
	
def getListofItems_nospace(line):
	"""A lot of inputs are of the form "variable = [ 1, 2, 3] where the value is a list of integers or really anything without quotation marks. 
	We need that list. 
	I assume the list values do not include [] or '' or "" """
	rightpart=line.split(']')[0].split('[')[1].split(',')
	refinedRightPart=[]
	for mid in rightpart:
		refinedRightPart.append(mid.strip())
	return refinedRightPart

def subalphabetCreator1by1(line):
	"""Returns a tuple (string,list of strings)
	An example is ('consonants', ['p', 't']) """
	right=getListofItems(line)
	left=line.split('=')[0].strip()
	return (left,right)

def subalphabetCreatorIter(lines):
	"""Returns a list of subalphabets which are exemplified above"""
	subalphabets=[]
	for line in lines:
		subalphabet=subalphabetCreator1by1(line)
		#print subalphabet
		subalphabets.append(subalphabet)
	return subalphabets

def functionCreator1by1(line):
	"""Returns a tuple of the form (string, dict) where string is the name of the function
	and where the dict is of the form { string:string}.
	An example input is diphthongReduce = { ('A','a'), ('E','e') }
	An example output is ('dipthongReduce', {'A':'a','E':'e'}) 
	"""
	line=line.strip().split('=')
	leftpart=line[0].strip()
	rightpart=line[1].split('}')[0].split('{')[1].strip()

	"""This will get a list of form [('A,'a'),('B','b')], this list is a list of strings"""
	tuples=re.findall('\(.*?\)',rightpart)
	refinedtuples=[]
	for tuple in tuples: 
		"""This will convert the list into a list of tuples of strings"""
		refinedtuple=re.findall('\'.*?\'',tuple)
		refinedtuple=(refinedtuple[0][1:-1],refinedtuple[1][1:-1])
		refinedtuples.append(refinedtuple) 
	#return refinedtuples
	return (leftpart,dict(refinedtuples))


def functionCreatorIter(lines,alphabetList):
	""" Returns a big dictionary of dictionaries to model the functions
	for example { 'ID':{'a':'a','A':'A'}, 'dipthongReduce':{'A':'A'}}
	We include the ID function here"""
	functions=[]
	for line in lines:
		function=functionCreator1by1(line)
		#print function
		functions.append(function)
	
	ID=[]
	for symbol in alphabetList:
		ID.append((symbol,symbol))
	ID=dict(ID)
	functions.append(("ID",ID))
	return dict(functions)

def transitionCreator1by1(line):
	"""Given a line of the form "(stateQ,inputA)=(stateP,outputB,direction')"
	This function will parse it into a 5-tuple
	I assume the states are flanked by '' and that they do not contain paranthesses or commas or ''
	The input/output are either strings like 'A' which do not include (), or commas or '' OR they are of the form \\string such as \\alphabet
	
	I do not debug for wrong states/symbols here but in the delta function"""
	
	transitionEntry=line.strip()
	try:
		
		#print ( "below is entry")
		#print (transitionEntry)
		leftpart=transitionEntry.split('=')[0].strip()
		rightpart=transitionEntry.split('=')[1].strip()

		refinedLeftPart=leftpart.split(')')[0].split('(')[1].strip().split(',')
		stateQ=refinedLeftPart[0].strip()[1:-1]
		inputA=refinedLeftPart[1].strip()
		if inputA[0]=="'":
			inputA=inputA[1:-1]
		elif inputA[0]=='\\':
			inputA=inputA.strip()

		#print "stateQ and inputA"
		#print stateQ
		#print inputA


		refinedRightPart=rightpart.split(')')[0].split('(')[1].strip().split(',')
		stateP=refinedRightPart[0].strip()[1:-1]
		outputB=refinedRightPart[1].strip()
		if outputB[0]=="'":
			outputB=outputB[1:-1]
		elif outputB[0]=='\\':
			outputB=outputB.strip()
		elif outputB[0]=='[':
			outputB=outputB.strip()
		direction=int(refinedRightPart[2].strip())
		#print "stateP outputB direction"
		#print stateP
		#print outputB
		#print direction
		return (stateQ,inputA,stateP,outputB,direction)
	except :
		print ( 'I got an error while trying to look up this transition\nDid you mistype it?',transitionEntry )
		sys.exit()	

def transitionCreatorIter(lines):
	transitions=[]
	for line in lines:
		transition=transitionCreator1by1(line)
		#print transition
		transitions.append(transition)
	return transitions



	

	
class Reader:
	def __init__(self,FST_file,input_strings,setting):
		"""Take as input two file names: FST file and input_strings, and a string "setting"
		if the setting is set to "w", then our job is to convert an FST written with the FST recipe into a list of transitions
		the FST_recipe_file is read to construct a 2-way FST 
		If the setting is set to "r", then our job is to read the FST written as a list of transitions into a working FST
		The transitions of the 2-way FST are written on the output_transitions file
		The 2-way FST will run on each string entry in input_strings and write their output on the output_strings file
		"""
		if setting=='w':
			f=codecs.open(FST_file,'r','utf-8')#io.open(FST_recipe_file,'r',encoding='utf-8')
			lines=f.readlines()
			if lines[0][0]==u'\ufeff':
				lines[0]=lines[0][1:]#utf8 texts start with the byte encoding symbol, remove it
			
			"""This gets the first line of the FST recipe assuming its the name of the FST"""
			self.name=lines[0][1:].strip()
			self.lines=simplifyLines(lines)
			#print ("ok time to process strings")
			self.processLines()
			#print ("ok i processed the basic lines\n")
			self.transitionSubPartsCreator()
			
			#print ("ok i made the transitions, now ill print  them to the output")
			
			self.output_transitions()
			self.output_strings_file(input_strings)

		elif setting=='r':
			f=codecs.open(FST_file,'r','utf-8') 
			#print('gonna read')
			lines=f.readlines()
			self.name="N/A"
			
			self.lines=simplifyLines(lines)
			self.read_transition_list(lines)
			self.output_transitions()#for the sake of double-checking
			self.output_strings_file(input_strings)
		else:
			print("Wrong setting provided. Must be either 'w' or 'r'")
			
			
	def processLines(self):
		currentLineIndex=0
		

		
		"""This checks if the user is using my default alphabet/subalphabet or if hes defining his own
		If he typed "user", then he will define his own alphabet
		If he typed "default ipa", then he will use the alphabet I already have for consonants vs vowels
		He likewise cannot use functions
		If he typed "simple ipa", then he will use the smaller alphabet I already have for consonants vs vowels 
		which are  mostly characters found on the keyboard plus the IPA symbols for length and stress
		
		"""
		self.line_user_alphabet=self.lines[currentLineIndex]
		self.default_alphabet_wanted=breakLineofForm_Alphabet_type_eq_IntStrChar(self.line_user_alphabet)
		currentLineIndex=currentLineIndex+1
		
		if self.default_alphabet_wanted=="default ipa":
			self.subalphabetCount=6
			consonants=['p', 'b', 'ɸ', 'β', 'm', 'ʙ', 'p͡f', 'f', 'v', 'ɱ', 'ʋ', 't̪', 'd̪', 'θ', 'ð', 't', 'd', 't͡s', 'd͡z', 't͡ɬ', 's', 'z', 't̪ˤ', 'd̪ˤ', 'θˤ', 'ðˤ', 'tˤ', 'dˤ', 'sˤ', 'zˤ', 'n', 'l', 'ɬ', 'ɮ', 'ɾ', 'ɺ', 'r', 'ʧ', 'ʤ', 'ʃ', 'ʒ', 'ɹ', 'ʈ', 'ɖ', 'ʂ', 'ʐ', 'ɳ', 'ɭ', 'ɽ', 'ɻ', 'k̘', 'g̘', 'ɡ̘', 'x̘', 'j', 'k', 'g', 'ɡ', 'ŋ', 'k͡x', 'x', 'ɣ', 'ʟ', 'k̙', 'g̙', 'ɡ̙', 'x̙', 'ɣ̙', 'q', 'ɢ', 'χ', 'ʁ', 'ɴ', 'ʀ', 'ħ', 'ʕ', 'ʔ', 'h', 'ɦ', 'w', 'ʍ', 'k͡p', 'ɡ͡b', 'ɥ', 't͡ɕ', 'd͡ʑ', 'ɕ', 'ʑ', 'c', 'ɟ', 'ç', 'ʝ', 'ɲ', 'ʎ', 'pː', 'bː', 'ɸː', 'βː', 'mː', 'ʙː', 'p͡fː', 'fː', 'vː', 'ɱː', 'ʋː', 't̪ː', 'd̪ː', 'θː', 'ðː', 'tː', 'dː', 't͡sː', 'd͡zː', 't͡ɬː', 'sː', 'zː', 't̪ˤː', 'd̪ˤː', 'θˤː', 'ðˤː', 'tˤː', 'dˤː', 'sˤː', 'zːˤ', 'nː', 'lː', 'ɬː', 'ɮː', 'ɾː', 'ɺː', 'rː', 'ʧː', 'ʤː', 'ʃː', 'ʒː', 'ɹː', 'ʈː', 'ɖː', 'ʂː', 'ʐː', 'ɳː', 'ɭː', 'ɽː', 'ɻː', 'k̘ː', 'g̘ː', 'ɡ̘ː', 'x̘ː', 'jː', 'kː', 'gː', 'ɡː', 'ŋː', 'k͡xː', 'xː', 'ɣː', 'ʟː', 'k̙ː', 'g̙ː', 'ɡ̙ː', 'x̙ː', 'ɣ̙ː', 'qː', 'ɢː', 'χː', 'ʁː', 'ɴː', 'ʀː', 'ħː', 'ʕː', 'ʔː', 'hː', 'ɦː', 'wː', 'ʍː', 'k͡pː', 'ɡ͡bː', 'ɥː', 't͡ɕː', 'd͡ʑː', 'ɕː', 'ʑː', 'cː', 'ɟː', 'çː', 'ʝː', 'ɲː', 'ʎː']
			vowels=['i', 'y', 'ɨ', 'ʉ', 'ɯ', 'u', 'ɪ', 'ʏ', 'ʊ', 'e', 'ø', 'ɘ', 'ɵ', 'ɤ', 'o', 'ɛ', 'œ', 'ɚ', 'ə', 'ɞ', 'ʌ', 'ɔ', 'æ', 'ɶ', 'a', 'ɑ', 'ɒ', 'ĩ', 'ỹ', 'ɨ̃', 'ʉ̃', 'ɯ̃', 'ũ', 'ɪ̃', 'ʏ̃', 'ʊ̃', 'ẽ', 'ø̃', 'ɘ̃', 'ɵ̃', 'ɤ̃', 'õ', 'ɛ̃', 'œ̃', 'ə̃', 'ɞ̃', 'ʌ̃', 'ɔ̃', 'æ̃', 'ɶ̃', 'ã', 'ɑ̃', 'ɒ̃', 'iː', 'yː', 'ɨː', 'ʉː', 'ɯː', 'uː', 'ɪː', 'ʏː', 'ʊː', 'eː', 'øː', 'ɘː', 'ɵː', 'ɤː', 'oː', 'ɛː', 'œː', 'ɚː', 'əː', 'ɞː', 'ʌː', 'ɔː', 'æː', 'ɶː', 'aː', 'ɑː', 'ɒː', 'ĩː', 'ỹː', 'ɨ̃ː', 'ʉ̃ː', 'ɯ̃ː', 'ũː', 'ɪ̃ː', 'ʏ̃ː', 'ʊ̃ː', 'ẽː', 'ø̃ː', 'ɘ̃ː', 'ɵ̃ː', 'ɤ̃ː', 'õː', 'ɛ̃ː', 'œ̃ː', 'ə̃ː', 'ɞ̃ː', 'ʌ̃ː', 'ɔ̃ː', 'æ̃ː', 'ɶ̃ː', 'ãː', 'ɑ̃ː', 'ɒ̃ː', 'ˈi', 'ˈy', 'ˈɨ', 'ˈʉ', 'ˈɯ', 'ˈu', 'ˈɪ', 'ˈʏ', 'ˈʊ', 'ˈe', 'ˈø', 'ˈɘ', 'ˈɵ', 'ˈɤ', 'ˈo', 'ˈɛ', 'ˈœ', 'ˈɚ', 'ˈə', 'ˈɞ', 'ˈʌ', 'ˈɔ', 'ˈæ', 'ˈɶ', 'ˈa', 'ˈɑ', 'ˈɒ', 'ˈĩ', 'ˈỹ', 'ˈɨ̃', 'ˈʉ̃', 'ˈɯ̃', 'ˈũ', 'ˈɪ̃', 'ˈʏ̃', 'ˈʊ̃', 'ˈẽ', 'ˈø̃', 'ˈɘ̃', 'ˈɵ̃', 'ˈɤ̃', 'ˈõ', 'ˈɛ̃', 'ˈœ̃', 'ˈə̃', 'ˈɞ̃', 'ˈʌ̃', 'ˈɔ̃', 'ˈæ̃', 'ˈɶ̃', 'ˈã', 'ˈɑ̃', 'ˈɒ̃', 'ˈiː', 'ˈyː', 'ˈɨː', 'ˈʉː', 'ˈɯː', 'ˈuː', 'ˈɪː', 'ˈʏː', 'ˈʊː', 'ˈeː', 'ˈøː', 'ˈɘː', 'ˈɵː', 'ˈɤː', 'ˈoː', 'ˈɛː', 'ˈœː', 'ˈɚː', 'ˈəː', 'ˈɞː', 'ˈʌː', 'ˈɔː', 'ˈæː', 'ˈɶː', 'ˈaː', 'ˈɑː', 'ˈɒː', 'ˈĩː', 'ˈỹː', 'ˈɨ̃ː', 'ˈʉ̃ː', 'ˈɯ̃ː', 'ˈũː', 'ˈɪ̃ː', 'ˈʏ̃ː', 'ˈʊ̃ː', 'ˈẽː', 'ˈø̃ː', 'ˈɘ̃ː', 'ˈɵ̃ː', 'ˈɤ̃ː', 'ˈõː', 'ˈɛ̃ː', 'ˈœ̃ː', 'ˈə̃ː', 'ˈɞ̃ː', 'ˈʌ̃ː', 'ˈɔ̃ː', 'ˈæ̃ː', 'ˈɶ̃ː', 'ˈãː', 'ˈɑ̃ː', 'ˈɒ̃ː', 'ˌi', 'ˌy', 'ˌɨ', 'ˌʉ', 'ˌɯ', 'ˌu', 'ˌɪ', 'ˌʏ', 'ˌʊ', 'ˌe', 'ˌø', 'ˌɘ', 'ˌɵ', 'ˌɤ', 'ˌo', 'ˌɛ', 'ˌœ', 'ˌɚ', 'ˌə', 'ˌɞ', 'ˌʌ', 'ˌɔ', 'ˌæ', 'ˌɶ', 'ˌa', 'ˌɑ', 'ˌɒ', 'ˌĩ', 'ˌỹ', 'ˌɨ̃', 'ˌʉ̃', 'ˌɯ̃', 'ˌũ', 'ˌɪ̃', 'ˌʏ̃', 'ˌʊ̃', 'ˌẽ', 'ˌø̃', 'ˌɘ̃', 'ˌɵ̃', 'ˌɤ̃', 'ˌõ', 'ˌɛ̃', 'ˌœ̃', 'ˌə̃', 'ˌɞ̃', 'ˌʌ̃', 'ˌɔ̃', 'ˌæ̃', 'ˌɶ̃', 'ˌã', 'ˌɑ̃', 'ˌɒ̃', 'ˌiː', 'ˌyː', 'ˌɨː', 'ˌʉː', 'ˌɯː', 'ˌuː', 'ˌɪː', 'ˌʏː', 'ˌʊː', 'ˌeː', 'ˌøː', 'ˌɘː', 'ˌɵː', 'ˌɤː', 'ˌoː', 'ˌɛː', 'ˌœː', 'ˌɚː', 'ˌəː', 'ˌɞː', 'ˌʌː', 'ˌɔː', 'ˌæː', 'ˌɶː', 'ˌaː', 'ˌɑː', 'ˌɒː', 'ˌĩː', 'ˌỹː', 'ˌɨ̃ː', 'ˌʉ̃ː', 'ˌɯ̃ː', 'ˌũː', 'ˌɪ̃ː', 'ˌʏ̃ː', 'ˌʊ̃ː', 'ˌẽː', 'ˌø̃ː', 'ˌɘ̃ː', 'ˌɵ̃ː', 'ˌɤ̃ː', 'ˌõː', 'ˌɛ̃ː', 'ˌœ̃ː', 'ˌə̃ː', 'ˌɞ̃ː', 'ˌʌ̃ː', 'ˌɔ̃ː', 'ˌæ̃ː', 'ˌɶ̃ː', 'ˌãː', 'ˌɑ̃ː', 'ˌɒ̃ː']
			short_vowels=['i', 'y', 'ɨ', 'ʉ', 'ɯ', 'u', 'ɪ', 'ʏ', 'ʊ', 'e', 'ø', 'ɘ', 'ɵ', 'ɤ', 'o', 'ɛ', 'œ', 'ɚ', 'ə', 'ɞ', 'ʌ', 'ɔ', 'æ', 'ɶ', 'a', 'ɑ', 'ɒ', 'ĩ', 'ỹ', 'ɨ̃', 'ʉ̃', 'ɯ̃', 'ũ', 'ɪ̃', 'ʏ̃', 'ʊ̃', 'ẽ', 'ø̃', 'ɘ̃', 'ɵ̃', 'ɤ̃', 'õ', 'ɛ̃', 'œ̃', 'ə̃', 'ɞ̃', 'ʌ̃', 'ɔ̃', 'æ̃', 'ɶ̃', 'ã', 'ɑ̃', 'ɒ̃', 'ˈi', 'ˈy', 'ˈɨ', 'ˈʉ', 'ˈɯ', 'ˈu', 'ˈɪ', 'ˈʏ', 'ˈʊ', 'ˈe', 'ˈø', 'ˈɘ', 'ˈɵ', 'ˈɤ', 'ˈo', 'ˈɛ', 'ˈœ', 'ˈɚ', 'ˈə', 'ˈɞ', 'ˈʌ', 'ˈɔ', 'ˈæ', 'ˈɶ', 'ˈa', 'ˈɑ', 'ˈɒ', 'ˈĩ', 'ˈỹ', 'ˈɨ̃', 'ˈʉ̃', 'ˈɯ̃', 'ˈũ', 'ˈɪ̃', 'ˈʏ̃', 'ˈʊ̃', 'ˈẽ', 'ˈø̃', 'ˈɘ̃', 'ˈɵ̃', 'ˈɤ̃', 'ˈõ', 'ˈɛ̃', 'ˈœ̃', 'ˈə̃', 'ˈɞ̃', 'ˈʌ̃', 'ˈɔ̃', 'ˈæ̃', 'ˈɶ̃', 'ˈã', 'ˈɑ̃', 'ˈɒ̃', 'ˌi', 'ˌy', 'ˌɨ', 'ˌʉ', 'ˌɯ', 'ˌu', 'ˌɪ', 'ˌʏ', 'ˌʊ', 'ˌe', 'ˌø', 'ˌɘ', 'ˌɵ', 'ˌɤ', 'ˌo', 'ˌɛ', 'ˌœ', 'ˌɚ', 'ˌə', 'ˌɞ', 'ˌʌ', 'ˌɔ', 'ˌæ', 'ˌɶ', 'ˌa', 'ˌɑ', 'ˌɒ', 'ˌĩ', 'ˌỹ', 'ˌɨ̃', 'ˌʉ̃', 'ˌɯ̃', 'ˌũ', 'ˌɪ̃', 'ˌʏ̃', 'ˌʊ̃', 'ˌẽ', 'ˌø̃', 'ˌɘ̃', 'ˌɵ̃', 'ˌɤ̃', 'ˌõ', 'ˌɛ̃', 'ˌœ̃', 'ˌə̃', 'ˌɞ̃', 'ˌʌ̃', 'ˌɔ̃', 'ˌæ̃', 'ˌɶ̃', 'ˌã', 'ˌɑ̃', 'ˌɒ̃']
			long_vowels=['iː', 'yː', 'ɨː', 'ʉː', 'ɯː', 'uː', 'ɪː', 'ʏː', 'ʊː', 'eː', 'øː', 'ɘː', 'ɵː', 'ɤː', 'oː', 'ɛː', 'œː', 'ɚː', 'əː', 'ɞː', 'ʌː', 'ɔː', 'æː', 'ɶː', 'aː', 'ɑː', 'ɒː', 'ĩː', 'ỹː', 'ɨ̃ː', 'ʉ̃ː', 'ɯ̃ː', 'ũː', 'ɪ̃ː', 'ʏ̃ː', 'ʊ̃ː', 'ẽː', 'ø̃ː', 'ɘ̃ː', 'ɵ̃ː', 'ɤ̃ː', 'õː', 'ɛ̃ː', 'œ̃ː', 'ə̃ː', 'ɞ̃ː', 'ʌ̃ː', 'ɔ̃ː', 'æ̃ː', 'ɶ̃ː', 'ãː', 'ɑ̃ː', 'ɒ̃ː', 'ˈiː', 'ˈyː', 'ˈɨː', 'ˈʉː', 'ˈɯː', 'ˈuː', 'ˈɪː', 'ˈʏː', 'ˈʊː', 'ˈeː', 'ˈøː', 'ˈɘː', 'ˈɵː', 'ˈɤː', 'ˈoː', 'ˈɛː', 'ˈœː', 'ˈɚː', 'ˈəː', 'ˈɞː', 'ˈʌː', 'ˈɔː', 'ˈæː', 'ˈɶː', 'ˈaː', 'ˈɑː', 'ˈɒː', 'ˈĩː', 'ˈỹː', 'ˈɨ̃ː', 'ˈʉ̃ː', 'ˈɯ̃ː', 'ˈũː', 'ˈɪ̃ː', 'ˈʏ̃ː', 'ˈʊ̃ː', 'ˈẽː', 'ˈø̃ː', 'ˈɘ̃ː', 'ˈɵ̃ː', 'ˈɤ̃ː', 'ˈõː', 'ˈɛ̃ː', 'ˈœ̃ː', 'ˈə̃ː', 'ˈɞ̃ː', 'ˈʌ̃ː', 'ˈɔ̃ː', 'ˈæ̃ː', 'ˈɶ̃ː', 'ˈãː', 'ˈɑ̃ː', 'ˈɒ̃ː', 'ˌiː', 'ˌyː', 'ˌɨː', 'ˌʉː', 'ˌɯː', 'ˌuː', 'ˌɪː', 'ˌʏː', 'ˌʊː', 'ˌeː', 'ˌøː', 'ˌɘː', 'ˌɵː', 'ˌɤː', 'ˌoː', 'ˌɛː', 'ˌœː', 'ˌɚː', 'ˌəː', 'ˌɞː', 'ˌʌː', 'ˌɔː', 'ˌæː', 'ˌɶː', 'ˌaː', 'ˌɑː', 'ˌɒː', 'ˌĩː', 'ˌỹː', 'ˌɨ̃ː', 'ˌʉ̃ː', 'ˌɯ̃ː', 'ˌũː', 'ˌɪ̃ː', 'ˌʏ̃ː', 'ˌʊ̃ː', 'ˌẽː', 'ˌø̃ː', 'ˌɘ̃ː', 'ˌɵ̃ː', 'ˌɤ̃ː', 'ˌõː', 'ˌɛ̃ː', 'ˌœ̃ː', 'ˌə̃ː', 'ˌɞ̃ː', 'ˌʌ̃ː', 'ˌɔ̃ː', 'ˌæ̃ː', 'ˌɶ̃ː', 'ˌãː', 'ˌɑ̃ː', 'ˌɒ̃ː']
			boundaries = ['-','+','.']
			segments=consonants+vowels
			self.alphabetList=segments+boundaries 
			self.subalphabets=[("consonants",consonants),("vowels",vowels),("alphabet",self.alphabetList),("long_vowels",long_vowels),("short_vowels",short_vowels), ("boundaries",boundaries),("segments",segments)]
			#print ("below alphabet list")
			#print ('\t',self.alphabetList)
			#print ("below subalphabetCount")
			#print ('\t',self.subalphabetCount)
		if self.default_alphabet_wanted=="keyboard ipa":
			self.subalphabetCount=8
			consonants = ['p','t','k','b','d','g','m','n','f','v','s','z','x','h','r','l','w','j','c','q']
			vowels = ['a','e','i','o','u','y', '`a','`e','`i','`o','`u','`y', '`a:','`e:','`i:','`o:','`u:','`y:', 'a:','e:','i:','o:','u:','y:']  
			long_vowels = ['`a:','`e:','`i:','`o:','`u:','`y:', 'a:','e:','i:','o:','u:','y:']
			short_vowels = ['a','e','i','o','u','y', '`a','`e','`i','`o','`u','`y']
			stressed_vowels = ['`a','`e','`i','`o','`u','`y', '`a:','`e:','`i:','`o:','`u:','`y:']
			unstressed_vowels =['a','e','i','o','u','y',  'a:','e:','i:','o:','u:','y:']
			boundaries = ['-','+','.']
			segments = consonants + vowels 
			self.alphabetList=consonants + vowels + boundaries
			self.subalphabets=[("consonants",consonants),("vowels",vowels),("alphabet",self.alphabetList),("short_vowels",short_vowels),("long_vowels",long_vowels),("stressed_vowels",stressed_vowels),("unstressed_vowels",unstressed_vowels), ("boundaries",boundaries),("segments",segments)]
			#print ("below alphabet list`")
			#print ('\t',self.alphabetList)
			#print ("below subalphabetCount")
			#print ('\t',self.subalphabetCount)

		
		elif self.default_alphabet_wanted=="simple ipa":
			self.subalphabetCount=2
			consonants=['b','ʙ','c','ç','ɕ','d','ð','ʤ','d͡z','d͡ʑ','ɖ','f','g','ɢ','ɣ','ɡ','ɡ͡b','h','ħ','ɦ','ɥ','j','ɟ','ʝ','k','k͡p','k͡x','l','ʟ','ɭ','ɬ','ɮ','m','ɱ','n','ɴ','ɲ','ɳ','ŋ','p','ɸ','p͡f','q','r','ʀ','ɽ','ɹ','ʁ','ɺ','ɻ','ɾ','s','ʂ','ʃ','t','ʈ','ʧ','t͡ɕ','t͡ɬ','t͡s','v','ʋ','w','ʍ','x','ʎ','z','ʐ','ʑ','ʒ','ʔ','ʕ','β','θ','χ']
			vowels=['i','y','ɨ','ʉ','ɯ','u','ɪ','ʏ','ʊ','e','ø','ɘ','ɵ','ɤ','o','ɛ','œ','ɚ','ə','ɞ','ʌ','ɔ','æ','ɶ','a','ɑ','ɒ']
			self.alphabetList=consonants+vowels
			self.subalphabets=[("consonants",consonants),("vowels",vowels),("alphabet",self.alphabetList)]
			
			#print ("below alphabet list`")
			#print ('\t',self.alphabetList)
			#print ("below subalphabetCount")
			#print ('\t',self.subalphabetCount)

						
		elif self.default_alphabet_wanted=="user":
			self.line_alphabetList=self.lines[currentLineIndex]
			self.alphabetList=getListofItems(self.line_alphabetList)
			currentLineIndex=currentLineIndex+1
			#print "line_alphabetList"
			#print ("below alphabet list`")
			#print ('\t',self.alphabetList)

			
		
			self.line_subalphabetCount=self.lines[currentLineIndex]
			self.subalphabetCount=int(breakLineofForm_Alphabet_type_eq_IntStrChar(self.line_subalphabetCount))
			currentLineIndex=currentLineIndex+1
			#print ("below subalphabetCount")
			#print ('\t',self.subalphabetCount)

			
			
			self.lines_subalphabets=self.lines[currentLineIndex:(currentLineIndex+self.subalphabetCount)]
			self.subalphabets=subalphabetCreatorIter(self.lines_subalphabets+[self.line_alphabetList])
			
			currentLineIndex=currentLineIndex+self.subalphabetCount
			
		#print ("below subalphabets + alphabet")
		for sub in self.subalphabets:
			#print ('\t',sub)
			for item in sub[1]:
				if item not in self.alphabetList:
					print ("error, the subalphabet "+sub[0]+" has a bad item "+item+" thats not in the alphabet")
					sys.exit()
					
					
			
		
			
		
		
		self.line_functionCount=self.lines[currentLineIndex]
		self.functionCount=int(breakLineofForm_Alphabet_type_eq_IntStrChar(self.line_functionCount))
		currentLineIndex=currentLineIndex+1
		#print ("functionCount")
		#print ('\t',self.functionCount)

		self.lines_functions=self.lines[currentLineIndex:(currentLineIndex+self.functionCount)]
		self.functions=functionCreatorIter(self.lines_functions,self.alphabetList)
		currentLineIndex=currentLineIndex+self.functionCount
		#print ("below functions + ID function")
		for fun in self.functions.items():
			#print ('\t',fun)
			for input_segment in fun[1].keys():
				if input_segment not in self.alphabetList:
					print ("error, the function",fun," has a bad item",input_segment,"thats not in the alphabet")
					sys.exit()
		
	
		

		self.line_stateList=self.lines[currentLineIndex]
		self.stateList=getListofItems(self.line_stateList)
		currentLineIndex=currentLineIndex+1
		#print ("stateList")
		#print ('\t',self.stateList)


		self.line_initialStates=self.lines[currentLineIndex]
		self.initialStateList=getListofItems(self.line_initialStates)
		currentLineIndex=currentLineIndex+1
		#print ("initialStates")
		#print ('\t',self.initialStateList)

		self.line_initialValue=self.lines[currentLineIndex]
		self.initialValue=breakLineofForm_Alphabet_type_eq_IntStrChar(self.line_initialValue)[1:-1]
		currentLineIndex=currentLineIndex+1
		#print ("initialValue")
		#print ('\t',self.initialValue)
		
		self.line_finalStates=self.lines[currentLineIndex]
		self.finalStateList=getListofItems(self.line_finalStates)
		currentLineIndex=currentLineIndex+1
		#print ("finalStates")
		#print ('\t',self.finalStateList)

		self.lines_transitions=self.lines[currentLineIndex:]
		self.transitions=transitionCreatorIter(self.lines_transitions)
		#print ("transitions")
		#for trans in self.transitions:
		#	print ('\t',trans)
			
	def transitionSubPartsCreator(self):
		"""Given a list of edges or 5-tuples (q,a,p,b,d)
		This function breaks the 5-tuples into 3 functions such that given q,a it will return p and b and d
		I debug for erronous state or symbol entries here"""
		self.deltaState={}
		self.deltaOutput={}
		self.deltaDirection={}
		#print ("ok doing the deltas")
		
		for trans in self.transitions:
			#print ("working on interpreting the delta function for the transition:",trans)
			try:
				
				#print ('working on transition: ',trans)
				
				stateQ=trans[0]
				inputA=trans[1]
				stateP=trans[2]
				outputB=trans[3]
				direction=trans[4]
				
				
				#print ('input state is: ',stateQ)
				if stateQ not in self.stateList:
					print ("error, the input state",stateQ,"isnt in state List for the transition:",trans)
					sys.exit()
				#print ('output state is: ',stateP)
				if stateP not in self.stateList:
					print ("error, the output state",stateP,"isnt in state List for the transition:",trans)
					sys.exit()
				#print ('direction is: ',direction)
				if direction not in [0,-1,1]:
					print ("error, the direction symbol",direction," isnt an okay direction  for the transition:",trans)
					sys.exit()
				
				expandedInputA=[]
				#print ('input symbol is:',inputA)
				if inputA[0]=='\\':
					alphCategory=inputA[1:]
					alphabetExists=False
					alphItems=[]
					for alph in self.subalphabets:
						if alphCategory==alph[0]:
							alphabetExists=True
							alphItems=alph[1]
							break
					if not alphabetExists:
						print ("error, the subalphabet",alphCategory,"doesnt exist for the transition:",trans)
						sys.exit()
					expandedInputA=alphItems
				
				elif inputA[0]=='{':
					"""Assume that if the input is a of form {}, then the person wants to do a set difference: alphabet - a
					For now I assume the first element is always of form \\alphabet and the second is either a single symbol or a subalphabet
					
					We should potentially replace this with somehow making the two-way reader read the transitions by ordering the subalphabets"""
					inside_parts=inputA[1:-1].split('-')
						
					alphCategory=inside_parts[0][1:].strip()#remember that the subalphabets are stored as just their names, like "consonants", not "\consonants"
					alphabetExists=False
					alphItems=[]
					#print ("Im checking if the subalphabet",alphCategory,"exists")
					for alph in self.subalphabets:
						#print ("checking if it matches: ",alph[0])
						if alphCategory==alph[0]:
							alphabetExists=True
							#print("it did!")
							alphItems=set(alph[1])
							break
					if not alphabetExists:
						print ("error, the subalphabet",alphCategory," doesnt exist for the transition:",trans)
						sys.exit()
					
					for to_be_removed in inside_parts[1:]:
						to_be_removed=to_be_removed.strip()
						#print ("going to interpret the element",to_be_removed,"in order to remove it")
						if to_be_removed[0]=='\\':
							to_be_removed_category=to_be_removed[1:]#remember that the subalphabets are stored as just their names, like "consonants", not "\consonants"
							to_be_removed_exists=False
							to_be_removed_set=[]
							#print ("Im checking if the subalphabet ",alphCategory," exists")
							for alph in self.subalphabets:
								#print ("checking if it matches: ",alph[0])
								if to_be_removed_category==alph[0]:
									to_be_removed_exists=True
									#print("it did!")
									to_be_removed_set=set(alph[1])
									break
							if not to_be_removed_exists:
								print ("error, the subalphabet",alphCategory," doesnt exist for the transition:",trans)
								sys.exit()
							alphItems.difference_update(to_be_removed_set)
						else:
							string_to_remove=to_be_removed[1:-1]
							#print ('going to remove the string',string_to_remove)
							alphItems.remove(string_to_remove)
					
					expandedInputA=list(alphItems)
		
					
				else:
					#print ('input symbol was not of form \\')
					if inputA not in self.alphabetList+['#','%']:
						print ("error, the input symbol",inputA," isnt in alphabet and isnt a boundary symbol for the transition:",trans)
						sys.exit()
					#print ('input symbol was in alphabet or #,%')
					expandedInputA.append(inputA)
				#print ('expanded inputs are the strings:\n\t',) 
				#for expanded_input in expandedInputA:
				#	print(expanded_input,)
					
				inputoutputPairs=[]
				#print ('output string is: (',outputB,')')
				for i in expandedInputA:
					#print ('working on getting output for the input symbol: ',i)
					if len(outputB)==0:
						#print ('output string was empty')
						inputoutputPairs.append((i,''))
					elif outputB[0]=='\\':
						funCategory=outputB[1:]
						inputoutputPairs.append((i,self.functions[funCategory][i]))
					elif outputB[0]=='[':#this is for the cases of ['m' \ID]
						inside_parts=outputB[1:-1].split()
						potential_output=""
						for inside_part in inside_parts:
							inside_part=inside_part.strip()
							if inside_part[0]=='\\':
								funCategory=inside_part[1:]
								potential_output=potential_output + self.functions[funCategory][i]
							else: #if the insides of the [] isnt \\ then its a string
								potential_output=potential_output+inside_part[1:-1]
							
						inputoutputPairs.append((i,potential_output))
					else: #if the output string doesnt start with [ or \\ then its a string
						#print ('output string was the symbol:', outputB)
						inputoutputPairs.append((i,outputB))
						
				for i,o in inputoutputPairs:
					qa=(stateQ,i)
					#print ('input state + input symbol pair is: ',qa)
					p=stateP
					b=o
					dir=direction
					if qa in self.deltaState:
						print ("error, nondeterminism for the transition:",trans)
						break
					else:
						self.deltaState[qa]=p
						self.deltaOutput[qa]=b
						self.deltaDirection[qa]=dir
			except :
				print ("an error happened while intrepreting the transition:",trans)
				sys.exit()
		#print ("delta state:")
		#for key in sorted(self.deltaState.keys()):
		#	print (key," --> ", self.deltaState[key],", ",self.deltaOutput[key],", ",self.deltaDirection[key])
			
	def output_transitions(self):
		"""Here we determine how the state strings will get mapped to numbers"""
		self.state_to_number={}
		n=0
		for state in self.initialStateList:
			#print ("initial state:",state)
			self.state_to_number[state]=n
			n=n+1
		for state in self.finalStateList:
			#print ("final state:",state)
			self.state_to_number[state]=n
			n=n+1
		for state in self.stateList:
			if state not in self.initialStateList and  state not in self.finalStateList:
				self.state_to_number[state]=n
				n=n+1
		
		"""Here we print out the state to number mapping"""
		f = codecs.open('output_transitions.txt','w','utf-8')#io.open('output_transitions.txt','w',encoding='utf-8')
		f.write(u"#\tThis is the list of transitions arcs for the 2-way FST that implements the following FST recipe:\r\n")
		f.write(u"#\t\t"+self.name+"\r\n")
		
		f.write(u"#\tThe states in our FST recipe were written as strings.\r\n")
		f.write(u"#\tThese get mapped to the following natural numbers:\r\n")
		for state in self.state_to_number.keys():
			f.write (u"#\t\t"+str(self.state_to_number[state])+'\t-->\t'+state+'\r\n')
		f.write(u"#\tThe mapped initial states are:\r\n")
		for state in self.initialStateList:
			f.write (u"#\t\t"+str(self.state_to_number[state])+'\t-->\t'+state+'\r\n')
		f.write(u"#\tThe mapped final states are:\r\n")
		for state in self.finalStateList:
			f.write (u"#\t\t"+str(self.state_to_number[state])+'\t-->\t'+state+'\r\n')
		f.write(u"\r\n\r\n\r\n")
		
		"""Print out the initial and final states"""
		f.write(u"Initial states are = [ %s "%str(self.state_to_number[self.initialStateList[0]]))
		for state in self.initialStateList[1:]:
			f.write (u", "+str(self.state_to_number[state])+" ")
		f.write(u"]\r\n")
		f.write(u"Final states are = [ %s "%str(self.state_to_number[self.finalStateList[0]]))
		for state in self.finalStateList[1:]:
			f.write (u", "+str(self.state_to_number[state]) )
		f.write(u"]\r\n")
		
		f.write(u"\r\n\r\n\r\n")
		
		"""Here we convert our tranisitions into a sorted tuples of input state,input symbol, output state, output string, direction"""
		lines_to_output=[]
		for key in sorted(self.deltaState.keys()):
			lines_to_output.append(str(self.state_to_number[key[0]])+","+key[1]+","+str(self.state_to_number[self.deltaState[key]])+","+self.deltaOutput[key]+","+str(self.deltaDirection[key]))
			#.encode('utf-8')
		lines_to_output.sort()
		for line in lines_to_output:
			f.write(line)# (line.decode('utf-8'))#.encode('utf-8'))
			f.write('\r\n')
		f.close()
			
	"""these functions will run the 2way FST on the input strings
	not sure if they should be methods of a class  or just general methods
	
	meh ill make em be part of class"""			
	def run(self,stateQ,output_so_far,entire_input,index_header):
		"""Given an input state, the output string, the input string, and the location of the reading head,
		this function runs the machine"""
		#print("stateQ:%s outputsofar:%s entireinput:%s indexheader=%s"% (stateQ,output_so_far,entire_input,index_header ) )

		if index_header==len(entire_input):
			#print ("huh i made it here")
			#print (stateQ,output_so_far)
			if stateQ  not in self.finalStateList:
				#print ("this did not end on the final state \"end\" ")
				return (output_so_far+" --- there was an error because we read till the end but didnt end in a final state, but in state " % stateQ)
			#in case youre working on a list of symbols and you dont want to see ' in your output list'
			if type(output_so_far)==list:
				output_so_far= list(filter(lambda x: x!= '', output_so_far))
			return output_so_far
		
		else:
			#print ("reached here2")
			#print ("q:",stateQ)
			#print ("outputsofar:",output_so_far)
			#print ("entire_input:",entire_input)
			#print ("index_header:",index_header)
			inputA=entire_input[index_header]
			#print("inputA:%s"%inputA)
			#print ("scanning input symbol:",entire_input[index_header])
			
			if stateQ not in self.stateList:
				return (output_so_far+" --- there was an error because the input state %s isn't in the state list" % stateQ)
			if inputA not in self.alphabetList + ['#','%']:
				return (output_so_far+" --- there was an error because the input symbol %s isn't in the alphabet" % inputA)
			
			try:
				stateP=self.deltaState[(stateQ,inputA)]
			except:
				#print("k")
				#print(stateQ)
				#print(inputA)
				#print(self.deltaState[(stateQ,inputA)])
				#print ("I got an error while trying to look up the output state  for the input_state+input_symbol pair (",stateQ," , ",inputA,") in the input\nPerhaps a key error?" )
				#sys.exit()
				return (output_so_far+" --- there was an error because couldn't find output state for the input state+input symbol pair ("+stateQ+","+inputA+")")
			try:
				outputB=self.deltaOutput[(stateQ,inputA)]
			except:
				#print ( 'I got an error while trying to look up the output string  for the input_state+input_symbol pair (',stateQ," , ",inputA,') in the input\nPerhaps a key error?' )
				return (output_so_far+" --- there was an error because couldn't find output string for the input state+input symbol pair ("+stateQ+","+inputA+")" )
			
			#print("type of output_so_far " + str(type(output_so_far))) 
			if ( type(output_so_far)==str or type(output_so_far)==unicode):
				output_so_far=output_so_far+outputB
			elif type(output_so_far)==list:
				output_so_far=output_so_far+[outputB]
			direction=self.deltaDirection[(stateQ,inputA)]
			index_header=direction+index_header
			return self.run(stateP,output_so_far,entire_input,index_header)			
		
			
	def transduce(self,input_string):
		"""given an input, this function processes the 2-way FST on the input and prints out the output
		If the 2-way FST's function is not defined on the input, then it crashes"""
		
		"""We first need to determine the initial state and initial value"""
		#print("transducing time")
		#print("so this is list of initial states:%s"%self.initialStateList)
		#print("so this is #1 of initial states:%s"%self.initialStateList[0])
		initialState=self.initialStateList[0]
		initialValue=self.initialValue
		
		"""We determine whether the input is in the form of a list, a string of characters separated by whitespace, or just a string without whitespace"""
		if ( type(input_string)==str) and " " in input_string:#type(input_string)==unicode or -- bugs
		 	#print("yes space")
		 	input_string=input_string.split()
		if type(input_string)==str:#type(input_string)==unicode or  bugs
		 	#print("no space")
		 	input_string=input_string.strip()
		 	input_string="#"+input_string+"%"
		elif type(input_string)==list:
			print ("ok..")
			input_string=["#"]+input_string+["%"]
			print (input_string)
			#if you want to output a list of symbols, not a string, then uncomment the below
			#if type(initialValue)==str:
			#	initialValue=[initialValue]
		#print("type: ",type(input_string))	
		return self.run(initialState,initialValue,input_string,0)
		
	def output_strings_file(self,input_string_file):
		"""Given a file with a list of input strings, this processes each input string and prints it out onto the output file"""
		f_input=codecs.open(input_string_file,'r','utf-8')#io.open(input_string_file,'r',encoding='utf-8')
		f_output=codecs.open('output_strings.txt','w','utf-8')#io.open('output_strings.txt','w',encoding='utf-8')
		input_lines=f_input.readlines()
		if input_lines[0][0]==u'\ufeff':
			input_lines[0]=input_lines[0][1:]#utf8 texts start with the byte encoding symbol, remove it
		for line in input_lines:
			line=line.strip()
			f_output.write (u''+line+"\t-->\t"+self.transduce(line)+"\r\n")
		f_input.close()
		f_output.close()
		
	def read_transition_list(self,transition_file):
		"""This takes as input a list of lines such that:
			1st line is of the form: initial states = [ 1,2,3]
			2nd line is of the form: final states = [ 1,2,3]
			all other lines have the template: input state, input symbol, output state, output string, direction
				e.g. : 2,a,3,aa,+1
			Note, both the input and output have the same alphabet
		"""
		#print('eh')
		self.input_alphabet=set([]) 
		self.output_alphabet=set([]) 
		self.alphabetList=set([]) 
		self.stateList=set([])
		self.initialValue=""
		self.transitions=[]
		
		currentLineIndex=0
		self.line_initialStates=self.lines[currentLineIndex]
#		print("so this is line of initial states:%s"%self.line_initialStates)
		self.initialStateList=getListofItems_nospace(self.line_initialStates)
#		print("so this is list of initial states:%s"%self.initialStateList)
#		print("so this is #1 of initial states:%s"%self.initialStateList[0])
		currentLineIndex=currentLineIndex+1
		#print('oy')
		self.line_finalStates=self.lines[currentLineIndex]
		self.finalStateList=getListofItems_nospace(self.line_finalStates)
		currentLineIndex=currentLineIndex+1

		
		self.lines_transitions=self.lines[currentLineIndex:]


		self.deltaState={}
		self.deltaOutput={}
		self.deltaDirection={}
		
		for trans in self.lines_transitions:
			try:
			#	print("pre-strip trans that im working on:%s"%trans)
				trans=trans.strip()
			#	print("post-strip trans that im working on:%s"%trans)
				trans=trans.split(',')
			#	print("post-split trans that im working on:%s"%trans)
				stateQ=trans[0]
				inputA=trans[1]
				stateP=trans[2]
				outputB=trans[3]
				direction=int(trans[4])
				
				
				if direction   not in [0,1,-1]:
					print ("error, the direction symbol",direction," isnt an okay direction  for the transition:",trans)
					sys.exit()
					
				self.transitions.append(trans)
				self.stateList.add(stateQ)
				self.input_alphabet.add(inputA)
				self.stateList.add(stateP)
				self.output_alphabet.add(outputB)
				
				i=inputA
				o=outputB
				qa=(stateQ,i)
				#print ('input state + input symbol pair is: ',qa)
				p=stateP
				b=o
				dir=direction
				if qa in self.deltaState:
					print ("error, nondeterminism for the transition:",trans)
					break
				else:
					self.deltaState[qa]=p
					self.deltaOutput[qa]=b
					self.deltaDirection[qa]=dir
			except :
				print ("an error happened while intrepreting the transition:",trans)
				sys.exit()
		
		self.alphabetList.update(self.input_alphabet)
		self.alphabetList.update(self.output_alphabet)
		self.alphabetList=list(self.alphabetList)
		self.input_alphabet=list(self.input_alphabet)
		self.output_alphabet=list(self.output_alphabet)
		self.stateList=list(self.stateList)
	
#def __main__(self,FST_recipe_file,input_strings):
def main():
    #for arg in sys.argv[1:]:
	#print ("arguments are:")
	#print (sys.argv[1])
	#print (sys.argv[2])
	reader=Reader( sys.argv[1],sys.argv[2],sys.argv[3])	

if __name__ == "__main__":
    main()		
