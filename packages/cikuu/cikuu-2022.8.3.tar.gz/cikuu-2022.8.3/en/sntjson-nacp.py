# 2023.2.5 , cp from sntjson-naclite.py | VBN -> past participle -> e | t -> to, b -> be , g -> VBG, c-> Clause , d-> ADV
import json, traceback,sys, time,  fileinput, os, fire,pathlib, pymysql, platform
from __init__ import *
from collections import Counter,defaultdict
from dic.lex_lemma import lex_lemma
from dic.wordlist import wordlist
has_zh  = lambda s : any([c for c in s if ord(c) > 255])
span_NP = lambda sp: " ".join([ "_NP" if t.ent_type_ == 'NP' else t.lemma_ for t in sp]) #else f"_{t.tag_}" if t.tag_ in ('VBN')
add		= lambda *names: [fire.ssi[ name.split('|')[0] ].update({ name.split('|')[-1] : 1}) for name in names if  not '\t' in name and len(name) <= 80 ]
insert	= lambda name, attr:  add( f"{name}|{attr}") 
addone	= lambda *pairs: [ ( add(pair),  arr:=pair.split('|')[0].split(':'), insert(":".join(arr[0:-1]), arr[-1]), add(f"*|{arr[-1]}") )  for pair in pairs ]

postag_func = { 
	"Vend": lambda doc, start, end, tag: add(doc[end-1].lemma_ + f":VERB:prmods|" + doc[start].lemma_ + " " + doc[start+1:end].text) , 
	"VP": lambda doc, start, end, tag: addone(doc[start].lemma_ + f":{doc[start].pos_}:VP|" + doc[start].lemma_ + " " + doc[start+1:end].text) , 
	"PP": lambda doc, start, end, tag: addone(doc[end-1].lemma_ + f":{doc[end-1].pos_}:PP|" + doc[start:end].text) ,
	"AP": lambda doc, start, end, tag: addone(doc[end-1].lemma_ + f":{doc[end-1].pos_}:AP|" + doc[start:end].text) ,
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

def skenp_func(doc, start, end, tag): 
	if tag.startswith("v"): 
		lem = doc[start].lemma_
		add( f"{lem}:VERB:{tag}|" + span_NP(doc[start:end]), f"{lem}:VERB|{tag}", f"*:VERB|{tag}", f"*|{tag}" )

trp3_func = { #drink:VERB:dobj:NOUN:water:amod:ADJ safe
	"dobj-advmod": lambda doc, i, j, k, tag:  add( f"{doc[i].lemma_}:{doc[i].pos_}:{doc[j].dep_}:{doc[j].pos_}:{doc[j].lemma_}:{doc[k].dep_}:{doc[k].pos_}|{doc[k].lemma_}" ) ,  
	"dobj-amod": lambda doc, i, j, k, tag:  add( f"{doc[i].lemma_}:{doc[i].pos_}:{doc[j].dep_}:{doc[j].pos_}:{doc[j].lemma_}:{doc[k].dep_}:{doc[k].pos_}|{doc[k].lemma_}" ) ,  
	"nba":	lambda doc, i, j, k, tag:  add(f"{doc[j].lemma_}:{doc[j].pos_}:{tag}|{doc[k].lemma_}", f"{doc[k].lemma_}:{doc[k].pos_}:~{tag}|{doc[j].lemma_}"
											, f"{doc[j].lemma_}:{doc[j].pos_}|{tag}", f"{doc[k].lemma_}:{doc[k].pos_}|~{tag}") ,
	"nbn":	lambda doc, i, j, k, tag:  add(f"{doc[j].lemma_}:{doc[j].pos_}:{tag}|{doc[k].lemma_}", f"{doc[k].lemma_}:{doc[k].pos_}:~{tag}|{doc[j].lemma_}"
											, f"{doc[j].lemma_}:{doc[j].pos_}|{tag}", f"{doc[k].lemma_}:{doc[k].pos_}|~{tag}") ,
	"advcl-acomp":lambda doc, i, j, k, tag:  add(f"{doc[i].lemma_}:{doc[i].pos_}:advcl:acomp|{doc[k].text.lower()}", f"{doc[k].text.lower()}:acomp:~advcl:{doc[i].pos_}|{doc[i].lemma_}"
										,f"{doc[i].lemma_}:{doc[i].pos_}:advcl|acomp", f"{doc[k].text.lower()}:acomp:~advcl|{doc[i].pos_}") ,
	"dobj-prt":lambda doc, i, j, k, tag:  add(f"{doc[i].lemma_}_{doc[j].lemma_}:{doc[i].pos_}:dobj:{doc[k].pos_}|{doc[k].lemma_}", f"{doc[k].lemma_}:{doc[k].pos_}:~dobj:{doc[i].pos_}|{doc[i].lemma_}_{doc[j].lemma_}"
										,f"{doc[i].lemma_}_{doc[j].lemma_}:{doc[i].pos_}:dobj|{doc[k].pos_}") ,
	"vpN":	lambda doc, i, j, k, tag:  add(f"{doc[i].lemma_}:{doc[i].pos_}:vpN:{doc[i].lemma_} {doc[j].text} _NOUN|{doc[k].lemma_}"
								, f"{doc[i].lemma_}:{doc[i].pos_}:vpN:{doc[i].lemma_} {doc[j].text} _NOUN|{doc[k].lemma_}"
								, f"{doc[i].lemma_}:{doc[i].pos_}|vpN"
								 ) ,
	}

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

			postag_match(doc, postag_func) 
			trp3_match(doc, trp3_func)
			merge_np(doc)  
			skenp_match(doc, skenp_func) 

			if (sid+1) % batch == 0 : 
				print (f"[{infile} -> {name}] sid = {sid}, \t| ", round(time.time() - start,1), flush=True)
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)

def run(infile, host='lab.jukuu.com' if platform.system() in ('Windows') else '172.17.0.1', port=3309, db='nacp', fts:bool=False,):
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