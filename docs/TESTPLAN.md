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
| T07 | Stop Patroni på den aktuelle databaseleder. | Patroni promoverer sikkert replikaen; database-VIP'en sender skrivninger til ny leder. | Bestået 2026-08-25: stop af db01 førte efter leader-lease til automatisk promotion af db02 (timeline 3). Web02 svarede grønt gennem VIP'en, og db01 returnerede som streaming-replika med 0 MB lag. |
| T08 | Gendan backup fra PBS01. | Gendannet portal/data kan verificeres. | Delvist bestået 2026-08-25: CT101 blev gendannet midlertidigt som CT201 fra PBS og derefter fjernet. PostgreSQL-konsistent restore/PITR mangler fortsat. |

## Bemærkning om timing

HAProxy markerer en backend som fejlet efter sine health checks. Failover er derfor ikke øjeblikkelig; i denne lab blev `web02` aktiv backend inden for 10 sekunder. Det er et målbart rapportpunkt, ikke en skjult fejl.
