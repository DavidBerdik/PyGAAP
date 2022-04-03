import cangjie
import numpy as np

"""
reverse character look up. aka look up the Cangjie code from a character.
This will take 3-10 minutes.
Using Debian's pycangjie library:
https://salsa.debian.org/input-method-team/pycangjie
"""

# and I OOP (Object-oriented programming)
cj = cangjie.Cangjie(cangjie.versions.CANGJIE5, cangjie.filters.CHINESE)

lookup_list=list(range(97, 123))
# the look up list is the list of ascii codes to convert to letters so the letter string can be used to look up a character.
# this is responsible for a single letter.

combine_list=[0]
# these are indicies of lookup_list. The combine list creates the look up string by converting individual numbers from
# lookup list to letters. The resulting look up string is used to find the characters.


##
# ooooh boy this is gonna be fun
# chinese characters unicode range: 19968 -> 195103. Cangjie may not cover the entire range, but better be sure.
# using numpy to save space
lookup_table=np.empty_like(['abcde'], dtype="<U5", shape=(175135,))
lookup_freqs=np.empty_like(['abcde'], dtype=int, shape=(175135,))
##

character_count=0
iterations=0

while len(combine_list)<=5: #limit the length of look-up code to 5.

	if iterations/50000==iterations//50000:
		print(iterations)

	# first construct look-up string. e.g. "bgr" -> 周.
	code=""
	for c in range(len(combine_list)):
		code+=chr(lookup_list[combine_list[c]])



	# look up the character
	try:
		characters=cj.get_characters(code)
		for c in characters:
			character_count+=1
			#print(c.chchar, c.code, c.frequency)
			lookup_table[ord(c.chchar)-19968]=code
			lookup_freqs[ord(c.chchar)-19968]=c.frequency
	except:
		pass


	# then increment the ascii code of the look up string. This functions as a base 26 number system.
	i=len(combine_list)-1
	combine_list[i]+=1
	while combine_list[i]>=len(lookup_list) and i>=0:
		combine_list[i]=0
		i-=1
		combine_list[i]+=1
	if i==-1:
		combine_list=[0]+combine_list
	
	iterations+=1
	


f=open("character_table.txt", "w+")
for char in range(len(lookup_table)):
	if lookup_table[char]!="":
		f.write(lookup_table[char]+","+str(char+19968)+",\n")

f.close()