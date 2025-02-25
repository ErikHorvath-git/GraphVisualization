# Vizualizácia grafových algoritmov# 

Tento projekt je interaktívna aplikácia napísaná v Pythone, ktorá slúži na vizualizáciu rôznych grafových algoritmov. Aplikácia využíva knižnice **Tkinter** na vytváranie grafického rozhrania, **NetworkX** na prácu s grafmi a **Matplotlib** na vykresľovanie grafických prvkov.

## Funkcie

- **Vizualizácia algoritmov:** Podpora pre krok za krokom vizualizáciu viacerých algoritmov:
  - Dijkstra
  - Bellman-Ford
  - A*
  - Kruskal
  - Prim
  - Kosaraju 
  - Tarjan 
- **Interaktívne pridávanie uzlov a hrán:** Umožňuje používateľovi vytvárať vlastné grafy kliknutím na plátno.
- **Animácia krokov:** Vizualizácia priebehu algoritmov pomocou animácií, vrátane zvýrazňovania zásobníka a detailov jednotlivých krokov.
- **Ukladanie a načítanie grafov:** Možnosť uloženia a načítania grafov vrátane pozícií uzlov a váh hrán.

## Inštalácia

### Požiadavky
- **Python 3.7** alebo novší
- Knižnice:
  - `tkinter` (zvyčajne súčasťou štandardnej knižnice Pythona)
  - `networkx`
  - `matplotlib`

### Inštalácia závislostí
Najskôr si vytvorte virtuálne prostredie (voliteľné) a následne nainštalujte požadované knižnice:

```bash
python -m venv venv
source venv/bin/activate      # pre Unix/MacOS
venv\Scripts\activate         # pre Windows
pip install networkx matplotlib
Klonovanie repozitára
Repozitár si môžete stiahnuť alebo naklonovať cez Git:

bash
Copy
git clone https://github.com/ErikHorvath-git/GraphVisualization
cd graph-algorithms-visualization
Použitie
Spustite aplikáciu pomocou príkazu:

bash
Copy
python app.py
Po spustení sa zobrazí hlavné grafické rozhranie, kde môžete:

Pridávať uzly kliknutím na plátno.
Pridávať hrany medzi uzlami (voľba pomocou tlačidla "Add Edge").
Spúšťať rôzne algoritmy z menu Algorithms.
Pozrieť si pseudokód vybraného algoritmu v ľavom paneli.
Sledovať animácie a detaily jednotlivých krokov algoritmu cez sekciu Stack Visualization a Step Details.
Nakoniec, po dokončení algoritmu Kosaraju alebo Tarjan, sa automaticky vykreslí finálna farebná vizualizácia grafu pomocou funkcie draw_scc(scc), ktorá zvýrazní silne súvisiace komponenty.
Prispievanie
Ak máte nápady na vylepšenie alebo objavíte chyby, neváhajte otvoriť issue alebo vytvoriť pull request. Pri prispievaní dodržujte nasledujúce pravidlá:

Forknite repozitár a vytvorte novú vetvu pre svoje zmeny.
Uistite sa, že vaše zmeny sú otestované a neporušujú existujúcu funkcionalitu.
Vytvorte jasný popis zmien v pull requeste.
