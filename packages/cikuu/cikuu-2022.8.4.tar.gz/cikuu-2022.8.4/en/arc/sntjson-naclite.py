# 2023.2.3 , cp from c4matcher.py | VBN -> past participle -> e | t -> to, b -> be , g -> VBG, c-> Clause , d-> ADV
import json, traceback,sys, time,  fileinput, os, en,sqlite3, fire,pathlib, spacy
from collections import Counter,defaultdict
from dic.lex_lemma import lex_lemma
from dic.wordlist import wordlist
has_zh  = lambda s : any([c for c in s if ord(c) > 255])
span_NP = lambda sp: " ".join([ "_NP" if t.ent_type_ == 'NP' else t.tag_ if t.tag_ in ('VBN') else t.lemma_ for t in sp])
_in		= lambda pair:	  fire.conn.execute(f"INSERT INTO nac(name, attr,count) VALUES(?,?,?) ON CONFLICT(name, attr) DO UPDATE SET count = count + 1", (pair[0].strip(), pair[1].strip(), 1) ) if not has_zh(pair[0]) else None
add		= lambda *names: [ _in(name.split("|")[0:2]) for name in names if  not '\t' in name and len(name) < 100 ]
insert	= lambda name, attr:  _in( [name, attr] ) 

def DepMatcher(rules:dict = {"advmod-dobj":[ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}}, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "subject", "RIGHT_ATTRS": {"DEP": "advmod"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "object","RIGHT_ATTRS": {"DEP": "dobj"}  }],} ):
	'''  [(spacy.nlp.vocab[name].text, ar) for name, ar in matcher(doc)]  #[('svo', [1, 0, 2])]'''
	from spacy.matcher import DependencyMatcher
	matcher = DependencyMatcher(spacy.nlp.vocab)
	[matcher.add(name, [pattern]) for name, pattern in rules.items() ]
	return matcher 

def dep(doc):
	if not hasattr(dep, 'matcher'): 
		dep.matcher = DepMatcher({
		"dobj-advmod":[ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "n","RIGHT_ATTRS": {"DEP": "dobj"}  }, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "adv", "RIGHT_ATTRS": {"DEP": "advmod"}}], # the last one , is the ADV 
		"dobj-amod":  [ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "n","RIGHT_ATTRS": {"DEP": "dobj"}  }, {"LEFT_ID": "n", "REL_OP": ">", "RIGHT_ID": "a", "RIGHT_ATTRS": {"DEP": "amod"}}], # 1,4,3  the last one is the adj 
		"nba":[ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"LEMMA": "be"}}, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "subject", "RIGHT_ATTRS": {"DEP": "nsubj"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "object","RIGHT_ATTRS": {"DEP": "acomp"}}],  # fate is good
		"nbn":[ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"LEMMA": "be"}}, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "subject", "RIGHT_ATTRS": {"DEP": "nsubj"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "object","RIGHT_ATTRS": {"DEP": "attr"}}],  # dream is film
		})
		dep.func = {
		"dobj-advmod":  lambda doc, i, j, k, tag: insert( ":".join( [doc[i].lemma_, doc[i].pos_, doc[j].dep_, doc[j].pos_, doc[j].lemma_, doc[k].dep_, doc[k].pos_]) , doc[k].lemma_ ) , 
		"dobj-amod":	dep.func['dobj-advmod'],  #drink:VERB:dobj:NOUN:water:amod:ADJ safe
		"nba":			lambda doc, i, j, k, tag :  add(f"{doc[j].lemma_}:{doc[i].pos_}:{tag}:{doc[k].pos_}|{doc[k].lemma_}", f"{doc[k].lemma_}:{doc[k].pos_}:{tag}:{doc[j].pos_}|{doc[j].lemma_}") ,
		"nbn":			dep.func['nba'], 
		}
	for name, ar in dep.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			i,j,k = ar[0:3] 
			dep.func[tag](doc, i,j,k, tag) 
		except Exception as e:
			print ("dep ex:", e, name, ar) 

def XP(doc): 
	if not hasattr(XP, 'matcher'): 
		XP.matcher = en.phrase_matcher({
		"Vend":[[{"POS": {"IN": ["AUX","VERB"]}},{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": {"IN": ["ADJ","VERB"]}, "OP": "*"},{"POS": {"IN": ["PART","ADP","TO"]}, "OP": "*"},{"POS": 'VERB'}]], # could hardly wait to meet
		"VP":  [[{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ"]}, "OP": "*"},{"POS": 'NOUN'}, {"POS": {"IN": ["ADP","TO"]}, "OP": "*"}], [{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ","TO","PART"]}, "OP": "*"},{"POS": 'VERB'}]], # wait to meet
		"PP":  [[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]],    
		"AP":  [[{"POS": {"IN": ["ADV"]}, "OP": "+"}, {"POS": 'ADJ'}]],  
		})
		XP.func = { # could hardly wait to meet
		"Vend": lambda doc, start, end, tag: add(doc[end-1].lemma_ + f":VERB:prmods|" + doc[start].lemma_ + " " + doc[start+1:end].text) , 
		"VP": lambda doc, start, end, tag: add(doc[start].lemma_ + f":{doc[start].pos_}:VP|" + doc[start].lemma_ + " " + doc[start+1:end].text) , 
		"PP": lambda doc, start, end, tag: add(doc[end-1].lemma_ + f":{doc[end-1].pos_}:PP|" + doc[start:end].text) ,
		"AP": lambda doc, start, end, tag: add(doc[end-1].lemma_ + f":{doc[end-1].pos_}:AP|" + doc[start:end].text) ,
		}
	for name, start, end in VP.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			XP.func[tag](doc, start, end, tag ) 
		except Exception as e:
			print ("postag ex:", e, name, start, end) 

def postag(doc): 
	if not hasattr(postag, 'matcher'): 
		postag.matcher = en.phrase_matcher({
		"vpn": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} , {"TAG":"NN"}]],  # be in force 
		"vnp": [[{"POS":"VERB"}, {"TAG":"NN"}, {"POS":"ADP"} ]],  # make use of, lay emphasis on
		"vp": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} ]],  # abide by | distinguish from
		"vpp": [[{"POS":"VERB"}, {"POS":"ADP"}, {"POS":"ADP"} ]], # live up to
		"vpg": [[{"POS":"VERB"}, {"POS":"ADP"}, {"TAG":"VBG","DEP":"pcomp"} ]], # insisted on going
		"pn": [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}]],  # by force
		"pnp": [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}, {"POS":"ADP", "DEP":"prep"}]],  # on account of
		"bapv": [[{"LEMMA":"be"} , {"TAG":{"IN": ["JJ"]}}, {"LEMMA":"to"}, {"POS":"VERB"}]],  # 
		"bepv": [[{"LEMMA":"be"} , {"TAG":{"IN": ["VBN"]}}, {"LEMMA":"to"}, {"POS":"VERB"}]],  # be forced to go / ? bepv? 
		"bap": [[{"LEMMA":"be"} , {"TAG":{"IN": ["JJ"]}}, {"POS":"ADP"}]], #be ignorant of
		"bvp": [[{"LEMMA":"be"} , {"TAG":{"IN": ["VBN"]}}, {"POS":"ADP"}]],  # be forced to
		"vop": [[{"POS":"VERB"} , {"TEXT": {"REGEX": "[a-z]+self$"}}, {"POS":"ADP"}]], #throw oneself into
		"vtv": [[{"POS":"VERB"}, {"LEMMA":"to"}, {"POS":"VERB", "DEP":"xcomp"} ]], 
		"vg": [[{"POS":"VERB"},  {"TAG":"VBG", "DEP":"xcomp"} ]], 
		"vdpg": [[{"POS":"VERB"},  {"POS":"ADV"} ,  {"POS":"ADP"} ,  {"TAG":"VBG"} ]],  # look forward to seeing
		})
		postag.func = {
		"vpn": lambda doc, start, end, tag: add(f"{doc[start].lemma_}:VERB:vpn|{doc[start].lemma_} {doc[start+1:end].text}", f"{doc[end-1].lemma_}:NOUN:vpn|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"vnp": lambda doc, start, end, tag: add(f"{doc[start].lemma_}:VERB:vnp|{doc[start].lemma_} {doc[start+1:end].text}", f"{doc[start+1].lemma_}:NOUN:vnp|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"vp":  lambda doc, start, end, tag: add(f"{doc[start].lemma_}:VERB:vp|{doc[start].lemma_} {doc[start+1].text}") ,
		"vpp": lambda doc, start, end, tag: add(f"{doc[start].lemma_}:VERB:vpp|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"vpg": lambda doc, start, end, tag: add(f"{doc[start].lemma_}:VERB:vpg|{doc[start].lemma_} {doc[start+1].text}") ,
		"pn":  lambda doc, start, end, tag: add(f"{doc[start+1].lemma_}:NOUN:pn|{doc[start:end].text}") ,
		"pnp": lambda doc, start, end, tag: add(f"{doc[start+1].lemma_}:NOUN:pnp|{doc[start:end].text}") ,
		"bapv": lambda doc, start, end,tag: add(f"{doc[start+1].lemma_}:ADJ:bapv|{doc[start].lemma_} {doc[start+1:end-1].text} _VERB") ,
		"bepv": lambda doc, start, end,tag: add(f"{doc[start+1].lemma_}:VERB:bepv|{doc[start].lemma_} {doc[start+1:end-1].text} _VERB") ,
		"bap": lambda doc, start, end, tag: add(f"{doc[start+1].lemma_}:ADJ:bap|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"bep": lambda doc, start, end, tag: add(f"{doc[start+1].lemma_}:VERB:bep|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"vop": lambda doc, start, end, tag: add(f"{doc[start].lemma_}:VERB:vop|{doc[start].lemma_} oneself {doc[end-1].text}") ,
		"vtv": lambda doc, start, end, tag: add(f"{doc[start].lemma_}:VERB:vtv|{doc[start].lemma_} {doc[start+1:end-1].text} _VERB") ,
		"vg": lambda doc, start, end, tag:	add(f"{doc[start].lemma_}:VERB:vg|{doc[start].lemma_} _VBG") ,
		"vdpg": lambda doc, start, end,tag: add(f"{doc[start].lemma_}:VERB:vdpg|{doc[start].lemma_} {doc[start+1:end-1].text} _VBG") ,
		}
	for name, start, end in postag.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			postag.func[tag](doc, start, end, tag ) 
		except Exception as e:
			print ("postag ex:", e, name, start, end) 

def skenp(doc): 
	if not hasattr(skenp, 'matcher'): skenp.matcher = en.phrase_matcher({
	"vnpn": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"ENT_TYPE":"NP"}, {"POS":{"IN": ["ADP"]}}, {"ENT_TYPE":"NP"}]],  # remind _NP of _NP , bring _NP to life
	"vpnpn": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":{"IN": ["ADP"]}}, {"ENT_TYPE":"NP"}, {"POS":{"IN": ["ADP"]}}, {"ENT_TYPE":"NP"}]],  # vary from _NP to _NP 
	"vppn": [[{"POS":"VERB"}, {"POS":"ADP"}, {"POS":"ADP"}, {"ENT_TYPE":"NP"} ]],  # live up to _NP
	"vdpn": [[{"POS":"VERB"}, {"POS":"ADV"}, {"POS":"ADP"}, {"ENT_TYPE":"NP"} ]],  # look back on _NP 
	"vn": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"} ]], 
	"vnn": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"}, {"ENT_TYPE":"NP"} ]], 
	"vna": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"}, {"POS":"ADJ"} ]], 
	"vne": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"}, {"TAG":"VBN"} ]], # leave it kept 
	"vntb": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"}, {"LEMMA":"to"} , {"LEMMA":"be"}]], # consider _NP _NP | _NP _ADJ | _NP to be 
	"vntv": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"}, {"LEMMA":"to"} , {"POS":"VERB"}]],
	"vntbn": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"}, {"LEMMA":"to"} , {"LEMMA":"be"}, {"ENT_TYPE":"NP"}]], 
	"vntba": [[{"POS":"VERB"}, {"ENT_TYPE":"NP"}, {"LEMMA":"to"} , {"LEMMA":"be"}, {"POS":"ADJ"}]],
	"vdpn": [[{"POS":"VERB"},  {"POS":"ADV"} ,  {"POS":"ADP"} ,  {"ENT_TYPE":"NP"} ]],  # look forward to _NP | a bright future 
	})
	for name, start, end in skenp.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			if tag.startswith("v"): 
				lem = doc[start].lemma_
				add( f"{lem}:VERB:{tag}|" + span_NP(doc[start:end]), f"{lem}:VERB|{tag}", f"*:VERB|{tag}", f"*|{tag}" )
		except Exception as e:
			print ("skenp ex:", e, name, start, end) 

def first_scan(infile):
	ssi = defaultdict(Counter) 
	add = lambda *names: [ssi[ name.split('|')[0] ].update({ name.split('|')[-1] : 1}) for name in names if  not '\t' in name and len(name) <= 80 ]
	start = time.time()
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			add( "*|SNTNUM")  
			arr = json.loads(line.strip()) 
			snt = arr.get('text','')
			for tok in arr.get('tokens',[]):
				add( "*|LEXSUM")
				lem,pos,tag,lex = tok['lemma'], tok['pos'], tok['tag'], snt[ tok['start']: tok['end'] ]
				if pos not in ('PROPN','X', 'PUNCT') : 
					add("LEM|{lem}", "LEX|{lex}", f"{lem}:LEX|{lex}")
				if pos in ('VERB','NOUN','ADJ','ADV'):
					add(f"{pos}|{lem}", f"*|{pos}", f"{lem}|{pos}", f"{lem}:{pos}|{tag}", f"*:{pos}|{tag}")
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
	print(f"{infile} first-scan is finished, \t| using: ", time.time() - start) 
	return ssi 

def run(infile, outfile:str=None, batch:int=10000):
	''' c4-train.00604-of-01024.docjsonlg.3.4.1.gz -> c4-train.00604-of-01024.chksi  '''
	if outfile is None: outfile = infile.strip('.').split('.docjson' if '.docjson' in infile else '.')[0].strip('/') + ".naclite" 
	if pathlib.Path(f"{outfile}").exists(): os.remove(outfile)
	print ("started:", infile ,  ' -> ',  outfile, flush=True)

	fire.conn = sqlite3.connect(outfile, check_same_thread=False) 
	fire.conn.execute("create table nac( name varchar(64) not null , attr varchar(64) not null, count int not null default 0, per float not null default 0, primary key(name, attr) ) without rowid") 
	fire.conn.execute('PRAGMA synchronous=OFF')
	fire.conn.execute('PRAGMA case_sensitive_like = 1')
	fire.conn.commit()

	start = time.time()
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			arr = json.loads(line.strip()) 
			doc = spacy.from_json(arr) 
			[ insert(f"{t.head.lemma_}:{t.head.pos_}", "vc") for t in doc if t.dep_ == 'ccomp' and t.head.pos_ == 'VERB' ]
			[ add(f"{t.lemma_}:{t.pos_}:nbe:VBN|{t.head.text.lower()}", f"{t.head.text.lower()}:VBN:nbe:{t.pos_}|{t.lemma_}", ) for t in doc if t.dep_ == 'nsubjpass' and t.head.tag_ == 'VBN' ] # the fate is sealed
			[ insert(f"{t.head.lemma_}:{t.head.pos_}", "advcl") for t in doc if t.dep_ == 'advcl' and t.head.pos_ == 'VERB' ]
			#[ ( insert(t.lemma_, t.pos_), insert(f"{t.lemma_}:{t.pos_}", t.tag_))  for t in doc if t.pos_ in ('VERB','NOUN','ADJ','ADV') ]

			dep(doc) 
			postag(doc) # submit(doc, matcher) 
			VP(doc) 
			[add(f"{sp.root.lemma_.lower()}:{sp.root.pos_}:NP|{sp.text.lower()}", f"{sp.root.lemma_.lower()}:{sp.root.pos_}|NP", f"*:{sp.root.pos_}|NP", f"*|NP",) for sp in doc.noun_chunks] #book:NOUN:np:a book
			add( "*|sntnum")  
			[add( f"{t.lemma_}|{t.pos_}", f"{t.lemma_}:LEX|{t.text.lower()}", f"LEM|{t.lemma_.lower()}", f"LEX|{t.text.lower()}", f"{t.pos_}|{t.lemma_.lower()}"
				,f"{t.lemma_.lower()}:{t.pos_}|{t.tag_}",f"*:{t.pos_}|{t.tag_}") for t in doc if not t.pos_ in ('PROPN','X', 'PUNCT') and t.is_alpha  and t.lemma_.lower() in wordlist]
			for t in doc:
				if t.pos_ in ("VERB","NOUN","ADJ","ADV") : add( f"{t.tag_}|{t.text.lower()}")  # VBD :  made , added 2022.12.10
				add( "*|LEX","*|LEM", f"*|{t.pos_}", f"*|{t.tag_}",f"*|{t.dep_}",f"*|~{t.dep_}") #,f"{t.pos_}|{t.dep_}" ,f"{t.pos_}|{t.tag_}"
				if t.pos_ not in ("PROPN","PUNCT","SPACE") and t.is_alpha and t.head.is_alpha and t.lemma_.lower() in wordlist and t.head.lemma_.lower() in wordlist: #*:VERB:~punct:VERB:wink
					add(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}|{t.lemma_}", f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}|{t.pos_}",f"{t.head.lemma_}:{t.head.pos_}|{t.dep_}", f"*:{t.head.pos_}|{t.dep_}", f"*:{t.head.pos_}:{t.dep_}:{t.pos_}|{t.head.lemma_}")
					if t.dep_ not in ('ROOT'): 	add(f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}|{t.head.lemma_}", f"{t.lemma_}:{t.pos_}:~{t.dep_}|{t.head.pos_}", f"{t.lemma_}:{t.pos_}|~{t.dep_}", f"*:{t.pos_}|~{t.dep_}", f"*:{t.pos_}:~{t.dep_}:{t.head.pos_}|{t.lemma_}")

			en.merge_np(doc) 
			skenp(doc) # submit(doc, skenp) 
			if (sid+1) % batch == 0 : 
				print (f"[{infile} -> {outfile}] sid = {sid}, \t| ", round(time.time() - start,1), flush=True)
				fire.conn.commit()
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)

	fire.conn.commit()
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

if __name__	== '__main__':
	fire.Fire(run)

'''
agree:VERB:bvpv|be agreed to _VERB|let => 1

sqlite> create table if not exists si( s varchar(64) not null primary key, i int not null default 0) without rowid;
sqlite> insert into si select name, sum(count) from nac group by name; 

			chk = doc[start].lemma_ + " " + doc[start+1:end].text if tag != 'vop' else doc[start].lemma_  + " oneself " + doc[start+2].text # devote oneself to
			for i,c in enumerate(tag): 
				if c in ('n','v','a'):  
					if c == 'v' and tag == 'vtv' and i > 0: continue # skip the last 'v' of 'vtv' 
					lem = doc[start+i].lemma_ if c =='v' and i==0 else doc[start+i].text.lower()
					if tag.startswith( ('bvp','bap') ): lem = lex_lemma.get(doc[start+i].text.lower(),doc[start+i].text.lower()) # be forced to , forced => force 
					add( f"{lem}:{doc[start+i].pos_}:{tag}|{chk}", f"{lem}:{doc[start+i].pos_}|{tag}", f"*:{doc[start+i].pos_}|{tag}", f"*|{tag}" )
					if tag.endswith("v"): add( f"{lem}:{doc[start+i].pos_}:{tag}|" + doc[start].lemma_ + " " + doc[start+1:end-1].text + " _VERB") # be forced to _VERB

'''