# 2022.3.10
import requests,re,time,sqlite3,itertools,sys,traceback,os
from collections import	Counter, defaultdict
now	= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))

import hashlib
sntmd5	= lambda sntarr: " ".join([hashlib.md5(snt.strip().lower().encode("utf-8")).hexdigest() for snt in sntarr if len(snt) > 1])
md5text	= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()
md5		= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()

from functools import wraps 
def tried(func):
	@wraps(func)
	def get_except(*args,**kw):
		try:
			return func(*args,**kw)
		except Exception as e:
			print(f'{func.__name__} exception:{e}')
			exc_type, exc_value, exc_traceback_obj = sys.exc_info()
			traceback.print_tb(exc_traceback_obj)
	return get_except
    
#test_demo
@tried
def tried_demo(num):
	return num/0

def walkfolder(folder:str, pattern:str=".txt"): 
	''' 2023.5.5 '''
	for root, dirs, files in os.walk(folder):
		for file in files: 
			if file.endswith(pattern):
				text = open(f"{folder}/{file}", 'r').read().strip() 
				yield (file, text)  #{"folder":folder, "filename":file, "content":text}

def sqlite_conn(sql:str="create table nac( name varchar(64) not null , attr varchar(64) not null, count int not null default 0, primary key(name, attr) ) without rowid") :
	conn  =	sqlite3.connect(outfile, check_same_thread=False) 
	conn.execute(sql)
	conn.execute('PRAGMA synchronous=OFF')
	conn.execute('PRAGMA case_sensitive_like = 1')
	conn.commit()
	return conn 

toks_product = lambda snt='one two/x three/y': [ar for ar in itertools.product( * [a.strip().split('/') for a in snt.strip().split()]) ]  #[('one', 'two', 'three'),  ('one', 'two', 'y'), ('one', 'x', 'three'), ('one', 'x', 'y')]
def cands_product(q='one two/ three/', sepa:str='/'):
	''' {'one three', 'one two', 'one two three'} '''
	if not ' ' in q : return set(q.strip().split(sepa))
	arr = [a.strip().split(sepa) for a in q.split()]
	res = [' '.join([a for a in ar if a]) for ar in itertools.product( * arr)]
	return [ s for s in set( [a.strip() for a in res if ' ' in a]) ]

from math import log as ln
def likelihood(a,b,c,d, minus=None):  #from: http://ucrel.lancs.ac.uk/llwizard.html
	try:
		if a is None or a <= 0 : a = 0.000001
		if b is None or b <= 0 : b = 0.000001
		if c is None or c <= 0 : c = 0.000001
		if d is None or d <= 0 : d = 0.000001
		E1 = c * (a + b) / (c + d)
		E2 = d * (a + b) / (c + d)
		G2 = round(2 * ((a * ln(a / E1)) + (b * ln(b / E2))), 2)
		if minus or  (minus is None and a * d < b * c): G2 = 0 - G2 #if minus or  (minus is None and a/c < b/d): G2 = 0 - G2
		return round(G2,1)
	except Exception as e:
		print ("likelihood ex:",e, a,b,c,d)
		return 0

def keyness(srcrows:list=[['one',5],['two',7]], srcsum:int=None, tgtrows:list=[['one',5],['three',17]], tgtsum:int=None, reverse:bool=True, topk:int=30):
	''' (word, src, tgt, srcper, tgtper, keyness), srcrows is the es result, 2023.5.10 '''
	srcsum	= sum([i for s,i in srcrows]) + 0.01 if srcsum is None else srcsum + 0.01
	tgtsum	= sum([i for s,i in tgtrows]) + 0.01 if tgtsum is None else tgtsum + 0.01
	dic1    = dict(tgtrows) 
	rows	= [ (s, i, dic1.get(s,0), round(100.0 * i/srcsum,1), round(100.0 * dic1.get(s,0)/tgtsum,1), likelihood( i, dic1.get(s,0), srcsum, tgtsum ) ) for s,i in srcrows ] 
	rows.sort(key=lambda a:a[-1], reverse =reverse)
	return rows[0:topk]	

has_zh = lambda s : any([c for c in s if ord(c) > 255])

def logdice(xy, x, y): # https://www.fi.muni.cz/usr/sojka/download/raslan2008/13.pdf
	return round(14  + ln ( 2 * xy/ (x+y), 2),1)
#print (logdice( 1, 23, 56) )

def lexlist( lemma='open', sepa="|"):
	from dic import lemma_lex
	return sepa.join(list(lemma_lex.lemma_lex.get(lemma, [lemma]))) #opens|openest|opened|opener|opening|open
highlight	= lambda snt='I open the door.', words='open|opened|door': re.sub(rf'\b({words})\b', r'<b>\g<0></b>', snt) if words else snt
token_split	= lambda sent: re.findall(r"[\w']+|[.,!?;]", sent) # return list

def  si_to_es(si, index, batch=10000, eshost='127.0.0.1',esport=9200): 
	''' ie: spellerr, added 2022.9.6 '''
	print (len(si), index,  flush=True) 
	actions=[]
	for s,i in si.items() if isinstance(si, dict) else si: 
		try:
			requests.post(f"http://{eshost}:{esport}/{index}/{s}", json={"s": s, "i":i})
		except Exception as e:
			print("ex:", e)	
	print(">>load finished:" , index )

def xblpop(r, name, arr, timeout=10, suc_prefix='suc:', err_prefix="err:"):
	''' name:xsnt/xsnts, arr: {"snt": "hello"}  added 2022.4.4 '''
	id  = r.xadd(name, arr)
	return r.blpop([f"{suc_prefix}{id}",f"{err_prefix}{id}"], timeout=timeout)

def getlog(logfile='daily.log'):
	import logging
	from logging.handlers import TimedRotatingFileHandler
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	handler = TimedRotatingFileHandler(logfile, when="midnight", interval=1)
	handler.suffix = "%Y%m%d"
	logger.addHandler(handler)
	handler.setLevel(logging.INFO) 
	handler.setFormatter(logging.Formatter("%(message)s"))
	logger.addHandler(handler)
	return logger

def readline(infile, sepa=None): #for line in fileinput.input(infile):
	with open(infile, 'r', encoding='utf-8') as fp:
		while True:
			line = fp.readline()
			if not line: break
			yield line.strip().split(sepa) if sepa else line.strip()

def process(infile, outfile, asjson=True, func = lambda x: x):
	''' line processor, added 2022.3.20  '''
	print ("process started:", infile, outfile, flush=True)
	with open(outfile, 'w') as fw: 
		for line in readline(infile):
			try:
				fw.write( func( json.loads(line.strip(), strict=False) if asjson else line.strip())  + "\n")
			except Exception as ex:
				print ("process ex:", ex, line) 
	print ('process finished:', infile) 

def hset_if_greater(r, key, eid, ver ): 
	res = r.hget(key, eid)
	try: 
		if not res :
			r.hset(key, eid, ver)
		else: 
			if int(ver) > int(res) : r.hset(key, eid, ver)
	except Exception as e:
		print("ex:", e, eid)

# nltk
def traverse(t, label='NP', f = lambda t:  print(t.pos()) ):
  try:
      t.label()
  except AttributeError:
      return
  else:
      if t.label() == label: f(t)  # or do something else
      else:
          for child in t: 
              traverse(child, label, f)

if __name__ == '__main__': 
	print( keyness()) 