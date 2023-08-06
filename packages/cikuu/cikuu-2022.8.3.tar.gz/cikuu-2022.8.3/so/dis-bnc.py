# 2023.5.11  
import requests,time, fire,json, spacy,fileinput,gecdsk # so 

def run(infile, outfile:str=None, content:str='doc', debug:bool=False, model:str='lg'):
	''' bnc.jsonl -> bnc.dis-jsonl '''
	nlp = spacy.load(f'en_core_web_{model}') # sm
	start = time.time()
	with open(outfile if outfile is not None else infile.split('.')[0] + ".dis-jsonl", 'w') as fw : 
		for i, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			if i % 100 == 0: print (f"[dis-eev] {infile}:\t", i, flush=True)
			arr = json.loads(line) 
			if arr[content] is None: continue # :null => None
			essay = arr[content] 
			doc = nlp(essay.strip())
			snts = [sp.as_doc().to_json() for sp in  doc.sents ] # docs
			fw.write(json.dumps({'info':arr, 'dsk': {}, 'snts': snts }) + "\n")
	print(f"dis-bnc finished: {infile}, \t| using: ", time.time() - start) 

if __name__ == '__main__':
	fire.Fire(run)