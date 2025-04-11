# Klipper TMC Autotune (Alpha -Version)

* * *

[![Español](https://flagcdn.com/w40/es.png)](README.md)[![English](https://flagcdn.com/w40/gb.png)](README.en.md)[![Deutsch](https://flagcdn.com/w40/de.png)](README.de.md)[![Italiano](https://flagcdn.com/w40/it.png)](README.it.md)[![Français](https://flagcdn.com/w40/fr.png)](README.fr.md)[![Português](https://flagcdn.com/w40/pt.png)](README.pt.md)

* * *

Klipper -Erweiterung für die automatische TMC -Konfiguration und -anpassung.

Diese Erweiterung berechnet optimale Werte für die meisten Aufzeichnungen der TMC -Treiber von Schritt -By -Step -Motoren, basierend auf den Informationsblattinformationen und dem vom Benutzer ausgewählten Anpassungsziel.

Insbesondere aktive Stealthchop in Z -Motoren und -Trusoren, coolstep, wo möglich, und ändert sich korrekt auf den vollständigen Schritt zu sehr hohen Geschwindigkeiten. Wenn mehrere Modi verfügbar sind, wählen Sie die ruhigsten Modi und den geringeren Energieverbrauch aus, vorbehaltlich der Einschränkungen der Homing ohne Sensoren (die bestimmte Kombinationen nicht zulässt).

### Aktueller Zustand

-   Offizielle Unterstützung für TMC2209, TMC2240 und TMC5160.
-   Die Unterstützung für TMC2130, TMC2208 und TMC2660 können funktionieren, wurde jedoch nicht getestet.
-   Das Homing ohne Sensoren mit aktiviertem Autotuning funktioniert in TMC2209, TMC2240 und TMC5160 korrekt, vorausgesetzt, die Homing -Geschwindigkeit ist schnell genug (Homing_Speed ​​muss numerisch größer sein als Rotation_Distanz für diejenigen Achsen, die ohne sensible Homing verwendet). Seien Sie wie immer sehr vorsichtig, wenn Sie das Homing ohne Sensoren zum ersten Mal ausprobieren.
-   Die Verwendung von Motorautotunen kann die Effizienz verbessern, sodass sie kälter werden und weniger Energie verbrauchen können. Es ist jedoch wichtig zu beachten, dass dieser Prozess auch TMC -Fahrer zum heißesten funktioniert, sodass geeignete Kühlmaßnahmen implementiert werden müssen.
-   Dynamisches Wärmeschutzsystem, das den Strom in Echtzeit basierend auf der Treibertemperatur und Motorlast anpasst
-   Fortgeschrittene Überwachung mit Probenahme alle 100 ms, einschließlich Überlasterkennung und plötzlicher Temperaturanstieg
-   Vorbeugender Kühlalgorithmus, der den Strom allmählich reduziert, bevor er kritische Grenzwerte erreicht

## Installation

Um dieses Plugin zu installieren, führen Sie das Installationsskript mit dem folgenden SSH -Befehl aus. In diesem Skript wird dieses GitHub -Repository in das Home -Verzeichnis seines RaspberryPI heruntergeladen und symbolische Links der Dateien im zusätzlichen Ordner von Klipper erstellt.

```bash
wget -O - https://github.com/LauOtero/klipper_tmc_autotune/main/install.sh | bash
```

Fügen Sie dann Folgendes zu Ihrem hinzu`moonraker.conf`Um automatische Updates zu aktivieren:

```ini
[update_manager klipper_tmc_autotune]
type: git_repo
channel: dev
path: ~/klipper_tmc_autotune
origin: https://github.com/LauOtero/klipper_tmc_autotune.git
managed_services: klipper
primary_branch: main
install_script: install.sh
```

## Bestehende Konfigurationsanpassung

Die Konfigurationen ihrer Treiber müssen enthalten:

-   Kiefern
-   Ströme (Betriebsstrom, Aufbewahrungsstrom, Homing -Strom, wenn Sie eine Klipper -Version verwenden, die sie unterstützt)
-   `interpolate: true`
-   Besprechen Sie andere Anpassungs- und Homing -Werte ohne Sensoren (halten Sie sie als Referenz, aber sie sind nicht aktiv).

Die Dokumentation von Klipper empfiehlt, die Interpolation nicht zu verwenden. Dies ist jedoch eher anwendbar, wenn niedrige Mikropenzahlen und die vorbestimmte Konfiguration des Treibers verwendet werden. Autotune liefert bessere Ergebnisse, sowohl dimensionale als auch Qualität, unter Verwendung der Interpolation und so viele Mikropassen wie möglich.

Überprüfen Sie die Pins -Diagramme der Treiberplatten: BTT TMC 2240 -Platten müssen konfiguriert werden`diag1_pin`und nicht`diag0_pin`, aber die Stiefstände MKS TMC 2240 erfordern`diag0_pin`Und_NEIN_`diag1_pin`. Es kann andere Treiber mit ungewöhnlichen Konfigurationen geben.

## Homing ohne Sensoren

Autotune kann zusammen mit Homing -Overrides für Homing ohne Sensoren verwendet werden. Sie müssen jedoch die Werte anpassen`sg4_thrs`(TMC2209, TMC2260) y/o`sgt`(TMC5160, TMC2240, TMC2130, TMC2660) speziell in den Autotune -Abschnitten. Wenn Sie diese Änderungen über GCODE oder in den Treiber -TMC -Abschnitten ausprobieren, wird keine Fehlermeldung erzeugt, die jedoch keinen Effekt hat, da der Autotuning -Algorithmus sie überschreibt.

Beachten Sie auch, dass sich die Einstellung der Homing ohne Sensoren aufgrund anderer Anpassungen wahrscheinlich ändern wird. Insbesondere kann Autotune möglicherweise schnellere Homing -Geschwindigkeiten erfordern, um zu funktionieren. Nimm das`rotation_distance`des Motors als Mindestgeschwindigkeit, die funktionieren kann, und wenn es schwierig ist, sich anzupassen, machen Sie die Homing schneller. Homing ohne Sensoren wird viel empfindlicher gegenüber höheren Geschwindigkeiten.

## Häufige Problemlösung

### 1. Einstellung der feinen Empfindlichkeit

**Problem:**Der Kopf hält zu früh an oder erkennt das Rennende nicht.

-   **Ursachen:**Werte von`sgt`/`sg4_thrs`zu niedrig, Induktivität des variablen Motors
-   **Lösung:**
    -   Zunahme`sgt`In 2-3 Einheiten (TMC5160/2240)
    -   Reduzieren`sg4_thrs`In 10-15 Einheiten (TMC2209)
    -   Überprüfen Sie das`homing_speed > rotation_distance`

### 2. Konfiguration optimaler Geschwindigkeit

**Problem:**Verlust von Schritten während des Homens

-   **Ursachen:**Zu niedrige Geschwindigkeit für die aktuelle Konfiguration
-   **Lösung:**
    -   Berechnen Sie die Mindestgeschwindigkeit:`homing_speed = rotation_distance * 1.2`
    -   Zu verwenden`tbl: 1`Und`toff: 2`Für größere Stabilität

### 3.. Fehlalarme

**Problem:**Fehlerhafte Erkennungen während der normalen Bewegung

-   **Ursachen:**Mechanische Schwingungen, unzureichender Strom
-   **Lösung:**
    -   Zunahme`extra_hysteresis`In 1-2 Einheiten
    -   Überprüfen Sie die Kühlung des Fahrers
    -   Sicherstellen`voltage`korrekt konfiguriert

### 4. Parameterkompatibilität

**Wichtig:**Manuelle Anpassungen in Abschnitten`[tmc2209]`Die`[tmc5160]`Sie werden überschrieben.

-   Immer konfigurieren:
    -   `sgt`In`[autotune_tmc]`Für TMC5160/2240
    -   `sg4_thrs`In`[autotune_tmc]`Für TMC2209
    -   `homing_speed`In`[stepper_x]`(und entsprechende Achsen)

## Autotune -Konfiguration

Fügen Sie Ihrem Folgenden hinzu`printer.cfg`(Ändern Sie die Namen von Motoren und entfernen oder fügen Sie Abschnitte nach Bedarf hinzu), um das Autotunieren für seine TMC -Treiber und -Motoren zu ermöglichen, und starten Sie Klipper neu:

```ini
[autotune_tmc stepper_x]
motor: ldo-42sth48-2004mah
[autotune_tmc stepper_y]
motor: ldo-42sth48-2004mah

[autotune_tmc stepper_z]
motor: ldo-42sth48-2004ac
[autotune_tmc stepper_z1]
motor: ldo-42sth48-2004ac
[autotune_tmc stepper_z2]
motor: ldo-42sth48-2004ac
[autotune_tmc stepper_z3]
motor: ldo-42sth48-2004ac

[autotune_tmc extruder]
motor: ldo-36sth20-1004ahg
```

## Abschnittsparameter[autotune_tmc]

Alle Abschnitte`[autotune_tmc]`Sie akzeptieren die folgenden konfigurierbaren Parameter:

| Parámetro          | Standardwert    | Reichweite                                 | Detaillierte Beschreibung                                                                                                                                                                                                                                                     |
| ------------------ | --------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `motor`            | _Obligatorisch_ | [Ver db](motor_database.cfg)               | Name der Datenbankmotor. Definiert physikalische Eigenschaften wie Widerstand, Induktivität und Drehmoment                                                                                                                                                                    |
| `tuning_goal`      | `auto`          | `auto`,`silent`,`performance`,`autoswitch` | Betriebsbetriebsmodus:<br>-`auto`: Automatische Auswahl basierend auf Achsenart<br>-`silent`: Priorisieren Sie die Stille über die Leistung<br>-`performance`: Maximale Geschwindigkeit und Drehmoment<br>-`autoswitch`: Dynamische Veränderung zwischen Modi (experimentell) |
| `extra_hysteresis` | 0               | 0-8                                        | Zusätzliche Hysterese zur Reduzierung der Vibration. Werte> 3 können übermäßige Wärme erzeugen                                                                                                                                                                                |
| `tbl`              | 2               | 0-3                                        | Die Blindzeit des Komparators:<br>- 0: 16 Zyklen<br>- 1: 24 Zyklen<br>- 2: 36 Zyklen<br>- 3: 54 Zyklen                                                                                                                                                                        |
| `toff`             | 0               | 0-15                                       | Chopper's Off Time. 0 = automatische Berechnung. Niedrige Werte verbessern hohe Geschwindigkeiten                                                                                                                                                                             |
| `sgt`              | 1               | -64 A 63                                   | Homing -Empfindlichkeit ohne Sensoren (TMC5160/2240). Negative Werte = größere Empfindlichkeit                                                                                                                                                                                |
| `sg4_thrs`         | 10              | 0-255                                      | Kombinierte Schwelle für Coolstep und Homing (TMC2209). Nichtlineare Beziehung zur echten Sensibilität                                                                                                                                                                        |
| `pwm_freq_target`  | 55 kHz          | 10-60 kHz                                  | PWM -Frequenzziel. Hohe Werte reduzieren das Rauschen, erhöhen aber die Verluste                                                                                                                                                                                              |
| `voltage`          | 24 V            | 0-60V                                      | Echte Motorzufuhrspannung. Kritiker für aktuelle Berechnungen                                                                                                                                                                                                                 |
| `overvoltage_vth`  | _Auto_          | 0-60V                                      | Overtious Protection Sool (TMC2240/5160). Es wird berechnet als`voltage + 0.8V`Wenn nicht angegeben                                                                                                                                                                           |

> **Wichtige Anmerkungen:**
>
> -   Parameter ohne Einheit übernehmen Werte im internationalen Metriksystem (v, A, Hz)
> -   Die Werte von`sgt`Und`sg4_thrs`Sie haben nichtlineare Effekte: Kleine Veränderungen können große Auswirkungen haben
> -   `tuning_goal`Es betrifft mehrere Parameter gleichzeitig:
>     ```plaintext
>     silent:   toff↑, tbl↑, pwm_freq↓, extra_hysteresis↑
>     performance: toff↓, tbl↓, pwm_freq↑, extra_hysteresis↓
>     ```
>
>
> ```
>
> ```

Bei Bedarf können Sie alles im laufenden Flug anpassen, während der Drucker mit dem Makro arbeitet`AUTOTUNE_TMC`in der Klipper -Konsole. Alle früheren Parameter sind verfügbar:

    AUTOTUNE_TMC STEPPER=<nombre> [PARÁMETRO=<valor>]

## Wie das Autoage funktioniert

Der Autojust -Prozess verwendet die folgenden Hauptklassen:

1.  **Tmcutilities**: Bietet Berechnungs- und Optimierungsfunktionen, um TMC -Treiber basierend auf den physikalischen Eigenschaften des Motors zu konfigurieren. Berechnen Sie Parameter wie:
    -   Optimale Hysterese basierend auf dem Strom und dem Anpassungsziel
    -   PWM -Schwellenwerte für automatische Veränderungen zwischen Wegen
    -   Überspannungsschutzwerte
    -   Optimaler Betriebsstrom

2.  **Realtimemonitor**: Bietet eine Echtzeitüberwachung der Temperatur und Last des Motors mit dynamischer Einstellung des Strom- und automatischen thermischen Schutzes.

3.  **Autotunetmc**: Hauptklasse, die die oben genannten Funktionen integriert und die optimale Konfiguration auf TMC -Treiber anwendet.

Der verbesserte Autojust -Algorithmus enthält jetzt:

1.  Automatische optimale PWM -Frequenzberechnung basierend auf Motorinduktivität
2.  Dynamische Hystereseanpassung nach realer Temperatur und Last
3.  Übergangsoptimierung zwischen den Betriebsmodi
4.  Schutz gegen Schwingungen und mechanische Resonanzen

Der vollständige Vorgang folgt folgenden Schritten:

1.  Lädt die physischen Konstanten der Engine aus der Datenbank oder der Benutzerkonfiguration
2.  Bestimmen Sie das Anpassungsziel (stille, leistungsbasierte, selbstbasierte) basierend auf dem Motortyp und der Konfiguration
3.  Berechnen Sie die optimalen Parameter für einen bestimmten TMC -Treiber
4.  Wenden Sie die Treiberkonfiguration an und überwachen Sie Ihre Leistung
5.  Passen Sie die Parameter während des Betriebs dynamisch an

Die Parameter sind speziell für jeden TMC -Treibertyp optimiert, wobei die einzigartigen Eigenschaften und Einschränkungen berücksichtigt werden.

## Benutzer -definierte Motoren

Die Namen der Motoren und ihrer physischen Konstanten befinden sich in der Datei[motor_database.cfg](motor_database.cfg), was automatisch vom Skript aufgeladen wird. Wenn eine Engine nicht aufgeführt ist, können Sie seine Definition in einer eigenen Konfigurationsdatei hinzufügen`printer.cfg`Hinzufügen dieses Abschnitts (PRs sind auch in anderen Motoren willkommen). Sie können diese Informationen auf Ihren Datenblättern finden, aber genau auf die Einheiten achten!

```ini
[motor_constants mi_motor_personalizado]
resistance: 0.00            # Ohms# Resistencia de la bobina, Ohms
inductance: 0.00            # Inductancia de la bobina, Henries
holding_torque: 0.00        # Torque de retención, Nm
max_current: 0.00           # Corriente nominal, Amperios
steps_per_revolution: 200   # Pasos por revolución (motores de 1.8° usan 200, de 0.9° usan 400)
```

Innen die Klasse`MotorConstants`Verwenden Sie diese Werte, um abgeleitete Parameter zu berechnen, z. B.:

-   Contralectromotriz -Kraftkonstante (CBEMF)
-   Motorzeit konstant (l/r)
-   PWM -Frequenz verursacht kalkaling basierend auf Induktivität
-   Optimale PWM -Werte unter Berücksichtigung von Akustikrauschen und Effizienz
-   Schwierigkeitsprävention mit niedriger Geschwindigkeit
-   Hystereseparameter an den Motor angepasst

Denken Sie daran, dass endlose Schraubmotoren häufig kein veröffentlichtes Drehmoment haben. Verwenden Sie beispielsweise einen Online -Taschenrechner, um das Drehmoment vom Schub der endlosen Schraube abzuschätzen<https://www.dingsmotionusa.com/torque-calculator>.

## Beseitigen Sie diese Klipper -Erweiterung

Kommentar zu allen Abschnitten`[autotune_tmc xxxx]`Aus seiner Konfiguration und dem Neustarten wird das Plugin vollständig deaktiviert. Sie können es so aktivieren/deaktivieren, wie Sie möchten.

Wenn Sie es vollständig deinstallieren möchten, beseitigen Sie den Abschnitt "Update Manager" von Moonraker aus Ihrer Datei`moonraker.conf`löschen Sie den Ordner`~/klipper_tmc_autotune`auf seinem Pi und starten Sie Klipper und Moonraker neu.
