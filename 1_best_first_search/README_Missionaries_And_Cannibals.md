# Cannibali e Missionari - Algoritmi di Ricerca

Realizzato da Giuseppe Pasquale Caligiure (Mat. 280867)

Disponibile su GitHub: https://github.com/caligiure/AI_Corso_Magistrale/tree/main/bfs

## Panoramica
Questo progetto è un'implementazione del classico problema di *river-crossing* "Missionari e Cannibali" utilizzando algoritmi di ricerca dell'Intelligenza Artificiale. Il programma, **realizzato utilizzando il framework proposto dal docente**, modella lo spazio del problema, definisce la validità degli stati e delle transizioni, e trova i percorsi ottimali o sub-ottimali verso la soluzione usando diverse strategie di ricerca.

L'obiettivo del puzzle è spostare `N` missionari e `N` cannibali dalla riva sinistra di un fiume alla riva destra utilizzando una barca che può contenere al massimo `B` persone. Il vincolo logico fondamentale è che in qualsiasi momento, su entrambe le rive, il numero di cannibali non può superare il numero di missionari (se ci sono missionari presenti), altrimenti i missionari verranno mangiati.

## Come Funziona il Programma
1. **Formulazione del Problema**: Lo stato del gioco è rappresentato come una tupla `(m, c, b)`, dove:
   - `m`: Numero di missionari sulla riva sinistra.
   - `c`: Numero di cannibali sulla riva sinistra.
   - `b`: La posizione della barca (`1` per la riva sinistra, `0` per la riva destra).
   
   Il numero di missionari e cannibali sulla riva destra è dato da `N - m` e `N - c` rispettivamente.
   
2. **Esecuzione Interattiva**: All'avvio, il programma chiede all'utente di inserire dei parametri personalizzati:
   - `N`: Il numero totale di missionari e cannibali.
   - `B`: La capacità massima di passeggeri della barca.
   
3. **Algoritmi Valutati**: Per dimostrare l'approccio di risoluzione dei problemi tramite IA, il programma esegue automaticamente il puzzle attraverso molteplici algoritmi di ricerca e stampa i passaggi e la soluzione per ciascuno:
   - **A\* Search** (usando un'euristica ottimistica che calcola una stima dei viaggi di sola andata)
   - **Greedy Best-First Search**
   - **Uniform Cost Search (Ricerca a Costo Uniforme)**
   - **Breadth-First Search (Ricerca in Ampiezza)**
   - **Depth-First Search (Ricerca in Profondità)**
   
4. **Visualizzazione**: Il terminale renderizza una visualizzazione visiva passo-passo delle rive e della barca che attraversa il fiume (`🌊⛵`) insieme all'azione eseguita (es. `2M, 1C crossing right`) per la soluzione trovata da ogni singolo algoritmo.

## Come Avviare il Programma

1. Aprire il terminale.
2. Navigare all'interno della directory del progetto contenente lo script `missionaries_and_cannibals.py`.
3. Eseguire lo script utilizzando Python inserendo il seguente comando:

```bash
python missionaries_and_cannibals.py
```

4. Seguire le istruzioni a schermo per interagire con l'interfaccia a riga di comando. Fornire i valori interi strettamente positivi richiesti (per esempio, `N=3`, `B=2`) e premere `Invio`. Le soluzioni per ciascun Algoritmo di Ricerca verranno immediatamente stampate a schermo.

## Prerequisiti
- Python 3.x installato sul proprio computer.
- Tutti i file di progetto inclusi (`missionaries_and_cannibals.py`, `problem.py`, `bfs_algorithms.py`) devono trovarsi all'interno della stessa cartella.
