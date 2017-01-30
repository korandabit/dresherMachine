from __future__ import print_function
import csv,ast,re, os, itertools
import dresher_LSA as d

"""
This script takes inventories from 1_input folder, and hierarchies from 2_KDM_pre-2.txt, which currently are set at minimum unique sets (go to 2_KDM_inventoryAnalysis to modify this), and counts the efficiency of each tree (default order only - could be changed in 2_KDM....).

to do this, hierarchy features are iteratively matched against features in current inventory(ies). When a vowel contains a unique feature (or uniquely doesn't), it's removed from the match function. when a vowel contains a feature it's counted in the (in)efficiency counter.
	INCOMPLETE

UPDATES
2016.12.29
	solved known issue where not all unique features were being removed. the issue was that the length test (( len(set(lst-1)))<len(set(lst))) )) needed to be indented.
2016.12.26
	current build successfully runs the script. errors include the following: seems to arbitrar
2016.12.21
	Trying to build a .csv import to compare inventories with analyses, in order to assess outputs.
	
This script when complete will need a folder of input csvs that match the list of csvs in the output.
	"""

def efficiency_analysis(input_list,list_of_files,inventory_range,vowel_inventory_size=3):

	################
	# Runtime Vars #
	################
		
	readInFile='inputVars'


	#############
	# Functions #
	#############

	def removekey(d, key):
		r = dict(d)
		del r[key]
		return r

	def listDifference(full,subset):

		for feature in subset:
			full.remove(feature)
		return full

	###############
	##Read in hierarchies
		
	hierDict={}
	for each in input_list:
		hierDict[each[0]]=each[4]
					
	#main runtime
	def inventoryRange(mover_listofFiles,inventory_range):
		if inventory_range==0:
			listofFiles=mover_listofFiles
		elif inventory_range==1:
			listofFiles=mover_listofFiles[:1]
		else:
			listofFiles=mover_listofFiles[0:2]
		return listofFiles
	"""looks in folder and iterates through (a dictionary made from) csvs of inventories. """
	errorCount=[]
	wRows=[]
	iterCounter=0
	permLen=0
	list_of_files=inventoryRange(list_of_files,inventory_range)
	
	"""Write a function that will create the denominator for the print to screen, here."""


	
	for curInventory in list_of_files:
		"""Match Names"""
		inventoryName=str(curInventory)[21:-4] #this is the name trimmer from 2_analysis. not sure if its necessary.

		inventory=d.inventoryImport(curInventory) #does the work to turn csv file into a dictionary phone:features

		if inventoryName not in hierDict.keys():
			print (inventoryName)
			print (hierDict.keys())
		



		for curHierarchy in hierDict[inventoryName]: 
			#looks at each hierarchy in list of hierarchies for given inventory, looked up by matching inventory name

			permutations=[]
			for each in itertools.permutations(curHierarchy,(len(curHierarchy))):
				permutations.append(each)
				
			permLen+=len(permutations)				
			for curIterHier in permutations:
				iterCounter+=1
				if iterCounter%250==0:
					print( str(iterCounter)+'/ '+str(permLen), end='\r')
				finishList=[]
				efficiency=0
				treeSpeller={} #makes a dictionary where features are defined by the hierarchy. redundant with dresher generate.
				features={}
				for curPhone in inventory.keys():
					treeSpeller[curPhone]="" #If instead this is using lists, then you  might be able to do fancy things like match features across inventories, etc.

				for curFeature in curIterHier: #e.g. low in low>rounded
					featureCt=0

					for curPhone in sorted(inventory.keys()): #e.g. a in a,i,o
						if curFeature in inventory[curPhone] and not curPhone in finishList: #e.g. if low in a
							treeSpeller[curPhone]+="1" #append low to a
							efficiency+=1
							featureCt+=1

						elif not curFeature in inventory[curPhone] and not curPhone in finishList:
							treeSpeller[curPhone]+="0"
						else:
							pass
					features[curFeature]=featureCt		
					
					"""after each completed round of spellout, test for unique features."""
					for curPhone in treeSpeller.keys():
						rmCurPhoneTest=removekey(treeSpeller,curPhone)
						if len(set(rmCurPhoneTest.values()))<len(set(treeSpeller.values())):
							finishList.append(curPhone)
							
				"""The following is a global check to make sure that the finished product has successfully uniquely discriminated all phonemes."""
				if not len(set(treeSpeller.values()))==len(treeSpeller.values()):
					errorTuple=(curInventory,curIterHier)
					errorCount.append(errorTuple)
				
				"""The following generates the unused features."""
				curUniqueFeatures=d.uniqueFeatures(inventory,inventory.keys())
				remainders=listDifference(curUniqueFeatures,curIterHier)
				curUniqueFeatures=d.uniqueFeatures(inventory,inventory.keys())

				#Summary block
				hierarchy_rn=[]
				for string in curIterHier:
					hierarchy_rn.append(string[0:4])

				#consolidate data points into output list of lists	
				wContent=[vowel_inventory_size,curInventory[21:27],hierarchy_rn,efficiency,features,treeSpeller,curUniqueFeatures,remainders]
				wRows.append(wContent)
				
	if len(errorCount)>0:
		print ("Error, incomplete tree.")
		print( len(errorCount))		


	return wRows
		
		
		
		
