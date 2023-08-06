# 2022.6.30
#uvicorn sbert-fastapi:app --reload --port 6006 --host 0.0.0.0
#https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2   2022.1.25
from uvirun import * 
import numpy as np

def sbert(name:str='all-MiniLM-L6-v2'):
	''' paraphrase-multilingual-mpnet-base-v2 / all-MiniLM-L6-v2 '''	
	from sentence_transformers import SentenceTransformer
	if not hasattr(sbert, name): setattr(sbert, name, SentenceTransformer(f'/data/model/sentence-transformers/{name}') )
	return getattr(sbert, name)

@app.post('/sbert/embeddings', tags=["sbert"])
def snts_embeddings(snts:list=["This is an example sentence", "Each sentence is converted"], name:str="all-MiniLM-L6-v2"): 
	''' paraphrase-multilingual-mpnet-base-v2 / all-MiniLM-L6-v2 '''
	embeddings = sbert(name).encode(snts)
	return [ (sentence, embedding.tolist()) for sentence, embedding in zip(snts, embeddings)]

@app.get('/sbert/cos_sim', tags=["sbert"])
def snts_cos_sim(snt0:str="This is a red cat with a hat.", snt1:str="Have you seen my red cat?", name:str="all-MiniLM-L6-v2"): 
	''' https://www.sbert.net/docs/quickstart.html '''
	from sentence_transformers import util
	model = sbert(name) 
	emb1 = model.encode(snt0)
	emb2 = model.encode(snt1)
	cos_sim = util.cos_sim(emb1, emb2)
	return cos_sim.tolist()[0][0]

@app.post('/sbert/cos_sim', tags=["sbert"])
def snts_cos_sim_post(refers:list=["This is a red cat with a hat.", "That is a red cat with hats."], snt:str="Have you seen my red cat?", name:str="all-MiniLM-L6-v2"): 
	''' 2022.10.16 '''
	from sentence_transformers import util
	model = sbert(name) 
	emb   = model.encode(snt)
	return [ {"refer":snt, "score": util.cos_sim(emb, model.encode(snt)).tolist()[0][0] }   for snt in refers]

@app.post('/sbert/query_answers', tags=["sbert"])
def snts_query_answers(answers:list=["London has 9,787,426 inhabitants at the 2011 census", "London is known for its finacial district"], query:str="How big is London"): 
	from sentence_transformers import SentenceTransformer, util
	if not hasattr(snts_query_answers,'models'):
		snts_query_answers.model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
	query_embedding = snts_query_answers.model.encode(query)
	passage_embedding = snts_query_answers.model.encode(answers)
	res =  util.dot_score(query_embedding, passage_embedding)
	return res.tolist()[0]

@app.post('/sbert/similar_pairs', tags=["sbert"])
def snts_similar_pairs(sentences:list, topn:int=5): 
	''' ["A man is eating food.",
          "A man is eating a piece of bread.",
          "The girl is carrying a baby.",
          "A man is riding a horse.",
          "A woman is playing violin.",
          "Two men pushed carts through the woods.",
          "A man is riding a white horse on an enclosed ground.",
          "A monkey is playing drums.",
          "Someone in a gorilla costume is playing a set of drums."
          ] '''
	embeddings = model.encode(sentences)
	#Compute cosine similarity between all pairs
	cos_sim = util.cos_sim(embeddings, embeddings)
	#Add all pairs to a list with their cosine similarity score
	all_sentence_combinations = []
	for i in range(len(cos_sim)-1):
		for j in range(i+1, len(cos_sim)):
			all_sentence_combinations.append([cos_sim[i][j], i, j])

	#Sort list by the highest cosine similarity score
	all_sentence_combinations = sorted(all_sentence_combinations, key=lambda x: x[0], reverse=True)
	#print("Top-5 most similar pairs:")
	return [ (sentences[i], sentences[j], cos_sim[i][j]) for score, i, j in all_sentence_combinations[0:topn] ]

@app.post('/sbert/paraphrase_mining', tags=["sbert"])
def snts_paraphrase_mining(sentences:list=["The cat sits outside",
             "A man is playing guitar",
             "I love pasta",
             "The new movie is awesome",
             "The cat plays in the garden",
             "A woman watches TV",
             "The new movie is so great",
             "Do you like pizza?"], topn:int=5):  #https://www.sbert.net/examples/applications/paraphrase-mining/README.html?highlight=paraphrase
	from sentence_transformers import util
	paraphrases = util.paraphrase_mining(model, sentences)
	return [(sentences[ paraphrase[1] ], sentences[paraphrase[2]], paraphrase[0] ) for paraphrase in paraphrases[0:topn] ]

@app.post('/sbert/cluster', tags=["sbert"])
def sbert_cluster(corpus:list = ['A man is eating food.',
          'A man is eating a piece of bread.',
          'A man is eating pasta.',
          'The girl is carrying a baby.',
          'The baby is carried by the woman',
          'A man is riding a horse.',
          'A man is riding a white horse on an enclosed ground.',
          'A monkey is playing drums.',
          'Someone in a gorilla costume is playing a set of drums.',
          'A cheetah is running behind its prey.',
          'A cheetah chases prey on across a field.'
          ], name:str="all-MiniLM-L6-v2"):  
	''' https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/clustering/agglomerative.py '''
	#from sklearn.cluster import AgglomerativeClustering
	from sentence_transformers import util
	corpus_embeddings = sbert(name).encode(corpus)
	# Normalize the embeddings to unit length
	#corpus_embeddings = corpus_embeddings /  np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)
	clusters = util.community_detection(corpus_embeddings, min_community_size=25, threshold=0.75)
	print("Clustering done after {:.2f} sec".format(time.time() - start_time))
	return clusters

if __name__ == '__main__':
	#print ("result:", snts_embeddings())
	print ( snts_cos_sim()) 

'''

	clustered_sentences = {}
	for i, cluster in enumerate(clusters):
		print("\nCluster {}, #{} Elements ".format(i+1, len(cluster)))
		for sentence_id in cluster[0:3]:
			print("\t", corpus_sentences[sentence_id])
		print("\t", "...")
		for sentence_id in cluster[-3:]:
			print("\t", corpus_sentences[sentence_id])

	# Perform kmean clustering
	clustering_model = AgglomerativeClustering(n_clusters=None, distance_threshold=1.5) #, affinity='cosine', linkage='average', distance_threshold=0.4)
	clustering_model.fit(corpus_embeddings)
	cluster_assignment = clustering_model.labels_

	clustered_sentences = {}
	for sentence_id, cluster_id in enumerate(cluster_assignment):
		if cluster_id not in clustered_sentences:
			clustered_sentences[cluster_id] = []
		clustered_sentences[cluster_id].append(corpus[sentence_id])

	return clustered_sentences
'''