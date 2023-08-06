#!/usr/bin/env  -*- coding: utf-8	-*-  2023.5.1
import sqlite3,collections

class Sntdb(collections.UserDict):  # (sid, snt) ,  sid: rowid 
	def	__init__(self, filename, tablename='snt', keylen=256):
		self.filename	= filename
		self.tablename	= tablename
		self.conn		= sqlite3.connect(self.filename, check_same_thread=False) 
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename} (snt varchar({keylen}) PRIMARY KEY)')
		self.conn.execute('PRAGMA synchronous=OFF')
		self.conn.commit()

	def load(self, sntfile): 
		[self.add(sid, snt.strip()) for sid, snt in enumerate(open(sntfile, 'r').readlines())]
		self.conn.commit()

	def	__str__(self): 	return "Sntdb(%s)"	% (self.filename)
	def	__repr__(self): return str(self)  #	no need	of something complex
	def	__len__(self):	return self.conn.execute('SELECT COUNT(*) FROM	"%s"' %	self.tablename).fetchone()[0]
	def	count(self):	return self.conn.execute('SELECT count(*) FROM "%s"'% self.tablename).fetchone()[0]
	def add(self, sid,  snt):  self.conn.execute(f"insert or ignore into {self.tablename}(rowid, snt) values(?,?)", (sid, snt)) 

	def	snts(self, start=0, len=-1):  
		for key in self.conn.execute(f'SELECT snt FROM {self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): yield key[0]
	def	items(self, start=0, len=-1): 
		for key, value in self.conn.execute(f'SELECT rowid,  snt FROM {self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): 	yield key, value
	def	__contains__(self, key): return self.conn.execute('SELECT 1 FROM "%s" WHERE snt = ?' %	self.tablename, (key,)).fetchone() is not None

	def	__getitem__(self, key):
		item = self.conn.execute(f'SELECT snt FROM "{self.tablename}" WHERE rowid = ? limit 1', (key,)).fetchone()
		return None if item	is None else item[0] 
	def get(self, key, defau=None): return self[key] if self.__contains__(key) else defau

	def	__delitem__(self, key): self.conn.execute('DELETE FROM	"%s" WHERE snt = ?'	% self.tablename,	(key,))
	def	__iter__(self): return self.keys()
	def	close(self): 	self.conn.commit()
	def	commit(self): 	self.conn.commit()
	def	snts_by_rowids(self, rowid_list): 	return list(self.conn.execute(f"select rowid, snt from {self.tablename} where rowid in ({rowid_list})"))

def hello():
	db =  Sntdb(":memory:") #"test.sidb")
	db.add(0, 'I overcome the problem.')
	db.add(1, 'I overcome the problems.')
	db.commit()
	print (list(db.snts()))
	print (list(db.items()))
	print ( db.snts_by_rowids("0,1"))
	db.close()

class SI(collections.Counter): 
	def __init__(self, dct_or_list={}): 	collections.Counter.__init__(self, dct_or_list) 
	incr = lambda self, *names, delta = 1: 	[self.update(collections.Counter({name: delta})) for name in names ] #si.incr('one', 'two')

class Sidb(collections.UserDict):  # key: str , value: int
	def	__init__(self, filename, tablename='si', keylen=128, vtype='int'):
		self.filename	= filename
		self.tablename	= tablename
		self.si			= SI() # sync-ed cache
		self.conn		= sqlite3.connect(self.filename, check_same_thread=False) 
		self.conn.execute(f'CREATE TABLE IF NOT EXISTS {self.tablename} (key varchar({keylen}) PRIMARY KEY, value {vtype})')
		self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=full,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''') #self.conn.execute('''CREATE VIRTUAL TABLE if not exists fts USING fts5(snt, terms, columnsize=0, detail=none,tokenize = "unicode61 remove_diacritics 0 tokenchars '-_'")''')
		self.conn.execute('PRAGMA synchronous=OFF')
		self.conn.commit()

	def index(self, snt, terms):  self.conn.execute(f"insert or ignore into fts(snt,terms) values(?,?)", (snt, terms if isinstance(terms, str) else ' '.join(terms))) # one,two,three
	def search(self, query, topn=10): list(self.conn.execute(f"SELECT rowid,* FROM fts where fts match 'overcome' order by rank limit {topn}"))
	def clear(self): (self.conn.execute(f'drop TABLE IF EXISTS {self.tablename}'), self.conn.execute(f'drop TABLE IF EXISTS fts'))

	def	__str__(self): 	return "SqliteDict(%s)"	% (self.filename)
	def	__repr__(self): return str(self)  #	no need	of something complex
	def	__len__(self):	return self.conn.execute('SELECT COUNT(*) FROM	"%s"' %	self.tablename).fetchone()[0]
	def	count(self):	return self.conn.execute('SELECT count(*) FROM "%s"'% self.tablename).fetchone()[0]

	def	keys(self, start=0, len=-1):  
		for key in self.conn.execute(f'SELECT key FROM {self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): yield key[0]
	def	values(self, start=0, len=-1): 
		for	value in self.conn.execute(f'SELECT value FROM {self.tablename} ORDER BY rowid  limit {start},{len}').fetchall(): yield value[0]
	def	items(self, start=0, len=-1): 
		for key, value in self.conn.execute(f'SELECT key, value FROM {self.tablename} ORDER BY rowid limit {start},{len}' ).fetchall(): 	yield key, value
	def	__contains__(self, key): return self.conn.execute('SELECT 1 FROM "%s" WHERE key = ?' %	self.tablename, (key,)).fetchone() is not None

	def	__getitem__(self, key):
		item = self.conn.execute(f'SELECT value FROM "{self.tablename}" WHERE key = ? limit 1', (key,)).fetchone()
		return None if item	is None else item[0] 
	def get(self, key, defau=None): return self[key] if self.__contains__(key) else defau
	def	__call__(self, key, topn=10): return self[key][0:topn] # ztop 

	def	__setitem__(self, key, value): 	self.conn.execute('REPLACE	INTO "%s" (key,	value) VALUES (?,?)' % self.tablename,	(key, value))
	def set(self, key, value): self[key] = value
	def	__delitem__(self, key): self.conn.execute('DELETE FROM	"%s" WHERE key = ?'	% self.tablename,	(key,))
	def	__iter__(self): return self.keys()
	def	close(self): 	self.conn.commit()
	def	commit(self): 	self.conn.commit()
	def	fetch(self, sql): 	return list(self.conn.execute(sql))
	def	sum(self, prefix="LEX"): 	return list(self.conn.execute(f"select sum(value) from si where key like '{prefix}:%'"))[0][0]
	
	def toredis(self, r, corpus):
		for k,v in self.items():
			arr = k.split(":")
			r.zadd( f"{corpus}:{':'.join(arr[0:-1])}" , {arr[-1]: v})
	def fromredis(self,r): pass

if __name__	== '__main__': 	hello()