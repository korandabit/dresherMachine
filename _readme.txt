KDM_LSA 
2017.01.30

PROJECT FILE DESCRIPTION/INSTRUCTION
See list below for minimum runtime and dependent files. 
Run main.py from command line, edit main.py for most functionality. outputs to .txt file. 
Reads csv files in place. Optionally, vowel inventory size can be specified from the command line:

python main.py 5

will analyze all unique 5-vowel inventories. Default parameters include a pre-processed set of vowel inventories
(00_KDM_inventoryGenerator). main.py will extract only unique inventories of the vowel size specified (integer, 
not ranges), and analyze over them. Currently set to look at a random subset of possible combos (saves on CPU),
analyzes, but does not write to file. 

I've centralized all python scripts to this main folder, and pointed to folders for any dependent files. one-off '*.txt' files write to this folder.


Runtime
main.py				most major functions run from this script. The exceptions follow. go here to make basic
				modifications, e.g. set vowel inventory size, count of inventories, write to file, run 
				analyses or not, etc.
'00_KDM_inventoryGenerator.py'	Generates inventories using 3 files from '0_input_files/'
				saves inventories to '0_output_inventories/'
09_featureProject		identifies unique feature count and items per inventory (can easily be integrated to 
				main.py).


This folder contains the following dependent python scripts and folders.


'main_1inventoryMover.py'	Identifies csv scripts for analyses.

'main_2inventoryParser2.py'	Parses identified scripts for feature set combos.
	
'main_3min_analysis.py'		Analyzes minimum and unique feature sets.

'main_4efficiency_analysis.py'	Computes raw efficiency for all permutations of unique feature sets in main_3

'dresher_LSA.py'		Library of functions for '1_KDM_inventoryParser.py'

'\0_output_inventories'		needs to contain at least 1 csv script with 2 columns: object and attribute. 


Change log

2017.01.05
	started working on the main algorithm, in inventoryParser2_1 (see there for details). cleaned up a LOT of visualization, so that lines are written over instead of returned in commandline. 
	Known bug: Current analysis output (e.g. some 6v outputs, especially with random generator on (i.e. analyze a % of all permutations) fail to completely parse vowel inventories (see error at output for main_4).
2016.12.31
	The structure of KDM_LSA has been streamlined through a single main.py file. Run that, and play with variables therein if you're lost. It has 4 main_*.py dependent files. 
		Besides streamlining, the major improvement is handling of read/write to disk. No files are written to disk until the end.

2016.12.30
	This file has not been completely updated. Major changes include 1) additional analyses files (30_KDM,09_KDM) 2) filenames extended to unique 2-digits and other name changes.
	Global tasks.
		12_KDM consolidates unique-ordered sets into unique unordered sets, divergent from 10_KDM. Further testing needed to validate this improvement.
		12_KDM and 09_featureProject are cleaned up to have runtime Vars. The rest of the scripts need more of this.
		All scripts need more modular functions, centralized and flexible.
		Modular functions need to be gloabally implemented. One example is writeBlock, which works well in 09,12, and 30 (I think).
		efficienctTree in 1*_KDM needs algorithm consolidating/reorganizing. (peculiar behavior explanation still outstanding)
	See _project notes for more.