# Klipper TMC Autotune (Alpha version)

* * *

[![Español](https://flagcdn.com/w40/es.png)](README.md)[![English](https://flagcdn.com/w40/gb.png)](README.en.md)[![Deutsch](https://flagcdn.com/w40/de.png)](README.de.md)[![Italiano](https://flagcdn.com/w40/it.png)](README.it.md)[![Français](https://flagcdn.com/w40/fr.png)](README.fr.md)[![Português](https://flagcdn.com/w40/pt.png)](README.pt.md)

* * *

Klipper extension for automatic TMC configuration and adjustment.

This extension calculates optimal values ​​for most records of the TMC drivers of step -by -step engines, based on the information sheet information and the adjustment target selected by the user.

In particular, active Stealthchop by default in z engines and extrusors, coolstep where possible, and changes correctly to full step to very high speeds. When there are multiple modes available, select the quietest modes and lower energy consumption, subject to the limitations of the homing without sensors (which does not allow certain combinations).

### Current state

-   Official Support for TMC2209, TMC2240 and TMC5160.
-   Support for TMC2130, TMC2208 and TMC2660 can work, but it has not been tested.
-   The homing without sensors with activated autotuning works correctly in TMC2209, TMC2240 and TMC5160, provided that the homing speed is rapid enough (homing_speed must be numerically larger than ROTATION_DISTANCE for those axes that use homing without sensors). As always, be very careful when trying the homing without sensors for the first time.
-   The use of motor autotuning can improve efficiency allowing them to work colder and consume less energy. However, it is important to keep in mind that this process can also make TMC drivers work the most hot, so appropriate cooling measures must be implemented.
-   Dynamic thermal protection system that adjusts the current in real time based on the driver temperature and motor load
-   Advanced monitoring with sampling every 100ms, including overload detection and sudden temperature rises
-   Preventive cooling algorithm that gradually reduces the current before reaching critical limits

## Installation

To install this plugin, run the installation script using the following SSH command. This script will download this Github repository to the home directory of its Raspberrypi and create symbolic links of the files in the extra folder of Klipper.

```bash
wget -O - https://github.com/LauOtero/klipper_tmc_autotune/main/install.sh | bash
```

Then add the following to your`moonraker.conf`To enable automatic updates:

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

## Existing configuration adjustment

The configurations of their drivers must contain:

-   Pines
-   Currents (operating current, retention current, homing current if you use a Klipper version that supports it)
-   `interpolate: true`
-   Discuss any other registration adjustment and homing values ​​without sensors (keep them as a reference, but they will not be active)

Klipper's documentation recommends not using interpolation. However, this is more applicable if low micropic counts and the predetermined configuration of the driver are used. Autotune gives better results, both dimensional and quality, using interpolation and as many micropasses as possible.

Check the pins diagrams of your drivers' plates: BTT TMC 2240 plates require configuring`diag1_pin`and not`diag0_pin`, but the StepSTICKS MKS TMC 2240 require`diag0_pin`y_no_`diag1_pin`. There may be other drivers with unusual configurations.

## Homing without sensors

Autotune can be used together with Homing Overrides for Homing without sensors. However, you must adjust the values`sg4_thrs`(TMC2209, TMC2260) y/o`sgt`(TMC5160, TMC2240, TMC2130, TMC2660) specifically in the Autotune sections. Trying these changes via GCODE or in the Driver TMC sections will not generate an error message, but it will not have an effect since the autotuning algorithm will overwrite them.

Also keep in mind that the homing adjustment without sensors will probably change due to other adjustments. In particular, autotune may require faster homing speeds to function; Take the`rotation_distance`of the engine as a minimum speed that can work, and if it is difficult to adjust, make homing faster. Homing without sensors becomes much more sensitive to higher speeds.

## Common problem solution

### 1. Fine sensitivity adjustment

**Problem:**The head stops too soon or does not detect the race end.

-   **Causes:**Values ​​of`sgt`/`sg4_thrs`too low, inductance of the variable engine
-   **Solution:**
    -   Increase`sgt`In 2-3 units (TMC5160/2240)
    -   Reduce`sg4_thrs`In 10-15 units (TMC2209)
    -   Verify that`homing_speed > rotation_distance`

### 2. Optimal speed configuration

**Problem:**Loss of steps during the homing

-   **Causes:**Too low speed for current configuration
-   **Solution:**
    -   Calculate minimum speed:`homing_speed = rotation_distance * 1.2`
    -   To use`tbl: 1`y`toff: 2`For greater stability

### 3. False positives

**Problem:**Erroneous detections during normal movement

-   **Causes:**Mechanical vibrations, insufficient current
-   **Solution:**
    -   Increase`extra_hysteresis`In 1-2 units
    -   Verify driver cooling
    -   Ensure`voltage`correctly configured

### 4. Parameter compatibility

**Important:**Manual adjustments in sections`[tmc2209]`o`[tmc5160]`They will be overwritten.

-   Always configure:
    -   `sgt`in`[autotune_tmc]`For TMC5160/2240
    -   `sg4_thrs`in`[autotune_tmc]`For TMC2209
    -   `homing_speed`in`[stepper_x]`(and corresponding axes)

## Autotune configuration

Add the following to your`printer.cfg`(Change the names of engines and remove or add sections as necessary) to enable autotuning for its TMC drivers and motors, and restart Klipper:

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

## Section parameters[autotune_tmc]

All sections`[autotune_tmc]`They accept the following configurable parameters:

| Parameter          | Default value | Range                                      | Detailed description                                                                                                                                                                                                                     |
| ------------------ | ------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `motor`            | _Mandatory_   | [Ver DB](motor_database.cfg)               | Name of the database engine. Defines physical characteristics such as resistance, inductance and torque                                                                                                                                  |
| `tuning_goal`      | `auto`        | `auto`,`silent`,`performance`,`autoswitch` | OPERATING OPERATION MODE:<br>-`auto`: Automatic selection based on axis type<br>-`silent`: Prioritize silence over performance<br>-`performance`: Maximum speed and torque<br>-`autoswitch`: Dynamic change between modes (experimental) |
| `extra_hysteresis` | 0             | 0-8                                        | Additional hysteresis to reduce vibration. Values> 3 can generate excessive heat                                                                                                                                                         |
| `tbl`              | 2             | 0-3                                        | Comparator's Blanking Time:<br>- 0: 16 cycles<br>- 1: 24 cycles<br>- 2: 36 cycles<br>- 3: 54 cycles                                                                                                                                      |
| `toff`             | 0             | 0-15                                       | Chopper's off time. 0 = automatic calculation. Low values ​​improve high speeds                                                                                                                                                          |
| `sgt`              | 1             | -64 a 63                                   | Homing sensitivity without sensors (TMC5160/2240). Negative values ​​= greater sensitivity                                                                                                                                               |
| `sg4_thrs`         | 10            | 0-255                                      | Combined threshold for Coolstep and Homing (TMC2209). Non -linear relationship with real sensitivity                                                                                                                                     |
| `pwm_freq_target`  | 55kHz         | 10-60kHz                                   | PWM Frequency Objective. High values ​​reduce noise but increase losses                                                                                                                                                                  |
| `voltage`          | 24V           | 0-60V                                      | Real engine feed voltage. Critic for current calculations                                                                                                                                                                                |
| `overvoltage_vth`  | _Auto_        | 0-60V                                      | OVERTISING PROTECTION SOOL (TMC2240/5160). It is calculated as`voltage + 0.8V`If not specified                                                                                                                                           |

> **IMPORTANT NOTES:**
>
> -   Parameters without unity assume values ​​in the international metric system (V, A, Hz)
> -   The values ​​of`sgt`y`sg4_thrs`They have non -linear effects: small changes can have great impacts
> -   `tuning_goal`It affects multiple parameters simultaneously:
>     ```plaintext
>     silent:   toff↑, tbl↑, pwm_freq↓, extra_hysteresis↑
>     performance: toff↓, tbl↓, pwm_freq↑, extra_hysteresis↓
>     ```
>
>
> ```
>
> ```

In addition, if necessary, you can adjust everything on the fly while the printer is working using the macro`AUTOTUNE_TMC`in the Klipper console. All previous parameters are available:

    AUTOTUNE_TMC STEPPER=<nombre> [PARÁMETRO=<valor>]

## How the autoage works

The autojuste process uses the following main classes:

1.  **TMCUtilities**: Provides calculation and optimization functions to configure TMC drivers based on the physical characteristics of the engine. Calculate parameters such as:
    -   Optimal Hysteresis based on the current and the adjustment objective
    -   PWM thresholds for automatic change between ways
    -   Overvoltage protection values
    -   Optimal operating current

2.  **RealTimeMonitor**: Provides real time monitoring of the temperature and load of the engine, with dynamic adjustment of the current and automatic thermal protection.

3.  **AutotuneTMC**: Main class that integrates the above functionalities and applies the optimal configuration to TMC drivers.

The improved autojuste algorithm now includes:

1.  Automatic Optimal PWM frequency calculation based on motor inductance
2.  Dynamic Hysteresis adjustment according to real temperature and load
3.  Transition optimization between operation modes
4.  Protection against oscillations and mechanical resonances

The complete process follows these steps:

1.  Loads the physical constants of the engine from the database or the user configuration
2.  Determine the adjustment objective (silent, performance, self -based) based on the engine type and configuration
3.  Calculate the optimal parameters for specific TMC driver
4.  Apply the driver configuration and monitor your performance
5.  Dynamically adjust the parameters as necessary during operation

The parameters are specifically optimized for each type of TMC driver, taking into account its unique characteristics and limitations.

## User -defined engines

The names of the engines and their physical constants are in the file[motor_database.cfg](motor_database.cfg), which is automatically charged by the script. If an engine is not listed, you can add its definition in its own configuration file`printer.cfg`Adding this section (PRS are also welcome to other engines). You can find this information on your data sheets, but pay close attention to the units!

```ini
[motor_constants mi_motor_personalizado]
resistance: 0.00            # Ohms# Resistencia de la bobina, Ohms
inductance: 0.00            # Inductancia de la bobina, Henries
holding_torque: 0.00        # Torque de retención, Nm
max_current: 0.00           # Corriente nominal, Amperios
steps_per_revolution: 200   # Pasos por revolución (motores de 1.8° usan 200, de 0.9° usan 400)
```

Internally, the class`MotorConstants`Use these values ​​to calculate derived parameters such as:

-   Contralectromotriz Force constant (CBEMF)
-   Motor time constant (l/r)
-   PWM frequency causcaling based on inductance
-   Optimal PWM values ​​considering acoustic noise and efficiency
-   Low speed oscillation prevention
-   Hysteresis parameters adapted to the engine

Keep in mind that endless screw engines often do not have a published torque. Use an online calculator to estimate the torque from the thrust of the endless screw, for example<https://www.dingsmotionusa.com/torque-calculator>.

## Eliminate this Klipper extension

Comment on all sections`[autotune_tmc xxxx]`From its configuration and restart Klipper will completely deactivate the plugin. So you can enable/disable it as you want.

If you want to uninstall it completely, eliminate the UPDATE manager section of Moonraker from your file`moonraker.conf`, delete the folder`~/klipper_tmc_autotune`on his pi and restart Klipper and Moonraker.
