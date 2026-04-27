# Agente Zola - playerSmart.py

Questo progetto contiene l'implementazione di un agente intelligente per il gioco Zola, sviluppato per la competizione del corso magistrale di Intelligenza Artificiale.

## Logica dell'Euristica (Pesi)

La scelta dei pesi nella funzione di valutazione (euristica) definisce la "personalità" e le priorità dell'agente. In `playerSmart.py` è stata utilizzata una gerarchia di pesi basata sul principio del **Lexicographic Ordering (Ordinamento Lessicografico)**. L'obiettivo è fare in modo che una priorità inferiore non possa mai superare una priorità superiore.

I pesi utilizzati sono i seguenti:
* **Vantaggio materiale (Pezzi): `* 100`**
* **Potenziale di cattura (Mosse di cattura future): `* 10`**
* **Mobilità generale (Mosse totali): `* 1`**

Vediamo nel dettaglio il ragionamento:

### 1. Il Materiale è Re (`* 100`)
Zola è un gioco di eliminazione: vince chi mangia tutti i pezzi dell'avversario. Avere un pezzo in più garantisce un netto vantaggio, perché riduce le opzioni nemiche e aumenta le proprie. 
Dando peso `100` a una pedina, ci assicuriamo che l'agente **non sacrificherà mai un pezzo** solo per ottenere una posizione apparentemente più "mobile". 
Anche se sacrificare un pezzo ci facesse guadagnare 5 mosse di mobilità in più, perderemmo `100` punti e ne guadagneremmo solo `5` (con il peso `1`). Quindi, l'agente proteggerà sempre il materiale prima di tutto.

### 2. Le Catture Future (`* 10`)
Fra due o più mosse di cattura disponibili, l'agente preferisce quella che negli stati successivi consentirà di effettuare un'altra cattura. 
Per implementare questo requisito, è stato dato peso `10` alle "mosse di cattura disponibili".
Quando l'agente confronta due stati in cui il numero di pedine è identico (stesso punteggio per il materiale), il peso `10` funge da **primo spareggio decisivo**. Lo stato che offre più bersagli raggiungibili guadagnerà `10` punti extra per ogni bersaglio, spingendo l'agente verso posizioni "aggressive".

### 3. Mobilità Generale (`* 1`)
Questo è l'**ultimo spareggio**. Se a parità di materiale c'è anche lo stesso numero di catture potenziali (oppure zero catture per entrambi), l'agente preferirà la posizione che gli offre più libertà di movimento generale (mosse di fuga o posizionamento).
In giochi ristretti come Zola, avere molte mosse significa che l'avversario farà molta fatica a forzarti a fare l'unica mossa pessima rimasta a disposizione (*Zugzwang*).

---

## Ottimizzazione della Ricerca: Forward Pruning Selettivo

Per gestire l'importante vincolo di tempo (3 secondi per mossa), l'agente non si limita a un semplice algoritmo Alpha-Beta Pruning standard, ma implementa una forma aggressiva di **Forward Pruning**.

### Cos'è il Forward Pruning?
Negli algoritmi di ricerca standard (come Minimax o Alpha-Beta), si esplorano tutti i possibili rami (mosse legali) a partire da un determinato stato, "tagliando" i rami solo quando si ha la certezza matematica che non influenzeranno il risultato finale (come fa l'Alpha-Beta). 
Il *Forward Pruning*, invece, è una tecnica euristica in cui l'agente decide *a priori* di **scartare e non esplorare del tutto** un sottoinsieme di mosse legali. Questo si fa partendo dal presupposto umano/euristico che quelle mosse scartate siano intrinsecamente peggiori, decidendo che non vale la pena sprecare tempo di calcolo per analizzarle.

### Come lo abbiamo applicato in Zola?
Nel nostro agente (`playerSmart.py`), abbiamo applicato il forward pruning separando le mosse legali in due macro-categorie: **Catture** (Captures) e **Fughe/Spostamenti** (Escapes). 
La logica algoritmica applicata in fase di espansione dei nodi è la seguente:
1. Se dallo stato attuale esistono mosse di cattura, l'agente esplora **esclusivamente** i rami delle catture. 
2. Le mosse di fuga vengono immediatamente scartate a priori per risparmiare tempo.
3. **Il "Paracadute" (Fallback)**: Le mosse di fuga vengono recuperate ed esplorate come piano d'emergenza **soltanto se** tutte le mosse di cattura analizzate portano inesorabilmente a una sconfitta certa (`score <= -9000`). Questo comportamento viene simulato simmetricamente anche quando tocca all'avversario.

### I Rischi del Forward Pruning
Sebbene questa tecnica abbatta drasticamente il branching factor (il numero medio di figli per ogni nodo) permettendo all'agente di raggiungere profondità di calcolo notevoli in soli 3 secondi, comporta un **rischio teorico intrinseco**:
* **Ignorare Mosse "Silenziose" Vincenti**: Potrebbe esistere una mossa di fuga o di riposizionamento geniale che, pur non catturando nulla immediatamente, prepara una trappola perfetta garantendo una vittoria spettacolare in 2 o 3 turni. Tuttavia, se l'agente rileva anche una sola banale mossa di cattura disponibile, seguirà la regola del pruning e scarterà immediatamente la mossa "silenziosa" geniale, senza averne mai calcolato gli effetti a lungo termine.

In giochi densi, reattivi e prevalentemente tattici come Zola, dare un'assoluta e rigida priorità alle dinamiche di cattura si rivela statisticamente una scelta vincente. Il lieve rischio di perdersi una tattica di posizionamento a lungo termine è ampiamente compensato dal brutale e schiacciante vantaggio di poter prevedere l'albero delle catture forzate con molti turni di anticipo rispetto all'avversario.
