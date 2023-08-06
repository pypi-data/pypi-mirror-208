# 2023.5.3,  loading 230537 essays to dis: dsk/info/spacy 
import time, fire,json, spacy, gecdsk

def run(outfile, debug:bool=False, model:str='lg'):
	''' write essays parsed result to outfile, ie: essays-dis.jsonl '''
	from dic import essays
	nlp = spacy.load(f'en_core_web_{model}') # sm
	start = time.time()
	with open(outfile, 'w') as fw : 
		for i, ess in enumerate(essays.essays):
			print ( i, flush=True)
			essay = ess['essay'] 
			doc = nlp(essay)
			dsk = gecdsk.parse({"essay":essay})
			arr = {'info':ess, 'dsk': dsk, 'spacy': doc.to_json()}
			fw.write(json.dumps(arr) + "\n")
 
	print(f"finished: {outfile}, \t| using: ", time.time() - start) 

if __name__ == '__main__': 	
	fire.Fire(run)