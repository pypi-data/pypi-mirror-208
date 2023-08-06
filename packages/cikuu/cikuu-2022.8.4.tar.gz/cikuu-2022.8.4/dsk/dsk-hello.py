#  1. spacy   2. gec   3. dskmkf 
import json, time, traceback, fire,sys, os,requests, spacy, difflib, redis 

spacy.nlp	= spacy.load('en_core_web_sm')
redis.r		= redis.Redis(host="gpu120.wrask.com", port=6379, db=0, decode_responses=True) # or: 55, 6626

trans_diff		= lambda src, trg:  [] if src == trg else [s for s in difflib.ndiff(src, trg) if not s.startswith('?')] #src:list, trg:list
trans_diff_merge= lambda src, trg:  [] if src == trg else [s.strip() for s in "^".join([s for s in difflib.ndiff(src, trg) if not s.startswith('?')]).replace("^+","|+").split("^") if not s.startswith("+") ]
mkf_input		= lambda i, snt, gec, toklist, gec_toklist, doc, diffmerge,pid=0: 	{"pid":pid, "sid":i, "snt":snt, "tok": toklist,  #"offset":-1,"len":-1,"re_sntbr":0,  normally, offset =0
				"pos":[t.tag_ for t in doc], "dep": [t.dep_ for t in doc],"head":[t.head.i for t in doc],  #"tag":[t.tag_ for t in doc],
				"seg":[ ("NP", sp.start, sp.end) for sp in doc.noun_chunks] + [ (np.label_, np.start,np.end) for np in doc.ents] , 
				"gec": gec, "diff": trans_diff_merge( toklist , gec_toklist) if diffmerge else trans_diff( toklist , gec_toklist)	}

def get_dsk(essay:str="English is a internationaly language which becomes importantly for modern world. In China, English is took to be a foreigh language which many student choosed to learn. They begin to studying English at a early age. They use at least one hour to learn English knowledges a day. Even kids in kindergarten have begun learning simple words. That's a good phenomenan, for English is essential nowadays. In addition to, some people think English is superior than Chinese. In me opinion, though English is for great significance, but English is after all a foreign language. it is hard for people to see eye to eye. English do help us read English original works, but Chinese helps us learn a true China. Only by characters Chinese literature can send off its brilliance. Learning a country's culture, especial its classic culture, the first thing is learn its language. Because of we are Chinese, why do we give up our mother tongue and learn our owne culture through a foreign language?"	, dskhost:str="gpu120.wrask.com:7095"): 

	doc		= spacy.nlp(essay)
	snts	= [sp.text for sp in doc.sents ] 	

	id		= redis.r.xadd("xsnts", {'snts':json.dumps(snts)})
	res		= redis.r.blpop([f"suc:{id}",f"err:{id}"], timeout=5)
	sntdic	= json.loads(res[1])

	docs	= [ spacy.nlp(snt) for snt in snts ] 
	input	= [ mkf_input(i,snts[i],sntdic[snts[i]], [t.text for t in doc], [t.text for t in (doc if snts[i] == sntdic[snts[i]] else spacy.nlp(sntdic[snts[i]]) ) ], doc, False)  for i, doc in enumerate(docs)]
	dsk		= requests.post(f"http://{dskhost}/parser", data={"q":json.dumps({"snts":input, "rid":"10"} ).encode("utf-8")}).json()
	return dsk 	

if __name__ == '__main__':
	print ( get_dsk() )