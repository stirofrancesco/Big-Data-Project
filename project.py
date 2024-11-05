import json 
import os
from   langchain_ollama       import ChatOllama
from   langchain_core.prompts import ChatPromptTemplate
import networkx as nx
import matplotlib.pyplot as plt
import re
import random

def add_sentence(dict, pair, edge_id, sentence):
    if pair in dict:
        dict[pair][1].append(sentence)
    else:
        dict[pair] = (edge_id,[sentence]) 


def format_input_for_llama(data):
    buffer = []
    for entities, details in data.items():
        entity1, entity2 = entities  # Estrai la coppia di entità
        edge_id, phrases = details  # Estrai l'ID dell'arco e la lista di frasi dalla tupla
        combined_phrases = ". ".join(phrases)  # Unisce le frasi in un unico testo
        buffer.append(f"Entities: {entity1} - {entity2}. Edge ID: {edge_id}. Sentences: {combined_phrases}")

    return buffer

def split_buffer(buffer, size):
    for i in range(0, len(buffer), size):
        yield buffer[i:i + size]


def extract_subphrases_from_sentences(sentences):
    
    buffer = {}
    G = nx.DiGraph()

    for doc_id, sentence in sentences.items():
        for i in range(0,len(sentence)):
            for edge_id, edge_info in sentence[i]['edges_new'].items():
                
                #Ricaviamo le posizioni di source e target
                source_start = edge_info['source'][0]
                source_end = edge_info['source'][1]
                target_start = edge_info['target'][0]
                target_end = edge_info['target'][1]

                #Estrazione delle entità
                entity_1 = sentence[i]['text'][source_start:source_end]
                entity_2 = sentence[i]['text'][target_start:target_end]

                #Aggiunta delle entità al grafo
                G.add_node(entity_1)
                G.add_node(entity_2)

                #Aggiungo l'arco senza etichetta (al momento) e ID come riferimento
                if not G.has_edge(entity_1, entity_2):
                    G.add_edge(entity_1, entity_2, id=edge_id, label=None)

                #Estrazione della sottofrase
                subphrase = sentence[i]['text'][source_start:target_end]
                
                #Aggiornamento della struttura dati
                add_sentence(buffer, (entity_1,entity_2), edge_id, subphrase)                                                                     
               
    return buffer, G

#Lettura file JSON

with open('1727789577.json','r',encoding='utf-8',errors="replace") as file:
    data = json.load(file)

#Nodi del grafo

nodes = data['nodes']

#Visualizzazione dei nodi 
for node in nodes:
    #print(f"Node ID: {node['key']}, Word: {node['word']}, Categories: {node['categories']}")
    break

#Visualizzazione degli archi del grafo
edges = data['edges']
for edge in edges:
    #print(f"Edge ID: {edge['key']}, Source: {edge['source']}, Target: {edge['target']}, Verbs: {edge['edge']}")
    break

sentences = data['sentences']

#Visualizzazione delle sentences.
for doc_id, sentence_list in sentences.items():
    #print(f"Document ID: {doc_id}")
    for sentence in sentence_list:
        #print((sentence))
        break
    break

data, G = extract_subphrases_from_sentences(sentences)

buffer = format_input_for_llama(data)

buffer = random.sample(buffer,10) #Buffer limitato per testing.

for entry in buffer:
    print(entry)

print("-----------------------------")

# LLAMA3

# ENVIRONMENT
# host = os.getenv('OLLAMA_HOST')
# port = os.getenv('OLLAMA_PORT')

host = "212.189.145.27"
port = 11435

# MODEL
llm = ChatOllama(model="llama3.1", base_url="http://{ip}:{port}".format(ip=host, port=port), temperature=0)

# PROMPT DEFINITION
system = """
You are an expert in summarization. You will be provided with a list of entity pairs and sentences that describe the interaction between them. 
Each block will contain the entities involved, the arc ID, and a set of sentences. 
Please provide a concise summary for each set of sentences, keeping the arc ID for each summary.

Each summary must:
- Be no longer than a few words
- Only include the most important points from the sentence.
- Avoid repeating the original sentence's phrasing or unnecessary details.
- Be as brief as possible while still retaining the core meaning.

Please summarize each sentence individually.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human" , "{_sentences}"),
    ]
)

chain = prompt | llm

# Dividi il buffer in blocchi di massimo 2 elementi
buffer_chunks = list(split_buffer(buffer, 2))

# Dichiara un dizionario per accumulare tutti i riassunti
all_summaries = {}


for chunk in buffer_chunks:

    response = chain.invoke({"_sentences": chunk})
    response_text = response.content

    # Usa una regex per trovare tutti gli ID e i riassunti
    pattern = r'\*\*(\w+)\*\*\n([^\n]+)'
    matches = re.findall(pattern, response_text)

    # Aggiungi i nuovi riassunti al dizionario globale
    for edge_id, summary in matches:
        all_summaries[edge_id] = summary


# Itera su tutti gli archi del grafo per aggiornare le label
for u, v, data in G.edges(data=True):
    for edge_id, summary in all_summaries.items():
        # Controlla se l'ID dell'arco corrisponde
        if data.get('id') == edge_id:
            # Aggiorna la label dell'arco
            G[u][v]['label'] = summary
            print(f"Arco {edge_id} aggiornato con label: {summary}")
            break

# Filtra gli archi che hanno una label
labeled_edges = [(u, v) for u, v, data in G.edges(data=True) if data.get('label') is not None]

# Crea un sottografo con solo gli archi con label
labeled_subgraph = G.edge_subgraph(labeled_edges).copy()

# Ottieni le posizioni dei nodi per il layout
#pos = nx.spring_layout(labeled_subgraph, k=0.5, iterations=100)

pos = nx.circular_layout(labeled_subgraph)

# Disegna il sottografo con solo gli archi con label
nx.draw(labeled_subgraph, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_weight='bold')

# Disegna le label degli archi
edge_labels = nx.get_edge_attributes(labeled_subgraph, 'label')
nx.draw_networkx_edge_labels(labeled_subgraph, pos, edge_labels=edge_labels, font_color='red', font_size=8)

# Mostra il grafico
plt.show()