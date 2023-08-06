# 2023.3.16  python es-index.py spacysnt gzjc.jsonlg.3.4.1.gz --index snt
import json, traceback,sys, time,  fileinput, os, fire,pathlib, platform, so,hashlib
from __init__ import *
from elasticsearch import Elasticsearch,helpers
from collections import Counter,defaultdict
md5text	= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()
add = lambda source:  os.actions.append( {'_op_type':'index', '_index':os.index, '_id': source['id'], '_source': source } )

def index_snt(sid, doc, tok:bool=False, np:bool=False, src:str=None): 
	if tok: [add({"type":"tok", "id": f"{sid}-tok-{t.i}", "sid":sid, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_ , "gtag":t.head.tag_ }) for t in doc ]
	if np: [ add({"type":"np", "id": f"{sid}-NP-{sp.start}", "sid":sid, 'chunk':sp.text, 'lem':doc[sp.end-1].lemma_ }) for sp in doc.noun_chunks if sp.end - sp.start > 1 ]
	arr = {'type':'snt',  "id":f"{sid}", "sntid":f"{sid}", 'snt':doc.text.strip(), 'postag': es_hyb(doc), 'tc': len(doc), 'skenp': es_skenp(doc) }
	if src is not None: arr['src'] = src
	add( arr  ) #,  # merged NP must be finally called 
def index_doc(did, tdoc, tok:bool=False, np:bool=False, info:dict={}): 
	sntnum = len([index_snt(f"{did}-{sid}", sp.as_doc(), tok, np ) for sid, sp in enumerate(tdoc.sents) if sp.text.strip()]) 
	#del info['doc_txt'] # spider 
	arr = {'type':'doc', "id": did,   "did":did,  'doc':tdoc.text, 'sntnum': sntnum }
	if 'url' in info: arr['url']  = info['url'] 
	if 'pubdate' in info:  arr['pubdate'] = info['pubdate'] 
	add( arr ) # add( {'type':'doc', "id": did,   "did":did,  'doc':tdoc.text, 'sntnum': sntnum, 'url': info.get('url','') }  )

class util(object):

	def __init__ (self, host='172.17.0.1',port=9200):
		self.host = host
		self.es = Elasticsearch([ f"http://{host}:{port}" ])  
		os.actions=[] #	def add(source):  actions.append( {'_op_type':'index', '_index':idxname, '_id': source['id'], '_source': source } )

	def delete(self, index): self.es.indices.delete(index=index)

	def _submit(self, batch):
		if len(os.actions) >= batch: 
			helpers.bulk(client=self.es,actions=os.actions, raise_on_error=False)
			print ( os.actions[-1], flush=True)
			os.actions = []

	def indexdoc(self, infile, idxname,tok:bool=False, np:bool=False): 
		''' python es-index.py index hello.txt coca |  find . -name "*.txt" -exec python es-index.py indexdoc {} test \; '''
		text = open(infile, 'r').read().strip() 
		print(f">>load started: host={self.host}, index={idxname} " , infile,  len(text),  flush=True )
		if not self.es.indices.exists(index=idxname): self.es.indices.create(index=idxname, body=so.config) 

		os.index = idxname 
		index_doc(infile.split('/')[-1], spacy.nlp(text))
		if os.actions : helpers.bulk(client=self.es,actions=os.actions, raise_on_error=False)
		print(">>load finished:" , infile, idxname, len(os.actions) )

	def spacysnt(self, infile, index:str=None, batch=200000,tok:bool=False, np:bool=False, topk:int=None): 
		''' python3 es-index.py spacysnt gzjc.jsonlg.3.4.1.gz'''
		os.index = index if index is not None else infile.split('.')[0]
		print(f">>[es-index spacysnt] load started: host={self.host}, index={os.index} " , infile, os.index, flush=True )
		if not self.es.indices.exists(index=os.index): self.es.indices.create(index=os.index, body=so.config) 
				
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				if topk is not None and sid > topk : break  # added 2023.3.17
				doc = Doc(spacy.nlp.vocab).from_json(json.loads(line.strip())) 
				index_snt(sid if index is None else md5text(doc.text), doc, tok, np, src=None if index is None else infile.split('.')[0]) 
				self._submit(batch) 
			except Exception as e:
				print("ex:", e, sid)	
				exc_type, exc_value, exc_obj = sys.exc_info() 	
				traceback.print_tb(exc_obj)
		if os.actions : helpers.bulk(client=self.es,actions=os.actions, raise_on_error=False)
		print(">>[es-index spacysnt] load finished:" , infile, sid, os.index )

	def spacydoc(self, infile, index:str=None, batch=200000,tok:bool=False, np:bool=False): 
		''' spider-aa.docjsonlg.3.4.1.gz '''
		os.index = index if index is not None else infile.split('.')[0].lower()
		print(f">>[es-index spacydoc] load started: host={self.host}, index={os.index} " , infile, os.index, flush=True )
		if not self.es.indices.exists(index=os.index): self.es.indices.create(index=os.index, body=so.config) 
				
		for did, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				arr = json.loads(line.strip())
				tdoc = Doc(spacy.nlp.vocab).from_json(arr) 
				info = arr.get('info',{}) # 
				if id in info : did = info['id']  # url inside
				index_doc(did, tdoc, tok, np, info) 
				self._submit(batch) 
			except Exception as e:
				print("ex:", e, did)	
				exc_type, exc_value, exc_obj = sys.exc_info() 	
				traceback.print_tb(exc_obj)
		if os.actions : helpers.bulk(client=self.es,actions=os.actions, raise_on_error=False)
		print(">>[es-index spacydoc] finished:" , infile, os.index )

	def es_submit(self, infile, index:str=None, batch=200000, recreate:bool=True, host='172.17.0.1',port=9200): 
		''' python3 -m api.sntjson-es gzjc.jsonlg.3.4.1.gz'''
		
		if index is None : index = infile.split('.')[0]
		print(f">>load started: host={host}, index={index} " , infile, index, flush=True )
		if recreate or not es.indices.exists(index=index): 
			if es.indices.exists(index=index):es.indices.delete(index=index)
			es.indices.create(index=index, body=so.config) 

		actions=[]
		def add(source):  
			actions.append( {'_op_type':'index', '_index':index, '_id': source['id'], '_source': source } )
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				doc = Doc(spacy.nlp.vocab).from_json(json.loads(line.strip())) # add skenp 
				for t in doc: 	add({"type":"tok", "id": f"{sid}-tok-{t.i}", "sid":sid, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_ , "gtag":t.head.tag_ }) #'i':t.i, "head":t.head.i,
				for sp in doc.noun_chunks: 	
					if sp.end - sp.start > 1: # skip PROPN ? 
						add({"type":"np", "id": f"{sid}-NP-{sp.start}", "sid":sid, 'chunk':sp.text, 'lem':doc[sp.end-1].lemma_ })
				for lem, pos, type, chunk in kp_matcher(doc): #brink:NOUN:pp:on the brink # [('pp', 'on the brink', 2, 5), ('ap', 'very happy', 9, 11)]
					add({"type":type, "id": f"{sid}-{type}-{chunk}", "sid":sid,  'chunk':chunk, 'lem':lem , "pos":pos}) #"src": doc.text,
				for name, ar in depmatch()(doc) : 
					type = spacy.nlp.vocab[name].text # worry be thrilled
					lem = doc[ar[0]].lemma_
					add({"type":type, "id": f"{sid}-{type}-{lem}", "sid":sid,  'lem':lem,  'tag':doc[ar[0]].tag_, 'lem1':doc[ar[1]].lemma_, 'lem2':doc[ar[2]].lemma_ , 'tag1':doc[ar[1]].tag_ , 'tag2':doc[ar[2]].tag_ }) 
				# merged NP must be finally called 
				add( {'type':'snt',  "id":sid,  'snt':doc.text, 'postag': es_postag(doc), 'tc': len(doc), 'skenp': es_skenp(doc) }  ) #, 
				if len(actions) >= batch: 
					helpers.bulk(client=es,actions=actions, raise_on_error=False)
					print ( sid, actions[-1], flush=True)
					actions = []
					#refresh() # 2022.1.23 
			except Exception as e:
				print("ex:", e, sid)	
				exc_type, exc_value, exc_obj = sys.exc_info() 	
				traceback.print_tb(exc_obj)
		if actions : helpers.bulk(client=es,actions=actions, raise_on_error=False)
		print(">>load finished:" , infile, index )

if __name__	== '__main__':
	print("ehllo") if platform.system() in ('Windows') else fire.Fire(util)

''' spider 
"info": {"id": 3000001, "did": 302539, "domain": "www.newsday.com", "description": "A new hunting season Will Attorney General William Barr be the instrument of Donald Trump's revenge against the \"witch hunt?\" The president would be terribly disappointed if Barr said he wouldn't be.", "title": "AG Barr goes snoop dogging, probes Trump probers", "url": "https://www.newsday.com/long-island/politics/trump-barr-mueller-russia-fbi-1.29655697", "doc_txt": "A new hunting

POST /endic/_search
{
  "query": {
    "intervals" : {
      "postag" : {
        "all_of" : {
          "ordered" : true,
          "intervals" : [
            {
              "match" : {
                "query" : "_overcome the",
                "max_gaps" : 1,
                "ordered" : true
              }
            },
            {
              "any_of" : {
                "intervals" : [
                  { "match" : { "query" : "difficulty" } },
                  { "match" : { "query" : "problem" } }
                ]
              }
            }
          ]
        }
      }
    }
  }
}
'''