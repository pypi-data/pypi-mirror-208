# 2022.10.3
import json, traceback,sys, time,  fileinput, os, en,sqlite3, spacy
from collections import Counter
from pathlib import Path
from spacy.matcher import Matcher,DependencyMatcher

def merge_v(doc): # 2023.1.22
	if not hasattr(merge_v, 'matcher'):
		merge_v.matcher = Matcher(spacy.nlp.vocab)
		merge_v.matcher.add("vprt", [[{"POS":"VERB"}, {"POS":"ADP", "DEP":"prt"}]], greedy ='LONGEST')
		merge_v.matcher.add("be-pn", [[{"LEMMA":"be"},{"TAG":"IN","POS":"ADP"},{"TAG":"NN"}]], greedy ='LONGEST') # be in construction
		merge_v.matcher.add("be-acomp", [[{"LEMMA":"be"},{"DEP":"acomp","POS":"ADJ"}]], greedy ='LONGEST') #"POS":"AUX",
		merge_v.matcher.add("be-auxpass", [[{"LEMMA":"be","DEP":"auxpass"},{"TAG":"VBN","POS":"VERB"}]], greedy ='LONGEST')
	with doc.retokenize() as retokenizer:
		spans = [ doc[start:end] for name, start, end in merge_v.matcher(doc) ]
		filtered = spacy.util.filter_spans(spans)
		for sp in filtered:  # 
			try: 
				start = sp.start
				end = sp.end 
				attrs = {"pos": "VERB", "tag": doc[start].tag, "dep": doc[start].dep, 
					"lemma":"_".join([doc[i].lemma_ if i == start else doc[i].text for i in range(start,end)]), 
					"ent_type": "merged" }
				retokenizer.merge(doc[start : end], attrs=attrs)
			except Exception as e:
				print ( "merge_v ex:", e , start, end)
	return doc

trps = lambda doc :  [	f"{t.dep_}:{t.head.pos_}:{t.pos_}:{t.head.tag_}:{t.tag_}:{t.head.lemma_}:{t.lemma_}" for t in doc if t.lemma_.replace('-','').replace('_','').isalpha() and t.head.lemma_.replace('-','').replace('_','').isalpha() and  t.pos_ not in ('SP','PUNCT','PROPN') and t.tag_ not in ('NUM','CD') and not ':' in t.text ]
def run(infile, outfile:str=None, batch:int=10000):
	''' c4-train.00604-of-01024.docjsonlg.3.4.1.gz -> c4-train.00604-of-01024.trpsi | 2022.8.22 '''
	if outfile is None: outfile = infile.strip('.').split('.docjson')[0].strip('/') + ".trpsi" 
	if Path(f"{outfile}").exists(): return f"{outfile} exists"
	print ("started:", infile ,  ' -> ',  outfile, flush=True)

	conn  =	sqlite3.connect(outfile, check_same_thread=False) 
	conn.execute("create table if not exists si( s varchar(64) not null primary key, i int not null default 0) without rowid")
	conn.execute('PRAGMA synchronous=OFF')
	conn.execute('PRAGMA case_sensitive_like = 1')
	conn.commit()
	start = time.time()
	ts = set() 
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			arr = json.loads(line.strip()) 
			ts.clear()
			doc = spacy.from_json(arr) 
			for t in trps(doc): ts.add(t)
			doc = merge_v(doc)   
			for t in trps(doc): ts.add(t)
			for t in ts:
				conn.execute(f"INSERT INTO si(s,i) VALUES(?,?) ON CONFLICT(s) DO UPDATE SET i = i + 1", (t,1))
			if (sid+1) % batch == 0 : 
				print (f"[{infile} -> {outfile}] sid = {sid}, \t| ", round(time.time() - start,1), flush=True)
				conn.commit()
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
	conn.commit()
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

if __name__	== '__main__':
	import fire 
	fire.Fire(run)

def run0(infile):
	outfile = infile.split('.docjson')[0] + f".trp"
	if Path(f"{outfile}.gz").exists(): return f"{outfile} exists"
	start = time.time()
	si = Counter()
	print ("started:", infile ,  ' -> ',  outfile, flush=True)
	with open(outfile, 'w') as fw: 
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				arr = json.loads(line.strip()) 
				doc = spacy.from_json(arr) 
				doc = en.merge_prt(doc)   # added 2022.1.13,  turn_off the radio 
				for t in doc:
					if not t.lemma_.replace('-','').replace('_','').isalpha() or not t.head.lemma_.replace('-','').replace('_','').isalpha(): continue # added 2022.1.6 
					if t.pos_ not in ('SP','PUNCT','PROPN') and t.tag_ not in ('NUM','CD') and not ':' in t.text :
						trp = f"{t.dep_}:{t.head.pos_}:{t.pos_}:{t.head.tag_}:{t.tag_}:{t.head.lemma_}:{t.lemma_}"  
						fw.write(f"{trp}\n")
			except Exception as e:
				print ("ex:", e, sid, line) 
	os.system(f"gzip -f -9 {outfile}")
	print(f"{infile} is finished, \t| using: ", time.time() - start) 