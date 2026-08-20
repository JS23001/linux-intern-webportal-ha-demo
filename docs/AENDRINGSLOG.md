# Ændringslog

Alle ændringer af scope, arkitektur, krav eller accepttest registreres her. Ændringen og den opdaterede projektdefinition commits sammen.

| Version | Dato | Ændring | Hvorfor | Konsekvens |
|---|---|---|---|---|
| 0.1 | 2026-08-20 | Oprettede projektdefinitionen. | Skabe ét styrende grundlag før implementering. | Projektet følger nu dokumenteret scope, milepæle og accepttest. |
| 0.1 | 2026-08-20 | Valgte to PVE-værter, redundante proxyer/webtjenester og en senere tredje PBS/QDevice-maskine som målbillede. | Matcher opgaven og giver plads til backup samt korrekt quorum-planlægning. | Detaljer om database, netværk og backup afklares før deres respektive milepæle. |
| 0.1 | 2026-08-20 | Afgrænsede tidsregistrering til et mock-system. | Fokus skal være på at demonstrere datareplikering og failover, ikke forretningsfunktioner. | Kun oprettelse og visning af testdata indgår. |
| 0.2 | 2026-08-20 | Oprettede Proxmox-clusteret `portal-ha` med `pve01` og `pve02`. | Fælles administration og senere HA/failover kræver et clustergrundlag. | Clusterkommunikation bruger midlertidigt lab-LAN; QDevice på tredje maskine er fortsat en forudsætning for robust to-noders HA. |

## Skabelon til kommende ændring

| Version | Dato | Ændring | Hvorfor | Konsekvens |
|---|---|---|---|---|
|  |  |  |  |  |
