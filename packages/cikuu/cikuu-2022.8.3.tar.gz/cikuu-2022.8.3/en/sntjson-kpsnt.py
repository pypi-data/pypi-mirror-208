# 2023.2.4,  kpsnt(kp,snt), to be merged to nacp later 
import json, traceback,sys, time, fire,os,traceback,fileinput,en, pymysql

def run(infile, host:str='172.17.0.1', port:int=3309, db:str='nacp'):
	'''  '''
	name = infile.split('.jsonlg' if '.jsonlg' in infile else '.')[0] 
	start = time.time()
	my_conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db=db)
	print ("sntjson-kpsnt started:", infile , name,  flush=True)
	with my_conn.cursor() as cursor: 
		cursor.execute(f"drop TABLE if exists {name}_kpsnt")
		cursor.execute(f"CREATE TABLE if not exists {name}_kpsnt(kp varchar(64) not null primary key, snt varchar(128) not null, cnt int not null default 0, per float not null default 0) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")
	
		kpset = set() # added 2023.3.14
		def reg( kp, snt): #reg = lambda kp, snt : cursor.execute(f"insert ignore into {name}_kpsnt(kp, snt) values(%s, %s)", (kp, snt)) if len(snt) <= 128 else None
			if kp not in kpset : 
				cursor.execute(f"insert ignore into {name}_kpsnt(kp, snt) values(%s, %s)", (kp, snt)) if len(snt) <= 128 else None
				kpset.add(kp) 

		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)):  
			try:
				arr = json.loads(line.strip()) 
				tdoc = spacy.from_json(arr)  
				for sid, sp in enumerate(tdoc.sents):				
					doc = sp.as_doc()
					for t in doc:
						if t.pos_ in ('VERB','NOUN','ADJ','ADV','ADP') : 
							reg(f"{t.lemma_}:{t.pos_}:{t.tag_}", doc.text.replace(t.text, f"***{t.text}***"))
							reg(f"{t.lemma_}:{t.pos_}:{t.tag_}:{t.text.lower()}", doc.text.replace(t.text, f"***{t.text}***")) # 2023.2.16
							reg(f"{t.lemma_}:{t.pos_}", doc.text.replace(t.text, f"***{t.text}***")) # consider:NOUN

						if t.pos_ not in ("PROPN","PUNCT","SPACE") and t.pos_ in ('VERB','NOUN','ADJ','ADV','ADP') and t.dep_ not in ('ROOT') and t.is_alpha and t.head.is_alpha: 
							snt = doc.text.replace(t.text, f"**{t.text}**").replace(t.head.text, f"***{t.head.text}***")
							reg(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}", snt) 
							reg(f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}:{t.head.lemma_}", snt)
							if t.dep_ == 'xcomp': 
								reg(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.tag_}", snt) 
				
					for sp in doc.noun_chunks: #book:NOUN:np:a book
						reg(f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np:{sp.text.lower()}", doc.text.replace(sp.text, f"***{sp.text}***") )
					# add kp,  vna, vnn, vp, ... , later  |
					for kp, item in en.kp_born(doc).items(): 
						reg(kp, doc.text ) # vp:contact with, added 2023.2.12 
						[reg(nac, doc.text ) for nac in item.get('nac',[]) if not '*' in nac] # sound:VERB:~vtv NONE 

			except Exception as e: 
				print ("ex:", e, sid,line)
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)
	my_conn.commit()
	print(f"{infile} is finished, \t| using: ", round(time.time() - start, 1) ) 

if __name__	== '__main__':
	fire.Fire(run)
