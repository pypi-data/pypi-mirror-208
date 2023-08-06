# 2023.5.10
import requests, traceback,sys , fire,spacy,os,json
from elasticsearch import Elasticsearch,helpers
from collections import Counter 

def run(index, pos:str='VERB', eshost:str='172.17.0.1:9200', debug:bool=False):
	''' python dump-pos.py nju2020 '''
	print ('[estok] start to walk:', index, flush=True)
	es	= Elasticsearch([ f"http://{eshost}" ])  
	si	= Counter()
	for doc in helpers.scan(client=es, query={"query" : {"match" : {"pos":pos}} }, index=index):
		# {'_index': 'nju2020', '_type': '_doc', '_id': 'doc-8697:snt-0:tok-15', '_score': None, '_source': {'level': 'gsl1', 'i': 15, 'idf': 2.6, 'type': 'tok', 'rid': 10, 'dep': 'conj', 'govlem': 'be', 'govpos': 'VERB', 'uid': 3544545, 'lem': 'have', 'pos': 'VERB', 'tag': 'VBZ', 'sntid': 'doc-8697:snt-0', 'did': 8697, 'lex': 'has'}, 'sort': [32]}
		try:
			if 'lem' in doc['_source'] and doc['_source']['lem'].isalpha():  
				si.update({doc['_source']['lem']:1})
		except Exception as ex:
			print(">>eswalk ex:", ex)
	
	with open(f"{index}.{pos}", 'w') as fw : 
		_sum = sum([i for s,i in si.items()])
		si.update({"_sum": _sum})
		fw.write( json.dumps(si) + "\n")

	print ('finished estok:', index, flush=True)

if __name__ == '__main__':
	fire.Fire(run)