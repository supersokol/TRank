import networkx as nx
from textblob import TextBlob
import os
import matplotlib.pyplot as plt

#initializing graphs
rg=nx.Graph()
vrg=nx.Graph()
path="C:/108/NLP/TRANK/inp/"
pathOut="C:/108/NLP/TRANK/out/"
propTG=["NN","NNS","JJ","JJR","JJS"]
txtRNK=[]
TRK=[]
TR={}
TRnew={}
TRfin={}

def filterTXT(pathTXT,TG):
	if os.path.exists(pathTXT):
		inputTXT=open(pathTXT)
		txtraw = TextBlob(inputTXT.read())
		txt = TextBlob('')
		#extracting lemmas
		for tag in txtraw.tags:
			if tag[1] in TG:
				txt += tag[0].lemmatize() + ' '
	return txt, txtraw
	
def createGraph(txt,rg):
	for word in txt.words:
		rg.add_node(word)
		#TR[str(rg.nodes[word])]=1
	for i in rg.nodes:
		TR[str(i)] = 1
		print(str(i)+' '+str(TR[str(i)]))

	for ngram in txt.ngrams(n=4):
		if rg.has_edge(ngram[0], ngram[1]) :
			rg.edges[ngram[0], ngram[1]] ['weight'] += 1
		else:
			rg.add_edge(ngram[0], ngram[1], weight=1)
		if rg.has_edge(ngram[0], ngram[2]) :
			rg.edges[ngram[0], ngram[2]] ['weight'] += 1
		else:
			rg.add_edge(ngram[0], ngram[2], weight=1)
		if rg.has_edge(ngram[0], ngram[3]) :
			rg.edges[ngram[0], ngram[3]] ['weight'] += 1
		else:
			rg.add_edge(ngram[0], ngram[3], weight=1)

def drawGraph(rg, pathOut):
	try:
		pos = nx.nx_agraph.graphviz_layout(rg)
	except:
		pos = nx.spring_layout(rg, iterations=20)
	   
	plt.rcParams['text.usetex'] = False
	plt.figure(figsize=(8, 6))

	nx.draw_networkx_nodes(rg, pos, node_size=70, node_color='w', alpha=0.4)

	nx.draw_networkx_edges(rg, pos, width=2, alpha=0.31, edge_color='g')

	nx.draw_networkx_edge_labels(rg, pos,  font_color='b', font_size=8)

	nx.draw_networkx_labels(rg, pos, font_size=14)
	font = {'fontname': 'Helvetica',
				'color': 'k',
				'fontweight': 'bold',
				'fontsize': 14}

	plt.axis('off')
	plt.show()
	plt.savefig(pathOut+text[1][1]+".jpg")	
				
def vozn(vg,vi,vj):
	wij=0
	for vk in vg.adj[vj]: 
		wght = vg.edges[vk,vj]['weight']
		wij += wght
	wght = vg.edges[vi,vj]['weight']
	return wght/wij
#pagerank function	
def Trank(vg,d,n):
	for i in range(n):
		print('iteration #' + str(i))
		print('')
		for node in vg.nodes:
			TRnew[str(node)] = sum([(vozn(vg,node,nodej)*TR[str(nodej)]) for nodej in vg.adj[node]])
		for node in vg.nodes:
			TR[str(node)] = 1 - d + d * TRnew[str(node)]
			print(str(TR[str(node)])+' '+str(TRnew[str(node)])+' '+ str(node))
		print('')
#	for node in vg.nodes:
#		txtRNK.append(str(vg.nodes[node]['TR'])+' '+ str(node))
		
def	composePhrases(txtraw,rg,vrg):
	keyTR=0
	keyphrase=''
	for sentence in txtraw.sentences:
		for word in sentence.words:
			if word.lemmatize() in rg.nodes:
				keyphrase+=word
				keyphrase+=' '
				keyTR+=TR[word.lemmatize()]
			else:
				if not keyphrase=='':
					vrg.add_node(keyphrase)
					TRfin[str(keyphrase)]=keyTR
					keyTR=0
					keyphrase=''
		if not keyphrase=='':
			vrg.add_node(keyphrase)
			TRfin[str(keyphrase)]=keyTR
			keyTR=0
			keyphrase=''		

			

Inp=input(" *\n* * * * * * * * * * * * * * * * * * *\nchose input(q to quit):\t")
#if Inp =='q':
		#break
if not Inp=='':
		pathTXT=path+Inp+".txt"

text=filterTXT(pathTXT,propTG)			
createGraph(text[0],rg)
Trank(rg,0.85,50)
composePhrases(text[1],rg,vrg)

#	if ngram[0].lemmatize() and ngram[1].lemmatize() in rg.nodes:
#		TRK.append([str(ngram[0]+' '+ngram[1])])#, (rg.nodes[ngram[0].lemmatize()]['TR']+rg.nodes[ngram[1].lemmatize()]['TR'])])
		#TRK.append([rg.nodes[ngram[0].lemmatize()]['TR']+rg.nodes[ngram[1].lemmatize()]['TR']])
print(text[1])
print('')
print(text[0])
print('')
print(sorted(text[0], reverse=True))
for node in vrg.nodes:
		if TRfin[str(node)]>1:
			print(str(TRfin[str(node)])+' '+str(node))
drawGraph(rg, pathOut)

#print('')
#print(TRK)
