# This is the Command Line interface for geneWordSearch.
# Needs to be run from the main program folder.

# Written by Joe Jeffers 
# Updated Jan 12 2015

import sys
import pickle
import argparse
from GeneWordSearch import geneWordSearch
from Classes import WordFreq

# Function to print the results 
def resultsPrinter(results, web, table, outfile, singles, genes):
	# Input: 
	#	The results from the geneWordSearch function
	#	a boolean for wheather to print links
	#	A boolean for whether it should be table output
	#	A writeable file object
	
	# Split the results
	words = results[0]
	links = results[1]
	
	if(table):
		# Print the header for the table
		outfile.write(WordFreq.robotHeaders(genes)+ '\n')
	
		# Print the genes by category of multiples and singles
		outfile.write('Multiple Gene Words:' + '\n' + '\n')
		for item in words:
			if(item.freq > 1):
				outfile.write(item.forRobot(genes) + '\n')
		
		if(singles):
			outfile.write('Single Gene Words:' + '\n' + '\n')
			for item in words:
				if(item.freq == 1):
					outfile.write(item.forRobot(genes) + '\n')
		
	# Prints out web links if needed
		if(web):
			for link in links:
				outfile.write(link + '\n')
	
	else:
		# Print the genes by category of multiples and singles
		outfile.write('Multiple Gene Words:' + '\n' + '\n')
		for item in words:
			if(item.freq > 1):
				outfile.write(item.forHuman(genes) + '\n')
		
		if(singles):
			outfile.write('Single Gene Words:' + '\n' + '\n')
			for item in words:
				if(item.freq == 1):
					outfile.write(item.forHuman(genes) + '\n')
	
	# Prints out web links if needed
		if(web):
			outfile.write('Web Links associated with these genes:'+'\n' + '\n')
			for link in links:
				outfile.write(link + '\n' + '\n')

# Setup the Parser
parser = argparse.ArgumentParser(description='Find the important words associated with supplied genes.')
parser.add_argument('-c',action='store_true',default=False,help=
'Sorts results by Holm–Bonferroni corrected p values to compensate for multiple hypothesis problem.')
parser.add_argument('-d',action='store_true',default=False,help=
'Indicates that input are database files, will start interactive DB builder. Please run again to indicate anlysis options after db is built (requires -s).')
parser.add_argument('-g',action='store_true',default=False,help=
'Prints list of genes associated with each word.')
parser.add_argument('-m',action='store_false',default=True,help=
'This prevents the writing of the words that only occur in one of the genes inputed.')
parser.add_argument('-n',action='store_true',default=False,help=
'Indicates the input is the starting point of a network, will first return list of genes in those networks, then the traditional output on that list of genes. Only works with maize at the momment (Incompatible with -d and -f).')
parser.add_argument('-o',action='store',type=str,default='out.txt',help=
'Location to write the file that contains the results, default is out.txt in current folder.')
parser.add_argument('-p',action='store',type=float,default=0.05,help=
'This option takes one argument and sets the probability cutoff, default is 0.05.')
parser.add_argument('-s',action='store',type=str,help=
'Allows indication of species to work with, \'maize\' and \'ath\' are currently available.')
parser.add_argument('-t',action='store_true',default=False,help=
'This will give a tsv output for machine readable purposes. Default is human readable output.')
parser.add_argument('-u',action='store',type=str,help=
'Takes one argument, file with list of genes to be used as universe for enrichment query. One gene per line or split by comma.')
parser.add_argument('-w',action='store_true',default=False,help=
'This will output associated weblinks with standard gene output.')
parser.add_argument('--file',action='store_true',default=False,help=
'This indicates that the input strings will be a file with genes in it (Incompatible with -d and -n).')
parser.add_argument('--folder',action='store_true',default=False,help=
'Indicates that the input is a directory and will process all files in the directory (Incompatible with -f and -n).')
parser.add_argument('things',action='store',nargs='*')

# Parse the arguments
args = parser.parse_args()
args.s = args.s.lower()

# Build alternate universe if it is so ordained
if(args.u):
	import DBBuilder
	genes = []
	geneUni = open(args.u)
	for row in geneUni.readlines():
		rowsy = row[:-1]
		genes += rowsy.split(',')
	DBBuilder.tempBuilder(genes,args.s)
	args.s = 'tmp'
	geneUni.close()
	del genes

# Open the output file for writing
out = open(args.o,'w')

if(args.file):
# Deals with input if it is a file name
	genes = []
	for name in args.things:
		geneList = open(name)
		for row in geneList.readlines():
			genes += row.split()
	results = geneWordSearch(genes,args.s,minChance=args.p,corrected=args.c)
	resultsPrinter(results,args.w,args.t,out,args.m,args.g)

elif(args.n):
# Deals with finding the gene network
	genes = []
	nets = open('databases/'+ args.s +'/networks.p','rb')
	networks = pickle.load(nets)
	
	for gene in args.things:
		genes += networks[gene]
	
	out.write('These are the genes related to the gene(s) you identified:'+'\n')	
	for gene in genes:
		out.write(gene + '\n')
	
	out.write('\n' + 'Results from this list:' + '\n' + '\n')
	results = geneWordSearch(genes,args.s,minChance=args.p,corrected=args.c)
	resultsPrinter(results,args.w,args.t,out,args.m,args.g)

elif(args.folder):
# Deals with directory option
	import glob
	
	results = []
	for folder in args.things:
		if(not(folder[-1] == '/')):
			folder += '/'
		fileList = glob.glob(folder + '*.txt')
		for fileName in fileList:
			genes = []
			geneList = open(fileName)
			for row in geneList.readlines():
				genes += row.split()
			if((len(genes) >= 10) and (len(genes) <= 300)):
				out.write('\n' + '\n')
				out.write('Results for ' + fileName + ':')
				out.write('\n' + '\n')
				results = geneWordSearch(genes,args.s,minChance=args.p,corrected=args.c)
				resultsPrinter(results,args.w,args.t,out,args.m,args.g)
			geneList.close()

elif(args.d):
	import DBBuilder
	DBBuilder.buildDBs(args.s,args.things)
	print('Database has been built in /databases/'+args.s)
	print('Please run this program again to do the gene analysis, and use the options -s')
	
else:
# Handles normal gene list input
	genes = args.things
	results = geneWordSearch(genes,args.s,minChance=args.p,corrected=args.c)
	resultsPrinter(results,args.w,args.t,out,args.m,args.g)

if not(args.d):
	out.close()
	if(args.u):
		import shutil
		shutil.rmtree('databases/tmp/')
	print('Completed! Check ' + args.o + ' for your results.')




