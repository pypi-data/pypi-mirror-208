# 2023.5.9
import requests, traceback,sys ,fire, dic
from elasticsearch import Elasticsearch,helpers
from dic import word_idf 

def run(index, type:str='tok', eshost:str='172.17.0.1:9200', debug:bool=True):
	''' python tok-idf.py nju2020 '''
	print ('[eswalk] start to walk:', index, flush=True)
	es	= Elasticsearch([ f"http://{eshost}" ])  
	word_level = dic.word_level()  

	def update(id, arr): # arr = {"tags":"VIP"}
		try:
			return requests.post(f"http://{eshost}/{index}/_doc/{id}/_update", json={"doc":arr }).json() 
		except Exception as ex:
			print(">>esupdate ex:", ex)

	for doc in helpers.scan(client=es, query={"query" : {"match" : {"type":type}} }, index=index):
		try:
			id	= doc['_id']
			if debug: print ( id, flush=True ) 
			lex		= doc['_source']["lex"].strip().lower()
			idf		= word_idf.word_idf.get(lex, 0) 
			if idf > 0: 
				arr = {"idf": idf }
				level	= word_level.get(lex, '') 
				if level: arr.update({'level':level})
				update(id, arr ) 
		except Exception as ex:
			print(">>eswalk ex:", ex)
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
	print ('finished eswalking:', index, flush=True)

if __name__ == '__main__':
	fire.Fire(run)