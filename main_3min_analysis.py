import csv,ast,re
import dresher_LSA as d


"""
This document reads in kdm_parsed as python elements (see moduloReader below). It writes two output files with minimal analyses. 

UPDATES
2016.12.30
	Started streamlining the document.

2016.09.30
	Started working on cleaun up trees
	Built output file (analyses.txt)
2016.12.21
	j write block at the end preps for 2_KDM_2

TODO:
	Analyses 1 and 2 need to be co-opted. They share redundant processes.
	writeBlock needs to be integrated.
	continue creating functions
	continue moving runtime vars to the top.

The txt file output from KDM_LSA.py currently(09.20.2016) gives 8 lines per inventory.
Each meaningful line is read into a dictionary called inventory.
dictionary key is the language analysed.
key value is a list of objects:
inventory[language][0]=vowel inventory
inventory[language][1]=feature inventory
inventory[language][2]=list of lists, all permutations
inventory[language][3]=list of strings, all trees.
"""
def min_analysis(input_list_oflists):
	#############
	# Functions #
	#############

	def mainVars_passer(input_list_oflists):
		"""Takes the list of lists passed from inventory parser, where each element is a language and its associated content. Converts this into dictionary key:values similar to moduloReader, above."""
		inventory={}
		for curInventory in input_list_oflists:
			inventory[curInventory[0]]=curInventory[3]
		return inventory			
			
	################
	# Runtime Vars #
	################

	main_script=True #uses main.py
	text_analysisInit="\n\n--------------------------\nDRESHER ANALYSIS INITIATED\n--------------------------\n"

	#############
	## Runtime ##
	#############
	
	inventory=mainVars_passer(input_list_oflists)
	
	#for main.py
	if main_script:
		wRows=[]
		print text_analysisInit
		print "file\tperms\tmin\tmax"
		for each in sorted(inventory.keys()):
			shortCount=0
			name=str(each)[21:-4] #trims off the filepath and .csv to give you the lang name.
			length=str(len(inventory[each]))

			minCount=min(map(len,inventory[each]))
			maxVal=str(max(map(len,inventory[each])))
			minVal=str(minCount)
			
			print name[1:7]+"\t"+length+"\t"+minVal+"\t"+maxVal+"\t"#+mode1+"\t"+mode2

			bestSets={}
			count=1
			for featureSet in inventory[each]:

				if len(featureSet)==minCount:
					bestSets[tuple(sorted(featureSet))]=1

			for featureSet in bestSets.keys():
				curString=str(featureSet)

			wRows.append([name,length,minVal,maxVal,bestSets.keys()])
	
	return wRows