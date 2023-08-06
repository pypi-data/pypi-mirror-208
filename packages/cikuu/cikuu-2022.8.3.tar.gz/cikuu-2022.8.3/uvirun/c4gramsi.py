# 2023.2.7, cp from exchunk_fastapi.py # 2022.6.30  # 2022.2.10  uvicorn exchunk:app --host 0.0.0.0 --port 7058 --reload | 8004 @ cpu76
from uvirun import *
import traceback, sys,sqlite3

isNP	= lambda t: t.ent_type_ == 'NP' and ' ' in t.text # len > 1 
doctoks = lambda doc: ['<s>'] + [ f"_{t.pos_}" if t.pos_ in ('PROPN','NUM','CD','X','SPACE') else "_NP" if isNP(t) else t.text.lower()  for t in doc ]

def ngram(toks, n:int=4): 
	ts = set() 
	tlen =  len(toks)
	for i in range( tlen ): 
		for j in range(n): 
			if i+j < tlen: 
				ts.add( " ".join(toks[i:i+j]) )
	return [t for t in ts if t and not '.' in t and not "'" in t]

def c4get(grams:list=['<s> is','jumped over _NP'], name='c4gram'):  
	if not hasattr(c4get,name): setattr( c4get, name, sqlite3.connect(f"/data/model/c4/{name}.si", check_same_thread=False) )  
	return { row[0] : row[1] for row in getattr(c4get, name).execute("select s,i from si where s in ('"+"','".join([k for k in grams if not "'" in k])+"')") } 

@app.get('/c4gram/ngram_check', tags=["c4"])
def ngram_check(snt:str="The quick fox jumped over the lazy dog.", n:int=4, lessthan:int=0):
	''' 2023.2.12 '''
	import en
	doc = spacy.nlp(snt)
	merge_np(doc) 
	toks	= doctoks(doc)
	grams	= ngram(toks, n)
	dic		= c4get(grams) 
	return [ {"gram": w, "cnt": dic.get(w,0) } for w in grams if dic.get(w,0) <= lessthan ]

@app.get('/c4get/si', tags=["c4"])
def c4get_si(chunks:str="just like|jumped over _NP", name:str='c4gram', sepa:str="|"): 
	''' name=c4np/c4gram  '''
	chk = chunks.strip().split(sepa) 
	dic = c4get(chk, name) 
	return [ {"s": w, "i": dic.get(w,0) } for w in chk if w]

@app.post('/c4get/sijson', tags=["c4"])
def c4get_sijson(rows:list=[{"kp":"VB:plan"}, {"kp":"vtv:plan to go"}, {"kp":"dobj-VERB-NOUN:learn knowledge"}], lib:str='endic-kp', name:str='kp', lessthan:int=0): 
	''' input is the spacy_kp output, 2023.2.13  '''
	chunks = [ row.get(name,'') for row in rows if row.get(name,'') ]
	dic = c4get(chunks, lib) 
	return [ {"s": w, "i": dic.get(w,0) } for w in chunks if w  and dic.get(w,0) <= lessthan] 

if __name__ == "__main__":  
	print ( c4get_sijson())

'''
@app.get('/c4gram/si', tags=["c4"])
def c4gram_si(chunks:str="just like|jumped over _NP", sepa:str="|"): 
	chk = chunks.strip().split(sepa) 
	dic = c4gram(chk) 
	return [ {"gram": w, "cnt": dic.get(w,0) } for w in chk]

def c4gram(grams:list=['<s> is','jumped over _NP']):  
	if not hasattr(c4gram,'conn'): 
		c4gram.conn	= sqlite3.connect("/data/model/c4/c4gram.si", check_same_thread=False)  # how to set readonly ? 
		c4gram.conn.execute(f'CREATE TABLE IF NOT EXISTS si (s varchar(100) PRIMARY KEY, i int) without rowid')
	return { row[0] : row[1] for row in c4gram.conn.execute("select s,i from si where s in ('"+"','".join([k for k in grams])+"')") }
'''