#!/usr/bin/env python 2022.12.18 cp from cikuu/bin/uniq-to-sqlsi.py  | 2023.2.2 add chksi 
import fire,json, fileinput, traceback,sqlite3, gzip ,time

class util(object):
	def __init__(self): pass

	def dumpgz(self, infile, outfile, table="si"):
		''' dump si table to gz file '''
		conn =	sqlite3.connect(infile, check_same_thread=False) 
		print("started:", infile,  flush=True)
		with gzip.open(outfile, 'wt', compresslevel=5) as f: 
			for row in conn.execute("select * from {table}"): 
				f.write(f"{row[0]}\t{row[1]}\n")
		print("finished:", infile)

	def loadsi(self, infile, sqlite, batch=10000000):
		''' load the existing si file, merge to si table '''
		conn =	sqlite3.connect(sqlite, check_same_thread=False) 
		conn.execute(f"create table if not exists si( s varchar(128) not null primary key, i int not null default 0) without rowid")
		conn.execute('PRAGMA synchronous=OFF')
		conn.execute('PRAGMA case_sensitive_like = 1')
		conn.commit()

		print("started:", infile, conn , flush=True)
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				if not isinstance(line, str): line = bytes.decode(line) # bytes 
				arr = line.strip().split("\t")
				if len(arr) != 2 : continue
				conn.execute(f"INSERT INTO si(s,i) VALUES(?,?) ON CONFLICT(s) DO UPDATE SET i = i + {cnt}", (arr[0],arr[1]))
				if (sid) % batch == 0 : 
					print (f"[{sqlite}] sid = {sid}, \t| {line} ", flush=True)
					conn.commit()
			except Exception as e:
				print ("ex:", e, "\t|", line) 
		conn.commit()
		print("finished:", infile)

	def loaduniq(self, infile, sqlite, batch=10000000):
		''' c4gram uniq result to sqlite3, initially normally '''
		conn =	sqlite3.connect(sqlite, check_same_thread=False) 
		#conn.execute(f'DROP TABLE if exists si')
		conn.execute(f"create table if not exists si( s varchar(128) not null primary key, i int not null default 0) without rowid")
		conn.execute('PRAGMA synchronous=OFF')
		conn.execute('PRAGMA case_sensitive_like = 1')
		conn.commit()

		print("started:", infile, conn , flush=True)
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				if not isinstance(line, str): line = bytes.decode(line) # bytes 
				line = line.strip()
				idx = line.find(' ') 
				if idx < 0: continue
				cnt = int(line[0:idx])
				gram = line[idx+1:].strip()
				if not gram or gram > 'zzzzzz': continue #insert or ignore into si(s,i) values(?,?)
				#conn.execute(f'''INSERT INTO si(s,i) VALUES('{gram.replace("'", "''")}', {cnt})  ON CONFLICT(s) DO UPDATE SET i = i + {cnt}''')
				conn.execute(f"INSERT INTO si(s,i) VALUES(?,?) ON CONFLICT(s) DO UPDATE SET i = i + {cnt}", (gram, cnt))
				if (sid) % batch == 0 : 
					print (f"[{sqlite}] sid = {sid}, \t| {line} ", flush=True)
					conn.commit()
			except Exception as e:
				print ("ex:", e, "\t|", line) 

		conn.commit()
		print("finished:", infile)

	def merge(self, src, dst:str='dst.si', batch:int=1000000):
		''' merge src-si to dst-si ''' 
		if dst is None: dst = src.strip('.').split(".")[0].strip('/') + ".dst.sqlsi"
		conn_dst =	sqlite3.connect(dst, check_same_thread=False) 
		conn_dst.execute(f"create table if not exists si( s varchar(64) not null primary key, i int not null default 0) without rowid")
		conn_dst.execute('PRAGMA synchronous=OFF')
		conn_dst.execute('PRAGMA case_sensitive_like = 1')
		conn_dst.commit()

		conn_src =	sqlite3.connect(src, check_same_thread=False) 
		print("started:", src, dst , flush=True)
		start = time.time() 
		for sid, row in enumerate(conn_src.execute("select * from si")): 
			try:
				s,i = row
				conn_dst.execute(f"INSERT INTO si(s,i) VALUES(?,?) ON CONFLICT(s) DO UPDATE SET i = i + {i}", row)
				if (sid) % batch == 0 : 
					print (f"[{src} -> {tgt}] sid = {sid}, \t| {row} \t", round(time.time() - start,1), flush=True)
					conn_dst.commit()
			except Exception as e:
				print ("ex:", e, "\t|", sid, row) 
		conn_dst.commit()
		print("finished:", src, dst, flush=True)

	def chksi(self, infile, name, host='files.jukuu.com', port=3309, db:str='nac'):
		''' name is table name, 2023.2.2 '''
		import pymysql 
		from dic.lex_lemma import lex_lemma
		start = time.time()
		my_conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db=db)
		print ("started:", infile , my_conn, host, name,  flush=True)
		with my_conn.cursor() as cursor: #cursor.execute(f"drop table if exists {name}")
			cursor.execute(f"create table if not exists {name} (`name` varchar(64) NOT NULL, `attr` varchar(128) NOT NULL, `count` int(11) NOT NULL DEFAULT 0,  PRIMARY KEY (`name`,`attr`)) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_bin")

			def add(k,n,c): cursor.execute(f"INSERT ignore INTO {name}(name, attr, count) VALUES (%s,%s,%s)", (k, n, c))
			conn =	sqlite3.connect(infile, check_same_thread=False) 
			for s,i in conn.execute("select * from si where s like 'pn:%'"): #pn:into force|29
				lem = s.strip().split(' ')[-1]
				tag = s.split(":")[0]
				add(f"{lem}:NOUN:{tag}", s.split(":")[-1], i)
			for s,i in conn.execute("select * from si where s like 'vpn:%'"): #vpn:come into force|29
				arr = s.strip().replace(":"," ").split(" ")
				if len(arr) == 4:
					add(f"{arr[3]}:NOUN:{arr[0]}", s.split(":")[-1], i)
					add(f"{arr[1]}:VERB:{arr[0]}", s.split(":")[-1], i)
			for s,i in conn.execute("select * from si where s like 'vnp:%'"): # make use of
				arr = s.strip().replace(":"," ").split(" ")
				if len(arr) == 4:
					add(f"{arr[2]}:NOUN:{arr[0]}", s.split(":")[-1], i)
					add(f"{arr[1]}:VERB:{arr[0]}", s.split(":")[-1], i)
			for s,i in conn.execute("select * from si where s like 'vp:%'"): # abide by
				arr = s.strip().replace(":"," ").split(" ")
				if len(arr) == 3: add(f"{arr[1]}:VERB:{arr[0]}", s.split(":")[-1], i)
			for s,i in conn.execute("select * from si where s like 'vnpn:%' or s like 'vppn:%' or s like 'vpp:%' or s like 'vop:%'"): 
				arr = s.strip().replace(":"," ").split(" ")
				add(f"{arr[1]}:VERB:{arr[0]}", s.split(":")[-1], i)
			for s,i in conn.execute("select * from si where s like 'bvp:%'"):
				arr = s.strip().replace(":"," ").split(" ")
				add(f"{lex_lemma.get(arr[2],arr[2])}:ADJ:{arr[0]}", s.split(":")[-1], i) # forced => force
			for s,i in conn.execute("select * from si where s like 'bap:%' or s like 'bapv:%'"):
				arr = s.strip().replace(":"," ").split(" ")
				add(f"{arr[2]}:ADJ:{arr[0]}", s.split(":")[-1], i) 
			for s,i in conn.execute("select * from si where s like 'pnp:%'"):
				arr = s.strip().replace(":"," ").split(" ")
				add(f"{arr[2]}:NOUN:{arr[0]}", s.split(":")[-1], i) 

			my_conn.commit()
		print(f"{infile} is finished, \t| using: ", time.time() - start)

if __name__ == '__main__':
	fire.Fire(util)