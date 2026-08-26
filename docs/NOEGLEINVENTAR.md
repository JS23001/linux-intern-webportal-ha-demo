# Nøgle- og credentialinventar

Senest kontrolleret: 2026-08-26  
Formål: at holde en versionsstyret oversigt over **hvor** credentials håndteres, uden at skrive hemmeligheder eller private nøgledata i dokumentation.

## Registreret status

| Aktiv | Placering og beskyttelse | Kontrolstatus | Handling |
|---|---|---|---|
| Portal-databaseforbindelse | `secrets/portal-runtime.enc.yaml`, SOPS-krypteret med age | Krypteret felt og lokal dekryptering valideret | Behold; roter ved mistanke om læk |
| Patroni superuser- og replikeringscredential | Samme SOPS-fil | Krypterede felter valideret | Behold; roter kontrolleret på begge databasenoder |
| PBS API-token | Samme SOPS-fil | Krypteret felt valideret | Behold; roter og restoretest efter ændring |
| Administrator-SSH, RSA | Lokal `secrets/`-mappe, Git-ignoreret og adgangsbegrænset | Fingerprint registreret internt; nøglebaseret adgang til db02 valideret | Opret krypteret SOPS-recovery-kopi ved næste lokale, kontrollerede import |
| Administrator-SSH, ED25519 | Lokal `secrets/`-mappe, Git-ignoreret og adgangsbegrænset | Fingerprint registreret internt; udrulning på alle værter er ikke bekræftet i denne audit | Kontrollér `authorized_keys`; udfas nøgle hvis den ikke bruges |
| Container-værtsnøgler (`.43`–`.46`) | Lokal known-hosts-inventar | Nuværende ED25519-fingerprints matcher de registrerede fingerprints | Behold streng værtsnøglekontrol |
| PVE-værtsnøgler (`.33`–`.35`) | Windows known-hosts | pve01 havde en gammel cached ECDSA-nøgle og afviste korrekt ny ED25519-nøgle | Verificér den nye fingerprint via fysisk konsol/Proxmox-konsol før known-hosts opdateres |
| age privat recovery-nøgle | Kun lokal, Git-ignoreret age-nøglefil | Bruges til SOPS-dekryptering | Lav én offline, fysisk adskilt recovery-kopi; må ikke lægges i samme SOPS-fil |

## Regler

- Private SSH-nøgler, adgangskoder og API-tokens vises aldrig i Git, logfiler eller rapporter.
- SOPS/age er projektets credential-manager. En krypteret recovery-kopi af SSH-nøgler må gerne ligge i Git, men den aktive nøglefil beholdes lokalt med begrænsede rettigheder.
- Host keys opdateres aldrig med `accept-new` efter en nøgleændring. Den nye fingerprint skal først bekræftes via en uafhængig, betroet kanal.
- age-recovery-nøglen skal være tilgængelig ved katastrofegendannelse, men holdes adskilt fra både Git-repository og den krypterede SOPS-fil.
- Credential-rotation registreres i både `AENDRINGSLOG.md` og `DRIFTSLOG.md` med påvirkede systemer og efterfølgende test.
