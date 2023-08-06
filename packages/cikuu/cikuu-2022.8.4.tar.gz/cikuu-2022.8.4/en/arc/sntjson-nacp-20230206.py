# 2023.2.5 , cp from sntjson-naclite.py | VBN -> past participle -> e | t -> to, b -> be , g -> VBG, c-> Clause , d-> ADV
import json, traceback,sys, time,  fileinput, os, en, fire,pathlib, spacy, pymysql, platform
from spacy.tokens import DocBin,Doc,Token,SpanGroup
from collections import Counter,defaultdict
from dic.lex_lemma import lex_lemma
from dic.wordlist import wordlist
has_zh  = lambda s : any([c for c in s if ord(c) > 255])
span_NP = lambda sp: " ".join([ "_NP" if t.ent_type_ == 'NP' else t.lemma_ for t in sp]) #else f"_{t.tag_}" if t.tag_ in ('VBN')
add		= lambda *names: [fire.ssi[ name.split('|')[0] ].update({ name.split('|')[-1] : 1}) for name in names if  not '\t' in name and len(name) <= 80 ]
insert	= lambda name, attr:  add( f"{name}|{attr}") 
addone	= lambda *pairs: [ ( add(pair),  arr:=pair.split('|')[0].split(':'), insert(":".join(arr[0:-1]), arr[-1]), add(f"*|{arr[-1]}") )  for pair in pairs ]

def DepMatcher(rules:dict = {"advmod-dobj":[ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}}, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "subject", "RIGHT_ATTRS": {"DEP": "advmod"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "object","RIGHT_ATTRS": {"DEP": "dobj"}  }],} ):
	'''  [(spacy.nlp.vocab[name].text, ar) for name, ar in matcher(doc)]  #[('svo', [1, 0, 2])]'''
	from spacy.matcher import DependencyMatcher
	matcher = DependencyMatcher(spacy.nlp.vocab)
	[matcher.add(name, [pattern]) for name, pattern in rules.items() ]
	return matcher 

phrase_rules = {
	"Vend":[[{"POS": {"IN": ["AUX","VERB"]}},{"POS": {"IN": ["ADV"]}, "OP": "*"}, {"POS": {"IN": ["ADJ","VERB"]}, "OP": "*"},{"POS": {"IN": ["PART","ADP","TO"]}, "OP": "*"},{"POS": 'VERB'}]], # could hardly wait to meet
	"VP":  [[{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ"]}, "OP": "*"},{"POS": 'NOUN'}, {"POS": {"IN": ["ADP","TO"]}, "OP": "*"}], [{'POS': 'VERB'},{"POS": {"IN": ["DET","ADP","ADJ","TO","PART"]}, "OP": "*"},{"POS": 'VERB'}]], # wait to meet
	"PP":  [[{'POS': 'ADP'},{"POS": {"IN": ["DET","NUM","ADJ",'PUNCT','CONJ']}, "OP": "*"},{"POS": {"IN": ["NOUN","PART"]}, "OP": "+"}]],    
	"AP":  [[{"POS": {"IN": ["ADV"]}, "OP": "+"}, {"POS": 'ADJ'}]],  
	"vpn": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} , {"TAG":"NN"}]],  # come into force 
	"bpn": [[{"LEMMA":"be"}, {"POS":"ADP"} , {"TAG":"NN"}]],  # be in force => vpn 
	"vnp": [[{"POS":"VERB"}, {"TAG":"NN"}, {"POS":"ADP"} ]],  # make use of, lay emphasis on
	"vp": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} ]],  # abide by | distinguish from
	"vpp": [[{"POS":"VERB"}, {"POS":"ADP"}, {"POS":"ADP"} ]], # live up to
	"vpg": [[{"POS":"VERB"}, {"POS":"ADP"}, {"TAG":"VBG","DEP":"pcomp"} ]], # insisted on going
	"pn": [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}]],  # by force
	"pnp": [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}, {"POS":"ADP", "DEP":"prep"}]],  # on account of
	"bapv": [[{"LEMMA":"be"} , {"TAG":{"IN": ["JJ"]}}, {"LEMMA":"to"}, {"POS":"VERB"}]],  # 
	"bepv": [[{"LEMMA":"be"} , {"TAG":{"IN": ["VBN"]}}, {"LEMMA":"to"}, {"POS":"VERB"}]],  # be forced to go / ? bepv? 
	"bap": [[{"LEMMA":"be"} , {"TAG":{"IN": ["JJ"]}}, {"POS":"ADP"}]], #be ignorant of
	"bep": [[{"LEMMA":"be"} , {"TAG":{"IN": ["VBN"]}}, {"POS":"ADP"}]],  # be forced to
	"vop": [[{"POS":"VERB"} , {"TEXT": {"REGEX": "[a-z]+self$"}}, {"POS":"ADP"}]], #throw oneself into
	"vtv": [[{"POS":"VERB"}, {"LEMMA":"to"}, {"POS":"VERB", "DEP":"xcomp"} ]], 
	"vg": [[{"POS":"VERB"},  {"TAG":"VBG", "DEP":"xcomp"} ]], 
	"vdpg": [[{"POS":"VERB"},  {"POS":"ADV"} ,  {"POS":"ADP"} ,  {"TAG":"VBG"} ]],  # look forward to seeing
	}

def phrase_match(doc): 
	''' add matched new span by phrase rules, 2023.2.6 '''
	if not hasattr(phrase_match, 'matcher'):  	
		phrase_match.matcher = en.phrase_matcher(phrase_rules)
	for name, start, end in phrase_match.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			doc.spans[f"span[{start},{end}):{tag}"] = SpanGroup(doc, name=tag, spans=[ doc[start : end] ], attrs={}) #attrs = {"pos": v.pos_, "tag": v.tag_, "dep": v.dep_, "lemma":v.lemma_, "ent_type": "S." + v.dep_ } 
		except Exception as e:
			print ("phrase_match ex:", e, name, start, end) 

phrase_funcs = { # could hardly wait to meet
"Vend": lambda doc, start, end, tag: print(doc[end-1].lemma_ + f":VERB:prmods|" + doc[start].lemma_ + " " + doc[start+1:end].text) , 
"VP": lambda doc, start, end, tag: print(doc[start].lemma_ + f":{doc[start].pos_}:VP|" + doc[start].lemma_ + " " + doc[start+1:end].text) , 
"PP": lambda doc, start, end, tag: print(doc[end-1].lemma_ + f":{doc[end-1].pos_}:PP|" + doc[start:end].text) ,
"AP": lambda doc, start, end, tag: print(doc[end-1].lemma_ + f":{doc[end-1].pos_}:AP|" + doc[start:end].text) ,
}


def trpx(doc):
	if not hasattr(trpx, 'matcher'): 
		trpx.matcher = DepMatcher({
		"dobj-advmod":[ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "n","RIGHT_ATTRS": {"DEP": "dobj"}  }, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "adv", "RIGHT_ATTRS": {"DEP": "advmod"}}], # the last one , is the ADV 
		"dobj-amod":  [ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "n","RIGHT_ATTRS": {"DEP": "dobj"}  }, {"LEFT_ID": "n", "REL_OP": ">", "RIGHT_ID": "a", "RIGHT_ATTRS": {"DEP": "amod"}}], # 1,4,3  the last one is the adj 
		"nba":[ {"RIGHT_ID": "v","RIGHT_ATTRS": {"LEMMA": "be"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "subject", "RIGHT_ATTRS": {"DEP": "nsubj", "POS":"NOUN"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "object","RIGHT_ATTRS": {"DEP": "acomp"}}],  # fate is good, film:NOUN:nba:ADJ
		"nbn":[ {"RIGHT_ID": "v","RIGHT_ATTRS": {"LEMMA": "be"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "subject", "RIGHT_ATTRS": {"DEP": "nsubj", "POS":"NOUN"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "object","RIGHT_ATTRS": {"DEP": "attr", "POS":"NOUN"}}],  # scene is a story
		"advcl-acomp":[ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}}, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "clv", "RIGHT_ATTRS": {"DEP": "advcl"}},{"LEFT_ID": "clv", "REL_OP": ">", "RIGHT_ID": "object","RIGHT_ATTRS": {"DEP": "acomp"}}],  # "While I was thrilled that it cried, I worried that I would fail.
		"prt-dobj":  [ {"RIGHT_ID": "v",  "RIGHT_ATTRS": {"POS": "VERB"}},{"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "prt","RIGHT_ATTRS": {"DEP": "prt"}  }, {"LEFT_ID": "v", "REL_OP": ">", "RIGHT_ID": "n", "RIGHT_ATTRS": {"DEP": "dobj"}}], # turn off the radio 
		})  # nbe? nbx = nba + nbe + nbn
		trpx.func = { #drink:VERB:dobj:NOUN:water:amod:ADJ safe
		"dobj": lambda doc, i, j, k, tag:  add( f"{doc[i].lemma_}:{doc[i].pos_}:{doc[j].dep_}:{doc[j].pos_}:{doc[j].lemma_}:{doc[k].dep_}:{doc[k].pos_}|{doc[k].lemma_}" ) ,  
		"nba":	lambda doc, i, j, k, tag:  add(f"{doc[j].lemma_}:{doc[j].pos_}:{tag}|{doc[k].lemma_}", f"{doc[k].lemma_}:{doc[k].pos_}:~{tag}|{doc[j].lemma_}"
												, f"{doc[j].lemma_}:{doc[j].pos_}|{tag}", f"{doc[k].lemma_}:{doc[k].pos_}|~{tag}") ,
		"nbn":	lambda doc, i, j, k, tag:  add(f"{doc[j].lemma_}:{doc[j].pos_}:{tag}|{doc[k].lemma_}", f"{doc[k].lemma_}:{doc[k].pos_}:~{tag}|{doc[j].lemma_}"
												, f"{doc[j].lemma_}:{doc[j].pos_}|{tag}", f"{doc[k].lemma_}:{doc[k].pos_}|~{tag}") ,
		"advcl":lambda doc, i, j, k, tag:  add(f"{doc[i].lemma_}:{doc[i].pos_}:advcl:acomp|{doc[k].text.lower()}", f"{doc[k].text.lower()}:acomp:~advcl:{doc[i].pos_}|{doc[i].lemma_}"
											,f"{doc[i].lemma_}:{doc[i].pos_}:advcl|acomp", f"{doc[k].text.lower()}:acomp:~advcl|{doc[i].pos_}") ,
		"prt":lambda doc, i, j, k, tag:  add(f"{doc[i].lemma_}_{doc[j].lemma_}:{doc[i].pos_}:dobj:{doc[k].pos_}|{doc[k].lemma_}", f"{doc[k].lemma_}:{doc[k].pos_}:~dobj:{doc[i].pos_}|{doc[i].lemma_}_{doc[j].lemma_}"
											,f"{doc[i].lemma_}_{doc[j].lemma_}:{doc[i].pos_}:dobj|{doc[k].pos_}") ,
		}
	for name, ar in trpx.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			i,j,k = ar[0:3] 
			trpx.func[tag.split('-')[0]](doc, i,j,k, tag) 
		except Exception as e:
			print ("trpx ex:", e, name, ar) 

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
		"VP": lambda doc, start, end, tag: addone(doc[start].lemma_ + f":{doc[start].pos_}:VP|" + doc[start].lemma_ + " " + doc[start+1:end].text) , 
		"PP": lambda doc, start, end, tag: addone(doc[end-1].lemma_ + f":{doc[end-1].pos_}:PP|" + doc[start:end].text) ,
		"AP": lambda doc, start, end, tag: addone(doc[end-1].lemma_ + f":{doc[end-1].pos_}:AP|" + doc[start:end].text) ,
		}
	for name, start, end in XP.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			XP.func[tag](doc, start, end, tag ) 
		except Exception as e:
			print ("postag ex:", e, name, start, end) 

def postag(doc): 
	if not hasattr(postag, 'matcher'): 
		postag.matcher = en.phrase_matcher({
		"vpn": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} , {"TAG":"NN"}]],  # come into force 
		"bpn": [[{"LEMMA":"be"}, {"POS":"ADP"} , {"TAG":"NN"}]],  # be in force => vpn 
		"vnp": [[{"POS":"VERB"}, {"TAG":"NN"}, {"POS":"ADP"} ]],  # make use of, lay emphasis on
		"vp": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"POS":"ADP"} ]],  # abide by | distinguish from
		"vpp": [[{"POS":"VERB"}, {"POS":"ADP"}, {"POS":"ADP"} ]], # live up to
		"vpg": [[{"POS":"VERB"}, {"POS":"ADP"}, {"TAG":"VBG","DEP":"pcomp"} ]], # insisted on going
		"pn": [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}]],  # by force
		"pnp": [[{"POS":"ADP", "DEP":"prep"} , {"TAG":"NN", "DEP":"pobj"}, {"POS":"ADP", "DEP":"prep"}]],  # on account of
		"bapv": [[{"LEMMA":"be"} , {"TAG":{"IN": ["JJ"]}}, {"LEMMA":"to"}, {"POS":"VERB"}]],  # 
		"bepv": [[{"LEMMA":"be"} , {"TAG":{"IN": ["VBN"]}}, {"LEMMA":"to"}, {"POS":"VERB"}]],  # be forced to go / ? bepv? 
		"bap": [[{"LEMMA":"be"} , {"TAG":{"IN": ["JJ"]}}, {"POS":"ADP"}]], #be ignorant of
		"bep": [[{"LEMMA":"be"} , {"TAG":{"IN": ["VBN"]}}, {"POS":"ADP"}]],  # be forced to
		"vop": [[{"POS":"VERB"} , {"TEXT": {"REGEX": "[a-z]+self$"}}, {"POS":"ADP"}]], #throw oneself into
		"vtv": [[{"POS":"VERB"}, {"LEMMA":"to"}, {"POS":"VERB", "DEP":"xcomp"} ]], 
		"vg": [[{"POS":"VERB"},  {"TAG":"VBG", "DEP":"xcomp"} ]], 
		"vdpg": [[{"POS":"VERB"},  {"POS":"ADV"} ,  {"POS":"ADP"} ,  {"TAG":"VBG"} ]],  # look forward to seeing
		})
		postag.func = {
		"vpn": lambda doc, start, end, tag: (addone(f"{doc[start].lemma_}:VERB:vpn|{doc[start].lemma_} {doc[start+1:end].text}", f"{doc[end-1].lemma_}:NOUN:vpn|{doc[start].lemma_} {doc[start+1:end].text}"), add(f"{doc[end-1].lemma_}:NOUN:vpn|_VERB {doc[start+1:end].text}") ) , # _VERB with force
		"bpn": lambda doc, start, end, tag: (addone(f"{doc[start].lemma_}:VERB:vpn|{doc[start].lemma_} {doc[start+1:end].text}", f"{doc[end-1].lemma_}:NOUN:vpn|{doc[start].lemma_} {doc[start+1:end].text}"), add(f"{doc[end-1].lemma_}:NOUN:vpn|_VERB {doc[start+1:end].text}") ) , # be with force, be is a VERB
		"vnp": lambda doc, start, end, tag: addone(f"{doc[start].lemma_}:VERB:vnp|{doc[start].lemma_} {doc[start+1:end].text}", f"{doc[start+1].lemma_}:NOUN:vnp|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"vp":  lambda doc, start, end, tag: addone(f"{doc[start].lemma_}:VERB:vp|{doc[start].lemma_} {doc[start+1].text}") ,
		"vpp": lambda doc, start, end, tag: addone(f"{doc[start].lemma_}:VERB:vpp|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"vpg": lambda doc, start, end, tag: (addone(f"{doc[start].lemma_}:VERB:vpg|{doc[start].lemma_} {doc[start+1].text}") ,add(f"{doc[start].lemma_}:VERB:vpg|_{doc[start].lemma_} {doc[start+1].text} _VBG") ),
		"pn":  lambda doc, start, end, tag: addone(f"{doc[start+1].lemma_}:NOUN:pn|{doc[start:end].text.lower()}") ,
		"pnp": lambda doc, start, end, tag: addone(f"{doc[start+1].lemma_}:NOUN:pnp|{doc[start:end].text.lower()}") ,
		"bapv": lambda doc, start, end,tag: (addone(f"{doc[start+1].lemma_}:ADJ:bapv|{doc[start].lemma_} {doc[start+1:end].text}") ,add(f"{doc[start+1].lemma_}:ADJ:bapv|_{doc[start].lemma_} {doc[start+1:end-1].text} _VERB") ),  
		"bepv": lambda doc, start, end,tag: (addone(f"{doc[start+1].lemma_}:VERB:bepv|{doc[start].lemma_} {doc[start+1:end].text}") , add(f"{doc[start+1].lemma_}:VERB:bepv|_be {doc[start+1:end-1].text} _VERB") ), # _be forced to _VERB
		"bap": lambda doc, start, end, tag: addone(f"{doc[start+1].lemma_}:ADJ:bap|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"bep": lambda doc, start, end, tag: addone(f"{doc[start+1].lemma_}:VERB:bep|{doc[start].lemma_} {doc[start+1:end].text}") ,
		"vop": lambda doc, start, end, tag: addone(f"{doc[start].lemma_}:VERB:vop|{doc[start].lemma_} oneself {doc[end-1].text}") ,
		"vtv": lambda doc, start, end, tag: (addone(f"{doc[start].lemma_}:VERB:vtv|{doc[start].lemma_} {doc[start+1:end].text}") , add(f"{doc[start].lemma_}:VERB:vtv|_{doc[start].lemma_} {doc[start+1:end-1].text} _VERB") ),  
		"vg": lambda doc, start, end, tag:	(addone(f"{doc[start].lemma_}:VERB:vg|{doc[start].lemma_} {doc[end-1].text}") , add(f"{doc[start].lemma_}:VERB:vg|_{doc[start].lemma_} _VBG") ), 
		"vdpg": lambda doc, start, end,tag: (addone(f"{doc[start].lemma_}:VERB:vdpg|{doc[start].lemma_} {doc[start+1:end].text}") ,add(f"{doc[start].lemma_}:VERB:vdpg|_{doc[start].lemma_} {doc[start+1:end-1].text} _VBG") ),
		}
	for name, start, end in postag.matcher(doc):
		try:
			tag = spacy.nlp.vocab[name].text
			postag.func[tag](doc, start, end, tag ) 
		except Exception as e:
			print ("postag ex:", e, name, start, end) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)

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
	"vntb": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"ENT_TYPE":"NP"}, {"LEMMA":"to"} , {"LEMMA":"be"}]], # consider _NP _NP | _NP _ADJ | _NP to be 
	"vntv": [[{"POS":"VERB","TAG": {"NOT_IN": ["VBN"]}}, {"ENT_TYPE":"NP"}, {"LEMMA":"to"} , {"POS":"VERB"}]], # _force _NP to _VERB
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

def json_walk(infile, name):
	start = time.time()
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			add( "SNTNUM|#")  
			arr = json.loads(line.strip()) 
			snt = arr.get('text','')
			for tok in arr.get('tokens',[]):
				lem,pos,tag,lex = tok['lemma'], tok['pos'], tok['tag'], snt[ tok['start']: tok['end'] ].lower()
				add( "LEXSUM|#", f"#{pos}|#", f"#{tag}|#", f"#LEM|#", f"#LEX|#")
				if pos not in ('PROPN','X', 'PUNCT') : 
					add(f"LEM|{lem}", f"{lem}:LEM|#", f"LEX|{lex}", f"{lem}:LEX|{lex}")
				if pos in ('VERB','NOUN','ADJ','ADV'):
					add(f"{pos}|{lem}", f"*|{pos}", f"{lem}|{pos}", f"{lem}:{pos}|{tag}", f"*:{pos}|{tag}", f"{tag}|{lex}") # VBD :  made , added 2022.12.10
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
	print(f"{infile} json-walk is finished, \t| using: ", round(time.time() - start,1), len(fire.ssi) ) 

def spacy_walk(infile,name, batch:int=100000):
	start = time.time()
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			arr = json.loads(line.strip()) 
			doc = spacy.from_json(arr) 
			[ add(f"{t.head.lemma_}:{t.head.pos_}|vc") for t in doc if t.dep_ == 'ccomp' and t.head.pos_ == 'VERB' ]
			[ add(f"{t.lemma_}:{t.pos_}|ROOT") for t in doc if t.dep_ == 'ROOT' ]
			[ add(f"{t.head.lemma_}:{t.head.pos_}:xcomp:{t.tag_}|{t.text}", f"{t.head.lemma_}:{t.head.pos_}:xcomp|{t.tag_}",
				  f"{t.text}:{t.tag_}:~xcomp:{t.head.pos_}|{t.head.lemma_}", f"{t.text}:{t.tag_}:~xcomp|{t.head.pos_}") for t in doc if t.dep_ == 'xcomp' ]
			[ add(f"{t.lemma_}:{t.pos_}:nbe:VBN|{t.head.text.lower()}", 
				  f"{t.head.text.lower()}:VBN:nbe:{t.pos_}|{t.lemma_}", ) for t in doc if t.dep_ == 'nsubjpass' and t.head.tag_ == 'VBN' ] # the fate is sealed
			#[ add(f"{t.head.lemma_}:{t.head.pos_}|advcl") for t in doc if t.dep_ == 'advcl' and t.head.pos_ == 'VERB' ]
			[ add(f"{sp.root.lemma_.lower()}:{sp.root.pos_}:NP|{sp.text.lower()}", f"{sp.root.lemma_.lower()}:{sp.root.pos_}|NP", f"*:{sp.root.pos_}|NP", f"*|NP",) for sp in doc.noun_chunks] #book:NOUN:np:a book

			[ add( f"*|{t.dep_}",f"*|~{t.dep_}",f"{t.head.lemma_}:{t.head.pos_}|{t.dep_}"
				,f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}|{t.pos_}",f"{t.lemma_}:{t.pos_}|~{t.dep_}"
				,f"{t.lemma_}:{t.pos_}:~{t.dep_}|{t.head.pos_}") for t in doc  if t.dep_ not in ('ROOT','punct','xcomp')]
			[ add( f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}|{t.lemma_}", f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}|{t.pos_}",f"{t.head.lemma_}:{t.head.pos_}|{t.dep_}", f"*:{t.head.pos_}|{t.dep_}", f"*:{t.head.pos_}:{t.dep_}:{t.pos_}|{t.head.lemma_}",
				f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}|{t.head.lemma_}", f"{t.lemma_}:{t.pos_}:~{t.dep_}|{t.head.pos_}", f"{t.lemma_}:{t.pos_}|~{t.dep_}", f"*:{t.pos_}|~{t.dep_}", f"*:{t.pos_}:~{t.dep_}:{t.head.pos_}|{t.lemma_}") for t in doc if t.pos_ in ("NOUN","VERB","ADJ","ADV","ADP") and t.dep_ not in ('ROOT','punct') and t.is_alpha and t.head.is_alpha and t.lemma_.lower() in wordlist and t.head.lemma_.lower() in wordlist]

			trpx(doc) 
			postag(doc)
			XP(doc) 
			en.merge_np(doc) 
			skenp(doc) 
			if (sid+1) % batch == 0 : print (f"[{infile} -> {name}] sid = {sid}, \t| ", round(time.time() - start,1), flush=True)
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)

def run(infile, host='lab.jukuu.com' if platform.system() in ('Windows') else '172.17.0.1', port=3309, db='nac', fts:bool=False,):
	''' saveto: mysql/file , set tmptable=True when on super large file, ie:gblog, nyt, ... '''
	name = infile.split('/')[-1].split('.')[0] 
	print ("started:", infile ,  ' -> ',  name, host, flush=True)

	start = time.time()
	fire.ssi = defaultdict(Counter)
	fire.conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db=db)
	fire.cursor = fire.conn.cursor()
	fire.cursor.execute(f"drop TABLE if exists {name}")
	fire.cursor.execute(f"CREATE TABLE if not exists {name}(name varchar(64) COLLATE latin1_bin not null, attr varchar(64) COLLATE latin1_bin not null, count int not null default 0, per float not null default 0, primary key(name,attr) ) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin") # not null default ''
		
	json_walk(infile,name) 
	spacy_walk(infile, name) 

	def per(name, attr, cnt ): 
		arr = name.split(":") 
		if name.endswith(":LEX") or f"{name}:LEM" in fire.ssi:  # sound:LEX  # sound | NOUN |    27 
			k = name.split(":")[0] +":LEM"
			if k in fire.ssi: return round(100 * cnt/fire.ssi[k]['#'], 1)
		if name.endswith( (':VERB',':NOUN',':ADJ',':ADV') ) and len(arr) == 2 and arr[0] in fire.ssi and arr[1] in fire.ssi[arr[0]]: #sound:VERB | VBG  | 
			return round(100 * cnt/fire.ssi[arr[0]][arr[1]], 1)
		if name in ('VERB','NOUN','ADJ','ADV', 'LEM','LEX','VBD','VBN','JJ') : 
			return round(1000000 * cnt/fire.ssi["SNTNUM"]['#'], 1) #mf 

		k = ":".join(arr[0:-1]) #open:VERB:dobj | NOUN
		v = arr[-1]
		if k in fire.ssi and v in fire.ssi[k]: return round(100 * cnt/fire.ssi[k][v], 1) 
		return 0

	fire.cursor.executemany(f"insert ignore into {name}(name, attr, count, per) values(%s, %s, %s, %s)",[(k,s,i, per(k,s,i) ) for k,si in fire.ssi.items() for s,i in si.items() ]) 
	fire.conn.commit()
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

if __name__	== '__main__':
	run("gzjc.jsonlg.3.4.1.gz") if platform.system() in ('Windows') else fire.Fire(run)

'''
hyb:be able to _VERB|convince|72
could hardly wait to _VERB

root@172.17.0.1|nac>select *, round(count * 100 /per)  from clec where name = 'look:VERB:vpp';
+---------------+-------------------+-------+------+-------------------------+
| name          | attr              | count | per  | round(count * 100 /per) |
+---------------+-------------------+-------+------+-------------------------+
| look:VERB:vpp | look after in     |     1 |  2.7 |                      37 |
| look:VERB:vpp | look down on      |     3 |  8.1 |                      37 |

select * , keyness(cnt1, cnt2, sm1, sm2) kn from 
(select attr, count cnt1 , round(count * 100 /per) sm1 from gzjc where name = 'consider:VERB' and count > 3 ) a 
join 
(select attr, count cnt2, round(count * 100 /per) sm2 from gzjc where name = '*:VERB' and count > 10 ) b 
using (attr)
order by kn desc 

root@172.17.0.1|nac>select * from dic where name = 'book:NOUN:acl:VERB:call'; 
+-------------------------+----------------------------------------------------------------------------+-------+
| name                    | attr                                                                       | count |
+-------------------------+----------------------------------------------------------------------------+-------+
| book:NOUN:acl:VERB:call | By late 1983 I was putting the finishing touches on a book called Hackers. |     6 |
+-------------------------+----------------------------------------------------------------------------+-------+
1 row in set (0.005 sec)


'''