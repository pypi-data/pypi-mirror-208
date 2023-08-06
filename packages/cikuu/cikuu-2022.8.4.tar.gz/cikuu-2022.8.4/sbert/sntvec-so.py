#2023.5.5  , to make a docker, data inside 
import json,os,time, platform,requests,math,re, redis,sys,traceback,random,fileinput,fire
import numpy as np 
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import __init__

def run(snt, rhost:str='172.17.0.1', rport=6380, debug:bool=False):
	''' python sntvec-so.py "I love you" '''
	r =redis.Redis(rhost,port= rport, decode_responses=False)
	vec = json.vec_encode(snt.strip())
	vector = np.array(vec).astype(np.float32).tobytes()
	if debug: print (vector, flush=True)
	SCHEMA = [
		TextField("snt"),
		VectorField("vec", "HNSW", {"TYPE": "FLOAT32", "DIM": 384, "DISTANCE_METRIC": "COSINE"}),
	]

	base_query = "*=>[KNN 7 @vec $vector AS vector_score]"
	query = Query(base_query).return_fields("snt", "vector_score").sort_by("vector_score").dialect(2)    
	result = r.ft("sntvecs").search(query, query_params={"vector": vector}) #<class 'redis.commands.search.result.Result'>
	for d in result.docs: print (d) #result.total, d.snt

if __name__ == '__main__':
	fire.Fire(run)

'''
ubuntu@dicvec-scivec-jukuu-com-flair-64-245:/data/cikuu/pypi/sbert$ python sntvec-so.py "She is very beautiful."
Document {'id': 'sntvec:44604e927ad054501f17edd8d5b1f25a', 'payload': None, 'vector_score': '0.226809322834', 'snt': "She's so beautiful herself."}
Document {'id': 'sntvec:a59e95ffb49520603119b981965f411d', 'payload': None, 'vector_score': '0.235813379288', 'snt': "She's beautiful in every way."}
Document {'id': 'sntvec:caee9b2322cc65c2417e7fd60ac03790', 'payload': None, 'vector_score': '0.236346185207', 'snt': 'She is known as a great beauty.'}
Document {'id': 'sntvec:87e97f19acdacfa0c06699b56475a0fe', 'payload': None, 'vector_score': '0.24262213707', 'snt': 'She is really a wonderful person.'}
Document {'id': 'sntvec:13177d3e4398dbc94bbfefc0051054ca', 'payload': None, 'vector_score': '0.260037779808', 'snt': 'She was a very beautiful woman.'}
Document {'id': 'sntvec:4dac2c716ac55716ed600338e1c4e81c', 'payload': None, 'vector_score': '0.266196846962', 'snt': 'She is a ravishing beauty.'}
Document {'id': 'sntvec:83a9ce0c1b7718d446de332c3f95480a', 'payload': None, 'vector_score': '0.268678188324', 'snt': "She's beautiful, vivacious, and charming."}
'''