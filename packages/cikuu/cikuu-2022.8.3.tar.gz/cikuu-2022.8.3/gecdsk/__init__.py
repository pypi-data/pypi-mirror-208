# 2023.4.30, move to pypi/gecdsk/__init__.py
# 2023.4.29 cp from wps7000.py  as a MQ consumer later 
import json, time, traceback, fire,sys, redis, platform,os,requests,re, difflib, spacy # 3.4.1 needed
#redis.r	= redis.Redis(host=os.getenv('rhost', "172.17.0.1" if 'linux' in sys.platform else 'hw160.jukuu.com' ), port=int( os.getenv('rport', 6626 ) ), decode_responses=True) # local cache only , no gec included
gechost = os.getenv('gechost', 'gpu120.wrask.com:7626') # HTTP api, on top of redis6626, xadd-blpop 
dskhost	= os.getenv('dskhost', "gpu120.wrask.com:7095") #gpu120.wrask.com:7095
getdoc	= lambda snt, ttl=37200:  ( res := redis.r.get(snt) if hasattr(redis,'r') else None, doc:= spacy.nlp(snt) if res is None else spacy.tokens.Doc(spacy.nlp.vocab).from_json(json.loads(res) ),  redis.r.setex(f"snt:{snt}", ttl, json.dumps(doc.to_json()) ) if hasattr(redis, 'r') and res is None else None ) [1]
getdocs	= lambda snts, ttl=37200: [ ( doc:=spacy.nlp(snt), redis.r.setex(f"snt:{snt}", ttl, json.dumps(doc.to_json()) ) if hasattr(redis,'r') else None, doc )[-1] if res is None else  spacy.tokens.Doc(spacy.nlp.vocab).from_json(json.loads(res) ) for snt, res in zip(snts, redis.r.mget([f"snt:{snt}" for snt in snts]) if hasattr(redis,'r') else [None] * len(snts) ) ]
trans_diff		= lambda src, trg:  [] if src == trg else [s for s in difflib.ndiff(src, trg) if not s.startswith('?')] #src:list, trg:list
trans_diff_merge= lambda src, trg:  [] if src == trg else [s.strip() for s in "^".join([s for s in difflib.ndiff(src, trg) if not s.startswith('?')]).replace("^+","|+").split("^") if not s.startswith("+") ]
mkf_input		= lambda i, snt, gec, toklist, gec_toklist, doc, diffmerge,pid=0: 	{"pid":pid, "sid":i, "snt":snt, "tok": toklist,  #"offset":-1,"len":-1,"re_sntbr":0,  normally, offset =0
				"pos":[t.tag_ for t in doc], "dep": [t.dep_ for t in doc],"head":[t.head.i for t in doc],  #"tag":[t.tag_ for t in doc],
				"seg":[ ("NP", sp.start, sp.end) for sp in doc.noun_chunks] + [ (np.label_, np.start,np.end) for np in doc.ents] , 
				"gec": gec, "diff": trans_diff_merge( toklist , gec_toklist) if diffmerge else trans_diff( toklist , gec_toklist)	}

if not hasattr(spacy, 'nlp'):
	from spacy.lang import en
	spacy.sntbr		= (inst := en.English(), inst.add_pipe("sentencizer"))[0]
	spacy.sntpid	= lambda essay: (pid:=0, [ ( pid := pid + 1 if "\n" in snt.text else pid,  (snt.text, pid))[-1] for snt in  spacy.sntbr(essay).sents] )[-1]
	spacy.nlp		= spacy.load('en_core_web_sm')

def parse(arr:dict={"essay":"English is a internationaly language which becomes importantly for modern world. In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays. In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"}
		, asdsk:bool=True, use_gec:bool=True, topk_gec:int=64, diffmerge:bool=False,  timeout:int=9, ttl:int=79200):  
	''' # 依赖 dskhost 和 gechost	'''
	try:
		essay	= arr.get("essay", arr.get('doc','')).strip() if isinstance(arr, dict) else arr # arr is dict/str 
		if not essay: return {"failed":"empty essay"}
		sntpids = spacy.sntpid(essay)  # [(snt,pid) ]
		snts	= [snt.strip() for snt,pid in sntpids ] 	
		if hasattr(redis, 'r') : [redis.r.xadd('xsnt-spacy', {'snt':snt}, maxlen=30000) for snt in snts if snt]  # notify:  spacy/gec , added maxlen 2022.10.15

		sntdic	= requests.post(f"http://{gechost}/xgec-snts?name=xsnts&timeout={timeout}&ttl={ttl}", json=snts).json() if use_gec else {}
		docs	= getdocs(snts, ttl) 
		input	= [ mkf_input(i,snts[i],sntdic[snts[i]], [t.text for t in doc], [t.text for t in (doc if snts[i] == sntdic.get(snts[i],snts[i]) else getdoc(sntdic.get(snts[i],snts[i])) ) ], doc, diffmerge)  for i, doc in enumerate(docs)]
		dsk		= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} if asdsk else input).encode("utf-8")}).json()
		return dsk
	except Exception as ex:
		print(">>parse_dsk Ex:", ex, "\t|", arr)

if __name__ == '__main__':
	print( parse()['doc'])  

'''
getdoc	= lambda snt, ttl=37200:  ( res := redis.r.get(snt), doc:= spacy.nlp(snt) if res is None else spacy.tokens.Doc(spacy.nlp.vocab).from_json(json.loads(res) ),  redis.r.setex(f"snt:{snt}", ttl, json.dumps(doc.to_json()) ) if res is None else None ) [1]

		exc_type, exc_value, exc_traceback_obj = sys.exc_info()
		traceback.print_tb(exc_traceback_obj)

def getdoc(snt, ttl=37200):
	if hasattr(redis, 'r')
		res = redis.r.get(snt)
		if res is not None:  return spacy.tokens.Doc(spacy.nlp.vocab).from_json(json.loads(res))
	doc = spacy.nlp(snt)
	if hasattr(redis, 'r'):  redis.r.setex(f"snt:{snt}", ttl, json.dumps(doc.to_json()) )
	return doc 

{'v_ttr': 0.44117647, 'x_len': 2.0, 'external_sim': 0.0, 'prmods_ratio': 0.33678368, 'pred_diff_avg': 5.023333, 'b0': 0.02, 'mwe_pvd': 0.9230769, 'b1': 0.84, 'n_num': 45.0, 'd_ratio': 0.053475935, 'flesch_reading_ease': 25.492226, 'b2': 0.04, 'b3': 0.1, 'score': 69.63337, 'b4': 0.07, 'sub_tc': 5.076923, 'internal_sim': 0.38714814, 'simple_sent_ri': 0.7368421, 'd_len': 4.8, 'psmods_ratio': 0.58954406, 'gramv_vxp': 7.0, 'r_type': 7.0, 'h_ttr2': 0.4090909, 'gramv': 10.0, 'h_ttr1': 0.45226702, 'd_type': 10.0, 'incomplete_ratio': 0.0, 'lex_num': 191.0, 'prprn_type': 0.0, 'prmods_tc': 5.076923, 'subcl_num': 0.0, 'gramv_vov': 2.0, 'a_num': 36.0, 'lemma_num': 187.0, 'snt_max': 24.0, 'token_num': 187.0, 'para_last_tratio': 0.0, 'lttr': 54.010696, 'c_num': 3.0, 'p_ratio': 0.11764706, 'comma_ratio': 0.04709576, 'doc_tc': 191.0, 'p_type': 10.0, 'd_ttr': 1.0, 'word_diff_avg': 5.0500007, 'grammar_correct_ri': 0.84269667, 'snt_min': 10.0, 'ast_sd': 4.5347657, 'word_type': 100.0, 'ttr1': 5.504819, 'r_num': 13.0, 'grammar_err': 5.6000004, 'infcl_num': 0.0, 'n_type': 28.0, 'spell_err': 5.0, 'lex_type': 107.0, 'gramv_vxxp': 1.0, 'prmods_tc_new': 5.076923, 'h_type': 3.0, 'h_len': 1.0, 'token_devia_ratio': 0.0, 'snt_correct_ratio': 0.8199328, 'prmods_ratio_new': 0.33678368, 'the_ratio': 0.005232862, 'para_first_tratio': 1.0, 'p_num': 22.0, 'a_ratio': 0.19251336, 'p_ttr2': 4.5454545, 'cate': 0.0, 'p_ttr1': 1.5075567, 'v_ttr2': 6.617647, 'psmods_tc': 8.615385, 'v_ttr1': 1.8190172, 'kp_err': 36.0, 'word_num': 165.0, 'v_len': 3.5588236, 'complex_max': 0.0, 'simple_sent_num': 5.0, 'a_ttr2': 16.0, 'score_kpu': 0.0, 'ast_new': 14.692307, 'a_ttr1': 2.828427, 'para_num': 1.0, 'snt_tc_30_39': 0.0, 'complex_factor': 0.0, 'h_ratio': 0.11764706, 'x_ttr': 1.0, 'd_ttr2': 10.0, 'm_len': 3.0, 'd_ttr1': 2.236068, 'snt_num': 13.0, 'kw_overlap': 0.0, 'cl_ratio': 0.0, 'mwe_pv': 12.0, 'snt_tc_40_': 0.0, 'prprtcl_num': 0.0, 'kp_correct_ri': 0.5813953, 'asl': 74.61539, 'cl_sum': 0.0, 'h_ttr': 0.13636364, 'awl_sd': 2.5038323, 'word_gt7': 0.26999998, 'b3_b1': 0.12941177, 'word_gt6': 0.32999998, 'word_gt9': 0.08, 'prprn_num': 0.0, 'ast': 14.692307, 'word_gt8': 0.16, 'whcl_num': 0.0, 'n_ratio': 0.24064171, 'd_num': 10.0, 'cjk_ratio': 0.0, 'p_len': 2.909091, 'cl_type': 0.0, 'v_num': 34.0, 'n_ttr1': 2.9514592, 'x_type': 1.0, 'n_ttr2': 17.422222, 'a_ttr': 0.6666667, 'atl': 4.1604276, 'm_num': 1.0, 'n_ttr': 0.62222224, 'doc_strlen': 0.0, 'fitted_num': 0.0, 'c_len': 3.0, 'punct_err': 0.0, 'lemma_type': 101.0, 'atl_sd': 2.6204197, 'dirtyword': 0.0, 'v_type': 15.0, 'a_type': 24.0, 'v_ratio': 0.18181819, 'ptprtcl_num': 0.0, 'pinyin_ratio': 0.11515152, 'a_len': 4.4722223, 'ttr2': 60.60606, 'c_ratio': 0.01604278, 'c_ttr': 0.6666667, 'r_len': 2.6923077, 'c_ttr1': 0.8164966, 'c_ttr2': 1.3333334, 'm_type': 1.0, 'mwe_disconj': 1.1538461, 'para_first_sratio': 1.0, 'compcl_num': 0.0, 'para_token_avg': 191.0, 'h_num': 22.0, 'sc_num': 0.0, 'snt_tc_10_19': 0.8396946, 'token_type': 103.0, 'snt_tc_0_9': 0.0, 'x_ttr1': 0.70710677, 'x_ttr2': 1.0, 'modifier_np': 0.0, 'mwe_pv_ratio': 0.06282722, 'dot_ratio': 0.06279435, 'r_ttr2': 3.7692308, 'r_ttr1': 1.372813, 'r_ttr': 0.53846157, 'b0_num': 2.0, 'mwe_pronaux': 0.0, 'snt_tc_20_29': 0.15267175, 'fitted_ratio': 0.0, 'gramv_idf': 16.41037, 'pinyin_num': 19.0, 'flesch_kincaid_grade_level': 6.5169697, 'spell_correct_ratio': 0.95049506, 'para_last_sratio': 0.0, 'r_ratio': 0.069518715, 'para_snt_avg': 13.0, 'ttr': 60.60606, 'p_ttr': 0.45454547, 'pred_diff_max1': 6.5, 'pred_diff_max2': 6.49, 'relcl_num': 0.0, 'awl': 4.581818, 'pred_diff_max3': 6.343333, 'c_type': 2.0, 'content_word_ratio': 0.0, 'x_num': 1.0, 'x_ratio': 0.0053475937, 'word_diff_num': 97.0, 'incomplete_num': 0.0, 'gramv_ratio': 0.29325515, 'n_len': 6.6, 'b1_bu': 0.16000003}
'''