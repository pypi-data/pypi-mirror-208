# 2023.2.2
import json, traceback,sys, time,  fileinput, os, en,sqlite3, spacy
from pathlib import Path
from spacy.matcher import Matcher

matcher = Matcher(spacy.nlp.vocab) # remind _NP of NP 
matcher.add("vpn", [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} , {"TAG":"NN"}]], greedy ='LONGEST') # be in force 
matcher.add("vnp", [[{"POS":"VERB"}, {"TAG":"NN"}, {"POS":"ADP"} ]], greedy ='LONGEST') # make use of, lay emphasis on
matcher.add("vp", [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} ]], greedy ='LONGEST') # abide by | distinguish from
matcher.add("vpp", [[{"POS":"VERB"}, {"POS":"ADP"}, {"POS":"ADP"} ]], greedy ='LONGEST') # live up to
matcher.add("pn", [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}]], greedy ='LONGEST') # by force
matcher.add("pnp", [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}, {"POS":"ADP", "DEP":"prep"}]], greedy ='LONGEST') # on account of
matcher.add("bapv", [[{"LEMMA":"be"} , {"TAG":{"IN": ["ADJ","VBN"]}}, {"LEMMA":"to"}, {"POS":"VERB"}]], greedy ='LONGEST') # be forced to go
matcher.add("bap", [[{"LEMMA":"be"} , {"TAG":{"IN": ["JJ"]}}, {"POS":"ADP"}]], greedy ='LONGEST')#be ignorant of
matcher.add("bvp", [[{"LEMMA":"be"} , {"TAG":{"IN": ["VBN"]}}, {"POS":"ADP"}]], greedy ='LONGEST') # be forced to
matcher.add("vop", [[{"POS":"VERB"} , {"TEXT": {"REGEX": "[a-z]+self$"}}, {"POS":"ADP"}]], greedy ='LONGEST')#throw oneself into

skenp = Matcher(spacy.nlp.vocab)
skenp.add("vnpn", [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"ENT_TYPE":"NP"}, {"POS":{"IN": ["ADP"]}}, {"ENT_TYPE":"NP"}]], greedy ='LONGEST') # remind _NP of _NP , bring _NP to life
skenp.add("vppn", [[{"POS":"VERB"}, {"POS":"ADP"}, {"POS":"ADP"}, {"ENT_TYPE":"NP"} ]], greedy ='LONGEST') # live up to _NP

def merge_np(doc):
	with doc.retokenize() as retokenizer:
		for np in doc.noun_chunks:
			attrs = {"tag": np.root.tag, "dep": np.root.dep, "ent_type": "NP", "lemma":doc[np.end-1].lemma} # , "lemma":doc[np.end-1].lemma | added 2022.7.26
			retokenizer.merge(np, attrs=attrs) 
	return doc

def run(infile, outfile:str=None, batch:int=10000):
	''' c4-train.00604-of-01024.docjsonlg.3.4.1.gz -> c4-train.00604-of-01024.chksi  '''
	if outfile is None: outfile = infile.strip('.').split('.docjson' if '.docjson' in infile else '.')[0].strip('/') + ".chksi" 
	if Path(f"{outfile}").exists(): os.remove(outfile)
	print ("started:", infile ,  ' -> ',  outfile, flush=True)

	conn  =	sqlite3.connect(outfile, check_same_thread=False) 
	conn.execute("create table if not exists si( s varchar(64) not null primary key, i int not null default 0) without rowid")
	conn.execute('PRAGMA synchronous=OFF')
	conn.execute('PRAGMA case_sensitive_like = 1')
	conn.commit()

	def add( doc, matcher):
		for name, start, end in matcher(doc):
			t = spacy.nlp.vocab[name].text + ":" + doc[start].lemma_ + " " + doc[start+1:end].text
			conn.execute(f"INSERT INTO si(s,i) VALUES(?,?) ON CONFLICT(s) DO UPDATE SET i = i + 1", (t,1))

	start = time.time()
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			arr = json.loads(line.strip()) 
			doc = spacy.from_json(arr) 
			add(doc, matcher) 
			merge_np(doc) 
			add(doc, skenp) 
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