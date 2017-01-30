import shutil,os,csv

"""This script moves files from inventory generator's output folder, to inventory parser's input folder. Set unique files to False if you'd like it to move all files.
UniqueFiles finds all the unique csv files, and counts redundant files.

Current build: successfully identifies unique phoneme combos, counts and prints unique/redundant combos.

Tasks
2016.12.31 work in write block, send to output for main.py

Test/verify that it moves the correct files.
Problem files: some strings include feature info. Are these redundant? Do we manually handle them here or in inventoryGenerator or in the input files?
	see test search on line 58.
Test 1_KDM on problem files: do the problems go away?
identify inventory lengths. test lines 44-56.

2: store names of unique systems (list and count redundant languages for systems)
	for curKey in dict.key():
		if curKey==x:
			dict[curkey].append(value)
	
	#retrieve unique names function;return lengths new object
	newlist=[]
	for each in dict.key():
		newlist.append(dict[each][0])

 (16)"""
def mover(inventorySize=7):
	uniqueFiles=True
	srcFolder='0_output_inventories/'
	dirFolder='1_input_inventories/'

	def uniqueSort(srcFolder,dirFolder):

		"""Build a dictionary of phoneme combos and the first csv associated with it."""
		completeDict={}
		wRow=[]
		for curFile in os.listdir(srcFolder):
		
			"""Adds filename as dictionary key."""
			a=open(srcFolder+curFile,'rU')
			reader=csv.DictReader(a)
			phoneString=''
			stringLength=0 #newline untested
			for row in reader:
				"""Adds only unique phonemes to a string."""
				if not str(row['phoneme']+'_') in phoneString:
					phoneString+=str(row['phoneme']+'_')
					stringLength+=1 #newline untested: it's supposed to count the length of phonemes.

			"""Adds only unique phonemeStrings to dictionary."""
			if phoneString in completeDict.keys():
				completeDict[phoneString][0].append(curFile)
			else:
				completeDict[phoneString]=[[curFile],stringLength] #untested 'stringLength'
			a.close()
	
		nameLst=[]
		for each in completeDict.keys():
			if completeDict[each][1]==inventorySize: #Modify this line to set criteria for inventories used.
				targetName=completeDict[each][0][0]
				# shutil.copyfile(srcFolder+targetName,dirFolder+targetName) #this is the line that physically moves files.
				nameLst.append(srcFolder+targetName)

		print sorted(nameLst)[0:2]
		tally2=0
		for each in completeDict.keys():
			if len(completeDict[each])>1:
				pass
			else:
				tally2+=1
		
		for eachVowels in sorted(completeDict.keys()):
			vowels=str(eachVowels)
			lengthT=str(completeDict[eachVowels][1])
			count=str(len(completeDict[eachVowels][0]))
			firstname=''
			for each in completeDict[eachVowels][0]:
				cleanName=each[1:]
				cleanName=cleanName.replace(".csv", "")

				firstname+=str(cleanName)+'\t'
			wRow.append([vowels,lengthT,count,firstname])

		return nameLst
					
	#########
	#Runtime#
	#########

	if not uniqueFiles:

		for curFile in os.listdir(srcFolder):
			"""Looks in the source directory for all files, writes all those files to destination directory."""
			shutil.copyfile(srcFolder+curFile,dirFolder+curFile)
	else:
		nameLst=uniqueSort(srcFolder,dirFolder)
		
	# return wRow
	# return completeDict
	return nameLst

