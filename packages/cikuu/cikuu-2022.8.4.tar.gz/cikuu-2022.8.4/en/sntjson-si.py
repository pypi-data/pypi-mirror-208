# 2023.2.7 , cp from sntjson-nacp.py | dobj-VERB-NOUN:open door, VBD:made | VBN -> past participle -> e | t -> to, b -> be , g -> VBG, c-> Clause , d-> ADV
import json, traceback,sys, time,  fileinput, os, fire,pathlib, pymysql, platform
from collections import Counter,defaultdict
from __init__ import * 

def run(infile, host='lab.jukuu.com' if platform.system() in ('Windows') else '172.17.0.1', port=3309, db='nacp', fts:bool=False, batch:int=100000):
	''' saveto: mysql/file , set tmptable=True when on super large file, ie:gblog, nyt, ... '''
	name = infile.split('/')[-1].split('.')[0] 
	print ("started:", infile ,  ' -> ',  name, host, flush=True)

	start = time.time()
	fire.si = Counter()
	fire.conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db=db)
	fire.cursor = fire.conn.cursor()
	fire.cursor.execute(f"drop TABLE if exists {name}_si")
	fire.cursor.execute(f"CREATE TABLE if not exists {name}_si(s varchar(80) COLLATE latin1_bin not null primary key, i int not null default 0) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin") 
		
	for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): #356317 docs of each doc file
		try:
			arr = json.loads(line.strip()) 
			doc = spacy.from_json(arr) 
			for kp, ar in kp_born(doc, base=True).items():  # nba:book good / nbe:fate sealed 
				fire.si.update({kp.split("[")[0].strip():1}) 
			if (sid+1) % batch == 0 : 
				print (f"[{infile} -> {name}] sid = {sid}, \t| ", round(time.time() - start,1), flush=True)
		except Exception as e:
			print ("ex:", e, sid, line[0:30]) 
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)

	fire.cursor.executemany(f"insert ignore into {name}_si(s,i) values(%s, %s)",[(s,i) for s,i in fire.si.items() ]) 
	fire.conn.commit()
	print(f"{infile} is finished, \t| using: ", time.time() - start, len(fire.si) ) 

if __name__	== '__main__':
	run("gzjc.jsonlg.3.4.1.gz") if platform.system() in ('Windows') else fire.Fire(run)