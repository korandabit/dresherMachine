from __future__ import print_function
from language import Language, SDA
import cmd
import re
import main_1inventoryMover as m

class DresherInterface(cmd.Cmd):
	intro = "dresherian hierarchy suite"
	prompt = "> "
	def do_generate(self, args):
		[lang.hierarchies for lang in self.languages]
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
			res1, res2 = lang.query(hierq)
			if what == "count":
				print(len(res1), res2)
			if what == "print":
				print(res2)
				[print(h) for h in res1]
	def do_quit(self, args):
		return True
	def do_list(self, args):
		if args == "languages":
			for i, lang in enumerate(self.languages):
				print(i+1, lang.name)
		if args == "features":
			for i, lang in enumerate(self.languages):
				print(i+1, lang.name)
				print("[" + ", ".join([f for f in lang._features]) + "]")
if __name__=="__main__":
	interface = DresherInterface()
	fileList = m.mover(6)
	langs = []
	for i, f in enumerate(fileList):
		langs.append(Language.load_from_file(f, i+1))
	interface.languages = langs
	interface.cmdloop()
