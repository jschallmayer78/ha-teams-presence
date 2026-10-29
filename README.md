# Microsoft Teams Presence für Home Assistant

Custom Integration, die den Teams-Status (Presence) eines Microsoft‑365‑Kontos über die
**Microsoft Graph API** (`GET /me/presence`) überwacht.

## Entitäten

| Entität | Typ | Werte |
|---|---|---|
| Verfügbarkeit | `sensor` (enum) | available, available_idle, away, be_right_back, busy, busy_idle, do_not_disturb, offline, presence_unknown |
| Aktivität | `sensor` (enum) | in_a_call, in_a_conference_call, in_a_meeting, presenting, off_work, out_of_office, … |
| Statusnachricht | `sensor` | Text der Teams-Statusnachricht (Attribut `expires`) |
| In Anruf oder Besprechung | `binary_sensor` | an bei InACall / InAConferenceCall / InAMeeting / Presenting |
| Beschäftigt | `binary_sensor` | an bei Busy / BusyIdle / DoNotDisturb |
| Online | `binary_sensor` | aus bei Offline / PresenceUnknown |
| Abwesenheitsnotiz aktiv | `binary_sensor` | Out-of-Office aktiv |

Mehrere Konten können parallel eingerichtet werden (je ein Config Entry).

## 1. App-Registrierung in Microsoft Entra ID

1. [Entra Admin Center](https://entra.microsoft.com) → **Anwendungen → App-Registrierungen → Neue Registrierung**
2. Name: z. B. `Home Assistant Teams Presence`
3. **Unterstützte Kontotypen:** *Konten in einem beliebigen Organisationsverzeichnis (mehrinstanzenfähig)*
   (für eine reine Single-Tenant-App siehe unten)
4. **Umleitungs-URIs:** Plattform **Web**, beide eintragen:
   - `https://my.home-assistant.io/redirect/oauth` (wird genutzt, wenn die `my`-Integration aktiv ist – Standard bei `default_config`)
   - `https://<deine-ha-url>/auth/external/callback` (wird ohne `my`-Integration genutzt), z. B. `https://ha.example.com/auth/external/callback`
5. **Zertifikate & Geheimnisse → Neuer geheimer Clientschlüssel** → *Wert* kopieren
6. **API-Berechtigungen → Berechtigung hinzufügen → Microsoft Graph → Delegierte Berechtigungen:**
   `Presence.Read`, `User.Read`, `offline_access`
   (je nach Tenant-Richtlinie ggf. „Administratorzustimmung erteilen“)

> **Single-Tenant-App:** In `custom_components/teams_presence/const.py` `TENANT = "organizations"`
> durch deine Tenant-ID (GUID) ersetzen.

> Die Weiterleitung über `my.home-assistant.io` setzt voraus, dass unter
> *Einstellungen → System → Netzwerk* eine Home-Assistant-URL gesetzt ist, die dein Browser erreicht
> (lokal genügt). Die Home-Assistant-Instanz selbst muss nicht aus dem Internet erreichbar sein.

## 2. Installation

**HACS:**

1. HACS öffnen → oben rechts **⋮ → Benutzerdefinierte Repositories**.
2. `https://github.com/jschallmayer78/ha-teams-presence` eintragen.
3. Typ **Integration** auswählen und hinzufügen.
4. In HACS nach **Microsoft Teams Presence** suchen, öffnen und herunterladen.

Dieses Projekt ist eine Custom Integration für HACS, kein Add-on-Repository.

**Manuell:** Ordner `custom_components/teams_presence` nach `<config>/custom_components/` kopieren.

Danach Home Assistant neu starten.

## 3. Einrichtung

1. *Einstellungen → Geräte & Dienste → Integration hinzufügen → „Microsoft Teams Presence“*
2. Anwendungs-(Client-)ID und geheimen Clientschlüssel eingeben
3. Mit dem Microsoft‑Konto anmelden und zustimmen

Das Abfrageintervall (Standard 30 s, 10–3600 s) lässt sich über **Konfigurieren** ändern.
Tokens werden automatisch erneuert. Läuft der Refresh-Token ab, startet Home Assistant eine erneute Anmeldung.

## Beispiel-Automation

```yaml
automation:
  - alias: "Rotes Licht bei Teams-Call"
    triggers:
      - trigger: state
        entity_id: binary_sensor.teams_max_mustermann_in_call_or_meeting
    actions:
      - action: >
          {{ 'light.turn_on' if trigger.to_state.state == 'on' else 'light.turn_off' }}
        target:
          entity_id: light.buero_tuer
        data: >
          {{ {'rgb_color': [255, 0, 0]} if trigger.to_state.state == 'on' else {} }}
```

## Hinweise

- Graph liefert Presence nur für Arbeits-/Schulkonten (Entra ID), nicht für private Microsoft-Konten.
- Bei Throttling (HTTP 429) wird der `Retry-After`-Header berücksichtigt.
