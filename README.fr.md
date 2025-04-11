# Klipper TMC AutoTune (version alpha)

* * *

![Español](https://flagcdn.com/w40/es.png)[![English](https://flagcdn.com/w40/gb.png)](README.en.md)[![Deutsch](https://flagcdn.com/w40/de.png)](README.de.md)[![Italiano](https://flagcdn.com/w40/it.png)](README.it.md)[![Français](https://flagcdn.com/w40/fr.png)](README.fr.md)[![Português](https://flagcdn.com/w40/pt.png)](README.pt.md)

* * *

Extension Klipper pour la configuration et le réglage du TMC automatique.

Cette extension calcule des valeurs optimales pour la plupart des enregistrements des pilotes TMC des moteurs à pas de pas, en fonction des informations sur la fiche d'information et de la cible de réglage sélectionnée par l'utilisateur.

En particulier, la furtivité active par défaut dans les moteurs et extrusteurs Z, CoolStep dans la mesure du possible, et change correctement en étape complète vers des vitesses très élevées. Lorsqu'il existe plusieurs modes disponibles, sélectionnez les modes les plus calmes et la consommation d'énergie inférieure, sous réserve des limitations du homing sans capteurs (ce qui ne permet pas certaines combinaisons).

### État actuel

-   Support officiel pour TMC2209, TMC2240 et TMC5160.
-   La prise en charge de TMC2130, TMC2208 et TMC2660 peut fonctionner, mais elle n'a pas été testée.
-   Le retour sans capteurs avec autotuning activé fonctionne correctement dans TMC2209, TMC2240 et TMC5160, à condition que la vitesse de homing soit suffisamment rapide (Homing_Speed ​​doit être numériquement plus grand que Rotation_Distance pour les axes qui utilisent le homing sans capteurs). Comme toujours, soyez très prudent lorsque vous essayez le homing sans capteurs pour la première fois.
-   L'utilisation de l'autotuning moteur peut améliorer l'efficacité, ce qui leur permet de travailler plus froid et de consommer moins d'énergie. Cependant, il est important de garder à l'esprit que ce processus peut également faire fonctionner les conducteurs TMC les plus chauds, de sorte que des mesures de refroidissement appropriées doivent être mises en œuvre.
-   Système de protection thermique dynamique qui ajuste le courant en temps réel en fonction de la température du conducteur et de la charge du moteur
-   Surveillance avancée avec échantillonnage toutes les 100 ms, y compris la détection de surcharge et la température soudaine augmente
-   Algorithme de refroidissement préventif qui réduit progressivement le courant avant d'atteindre les limites critiques

## Installation

Pour installer ce plugin, exécutez le script d'installation à l'aide de la commande SSH suivante. Ce script téléchargera ce référentiel GitHub dans le répertoire domestique de son RaspberryPI et créera des liens symboliques des fichiers dans le dossier supplémentaire de Klipper.

```bash
wget -O - https://github.com/LauOtero/klipper_tmc_autotune/main/install.sh | bash
```

Puis ajoutez ce qui suit à votre`moonraker.conf`Pour activer les mises à jour automatiques:

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

## Réglage de la configuration existant

Les configurations de leurs pilotes doivent contenir:

-   Pins
-   Courants (courant d'exploitation, courant de rétention, courant de retour à l'atterrissage si vous utilisez une version Klipper qui le prend en charge)
-   `interpolate: true`
-   Discutez de tout autre ajustement d'enregistrement et des valeurs de retour sans capteurs (gardez-les comme référence, mais ils ne seront pas actifs)

La documentation de Klipper recommande de ne pas utiliser d'interpolation. Cependant, cela est plus applicable si un faible nombre de micropiques et la configuration prédéterminée du pilote sont utilisées. AutoTune donne de meilleurs résultats, à la fois dimensionnels et de qualité, en utilisant l'interpolation et autant de micropasse que possible.

Vérifiez les diagrammes des broches des plaques de vos pilotes: les plaques BTT TMC 2240 nécessitent une configuration`diag1_pin`et pas`diag0_pin`, mais les beaux-pieds MKS TMC 2240 nécessitent`diag0_pin`et_Non_`diag1_pin`. Il peut y avoir d'autres pilotes avec des configurations inhabituelles.

## Horming sans capteurs

AutoTune peut être utilisé avec des remplacements de renverser pour le retour sans capteurs. Cependant, vous devez ajuster les valeurs`sg4_thrs`(TMC2209, TMC2260) O / O`sgt`(TMC5160, TMC2240, TMC2130, TMC2660) spécifiquement dans les sections automatique. Essayer ces modifications via GCODE ou dans les sections TMC du pilote ne générera pas de message d'erreur, mais il n'aura pas d'effet car l'algorithme de mise à jour les écrasera.

Gardez également à l'esprit que le réglage des homing sans capteurs changera probablement en raison d'autres ajustements. En particulier, AutoTune peut nécessiter des vitesses de renverser plus rapides pour fonctionner; Prendre le`rotation_distance`du moteur comme une vitesse minimale qui peut fonctionner, et s'il est difficile à régler, accélérez le retour plus rapidement. Le retour sans capteurs devient beaucoup plus sensible aux vitesses plus élevées.

## Solution de problème commun

### 1. Réglage de la sensibilité fine

**Problème:**La tête s'arrête trop tôt ou ne détecte pas la fin de la course.

-   **Causes:**Des valeurs`sgt`/`sg4_thrs`Trop bas, inductance du moteur variable
-   **Solution:**
    -   Augmenter`sgt`En 2-3 unités (TMC5160 / 2240)
    -   Réduire`sg4_thrs`EN 10-15 unités (TMC2209)
    -   Vérifiez que`homing_speed > rotation_distance`

### 2. Configuration de vitesse optimale

**Problème:**Perte des étapes pendant le homing

-   **Causes:**Trop basse vitesse pour la configuration actuelle
-   **Solution:**
    -   Calculer la vitesse minimale:`homing_speed = rotation_distance * 1.2`
    -   Pour utiliser`tbl: 1`et`toff: 2`Pour une plus grande stabilité

### 3. Faux positifs

**Problème:**Détections erronées pendant le mouvement normal

-   **Causes:**Vibrations mécaniques, courant insuffisant
-   **Solution:**
    -   Augmenter`extra_hysteresis`En 1-2 unités
    -   Vérifiez le refroidissement du conducteur
    -   Assurer`voltage`correctement configuré

### 4. Compatibilité des paramètres

**Importante:**Ajustements manuels en sections`[tmc2209]`le`[tmc5160]`Ils seront écrasés.

-   Configurez toujours:
    -   `sgt`en`[autotune_tmc]`Pour TMC5160 / 2240
    -   `sg4_thrs`en`[autotune_tmc]`Pour TMC2209
    -   `homing_speed`en`[stepper_x]`(et axes correspondants)

## Configuration automatique

Ajoutez ce qui suit à votre`printer.cfg`(Modifiez les noms des moteurs et supprimez ou ajoutez des sections si nécessaire) pour activer la mise à jour pour ses pilotes et moteurs TMC, et redémarrez Klipper:

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

## Paramètres de section[autotune_tmc]

Toutes les sections`[autotune_tmc]`Ils acceptent les paramètres configurables suivants:

| Paramètre          | Valeur par défaut | Gamme                                      | Description détaillée                                                                                                                                                                                                                                                          |
| ------------------ | ----------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `motor`            | _Obligatoire_     | [Ver db](motor_database.cfg)               | Nom du moteur de la base de données. Définit les caractéristiques physiques telles que la résistance, l'inductance et le couple                                                                                                                                                |
| `tuning_goal`      | `auto`            | `auto`,`silent`,`performance`,`autoswitch` | Mode de fonctionnement de fonctionnement:<br>-`auto`: Sélection automatique basée sur le type d'axe<br>-`silent`: Prioriser le silence sur les performances<br>-`performance`: Vitesse et couple maximum<br>-`autoswitch`: Changement dynamique entre les modes (expérimental) |
| `extra_hysteresis` | 0                 | 0-8                                        | Hystérésis supplémentaire pour réduire les vibrations. Les valeurs> 3 peuvent générer une chaleur excessive                                                                                                                                                                    |
| `tbl`              | 2                 | 0-3                                        | Temps de bloque du comparateur:<br>- 0: 16 cycles<br>- 1: 24 cycles<br>- 2: 36 cycles<br>- 3: 54 cycles                                                                                                                                                                        |
| `toff`             | 0                 | 0-15                                       | L'hopper est le temps de désactivation. 0 = calcul automatique. Les valeurs faibles améliorent les vitesses élevées                                                                                                                                                            |
| `sgt`              | 1                 | -64 A 63                                   | Sensibilité à la conduite sans capteurs (TMC5160 / 2240). Valeurs négatives = plus grande sensibilité                                                                                                                                                                          |
| `sg4_thrs`         | 10                | 0-255                                      | Seuil combiné pour Coolstep et Homing (TMC2209). Relation non linéaire avec une véritable sensibilité                                                                                                                                                                          |
| `pwm_freq_target`  | 55 kHz            | 10-60 kHz                                  | Objectif de fréquence PWM. Des valeurs élevées réduisent le bruit mais augmentent les pertes                                                                                                                                                                                   |
| `voltage`          | 24V               | 0-60v                                      | Véritable tension d'alimentation du moteur. Critique pour les calculs actuels                                                                                                                                                                                                  |
| `overvoltage_vth`  | _Auto_            | 0-60v                                      | Protection de la protection SOOL (TMC2240 / 5160). Il est calculé comme`voltage + 0.8V`Si non spécifié                                                                                                                                                                         |

> **Remarques importantes:**
>
> -   Les paramètres sans unité supposent des valeurs dans le système métrique international (V, A, Hz)
> -   Les valeurs de`sgt`et`sg4_thrs`Ils ont des effets non linéaires: les petits changements peuvent avoir de grands impacts
> -   `tuning_goal`Il affecte simultanément plusieurs paramètres:
>     ```plaintext
>     silent:   toff↑, tbl↑, pwm_freq↓, extra_hysteresis↑
>     performance: toff↓, tbl↓, pwm_freq↑, extra_hysteresis↓
>     ```
>
>
> ```
>
> ```

De plus, si nécessaire, vous pouvez tout ajuster à la volée pendant que l'imprimante fonctionne en utilisant la macro`AUTOTUNE_TMC`dans la console Klipper. Tous les paramètres précédents sont disponibles:

    AUTOTUNE_TMC STEPPER=<nombre> [PARÁMETRO=<valor>]

## Comment fonctionne l'autoage

Le processus automatique utilise les principales classes suivantes:

1.  **Tmcuties**: Fournit des fonctions de calcul et d'optimisation pour configurer les pilotes TMC en fonction des caractéristiques physiques du moteur. Calculez des paramètres tels que:
    -   Hystérésis optimale basé sur le courant et l'objectif d'ajustement
    -   Seuils PWM pour le changement automatique entre les moyens
    -   Valeurs de protection contre la surtension
    -   Courant de fonctionnement optimal

2.  **RealTimemonitor**: Fournit une surveillance en temps réel de la température et de la charge du moteur, avec un réglage dynamique de la protection thermique actuelle et automatique.

3.  **Autotunetmc**: Classe principale qui intègre les fonctionnalités ci-dessus et applique la configuration optimale aux pilotes TMC.

L'algorithme AutoJuste amélioré comprend désormais:

1.  Calcul de fréquence PWM optimal automatique basé sur l'inductance du moteur
2.  Réglage de l'hystérésis dynamique en fonction de la température et de la charge réelles
3.  Optimisation de transition entre les modes d'opération
4.  Protection contre les oscillations et les résonances mécaniques

Le processus complet suit ces étapes:

1.  Charge les constantes physiques du moteur à partir de la base de données ou de la configuration de l'utilisateur
2.  Déterminez l'objectif d'ajustement (silencieux, performances, auto-basé) en fonction du type de moteur et de la configuration
3.  Calculez les paramètres optimaux pour un pilote TMC spécifique
4.  Appliquez la configuration du pilote et surveillez vos performances
5.  Ajustez dynamiquement les paramètres si nécessaire pendant le fonctionnement

Les paramètres sont spécifiquement optimisés pour chaque type de pilote TMC, en tenant compte de ses caractéristiques et limitations uniques.

## Moteurs définis par l'utilisateur

Les noms des moteurs et leurs constantes physiques sont dans le fichier[moteur_database.cfg](motor_database.cfg), qui est automatiquement chargé par le script. Si un moteur n'est pas répertorié, vous pouvez ajouter sa définition dans son propre fichier de configuration`printer.cfg`Ajout de cette section (les PR sont également les bienvenus à d'autres moteurs). Vous pouvez trouver ces informations sur vos fiches techniques, mais prêter une attention particulière aux unités!

```ini
[motor_constants mi_motor_personalizado]
resistance: 0.00            # Ohms# Resistencia de la bobina, Ohms
inductance: 0.00            # Inductancia de la bobina, Henries
holding_torque: 0.00        # Torque de retención, Nm
max_current: 0.00           # Corriente nominal, Amperios
steps_per_revolution: 200   # Pasos por revolución (motores de 1.8° usan 200, de 0.9° usan 400)
```

En interne, la classe`MotorConstants`Utilisez ces valeurs pour calculer les paramètres dérivés tels que:

-   Constante de force de la Contralectromotriz (CBEMF)
-   Temps de moteur constant (L / R)
-   PWM Fréquence causalation basée sur l'inductance
-   Valeurs PWM optimales en considérant le bruit et l'efficacité acoustiques
-   Prévention de l'oscillation à basse vitesse
-   Paramètres d'hystérésis adaptés au moteur

Gardez à l'esprit que les moteurs à vis sans fin n'ont souvent pas de couple publié. Utilisez une calculatrice en ligne pour estimer le couple de la poussée de la vis sans fin, par exemple<https://www.dingsmotionusa.com/torque-calculator>.

## Éliminez cette extension Klipper

Commentez toutes les sections`[autotune_tmc xxxx]`Depuis sa configuration et le redémarrage, Klipper désactivera complètement le plugin. Vous pouvez donc l'activer / le désactiver comme vous le souhaitez.

Si vous souhaitez le désinstaller complètement, éliminez la section de mise à jour de Moonraker à partir de votre fichier`moonraker.conf`, supprimez le dossier`~/klipper_tmc_autotune`Sur son Pi et redémarrez Klipper et Moonraker.
