# 2023.5.11, score the different paraphrase sent in the given essay,  NOT gec the current sent 
import gecdsk, requests

def para_vs( essay:str='The quick fox jumped over the lazy dog. She has ready.', snt: str='She has ready.', num:int=5, apihost:str="api.jukuu.com"):
	'''  '''
	res = [( snt, gecdsk.parse({"essay":essay}).get('info',{}).get('final_score',0) )]
	for row in requests.get(f"http://{apihost}/paraphrase",params={"snt":snt, "num_return_sequences":num}).json(): #[{"id":0,"snt":"She is prepared."},{"id":1,"snt":"Her readiness is complete."},{"id":2,"snt":"She has got it."},{"id":3,"snt":"She's prepared."},{"id":4,"snt":"Her preparation has been completed."}]
		try:
			txt = essay.replace(snt, row['snt'])
			dsk = gecdsk.parse({"essay":txt})
			res.append( ( row['snt'], dsk['info']['final_score'] ) )
		except Exception as ex:
			print(">>para_vs ex:", ex)
	return res 

if __name__ == '__main__': 	
	print (para_vs(num=4)) 