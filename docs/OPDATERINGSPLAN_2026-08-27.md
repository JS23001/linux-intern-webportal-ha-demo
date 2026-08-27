# Rullende opdateringsplan — 2026-08-27

Status: klar til godkendt gennemførelse. Denne plan installerer **ingen** pakker af sig selv.

## Grundlag

APT-indekser blev opdateret læsende på alle PVE-værter, ni LXC'er og PBS01 den 27. august 2026. Backup-gaten er grøn: PBS-snapshots er verificerede, og en reel pgBackRest-cron-test gennemførte på den aktuelle Patroni-leder med `status: ok`.

| Komponent | Ventende pakker | Vurdering |
|---|---:|---|
| pve01, pve02, pve03 | 3 pr. vært | OpenSSL-sikkerhedsopdateringer; ingen ny PVE- eller kernelpakke |
| proxy01, proxy02 | 25 pr. container | Base-OS, OpenSSL, util-linux, Postfix, BIND og Python |
| web01, web02 | 21 pr. container | Base-OS, OpenSSL, util-linux, Postfix og BIND |
| db01, db02 | 25 pr. container | Base-OS, OpenSSL, util-linux, Postfix, BIND og Python; ingen PostgreSQL-/Patroni-pakke |
| etcd01, etcd02, etcd03 | 25 pr. container | Base-OS, OpenSSL, util-linux, Postfix, BIND og Python; ingen etcd-pakke |
| PBS01 | 12 | AppArmor samt GRUB/shim; forvent mulig genstart af PBS-VM |

## Stopkriterier før hvert trin

1. Portal-VIP og `/health` svarer.
2. Patroni har én leder og én streaming-replika.
3. Alle tre etcd-endpoints er raske.
4. PBS-datastore og seneste backup er tilgængelige.
5. PVE-clusteret er quorate med mindst to noder.

Ved ét rødt kontrolpunkt stoppes rullen. Den redundante partner holdes i drift, og hændelsen registreres før næste forsøg.

## Udførelsesrækkefølge

| Bølge | Handling | Verifikation |
|---|---|---|
| 0 | Tag baseline: portal-health, Patroni, etcd, PBS og PVE-quorum. | Alle stopkriterier grønne. |
| 1 | Opdatér én etcd-container ad gangen: etcd03, etcd02, etcd01. | Tre raske etcd-medlemmer efter hvert trin. |
| 2 | Opdatér den proxy, som **ikke** ejer VIP'en, derefter den anden. | VIP og portal svarer efter hvert trin. |
| 3 | Opdatér den passive webnode, derefter den aktive. | Portal viser data og `/health` er grøn. |
| 4 | Opdatér database-replikaen først; udfør kontrolleret Patroni-switchover; opdatér derefter den tidligere leder. | Replikering, skriv/læs i portal og backupscript er grønne. |
| 5 | Opdatér PBS01 og genstart kun PBS-VM'en, hvis pakken kræver det. | Datastore, PBS-login og en læsende backupkontrol er grøn. |
| 6 | Opdatér pve01, pve02 og pve03 én ad gangen. | Cluster-quorum, gæster og portal er grønne efter hvert værtsstep. |
| 7 | Afsluttende kontrol og logføring. | Samlet HA-, backup- og applikationstest er bestået. |

## Udførelsesregler

- Brug almindelig `apt-get upgrade`; der anvendes ikke `dist-upgrade`, `autoremove` eller pakkefjernelse uden ny beslutning.
- Genstart kun den berørte container/VM/vært, hvis APT eller den efterfølgende servicekontrol kræver det.
- Databaserollen ændres kun via kontrolleret Patroni-switchover — aldrig ved at stoppe den aktuelle leder først.
- Efter hver bølge registreres pakkeantal, eventuel genstart og testresultat i `DRIFTSLOG.md`.

## Godkendelsespunkt

Planen er klar. Første installationsbølge påbegyndes kun efter eksplicit godkendelse af vedligeholdelsesvinduet.
