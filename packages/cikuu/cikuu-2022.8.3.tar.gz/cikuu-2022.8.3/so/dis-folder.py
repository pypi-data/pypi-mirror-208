# 2023.5.5,  loading inau 
import requests,time, fire,json, spacy, gecdsk
from __init__ import *  # for debug , change to : from so import * 

def run(folder, debug:bool=False, model:str='lg', dsk:bool = False):
	''' inau-dis.jsonl '''
	nlp = spacy.load(f'en_core_web_{model}') # sm
	start = time.time()
	with open(f"{folder}-dis.jsonl", 'w') as fw : 
		for filename, content in walkfolder(folder, ".txt"): 
			print ( filename, flush=True)
			doc = nlp(content)
			snts = [ sp.text.strip() for sp in doc.sents if sp.text.strip()]
			arr = {'info':{"filename":filename, "doc":content, "folder":folder, "sntnum":len(snts), "snts": snts, "wordnum": len(doc)}, 'dsk': gecdsk.parse({"essay":content}) if dsk else {}, 'spacy': doc.to_json()}
			fw.write(json.dumps(arr) + "\n")
	print(f"finished: {folder}, \t| using: ", time.time() - start) 

if __name__ == '__main__': 	#run('testdoc', debug=True)
	fire.Fire(run)