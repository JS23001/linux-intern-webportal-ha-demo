# Testplan og testbeviser

| ID | Test | Forventet resultat | Status / bevis |
|---|---|---|---|
| T01 | Kald `/health` to gange gennem `192.168.1.40`. | Trafik fordeles på begge webnoder. | Bestået: kald ramte `web01` og derefter `web02`. |
| T02 | Stop Keepalived på den aktive proxy. | VIP flytter til den anden proxy, og portalen svarer. | Bestået: `proxy02` fik VIP'en, og `/health` svarede stadig. |
| T03 | Stop `portal` på `web01` og vent på HAProxy health check. | Trafik fortsætter via `web02`. | Bestået efter 10 sekunder: VIP svarede fra `web02`. En test efter 3 sekunder gav HTTP 503, fordi backenden endnu ikke var markeret nede. |
| T04 | Opret en testregistrering gennem VIP'en. | Data gemmes på PostgreSQL-primæren. | Bestået: POST gav HTTP 302. |
| T05 | Kontroller testregistreringen på `db02`. | Data findes på read-only standby. | Bestået: registreringen var til stede på standbyen efter streaming-replikering. |
| T05a | Kald `/replication` gennem VIP'en. | Begge webnoder viser mindst én streamende standby. | Bestået 2026-08-24: to kald ramte hver sin webnode og rapporterede `streaming_replicas: 1`. |
| T06 | Sluk en hel Proxmox-vært. | Tjenester genstarter automatisk på den anden vært. | Ikke udført: tre-node-quorum er nu klar, men fysisk værts-HA testes som særskilt næste fase. |
| T07 | Stop Patroni på den aktuelle databaseleder. | Patroni promoverer sikkert replikaen; database-VIP'en sender skrivninger til ny leder. | Bestået 2026-08-25: stop af db01 førte efter leader-lease til automatisk promotion af db02 (timeline 3). Web02 svarede grønt gennem VIP'en, db01 returnerede som streaming-replika med 0 MB lag, og en ny tidsregistrering skrevet via VIP'en kunne læses på begge noder. |
| T08 | Gendan backup fra PBS01. | Gendannet portal/data kan verificeres. | Bestået 2026-08-25: CT101 blev tidligere gendannet midlertidigt som CT201 fra PBS. PostgreSQL blev desuden gendannet til separat testmappe fra pgBackRest på PBS01, nåede konsistent WAL-recovery og returnerede `Failover-test-20260825` på en isoleret, read-only instans. Testområdet blev stoppet og slettet. |
| T09 | Kør pgBackRest fuld backup og inkrementel backup. | Repository på PBS01 indeholder konsistent backup og WAL-arkiv. | Bestået 2026-08-25: fuld backup `20260825-105455F`, efterfulgt af inkrementel backup; `pgbackrest info` rapporterede status `ok` og WAL-arkiv på timeline 4. |

## Bemærkning om timing

HAProxy markerer en backend som fejlet efter sine health checks. Failover er derfor ikke øjeblikkelig; i denne lab blev `web02` aktiv backend inden for 10 sekunder. Det er et målbart rapportpunkt, ikke en skjult fejl.
