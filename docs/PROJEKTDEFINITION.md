# Projektdefinition: Intern webportal – HA-demo

| Felt | Indhold |
|---|---|
| Status | Portal, web-HA, PBS-backup og automatisk databasefailover er verificeret i labmiljøet |
| Version | 0.18 |
| Senest opdateret | 2026-08-25 |
| Ejer | Projektgruppen |
| Kilde | Opgaven *Intern Webportal – Linux Servere* |

## 1. Formål

Vi bygger en intern webportal, som demonstrerer høj tilgængelighed på Linux-infrastruktur. Løsningen skal fortsat være tilgængelig, hvis én webserver eller én Proxmox-vært fejler, og ændrede testdata skal stadig være tilgængelige efter failover.

Portalen indeholder et simpelt mock-tidsregistreringssystem. Det er ikke et færdigt forretningssystem; det er et synligt bevis på, at fælles data, datareplikering og failover fungerer.

## 2. Krav fra opgaven

- To Linux-servere skal kunne levere virksomhedens webportal.
- Webtrafik skal automatisk fordeles mellem serverne.
- Hvis én server fejler, skal den anden automatisk overtage.
- Indholdet skal være ens uanset, hvilken server brugeren rammer.
- Data ændret via én server skal være tilgængelige via den anden.

## 3. Aftalt løsningsprincip

De to Linux-servere forstås som to fysiske Proxmox VE-værter. De kører de virtuelle tjenester, som tilsammen leverer portalen.

```text
Bruger
  │
  ▼
Virtuel IP (VIP)
  │
  ├───────────────┐
  ▼               ▼
PVE01           PVE02
├─ proxy01       ├─ proxy02
├─ web01         ├─ web02
└─ db01          └─ db02

PVE03 (tredje fysisk maskine)
├─ tredje stemme i Proxmox-clusteret
├─ PBS01-VM som backupmål
└─ etcd03-container som database-witness
```

| Lag | Plan | Formål |
|---|---|---|
| Virtualisering | `PVE01`, `PVE02` og `PVE03` | Tre rigtige clusterstemmer; pve03 giver samtidig en selvstændig fysisk platform til støttefunktioner. |
| Indgang | `proxy01` og `proxy02` | HAProxy fordeler trafik; Keepalived flytter den virtuelle IP ved fejl. |
| Web | `web01` og `web02` | To ens instanser af portalen, én på hver PVE-vært. |
| Data | `db01` og `db02` | PostgreSQL 17 styret af Patroni med streaming-replikering og automatisk rollevalg. |
| Database-endpoint | `portal-vip:5432` | HAProxy sender kun databaseforbindelser til Patroni-noden, som svarer `200` på `/primary`. |
| Backup | `PBS01`-VM på pve03 | Adskilt backup- og restoremål med 7 dages retention. |
| Witness | `etcd01`/`etcd02`/`etcd03` | Tre etcd-medlemmer giver Patroni konsensus og forhindrer usikker promotion/split brain. |

### Implementeret platformstatus

- Proxmox-cluster: `portal-ha`.
- Medlemmer: `pve01` (`192.168.1.33`), `pve02` (`192.168.1.34`) og `pve03` (`192.168.1.35`).
- Corosync-link: eksisterende lab-LAN (`192.168.1.0/24`). Et dedikeret fysisk cluster-net er fortsat ønskeligt, men ikke tilgængeligt i denne fase.
- Begge noder er opdateret til samme Proxmox- og kernelversion.
- Clusteret har tre Corosync-stemmer og quorum på to stemmer. Det kan derfor bevare quorum ved tab af én fysisk node, uden kunstigt at reducere forventede stemmer eller skabe split-brain-risiko.

### Plan for pve03

`pve03` installeres som en tredje Proxmox VE-vært og tilføjes direkte til `portal-ha`. Den er dermed selv den tredje Corosync-stemme; en QDevice installeres **ikke** oven på pve03, da det ikke giver ekstra fejlmodstand.

1. **Udført:** Opret DHCP-reservationer for pve01/pve02/pve03; adresserne er `.33`, `.34` og `.35`.
2. **Udført:** Installér samme PVE-version og sikker SSH-adgang som pve01/pve02.
3. **Udført:** Tilføj pve03 til `portal-ha` og verificér tre stemmer/quorum.
4. **Udført:** Opret PBS01 som VM med en separat virtuel backupdisk på pve03 og konfigurer PBS-datastore/backupjob.
5. **Udført:** Opret etcd01/02/03 på hver sin PVE-vært og konfigurer Patroni på db01/db02.
6. **Udført:** Test automatisk databasefailover. Fysisk værts-HA er næste selvstændige test.

## 4. Mock-tidsregistrering

### Med i scope

- Opret en testregistrering med navn, dato og timer.
- Vis alle testregistreringer i en tabel.
- Vis identiteten på den webserver, der leverer siden.
- Vis relevant driftsstatus, herunder antal streamende database-standbyer.
- Gem data i den database, der indgår i replikeringsdesignet.

### Uden for scope

- Rigtig login, roller eller persondatabehandling.
- Lønberegning, godkendelsesflow, eksport og integrationer.
- Produktionsegnet design og sikkerhed ud over det nødvendige for laboratoriet.

## 4.1 Valgt teknisk stack

| Del | Valg |
|---|---|
| Gæsteoperativsystem | Debian 13 LXC-containere |
| Reverse proxy/load balancing | HAProxy + Keepalived |
| Webapplikation | Python/Flask + Gunicorn |
| Database | PostgreSQL med streaming-replikering |
| Container-skabelon | `debian-13-standard_13.6-1_amd64.tar.zst` |

## 4.2 IP-plan for tjenester

Alle adresser ligger på `192.168.1.0/24` med gateway/DNS `192.168.1.1`. De er kontrolleret som ledige før brug og skal efterfølgende reserveres i routeren.

| Funktion | Navn | PVE-vært | IP-adresse |
|---|---|---|---|
| Virtuel indgangsadresse | `portal-vip` | Flytter mellem proxyer | `192.168.1.40` |
| Proxy | `proxy01` | `pve01` | `192.168.1.41` |
| Proxy | `proxy02` | `pve02` | `192.168.1.42` |
| Web | `web01` | `pve01` | `192.168.1.43` |
| Web | `web02` | `pve02` | `192.168.1.44` |
| Database | `db01` | `pve01` | `192.168.1.45` |
| Database | `db02` | `pve02` | `192.168.1.46` |
| PVE-vært | `pve03` | Fysisk vært 3 | `192.168.1.35` (Proxmox-webinterface verificeret) |
| Backup-VM | `pbs01` | `pve03` | `192.168.1.47` |
| etcd | `etcd01` | `pve01` | `192.168.1.48` |
| etcd | `etcd02` | `pve02` | `192.168.1.49` |
| etcd | `etcd03` | `pve03` | `192.168.1.50` |

## 5. Afgrænsninger og risici

- Pve03 skal være en selvstændig fysisk maskine. Hvis den fejler, er pve01 og pve02 fortsat to af tre clusterstemmer.
- Backup er ikke det samme som replikering: replikering giver tilgængelighed, mens PBS01 giver mulighed for gendannelse.
- Løsningen skal undgå, at én enkelt proxy, database eller delt filservice bliver et ubehandlet single point of failure.
- Databasefailover er baseret på Patroni og et tre-medlems etcd-kvorum. Patroni må kun promovere én databaseleder; HAProxy vælger den aktuelle leder via Patronis `/primary`-endpoint.
- etcd-trafik er ukrypteret HTTP i dette afgrænsede lab-LAN. En produktionsløsning skal bruge TLS, firewall-regler, adskilte konti og hemmelighedshåndtering.

## 5.1 Backup-policy for labmiljøet

Pve03 har begrænset kapacitet og er ikke en off-site-løsning. Backupdesignet er derfor bevidst lille, men skal stadig kunne dokumentere en sikker og konsistent restore.

| Område | Metode | Kørsel | Retention |
|---|---|---|---|
| LXC/VM | PBS01 backupjob | Dagligt kl. 01:30 | 7 daglige snapshots |
| PostgreSQL | pgBackRest-basebackup + WAL-arkivering på PBS01 | Fuld søndag kl. 00:15; differential de øvrige nætter kl. 00:15; inkrementel dagligt kl. 12:15. Scriptet udfører kun arbejde på Patroni-lederen. | 2 komplette backupkæder, derefter automatisk oprydning |
| Gendannelse | Dokumenteret restore-test | Mindst én gang, efter første backupkæde | Resultat og tidspunkt logges |

En PBS-snapshot af en container er et ekstra infrastrukturlag, men erstatter ikke en PostgreSQL-konsistent backup. WAL-arkivering og pgBackRest gør det muligt at gendanne databasen til et valgt tidspunkt inden for den bevarede backupkæde.

## 5.2 Hemmelighedshåndtering

Labbet bruger SOPS + age til krypterede secrets i Git og root-ejede runtime-filer med rettigheden `0600` på tjenesterne. En Vault-klynge er fravalgt, fordi den ville være en uforholdsmæssigt tung ekstra afhængighed i dette kapacitetsbegrænsede mock-miljø. Den konkrete nøgle-, deploy- og rotationsprocedure findes i `HEMMELIGHEDSHAANDTERING.md`.

## 6. Leverancer

- Netværksdiagram og IP-/navneplan.
- Konfigurationsoversigt for PVE, proxy, web, database og backup.
- Kildekode til mock-portalen.
- Reproducerbar installationsvejledning.
- Testplan med resultater og screenshots/loguddrag.
- Rapport med valg, begrundelser, udførelse, fejl og læring.

## 7. Milepæle

| Nr. | Milepæl | Færdig når |
|---|---|---|
| M1 | Design godkendt | Diagram, IP-plan, komponentvalg og testplan er dokumenteret. |
| M2 | Platform klar | PVE01/PVE02/PVE03, netværk og tre stemmer er klar. **Opnået 2026-08-24.** |
| M3 | Portal klar | Mock-portalen kører ens på web01 og web02. **Opnået 2026-08-20.** |
| M4 | HA klar | VIP, load balancing, web-failover og fysisk værtsfailover er testet. **Opnået 2026-08-25: pve01 blev stoppet; pve02/pve03 beholdt quorum, og portal/database fortsatte på pve02.** |
| M5 | Data klar | Datareplikering og database-failover er testet. **Opnået 2026-08-25: db01 blev stoppet, db02 blev automatisk Patroni-leder, og db01 kom tilbage som streaming-replika.** |
| M6 | Backup klar | PBS-backup samt pgBackRest/WAL-backup og isoleret database-restore er testet. **Opnået 2026-08-25.** |
| M7 | Rapportgrundlag klar | Dokumentation, testbeviser og ændringslog er komplette. |

## 8. Accepttest

Projektet er klar til aflevering, når nedenstående er gennemført og dokumenteret.

1. Begge webservere kan levere portalen.
2. Trafik går via én virtuel IP og fordeles mellem webserverne.
3. En testregistrering oprettet via portalen kan vises, uanset hvilken webserver der leverer siden.
4. Ved stop af én webserver forbliver portalen tilgængelig.
5. Ved fejl på den aktive proxy flytter VIP'en automatisk til den anden proxy.
6. Ved den planlagte database-failover er allerede oprettede testdata stadig tilgængelige.
7. Mindst én backup er gendannet fra PBS01 og resultatet er verificeret.

## 9. Arbejds- og versionsstyringsregler

- Projektdefinitionen er den aktuelle aftale om, hvad vi bygger.
- Ændres mål, scope, arkitektur, krav eller testkriterier, opdateres dette dokument og `docs/AENDRINGSLOG.md` i samme commit.
- Hver ændring får et versionsnummer: `0.x` under planlægning, `1.x` efter design er låst, og derefter mindre versioner for kontrollerede ændringer.
- En ændringslogpost skal indeholde: dato, version, ændring, begrundelse, konsekvens og beslutningstager.
- Git-commits skrives beskrivende, fx `docs: vælg PBS01 som backupmål og QDevice`.
- Fejl, testresultater og afvigelser dokumenteres; de skjules ikke, da de er rapportmateriale.

## 10. Åbne beslutninger

| Beslutning | Muligheder | Skal afklares før |
|---|---|---|
| Pve03-kapacitet | PBS01 bruger 2 vCPU, 4 GB RAM, 32 GB systemdisk og 140 GB datadisk; etcd03 er etableret som lille LXC | Løbende kapacitetskontrol |
| Netværk | VLAN'er og fysisk Corosync-net | Før produktionslignende drift |
| Backup-politik | PostgreSQL PITR, kryptering og database-konsistent restore-test | Før endelig rapport/aflevering |
| Lagrings-HA | Delt eller replikeret storage, hvis workloads skal kunne genstartes automatisk på anden PVE-vært | Uden for lab-scope; beskriv som begrænsning i rapporten |
