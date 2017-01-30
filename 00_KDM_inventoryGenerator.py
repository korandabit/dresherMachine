import csv

"""
This script takes in three files: 'languagetocode.txt','codetophoneme.txt', and phonetofeature2.csv', converts them into dictionaries, and then compiles them for output csvs. each language is a unique csv with phonemes and features.

Write to file section has a subset criteria. it searches the feature list of phones to determine if 'sonorant' or other criteria is met. this can be adapted to be more flexible: 'has a' or 'b' or other. any() and all() functions?.

UPDATES
2016.12.17 - write to file was not ordering phonemes. applied 'sorted' to correct this. it's needed because 0_KDM_Mover will consider order as mattering. 
"""

#set filter criteria to return only phonemes that meet this.
featureCriteria='vowel' 
criteriaDelete=True #toggle to 'False' if you don't want this criteria deleted from analyses.

inputDir='0_input_files/'
def languageDict():
	"""key:value combination of language name and language code from a text file->stored dictionary."""
	languageCode={}
	with open(inputDir+'languagetocode.txt') as csvfile:
		languageToCode=csv.DictReader(csvfile, fieldnames=['language','code'], restkey=None, restval=None, dialect='excel')
		for row in languageToCode:
			languageCode[row['code']]=row['language'] #you'll swap code and language if it is easier.
		# print languageCode.values()
	return languageCode

def phonemeDict():
	"""key:value combos of language code and phonemes."""
	codePhoneme={}
	with open(inputDir+'codetophoneme.txt') as csvfile:
		codeToPhoneme=csv.DictReader(csvfile, fieldnames=['code','phoneme'], restkey=None, restval=None, dialect='excel')

		for row in codeToPhoneme:
			if row['code'] in codePhoneme:
				codePhoneme[row['code']].append(row['phoneme'])
			else:
				codePhoneme[row['code']] = [row['phoneme']]
	return codePhoneme

def featureDict():
	"""key:value combo of phonemes:allFeatures, from csv file. where's the csv file from?"""
	features={}
	with open(inputDir+'phonemetofeature2.csv','rU') as csvfile:
		phonemeToFeature=csv.DictReader(csvfile, fieldnames=None, restkey=None, restval=None, dialect='excel')

		for row in phonemeToFeature:
			features[row['phoneme']] = [row['f1']]
			for each in ['f2','f3','f4','f5','f6','f7','f8','f9','f10','f11']:
				if not row[each]=='':
					features[row['phoneme']].append(row[each])
				else:
					pass
					
	for each in features.keys()[0:5]:
		print features[each]
		
	return features
	

language=languageDict()
phonemes=phonemeDict()

languagePhoneme={}
for each in language.keys():
	languagePhoneme[language[each]]=phonemes[each]

features=featureDict()


"""The above loop links the language to its phonemes by the common lookup code"""


#Printout/writeToFile

errorLog=[]
directory='0_output_inventories/'
for curLanguage in languagePhoneme.keys():
	nameLanguage=curLanguage
	for each in ['?','!',"'","*"]:
		nameLanguage=nameLanguage.replace(each, "")
	f = open(directory+'_%s.csv' % (str(nameLanguage)) , 'w')
	f.write('phoneme,feature\n')
	for curPhoneme in sorted(languagePhoneme[curLanguage]):
		cleanPhoneme=curPhoneme.replace("\\", "")
		cleanPhoneme2=cleanPhoneme.replace("\"", "xx")
		cleanPhoneme2=cleanPhoneme2.replace("\'", "x")

		
		try:
			if featureCriteria in features[cleanPhoneme]: #only returns phonemes that contain criteria (see top of script).
				for feature in features[cleanPhoneme]:
					if feature==featureCriteria and criteriaDelete:
						pass # skips criteria feature before writing features to file, below.
					else:
						newString=str(cleanPhoneme2)+','+str(feature)+'\n'
						f.write(newString)
						if len(cleanPhoneme)>6:
							print newString
		except:
				print "Key error: "+str(cleanPhoneme)
				errorLog.append((curLanguage,cleanPhoneme))
	f.close()
if len(errorLog)>0:	
	f = open('errorLog.txt' , 'a')
	for curLanguage,cleanPhoneme in errorLog:
		newString=str(curLanguage)+'\t'+str(cleanPhoneme)+'\n'
		f.write(newString)
		
	f.close()

print len(set(errorLog))	
	
# for each in codePhoneme.values():
# for objy in each:
	# objy=objy.replace("\\", "")	
# objy=objy.replace("\\", "")
#JOIN
# s = "-";
# seq = ("a", "b", "c"); # This is sequence of strings.
# print s.join( seq )
#a-b-c