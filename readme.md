NOTE:

1. File Synthesize.ipynb (versione anche in pdf) contiene un esempio du sintetizzatore (molto easy) che ho testato su Llama3.1 deployato sul mio server remoto. E' lentino perchè gira su CPU.
Esso è un punto di partenza da espandere.


2. <code_net>.json
Tale jeson contiene le chiavi nodes, edges e sentences che sono quelle di interesse.
-- nodes contiene la lista dei nodi del grafo. ogni nodo è composto dai seguenti campi:
  quelle con -> sono di interesse
  - 'key',           -> id univoco del nodo
  - 'edge',
  - 'word',          -> parola associata dall'annotatore per non avere sinonimi, abbreviazioni, etc
  - 'spot',          -> lista di parole reali nei testi che sono stati associati alla word
  - 'categories',    -> categorie del nodo
  - 'count',
  - 'pagerank'

ESEMPIO:
{'key': 'natural killer cell', 'edge': 'natural killer cell', 'word': 'natural killer cell', 'spot': ['Natural Killer cells', 'Natural killer cells', 'Natural killer cell', 'Natural Killer Cell', 'natural killer cells', 'NK cells', 'Natural Killer Cells', 'NATURAL KILLER CELL', 'NK cell', 'NK CELL', 'NK Cell', 'NK Cells', 'natural killer cell', 'NK CELLS', 'NATURAL KILLER CELLS'], 'categories': ['lymphocyte', 'agranulocytes', 'cell type'], 'count': 82.19, 'pagerank': 0.022}

-- edges contiene la lista degli archi presenti nel grafo. E' composto dai seguenti campi:
  - 'key',           -> id univoco dell'arco
  - 'source',        -> 'word' relativa al nodo sorgente
  - 'target',        -> 'word' relativa al nodo target
  - 'edge',          -> verbo o concatenazione di verbi tramite ;
  - 'weight',
  - 'mrho',
  - 'bio',
  - 'articles'

ESEMPIO:
{'key': '6df31d990fd0ffcc07c2698774370a15', 'source': 'f. nucleatum', 'target': 'Human', 'edge': 'is associated', 'weight': 0.067, 'mrho': 0.5, 'bio': 1.0, 'articles': ['PMC10177588']}


-- sentences contiene la lista delle sentence di ogni documento. la chiave principale è l'id del documento. ad ogni documento è associato la lista delle sentenze.
 - pmid/pmcid
    [
       {
          -key
            - 'source'    -> vettore contenente posizione iniziale e finale del termine
            - 'target'    -> vettore contenente posizione iniziale e finale del termine
            - 'act_pos'   -> vettore di vettori contenente posizione iniziale e finale dei verbi che separano sorgente e destinazione
       }
    ]

ESEMPIO
{'ab0725e354baa043e73d0f57c5297e7f': {'source': [0, 17], 'target': [69, 81], 'act_pos': [[18, 20]]}}
