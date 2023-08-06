# 2023.5.5,  
import requests,time, fire,json, spacy,fileinput,gecdsk # so 

def run(infile, outfile:str=None, debug:bool=False, model:str='lg'):
	''' nju2020.txt -> nju2020-dis.jsonl '''
	nlp = spacy.load(f'en_core_web_{model}') # sm
	start = time.time()
	with open(outfile if outfile is not None else infile.split('.')[0] + ".dis-jsonl", 'w') as fw : 
		for i, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			if i % 100 == 0: print (f"[dis-eev] {infile}:\t", i, flush=True)
			arr = json.loads(line.replace('"essay_id"','"eid"').replace('"request_id"','"rid"').replace('"user_id"','"uid"') ) 
			if arr['essay'] is None: continue # :null => None
			essay = arr['essay'] 
			doc = nlp(essay.strip())
			dsk = gecdsk.parse({"essay":essay})
			snts = [sp.as_doc().to_json() for sp in doc.sents ] # docs
			fw.write(json.dumps({'info':arr, 'dsk': dsk, 'snts': snts }) + "\n")
			#fw.write(json.dumps({'info':arr, 'dsk': dsk, 'spacy': doc.to_json()}) + "\n")
	print(f"finished: {infile}, \t| using: ", time.time() - start) 

if __name__ == '__main__': 	#run('testdoc', debug=True)
	fire.Fire(run)

'''
ubuntu@dicvec-scivec-jukuu-com-flair-64-245:/data/cikuu/pypi/so$ nohup python dis-eev.py nju.2023.jsonl.gz & 
[1] 4058090
'''