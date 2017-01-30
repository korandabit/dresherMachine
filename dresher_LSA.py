import itertools,numpy,csv,random

#####################
## Dresher Machine ##
##    Functions    ##
#####################

## NOTE: THIS SCRIPT CONTAINS CORE FUNCTIONS TO DRESHER MACHINE. EDIT WITH CAUTION.

##Updates
"""
2016.10.01 - working on ~328-350: phoneme tree builder stuff. See here if Raimy wants to omit 'none' entries from phoneme feature spell-out.

change so that read-in inventories are in a separate folder. how to do this? look at that image conversion script with 'old' and 'new' folders.
"""
##############
## Overview ##
##############

"""Description of contents.
	With the exception of the subset lists you see immediately below, this 
	script exclusively contains python functions which are called by 
	'dresher_run.py'. Functions are listed generally in the order they are 
	called in 'dresher_run.py'. 
	
	Initiation functions
		-Inventory
		-Subsets

	Features and orders
		-unique features
		-permutations
		-efficient permutations
		
	Output/analysis
		-Dresher hierarchy builder
		-Initial branch constraint
		-Final branch constraint
	
	A note about commenting style: The comments in this script assume 
	working knowledge of functions, their arguments, and outputs. 
	
	Comments about specific line functions typically follow the line, 
	while definitions and broader descriptions precede functions and 
	sections of code.
	"""

##########################
## Initiation functions ##
##########################

###############
## Inventory ##
###############
"""See dresher_run.py for descriptive of inventory function. Below are 
	comments for modifiable parameters."""
	
def inventoryImport(fileName='inventory.csv'): # change 'inventory.csv' to change default filename. 

	# inventory={'p':[],'b':['GT'],'ph':['GW'],'bh':['GT','GW'],'pg1':['GW'],'pg2':['LH'],'bi1':['LH'],'bi2':['LH','GT']} 

	try:
		data_file=open(fileName,'rU')
		reader=csv.DictReader(data_file)
		inventory={}
		for row in reader:
			if row['phoneme'] in inventory:
				inventory[row['phoneme']].append(row['feature'])
			else:
				inventory[row['phoneme']] = [row['feature']]
		data_file.close()
		# print 'using imported inventory:'
	except:
		raise Exception('Inventory Import failed!')
	return inventory

#############
## Subsets ##
#############

"""The following example list will not be used unless labeled as 'subset' and 
	dresher_run.py has no 'subset' list. Strings must be identical to a 
	label in the inventory. See 'dresher_run.py' for more details about 
	subsets."""

subsetC=[
	('English',['p','ph']),
	('Spanish',['p','b']),
	('Thai',['p','b','ph']),
	('Sindhi',['p','b','ph','bh','bi1']),
	('Beja',['p','b','ph','bh','pg2','bi2'])
]

def subsetMachine(inventory,subsets=4,phonemes=2): # Change the value for the second and third arguments to change the default number of subsets and number of randomly selected phonemes per subset generated, respectively.
	"""Function for generating randomized subsets. See dreher_run.py for 
		description."""
	subset=[]
	labelCount=1
	for i in range(subsets):
		curSubset=[]
		for i in range(phonemes):
			curRand=random.choice(inventory.keys())
			while curRand in curSubset: 
				"""If a phoneme is selected a second time, this while loop 
					reselects until a unique one is selected. This while 
					loop is the reason why this generator is not optimal 
					for near-saturation selection. It could likely be 
					writtten with another itertools/random function."""
			
				curRand=random.choice(inventory.keys())
			curSubset.append(curRand)
		label='set.no'+str(labelCount) # change the initial string to change the global label for subsets.
		subset.append((label,curSubset))
		labelCount+=1
	print subset
	return subset

#########################
## Features and orders ##
#########################
	
"""The functions in this section perform the analyses on subsets by 
	comparing the features across phonemes, and generating hierarchies for 
	them."""

def uniqueFeatures(inventory,curSubset):
	"""This function extracts all unique features of the inventory subset 
		you're analyzing. Define this subset in the list 'subset' on line 
		8, using identical phoneme labels from the dictionary full set on 
		line 4"""
	uniqueFeatures={}
	for curPhone in curSubset:
		for each in inventory[curPhone]:
			uniqueFeatures[each]=True
	
	return uniqueFeatures.keys()
	
################################
####Permutations generators ####
################################
##FULL PERMS  ###
#################


def permGenerator(uniqueFeatures, length, order=True): # third argument: 'y' gives all possible orders, 'n' gives only unique combinations.
	"""Function for generating all permutations (with or without unique 
		orders) given unique features in the subset. Note that Setting 
		order to yes for massive subsets of phoneme/features can be 
		computationally costly. Some analyses do not require unique 
		orders."""
	if order: # order matters
		# permutations=list(itertools.permutations(uniqueFeatures,len(uniqueFeatures)))
		permutations=[]
		for each in itertools.permutations(uniqueFeatures,length):
			permutations.append(each)
		
	else:
		permutations=list(itertools.combinations(uniqueFeatures,length))
		
	return permutations	


###################
## EfficientTree ##
###################

"""The following set of 5 functions comprise the efficient permutation 
	generator. For feature geometries that are non-redundant, that is, 
	ones where it is not possible to exclude any of the unique features in 
	a heirarchy (like a heirarchy of laryngeal features) the function will 
	return an empty set. Where possible, the function will return a list 
	of efficient sets of features, indexed in order of the unique feature 
	list."""

# Much thanks to Chris Cox for help with this section.
# Credit for unique_rows, dropConstants, findDiscriminatingPhonemes goes to him.


def arrayBuilder(inventory,curSubset,uniqueFeatures,binary='n'):
	"""takes current subset of contrasts, unique features, and optionally 
		reports binary array of feature/phoneme array. columns are ordered 
		unique features, rows are ordered phoneme subset"""
	phoneArray=[]
	for curPhoneme in curSubset:
		phoneRow=[]
		for feature in uniqueFeatures:
			if feature in inventory[curPhoneme]:
				phoneRow.append(1)
			else:
				phoneRow.append(0)
		phoneArray.append(phoneRow)
	output=numpy.asarray(phoneArray)
	# if not binary=='n':
		# print "\nHere is a binary representation of each phoneme and feature, unlabeled for your convenience. \n", str(output)
	return output

	
"""The function below sets up tested unique arrays as part of 
	findDiscriminatingPhonemes()."""
def unique_rows(array):
    nrow = array.shape[0]
    ncol = array.shape[1]
    list_of_tuples = [tuple(row) for row in array]
    uniq = list(set(list_of_tuples))
    uniq_array = numpy.atleast_2d(numpy.array(uniq))
    return uniq_array

"""The function below identifies any features which are fully redundant 
	(appear in every phoneme), and removes them."""
def dropConstants(phonemeMatrix):
    P = numpy.array(phonemeMatrix)
    droplist = []
    for i, (isone, iszero) in enumerate(zip(P.T==1,P.T==0)):
        if all(isone) or all(iszero):
            droplist.append(i)
    return numpy.delete(P, droplist, 1)

	
"""The below function iteratively tests and removes features. It tries 
	removing one feature at a time. If after removing the feature, all 
	phonemes remain discriminable, the feature stays removed. If not, it 
	is replaced and the next feature is tested. This iteration is repeated 
	until a full cycle through remaining features reveals no successful 
	removal. It returns the remaining set."""
def findDiscriminatingPhonemes(P,columnLabels=[]): 
	#Second parameter could be curUniqueFeatures, but more downstream needs to be fixed to make it work.
    nrow = P.shape[0]
    ncol = P.shape[1]
    if not columnLabels:
        columnLabels = range(ncol)
    discriminatingPhonemes = []

    for i in xrange(ncol):
        columnLabels_subset = tuple(columnLabels[j] for j in range(i) + range(i+1, ncol))
        Pt = numpy.delete(P, i, 1)
        Pu = unique_rows(Pt);
        if Pu.shape[0] == nrow:
            tmp = findDiscriminatingPhonemes(Pt, columnLabels_subset)
            if tmp:
                columnLabels_subset = tmp
                discriminatingPhonemes.extend(columnLabels_subset)
            else:
                discriminatingPhonemes.append(columnLabels_subset)

    return set(discriminatingPhonemes)

def efficientWrapper(curUniqueFeatures,eTrees):
	"""This function converts the output numpy array and efficient 
		features back into a list object for use in dresherGenerate(), as 
		well as reports whether the efficientTree was successful."""
	counter=1
	listOfTrees=[]
	for eachTree in eTrees:
		#print "Tree"+str(counter)
		listOfFeats=[]
		for eachFeature in eachTree:
			listOfFeats.append(curUniqueFeatures[eachFeature])
		listOfTrees.append(listOfFeats)
		counter+=1
		# print "Minimal feature set: "
		# print listOfTrees
		return listOfTrees
	if len(eTrees)==0:
		# print "No redundant features." 
		# print curUniqueFeatures
		return [curUniqueFeatures]


		
######################
## Dresher builder  ##
######################
	
def dresherGenerate(inventory,permutations,curSubset,curLabel):			
	"""This function takes permutations and implements a tree structure in 
		two formats. 
	
		First format: Dictionary containing each permuation. Each 
		permutation takes a list of tuples. For each phoneme in the 
		subset, a binary string is generated representing the order, and 
		branch for each feature in the current permutation; if the feature 
		is present in the phoneme, a 1 is represented for that branch, and 
		if the feature is missing a 0. The binary string is the coordinate 
		for a terminal node corresponding to that phoneme. The tuple 
		generated is the binary string-phoneme correspondence.
	
		After the dictionary is populated with tuples of the subset of 
		phonemes, an iterator identifies and generates 'unused' branches. 
		It reports these as 'missing', which can serve as an index for how 
		efficient your tree is. A primary purpose for this function 
		however, was to optimize the following graphic format, which 
		required all branches be filled with a phoneme or an "empty" 
		phoneme.
	
		Second format: Generates a string representation of the above 
		information for graphical output. See stringMaker() below."""			
	
	dreshers={}
	treeNumber=0
	listStrings=[]
	for curPermutation in permutations: #e.g. [contrastA,contrastB,contrastC]
		curPermName=''
		curTreeLabels={}
		
		"""local dictionary for permutations with tuple of phones and 
			binary values for place in particular dresher heirarchy."""
		dreshers[curPermName]=[]
		completeList=[] #see below.
		for curPhone in curSubset: #e.g. for 'p' in this language...
			curTreeLabels[curPhone]=[] #builds a dictionary entry for the phoneme. Value will be a list of feeatures in order of current contrast.
			phoneBinary=''
			for curContrast in curPermutation: #e.g. for 1st contrast (contrastA) out of possible sets of contrasts.
				if curContrast in inventory[curPhone]: #e.g. if this contrast is one of 'p's contrasts...
					phoneBinary+='1'
					curTreeLabels[curPhone].append(curContrast)
				else:
					phoneBinary+='0'
					curTreeLabels[curPhone].append('fns') #fns for feature not specified
			dreshers[curPermName].append((curPhone,phoneBinary))
			completeList.append(phoneBinary)

		
		"""The following generates binary strings for tree nodes with no 
			phoneme, to complete a tree generator. It does so by first generating
			all possible binary combinations, then checking for existing ones. It also reports to the 
			terminal nodes created."""
		binaryComplete=["".join(seq) for seq in itertools.product("01", repeat=len(curPermutation))]
		emptyCount=0
		for curBinary in binaryComplete:
			if curBinary not in completeList:
				dreshers[curPermName].append((' ',curBinary))
				emptyCount+=1
				# print "Missing:"+str(curBinary) #Activate in order to see which nodes are empty.
		dreshers[curPermName].sort(key=lambda tup: tup[1]) # now the tuples are sorted in order
		# print curPermutation, emptyCount

		curDict={}
		for curPhone in dreshers[curPermName]:
			
			# Creates labels for terminal branch nodes; prints branch label and phoneme.
			curBranch=''
			for i in range(len(curPhone[1])): #refers to the (phoneme, binary) tuple. 
				if not i == 0:
					curBranch+='.'
				if curPhone[1][i]=='0':
					curBranch+='0'
				else:
					curBranch+=str(curPermutation[i])
			
			# The following writes to a dictionary the same thing.
			if curBranch not in curDict.keys():
				curDict[curBranch]=[curPhone[0]]
			else:
				curDict[curBranch].append(curPhone[0])

		#The following print codes are normally activated. Deactivated here to reduce printing.		
		# print '\nHierarchy: '+str(curPermutation)
		# print 'Terminal branch: [phonemes]'
		# print curDict

		treeNumber+=1
		
		def stringMaker():
			"""This is a function embedded within dresherGenerate, which 
				generates the to-.txt file of strings for graphic dresher 
				trees. The formatting of the string is optimized for 
				http://mshang.ca/syntree/. 
		
				stringMaker could be made into an independent function 
				allowing greater flexibility. This would require 
				dresherGenerate outputting all necessary components 
				(likely an object), and stringMaker taking in these as 
				fixed arguments."""
		
			labeler=str(curLabel)+"_tree"+str(treeNumber)+" "
			outString='[x]'
			for curContrast in curPermutation: 
				"""The logic of this function here is as follows: For 
					every contrastive feature in the current permutation, 
					a nested branch is created at an 'X' with two 
					subsequent 'X's. This is the best I could come up with 
					to allow flexible embedding. In fact however, such 
					formatting rigidly creates a full tree, including 
					unused branches."""
			
				outString=outString.replace('x','[0 x][''{} x]'.format(str(curContrast))) 
			outPhone=curDict.keys()
			outPhone.sort()
			# print outPhone
			for curBranch in outPhone:
				outString=outString.replace('x','/{}/'.format(str(curDict[curBranch][0])),1) 
				"""The above line inserts a label for the tree. To modify 
					the label, replace the content of the final str() 
					function (careful with the embedded parentheses, and 
					be sure to leave the ',1)' at the end)."""
				
			outString=outString[0]+labeler+outString[1:]

			# print 'tree generator string: '+outString
			return outString
		curString=stringMaker()
		listStrings.append(curString)

	return listStrings


###############
## Analysers ##
###############

"""Pair of filters used to reduce full set of permutations to ones of 
	interest. See dresher_run.py for further description. Structure of 
	both definitions are similar."""

def dresherFinal(permutations,spec):
	newPermutations=[]
	if spec in permutations[0]:
		for curPermutation in permutations:
			print curPermutation
			if curPermutation[-1]==spec: 
				"""The number in brackets indexes which item in the 
					permutation must be matched. This can be replaced with 
					any real index value. For example, [1] would define 
					the second position feature required. The same is true 
					for dresherInitial."""
			
				newPermutations.append(curPermutation)
		return newPermutations
	else: # If permutation doesn't contain specified feature, 'fail' is printed to terminal.
		print "dresherFinal failed"
		return permutations

		
def dresherInitial(permutations,spec):
	newPermutations=[]
	if spec in permutations[0]:
		for curPermutation in permutations:
			# print curPermutation
			if curPermutation[0]==spec:
				newPermutations.append(curPermutation)
		return newPermutations
	else:
		print "dresherInitial failed"
		return permutations
		
#for KDM LSA
#in order to search a problem space with massive combinatorics, here's a subset generator which randomly samples based on adjustable criteria.

def randomSampler(lst,sampleSize):
	random.shuffle(lst)
	if not 0<sampleSize<101:
		print "\n\nError: set sample size between 0 and 100.\n\n"
		return
	curSample=len(lst)*sampleSize//100
	# print curSample
	subset=lst[0:curSample]
	# subset=lst[0:sampleSize]
	# print len(subset)
	return subset

	
def writeBlock(rows, filename, header=[], ext='.txt', method='a', delim='\t',initBuffer=0,endBuffer=0):
	f = open(filename+ext, method)
	lineCount=0
	
	def buffer(size):
		for i in range(size):
			f.write('\n')
		
	if len(header)>0:
		for col in header:
			f.write(str(col))
			f.write(delim)
		f.write('\n')
		
	for row in rows:
	
		buffer(initBuffer)
		
		for col in row:
			f.write(str(col))
			f.write(delim)
		f.write('\n')
		
		buffer(endBuffer)
		
	f.close()
	
	
################
## Extra Code ##
################
"""This is not a working function. Code may be used to build one. The 
	function was intended to test merger, sisterhood, or other diachronic 
	change in hierarchies, by allowing deletion of a feature, and 
	reporting resulting hierarchies."""

def dresherDelete(permutation,curSubset,delete):
	tempDict=inventory
	print tempDict
	for each in tempDict.keys():
		try:
			tempDict[each].remove(delete)
		except:
			pass
	permutation=list(permutation)
	try:
		permutation.remove(delete)
		print "merge1 ",str(permutation)
	except:
		pass
	output=dresherGenerate(permutation,curSubset,curLabel)
	return output
