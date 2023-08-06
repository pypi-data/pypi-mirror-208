# 2023.3.18, 
import json, traceback,sys, time, fire,os,traceback,fileinput,en

def run(infile, topk:int=2, outfile:str=None):
	'''  '''
	name = infile.split('.jsonlg')[0] 
	if outfile is None: outfile = name + f".{topk}"
	start = time.time()
	print ("started:", infile ,  flush=True)
	with open(outfile, 'w') as fw: 
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)):  
			if sid >= topk: break
			fw.write(f"{line}")
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

if __name__	== '__main__':
	fire.Fire(run)
