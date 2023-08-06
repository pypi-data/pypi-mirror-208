# 2023.5.4   docker run -d --name redis-stack-server -p 6380:6379 -v /data/redis-stack-sntvec:/data redis/redis-stack-server:latest  
import json,os,time, platform,requests,math,re, redis,sys,traceback,random,fileinput,fire,hashlib
import numpy as np 
import __init__ 
md5	= lambda text: hashlib.md5(text.strip().encode("utf-8")).hexdigest()

def run(infile, rhost:str='172.17.0.1', rport=6380):
	r =redis.Redis(rhost,port= rport, decode_responses=True)
	for i, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
		if i % 100 == 0: print (i, flush=True)
		vec = json.vec_encode(line.strip())
		vector = np.array(vec).astype(np.float32).tobytes()
		r.hset(name=f"sntvec:{md5(line)}", mapping={"snt": line.strip(), "vec": vector   })

	r.save() 
	print ("finished: ", infile ) 


if __name__ == '__main__':
	fire.Fire(run)