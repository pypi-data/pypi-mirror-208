# 2023.5.2,  loading 230537 essays 
import requests,time, fire,json, spacy # so 
from __init__ import *  # for debug , change to : from so import * 
nlp = spacy.load('en_core_web_sm')

def run(idxname, debug:bool=False, postag:bool=False, reset:bool=False):
	''' essay, 2023.5.2 '''
	from dic import essays
	if reset: requests.es.indices.delete(index=idxname)
	check(idxname) 
	start = time.time()
	for i, ess in enumerate(essays.essays):
		#if i > 5: break  # debug 
		did = f"doc-{ess.get('eid',0)}"
		print (did, flush=True) 

		ess.update({'type': 'doc' ,'did': did})
		esindex(idxname, did, ess ) # add essay 
		dskindex(idxname, did, ess) # add dsk 
	print(f"dsk indexing finished: {idxname}, \t| using: ", time.time() - start) 

	rows = cursor_rows(f"select sntid, did, snt, rid, uid from {idxname} where type ='snt' and sntid is not null ")
	print (len(rows), flush=True)
	for sid, did, snt,rid,uid in rows: 
		if debug : print ( sid, snt , flush=True) 
		doc = nlp(snt) 
		update(idxname, sid, skenp(doc)) #requests.es.update(index=idxname, id =sid, body= skenp(doc))  #partial update 
		for t in doc: 
			esindex(idxname, f"{sid}:tok-{t.i}", {"did": did, 'sid': sid, 'i': t.i, 'type':'tok', 'rid': rid, 'uid': uid,'lex': t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, 'govlem': t.head.lemma_, 'govpos': t.head.pos_ })

	print(f"tok indexing finished: {idxname}, \t| using: ", time.time() - start) 

if __name__ == '__main__': 	#run('testdoc', debug=True)
	run('essay', True) 
	#fire.Fire(run)

'''
fire.es.delete_by_query(index=fire.index, conflicts='proceed', body={"query":{"match":{"eid":eid}}})

POST /policy_document/policy_document/222/_update
{
  "doc": {
    "tags":["VIP"]
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