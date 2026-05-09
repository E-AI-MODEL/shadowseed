# Shadow Seed Learning 4.5

Welkom. Deze wiki is nu ook bedoeld voor bezoekers die het project voor het eerst zien.

De kernvraag van SSL is eenvoudig:

> kan een model betere antwoorden geven als het niet alleen kijkt naar aanwezige informatie, maar ook naar structurele afwezigheden?

SSL slaat zo'n afwezigheid op als een seed. Die seed begint gewichtloos. Pas na validatie via de Validation Gate mag hij invloed krijgen.

## Lees dit eerst

Als je snel wilt begrijpen wat je bekijkt, gebruik deze volgorde:

1. [Start hier](Start-Hier)
2. [Latest Test Results](Latest-Test-Results)
3. [SSL 4.5 Analysis](SSL-45-Analysis)
4. [Benchmarks](Benchmarks)
5. [GitHub Pages dashboard](https://e-ai-model.github.io/shadowseed/)

## Wat bezoekers meestal willen weten

### 1. Wat is SSL?

SSL is geen nieuw foundation model en geen modeltraining.
Het is een evaluatie- en navigatielaag die probeert kleine, toetsbare ontbrekende punten in antwoorden vast te leggen en pas na validatie te gebruiken.

### 2. Wat bekijk ik hier?

De standaardpublicatie bestaat uit:

- regressietests;
- technische en methodologische smoke-tests;
- kleine benchmarklagen;
- aanvullende evidencelagen voor adversarial Gate-gedrag en probe utility.

### 3. Wat bewijst dit wel?

De repo laat nu overtuigend zien dat:

- de mechanische SSL-kern werkt;
- de standaard meetketen draait;
- aanvullende evidencelagen zichtbaar gemaakt kunnen worden zonder ze te vermengen met de basisregressies.

### 4. Wat bewijst dit nog niet?

De repo bewijst nog niet automatisch:

- algemene modelprestatie buiten kleine suites;
- volledige open-set validatie;
- brede domeintransfer;
- modelinterne validatie.

## Waar kijk je het best naar?

- [Latest Test Results](Latest-Test-Results): de laatste gepubliceerde snapshot
- [SSL 4.5 Analysis](SSL-45-Analysis): de centrale samenvatting
- [Benchmarks](Benchmarks): uitleg per testlaag
- [Architectuur](Architectuur): technische kaart van de repo

## Praktische leesregel

Als een pagina resultaatcijfers toont, let dan altijd eerst op de bewijssoort:

- regressie
- technische smoke
- methodologische smoke
- kleine benchmark
- aanvullende evidencelaag

Niet elke pagina draagt dezelfde claim.

## Hoofdprincipe

> Een seed bevat precies één gap.

Dat principe houdt SSL tegelijk simpel en complex:

- simpel, omdat elke seed klein en toetsbaar moet blijven;
- complex, omdat de totale keten daarna detectie, validatie, retrieval, falsificatie en rapportage kan combineren.
