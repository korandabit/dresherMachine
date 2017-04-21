from __future__ import print_function
from collections import defaultdict
from language import Language, SDA
import cmd
import re
import csv
import tables
import threading
import os
from shutil import rmtree
import main_1inventoryMover as m

class DresherInterface(cmd.Cmd, object):
	intro = "dresherian hierarchy suite"
	prompt = "> "
	
	oldsummary_format = ["inv", "linv", "freq", "min", "lfeats", "feats", "names"]
	hierarchy_format = ["something", "else"]
	summary_format = ["inv", "linv", "freq", "lhiers", "min", "lminh", "minmark", "avemark", "lfeats", "feats", "names"]

	

	def __init__(self):
		super(DresherInterface, self).__init__()
		# Clean up from last run
		try:
			rmtree("run")
		except OSError:
			pass
		os.mkdir("run")
		os.chdir("run")
		self.languages = []
		self.generate_threads = []
		self.query_thread_dict = defaultdict(list)
		self.inv_name_dict = defaultdict(list)
		self.queries = []
	def do_load(self, args):
		"""syntax: load folder length
loads files from specified folder of specified inventory length
length optional
ex: load 0_output_inventories/ 5
"""
		splitargs = args.split(" ")
		folder = splitargs[0]
		self.languages = []
		os.chdir("..")
		
		featdictdict = {}
		for fname in os.listdir(folder):
			with open(os.path.join(folder, fname), 'rU') as f:
				reader = csv.DictReader(f)
				reader = [{'phoneme': row['phoneme'], 'feature': row['feature']} for row in reader]
				phones = frozenset([row['phoneme'] for row in reader])
				featdictdict[phones] = {phone: [row['feature'] for row in reader if row['phoneme'] == phone] for phone in phones}
				self.inv_name_dict[phones].append(os.path.splitext(fname)[0].strip("_"))
		os.chdir("run")
		for inv, invdict in featdictdict.items():
			feats = tuple(set([feat for key in inv for feat in invdict[key]]))
			featDict = {phone: [1 if feat in invdict[phone] else 0 for feat in feats] for phone in inv}
			self.languages.append(Language(self.inv_name_dict[inv][0], len(self.inv_name_dict[inv]), featDict, feats))
		#fileList = m.mover(int(args))
		
		#os.chdir("run")
		#print(fileList)
		#for f in fileList:
		#	lname, ldict, lfeats = Language.load_from_file(f)
		#	print(lname, ldict.keys())
		#	if ldict.keys() in [lang._phones.keys() for lang in self.languages]:
		#		print("duplicate inveontory found")
		#		self.languages[[lang._phones.keys() for lang in self.languages].index(ldict.keys())].name += lname
		#	else:	
		#		self.languages.append(Language(lname, len(self.languages) + 1, ldict, lfeats))
	def do_filter(self, args):
		lens = [int(i) for i in args.split(" ")]
		newlangs = []
		for lang in self.languages:
			if len(lang._phones.keys()) in lens:
				newlangs.append(lang)
		for lang in self.languages:
			if lang not in newlangs:
				lang.table_file.close()
		self.languages = newlangs
#	def do_add(self, args):
#		os.chdir("..")
#		fileList = m.mover(int(args))
#		os.chdir("run")
#		for f in fileList:
#			lname, ldict, lfeats = Language.load_from_file(f)
#			print(lname, ldict.keys())
#			# make sure language not already loaded by checking name
#			if lname.strip(".")  not in [la.name for la in self.languages]:
#				self.languages.append(Language(lname, len(self.languages) + 1, ldict, lfeats))
	def do_generate(self, args):
		[lang.hierarchies for lang in self.languages]
	def do_threadedgen(self, args):
		for lang in self.languages:
			t = threading.Thread(name = lang.name + " hierarchies", target = getattr, args= (lang, "hierarchies"))
			print("spawning thread to generate hierarchies for " + lang.name)
			t.start()
			self.generate_threads.append(t)
	def do_query(self, query):
		"""Usage: query languages (if condition) count/print hierarchycondition
where:
	languages 		= all OR list of language numbers (as in > list languages)
	condition		= list of features that must be present for a language to be queried
	count			= returns count of hierarchies that satisfy hierarchycondition
	print			= prints the hierarchies that satisfy hierarchycondition
	hierarchycondition	= condition on ordering of features in hierarchies (see examples)
Examples:	
	1. query all if nasal count nasal > low
		this counts the hierarchies where the feature nasal is ordered before low in languages where nasal is a possible feature
		this is different from
	2. query all count nasal > low where nasal
		1. will only search through languages where nasal is a contrastive feature
		2. will search all languages, but will only count/return hierarchies that contain nasal. think of the "where" keyword as changing the denominator
	3. query [1, 2, 3] count [nasal, low] > high where round
		this will query only languages 1 2 and 3, counting hierarchies where both nasal and low are ordered before high (with no constraint on the ordering of nasal and low) and only checks hierarchies that use the feature round
		"""
		#TODO queries can be async threads too to allow multiple 'simultaneous' queries

		#regex = re.compile(r"\A(?P<cond>.*?(?= if (?P<predicate>.*)))|(.*)(?= count (.*))")
		#print(regex.match(query).groups())
		split = re.split(r"\s+(count|print)\s+", query)
		langq = split[0]
		what = split[1]
		hierq = split[2]
		langsp = re.split(r"\s+if\s+", langq)
		print(split)
		print(langsp)
		if langsp[0].lower() == "all":
			langset = self.languages
		else:
			langset = [self.languages[int(ind)-1] for ind in re.split(r"\s*,\s*", langsp[0].strip("[]"))]
		try:
			langsp[1]
			cond = lambda lang: set(tuple(re.split(r"\s*,\s*",langsp[1].strip("[]")))).issubset(set(tuple(lang._features)))
		except IndexError:
			cond = lambda lang: True
		langset = [lang for lang in langset if cond(lang)]
		for lang in langset:
			print(lang.name)
			#TODO make querying into a thread of its own to allow multiple languages
			# to be queried at once. This is tricky because of return values
			res1, res2 = lang.query(hierq)
			if what == "count":
				print(len(res1), res2)
			if what == "print":
				print(res2)
				[print(h) for h in res1]
		
	def do_quit(self, args):
		if args == "save":
			# save session
			[t.join() for t in self.generate_threads]
			for lang in self.languages:
				lang.table_file.close()
			return True
		if threading.active_count() == 1 or args == "force":
			os.chdir("..")
			rmtree("run")
			return True
		print(str(threading.active_count()) + " thread(s) still alive")
		if args == "wait":
			# wait is really a pointless option
			[t.join() for t in self.generate_threads]
			os.chdir("..")
			rmtree("run")
			return True
	def do_list(self, args):
		if args == "languages":
			[print(i+1, lang.name) for i, lang in enumerate(self.languages)]
		if args == "features":
			for i, lang in enumerate(self.languages):
				print(i+1, lang.name)
				print("[" + ", ".join([f for f in lang._features]) + "]")
		if args == "phones":
			for i, lang in enumerate(self.languages):
				print(i+1, lang.name)
				print("[" + ", ".join([f for f in lang._features]) + "]")
				[print(str(k) + " : " + str(v)) for k, v in lang._phones.items()]
		if args == "threads":
			print("Generation threads")
			[print(thread.name) for thread in self.generate_threads if thread.is_alive()]
		if args == "queries":
			[print(i+1, q) for i, q in enumerate(self.queries.keys())]
	def do_min(self, args):
		for lang in self.languages:
			oldverbose = lang.verbose
			lang.verbose = True
			lang.min_analysis()
			lang.verbose = oldverbose
	def do_write(self, args):
		""" Writes desired data to csv
syntax: write outfile what fields
what can be summary, hierarchies, or custom
built in output structures:
	1) 
	2) 
	3)
available fields:
	
		"""
		asplit = args.split(" ")
		fname = asplit[0]
		what = asplit[1]
		os.chdir("..")	
		with open(fname, 'wb') as f:
			if what == "summary" or what == "oldsummary":
				form = DresherInterface.summary_format if what == "summary" else DresherInterface.oldsummary_format
				dw = csv.DictWriter(f, delimiter = "\t", fieldnames = form)
				dw.writeheader()
				for lang in sorted(self.languages, key = lambda l: len(l._phones.keys())):
					dw.writerow(dict(zip(form, [self.get_language_info(lang, x) for x in form])))
			if what == "hierarchies":
				pass
		os.chdir("run")
		# parse what the user wants to write to file
		
		# make sure all the threads that need to be finished have finished
		# using .join() on the appropriate groups of threads
	def get_language_info(self, lang, arg):
		if arg == "name":
			return lang.name
		if arg == "lhiers":
			return sum(lang.hierarchyLengths.values())
		if arg == "lminh":
			return lang.hierarchyLengths[lang.min_analysis()[0]]
		if arg[0] == "l":
			return len(self.get_language_info(lang, arg[1:]))
		if arg == "inv":
			return lang._phones.keys()
		if arg == "feats":
			return lang._features			
		if arg == "names":
			return self.inv_name_dict[frozenset(lang._phones.keys())]
		if arg == "freq":
			# equivalent to lnames
			return lang.freq
		if arg == "min":
			return lang.min_analysis()[0]
		if arg == "minmark":
			return min(lang.efficiency_analysis()[1].keys())
		if arg == "avemark":
			_, d = lang.efficiency_analysis()
			tot = sum([m*freq for m, freq in d.iteritems()])
			denom = sum([freq for m, freq in d.iteritems()])
			return tot/float(denom)
if __name__=="__main__":
	interface = DresherInterface()
	interface.cmdloop()
