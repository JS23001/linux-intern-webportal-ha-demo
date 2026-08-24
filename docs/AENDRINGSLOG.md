# Ændringslog

Alle ændringer af scope, arkitektur, krav eller accepttest registreres her. Ændringen og den opdaterede projektdefinition commits sammen.

| Version | Dato | Ændring | Hvorfor | Konsekvens |
|---|---|---|---|---|
| 0.1 | 2026-08-20 | Oprettede projektdefinitionen. | Skabe ét styrende grundlag før implementering. | Projektet følger nu dokumenteret scope, milepæle og accepttest. |
| 0.1 | 2026-08-20 | Valgte to PVE-værter, redundante proxyer/webtjenester og en senere tredje PBS/QDevice-maskine som målbillede. | Matcher opgaven og giver plads til backup samt korrekt quorum-planlægning. | Detaljer om database, netværk og backup afklares før deres respektive milepæle. |
| 0.1 | 2026-08-20 | Afgrænsede tidsregistrering til et mock-system. | Fokus skal være på at demonstrere datareplikering og failover, ikke forretningsfunktioner. | Kun oprettelse og visning af testdata indgår. |
| 0.2 | 2026-08-20 | Oprettede Proxmox-clusteret `portal-ha` med `pve01` og `pve02`. | Fælles administration og senere HA/failover kræver et clustergrundlag. | Clusterkommunikation bruger midlertidigt lab-LAN; QDevice på tredje maskine er fortsat en forudsætning for robust to-noders HA. |
| 0.3 | 2026-08-20 | Låste teknisk stack og service-IP-plan. | Gør provisionering og test reproducerbar uden at udvide mock-systemets scope. | Debian 13 LXC, HAProxy/Keepalived, Flask/Gunicorn og PostgreSQL-replikering bruges; routerreservationer skal senere oprettes for `.40`–`.46`. |
| 0.4 | 2026-08-20 | Tilføjede en PostgreSQL 17 primær/standby-topologi og konkrete LXC-roller. | Viser datareplikation i den krævede mock-løsning og fordeler komponenter mellem de to Proxmox-værter. | Automatisk databasefailover er fortsat uden for scope, indtil der er et sikkert konsensus-/witness-design. |
| 0.5 | 2026-08-20 | Færdiggjorde mock-portalen, VIP/load balancing og den første dokumenterede failover-test. | Gør den aftalte HA-demo konkret og målbar. | Proxyfailover og streaming-replikering er verificeret; fysisk værts-HA, databasefailover og backup afhænger fortsat af tredje maskine og næste fase. |
| 0.6 | 2026-08-24 | Tilføjede applikationssynlig replikationsstatus. | Rapporten skal kunne vise, at databasen ikke blot indeholder de samme data, men har en aktiv streamende standby. | Endpointet `/replication` og forsiden viser antal streamende replikaer; portalens databasebruger har målrettet monitoreringsadgang. |
| 0.7 | 2026-08-24 | Fastlagde containeres opstartsorden på hver PVE-vært. | Afhængige tjenester skal starte i en forudsigelig rækkefølge efter genstart. | Database starter først, derefter web og til sidst proxy; eksisterende autostart bevares. |
| 0.8 | 2026-08-24 | Rettede visning af bytekodede navne i tidsregistreringstabellen. | Navne blev vist som Python-repræsentation, fx `b'Jens'`, hvilket forringede mock-systemets visuelle kvalitet. | Portalen afkoder kun byteværdier til UTF-8 ved visning; eksisterende testdata ændres ikke. |

## Skabelon til kommende ændring

| Version | Dato | Ændring | Hvorfor | Konsekvens |
|---|---|---|---|---|
|  |  |  |  |  |
