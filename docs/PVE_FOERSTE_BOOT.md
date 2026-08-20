# Første boot: pve01 og pve02

Dette dokument udføres først, når begge Proxmox-værter er færdiginstallerede og kan nås på deres reserverede IP-adresser.

## Adresser

| Vært | FQDN | Adresse |
|---|---|---|
| `pve01` | `pve01.local` | `192.168.1.33/24` |
| `pve02` | `pve02.local` | `192.168.1.34/24` |
| Gateway/DNS | – | `192.168.1.1` |

## Før vi ændrer noget

1. Åbn `https://192.168.1.33:8006` og `https://192.168.1.34:8006`.
2. Log ind som `root` med installationsadgangskoden.
3. Kontrollér på begge værter:

   ```bash
   hostnamectl
   ip -br addr
   ip route
   pveversion
   ```

4. Bekræft, at hver vært kan pinge gatewayen og den anden vært:

   ```bash
   ping -c 3 192.168.1.1
   ping -c 3 192.168.1.33  # køres på pve02
   ping -c 3 192.168.1.34  # køres på pve01
   ```

## Første grundopsætning

Når SSH-adgang er bekræftet, udføres på én vært ad gangen:

1. Opdater pakker.
2. Konfigurér den gratis `pve-no-subscription`-pakke-kilde, hvis ingen abonnementslicens bruges.
3. Genstart, hvis kernel/opdateringer kræver det.
4. Installér administratorens SSH-offentlige nøgle; slå først adgangskode-login fra, når nøgle-login er testet.
5. Dokumentér versioner, netværksresultater og ændringer i `DRIFTSLOG.md`.

## Ikke endnu

- Opret ikke clusteret før begge værter er opdaterede, har korrekt navn/IP og kan nå hinanden stabilt.
- Opret ikke produktions-VM'er eller containere før storage- og netværksdesign er besluttet.
- Deaktivér ikke root-adgang eller SSH-adgangskode før nøglebaseret adgang er testet fra administrationsmaskinen.
