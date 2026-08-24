# Testplan og testbeviser

| ID | Test | Forventet resultat | Status / bevis |
|---|---|---|---|
| T01 | Kald `/health` to gange gennem `192.168.1.40`. | Trafik fordeles på begge webnoder. | Bestået: kald ramte `web01` og derefter `web02`. |
| T02 | Stop Keepalived på den aktive proxy. | VIP flytter til den anden proxy, og portalen svarer. | Bestået: `proxy02` fik VIP'en, og `/health` svarede stadig. |
| T03 | Stop `portal` på `web01` og vent på HAProxy health check. | Trafik fortsætter via `web02`. | Bestået efter 10 sekunder: VIP svarede fra `web02`. En test efter 3 sekunder gav HTTP 503, fordi backenden endnu ikke var markeret nede. |
| T04 | Opret en testregistrering gennem VIP'en. | Data gemmes på PostgreSQL-primæren. | Bestået: POST gav HTTP 302. |
| T05 | Kontroller testregistreringen på `db02`. | Data findes på read-only standby. | Bestået: registreringen var til stede på standbyen efter streaming-replikering. |
| T05a | Kald `/replication` gennem VIP'en. | Begge webnoder viser mindst én streamende standby. | Bestået 2026-08-24: to kald ramte hver sin webnode og rapporterede `streaming_replicas: 1`. |
| T06 | Sluk en hel Proxmox-vært. | Tjenester genstarter automatisk på den anden vært. | Ikke udført: kræver tredje QDevice/PBS-maskine, før to-noders-clusteret har robust quorum. |
| T07 | Promovér database-standby ved tab af primær. | Skrivning kan fortsætte sikkert på ny primær. | Ikke udført: automatisk/manuelt failover-flow fastlægges først med et sikkert witness-/konsensusdesign. |
| T08 | Gendan backup fra PBS01. | Gendannet portal/data kan verificeres. | Ikke udført: afventer tredje maskine og PBS-installation. |

## Bemærkning om timing

HAProxy markerer en backend som fejlet efter sine health checks. Failover er derfor ikke øjeblikkelig; i denne lab blev `web02` aktiv backend inden for 10 sekunder. Det er et målbart rapportpunkt, ikke en skjult fejl.
