# Introduzione al PDDL e ai Problemi di Planning

Questa directory contiene una serie di file scritti in **PDDL** (Planning Domain Definition Language), utilizzati per definire e risolvere problemi di _Automated Planning_ (Pianificazione Automatica) nell'ambito dell'Intelligenza Artificiale.

## 1. Cos'è il PDDL, come funziona e perché si usa

### Cos'è il PDDL?
Il **PDDL** (Planning Domain Definition Language) è un linguaggio standardizzato, originariamente sviluppato nel 1998 e basato sulla sintassi del LISP (da qui l'uso abbondante di parentesi tonde), per esprimere formalmente problemi di pianificazione. L'obiettivo dell'Intelligenza Artificiale in questo ambito è **non codificare** la soluzione algoritmica a un problema specifico (come un algoritmo di ricerca pathfinding customizzato), ma descrivere formalmente l'ambiente in cui ci troviamo per poi far trovare la soluzione (il "piano") a un motore software generale detto **Planner** o *Solver*.

### Come funziona la struttura PDDL
Qualsiasi problema di pianificazione viene rigorosamente scisso in due file logici separati:
1. **Il file di Dominio (Domain):** Rappresenta la "fisica" del nostro mondo. Definisce le regole generali, la tipologia degli oggetti (es. veicoli, container, locazioni), le proprietà che possono variare (i *predicati*) e le azioni o manovre consentite agli agenti.
2. **Il file del Problema (Problem):** È lo "scenario" d'impiego operativo. Descrive la precisa situazione della stanza (lo "stato iniziale"), precisa l'obiettivo finale da concretizzare (il *target abstract state*) e dichiara quali sono le vere istanze fisiche in gioco. 

Il *Planner* elabora poi assieme Dominio e Problema simulando internamente percorsi di ricerca in uno state-space virtuale, cercando una sequenza di **Azioni** che permetta la transizione verso il risultato, senza mai violare i vincoli (le cosiddette precondizioni).

---

## 2. I file di Dominio (`/Domini`)

Il Dominio contiene entità fondamentali come:
- **`:requirements`**: Estensioni logiche necessarie al solver (es. `:typing` per dichiarare gerarchie logiche nel codice, `:action-costs` per sommare i flussi di transazione, oppure `:negative-preconditions`).
- **`:predicates`**: Fatti logico/booleani che indicano qualcosa di intrinsecamente vero o falso come stato parziale. (Es: "La valigia è nel baule").
- **`:actions`**: Operazioni consentite regolamentate da *Precondizioni* (cosa serve affinché avvenga lo snap) ed *Effetti* (su cosa interviene).

Ecco i domini inclusi nel progetto:

### `blocksworld.pddl` (Il mondo dei blocchi)
È un dominio che simula i movimenti di base di un braccio robotico che sposta cubi sparsi su un banco di officina per impilarli correttamente.
- **Tipi:** Un unico tipo di oggetti `block`.
- **Predicati:** Tracciano dinamicamente tutto lo stato strutturale: se un blocco si trova sopra un altro `(on)`, è presente sul tavolo `(ontable)`, è libero sopra `(clear)` o se si trova nella morsa `(holding)`.
- **Azioni:** `pick-up` solleva un blocco dal tavolo, `put-down` sgancia un blocco sul tavolo, `unstack` raccogli il primo blocco dalla cima di una pila, `stack` posiziona un blocco in cima ad una pila.

### `knights-tour.pddl` (Il cammino del cavallo)
Modelizza un problema della teoria dei grafi, ovvero trovare un percorso di visita di tutte le celle di una scacchiera muovendo la pedina del cavallo (a salti a "L") e visitando ogni cella una sola volta.
- Rispetto ai domini di partenza, sfrutta un feature essenziale (`:negative-preconditions`) che consente di verificare la negazione di un predicato nelle precondizioni di un'azione.
- **Azione base:** Viene permessa sola una singola transizione, `move`, soggetta ai vincoli di validità `(valid_move)`.

### `linehaul-with-costs.pddl` (Logistica con calcolo del costo operativo)
Dominio che modellizza il trasporto di merci, distinguendo fra beni a temperatura ambiente e beni refrigerati, su una rete logistica.
- **Funzioni matematiche introdotte:** Sfrutta `:action-costs` per definire una funzione `total-cost` che viene incrementata ad ogni azione `drive` in base alla distanza e al costo per km del mezzo. L'obiettivo è consegnare tutte le merci richieste minimizzando il costo totale.
- **Aritmetica naturale per incrementi:** Dato che i parser PDDL di base non supportano l'aritmetica, la sottrazione (o addizione) di beni richiesti dai clienti viene gestita tramite l'uso di predicati ausiliari `plus1`. Questi predicati stabiliscono una relazione tra un quantitativo e il suo successore, permettendo di simulare un decremento (o incremento) come una transizione tra stati predefiniti. Nel pratico, l'azione `deliver_chilled` sfrutta questa logica per decrementare la domanda di beni refrigerati, passando da uno stato di inventario $N$ a uno stato $N-1$, fino al raggiungimento dello stato base zero.

---

## 3. I file di Problema (`/Problemi`)

Il file Problema definisce l'istanza del dominio.
- **`:objects`**: Definisce gli oggetti specifici del problema, come i veicoli, le locazioni e le quantità di beni da trasportare.
- **`:init`**: Definisce lo stato iniziale del problema, ovvero lo stato del sistema al momento T=0. 
- **`:goal`**: Definisce l'obiettivo logico `and / or` che il planner deve raggiungere. Se l'obiettivo non viene raggiunto, il planner segnala un "Plan Fail".
- **`:metric minimize`**: Indica al planner di risolvere il problema cercando il valore "minimo" per la funzione `(total-cost)`. Se la metrica di costo non viene specificata, il planner cercherà di risolvere il problema nel minor numero di mosse.

### `blocksworld-example.pddl`
Prepara il tavolo virtuale e registra fisicamente quattro oggetti di tipo cubo (`red`, `yellow`, `blue`, `orange`). Lo stato iniziale corrisponde a yellow, orange e red sul tavolo e blue su orange. Il `goal` corrisponde allo stato in cui yellow, orange e red sono sul tavolo e orange è su blu.

### `instance-8x8-A8.pddl`
Scenario di test per il dominio `knights-tour`. Vengono dichiarate tutte le celle di una scacchiera tradizionale (`objects: da A1 a H8`) e, per ognuna di esse, viene dichiarata ogni possibile mossa che la pedina del cavallo può compiere se si trova su quella cella.

### `linehaul-example.pddl`
Definisce un problema di logistica con due veicoli, uno refrigerato e uno no, e quattro locazioni. L'obiettivo è consegnare tutte le merci richieste minimizzando il costo totale. Le quantità sono gestite tramite un sistema di simulazione dei numeri interi realizzato con predicati ausiliari `plus1`.
