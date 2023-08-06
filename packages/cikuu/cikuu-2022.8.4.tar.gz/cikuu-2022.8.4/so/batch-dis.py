# 2023.5.10, batch-index-dis,  cp from index-dis.py 
import requests,time, fire,json, spacy, fileinput ,traceback, dic
from dic import word_idf 
from __init__ import * 

def dskadd(idxname, did, dsk_or_essay, did_source):
	''' (sntid, did, snt, ... ) , 2023.5.9 '''
	import gecdsk 
	dsk = gecdsk.parse({"essay":dsk_or_essay}) if isinstance(dsk_or_essay, str) else dsk_or_essay
	actions = []
	info = dsk['info'] 
	rid = did_source.get('rid',0)
	uid = did_source.get('uid',0)

	snts = [ mkf['meta']['snt'].strip() for mkf in dsk['snt'] ] #esindex(idxname, f"{did}:snts", {"id": f"{did}:snts", 'did': did, 'type':'snts', 'rid':rid, 'uid':uid, 'snts': snts, 'sntnum':len(snts) })
	did_source.update({'snts': snts, 'sntnum':len(snts) })
	dims = dsk['doc']		#esindex(idxname, f"{did}:dims", {"id": f"{did}:dims", 'did': did, 'type':'dims', 'rid':rid, 'uid':uid, 'dims': json.dumps(dims),"awl":dims["awl"], "ttr1":dims["ttr1"], "word_diff_avg":dims["word_diff_avg"], "ast":dims["ast"], "cl_ratio":dims["cl_ratio"], 	"doc_tc":dims["doc_tc"], "para_num":dims["para_num"], "spell_correct_ratio":dims["spell_correct_ratio"], "grammar_correct_ri":dims["grammar_correct_ri"],  })
	did_source.update({'dims': json.dumps(dims),"awl":dims["awl"], "ttr1":dims["ttr1"], "word_diff_avg":dims["word_diff_avg"], "ast":dims["ast"], "cl_ratio":dims["cl_ratio"], 	"doc_tc":dims["doc_tc"], "para_num":dims["para_num"], "spell_correct_ratio":dims["spell_correct_ratio"], "grammar_correct_ri":dims["grammar_correct_ri"],  })
	
	for i,mkf in enumerate(dsk['snt']): 
		snt = mkf['meta']['snt'].strip() 	
		sid = f"doc-{did}:snt-{i}" 	#esindex(idxname, sid, {"did": did,'sntid': sid, 'type':'snt', 'snt': snt, 'rid': rid, 'uid': uid, 'tc': mkf['meta'].get('tc',0)} )
		for k, item in mkf['feedback'].items():
			cate = item.get('cate','')
			if cate.startswith("e_") or cate.startswith("w_"):
				actions.append( {'_op_type':'index', '_index':idxname, '_id': f"{sid}:{k}", '_source': {"did": did, 'sntid': sid, 'rid': rid, 'uid': uid, 'type':'sntfd', 'kp': item['kp'], 'cate': cate, 'short_msg':item.get('short_msg',''), 'sent':snt} } )
	return actions

def run(infile, index:str=None, model:str="en_core_web_lg", debug:bool=False, postag:bool=False, reset:bool=True, batch:int=100000):
	''' (dsk, info, snts_spacy) in the jsonl, essays.dis-jsonl.gz, 2023.5.2 '''
	if index is None : index = infile.split('.')[0] 
	if reset: drop(index)
	check(index) 
	nlp = spacy.load(model)
	word_level = dic.word_level()  
	print ( 'started:', infile, index, batch, flush=True)

	start = time.time()
	actions = []
	for did, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
		try:
			arr = json.loads(line.strip()) # dis
			info, dsk, snts = arr['info'], arr.get('dsk',''), arr.get('snts',[])  # spacy
			if debug: print (f"[index-dis] {infile}:\t", did, round(time.time() - start, 2), flush=True) 

			info.update({'type': 'doc' ,'did': did})
			if dsk: actions.extend( dskadd(index, did, dsk, info) )  # add dsk 
			actions.append( {'_op_type':'index', '_index':index, '_id': did, '_source': info } ) 
		
			for j, sntjson in enumerate( snts ): 
				doc = spacy.tokens.Doc(nlp.vocab).from_json( sntjson )
				sntid = f"doc-{did}:snt-{j}"
				source = skenp(doc)
				source.update({"did":did, "sntid":sntid, "type":"snt", "tc": len(doc),"snt":doc.text.strip()}) 
				if 'rid' in info: source.update({'rid': info.get('rid',0)})
				if 'uid' in info: source.update({'uid': info.get('uid',0)})
				actions.append( {'_op_type':'index', '_index':index, '_id': sntid, '_source': source } )

				for t in doc:
					ar = {"did": did, 'sntid': sntid, 'i': t.i, 'type':'tok', 'rid': info.get('rid',0), 'uid': info.get('uid',0),'lex': t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, 'govlem': t.head.lemma_, 'govpos': t.head.pos_ }
					idf = word_idf.word_idf.get(t.text.lower(), 0)
					if idf : ar.update({"idf":idf})
					level = word_level.get(t.text.lower(), '') 
					if level: ar.update({"level":level})
					actions.append( {'_op_type':'index', '_index':index, '_id': f"{sntid}:tok-{t.i}", '_source': ar } )

			if len(actions) >= batch: 
				helpers.bulk(client=requests.es,actions=actions, raise_on_error=False)
				print (f"[index-dis] {infile}:\t No:{did} ",round(time.time() - start, 2), actions[-1], flush=True) 
				actions = []
	
		except Exception as e:
			print("ex:", e)	
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
	
	if actions : helpers.bulk(client=requests.es,actions=actions, raise_on_error=False)
	print(f"indexing finished: {index}, \t| using: ", time.time() - start) 

if __name__ == '__main__': 	#run('testdoc', debug=True)
	fire.Fire(run)