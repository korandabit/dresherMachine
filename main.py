#mainscript
from __future__ import print_function
from collections import Counter
import csv,ast,re, itertools, glob,sys,os,datetime


import dresher_LSA as d
import main_1inventoryMover as m
import main_2inventoryParser2 as k
import main_3min_analysis as a1
import main_4efficiency_analysis as a2
"""
2017.01.04
	created /r for print to screen. stitched some functions, added upper limit to perm sizes for inventories larger than their feature sets (e.g. 28>12).
	possible soln to implement/test:
		run efficientTree on order=false, then make order=true for only subsets where efficient trees are produced. depends on some assumption about set1 outputs.
		
2016.12.31
This script streamlines all functions of KDM_ to date. Running this script requires 0_inputFiles to be populated with csv files, and that's it. It works in place by 1) choosing a subset of csv's to look at, passing that info and all extractions onto subsequent scripts, and only outputting a file at the end.

TODO:
	add a sys.argv at the end of a script, so things like errors can be explored before quitting.
	
	inventory_size 6 currently produces "Error Incomplete Trees."

TEST SOLN below (it's been coded, I think)
known issue: analysis 2 currently depends on a full inventory set being run.
solution: feed analysis 2 the same input (and perhaps function from within) runTimeVars regarding subsetting.


dependent files can be rid of cloogy read/write file content. Archive/annotate/retire them.
bring over a number of runtime vars to this file from dependent files.
"""



################
# Runtime Vars #
################

analysis=True #toggle in order to turn off analyses
writer=False #toggle in order to write to file.

try:
	vowel_inventory_size=int(sys.argv[1])
except:
	vowel_inventory_size=7
#could be written to optionally take range. currently doesn't. 
inventory_range=0 #inventory range setting (0=full, 1=first, 2=first 2). This gets passed to Parser and Analysis 2.
use_random_generator=False #toggle to turn of sampling of only a subset of features.

today=datetime.date.today()
wFilename='{} v{}'.format(today,str(vowel_inventory_size))


#########
# Mover #
#########

mover_listofFiles = m.mover(vowel_inventory_size) #vowel inventory size
#Currently written to return listofFiles. a dictionary exists which can return quantity, redundancy

##########
# Parser #
##########

kdm_parsed = k.runTimeVars(mover_listofFiles, #list of files from mover;
							vowel_inventory_size, # vowel inventory size; 
							inventory_range=inventory_range, #inventory range setting (0=full, 1=first, 2=first 2)
							randomGenerator = use_random_generator, #random % of permutations = True
							writeFile=False) # write to file = false
#takes in list of files from mover.
#outputs 1_KDM_parsed.txt
#print(kdm_parsed)
#for i in range(len(kdm_parsed[0])):
#	if i==3:
#		for j in range(len(kdm_parsed[0][i])):
#			print(kdm_parsed[0][i][j])
#			if j in range(3):
#				inv = d.inventoryImport(mover_listofFiles[0])
#				pArray = d.arrayBuilder(inv, inv.keys(), kdm_parsed[0][i][j], binary='n')
#				print(pArray)
#				discp = d.findDiscriminatingPhonemes(pArray, columnLabels=[])
#				print(discp)
#				print(d.efficientWrapper(kdm_parsed[0][i][j], discp))
#	else:
#		print(kdm_parsed[0][i])
#################
# Analysis 1 & 2#
#################
if analysis:
	analysis_out = a1.min_analysis(kdm_parsed) #pass in list of lists object with similar elements to .txt file.

	# output is a list of these: [name,length,minVal,maxVal,bestSets.keys()]
	# analysis_out[0][4] #bestSet.keys(); set of efficient hierarchies for 1st language

	output=a2.efficiency_analysis(analysis_out, mover_listofFiles,inventory_range, vowel_inventory_size)
	# output rows: [vowel_inventory_size,curInventory[21:27],hierarchy_rn,efficiency,features,treeSpeller,curUniqueFeatures,remainders]

	# print(output[0][0])
	wHeader=['#','Invty','Hierarchy_Order','Total','Feats','Vowels','Total_features','Remaining_Features']

	wRows=output
if writer:
	d.writeBlock(wRows, wFilename, ext='.txt', method='a', delim='\t') #For headers, insert 'wHeader' after wFilename 


