# Nøgle- og credentialinventar

Senest kontrolleret: 2026-08-26  
Formål: at holde en versionsstyret oversigt over **hvor** credentials håndteres, uden at skrive hemmeligheder eller private nøgledata i dokumentation.

## Registreret status

| Aktiv | Placering og beskyttelse | Kontrolstatus | Handling |
|---|---|---|---|
| Portal-databaseforbindelse | `secrets/portal-runtime.enc.yaml`, SOPS-krypteret med age | Krypteret felt og lokal dekryptering valideret | Behold; roter ved mistanke om læk |
| Patroni superuser- og replikeringscredential | Samme SOPS-fil | Krypterede felter valideret | Behold; roter kontrolleret på begge databasenoder |
| PBS API-token | Samme SOPS-fil | Krypteret felt valideret | Behold; roter og restoretest efter ændring |
| Administrator-SSH, RSA | Lokal `secrets/`-mappe, Git-ignoreret og adgangsbegrænset | Fingerprint registreret internt; nøglebaseret adgang til alle PVE-værter og relevante portalcontainere valideret | Opret krypteret SOPS-recovery-kopi ved næste lokale, kontrollerede import |
| Administrator-SSH, ED25519 | Lokal `secrets/`-mappe, Git-ignoreret og adgangsbegrænset | Fingerprint registreret internt; udrulning på alle værter er ikke bekræftet i denne audit | Kontrollér `authorized_keys`; udfas nøgle hvis den ikke bruges |
| Container-værtsnøgler (`.43`–`.46`) | Lokal known-hosts-inventar | Nuværende ED25519-fingerprints matcher de registrerede fingerprints | Behold streng værtsnøglekontrol |
| PVE-værtsnøgler (`.33`–`.35`) | Windows known-hosts | ED25519-fingerprints fysisk verificeret 2026-08-26; direkte SSH testet mod alle tre | Behold streng værtsnøglekontrol og dokumentér fremtidige nøgleskift |
| PVE-/clusterinterne SSH-nøgler | PVE-værternes root `authorized_keys` | Forventede node- og cluster-join-nøgler er til stede på alle tre værter | Hold private modparter node-lokale; kopiér ikke interne nøgler til credential-manageren uden særskilt recovery-design |
| age privat recovery-nøgle | Kun lokal, Git-ignoreret age-nøglefil | Bruges til SOPS-dekryptering | Lav én offline, fysisk adskilt recovery-kopi; må ikke lægges i samme SOPS-fil |

## Regler

- Private SSH-nøgler, adgangskoder og API-tokens vises aldrig i Git, logfiler eller rapporter.
- SOPS/age er projektets credential-manager. En krypteret recovery-kopi af SSH-nøgler må gerne ligge i Git, men den aktive nøglefil beholdes lokalt med begrænsede rettigheder.
- Credential-manageren opbevarer brugeradministrerede credentials og recovery-materiale. Private nøgler, der er genereret internt på PVE-noderne til clusterdrift, forbliver node-lokale, medmindre et særskilt, godkendt recovery-design etableres.
- Host keys opdateres aldrig med `accept-new` efter en nøgleændring. Den nye fingerprint skal først bekræftes via en uafhængig, betroet kanal.
- age-recovery-nøglen skal være tilgængelig ved katastrofegendannelse, men holdes adskilt fra både Git-repository og den krypterede SOPS-fil.
- Credential-rotation registreres i både `AENDRINGSLOG.md` og `DRIFTSLOG.md` med påvirkede systemer og efterfølgende test.
