#2023.4.30  import redisr 
import json,os,time, platform,requests,math,re, redis,sys,traceback,random
from collections import Counter,defaultdict
from functools import lru_cache

if not hasattr(redis, 'r'): 
	redis.r		= redis.Redis(host=os.getenv('rhost', '172.17.0.1' if 'linux' in sys.platform else 'data.penly.cn'), port=int(os.getenv('rport', 6626)), decode_responses=True) 
	redis.si	= Counter()

hgetall		= lambda key='ap:CC1BE0E29824:sub-folder': redis.r.hgetall(key)	 # ap:* , page:*, pen:* , config:* , app:* 
now			= lambda: time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
mid			= lambda s, left, right=':':  s.split(left)[-1].split(right)[0]

'''
os.setenv('rhost', os.getenv('rhost', '172.17.0.1')) )
'''