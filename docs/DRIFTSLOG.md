# Driftslog

Denne log beskriver, hvad der faktisk er udført. Den erstatter ikke ændringsloggen: scope- og designændringer registreres fortsat i `AENDRINGSLOG.md`.

| Dato | Fase | Handling | Resultat / bevis |
|---|---|---|---|
| 2026-08-20 | Installation | Downloadede Proxmox VE 9.2-1 ISO fra officiel Proxmox-kilde. | SHA-256 verificeret: `4e88fe416df9b527624a175f24c9aa07c714d3332afb1ee3dbf3879573ef2c6c`. |
| 2026-08-20 | Installation | Flashede USB-installationsmedie til Kingston DataTraveler 3.0, ca. 62 GB. | USB'en ændrede fra Windows-NTFS-volumen til Proxmox' GPT/hybrid-installationslayout. |
| 2026-08-20 | Installation | Verificerede det flashede medie mod ISO'en. | De første 16 MiB på USB'en matcher ISO'en byte-for-byte. |
| 2026-08-20 | Installation | Fejlsøgte boot på HP EliteDesk 800 SFF. | Mediet booter, når Secure Boot er aktiveret. Secure Boot beholdes derfor aktiveret på denne vært. |
| 2026-08-20 | Netværk | Bekræftede lab-LAN fra den aktive Ethernet-forbindelse. | Net: `192.168.1.0/24`; gateway, DHCP og DNS: `192.168.1.1`. |
| 2026-08-20 | Installation | Planlagde Proxmox-værter. | `pve01`: `192.168.1.33`; `pve02`: `192.168.1.34`; gateway/DNS: `192.168.1.1`; netmaske: `/24`. |
| 2026-08-20 | Grundopsætning | Verificerede begge Proxmox-værter efter installation. | Begge kører Proxmox VE `9.2.2` med kernel `7.0.2-6-pve`; de er ikke endnu medlemmer af et cluster. |
| 2026-08-20 | Grundopsætning | Etablerede nøglebaseret SSH-adgang fra administrations-pc'en til begge værter. | Administratornøgle er testet mod `pve01` og `pve02`. Private nøgle er lokal og Git-ignoreret. |
| 2026-08-20 | Grundopsætning | Sikrede SSH på begge værter. | Root accepterer kun nøglebaseret SSH (`PermitRootLogin prohibit-password`); password- og keyboard-interactive-login er deaktiveret. Proxmox-webinterfacet påvirkes ikke. |
| 2026-08-20 | Grundopsætning | Tilføjede gensidigt navneopslag. | Begge værters `/etc/hosts` indeholder `pve01`/`pve01.local` → `192.168.1.33` og `pve02`/`pve02.local` → `192.168.1.34`. |
| 2026-08-20 | Grundopsætning | Skiftede `pve02` til `pve-no-subscription`-repository. | Enterprise- og Ceph-enterprise-repositories er deaktiveret; no-subscription-repository er konfigureret. `apt update` afventer stabil forbindelse til eksterne pakkekilder og er ikke afsluttet. |
| 2026-08-20 | Opdatering | Aktiverede WAN-adgang og opdaterede begge Proxmox-værter. | Begge er opdateret til Proxmox VE `9.2.11` med kernel `7.0.14-12-pve`; begge blev genstartet og deres SSH/webinterface verificeret. |
| 2026-08-20 | Cluster | Oprettede `portal-ha` på `pve01` og tilføjede `pve02`. | Begge noder er `Quorate`; medlemskab og Corosync-status er verificeret fra begge værter. |
| 2026-08-20 | Provisionering | Hentede Debian 13 LXC-skabelon på `pve01`. | `debian-13-standard_13.6-1_amd64.tar.zst` blev checksum-verificeret; samme download blev efterfølgende igangsat på `pve02`. |
| 2026-08-20 | Netværk | Kontrollerede og reserverede projektets service-IP-plan. | `.40`–`.46` svarede ikke på ping/ARP under kontrollen og er dokumenteret til proxy, web, database og VIP. |
| 2026-08-20 | Provisionering | Oprettede seks unprivileged Debian 13 LXC-containere med autostart. | `proxy01`/`web01`/`db01` på `pve01` og `proxy02`/`web02`/`db02` på `pve02`; alle svarer på deres planlagte IP-adresser. |
| 2026-08-20 | Provisionering | Installerede grundpakker på servicecontainere. | HAProxy og Keepalived på proxyer, Python på webnoder og PostgreSQL 17 på databasenoder. |
| 2026-08-20 | Database | Konfigurerede PostgreSQL-primær og fysisk standby. | `db01` (`192.168.1.45`) er primær; `db02` (`192.168.1.46`) er i recovery og streamer WAL fra primæren. Replikations- og applikationshemmeligheder er kun lagret lokalt på værterne. |
| 2026-08-20 | Portal | Udrullede Flask/Gunicorn mock-tidsregistrering på begge webnoder. | Begge instanser svarer på `/health`, angiver deres respektive nodenavn og deler PostgreSQL-primæren. |
| 2026-08-20 | HA | Konfigurerede og testede HAProxy/Keepalived. | VIP `192.168.1.40` fordelte to efterfølgende kald til `web01` og `web02`. Ved stop af Keepalived på `proxy01` overtog `proxy02` VIP'en, og portalens health endpoint svarede fortsat. |
| 2026-08-20 | HA | Testede webnode-failover via HAProxy health checks. | Et første kald efter 3 sekunder gav forventeligt ikke konvergeret HTTP `503`. Efter 10 sekunder med `web01` stoppet leverede VIP'en `/health` fra `web02`; `web01` blev derefter startet igen. |
| 2026-08-20 | Data | Testede skrivevej og replikering. | En testregistrering oprettet via VIP'en gav HTTP `302`; den var derefter til stede på `db02`-standbyen. Rettigheder til applikationsrollen blev udvidet målrettet efter første test fejlede med HTTP `500`. |
| 2026-08-24 | Genstart | Startede laboratoriet efter weekendnedlukning. | Begge PVE-noder blev quorate igen, og alle seks LXC-containere startede automatisk. VIP-portalen svarede fra `web01`. |
| 2026-08-24 | Observability | Udrullede portalens replikationsstatus på begge webnoder. | To kald gennem VIP'en ramte `web02` og `web01`; begge rapporterede `streaming_replicas: 1`. |
| 2026-08-24 | Drift | Konfigurerede eksplicit LXC-opstartsorden på begge PVE-værter. | På hver vært: database `order=10,up=10`, web `order=20,up=5`, proxy `order=30,up=5`; konfigurationerne blev læst tilbage og verificeret. |
| 2026-08-24 | Portal | Rettede navnevisning i tidsregistreringstabellen. | Fejlen `b'Jens'` blev reproduceret og derefter rettet på begge webnoder. VIP-testen viser nu `Jens` og `HA-test` som normal tekst. |

## Næste registrering

Næste fase er udrulning af mock-applikationen til begge webnoder og konfiguration af VIP/load balancer.
