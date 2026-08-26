# Opdateringspolitik

Senest opdateret: 2026-08-26  
Gælder: alle PVE-værter, LXC'er, PBS01 og deres HA-afhængigheder.

## Formål

Sikkerheds- og systemopdateringer gennemføres rullende, så en opdatering aldrig fjerner både en service og dens redundante partner samtidig. Politikken er et driftsbilag til projektdefinitionens afsnit 5.3.

## Backup-gate

Ingen pakkeinstallation eller genstart må begynde, før alle punkter er grønne:

1. Seneste planlagte PBS-job er gennemført og PBS-verificeret.
2. Seneste planlagte pgBackRest-job er gennemført med `status: ok`.
3. Patroni har én leder, én streaming-replika og raske etcd-endpoints.
4. Portal-VIP'en og `/health` svarer fra den aktive service.
5. Ændringen og rollback-punktet er registreret i driftsloggen.

Pr. 2026-08-26 er PBS-gaten grøn. pgBackRest-cron er rettet og funktionstestet, men den næste ordinære natlige kørsel mangler fortsat som bevis, så hele gaten er **lukket**.

## Gennemførelse

| Fase | Rækkefølge | Stopkriterium |
|---|---|---|
| Forberedelse | Læs opdateringsliste, kontrollér backup-gate og notér versionsniveau | Enhver backup-, quorum- eller health-fejl |
| etcd | Ét medlem ad gangen, og bevar mindst to raske medlemmer | Etcd mister quorum eller endpoint er ikke raskt |
| Proxy og web | Opdatér én redundant container ad gangen | VIP eller portal-health fejler |
| Database | Først streaming-replika, kontrolleret switchover, derefter tidligere leder | Patroni/replikering eller applikationstest fejler |
| PBS | Opdatér separat; ved større PBS/pgBackRest-skift køres restoretest | Datastore, backupjob eller restore fejler |
| PVE | Én vært ad gangen; mindst to clusternoder skal have quorum | Cluster ikke quorate eller gæster returnerer ikke raske |

Efter hvert trin kontrolleres tjenestens health, logs og HA-status. Først når kontrollen er grøn, fortsættes til næste partner.

## Rollback og registrering

- Stop rullen straks ved fejl og hold den fungerende redundante partner i drift.
- Rul den seneste pakke-/konfigurationsændring tilbage, hvis det kan ske uden datatab; ellers gendan efter den dokumenterede PBS- eller pgBackRest-procedure.
- Opret en driftslogpost med start/slut, opdaterede komponenter, versioner, testresultat og eventuelt rollback.
- Opdater ændringsloggen, hvis rækkefølge, scope eller acceptkriterier ændres.

## Frekvens

Læsende opdateringskontrol udføres ugentligt. Installationer sker kun i et aftalt vedligeholdelsesvindue efter grøn backup-gate. Kritiske sikkerhedsopdateringer følger samme rækkefølge og kontrol, men kan prioriteres til næste mulige vedligeholdelsesvindue.
