# 2022.6.30 cp from uvicorn corpusly-19200:app --host 0.0.0.0 --port 19200 --reload
from uvirun import *
from util import likelihood

@app.get('/auto/paraphrase', tags=["gpt2"])
def two_snts_are_paraphrase(snt0:str="I love you", snt1:str="I like you", host:str="172.17.0.1:8008"): 
	return requests.get(f"http://{host}/auto/paraphrase", params={"snt0":snt0,"snt1":snt1 }).json()

@app.get('/auto/nextword', tags=["gpt2"])
def nextword_of_given_sentence(snt:str ="I study English for the",topk:int=10, host:str="172.17.0.1:8008"): 
	return requests.get(f"http://{host}/auto/nextword", params={"snt":snt,"topk":topk }).json()

@app.get('/auto/autowrite', tags=["gpt2"])
def autowrite_next_parts_of_given_texts(snt:str="The world weather is becoming", maxlen:int=30, do_sample:bool=True, host:str="172.17.0.1:8008"): 
	return requests.get(f"http://{host}/auto/autowrite", params={"snt":snt,"maxlen":maxlen, "do_sample":do_sample }).json()

@app.get('/auto/nsp', tags=["gpt2"])
def next_sentence_predicator(snt0:str="I go to the shop .",snt1:str="I buy a book .", host:str="172.17.0.1:8008"): 
	return requests.get(f"http://{host}/auto/nsp", params={"snt0":snt0,"snt1":snt1 }).json()

@app.post('/gecdsk', tags=["dsk"])
def gec_dsk_wrapper(formula:dict={ "ast":[9.9, 11.99, 15.3, 18.51, 25.32,				2,0.0882, 0.3241],
			"awl":[3.5, 4.1, 4.56, 5.1, 6.0,					3,0.0882, 0.5],
			"b3":[0, 0.03, 0.08, 0.12, 0.15 ,					1, 0.0956, 0.2096],
			"cl_sum":[1, 6.68, 12, 16, 26,						2,0.0441, 0.1621],
			"grammar_correct_ri":[0.6, 0.85, 0.92, 0.97,1.0,	2,0.0368, 0.1352],
			"internal_sim":[0.0, 0.08, 0.4, 0.6, 0.8,			4, 0.0735, 0.7688], #"internal_sim":[0.0, 0.08, 0.2, 0.3, 0.4,			4, 0.0735, 0.7688],
			"kp_correct_ri":[0.7, 0.9, 0.95, 0.97, 1,			1, 0.0368, 0.0807],
			"mwe_pv":[0.01,8.03, 12, 20.21, 25,					4, 0.0221, 0.2312],
			"pred_diff_max3":[3.84, 5.11, 6.51, 7.9, 10.09 ,	1, 0.0368, 0.0807],
			"prmods_ratio":[0.06, 0.21, 0.3, 0.4, 0.5,			2, 0.0294, 0.108],
			"prmods_tc":[1.1, 2.76, 4.75, 6.76, 10.0,			2, 0.0368, 0.1352],
			"simple_sent_ri":[0.4, 0.65, 0.9, 0.95, 1,			2, 0.0368, 0.1352],
			"snt_correct_ratio":[0.1, 0.6, 0.8, 0.9, 1,		1, 0.0368, 0.0807], #"snt_correct_ratio":[0.01, 0.2, 0.45, 0.75, 1,		1, 0.0368, 0.0807],
			"spell_correct_ratio":[0.8, 0.9, 0.97, 0.99, 1,		1, 0.1471, 0.3226],
			"ttr1":[3.43, 4.28, 5.2, 6, 6.8,					3, 0.0882, 0.5],
			"word_diff_avg":[4.47, 4.73, 5.25,5.8, 6.6,			1, 0.0441, 0.0967],
			"word_gt7":[0.11, 0.19, 0.3, 0.42, 0.49,			1, 0.0588, 0.1289]} , 
			essay_or_snts:str="She has ready. It are ok. I think it is right.",timeout:int=9, use_gec:bool=True, topk_gec:int=64,  internal_sim_default:float=0.2, #rescore:bool=False, 
			rhost:str=None, gechost:str='gpu120.wrask.com:6379', dskhost:str='gpu120.wrask.com:7095', with_dim_score:bool=False, host:str="hw6.jukuu.com:7000"):
	return requests.post(f"http://{host}/gecdsk", json=formula, params={"essay_or_snts":essay_or_snts, "timeout":timeout, "use_gec":use_gec, "topk_gec":topk_gec,"internal_sim_default":internal_sim_default,
		"rhost":rhost, 'gechost':gechost, 'dskhost':dskhost, 'with_dim_score':with_dim_score}).json()

@app.get("/style")
def style(snt:str="I am quitting my job.",  inference_on:int=-1, quality_filter:float=0.95, max_candidates:int=5, host:str="172.17.0.1:8005"):
	''' docker run -d --restart=always --name style -p 8005:80  wrask/style uvicorn style-fastapi:app --port 80 --host 0.0.0.0 '''
	return requests.get(f"http://{host}/styleformer/casual_formal_snt", params={"snt":snt,"inference_on":inference_on, "quality_filter":quality_filter, "max_candidates":max_candidates }).json()

@app.get("/parrot")
def parrot(snt:str="I'm glad to meet you.", use_gpu:bool=False, diversity_ranker:str="euclidean",do_diverse:bool=False, max_return_phrases:int=10, max_length:int=32,adequacy_threshold:float=0.9, fluency_threshold:float=0.9,  host:str="172.17.0.1:8006"):
	''' docker run -d --restart=always --name parrot -p 8006:80 wrask/parrot uvicorn parrot-fastapi:app --port 80 --host 0.0.0.0 '''
	return requests.get(f"http://{host}/parrot/snt", params={"snt":snt, "use_gpu":use_gpu, "diversity_ranker":diversity_ranker, "do_diverse":do_diverse, "max_return_phrases":max_return_phrases, "max_length":max_length, "adequacy_threshold":adequacy_threshold,"fluency_threshold":fluency_threshold }).json()

@app.post("/dskjava")
def dskjava(arr:dict={"q": "{'snts': [{'dep': ['nsubj', 'ROOT', 'acomp', 'punct'],'head': [1, 1, 1, 1],'pid': 0,'pos': ['PRP', 'VBZ', 'JJ', '.'],'seg': [['NP', 0, 1]],'sid': 0,'snt': 'It is OK .','tok': ['It', 'is', 'OK', '.'],'gec': 'It is OK .','diff': []}]}"}, dskhost:str='192.168.201.120:7095'):
	''' dsk 7095 , added 2022.9.7 '''
	return requests.post(f"http://{dskhost}/parser", data=arr).json()

@app.post('/util/dualarr_keyness')
def dualarr_keyness(src:dict={"one":2, "two":12}, tgt:dict={"three":3, "one":1}, sum1:float=None, sum2:float=None, threshold:float=0.0, leftonly:bool=False): 
	'''  "src": {"one":2, "two":12}, "tgt": {"three":3, "one":1}, added 2021.10.24  '''
	if not sum1: sum1 = sum([i for s,i in src.items()])
	if not sum2: sum2 = sum([i for s,i in tgt.items()])
	if not sum1: sum1 = 0.0001
	if not sum2: sum2 = 0.0001
	words = set(src.keys()) | set(tgt.keys()) if not leftonly else set(src.keys())
	res  = [(w, src.get(w,0), tgt.get(w,0), sum1, sum2, likelihood(src.get(w,0.01), tgt.get(w,0.01), sum1, sum2))  for w in words]
	res.sort(key=lambda a:a[-1], reverse=True)
	return [ar for ar in res if abs(ar[-1]) > threshold ]

@app.get('/dic/wordattr')
def dic_wordattr(w:str='consider'): 
	from dic import wordattr
	return wordattr.wordattr.get(w, {})

@app.get('/cola')
def cola_get(snt:str='I love you.', host:str="172.17.0.1:8003"): 
	return requests.get(f"http://{host}/cola", params={"snt":snt}).json()
@app.post('/cola/snts')
def cola_snts(snts:list=["I love you.", "I like you."], host:str="172.17.0.1:8003", multiply:int=100, asrows:bool=True,asdic:bool=True): 
	res = requests.post(f"http://{host}/cola/snts", json=snts, params={"multiply":multiply, "asrows":asrows}).json() 
	return dict(res) if asdic else res

@app.get('/cola/single')
def cola_single(body:str="Parents * much importance to education.", options:str="pay,link,attach,apply", sepa:str=',', host:str="172.17.0.1:8003",asdic:bool=False): 
	res = requests.post(f"http://{host}/cola/snts", json=[body.replace('*', s) for s in options.strip().split(sepa)], params={"multiply":100, "asrows":True}).json() 
	return dict(res) if asdic else [{"snt":s, "score": i} for s,i in res]	

@app.get('/essays')
def dic_docs(name:str='hello'): 
	''' src data in pypi/dic/__init__.py '''
	import dic 
	return dic.docs(name) 

four_int = lambda four, denom=100: [int( int(a)/denom) for a in four]
xy = lambda four : [f"{a},{b}" for a in range(four[0], four[2]+2) for b in range( four[1], four[3] + 2) ] # xy_to_item
@app.post('/penly/xy_to_item')
def penly_xy_to_items(arr:list=[[2500,2960,3000,3160,"select-11:C"],[3500,2960,3700,3160,"select-11:D"]], denom:int=100): 
	''' submit data into the permanent store, updated 2021.10.8 '''
	return {k:tag for x1,y1,x2,y2,tag in arr for k in xy( ( int(x1/denom), int(y1/denom), int(x2/denom), int(y2/denom)) ) }

@app.post('/sent/diff')
def sentdiff(snts:list, refs:list):
	import textdistance
	from nltk.tokenize import TreebankWordTokenizer
	if not hasattr(sentdiff, 'tokenizer'):
		sentdiff.tokenizer = TreebankWordTokenizer()
		sentdiff.hamming = textdistance.Hamming(external=False)

	score = 0
	for s in snts:
		for rs in refs:
			src_toks = sentdiff.tokenizer.tokenize(s)
			ref_toks = sentdiff.tokenizer.tokenize(rs)
			edits = sentdiff.hamming(src_toks, ref_toks)
			is_same = True if (1 - round(edits / len(ref_toks), 2))==1.0 else False
			if not is_same:
				continue
			score = 100
			break
				
	return {"code": 100, "score": score,"msg": "OK"}

if __name__ == "__main__":  
	print (dualarr_keyness())
	uvicorn.run(app, host='0.0.0.0', port=80)

'''

@app.get('/dsk/annotate', tags=["dsk"])
def dsk_annotate(text:str='The quick fox jumped over the lazy dog.', cates:str='e_snt.nv_agree,e_spell'): 
	# 2022.7.27 night 
	from dsk_fastapi import dsk_wrapper
	cates = cates.strip().split(',') 
	dsk = dsk_wrapper(text ) 
	tokens = []
	for ar in dsk['snt']:
		for mkf in ar:
			arrlex = mkf.get("meta",{}).get("lex_list",'').split()
			si = {}
			for k,v in mkf.get('feedback',{}).items(): 
				si[ v['ibeg'] ] = v['cate']
			tokens.extend( [ {'text': w} if not i in si else {'text': t.text, "labels":[si[i]]} for i, w in enumerate(arrlex) ] )
	
	return {"tokens": tokens,"labels": [ {"text": cate} for cate in cates] }
'''