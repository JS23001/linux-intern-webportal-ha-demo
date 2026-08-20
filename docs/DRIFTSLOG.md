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

## Næste registrering

Når første vært er installeret, registreres hostname, IP-adresse, operativsystem/version, netværksopsætning og bekræftet SSH-adgang her.
