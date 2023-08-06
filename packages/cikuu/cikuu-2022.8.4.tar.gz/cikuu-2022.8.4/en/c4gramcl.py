# 2023.2.8 
# 2023.1.28 , cp from c4gram.cl   # 2022.10.22
import json, traceback,sys, time,  fileinput, os,en, sqlite3,re,itertools
from collections import Counter
from pathlib import Path
has_zh	= lambda s : any([c for c in s if ord(c) > 255])
invalid	= lambda s: len(s) > 64 or '(' in s or '$' in s or '#' in s or ')' in s or '~' in s or '*' in s or '%' in s or '@' in s or '^' in s or '\\' in s or '+' in s or '=' in s or '{' in s or '}' in s or '[' in s or ']' in s or '/' in s  or '`' in s or '&' in s or '|' in s
# The quick fox who looked fine is ok.  | who -> _NP ,  => '_NP who looked' failed in the gram 
# <s> _NP jumped over _NP . 
skenp = lambda doc: ["<s>"] + ["_CL" if t.ent_id_.startswith("_CL") else "_NP" if t.ent_type_ == 'NP' else f"_{t.pos_}" if t.pos_ in ('PROPN','NUM','X','SPACE') else t.text for t in doc]

def tok ( t ): 
	if t.pos_ in ('PROPN','NUM','CD','X','SPACE'): return f"_{t.pos_}"
	if t.ent_type_ == 'CL': return '_CL'
	if t.ent_type_ == 'NP': return '_NP' if ' ' in t.text else f"{t.text.lower()}/_NP"  # who/_NP 
	if t.lemma_ == 'be' : return f"{t.text.lower()}/_be"
	if t.pos_ == 'VERB' : return f"{t.text.lower()}/_{t.lemma_}/_{t.tag_ if t.tag_ in ('VBG','VBN') else t.pos_}" 
	return t.text.lower()
doctoks		= lambda doc: " ".join(['<s>'] + [ tok(t) for t in doc ])
toks_product= lambda s='one two/x three/y': [ar for ar in itertools.product( * [a.strip().split('/') for a in s.strip().split(' ')]) ]  #[('one', 'two', 'three'),  ('one', 'two', 'y'), ('one', 'x', 'three'), ('one', 'x', 'y')]
#toks_product= lambda toks: [ar for ar in itertools.product( * [a.strip().split('/') for a in toks]) ]  #[('one', 'two', 'three'),  ('one', 'two', 'y'), ('one', 'x', 'three'), ('one', 'x', 'y')]

def count(toks, ts, n): # ts: set 
	tlen =  len(toks)
	for i in range( tlen ): 
		for j in range(n): 
			if i+j <= tlen: 
				ts.add( " ".join(toks[i:i+j]) )

cl_root = lambda t: t.dep_ != 'ROOT' and ( (t.pos_ == 'VERB' and t.tag_ != 'VBN')  or (t.pos_ == 'AUX' and t.lemma_ == 'be') )
def mark_cl(doc):
    for t in doc: 
        if cl_root(t) : t.ent_id_ = 'cl_root'
leave_cl = lambda t: cl_root(t) and len([tr for tr in t.subtree if tr.ent_id_ == 'cl_root']) == 1
def merge_leave_cl(doc): #doc = spacy.nlp("While I was thrilled that it was ok, I worried that I would fail.")
	mark_cl(doc)
	with doc.retokenize() as retokenizer:
		for v in [t for t in doc if leave_cl(t) ] : # non-root
			try:
				children = list(v.subtree)
				start = children[0].i  	
				end = children[-1].i 
				attrs = {"pos": v.pos, "tag": v.tag, "dep": v.dep, "lemma":v.lemma, "ent_type": "CL"} # S.advcl ,  S.conj | or keep _advcl ?
				if v.dep_ not in ('xcomp') and doc[start].lemma_ not in ('to') and doc[start].tag_ not in ('TO'): # skip to-clause  | He made the choice to give all his money away .
					retokenizer.merge(doc[start : end+1], attrs=attrs)
			except Exception as e:
				print ( "merge_leave_cl ex:", e, v )
	return doc 

def process(doc, n:int=7):
	snts = set() 
	[snts.add(tlist) for tlist in toks_product( doctoks(doc))]
	en.merge_np(doc) 
	[snts.add(tlist) for tlist in toks_product( doctoks(doc))]
	merge_leave_cl(doc)
	[snts.add(tlist) for tlist in toks_product( doctoks(doc))]	#[count( tlist, ts, n)  for tlist in toks_product( doctoks(doc))]

	ts = set()
	[count( tlist, ts, n)  for tlist in snts]
	ts.add(" ".join(skenp(doc))) # no gram len limit
	return ts 

def run(infile, outfile:str=None,  n:int=7, batch:int=3000, remove:bool=False):
	''' c4-train.00604-of-01024.docjsonlg.3.4.1.gz -> c4-train.sqlsi | 2023.2.8 '''
	if outfile is None: outfile = infile.strip('.').split('.docjson' if '.docjson' in infile else '.')[0].strip('/') + ".gramsi" 
	if Path(f"{outfile}").exists(): return f"{outfile} exists"
	print ("started:", infile ,  ' -> ',  outfile, batch, flush=True)

	conn  =	sqlite3.connect(outfile, check_same_thread=False) 
	conn.execute("create table if not exists si( s varchar(64) not null primary key, i int not null default 0) without rowid")
	conn.execute('PRAGMA synchronous=OFF')
	conn.execute('PRAGMA case_sensitive_like = 1')
	conn.commit()
	start = time.time()
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			arr = json.loads(line.strip()) 
			tdoc = spacy.from_json(arr) 
			for sp in tdoc.sents:
				doc = sp.as_doc()
				ts = process(doc) 
				for s in ts:  
					if not s or has_zh(s) or invalid(s): continue
					conn.execute(f"INSERT INTO si(s,i) VALUES(?,?) ON CONFLICT(s) DO UPDATE SET i = i + 1", (s,1))
			if (sid+1) % batch == 0 : 
				spacy.nlp	= spacy.load('en_core_web_lg')
				print (f"[{infile} -> {outfile}] sid = {sid}, \t| ", round(time.time() - start,1), flush=True)
				conn.commit()
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
	conn.commit()
	if remove:  os.remove(infile) # delete , added 2022.10.22
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

if __name__	== '__main__':
	import fire, platform
	print ( process(spacy.nlp("People who looked fine is ok."))) if platform.system() in ('Windows') else  fire.Fire(run)

'''
_NP who looked 

_VERB in force 
_be in force
by force 
_come into force 
_be forced to _VERB 

#doctoks = lambda doc: ['<s>'] + [ f"_{t.pos_}" if t.pos_ in ('PROPN','NUM','CD','X','SPACE') else f"_{t.ent_type_}" if t.ent_type_ in ('NP','CL') else t.text.lower()  for t in doc ] #  and ' ' in t.text 
#lemtoks = lambda doc: ['<s>'] + [ f"_{t.pos_}" if t.pos_ in ('PROPN','NUM','CD','X','SPACE') else f"_{t.ent_type_}" if t.ent_type_ in ('NP','CL') else f"_{t.lemma_}" if t.pos_ in ("VERB") else t.text.lower()  for t in doc ]
#postoks = lambda doc: ['<s>'] + [ f"_{t.pos_}" if t.pos_ in ('PROPN','NUM','CD','X','SPACE', 'VERB') else f"_{t.lemma_}" if t.lemma_ in ("be") else f"_{t.ent_type_}" if t.ent_type_ in ('NP','CL') else t.text.lower()  for t in doc ]
'''