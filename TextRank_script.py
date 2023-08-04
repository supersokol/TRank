import networkx as nx
import numpy as np
from textblob import TextBlob
import os
import matplotlib.pyplot as plt
import argparse
import logging
import sys

# initializing graphs
sentence_graph = nx.Graph()
word_graph = nx.Graph()
phrase_graph = nx.Graph()

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


def drawGraph(rg, pathOut, label):
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
    plt.savefig(pathOut + label + ".png")
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


def Trank(vg, d, n, log):
    for i in range(n):
        if i%10==0:
            log.info('\n\nTexTrank iteration #' + str(i) + '\nINFO:\n\n')
        for node in vg.nodes:
            TRnew[str(node)] = sum([(vozn(vg, node, nodej) * TR[str(nodej)]) for nodej in vg.adj[node]])
        for node in vg.nodes:
            if i%10==0:
                log.info(str(TR[str(node)]) + ' ' + str(1 - d + d * TRnew[str(node)]) + ' ' + str(node))
            TR[str(node)] = 1 - d + d * TRnew[str(node)]
        


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


# do all stuff
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-i', '--input_path',    default=None,                                   type=str,   help='Path to a txt file. (str, default: None)')
    argparser.add_argument('-o', '--output_path',   default="./out/",                               type=str,   help='output path, str, defaults to \"out\" directory')   
    argparser.add_argument('-l', '--log_path',      default='./new_log.log',                        type=str,   help='optional log filename.')
    
    args = argparser.parse_args()
    log_file = args.log_path
    if log_file:
        logging.basicConfig(filename = log_file,
                            filemode = 'a',
                            format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt = '%H:%M:%S',
                            level = logging.INFO)
    else:
        logging.basicConfig(level = logging.INFO)
    
    log = logging.getLogger("TRank_simple_summarization_example")
    log.info(f'processing text file: {args.input_path}')
    if os.path.exists(args.input_path):
                try:
                    log.info('File exists!')
                    text = filterTXT(args.input_path, filterTG)
                    log.info('Text filtered!')
                    log.info(f'Before filtartion: \n\n{text[1]}\n\n')
                    log.info(f'After filtartion: \n\n{text[0]}\n\n')
                    log.info('\n\n' + str(len(text[0].sentences)) + " sentences\n")
                except Exception as err:
                    log.info('Error occured!')
                    log.info(' %s' % err)
                    sys.exit(1)
                try:
                    log.info('creating word graph..........')
                    create_word_graph(text[0], word_graph)
                    log.info('Word graph constructed!')
                    Trank(word_graph, 0.85, 30, log)
                    log.info('All TextRank iterations on word graph are finished\n\n')
                    log.info('creating sentence graph..........')
                    create_sentence_graph(text[1], sentence_graph, propTG)
                    log.info('Sentence graph constructed!')
                    Trank(sentence_graph, 0.85, 50, log)
                    log.info('All TextRank iterations on sentence graph are finished\n\n')
                    amm, lim = set_limit(sentence_graph, 5)
                    log.info(f'lim is set to {lim}')
                    log.info(f'amm is set to {amm}\n')

                    log.info('composing phrase graph..........')
                    compose_phrase_graph(text[1], word_graph, phrase_graph)
                    log.info('phrase graph composed!\n\n')
                    log.info(f'phrase nodes:\n\n{get_nodes(phrase_graph, 5)[1]}\n\n')
                    log.info(f'word nodes:\n\n{get_nodes(word_graph, 10)[1]}\n\n')
                    log.info(f'\n\nSentence-based TextRank summarization results:\n1:\n{get_sentences(sentence_graph, text[1], 5)[0]}\n2:\n{get_sentences(sentence_graph, text[1], 5)[1]}\n\n')
                    
                    try:
                        drawGraph(word_graph, args.output_path, 'word_graph')
                        log.info('Word graph image saved.')
                        drawGraph(phrase_graph, args.output_path, 'phrase_graph')
                        log.info('Phrase graph image saved.')

                        drawGraph(get_nodes(sentence_graph, 4)[0], args.output_path, 'sentence_graph')
                        log.info('Sentence graph image saved.')
                        sys.exit(0)
                    except Exception as err:
                        log.info('Error occured')
                        log.info(' %s' % err)
                        sys.exit(1)
                
                except Exception as err:
                    log.info('Error occured!')
                    log.info(' %s' % err)
                    sys.exit(1)