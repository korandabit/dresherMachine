from __future__ import print_function
import glob,sys,os
from collections import Counter

import dresher_LSA as d

"""This script is adapted from dresherClean_run in order to address fully 
iterated efficient trees.


next tasks: verify that novel outputs of total trees are viable trees. REMINDER, the FOR LOOP NEEDS TO BE A SUBSET OF 720 to not run forever.

Updates 01.05.2017
	Commandline cleanup. Further Re-factoring of data. 

Updates 12.30.2016
	Wrote runtime vars to make modifications easier, cleaned up print, write, and runtime functions and loops to remove unnecessary features.
	This version (vs. 1.8) uses a dictionary and dictionary keys to identify unique sets after analyzing, on the assumption that order functions are applied later in analysis.


Updates 09.30.2016
Built an optional argument for .csv
	command line: python KDM_LSA.py filename.csv
	default reads all CSV files in folder.
Wrote readme file.
Wrote a readIn.py file (fixed encoding file), which reads output.txt into a dictionary of objects; writes 'analyses.txt'
readIn.py: started working on deleting empty nodes in the trees.
	
	
TODO:
unicode character compliant
**if in tree [], delete.: see readIn.py for update.
**spell out vowel and the features used..

*update readme to include post-kdm_lsa.py analysis, and pre- inventory generator.
*write "look in directory x for inventories, write in directory y for analyses" functions to keep folders clean.

"""




################
# Runtime Vars #
################
def runTimeVars(mover_listofFiles,vowel_inventory_size,inventory_range=1,randomGenerator = True,writeFile=True):
	#Inventory settings
	dirFolder='1_input_inventories/'

	#GUI settings
	text_analysisInit="\n\n-------------------------\nDRESHER PARSING INITIATED\n-------------------------\n"
	header='*Vowel inventory size, inventory number, language used, unique efficient permutations found, current iteration count, total iterations to parse.\n\nV-Ct\tname\tperms\tcurIt\ttotal'
	GUI_update_freq = 500 #Set higher for quicker analyses, fewer updates

	#Permutations settings
	permOrder = True #If order matters, change here. If not, set to false (e.g. only unique sets). Needs to be set to true if looking for all unique efficient trees.
	permLength_buffer = 2 #This number is subtracted from inventory size to give feature permutation size.

	# randomGenerator = True #Turn on random sampling to reduce number of permutations? Set to True, and 
	randomGenSize = 25 # set integer between 1-100 (percent) of permutations to be sampled.

	treeGenerator_on = False #build strings usable for a visual syntax maker.

	#write file settings
	endBuffer=2 #adds 3 lines after each block to make 
	wFilename='1_KDM_parsed'
	writeMethod='w'
	
	#############
	# Functions #
	#############
	def inventoryRange(mover_listofFiles,inventory_range):
		if inventory_range==0:
			listofFiles=mover_listofFiles
		elif inventory_range==1:
			listofFiles=mover_listofFiles[:1]
		else:
			listofFiles=mover_listofFiles[0:2]
		return listofFiles
	
	def runtime(inventory):

		curUniqueFeatures=d.uniqueFeatures(inventory,inventory.keys())
		local_vowel_length=len(inventory.keys())
		def permLength(vowel_inventory_size,curUniqueFeatures):
			"""Sets a smaller size of feature sets searched, as a function of vowel inventory size to avoid combo explosion. It's a hack which eventually could be replaced."""
			if vowel_inventory_size>5:
				permLength=vowel_inventory_size-permLength_buffer
			else:
				permLength=5
			"""below sets an upper bound to all possible features (in cases where vowel count>feature count."""
			curLength=len(curUniqueFeatures)
			if permLength>curLength:
				permLength=curLength-(permLength_buffer*2)
			return permLength
			
		"""List of all iterations of current unique features."""
		
		permLength=permLength(vowel_inventory_size,curUniqueFeatures)
		fullPerms=d.permGenerator(curUniqueFeatures, permLength, permOrder) #See Runtime Vars to configure.
		
		if randomGenerator: #See Runtime Vars to configure random sampling.
			fullPerms=d.randomSampler(fullPerms,randomGenSize)
			# print( "Random Gen on: "+str(len(fullPerms))+" inventories.")
		
		
		"""Efficient algorithm"""	
		totalTrees={}
		counterTotal=0
		for curPerm in fullPerms:
		
			phoneFeatArray=d.arrayBuilder(inventory,inventory.keys(),curPerm,binary='n')
			eTrees=d.findDiscriminatingPhonemes(phoneFeatArray,columnLabels=[]) 
			# print eTrees
			eTrees=d.efficientWrapper(curPerm,eTrees)
			
			totalTrees[tuple(sorted(eTrees[0]))] = True
			counterTotal+=1
			totalTrees_len=len(totalTrees.keys())
			
			"""Prints updates to screen"""

			
			if counterTotal % GUI_update_freq == 0: 
				gui_update= str(local_vowel_length)+'-'+str(invNum)+"\t"+str(curInventory[22:28])+'\t'+ str(totalTrees_len)+"\t"+str(counterTotal)+"\t"+str(len(fullPerms))
				print(gui_update, end='\r')
				
		gui_update= str(local_vowel_length)+'-'+str(invNum)+"\t"+str(curInventory[22:28])+'\t'+ str(totalTrees_len)+"\t"+str(counterTotal)+"\t"+str(len(fullPerms))
		print (gui_update)

		"""Error check."""
		#If 'Saturated list' appears in output file, change length threshold on unique perms.
		if counterTotal==totalTrees_len:
			totalTrees={"saturated list":True}
		
		"""write to file"""
		wRows.append([curInventory,inventory.keys(),curUniqueFeatures,totalTrees.keys()])
		
		"""Tree Generator"""

		if treeGenerator_on:
			fullPermOutput=d.dresherGenerate(inventory,totalTrees.keys(),inventory.keys(),curInventory) #this is what makes the trees.
			writeRow.append(fullPermOutput)
			
		return totalTrees.keys()

	
	#############
	## Runtime ##
	#############

	
	listofFiles=[]
	collection={}
	invNum=1
	wRows=[] #wrapper object for write to file
		
	"""Main loop over CSV files"""
	listofFiles=inventoryRange(mover_listofFiles,inventory_range) #see fn. above: creates subset for testing.
	print (text_analysisInit)
	print (header)
	
	for curInventory in listofFiles:
		inventory=d.inventoryImport(curInventory) 

		collection[curInventory]=runtime(inventory)	
		invNum+=1
		
	"""Write to file"""
	if writeFile:
		if treeGenerator_on:
			endBuffer+=-1
		d.writeBlock(wRows, wFilename, ext='.txt', method=writeMethod, delim='\n',endBuffer=endBuffer)

	return wRows


