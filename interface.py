from __future__ import print_function
from builtins import range
from collections import defaultdict
from language import Language, SDA
import cmd
import re
import csv
#import tables
import threading
import os
import glob
import readline
from shutil import rmtree
readline.set_completer_delims(" \t\n")
history_file = os.path.abspath(".dresher_interface_history")
history_length = 100

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
		self.languages = []
		self.generate_threads = []
		self.query_thread_dict = defaultdict(list)
		self.inv_name_dict = defaultdict(list)
		self.feature_dict = defaultdict(list)
		self.lang_phone_dict = defaultdict(list)
		self.queries = []
		self.verbose = False
		self.semaphore = threading.BoundedSemaphore(10)
	def log(self, *args):
		if self.verbose:
			print(*args)
	def wrap_semaphore(self, f):
		def wrapped(*args, **kwargs):
			self.log("waiting for semaphore")
			with self.semaphore:
				self.log("got semaphore")
				result = f(*args, **kwargs)
				self.log("releasing semaphore")
			return result
		return wrapped
	def preloop(self):
		if os.path.exists(history_file):
			readline.read_history_file(history_file)
	def postloop(self):
		readline.set_history_length(history_length)
		readline.write_history_file(history_file)
	def do_languages(self, args):
		"""syntax: languages file filter"""
		self.lang_phone_dict = defaultdict(list)
		self.inv_name_dict = defaultdict(list)
		self.languages = []
		sp = args.split(" ")
		f = sp[0]
		fil = sp[1:]
		langs_file = open(f, "r")
		for line in langs_file:
			sp = line.strip("\n").split(",")
			lang = sp[0]
			phone = sp[1].strip("\r")
			if set(fil) <= set(self.feature_dict[phone]):
				self.lang_phone_dict[lang].append(phone)
		for (k, v) in self.lang_phone_dict.items():
			self.inv_name_dict[frozenset(v)].append(k)
		for (inv, names) in self.inv_name_dict.items():
			lang_feats = tuple(set([feat for key in inv for feat in self.feature_dict[key]]))
			lang_feat_dict = {phone: [1 if feat in self.feature_dict[phone] else 0 for feat in lang_feats] for phone in inv}
			self.languages.append(Language(names[0], len(names), lang_feat_dict, lang_feats, self.semaphore))
	def do_features(self, f):
		"""syntax: features file"""
		self.feature_dict = defaultdict(list)
		feat_file = open(f, "r")
		for line in feat_file:
			if line == "\n":
				continue
			sp = line.strip("\n").split(",")
			phoneme = sp[0]
			features = sp[1:]
			features = [f for f in features if f != "" and f != "\n" and f != "\r\r"]
			self.feature_dict[phoneme] = features
	def do_load(self, args):
		"""syntax: load folder length(s)
loads files from specified folder of specified inventory length(s)
length(s) optional
ex: load 0_output_inventories/ 5
NOTE: currently just loads all the inventories from the folder
"""
		splitargs = args.split(" ")
		folder = splitargs[0]
		self.languages = []
		
		featdictdict = {}
		for fname in os.listdir(folder):
			with open(os.path.join(folder, fname), 'rU') as f:
				reader = csv.DictReader(f)
				try:
					reader = [{'phoneme': row['phoneme'], 'feature': row['feature']} for row in reader]
				except:
					continue
				phones = frozenset([row['phoneme'] for row in reader])
				featdictdict[phones] = {phone: [row['feature'] for row in reader if row['phoneme'] == phone] for phone in phones}
				self.inv_name_dict[phones].append(os.path.splitext(fname)[0].strip("_"))
		with wd("run"):
			for inv, invdict in featdictdict.items():
				feats = tuple(set([feat for key in inv for feat in invdict[key]]))
				featDict = {phone: [1 if feat in invdict[phone] else 0 for feat in feats] for phone in inv}
				self.languages.append(Language(self.inv_name_dict[inv][0], len(self.inv_name_dict[inv]), featDict, feats))
	def do_filter(self, args):
		"""syntax: filter length(s)
ex: filter 3 4 5
throws out currently loaded languages whose length is not 3, 4, or 5
"""
		lens = [int(i) for i in args.split(" ")]
		newlangs = []
		for lang in self.languages:
			if len(lang._phones.keys()) in lens:
				newlangs.append(lang)
		# uncomment these lines if I switch back to hdf5 tables
		#for lang in self.languages:
		#	if lang not in newlangs:
		#		lang.table_file.close()
		self.languages = newlangs
	def do_generate(self, args):
		"""generate the hierarchies for languages"""
		[lang.hierarchies for lang in self.languages]
	def do_threadedgen(self, args):
		"""use multithreading to generate hierarchies
"""
		for lang in self.languages:
			t = threading.Thread(name = lang.name + " hierarchies", target = self.wrap_semaphore(getattr), args= (lang, "hierarchies"))
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
			# uncomment if we go back to hdf5 tables
			#for lang in self.languages:
			#	lang.table_file.close()
			return True
		if threading.active_count() == 1 or args == "force":
			rmtree("run")
			return True
		print(str(threading.active_count()) + " thread(s) still alive")
		if args == "wait":
			# wait is really a pointless option
			[t.join() for t in self.generate_threads]
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

		if what == "summary" or what == "oldsummary":
			with open(fname, 'w') as f:
				form = DresherInterface.summary_format if what == "summary" else DresherInterface.oldsummary_format
				for i, x in enumerate(form):
					f.write(x)
					if i == len(form)-1:
						f.write("\n")
					else:
						f.write("\t")
				#for lang in sorted(self.languages, key = lambda l: len(l._phones.keys())):
				#	dw.writerow(dict(zip(form, [self.get_language_info(lang, x) for x in form])))
				for lang in sorted(self.languages, key = lambda l: len(l._phones.keys())):
					for i, x in enumerate(form):
						f.write(str(self.get_language_info(lang, x)))
						if i == len(form)-1:
							f.write("\n")
						else:
							f.write("\t")
		if what == "hierarchies":
			# format: #vowels, langname, hierarchy, len(hier), #of marks, lfeats, inv, freq, 
			# how many times each feat marked, the actual marks, vowel:feature set, unused features
			# take fname to be name of directory to write outfiles to
			with wd(fname):
				for lang in self.languages:
					num_vowels = self.get_language_info(lang, "linv")
					name = lang.name
					num_feats = self.get_language_info(lang, "lfeats")
					inv = self.get_language_info(lang, "inv")
					freq = self.get_language_info(lang, "freq")
					inv_feats = lang.phone_feat_dict
					with open(name.replace(" ","")+".txt", 'w') as f:
						f.write("num_vowels\tname\thierarchy\tlen_hier\tnum_marks\tnumfeats\tinv\tfreq\tfeat_marks\tinv_marks\tinv_feats\tunused_feats\n")
						for h in lang.hierarchies:
							f.write(str(num_vowels))
							f.write("\t")
							f.write(name)
							f.write("\t")
							f.write(str(h))
							f.write("\t")
							f.write(str(len(h)))
							f.write("\t")
							spec = SDA(lang._phones, lang._features, h)
							markedness = sum([x for phone in spec.keys() for x in spec[phone] if x == 1])
							f.write(str(markedness))
							f.write("\t")
							f.write(str(num_feats))
							f.write("\t")
							f.write(str(inv))
							f.write("\t")
							f.write(str(freq))
							f.write("\t")
							feat_counts = {f:sum([spec[phone][i] for phone in spec.keys() if spec[phone][i] == 1]) for i, f in enumerate(h)}
							f.write(str(feat_counts))
							f.write("\t")
							f.write(str(spec))
							f.write("\t")
							f.write(str(inv_feats))
							f.write("\t")
							f.write(str(list(set(lang._features)-set(h))))
							f.write("\n")
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
			return list(lang._phones.keys())
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
			tot = sum([m*freq for m, freq in d.items()])
			denom = sum([freq for m, freq in d.items()])
			return tot/float(denom)
	def complete_features(self, text, line, startx, endx):
		return complete(text)
	def complete_languages(self, text, line, startx, endx):
		return complete(text)
class wd:
	def __init__(self, desired_wd):
		self.new_wd = desired_wd
		self.old_wd = os.getcwd()
	def __enter__(self):
		if not os.path.exists(self.new_wd):
			os.mkdir(self.new_wd)
		os.chdir(self.new_wd)
	def __exit__(self, t, value, traceback):
		os.chdir(self.old_wd)

def complete(path):
	if os.path.isdir(path):
		return glob.glob(os.path.join(path, "*"))
	return glob.glob(path + "*")

if __name__=="__main__":
	interface = DresherInterface()
	interface.cmdloop()
