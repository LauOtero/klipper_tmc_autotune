# Klipper TMC AutoTune (versão alfa)

* * *

![Español](https://flagcdn.com/w40/es.png)[![English](https://flagcdn.com/w40/gb.png)](README.en.md)[![Deutsch](https://flagcdn.com/w40/de.png)](README.de.md)[![Italiano](https://flagcdn.com/w40/it.png)](README.it.md)[![Français](https://flagcdn.com/w40/fr.png)](README.fr.md)[![Português](https://flagcdn.com/w40/pt.png)](README.pt.md)

* * *

Extensão Klipper para configuração e ajuste automáticos de TMC.

Essa extensão calcula os valores ótimos para a maioria dos registros dos drivers TMC dos mecanismos de etapa de etapa, com base nas informações da folha de informações e no alvo de ajuste selecionado pelo usuário.

Em particular, o StoralthChop ativo por padrão nos motores Z e extrusores, Coolstep sempre que possível, e muda corretamente para a etapa completa para velocidades muito altas. Quando houver vários modos disponíveis, selecione os modos mais silenciosos e menor consumo de energia, sujeito às limitações do Homing sem sensores (que não permitem certas combinações).

### Estado actual

-   Apoio oficial ao TMC2209, TMC2240 e TMC5160.
-   O suporte para TMC2130, TMC2208 e TMC2660 pode funcionar, mas não foi testado.
-   O Homing sem sensores com autotutação ativada funciona corretamente no TMC2209, TMC2240 e TMC5160, desde que a velocidade de retorno seja rápida o suficiente (Homing_speed deve ser numericamente maior que a Rotation_distância para aqueles eixos que usam a casa sem sensores). Como sempre, tenha muito cuidado ao tentar o Homing sem sensores pela primeira vez.
-   O uso do automóvel motor pode melhorar a eficiência, permitindo que eles trabalhem mais frios e consumam menos energia. No entanto, é importante ter em mente que esse processo também pode fazer com que os drivers do TMC funcionem mais quentes; portanto, as medidas de resfriamento apropriadas devem ser implementadas.
-   Sistema dinâmico de proteção térmica que ajusta a corrente em tempo real com base na temperatura do motorista e na carga do motor
-   Monitoramento avançado com amostragem a cada 100ms, incluindo detecção de sobrecarga e aumento repentino de temperatura
-   Algoritmo de resfriamento preventivo que reduz gradualmente a corrente antes de atingir os limites críticos

## Instalación

Para instalar este plug -in, execute o script de instalação usando o seguinte comando ssh. Este script baixará este repositório do GitHub para o diretório inicial do seu Raspberrypi e criará links simbólicos dos arquivos na pasta extra do Klipper.

```bash
wget -O - https://github.com/LauOtero/klipper_tmc_autotune/main/install.sh | bash
```

Em seguida, adicione o seguinte ao seu`moonraker.conf`Para ativar atualizações automáticas:

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

## Ajuste de configuração existente

As configurações de seus motoristas devem conter:

-   Pinheiros
-   Correntes (corrente operacional, corrente de retenção, corrente de homing se você usar uma versão Klipper que a suporta)
-   `interpolate: true`
-   Discuta qualquer outro ajuste de registro e valores de homing sem sensores (mantenha -os como referência, mas eles não estarão ativos)

A documentação de Klipper recomenda não usar a interpolação. No entanto, isso é mais aplicável se forem usadas contagens micrópicas baixas e a configuração predeterminada do driver. O autotune fornece melhores resultados, dimensionais e qualidade, usando interpolação e o maior número possível de micropasses.

Verifique os diagramas de pinos das placas de seus drivers: BTT TMC 2240 Placas requerem configuração`diag1_pin`e não`diag0_pin`, mas os stepsticks mks tmc 2240 exigem`diag0_pin`e_no_`diag1_pin`. Pode haver outros motoristas com configurações incomuns.

## Homing sin sensores

O autotune pode ser usado juntamente com substituições de homing para homing sem sensores. No entanto, você deve ajustar os valores`sg4_thrs`(TMC2209, TMC2260) y/o`sgt`(TMC5160, TMC2240, TMC2130, TMC2660) especificamente nas seções automáticas. Tentar essas alterações via Gcode ou nas seções do TMC do driver não gerará uma mensagem de erro, mas não terá efeito, pois o algoritmo de autotutação as substituirá.

Lembre -se também de que o ajuste do homing sem sensores provavelmente mudará devido a outros ajustes. Em particular, o autotune pode exigir velocidades mais rápidas de homing para funcionar; Pegue o`rotation_distance`do motor como uma velocidade mínima que pode funcionar e, se for difícil ajustar, torne o Homing mais rápido. Homing sem sensores se torna muito mais sensível a velocidades mais altas.

## Solução de problemas comum

### 1. Ajuste fino de sensibilidad

**Problema:** El cabezal se detiene demasiado pronto o no detecta el final de carrera.

-   **Causas:**Valores de`sgt`/`sg4_thrs`Muito baixa, indutância do mecanismo variável
-   **Solução:**
    -   Aumentar`sgt`en 2-3 unidades (TMC5160/2240)
    -   Reduzir`sg4_thrs`en 10-15 unidades (TMC2209)
    -   Verificar que`homing_speed > rotation_distance`

### 2. Configuração de velocidade ideal

**Problema:**Perda de etapas durante o homing

-   **Causas:**Velocidade muito baixa para a configuração atual
-   **Solução:**
    -   Calcule a velocidade mínima:`homing_speed = rotation_distance * 1.2`
    -   Usar`tbl: 1`e`toff: 2`Para maior estabilidade

### 3. Falsos positivos

**Problema:**Detecções errôneas durante o movimento normal

-   **Causas:**Vibrações mecânicas, corrente insuficiente
-   **Solução:**
    -   Aumentar`extra_hysteresis`en 1-2 unidades
    -   Verifique o resfriamento do motorista
    -   Garantir`voltage`configurado correctamente

### 4. Compatibilidade de parâmetros

**Importante:**Ajustes manuais em seções`[tmc2209]`o`[tmc5160]`Eles serão substituídos.

-   Sempre configure:
    -   `sgt`em`[autotune_tmc]`para TMC5160/2240
    -   `sg4_thrs`em`[autotune_tmc]`para TMC2209
    -   `homing_speed`em`[stepper_x]`(e eixos correspondentes)

## Configuração autotune

Adicione o seguinte ao seu`printer.cfg`(Altere os nomes dos motores e remova ou adicione seções conforme necessário) para ativar o automobilismo para seus drivers e motores do TMC e reinicie o Klipper:

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

## Parâmetros de seção[autotune_tmc]

Todas as seções`[autotune_tmc]`Eles aceitam os seguintes parâmetros configuráveis:

| Parâmetro          | Valor por defecto | Faixa                                      | Descrição detalhada                                                                                                                                                                                                                                       |
| ------------------ | ----------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `motor`            | _Obrigatório_     | [Ver DB](motor_database.cfg)               | Nome do mecanismo de banco de dados. Define características físicas, como resistência, indutância e torque                                                                                                                                                |
| `tuning_goal`      | `auto`            | `auto`,`silent`,`performance`,`autoswitch` | Modo de operação operacional:<br>-`auto`: Seleção automática com base no tipo de eixo<br>-`silent`: Priorize o silêncio sobre o desempenho<br>-`performance`: Velocidade máxima e torque<br>-`autoswitch`: Mudança dinâmica entre os modos (experimental) |
| `extra_hysteresis` | 0                 | 0-8                                        | Histerese adicional para reduzir a vibração. Valores> 3 podem gerar calor excessivo                                                                                                                                                                       |
| `tbl`              | 2                 | 0-3                                        | Tempo de inchaço do comparador:<br>- 0: 16 ciclos<br>- 1: 24 ciclos<br>- 2: 36 ciclos<br>- 3: 54 ciclos                                                                                                                                                   |
| `toff`             | 0                 | 0-15                                       | Tempo fora do helicóptero. 0 = cálculo automático. Valores baixos melhoram as altas velocidades                                                                                                                                                           |
| `sgt`              | 1                 | -64 A 63                                   | Sensibilidade ao homing sem sensores (TMC5160/2240). Valores negativos = maior sensibilidade                                                                                                                                                              |
| `sg4_thrs`         | 10                | 0-255                                      | Limiar combinado para Coolstep e Homing (TMC2209). Relacionamento não linear com sensibilidade real                                                                                                                                                       |
| `pwm_freq_target`  | 55kHz             | 10-60kHz                                   | Objetivo da frequência PWM. Altos valores reduzem o ruído, mas aumentam as perdas                                                                                                                                                                         |
| `voltage`          | 24V               | 0-60V                                      | Tensão real de alimentação do motor. Crítico para cálculos atuais                                                                                                                                                                                         |
| `overvoltage_vth`  | _Auto_            | 0-60V                                      | Proteção ao máximo SOOL (TMC2240/5160). É calculado como`voltage + 0.8V`Se não for especificado                                                                                                                                                           |

> **Notas importantes:**
>
> -   Parámetros sin unidad asumen valores en el sistema métrico internacional (V, A, Hz)
> -   Os valores de`sgt`e`sg4_thrs`Eles têm efeitos não lineares: pequenas mudanças podem ter grandes impactos
> -   `tuning_goal`Afeta vários parâmetros simultaneamente:
>     ```plaintext
>     silent:   toff↑, tbl↑, pwm_freq↓, extra_hysteresis↑
>     performance: toff↓, tbl↓, pwm_freq↑, extra_hysteresis↓
>     ```
>
>
> ```
>
> ```

Além disso, se necessário, você pode ajustar tudo em tempo real enquanto a impressora está trabalhando usando a macro`AUTOTUNE_TMC`no console Klipper. Todos os parâmetros anteriores estão disponíveis:

    AUTOTUNE_TMC STEPPER=<nombre> [PARÁMETRO=<valor>]

## Como funciona a automóvel

O processo AutoJuste usa as seguintes classes principais:

1.  **TMCutilidades**: Fornece funções de cálculo e otimização para configurar os drivers TMC com base nas características físicas do mecanismo. Calcule parâmetros como:
    -   Histerese ideal com base no objetivo atual e de ajuste
    -   Limiares PWM para mudança automática entre maneiras
    -   Valores de proteção de sobretensão
    -   Corrente operacional ideal

2.  **RealTimeMonitor**: Fornece monitoramento em tempo real da temperatura e carga do motor, com ajuste dinâmico da proteção térmica atual e automática.

3.  **AutoTuNetMC**: Classe principal que integra as funcionalidades acima e aplica a configuração ideal aos drivers TMC.

O algoritmo Autojuste aprimorado agora inclui:

1.  Cálculo automático de frequência PWM automática com base na indutância motora
2.  Ajuste de histerese dinâmica de acordo com a temperatura real e a carga
3.  Otimização de transição entre os modos de operação
4.  Proteção contra oscilações e ressonâncias mecânicas

O processo completo segue estas etapas:

1.  Carrega as constantes físicas do motor do banco de dados ou da configuração do usuário
2.  Determine o objetivo de ajuste (silencioso, desempenho, auto -baseado) com base no tipo de motor e na configuração
3.  Calcula los parámetros óptimos para el driver TMC específico
4.  Aplique a configuração do driver e monitore seu desempenho
5.  Ajuste dinamicamente os parâmetros conforme necessário durante a operação

Os parâmetros são otimizados especificamente para cada tipo de driver TMC, levando em consideração suas características e limitações exclusivas.

## Motores definidos pelo usuário

Os nomes dos motores e suas constantes físicas estão no arquivo[motor_database.cfg](motor_database.cfg), que é carregado automaticamente pelo script. Se um mecanismo não estiver listado, você poderá adicionar sua definição em seu próprio arquivo de configuração`printer.cfg`Adicionando esta seção (os PRs também são bem -vindos a outros motores). Você pode encontrar essas informações em suas folhas de dados, mas preste muita atenção às unidades!

```ini
[motor_constants mi_motor_personalizado]
resistance: 0.00            # Ohms# Resistencia de la bobina, Ohms
inductance: 0.00            # Inductancia de la bobina, Henries
holding_torque: 0.00        # Torque de retención, Nm
max_current: 0.00           # Corriente nominal, Amperios
steps_per_revolution: 200   # Pasos por revolución (motores de 1.8° usan 200, de 0.9° usan 400)
```

Internamente, a classe`MotorConstants`Use esses valores para calcular parâmetros derivados, como:

-   Constante de força contralectroMotriz (CBEMF)
-   Tempo do motor constante (l/r)
-   Causa da frequência PWM com base na indutância
-   Valores óptimos de PWM considerando ruido acústico y eficiencia
-   Prevenção de oscilação de baixa velocidade
-   Parámetros de hysteresis adaptados al motor

Lembre -se de que os inúmeros motores de parafusos geralmente não têm um torque publicado. Use uma calculadora on -line para estimar o torque a partir do impulso do parafuso sem fim, por exemplo<https://www.dingsmotionusa.com/torque-calculator>.

## Elimine esta extensão Klipper

Comente em todas as seções`[autotune_tmc xxxx]`A partir de sua configuração e reinicialização, o Klipper desativará completamente o plug -in. Para que você possa habilitá -lo/desativá -lo como quiser.

Se você deseja desinstalá -lo completamente, elimine a seção do gerente de atualização do Moonraker do seu arquivo`moonraker.conf`, exclua a pasta`~/klipper_tmc_autotune` en su Pi y reinicie Klipper y Moonraker.
