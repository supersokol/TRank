import networkx as nx
import numpy as np
from textblob import TextBlob
import os
import matplotlib.pyplot as plt

# initializing graphs
sentence_graph = nx.Graph()
word_graph = nx.Graph()
phrase_graph = nx.Graph()
# paths to files
path = "./inp/"
pathOut = "./out/"
# proper POS tags
propTG = ["NN", "NNS", "NNP", "NNPS", "MD", "JJ", "JJR", "JJS", "RB", "RBR", "RBS", "VB", "VBD", "VBG", "VBN", "VBP",
          "VBZ", "WDT", "WP", "WRB"]
filterTG = ["NN", "NNS", "JJ", "JJR", "JJS"]
TR = {}
TRnew = {}
TRfin = {}

def compare_sentences(sentence1, sentence2, TG):
    comp_score = 0
    for tag in sentence1.tags:
        if tag[1] in TG:
            for word in sentence2.words:
                if tag[0].lemmatize() == word.lemmatize():
                    comp_score += 1
    return comp_score/(np.log(len(sentence1.words))+np.log(len(sentence2.words)))


def create_sentence_graph(txt, sent_graph, TG):
    print('creating sentence graph..........')
    for sentence in txt.sentences:
        sent_graph.add_node(sentence, score=1)
        TR[str(sentence)] = 1
    j = 1
    for node in sent_graph.nodes:
        jj = j
        while jj < len(txt.sentences):
            if not compare_sentences(node, txt.sentences[jj], TG) == 0:
                sent_graph.add_edge(node, txt.sentences[jj],
                                    weight=compare_sentences(node, txt.sentences[jj], TG))
            jj += 1
        j += 1


def create_word_graph(txt_filtered, wrd_graph):
    print('creating word graph..........')
    for word in txt_filtered.words:
        wrd_graph.add_node(word)
        # TR[str(rg.nodes[word])]=1
    for i in wrd_graph.nodes:
        TR[str(i)] = 1
        # print(str(i) + ' ' + str(TR[str(i)]))

    for ngram in txt_filtered.ngrams(n=4):
        j = 1
        while j < 4:
            if wrd_graph.has_edge(ngram[0], ngram[j]):
                wrd_graph.edges[ngram[0], ngram[j]]['weight'] += 1
            else:
                wrd_graph.add_edge(ngram[0], ngram[j], weight=1)
            j += 1



def compose_phrase_graph(txt, wrd_graph, phr_graph):
    print('composing phrase graph..........')
    keyTR = 0
    keyphrase = ''
    for sentence in txt.sentences:
        for word in sentence.words:
            if word.lemmatize() in wrd_graph.nodes:
                keyphrase += word
                keyphrase += ' '
                keyTR += TR[word.lemmatize()]
            else:
                if not keyphrase == '':
                    phr_graph.add_node(keyphrase)
                    TR[str(keyphrase)] = keyTR
                    keyTR = 0
                    keyphrase = ''
        if not keyphrase == '':
            phr_graph.add_node(keyphrase)
            TR[str(keyphrase)] = keyTR
            keyTR = 0
            keyphrase = ''


def drawGraph(rg, pathOut):
    try:
        pos = nx.nx_agraph.graphviz_layout(rg)
    except:
        pos = nx.spring_layout(rg, iterations=20)

    plt.rcParams['text.usetex'] = False
    plt.figure(figsize=(8, 6))

    nx.draw_networkx_nodes(rg, pos, node_size=70, node_color='r', alpha=0.4)

    nx.draw_networkx_edges(rg, pos, width=2, alpha=0.31, edge_color='g')

    nx.draw_networkx_edge_labels(rg, pos, font_color='b', alpha=0.81, font_size=2)

    nx.draw_networkx_labels(rg, pos, font_size=14)
    font = {'fontname': 'Helvetica',
            'color': 'k',
            'fontweight': 'bold',
            'fontsize': 4}

    plt.axis('off')
    plt.savefig(pathOut + text[1][1] + ".png")
    plt.show()


def vozn(vg, vi, vj):
    wij = 0
    for vk in vg.adj[vj]:
        wght = vg.edges[vk, vj]['weight']
        wij += wght
    wght = vg.edges[vi, vj]['weight']
    if wij == 0:
        return 0
    else:
        return wght / wij


# pagerank function


def Trank(vg, d, n):
    for i in range(n):
        print('iteration #' + str(i) + '\n')
        for node in vg.nodes:
            TRnew[str(node)] = sum([(vozn(vg, node, nodej) * TR[str(nodej)]) for nodej in vg.adj[node]])
        for node in vg.nodes:
            print(str(TR[str(node)]) + ' ' + str(1 - d + d * TRnew[str(node)]) + ' ' + str(node))
            TR[str(node)] = 1 - d + d * TRnew[str(node)]
        print('')


def set_limit(vg, cap):
    limit = 0
    amount = len(vg.nodes)
    while amount > cap:
        amount = len(vg.nodes)
        limit += 0.1
        for node in vg.nodes:
            if TR[str(node)] < limit:
                amount -= 1
    if amount == cap:
        return amount, limit
    else:
        return amount, limit - 0.1


def get_sentences(vg, txt, cap):
    amm, lim = set_limit(vg, cap)
    out_amm = cap
    out_txt = TextBlob('')
    for sentence in txt.sentences:
        if TR[sentence] >= lim:
            out_txt += sentence +'\n'
            out_amm -= 1
            if out_amm <= 0:
                return out_txt, len(out_txt.sentences)


def get_nodes(vg, cap):
    out_graph = nx.Graph()
    out_txt = TextBlob('')
    am, lim = set_limit(vg, cap)
    out_amm = cap
    for node in vg.nodes:
        if TR[node] >= lim:
            out_graph.add_node(node)
            out_txt += node + " (TR:" + str(TR[node]) + ");\n"
            out_amm -= 1
            if out_amm <= 0:
                for node1 in out_graph.nodes:
                    for node2 in out_graph.nodes:
                        if vg.has_edge(node1,node2):
                            out_graph.add_edge(node1, node2, weight=vg.edges[node1, node2]['weight'])
                return out_graph, out_txt


def filterTXT(pathTXT, TG):
    txt = TextBlob('')
    if os.path.exists(pathTXT):
        inputTXT = open(pathTXT)
        txtraw = TextBlob(inputTXT.read())
        
        # extracting lemmas
        for tag in txtraw.tags:
            if tag[1] in TG:
                txt += tag[0].lemmatize() + ' '
    return txt, txtraw


Inp = input(" *\n* * * * * * * * * * * * * * * * * * *\nchose input(q to quit):\t")
# if Inp =='q':
# break
if not Inp == '':
    pathTXT = path + Inp + ".txt"

text = filterTXT(pathTXT, filterTG)


create_word_graph(text[0], word_graph)
Trank(word_graph, 0.85, 30)
compose_phrase_graph(text[1], word_graph, phrase_graph)
print(text[1] + '\n\n' + str(len(text[1].sentences)) + " sentences\n")

print(get_nodes(phrase_graph, 5)[1])
print(get_nodes(word_graph, 10)[1])
drawGraph(word_graph, pathOut)
#drawGraph(get_nodes(word_graph, 10)[0], pathOut)
'''
k = 1
for sentence in text[1].sentences:
    kk = k
    while kk < len(text[1].sentences):
        print(sentence)
        print(text[1].sentences[kk])
        print(compare_sentences(sentence, text[1].sentences[kk], propTG))
        kk += 1
    k += 1
'''
'''
'''
'''
create_sentence_graph(text[1], sentence_graph, propTG)
Trank(sentence_graph, 0.85, 50)
amm, lim = set_limit(sentence_graph, 5)
print(text[1] + '\n\n' + str(len(text[1].sentences)) + " sentences\n")
print(lim)
print(amm)

print(get_sentences(sentence_graph, text[1], 5)[0])
print(get_sentences(sentence_graph, text[1], 5)[1])
drawGraph(get_nodes(sentence_graph, 4)[0], pathOut)
'''