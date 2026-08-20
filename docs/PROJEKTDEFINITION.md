# Projektdefinition: Intern webportal – HA-demo

| Felt | Indhold |
|---|---|
| Status | Platformgrundlag klar |
| Version | 0.2 |
| Senest opdateret | 2026-08-20 |
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

PBS01 / QDevice (tredje fysisk maskine)
├─ backupmål for VM'er og containere
└─ ekstra stemme til Proxmox-clusterets quorum
```

| Lag | Plan | Formål |
|---|---|---|
| Virtualisering | `PVE01` og `PVE02` | Adskiller tjenester, giver plads til udvidelse og fejltest af en hel vært. |
| Indgang | `proxy01` og `proxy02` | HAProxy fordeler trafik; Keepalived flytter den virtuelle IP ved fejl. |
| Web | `web01` og `web02` | To ens instanser af portalen, én på hver PVE-vært. |
| Data | `db01` og `db02` | Replikeret database, så mock-data kan bevares ved fejl. Den præcise teknologi vælges i designfasen. |
| Backup/quorum | `PBS01` / QDevice | Uafhængige backups og quorum-støtte til et cluster med to PVE-værter. |

### Implementeret platformstatus

- Proxmox-cluster: `portal-ha`.
- Medlemmer: `pve01` (`192.168.1.33`) og `pve02` (`192.168.1.34`).
- Corosync-link: eksisterende lab-LAN (`192.168.1.0/24`). Et dedikeret fysisk cluster-net er fortsat ønskeligt, men ikke tilgængeligt i denne fase.
- Begge noder er opdateret til samme Proxmox- og kernelversion.
- Automatisk HA ved tab af én fysisk node er **ikke** klar endnu, før en tredje QDevice-maskine er tilsluttet. Clusteret må ikke ændres til kunstigt at acceptere én enkelt stemme, da det vil give split-brain-risiko.

## 4. Mock-tidsregistrering

### Med i scope

- Opret en testregistrering med navn, dato og timer.
- Vis alle testregistreringer i en tabel.
- Vis identiteten på den webserver, der leverer siden.
- Vis relevant driftsstatus, fx aktiv database/primær node eller seneste synkronisering.
- Gem data i den database, der indgår i replikeringsdesignet.

### Uden for scope

- Rigtig login, roller eller persondatabehandling.
- Lønberegning, godkendelsesflow, eksport og integrationer.
- Produktionsegnet design og sikkerhed ud over det nødvendige for laboratoriet.

## 5. Afgrænsninger og risici

- To PVE-værter alene giver ikke et robust quorum. Tredje maskine planlægges derfor som QDevice fra starten.
- Backup er ikke det samme som replikering: replikering giver tilgængelighed, mens PBS01 giver mulighed for gendannelse.
- Løsningen skal undgå, at én enkelt proxy, database eller delt filservice bliver et ubehandlet single point of failure.
- Databasevalg og automatisk database-failover er en designbeslutning, der dokumenteres før implementering.

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
| M2 | Platform klar | PVE01/PVE02, netværk og QDevice er klar. |
| M3 | Portal klar | Mock-portalen kører ens på web01 og web02. |
| M4 | HA klar | VIP, load balancing og web-failover er testet. |
| M5 | Data klar | Datareplikering og database-failover er testet. |
| M6 | Backup klar | PBS-backup og mindst én restore er testet. |
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
| Operativsystem i tjenester | Debian eller Ubuntu Server | M2 |
| Webserver og portalteknologi | Nginx/Apache og valgt mock-app | M3 |
| Database og replikering | Fx PostgreSQL med valgt failover-mekanisme | M5 |
| Netværk | IP-adresser, VLAN'er og fysisk Corosync-net | M2 |
| Backup-politik | Tidspunkt, retention, kryptering og restore-test | M6 |
