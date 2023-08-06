# 2023.5.2,  loading inau 
import requests,time, fire,json, spacy # so 
from __init__ import *  # for debug , change to : from so import * 
nlp = spacy.load('en_core_web_sm')

def run(folder:str, idxname:str=None, pattern:str=".txt", debug:bool=False, reset:bool=False): 
	''' inau, 2023.5.2 '''
	if idxname is None: idxname = folder 
	if reset: drop(idxname)
	check(idxname) 
	addfolder(folder, idxname, pattern)
	
	rows = cursor_rows(f"select did, doc from {idxname} where type ='doc' and did is not null ")
	print (len(rows), flush=True)
	for did, doc in rows: 
		if debug : print ( did, doc[0:20], flush=True) 
		tdoc = sntbr(doc) 
		for i, sp in enumerate(tdoc.sents): 
			snt = sp.text.strip() 
			sntid = f"{did}:snt-{i}"
			doc = nlp(snt) 
			arr = skenp(doc)
			arr.update({"did":did, "sntid":sntid, "type":"snt", "tc": len(sp),"snt":snt}) #			update(idxname, sntid, skenp(doc)) #requests.es.update(index=idxname, id =sid, body= skenp(doc))  #partial update 
			esindex(idxname, sntid, arr ) 
			for t in doc: 
				esindex(idxname, f"{sntid}:tok-{t.i}", {"did": did, 'sntid': sntid, 'i': t.i, 'type':'tok', 'lex': t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, 'govlem': t.head.lemma_, 'govpos': t.head.pos_ })

	print(f"tok indexing finished: {idxname}") 

if __name__ == '__main__': 	#run('testdoc', debug=True)
	#run('inau') 
	fire.Fire(run)

'''
fire.es.delete_by_query(index=fire.index, conflicts='proceed', body={"query":{"match":{"eid":eid}}})

POST /policy_document/policy_document/222/_update
{
  "doc": {
    "tags":["VIP"]
  }

GET /inau/_search
{
    "query": {
        "bool": {
            "must": [
                {"match": {"type" : "tok"}},
                {"match": {"tag" : "VBD"}}
            ]
        }
    }
}

}

  es.update( # excpetion here 
            index=log['_index'],
            doc_type='_doc',
            id=log['_id'],
            body={'doc':log['_source']} # 
        )

ubuntu@dicvec-scivec-jukuu-com-flair-64-245:~/cikuu/pypi/so/inaugural$ find . -name "*.txt" -exec python ../__main__.py add {} --taglist inau \;
'''