# Hemmelighedshåndtering i labmiljøet

## Beslutning

Projektet anvender **SOPS med age** som secrets-management-løsning. En komplet Vault-/credential-manager-klynge fravælges: den ville tilføre endnu en HA-tjeneste, databackend og driftsopgave uden at styrke selve opgavens demonstration tilsvarende.

## Model

```text
Administrations-pc
├─ age privat nøgle (lokal, Git-ignoreret)
└─ SOPS krypterer secrets/portal-runtime.enc.yaml
                 │
                 ▼
Git-repository
└─ Kun krypteret secret-fil og offentlig age-modtager
                 │
                 ▼
Målcontainer ved deploy
└─ Runtime-fil med chmod 0600 og root som ejer
```

Følgende må aldrig committes ukrypteret: PostgreSQL-applikationsadgang, Patroni-replikationsadgang, PBS API-token, private SSH-nøgler og router-/PVE-adgangskoder.

## Implementeringsforløb

1. Installér `age` og `sops` på administrations-pc'en fra deres officielle udgivelser.
2. Generér ét age-nøglepar. Den private nøgle gemmes kun lokalt under den allerede Git-ignorerede `secrets/`-mappe; den offentlige modtager registreres i `.sops.yaml`.
3. Opret én krypteret fil med kun de runtime-værdier, der skal udrulles. Den må gerne committes, fordi alle værdier er SOPS-krypteret.
4. Dekryptér kun under kontrolleret deploy til `/etc/portal/portal.env` og `/etc/patroni/config.yml` på de relevante containere. Runtime-filer sættes til `root:root` og `0600`.
5. Genstart kun den berørte service og kør `/health`, Patroni-status og replikationstest efter ændringen.
6. Ved mistanke om læk: skift først PostgreSQL-/PBS-credential, opdatér den krypterede fil, udrul igen og dokumentér rotationen i driftsloggen.

## Begrænsninger

SOPS krypterer secrets i versionsstyring og beskytter mod et utilsigtet Git-læk. Det erstatter ikke TLS mellem tjenester, firewall-regler eller rettighedsstyring på værterne. age-nøglens backup skal opbevares adskilt fra lab-pc'en; uden den kan de krypterede værdier ikke gendannes.
