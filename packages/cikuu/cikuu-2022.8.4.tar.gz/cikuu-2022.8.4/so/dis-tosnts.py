# 2023.5.9, spacy -> snts , a temp patcher 
import requests,time, fire,json, spacy, fileinput ,traceback,sys

def run(infile, outfile:str=None, model:str="en_core_web_lg", debug:bool=False,):
	'''  '''
	nlp = spacy.load(model)
	start = time.time()
	with open(outfile if outfile is not None else infile.split('.')[0] + ".snts-dis", 'w') as fw : 
		for i, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				arr = json.loads(line.strip()) # dis
				info, dsk, spa = arr['info'], arr.get('dsk',{}), arr['spacy'] 
				doc = spacy.tokens.Doc(nlp.vocab).from_json( spa )
				snts = [sp.as_doc().to_json() for sp in doc.sents ] # docs
				fw.write(json.dumps({'info':info, 'dsk': dsk, 'snts': snts }) + "\n")
			except Exception as e:
				print("ex:", e)	
				exc_type, exc_value, exc_traceback_obj = sys.exc_info()
				traceback.print_tb(exc_traceback_obj)

	print(f"indexing finished: {infile}, \t| using: ", time.time() - start) 

if __name__ == '__main__': 	
	fire.Fire(run)