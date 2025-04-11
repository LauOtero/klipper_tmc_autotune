# Klipper TMC Autotune (Versión Alpha)

---
[![Español](https://flagcdn.com/w40/es.png)](README.md) [![English](https://flagcdn.com/w40/gb.png)](README.en.md) [![Deutsch](https://flagcdn.com/w40/de.png)](README.de.md) [![Italiano](https://flagcdn.com/w40/it.png)](README.it.md) [![Français](https://flagcdn.com/w40/fr.png)](README.fr.md) [![Português](https://flagcdn.com/w40/pt.png)](README.pt.md)

---

Extensión de Klipper para la configuración y ajuste automático de drivers TMC.

Esta extensión calcula valores óptimos para la mayoría de los registros de los drivers TMC de motores paso a paso, basándose en la información de la hoja de datos del motor y el objetivo de ajuste seleccionado por el usuario.

En particular, activa StealthChop por defecto en los motores Z y extrusores, CoolStep donde sea posible, y cambia correctamente al modo de paso completo a velocidades muy altas. Cuando hay múltiples modos disponibles, selecciona los modos más silenciosos y de menor consumo de energía, sujeto a las limitaciones del homing sin sensores (que no permite ciertas combinaciones).

### Estado actual

- Soporte oficial para TMC2209, TMC2240 y TMC5160.
- Soporte para TMC2130, TMC2208 y TMC2660 puede funcionar, pero no ha sido probado.
- El homing sin sensores con autotuning activado funciona correctamente en TMC2209, TMC2240 y TMC5160, siempre que la velocidad de homing sea suficientemente rápida (homing_speed debe ser numéricamente mayor que rotation_distance para esos ejes que usan homing sin sensores). Como siempre, tenga mucho cuidado al probar el homing sin sensores por primera vez.
- El uso de autotuning para los motores puede mejorar la eficiencia permitiendo que funcionen más fríos y consuman menos energía. Sin embargo, es importante tener en cuenta que este proceso también puede hacer que los drivers TMC funcionen más calientes, por lo que se deben implementar medidas de refrigeración adecuadas.
- Sistema de protección térmica dinámica que ajusta la corriente en tiempo real basado en la temperatura del driver y la carga del motor
- Monitoreo avanzado con muestreo cada 100ms, incluyendo detección de sobrecargas y subidas bruscas de temperatura
- Algoritmo de enfriamiento preventivo que reduce gradualmente la corriente antes de alcanzar límites críticos

## Instalación

Para instalar este plugin, ejecute el script de instalación usando el siguiente comando por SSH. Este script descargará este repositorio de GitHub al directorio home de su RaspberryPi y creará enlaces simbólicos de los archivos en la carpeta extra de Klipper.

```bash
wget -O - https://github.com/LauOtero/klipper_tmc_autotune/main/install.sh | bash
```

Luego, agregue lo siguiente a su `moonraker.conf` para habilitar actualizaciones automáticas:

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

## Ajuste de configuración existente

Las configuraciones de sus drivers deben contener:

- Pines
- Corrientes (corriente de funcionamiento, corriente de retención, corriente de homing si usa una versión de Klipper que lo soporte)
- `interpolate: true`
- Comente cualquier otro ajuste de registro y valores de homing sin sensores (manténgalos como referencia, pero no estarán activos)

La documentación de Klipper recomienda no usar interpolación. Sin embargo, esto es más aplicable si se usan conteos de micropasos bajos y la configuración predeterminada del driver. Autotune da mejores resultados, tanto dimensionales como de calidad, usando interpolación y tantos micropasos como sea posible.

Verifique los diagramas de pines de sus placas de drivers: las placas BTT TMC 2240 requieren configurar `diag1_pin` y no `diag0_pin`, pero los stepsticks MKS TMC 2240 requieren `diag0_pin` y *no* `diag1_pin`. Puede haber otros drivers con configuraciones inusuales.

## Homing sin sensores

Autotune puede usarse junto con homing overrides para homing sin sensores. Sin embargo, debe ajustar los valores `sg4_thrs` (TMC2209, TMC2260) y/o `sgt` (TMC5160, TMC2240, TMC2130, TMC2660) específicamente en las secciones de autotune. Intentar hacer estos cambios via gcode o en las secciones del driver tmc no generará un mensaje de error, pero no tendrá efecto ya que el algoritmo de autotuning los sobrescribirá.

También tenga en cuenta que el ajuste del homing sin sensores probablemente cambiará debido a otros ajustes. En particular, autotune puede requerir velocidades de homing más rápidas para funcionar; tome el `rotation_distance` del motor como velocidad mínima que puede funcionar, y si es difícil de ajustar, haga homing más rápido. El homing sin sensores se vuelve mucho más sensible a velocidades más altas.

## Solución de Problemas Comunes

### 1. Ajuste fino de sensibilidad

**Problema:** El cabezal se detiene demasiado pronto o no detecta el final de carrera.

- **Causas:** Valores de `sgt`/`sg4_thrs` demasiado bajos, inductancia del motor variable
- **Solución:**
  - Aumentar `sgt` en 2-3 unidades (TMC5160/2240)
  - Reducir `sg4_thrs` en 10-15 unidades (TMC2209)
  - Verificar que `homing_speed > rotation_distance`

### 2. Configuración óptima de velocidad

**Problema:** Pérdida de pasos durante el homing

- **Causas:** Velocidad demasiado baja para la configuración actual
- **Solución:**
  - Calcular velocidad mínima: `homing_speed = rotation_distance * 1.2`
  - Usar `tbl: 1` y `toff: 2` para mayor estabilidad

### 3. Falsos positivos

**Problema:** Detecciones erróneas durante el movimiento normal

- **Causas:** Vibraciones mecánicas, corriente insuficiente
- **Solución:**
  - Aumentar `extra_hysteresis` en 1-2 unidades
  - Verificar refrigeración del driver
  - Asegurar `voltage` configurado correctamente

### 4. Compatibilidad de parámetros

**Importante:** Los ajustes manuales en secciones `[tmc2209]` o `[tmc5160]` serán sobrescritos.

- Siempre configure:
  - `sgt` en `[autotune_tmc]` para TMC5160/2240
  - `sg4_thrs` en `[autotune_tmc]` para TMC2209
  - `homing_speed` en `[stepper_x]` (y ejes correspondientes)

## Configuración de Autotune

Agregue lo siguiente a su `printer.cfg` (cambie los nombres de motores y elimine o agregue secciones según sea necesario) para habilitar el autotuning para sus drivers TMC y motores, y reinicie Klipper:

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

## Parámetros de la sección [autotune_tmc]

Todas las secciones `[autotune_tmc]` aceptan los siguientes parámetros configurables:

| Parámetro | Valor por defecto | Rango | Descripción Detallada |
| --- | --- | --- | --- |
| `motor` | *Obligatorio* | [Ver DB](motor_database.cfg) | Nombre del motor de la base de datos. Define características físicas como resistencia, inductancia y torque |
| `tuning_goal` | `auto` | `auto`, `silent`, `performance`, `autoswitch` | Modo de operación objetivo:<br>- `auto`: Selección automática basada en tipo de eje<br>- `silent`: Prioriza silencio sobre rendimiento<br>- `performance`: Máxima velocidad y torque<br>- `autoswitch`: Cambio dinámico entre modos (experimental) |
| `extra_hysteresis` | 0 | 0-8 | Histeresis adicional para reducir vibración. Valores >3 pueden generar calor excesivo |
| `tbl` | 2 | 0-3 | Tiempo de blanking del comparador:<br>- 0: 16 ciclos<br>- 1: 24 ciclos<br>- 2: 36 ciclos<br>- 3: 54 ciclos |
| `toff` | 0 | 0-15 | Tiempo de apagado del chopper. 0 = cálculo automático. Valores bajos mejoran altas velocidades |
| `sgt` | 1 | -64 a 63 | Sensibilidad de homing sin sensores (TMC5160/2240). Valores negativos=mayor sensibilidad |
| `sg4_thrs` | 10 | 0-255 | Umbral combinado para CoolStep y homing (TMC2209). Relación no lineal con la sensibilidad real |
| `pwm_freq_target` | 55kHz | 10-60kHz | Frecuencia PWM objetivo. Valores altos reducen ruido pero aumentan pérdidas |
| `voltage` | 24V | 0-60V | Voltaje real de alimentación del motor. Crítico para cálculos de corriente |
| `overvoltage_vth` | *Auto* | 0-60V | Umbral de protección contra sobretensión (TMC2240/5160). Se calcula como `voltage + 0.8V` si no se especifica |

>**Notas importantes:**
>- Parámetros sin unidad asumen valores en el sistema métrico internacional (V, A, Hz)
>- Los valores de `sgt` y `sg4_thrs` tienen efectos no lineales: pequeños cambios pueden tener grandes impactos
>- `tuning_goal` afecta múltiples parámetros simultáneamente:
>  ```plaintext
>  silent:   toff↑, tbl↑, pwm_freq↓, extra_hysteresis↑
>  performance: toff↓, tbl↓, pwm_freq↑, extra_hysteresis↓
>```

Además, si es necesario, puede ajustar todo sobre la marcha mientras la impresora está funcionando usando la macro `AUTOTUNE_TMC` en la consola de Klipper. Todos los parámetros anteriores están disponibles:

```
AUTOTUNE_TMC STEPPER=<nombre> [PARÁMETRO=<valor>]
```

## Cómo funciona el autoajuste

El proceso de autoajuste utiliza las siguientes clases principales:

1. **TMCUtilities**: Proporciona funciones de cálculo y optimización para configurar los drivers TMC basándose en las características físicas del motor. Calcula parámetros como:
   - Hysteresis óptima basada en la corriente y el objetivo de ajuste
   - Umbrales PWM para cambio automático entre modos
   - Valores de protección contra sobretensión
   - Corriente de funcionamiento óptima

2. **RealTimeMonitor**: Proporciona monitoreo en tiempo real de la temperatura y carga del motor, con ajuste dinámico de la corriente y protección térmica automática.

3. **AutotuneTMC**: Clase principal que integra las funcionalidades anteriores y aplica la configuración óptima a los drivers TMC.

El algoritmo mejorado de autoajuste ahora incluye:

1. Cálculo automático de frecuencia PWM óptima basado en inductancia del motor
2. Ajuste dinámico de hysteresis según temperatura y carga reales
3. Optimización de transiciones entre modos de operación
4. Protección contra oscilaciones y resonancias mecánicas

El proceso completo sigue estos pasos:

1. Carga las constantes físicas del motor desde la base de datos o la configuración del usuario
2. Determina el objetivo de ajuste (silent, performance, autoswitch) basado en el tipo de motor y la configuración
3. Calcula los parámetros óptimos para el driver TMC específico
4. Aplica la configuración al driver y monitorea su rendimiento
5. Ajusta dinámicamente los parámetros según sea necesario durante el funcionamiento

Los parámetros se optimizan específicamente para cada tipo de driver TMC, teniendo en cuenta sus características únicas y limitaciones.

## Motores definidos por el usuario

Los nombres de los motores y sus constantes físicas están en el archivo [motor_database.cfg](motor_database.cfg), que es cargado automáticamente por el script. Si un motor no está listado, puede agregar su definición en su propio archivo de configuración `printer.cfg` agregando esta sección (también son bienvenidos PRs para otros motores). Puede encontrar esta información en sus hojas de datos, pero preste mucha atención a las unidades!

```ini
[motor_constants mi_motor_personalizado]
resistance: 0.00            # Ohms# Resistencia de la bobina, Ohms
inductance: 0.00            # Inductancia de la bobina, Henries
holding_torque: 0.00        # Torque de retención, Nm
max_current: 0.00           # Corriente nominal, Amperios
steps_per_revolution: 200   # Pasos por revolución (motores de 1.8° usan 200, de 0.9° usan 400)
```

Internamente, la clase `MotorConstants` utiliza estos valores para calcular parámetros derivados como:

- Constante de fuerza contraelectromotriz (cbemf)
- Constante de tiempo del motor (L/R)
- Autoscaling de frecuencia PWM basado en inductancia
- Valores óptimos de PWM considerando ruido acústico y eficiencia
- Prevención de oscilaciones en bajas velocidades
- Parámetros de hysteresis adaptados al motor

Tenga en cuenta que los motores de tornillo sinfín a menudo no tienen un torque publicado. Use una calculadora en línea para estimar el torque a partir del empuje del tornillo sinfín, por ejemplo <https://www.dingsmotionusa.com/torque-calculator>.

## Eliminar esta extensión de Klipper

Comentar todas las secciones `[autotune_tmc xxxx]` de su configuración y reiniciar Klipper desactivará completamente el plugin. Así que puede habilitarlo/deshabilitarlo como desee.

Si quiere desinstalarlo completamente, elimine la sección del update manager de moonraker de su archivo `moonraker.conf`, borre la carpeta `~/klipper_tmc_autotune` en su Pi y reinicie Klipper y Moonraker.
