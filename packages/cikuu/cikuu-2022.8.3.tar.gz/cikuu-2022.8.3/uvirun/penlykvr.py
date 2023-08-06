# 2023.2.3 cp from penly-uviredis.py 
from uvirun import * 
import json,requests,hashlib,os,time,redis,fastapi, uvicorn , random,asyncio, platform ,sys, traceback
r		= os.getenv('kvr', '172.17.0.1:6666' if 'linux' in sys.platform else 'data.penly.cn:6666') 
redis.r	= redis.Redis(host=r.split(':')[0], port=int(r.split(':')[-1]), decode_responses=True) 

@app.post('/feishu/event', tags=["feishu"])
def feishu_event(arr:dict={ "challenge": "ajls384kdjx98XX", "token": "xxxxxx",     "type": "url_verification"   } ):
	''' called by feishu '''
	arr.update({'from': 'feishu', 'borntm': time.time()})
	redis.r.publish("pen-feishu-event", json.dumps(arr)) 
	return arr

@app.get('/redis/get', tags=["redis"])
def redis_get(key:str=""):  return redis.r.get(key)
@app.post('/redis/keylist', tags=["redis"]) 
def redis_keylist(keys:list=["ap-ap136:info:page-1713.537.31.107"],names:list=["ctime"]): return [{"key": key, "value":redis.r.hmget(key,*names)} for key in keys]
@app.post('/redis/keylistAll', tags=["redis"])
def redis_keylistAll(keys:list=["ap-ap136:info:page-1713.537.31.107"]): return [{"key": key, "value":redis.r.hgetall(key)} for key in keys]
@app.get('/redis/hgetall', tags=["redis"])
def redis_hgetall(key:str='rid-230537:tid-1', JSONEachRow:bool=False): return redis.r.hgetall(key) if not JSONEachRow else [{"key":k, "value":v} for k,v in redis.r.hgetall(key).items()]
@app.get('/redis/hgetalls', tags=["redis"])
def redis_hgetalls(pattern:str='label:ap-CC1BE0E29824:date-20220929:page-0.0.0:pen-*'):
	''' rid-230537:tid-1:uid-* | for JSONEachRow , added 2022.5.17 '''
	if not pattern.endswith("*") : pattern =  pattern +"*"
	return { key: redis.r.hgetall(key) for key in redis.r.keys(pattern) if redis.r.type(key) == 'hash' }
@app.get('/redis/zrangelist', tags=["redis"])
def redis_zrangelist(pattern:str='stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-*', withscores:bool=False):
	''' stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-fill-11  '''
	if not pattern.endswith("*") : pattern =  pattern +"*"
	return { key: list(redis.r.zrange(key,0,-1, withscores=withscores)) for key in redis.r.keys(pattern) if redis.r.type(key) == 'zset' }

@app.get('/redis/zranges', tags=["redis"])
def redis_zranges(pattern:str='stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-*', withscores:bool=False, suffix:str=""):
	''' kvr version of zrangelist, kvr expects "*" as the last char, 2023.2.3  '''
	if not pattern.endswith("*") : pattern =  pattern +"*" # must the last char in kvr
	return { key: list(redis.kvr.zrange(key,0,-1, withscores=withscores)) for key in redis.kvr.keys(pattern) if redis.kvr.type(key) == 'zset' and key.endswith(suffix) }

@app.get('/redis/keys_hgetall', tags=["redis"])
def redis_hgetalls_map(pattern:str='rid-230537:tid-0:uid-*'): return [] if pattern.startswith("*") else [{"key": key, "value":redis.r.hgetall(key)} for key in redis.r.keys(pattern)]
@app.get('/redis/keys', tags=["redis"]) 
def redis_keys(pattern:str='rid-230537:tid-0:uid-*'):	return [] if pattern.startswith("*") else [{"key": key} for key in redis.r.keys(pattern)] 
@app.get('/redis/keys_hget', tags=["redis"])
def redis_keys_hget(pattern:str='rid-230537:tid-0:uid-*', hkey:str='rid', jsonloads:bool=False):
	if pattern.startswith("*"): return []
	return [{"key": key, "value": ( res:=redis.r.hget(key, hkey), json.loads(res) if res and jsonloads else res)[-1] } for key in redis.r.keys(pattern)]
@app.get('/redis/hget', tags=["redis"])
def redis_hget(key:str='config:rid-10086:tid-1', hkey:str='rid', jsonloads:bool=False):
	res = redis.r.hget(key, hkey)
	return json.loads(res) if res and jsonloads else res  
@app.post('/redis/execute_command', tags=["redis"])
def redis_execute_command(cmd:list='zrevrange rid-230537:snt_cola 0 10 withscores'.split(), name:str='kvr'):	return getattr(redis, name).execute_command(*cmd)  # name: kvr/r/config
@app.post('/redis/execute_commands', tags=["redis"])
def redis_execute_commands(cmds:list=["info"]):	return [redis.r.execute_command(cmd) for cmd in cmds]
@app.post('/redis/xinfo', tags=["redis"])
def redis_xinfo(keys:list=["rid-230537:xwordidf","xessay"], name:str="last-entry"):	return { key: redis.r.xinfo_stream(key)[name]  for key in keys }
@app.get('/redis/delkeys', tags=["redis"])
def redis_delkeys(pattern:str="rid-230537:*"): return [redis.r.delete(k) for k in redis.r.keys(pattern)]
@app.post('/redis/delkeys', tags=["redis"])
def redis_delkeys_list(patterns:list=["rid-230537:*","essay:rid-230537:*"]): return [ redis_delkeys(pattern) for pattern in patterns ]
@app.get('/redis/delete', tags=["redis"])
def redis_delete(key:str="stroke:ap-{ap}:page-{page}:pen-{pen}:item-{item}"): return redis.r.delete(key)
@app.post('/redis/xadd', tags=["redis"])
def redis_xadd(name:str="xitem", arr:dict={"rid":"230537", "uid":"1001", "tid":0, "type":"fill", "label":"open the door"}): return redis.r.xadd(name, arr )
@app.get('/redis/xrange', tags=["redis"])
def redis_xrange(name:str='xitem', min:str='-', max:str="+", count:int=1): return redis.r.xrange(name, min=min, max=max, count=count)
@app.get('/redis/lrange', tags=["redis"])
def redis_lrange(name:str='stroke:ap-quick:page-1713.537.31.92:pen-BP2-0L3-03I-4V:item-fill-11', start:int=0, end:int=-1): return redis.r.lrange(name, start, end)
@app.get('/redis/xrevrange', tags=["redis"])
def redis_xrevrange(name:str='xlog', min:str='-', max:str="+", count:int=1): return redis.r.xrevrange(name, min=min, max=max, count=count)
@app.get('/redis/zrevrange', tags=["redis"])
def redis_zrevrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrevrange(name, start, end, withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrevrange(name, start, end, withscores)]
@app.get('/redis/zrange', tags=["redis"])
def redis_zrange(name:str='rid-230537:log:tid-4', start:int=0, end:int=-1, withscores:bool=True, JSONEachRow:bool=False): return redis.r.zrange(name, start, end, withscores=withscores) if not JSONEachRow else [{"member":member, "score":score} for member, score in redis.r.zrange(name, start, end, withscores=withscores)]
@app.get('/redis/set', tags=["redis"])
def redis_set(key:str='rid-230537:config',value:str=""): return redis.r.set(key, value) 
@app.post('/redis/hset', tags=["redis"])
def redis_hset(arr:dict={}, key:str='rid-10086:tid-1:uid-pen-zz', k:str="label", v:str="v"):	return redis.r.hset(key, k, v, arr) 
@app.post('/redis/hmset', tags=["redis"])
def redis_hmset(arr:dict={}, key:str='rid-10086:tid-1:uid-pen-zz'):	return redis.r.hmset(key,arr) 
@app.post('/redis/hdel', tags=["redis"])
def redis_hdel(keys:list=[], name:str='one'): return redis.r.hdel(name, *keys) 
@app.get('/redis/hdel', tags=["redis"])
def redis_hdel_get(key:str='one', hkey:str='k,k1' , sep:str=','): return [redis.r.hdel(key, k) for k in hkey.split(sep)]
@app.post('/redis/zadd', tags=["redis"])
def redis_zadd(arr:dict={}, key:str='rid-230537:config'): return redis.r.zadd(key, arr) 
@app.get('/redis/xlen', tags=["redis"])
def redis_xlen(key:str='xsnt',ts:bool=False): return redis.r.xlen(key) if not ts else {"time":time.time(), "Value":redis.r.xlen(key)}
@app.get('/redis/zsum', tags=["redis"])
def redis_zsum(key='rid-230537:essay_wordnum',ibeg=0, iend=-1): return sum([v for k,v in redis.r.zrevrange(key, ibeg, iend, True)])
@app.get('/redis/zrangebyscore', tags=["redis"])
def redis_zrangebyscore(key='pen-id', min:float=0, max:float=0, withscores:bool=False):  return redis.r.zrangebyscore(key, min=min, max=max, withscores=withscores) 
@app.get('/redis/publish', tags=["redis"])
def redis_publish(name:str='pen_key_update',msg:str='{"key":"tiku:ap-quick:date-20220919:page-1713.537.31.92:keyscore", "updated_hkeys":["select-5"]}'): return redis.r.publish(name, msg)
@app.post('/redis/join_even_odd', tags=["redis"])
def redis_even_odd(arr:list=['even line','odd line'], asdic:bool=False): return dict(zip(arr[::2], arr[1::2])) if asdic else list(zip(arr[::2], arr[1::2]))

four_int = lambda four, denom=100: [int( int(a)/denom) for a in four]
xy = lambda four : [f"{a},{b}" for a in range(four[0], four[2]+2) for b in range( four[1], four[3] + 2) ] # xy_to_item
@app.post('/redis/penly/xy_to_item', tags=["redis"])
def penly_xy_to_items(arr:list=[[861,1577,11712,2214,"{\"item\":\"fill-1\",\"key\":\"B\"}"],[861,2239,11712,2706,"fill-2"],[861,2731,11712,3297,"fill-3"],[861,3321,11712,3801,"fill-4"],[861,3826,11712,4306,"fill-5"],[861,4330,11712,4798,"fill-6"],[861,4822,11712,5376,"fill-7"],[861,5401,11712,5905,"fill-8"],[861,5930,11712,6336,"fill-9"],[861,6360,11712,6988,"fill-10"],[861,7012,11712,7517,"fill-11"],[861,7541,11712,8009,"fill-12"],[861,8033,11712,8562,"fill-13"],[861,8587,11712,9104,"fill-14"],[861,9128,11712,9596,"fill-15"],[861,9620,11712,10186,"fill-16"],[861,10211,11712,10740,"fill-17"],[861,10765,11712,11232,"fill-18"],[861,11257,11712,11774,"fill-19"],[861,11798,11712,12303,"fill-20"],[861,12327,11712,12868,"fill-21"],[861,12893,11712,13398,"fill-22"],[861,13422,11712,13939,"fill-23"],[861,13963,11712,14468,"fill-24"],[861,14492,11712,14985,"fill-25"],[861,15009,11712,15661,"fill-26"]], denom:int=100,key:str="page:0.100.0:xy_to_item",tsd:str="0"): 
	''' 
	submit data into the permanent store, updated 2021.10.8 
	tsd=1 拓思德，回转换为腾千里格式
	'''
	if tsd=='1':
		##拓思德最大像素 5600*7920
		## 腾千里 a4 最大像素  13779*19488  13779=210*100/1.524 19488=297*100/1.524
		dt=  2.4606 ##210*100/(1.524*5600) 
		arr2 = [[int(x1*dt), int(y1*dt), int(x2*dt), int(y2*dt),tag] for x1,y1,x2,y2,tag in arr ]
		redis.r.set("page:"+key.split(':')[1]+":rect_position", json.dumps(arr2))
		return [redis.r.hset(key, k, tag) for x1,y1,x2,y2,tag in arr for k in xy( ( int(x1*dt/denom), int(y1*dt/denom), int(x2*dt/denom), int(y2*dt/denom)) )]
	else:
		redis.r.set("page:"+key.split(':')[1]+":rect_position", json.dumps(arr))
		return [redis.r.hset(key, k, tag) for x1,y1,x2,y2,tag in arr for k in xy( ( int(x1/denom), int(y1/denom), int(x2/denom), int(y2/denom)) )]

if __name__ == '__main__':	
	pass