# 2023.2.9 , cp from sntjson-naclite.py | VBN -> past participle -> e | t -> to, b -> be , g -> VBG, c-> Clause , d-> ADV
import json, traceback,sys, time,  fileinput, os, fire,pathlib, pymysql, platform
from __init__ import *
from collections import Counter,defaultdict
add		= lambda *names: [fire.ssi[ name.split('|')[0] ].update({ name.split('|')[-1] : 1}) for name in names if  not '\t' in name and len(name) <= 80 ]

def spacy_walk(infile,name, batch:int=100000):
	start = time.time()
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			arr = json.loads(line.strip()) 
			doc = spacy.from_json(arr) 
			add( "SNTNUM|#")  #The third configuration Considers mixing gas with a coal-water slurry.
			[add( "LEXSUM|#", f"#{t.pos_}|#", f"#{t.tag_}|#", f"#LEM|#", f"#LEX|#") for t in doc]
			[add(f"LEM|{t.lemma_}", f"{t.lemma_}:LEM|#", f"LEX|{t.text.lower()}", f"{t.lemma_}:LEX|{t.text.lower()}") for t in doc if t.pos_ not in ('PROPN','X', 'PUNCT')]
			for kp, item in kp_born(doc).items(): # user_data 
				if 'nac' in item: 
					add(* item['nac'] ) 
			if (sid+1) % batch == 0 : 
				print (f"[{infile} -> {name}] sid = {sid}, \t| ", round(time.time() - start,1), flush=True)
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)

def run(infile, host='sntvec.wrask.com' if platform.system() in ('Windows') else '172.17.0.1', port=3309, db='nacp',):
	''' saveto: mysql/file , set tmptable=True when on super large file, ie:gblog, nyt, ... '''
	name = infile.split('/')[-1].split('.')[0] 
	print ("nacp training started:", infile ,  ' -> ',  name, host, port, db, flush=True)

	start = time.time()
	fire.ssi = defaultdict(Counter)
	fire.conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db=db)
	fire.cursor = fire.conn.cursor()
	fire.cursor.execute(f"drop TABLE if exists {name}")
	fire.cursor.execute(f"CREATE TABLE if not exists {name}(name varchar(64) COLLATE latin1_bin not null, attr varchar(64) COLLATE latin1_bin not null, count int not null default 0, per float not null default 0, snt varchar(128) not null default '', primary key(name,attr), KEY `attr` (`attr`) ) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin") # not null default ''
		
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

	try:
		fire.cursor.executemany(f"insert ignore into {name}(name, attr, count, per) values(%s, %s, %s, %s)",[(k,s,i, per(k,s,i) ) for k,si in fire.ssi.items() for s,i in si.items() ]) 
	except Exception as e: # batch -> step by step
		print ("batch submit failed:", e, flush=True)
		[ fire.cursor.execute(f"insert ignore into {name}(name, attr, count, per) values(%s, %s, %s, %s)",(k,s,i, per(k,s,i) ) ) for k,si in fire.ssi.items() for s,i in si.items() ]

	# set *:VERB attr | select sum(count) FROM gzjc where attr  = 'vtv'
	for attr in postag_func_kp: # ('vtv','vg') : 
		fire.cursor.execute(f"select sum(count) FROM {name} where attr  = '{attr}'")
		cnt = fire.cursor.fetchall()[0][0]
		if cnt is None: cnt = 0
		fire.cursor.execute(f"insert ignore into {name}(name, attr, count, per) values(%s, %s, %s, %s)",(f"*:VERB",attr,cnt, round(100 * cnt/fire.ssi['*']['VERB'],1) )  ) 

	fire.cursor.execute(f"update {name}, {name}_kpsnt set {name}.snt = {name}_kpsnt.snt where kp = concat(name, ':', attr)") # add 2023.2.16
	# vp:contact with
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

def term(doc): 
	try:
		add( "SNTNUM|#")  
		for t in doc:
			lem,pos,tag,lex = t.lemma_, t.pos_, t.tag_, t.text.lower()
			add( "LEXSUM|#", f"#{pos}|#", f"#{tag}|#", f"#LEM|#", f"#LEX|#")
			if pos not in ('PROPN','X', 'PUNCT') : add(f"LEM|{lem}", f"{lem}:LEM|#", f"LEX|{lex}", f"{lem}:LEX|{lex}")
			if pos in ('VERB','NOUN','ADJ','ADV'): add(f"{pos}|{lem}", f"*|{pos}", f"{lem}|{pos}", f"{lem}:{pos}|{tag}", f"*:{pos}|{tag}", f"{tag}|{lex}") # VBD :  made , added 2022.12.10
	except Exception as e:
		print ("term ex:", e) 

'''