# 2023.1.19,  
import json, traceback,sys, time, fire,os,traceback,fileinput,en, pymysql

def run(infile, host:str='172.17.0.1', port:int=3309, db:str='nac'):
	'''  '''
	name = infile.split('.')[0] 
	start = time.time()
	my_conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db=db)
	print ("started:", infile , my_conn,  flush=True)
	with my_conn.cursor() as cursor: 
		cursor.execute(f"drop TABLE if exists {name}_spacy")
		#cursor.execute(f"CREATE TABLE `{name}_spacy` (`sid` int(11) NOT NULL, `tc` int(11) NOT NULL default 0, `snt` text NOT NULL,`spacy` text NOT NULL, PRIMARY KEY (`sid`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED")
		cursor.execute(f"CREATE TABLE `{name}_spacy` (`sid` int(11) NOT NULL, `tc` int(11) NOT NULL default 0, `snt` text NOT NULL,`spacy` text NOT NULL, PRIMARY KEY (`sid`)) ENGINE=myisam DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPRESSED")
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)):  #for rowid, snt, doc in tqdm(Spacybs(dbfile).docs()) :
			try:
				arr = json.loads(line.strip()) 
				doc = spacy.from_json(arr)  #for sid, sp in enumerate(tdoc.sents):				doc = sp.as_doc()
				cursor.execute(f"insert ignore into {name}_spacy(sid, tc, snt, spacy) values(%s, %s, %s, %s)", (sid, len(doc), doc.text.strip(), line.strip()) )
			except Exception as e: 
				print ("ex:", e, sid,line)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

if __name__	== '__main__':
	fire.Fire(run)