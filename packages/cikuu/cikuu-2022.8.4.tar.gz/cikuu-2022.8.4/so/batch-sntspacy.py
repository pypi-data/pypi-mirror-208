# 2023.5.12, one line one snt, spacy json result 
import requests,time, fire,json, spacy, fileinput ,traceback, dic
from dic import word_idf 
from __init__ import * 

def run(infile, index:str=None, model:str="en_core_web_lg", debug:bool=False, tok:bool=False, reset:bool=True, batch:int=100000):
	''' gzjc.*.gz, 2023.5.2 '''
	if index is None : index = infile.split('.')[0] 
	if reset: drop(index)
	check(index) 
	nlp = spacy.load(model)
	word_level = dic.word_level()  
	print ( 'started:', infile, index, batch, flush=True)

	start = time.time()
	for did, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
		try:
			arr = json.loads(line.strip()) # dis
			doc = spacy.tokens.Doc(nlp.vocab).from_json( arr )
			sntid = f"snt-{did}"
			source = skenp(doc)
			source.update({"did":sntid, "type":"snt", "tc": len(doc),"snt":doc.text.strip()}) 
			addaction( {'_op_type':'index', '_index':index, '_id': sntid, '_source': source }, batch)
			
			if tok: 
				for t in doc:
					ar = {"did": sntid, 'i': t.i, 'type':'tok','lex': t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, 'govlem': t.head.lemma_, 'govpos': t.head.pos_ }
					idf = word_idf.word_idf.get(t.text.lower(), 0)
					if idf : ar.update({"idf":idf})
					level = word_level.get(t.text.lower(), '') 
					if level: ar.update({"level":level})
					addaction( {'_op_type':'index', '_index':index, '_id': f"{sntid}:tok-{t.i}", '_source': ar } )

		except Exception as e:
			print("ex:", e)	

	submit_actions()
	print(f"indexing finished: {index}, \t| using: ", time.time() - start) 

if __name__ == '__main__': 	#run('testdoc', debug=True)
	fire.Fire(run)