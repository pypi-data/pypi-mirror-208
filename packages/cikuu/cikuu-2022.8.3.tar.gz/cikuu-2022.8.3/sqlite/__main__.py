#!/usr/bin/env  -*- coding: utf-8	-*-  2023.5.1
import sqlite3,collections, sqlite, fire

class Util(object):
	def __init__(self): pass 

	def sntdb(self, infile, output:str=None): 
		''' python -m sqlite sntdb gzjc.snt | load gzjc.snt -> gzjc.sntdb, for hnswlib indexer, 2023.5.1 '''
		if output is None: output = infile.split('.')[0]
		db = sqlite.Sntdb(f"{output}.sntdb")
		db.load(infile) # gzjc.snt
		db.close()
		print ("fininshed:", infile,output )

if __name__	== '__main__':
	fire.Fire(Util)