# 2023.5.1  .# 2022-2-13  cp from cikuu/bin/es.py 
import so, requests,time,os

def add(infile, idxname="testdoc", taglist:str=None):
	''' add doc only , 2023.5.1 '''
	so.check(idxname)
	start = time.time()
	text = open(infile, 'r').read().strip() 
	did	 = so.md5(text)
	requests.es.index(index=idxname, body={"did": f"doc-{did}", "doc":text,  "filename": infile, 'type':'doc', 'tags':[] if taglist is None else taglist.strip().split(',') if isinstance(taglist, str) else taglist }, id = f"doc-{did}")
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

def addfolder(folder:str, idxname:str=None, pattern:str=".txt"): 
	''' folder -> esindex '''
	if idxname is None : idxname=  folder
	print("addfolder started:", folder, idxname, requests.es, flush=True)
	for root, dirs, files in os.walk(folder):
		for file in files: 
			if file.endswith(pattern):
				add(f"{folder}/{file}", idxname = idxname, taglist=folder) 
				print (f"{folder}/{file}", flush=True)
	print("addfolder finished:", folder, idxname, requests.es, flush=True)

def init(idxname):
	''' init a new index '''
	if requests.es.indices.exists(index=idxname):requests.es.indices.delete(index=idxname)
	requests.es.indices.create(index=idxname, body=so.config) #, body=snt_mapping
	print(">>finished " + idxname )

def drop(idxname): 
	''' drop a index ''' 
	print ( requests.es.indices.delete(index=idxname) )

if __name__ == '__main__':
	import fire
	fire.Fire()

'''

1. ubuntu@dicvec-scivec-jukuu-com-flair-64-245:~/cikuu/pypi/so$ python __main__.py addfolder inaugural
2. ubuntu@dicvec-scivec-jukuu-com-flair-64-245:~/cikuu/pypi/so$ python sntbr.py inaugural
58
sntbr indexing finished: inaugural, 	| using:  54.86855387687683

python sntbr.py inaugural --debug true --postag true

POST /policy_document/policy_document/222/_update
{
  "doc": {
    "tags":["VIP"]
  }
}

  es.update( # excpetion here 
            index=log['_index'],
            doc_type='_doc',
            id=log['_id'],
            body={'doc':log['_source']} # 
        )

ubuntu@dicvec-scivec-jukuu-com-flair-64-245:~/cikuu/pypi/so/inaugural$ find . -name "*.txt" -exec python ../__main__.py add {} --taglist inau \;
'''