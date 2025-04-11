# Klipper TMC Autotune (versione Alpha)

* * *

![Español](https://flagcdn.com/w40/es.png)[![English](https://flagcdn.com/w40/gb.png)](README.en.md)[![Deutsch](https://flagcdn.com/w40/de.png)](README.de.md)[![Italiano](https://flagcdn.com/w40/it.png)](README.it.md)[![Français](https://flagcdn.com/w40/fr.png)](README.fr.md)[![Português](https://flagcdn.com/w40/pt.png)](README.pt.md)

* * *

Estensione Klipper per la configurazione e la regolazione automatica di TMC.

Questa estensione calcola i valori ottimali per la maggior parte dei record dei driver TMC dei motori a passo passo, in base alle informazioni sul foglio informativo e all'obiettivo di regolazione selezionato dall'utente.

In particolare, StealthChop attivo per impostazione predefinita nei motori e negli estrusici, il coolstep ove possibile e si trasforma correttamente a un passo completo a velocità molto elevate. Quando sono disponibili più modalità, selezionare le modalità più silenziose e il consumo di energia più basso, fatte salve i limiti dell'homing senza sensori (che non consentono determinate combinazioni).

### Stato attuale

-   Supporto ufficiale per TMC2209, TMC2240 e TMC5160.
-   Il supporto per TMC2130, TMC2208 e TMC2660 può funzionare, ma non è stato testato.
-   L'homing senza sensori con autotuning attivato funziona correttamente in TMC2209, TMC2240 e TMC5160, a condizione che la velocità di homing sia abbastanza rapida (Homing_Speed ​​deve essere numericamente più grande di rotazione_distanza per quegli assi che usano homing senza sensor). Come sempre, fai molta attenzione quando provi l'homing senza sensori per la prima volta.
-   L'uso dell'autotuning del motore può migliorare l'efficienza consentendo loro di lavorare più freddo e consumare meno energia. Tuttavia, è importante tenere presente che questo processo può anche far funzionare i conducenti TMC più caldi, quindi devono essere implementate misure di raffreddamento appropriate.
-   Sistema di protezione termica dinamica che regola la corrente in tempo reale in base alla temperatura del conducente e al carico del motore
-   Monitoraggio avanzato con campionamento ogni 100 ms, incluso il rilevamento del sovraccarico e aumenta di temperatura improvvisa
-   Algoritmo di raffreddamento preventivo che riduce gradualmente la corrente prima di raggiungere i limiti critici

## Installazione

Per installare questo plug -in, eseguire lo script di installazione utilizzando il seguente comando SSH. Questo script scaricherà questo repository GitHub nella home directory del suo Raspberrypi e creerà collegamenti simbolici dei file nella cartella extra di Klipper.

```bash
wget -O - https://github.com/LauOtero/klipper_tmc_autotune/main/install.sh | bash
```

Quindi aggiungi quanto segue al tuo`moonraker.conf`Per abilitare gli aggiornamenti automatici:

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

## Regolazione della configurazione esistente

Le configurazioni dei loro driver devono contenere:

-   Pini
-   Correnti (corrente operativa, corrente di conservazione, corrente di homing se si utilizza una versione klipper che la supporta)
-   `interpolate: true`
-   Discutere di qualsiasi altro regolazione di registrazione e valori di homing senza sensori (mantienili come riferimento, ma non saranno attivi)

La documentazione di Klipper consiglia di non utilizzare l'interpolazione. Tuttavia, questo è più applicabile se vengono utilizzati conteggi micro -bassi e la configurazione predeterminata del driver. Autotune dà risultati migliori, sia dimensionali che di qualità, usando l'interpolazione e quante più micropassi possibili.

Controlla i diagrammi dei pin delle piastre dei driver: le piastre BTT TMC 2240 richiedono la configurazione`diag1_pin`e no`diag0_pin`, ma le fasi dei passaggio MKS TMC 2240 richiedono`diag0_pin`E_NO_`diag1_pin`. Potrebbero esserci altri driver con configurazioni insolite.

## Homing senza sensori

Autotune può essere utilizzato insieme a Homing Slorarrids per Homing senza sensori. Tuttavia, è necessario regolare i valori`sg4_thrs`(TMC2209, TMC2260) Y/O.`sgt` (TMC5160, TMC2240, TMC2130, TMC2660) específicamente en las secciones de autotune. Intentar hacer estos cambios via gcode o en las secciones del driver tmc no generará un mensaje de error, pero no tendrá efecto ya que el algoritmo de autotuning los sobrescribirá.

Tieni anche presente che l'adeguamento di homing senza sensori probabilmente cambierà a causa di altre regolazioni. In particolare, l'autotune può richiedere una velocità di homing più rapide per funzionare; Prendere il`rotation_distance`del motore come una velocità minima che può funzionare e, se è difficile da regolare, rendere più veloce l'honing. L'homing senza sensori diventa molto più sensibile alle velocità più elevate.

## Soluzione del problema comune

### 1. Regolazione della sensibilità fine

**Problema:**La testa si ferma troppo presto o non rileva la fine della gara.

-   **Cause:**Valori di`sgt`/`sg4_thrs`Troppo basso, induttanza del motore variabile
-   **Soluzione:**
    -   Aumento`sgt`In 2-3 unità (TMC5160/2240)
    -   Ridurre`sg4_thrs`In 10-15 unità (TMC2209)
    -   Verifica che`homing_speed > rotation_distance`

### 2. Configurazione ottimale della velocità

**Problema:**Perdita di passaggi durante la casa

-   **Cause:**Velocità troppo bassa per la configurazione corrente
-   **Soluzione:**
    -   Calcola la velocità minima:`homing_speed = rotation_distance * 1.2`
    -   Da usare`tbl: 1`E`toff: 2`Per una maggiore stabilità

### 3. Falsi positivi

**Problema:**Rilevamenti errati durante il normale movimento

-   **Cause:**Vibrazioni meccaniche, corrente insufficiente
-   **Soluzione:**
    -   Aumento`extra_hysteresis`In 1-2 unità
    -   Verifica il raffreddamento del driver
    -   Garantire`voltage`configurato correttamente

### 4. Compatibilità dei parametri

**Importante:**Regolazioni manuali nelle sezioni`[tmc2209]`IL`[tmc5160]`Saranno sovrascritti.

-   Configura sempre:
    -   `sgt`In`[autotune_tmc]`Per TMC5160/2240
    -   `sg4_thrs`In`[autotune_tmc]`Per TMC2209
    -   `homing_speed`In`[stepper_x]`(e assi corrispondenti)

## Configurazione automatica

Aggiungi quanto segue al tuo`printer.cfg`(Modifica i nomi dei motori e rimuovi o aggiungi le sezioni se necessario) per consentire l'autotuning per i suoi driver e motori TMC e riavviare Klipper:

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

## Parametri di sezione[Autotune_tmc]

Tutte le sezioni`[autotune_tmc]`Accettano i seguenti parametri configurabili:

| Parametro          | Valore predefinito | Rango                                      | Descrizione dettagliata                                                                                                                                                                                                                                              |
| ------------------ | ------------------ | ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `motor`            | _Obbligatorio_     | [Ver db](motor_database.cfg)               | Nome del motore del database. Definisce caratteristiche fisiche come resistenza, induttanza e coppia                                                                                                                                                                 |
| `tuning_goal`      | `auto`             | `auto`,`silent`,`performance`,`autoswitch` | Modo de operación objetivo:<br>-`auto`: Selezione automatica in base al tipo di asse<br>-`silent`: Priorità al silenzio rispetto alle prestazioni<br>-`performance`: Velocità massima e coppia<br>-`autoswitch`: Cambiamento dinamico tra le modalità (sperimentale) |
| `extra_hysteresis` | 0                  | 0-8                                        | Ulteriore isteresi per ridurre le vibrazioni. Valori> 3 possono generare calore eccessivo                                                                                                                                                                            |
| `tbl`              | 2                  | 0-3                                        | Tempo di blanking del comparatore:<br>- 0: 16 cicli<br>- 1: 24 cicli<br>- 2: 36 cicli<br>- 3: 54 cicli                                                                                                                                                               |
| `toff`             | 0                  | 0-15                                       | Chopper è il tempo libero. 0 = calcolo automatico. Valori bassi migliorano le alte velocità                                                                                                                                                                          |
| `sgt`              | 1                  | -64 a 63                                   | Sensibilità di homing senza sensori (TMC5160/2240). Valori negativi = maggiore sensibilità                                                                                                                                                                           |
| `sg4_thrs`         | 10                 | 0-255                                      | Soglia combinata per coolstep e homing (TMC2209). Relazione non lineare con la vera sensibilità                                                                                                                                                                      |
| `pwm_freq_target`  | 55kHz              | 10-60kHz                                   | Obiettivo di frequenza PWM. Valori alti riducono il rumore ma aumentano le perdite                                                                                                                                                                                   |
| `voltage`          | 24 V.              | 0-60v                                      | Vera tensione di alimentazione del motore. Critico per i calcoli attuali                                                                                                                                                                                             |
| `overvoltage_vth`  | _Auto_             | 0-60v                                      | Protezione di palenza SOOL (TMC2240/5160). È calcolato come`voltage + 0.8V`Se non specificato                                                                                                                                                                        |

> **Note importanti:**
>
> -   I parametri senza unità assumono valori nel sistema metrico internazionale (V, A, HZ)
> -   I valori di`sgt`E`sg4_thrs`Hanno effetti non lineari: piccoli cambiamenti possono avere grandi impatti
> -   `tuning_goal`Colpisce contemporaneamente più parametri:
>     ```plaintext
>     silent:   toff↑, tbl↑, pwm_freq↓, extra_hysteresis↑
>     performance: toff↓, tbl↓, pwm_freq↑, extra_hysteresis↓
>     ```
>
>
> ```
>
> ```

Inoltre, se necessario, è possibile regolare tutto al volo mentre la stampante funziona utilizzando la macro`AUTOTUNE_TMC`Nella console Klipper. Tutti i parametri precedenti sono disponibili:

    AUTOTUNE_TMC STEPPER=<nombre> [PARÁMETRO=<valor>]

## Come funziona l'autoage

Il processo automatico utilizza le seguenti classi principali:

1.  **Tmcutilities**: Fornisce funzioni di calcolo e ottimizzazione per configurare i driver TMC in base alle caratteristiche fisiche del motore. Calcola parametri come:
    -   Isteresi ottimale in base alla corrente e all'obiettivo di regolazione
    -   Soglie di PWM per il cambiamento automatico tra i modi
    -   Valori di protezione da sovratensione
    -   Corrente operativa ottimale

2.  **Realtimemonitor**: Proporciona monitoreo en tiempo real de la temperatura y carga del motor, con ajuste dinámico de la corriente y protección térmica automática.

3.  **Autotunetmc**: Classe principale che integra le funzionalità di cui sopra e applica la configurazione ottimale ai driver TMC.

L'algoritmo Autojuste migliorato ora include:

1.  Calcolo automatico della frequenza PWM ottimale in base all'induttanza motoria
2.  Regolazione dinamica di isteresi in base alla temperatura e al carico reali
3.  Ottimizzazione della transizione tra le modalità operative
4.  Protezione contro le oscillazioni e le risonanze meccaniche

Il processo completo segue questi passaggi:

1.  Carica le costanti fisiche del motore dal database o dalla configurazione dell'utente
2.  Determinare l'obiettivo di regolazione (silenzioso, prestazioni, auto -basato) in base al tipo e alla configurazione del motore
3.  Calcola i parametri ottimali per driver TMC specifico
4.  Applica la configurazione del driver e monitora le prestazioni
5.  Regola dinamicamente i parametri in se necessario durante il funzionamento

I parametri sono specificamente ottimizzati per ogni tipo di driver TMC, tenendo conto delle sue caratteristiche e limitazioni uniche.

## Motori definiti dall'utente

I nomi dei motori e le loro costanti fisiche sono nel file[motor_database.cfg](motor_database.cfg), che viene automaticamente addebitato dallo script. Se un motore non è elencato, è possibile aggiungere la sua definizione nel proprio file di configurazione`printer.cfg`L'aggiunta di questa sezione (i PR sono anche benvenuti ad altri motori). Puoi trovare queste informazioni sui tuoi dati di dati, ma presta molta attenzione alle unità!

```ini
[motor_constants mi_motor_personalizado]
resistance: 0.00            # Ohms# Resistencia de la bobina, Ohms
inductance: 0.00            # Inductancia de la bobina, Henries
holding_torque: 0.00        # Torque de retención, Nm
max_current: 0.00           # Corriente nominal, Amperios
steps_per_revolution: 200   # Pasos por revolución (motores de 1.8° usan 200, de 0.9° usan 400)
```

Internamente, la clase `MotorConstants`Usa questi valori per calcolare i parametri derivati ​​come:

-   Contralectromotriz Force costante (CBEMF)
-   Costante del tempo motore (L/R)
-   Frequenza PWM Causcaling basato sull'induttanza
-   Valori PWM ottimali considerando il rumore acustico ed efficienza
-   Prevenzione dell'oscillazione a bassa velocità
-   Parametri di isteresi adattati al motore

Tieni presente che i motori a vite infiniti spesso non hanno una coppia pubblicata. Usa un calcolatore online per stimare la coppia dalla spinta della vite infinita, ad esempio<https://www.dingsmotionusa.com/torque-calculator>.

## Elimina questa estensione di Klipper

Commenta tutte le sezioni`[autotune_tmc xxxx]`Dalla sua configurazione e il riavvio Klipper disattiverà completamente il plug -in. Quindi puoi abilitarlo/disabilitarlo come vuoi.

Se vuoi disinstallarlo completamente, elimina la sezione Update Manager di Moonraker dal tuo file`moonraker.conf`, Elimina la cartella`~/klipper_tmc_autotune`sul suo Pi e riavvia Klipper e Moonraker.
