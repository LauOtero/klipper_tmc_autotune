import math
import logging
from typing import Tuple, Optional, Dict, Any, Union

# Base de datos de motores, contiene especificaciones para motores paso a paso.

# R es la resistencia de la bobina, Ohms
# L es la inductancia de la bobina, Henrios
# T es el par de retención, Nm (cuidado con las unidades aquí)
# I es la corriente nominal, Amperios

# Constantes para los cálculos
DEFAULT_FCLK = 12.5e6           # Frecuencia de reloj por defecto en Hz
DEFAULT_VOLTAGE = 24.0          # Tensión por defecto en V
PWM_GRAD_FACTOR = 1.46          # Factor utilizado en el cálculo de pwmgrad
PWM_OFS_FACTOR = 374            # Factor utilizado en el cálculo del pwmofs
MAX_PWM_VALUE = 255             # Valor PWM máximo
DEFAULT_STEPS = 200             # Pasos por revolución predeterminados para motores paso a paso estándar
MIN_INDUCTANCE = 0.0001         # Valor mínimo de inductancia para evitar la división por cero
MIN_CURRENT = 0.001             # Valor mínimo de corriente para evitar la división por cero


class MotorConstants:
    """Clase para manejar constantes de motores paso a paso y cálculos.
    
    Esta clase provee métodos para calcular varios parámetros de drivers TMC
    basados en especificaciones del motor. Maneja validación de parámetros de entrada
    y provee cálculos optimizados para configuración de drivers TMC.
    """
    
    def __init__(self, config):
        """Inicializa constantes del motor desde configuración.
        
        Args:
            config: Objeto de configuración con especificaciones del motor
        """
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        
        # Load basic motor parameters
        self._R = config.getfloat('resistance', minval=0.)
        self._L = config.getfloat('inductance', minval=0.)
        self._T = config.getfloat('holding_torque', minval=0.)
        self._S = config.getint('steps_per_revolution', minval=0)
        self._I = config.getfloat('max_current', minval=0.)
        
        # Validación y limpieza de parámetros críticos
        self._validate_and_sanitize_parameters()
        
        # Calcular constantes derivadas
        self._calculate_derived_constants()
        
    def _validate_and_sanitize_parameters(self) -> None:
        """Valida y sanitiza parámetros del motor para evitar errores de cálculo."""

        # Validar inductancia
        if self._L <= 0.0:
            logging.warning("Motor %s tiene inductancia cero o negativa", self.name)
            self._L = MIN_INDUCTANCE

        # Validar resistencia
        if self._R <= 0.0:
            logging.warning("Motor %s tiene resistencia cero o negativa", self.name)
            self._R = 1e-12  # Establecer una resistencia mínima para evitar divisiones por cero

    def _validate_current(self, current: float) -> float:
        """Valida la corriente del motor y devuelve un valor válido.

        Args:
            current: Corriente del motor a validar

        Returns:
            Valor válido de corriente del motor
        """
        if current <= 0.0:
            logging.warning("Valor de corriente inválido para el motor %s", self.name)
            return self._I
        return current

    def _validate_steps(self, steps: int) -> int:
        """Valida los pasos por revolución y devuelve un valor válido.
        
        Args:
            steps: Pasos por revolución a validar
            
        Returns:
            Valor válido de pasos por revolución
        """
        if steps <= 0:
            if self._S > 0:
                return self._S
            logging.warning("Valor de pasos inválido para el motor %s", self.name)
            return DEFAULT_STEPS
        return steps
        
    def _validate_voltage(self, volts: float) -> float:
        """Valida el voltaje y devuelve un valor válido.
        
        Args:
            volts: Voltaje a validar
            
        Returns:
            Valor válido de voltaje
        """
        if volts <= 0.0:
            logging.warning("Valor de voltaje inválido para el motor %s", self.name)
            return DEFAULT_VOLTAGE
        return volts


    def _calculate_derived_constants(self) -> None:
        """Calcula constantes derivadas de los parámetros básicos del motor."""
        # Calcular la constante de fuerza contraelectromotriz
        self._cbemf = self._T / (2.0 * self._I)
        
        # Calcular la constante de tiempo del motor (L/R)
        self._time_constant = self._L / self._R if self._R > 0 else 0
        
    # Propiedades de encapsulación y validación
    @property
    def resistance(self) -> float:
        """Obtiene la resistencia de la bobina del motor en Ohmios."""
        return self._R
    
    @property
    def inductance(self) -> float:
        """Obtiene la inductancia de la bobina del motor en Henrios."""
        return self._L
    
    @property
    def holding_torque(self) -> float:
        """Obtiene el par de retención del motor en Nm."""
        return self._T
    
    @property
    def steps_per_revolution(self) -> int:
        """Obtiene los pasos por revolución del motor."""
        return self._S
    
    @property
    def max_current(self) -> float:
        """Obtiene la corriente máxima nominal del motor en Amperios."""
        return self._I
    
    @property
    def cbemf(self) -> float:
        """Obtiene la constante de fuerza contraelectromotriz."""
        return self._cbemf
    
    @property
    def T(self) -> float:
        """Obtiene la constante de tiempo del motor (L/R) en segundos."""
        return self._time_constant

    def pwmgrad(self, fclk: float = DEFAULT_FCLK, steps: int = 0, volts: float = DEFAULT_VOLTAGE) -> int:
        """Calcula el parámetro PWM gradient para drivers TMC.
        
        El gradiente PWM define qué tan rápido aumenta el ciclo de trabajo PWM con la velocidad.
        Valores más altos resultan en regulación PWM más temprana a bajas velocidades.
        
        Args:
            fclk: Frecuencia de reloj en Hz
            steps: Pasos por revolución (usa valor del motor si es 0)
            volts: Voltaje de alimentación en V
            
        Returns:
            Valor de gradiente PWM para configuración TMC
        """
        # Validar parámetros de entrada
        steps_value = self._validate_steps(steps)
        voltage = self._validate_voltage(volts)
        
        if self._L <= 0 or self._R <= 0:
            logging.warning("Motor %s tiene inductancia o resistencia inválida para cálculo PWM", self.name)
            return 0
        
        try:
            # Calcular según fórmula TMC: (2πLfclk) / (R * steps * V) * factor
            grad = (2 * math.pi * self._L * fclk) / (self._R * steps_value * voltage)
            grad_ajustado = grad * PWM_GRAD_FACTOR
            
            # Asegurar valor entero positivo
            return max(min(int(math.ceil(grad_ajustado)), MAX_PWM_VALUE), 1)
        except ZeroDivisionError:
            logging.error("Error división por cero en pwmgrad para motor %s", self.name)
            return 1

    def pwmofs(self, volts: float = DEFAULT_VOLTAGE, current: float = 0.0) -> int:
        """Calcula el parámetro PWM offset para drivers TMC.
        
        El offset PWM define el ciclo de trabajo mínimo requerido para superar
        la resistencia eléctrica del motor al inicio del movimiento.
        
        Args:
            volts: Voltaje de alimentación en V
            current: Corriente del motor en A (usa corriente máxima del motor si es 0)
            
        Returns:
            Valor de offset PWM para configuración TMC
        """
        # Validar entradas
        voltage = self._validate_voltage(volts)
        current_value = self._validate_current(current)
        
        # Calcular el offset PWM utilizando la fórmula de la hoja de datos TMC
        # PWM_OFS = (factor * R * I) / V
        return int(math.ceil(PWM_OFS_FACTOR * self._R * current_value / voltage))

    def maxpwmrps(self, fclk: float = DEFAULT_FCLK, steps: int = 0, 
                volts: float = DEFAULT_VOLTAGE, current: float = 0.0) -> float:
        """Calcula las revoluciones por segundo máximas antes de alcanzar el PWM máximo.
        
        Esta es la velocidad a la cual el ciclo de trabajo PWM alcanza su valor máximo,
        más allá del cual el motor perderá torque por voltaje insuficiente.
        
        Args:
            fclk: Frecuencia de reloj en Hz
            steps: Pasos por revolución (usa valor del motor si es 0)
            volts: Voltaje de alimentación en V
            current: Corriente del motor en A (usa corriente máxima del motor si es 0)
            
        Returns:
            Revoluciones por segundo máximas
        """
        # Validación de parámetros
        voltage = self._validate_voltage(volts)
        current_value = self._validate_current(current)
        steps_value = self._validate_steps(steps)

        # Calcular parámetros PWM
        pwm_ofs = self.pwmofs(volts, current_value)
        pwm_grad = self.pwmgrad(fclk, steps_value, voltage)

        if pwm_grad <= 0:
            logging.warning("Motor %s - PWM gradient inválido: %.2f", self.name, pwm_grad)
            return 0.0

        try:
            # Cálculo preciso con valores flotantes
            rps = (MAX_PWM_VALUE - pwm_ofs) / (math.pi * pwm_grad)
            logging.debug("Motor %s - RPS máximo calculado: %.2f @ %.1fV, %.2fA (PWM_OFS=%d, PWM_GRAD=%d)",
                        self.name, rps, voltage, current_value, pwm_ofs, pwm_grad)
            return round(rps, 2)
        except ZeroDivisionError:
            logging.error("Error división por cero en maxpwmrps para motor %s", self.name)
            return 0.0
        except Exception as e:
            logging.exception("Error inesperado en maxpwmrps: %s", str(e))
            raise

    def hysteresis(self, extra: int = 0, fclk: float = DEFAULT_FCLK, 
                  volts: float = DEFAULT_VOLTAGE, current: float = 0.0, 
                  tbl: int = 1, toff: int = 0) -> Tuple[int, int]:
        """Calcula parámetros de histéresis para drivers TMC.
        
        Los parámetros de histéresis controlan los umbrales de corriente para cambiar entre
        modos de decaimiento rápido y lento. Configuraciones adecuadas son críticas
        para una operación suave y silenciosa del motor.
        
        Args:
            extra (0-8): Valor adicional de histéresis para ajuste fino
            fclk (12.5e6): Frecuencia del reloj del driver en Hz
            volts (24.0): Voltaje de alimentación del motor
            current: Corriente máxima del motor (A). Usa valor configurado si es 0
            tbl (0-3): Tiempo blanking (0:16clk, 1:24clk, 2:36clk, 3:54clk)
            toff (0-15): Tiempo mínimo de decaimiento rápido (3.2-20us)
        
        Returns:
            Tuple[int, int]: Par (hstrt-1, hend+3) para registros TMC:
            - hstrt: 0-7 (1-8 antes del ajuste)
            - hend: 3-15 (0-12 antes del ajuste)
        
        Raises:
            ValueError: Si tbl/toff están fuera de rango (ajustados automáticamente)
        """
        # Validación de parámetros de entrada
        current_value = self._validate_current(current)
        voltage = self._validate_voltage(volts)
        tbl_original = tbl
        toff_original = toff
        tbl = max(0, min(tbl, 3))  # Asegurar rango 0-3
        toff = max(0, min(toff, 15))  # Asegurar rango 0-15
        
        if tbl != tbl_original or toff != toff_original:
            logging.warning("Motor %s - Parámetros fuera de rango: tbl=%d→%d, toff=%d→%d",
                         self.name, tbl_original, tbl, toff_original, toff)
        
        logging.info("Motor %s - Configurando histéresis @ %.1fV, I=%.2fA, TBL=%d, TOFF=%d",
                   self.name, voltage, current_value, tbl, toff)
        
        # Cálculo de tiempos característicos
        tblank = 16.0 * (1.5 ** tbl) / fclk # Tiempo blanking (evita falsos triggers)
        tsd = (12.0 + 32.0 * toff) / fclk   # Tiempo de decaimiento rápido
        
        # Constantes precomputadas (optimización)
        CURRENT_VAR_FACTOR = 248        # 248 = (256 - 8) para ajuste de offset
        NOISE_REDUCTION_FACTOR = 0.92   # Factor empírico para reducción de ruido
        
        # Calcule los cambios actuales durante estos periodos de tiempo
        # ΔI = V * Δt / L for voltage driven current change
        dcoilblank = voltage * tblank / self._L
        
        # ΔI = R * I * Δt / L para la disminución de corriente por resistencia
        dcoilsd = self._R * current_value * 2.0 * tsd / self._L
        
        logging.info("Variación corriente - blank: %.3fA, decay: %.3fA", dcoilblank, dcoilsd)
        
        # Cálculo base de histéresis optimizado
        current_variation = (dcoilblank + dcoilsd) * 2 * NOISE_REDUCTION_FACTOR
        hysteresis_base = 0.5 + (current_variation * CURRENT_VAR_FACTOR / current_value) - 8
        
        # Validar y ajustar parámetro 'extra'
        extra = max(0, min(extra, 8))
        
        # Aplique histéresis extra y asegúrese de que está dentro del rango válido
        hysteresis = extra + int(math.ceil(max(hysteresis_base, -2)))
        
        # Limitar la histéresis total al rango válido (0-14)
        htotal = min(max(hysteresis, 0), 14)
        # Distribución optimizada con límites claros
        hstrt = min(8, max(1, htotal // 2))
        hend = min(12, max(0, htotal - hstrt))
        
        logging.info("Motor %s - Histéresis optimizada: Base=%.1f (NRF=%.2f), Extra=%d, Total=%d",
                   self.name, hysteresis_base, NOISE_REDUCTION_FACTOR, extra, htotal)
        logging.debug("Distribución final - Start: %d, End: %d", hstrt, hend)
        
        # Valores de retorno ajustados al formato de registro TMC
        # TMC requiere hstrt-1 y hend+3 para los valores de registro
        return hstrt - 1, hend + 3
        
    def get_motor_info(self) -> Dict[str, Any]:
        """Obtiene un diccionario con todos los parámetros del motor y valores calculados.
        
        Returns:
            Dictionary with motor parameters and calculated values
        """
        return {
            'name': self.name,
            'resistance': self._R,
            'inductance': self._L,
            'holding_torque': self._T,
            'steps_per_revolution': self._S,
            'max_current': self._I,
            'cbemf': self._cbemf,
            'time_constant': self._time_constant
        }

def load_config_prefix(config):
    return MotorConstants(config)