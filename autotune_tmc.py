from enum import Enum
import logging
import os

from . import tmc


# Parámetros generales de sintonización
TUNING_GOAL = 'auto'                    # Objetivo de sintonización (auto/silent/performance)
VOLTAGE = 24.0                          # Voltaje de alimentación en voltios
OVERVOLTAGE_VTH = None                  # Umbral de protección contra sobrevoltaje

# Parámetros de control de corriente paso a paso
TBL = 2                                 # Longitud del blank time 
TOFF = 3                                # Tiempo de apagado del chopper
TPFD = 0                                # Filtro de paso rápido
EXTRA_HYSTERESIS = 0                    # Histéresis adicional para el control de corriente

# Parámetros de StallGuard
SGT = 0                                 # Umbral de StallGuard
SG4_THRS = 100                          # Umbral de StallGuard4
SLOPE_CONTROL = 3                       # Control de pendiente del StallGuard

# Factores de conmutación automática
AUTOSWITCH_FACTOR_LOW = 0.3             # Factor bajo para conmutación automática
AUTOSWITCH_FACTOR_HIGH = 0.6            # Factor alto para conmutación automática
AUTOSWITCH_HYSTERESIS = 0.15            # Histéresis para conmutación automática
COOLSTEP_THRS_FACTOR = 0.8              # Factor de umbral para CoolStep
FULLSTEP_THRS_FACTOR = 1.25             # Factor de umbral para paso completo

# Configuración PWM y filtros
MULTISTEP_FILT = True                   # Filtro de micropasos habilitado
PWM_AUTOSCALE = True                    # Autoescalado PWM habilitado
PWM_AUTOGRAD = True                     # Autogradiente PWM habilitado

# Parámetros de CoolStep
SEMIN = 3                               # Umbral mínimo de CoolStep
SEMAX = 5                               # Umbral máximo de CoolStep
SEUP = 3                                # Incremento de corriente CoolStep
SEDN = 1                                # Decremento de corriente CoolStep
SEIMIN = 1                              # Corriente mínima en CoolStep
SFILT = 1                               # Filtro de CoolStep

# Configuración de retardos y modo de espera
FAST_STANDSTILL = True                  # Detección rápida de parada
SMALL_HYSTERESIS = False                # Histéresis pequeña desactivada
IHOLDDELAY = 10                         # Retardo para corriente de retención
IRUNDELAY = 0                           # Retardo para corriente de funcionamiento

# Configuración de alta velocidad
VHIGHFS = True                          # Paso completo a alta velocidad
VHIGHCHM = False                        # Modo chopper a alta velocidadd

AUTO_PERFORMANCE_MOTORS = {
    'stepper_x', 'stepper_y', 'dual_carriage', 'stepper_x1', 'stepper_y1', 
    'stepper_a', 'stepper_b', 'stepper_c'
}
DRIVER_SPECIFIC_PARAMS = {
    "tmc2130": {
        "current_factor": 0.93,
        "pwm_lim": 5,                # Límite de PWM
        "pwm_reg": 12,               # Regulación PWM
        "pwm_freq_target": 45e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.28,   # Factor de conmutación automática
        "sg_filter": False,          # Filtro StallGuard desactivado
        "has_thermal_control": True, # Has temperature sensing and protection
        "thermal_limit": 120,        # Operating temperature limit (°C) - Más conservador
        "thermal_warning": 90,       # Warning temperature threshold (°C) - Aviso anticipado
        "thermal_shutdown": 140,     # Shutdown temperature threshold (°C) - Más seguro
        "max_current": 1.2,          # Maximum RMS current (A)
        "sense_resistor": 0.11       # Current sense resistor value (ohm)
    },
    "tmc2208": {
        "current_factor": 0.97,
        "pwm_lim": 6,                # Límite de PWM
        "pwm_reg": 10,               # Regulación PWM
        "pwm_freq_target": 38e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.32,   # Factor de conmutación automática
        "sg_filter": False,          # Filtro StallGuard desactivado
        "has_thermal_control": True, # Has temperature sensing and protection
        "thermal_limit": 110,        # Operating temperature limit (°C) - Más conservador
        "thermal_warning": 85,       # Warning temperature threshold (°C) - Aviso anticipado
        "thermal_shutdown": 135,     # Shutdown temperature threshold (°C) - Más seguro
        "max_current": 1.4,          # Maximum RMS current (A)
        "sense_resistor": 0.11       # Current sense resistor value (ohm)
    },
    "tmc2209": {
        "current_factor": 0.95,
        "pwm_lim": 6,                # Límite de PWM
        "pwm_reg": 10,               # Regulación PWM
        "pwm_freq_target": 38e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.35,   # Factor de conmutación automática
        "sg_filter": True,           # Filtro StallGuard activado
        "has_thermal_control": True, # Has temperature sensing and protection
        "thermal_limit": 110,        # Operating temperature limit (°C) - Más conservador
        "thermal_warning": 85,       # Warning temperature threshold (°C) - Aviso anticipado
        "thermal_shutdown": 135,     # Shutdown temperature threshold (°C) - Más seguro
        "sg_thrs_min": 80,           # Umbral mínimo de StallGuard
        "max_current": 2.0,          # Maximum RMS current (A)
        "sense_resistor": 0.11       # Current sense resistor value (ohm)
    },
    "tmc2225": {
        "current_factor": 0.96,
        "pwm_lim": 6,                # Límite de PWM
        "pwm_reg": 10,               # Regulación PWM
        "pwm_freq_target": 38e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.35,   # Factor de conmutación automática
        "sg_filter": True,           # Filtro StallGuard activado
        "has_thermal_control": True, # Has temperature sensing and protection 
        "thermal_limit": 110,        # Operating temperature limit (°C) - Más conservador
        "thermal_warning": 85,       # Warning temperature threshold (°C) - Aviso anticipado
        "thermal_shutdown": 135,     # Shutdown temperature threshold (°C) - Más seguro
        "max_current": 1.4,          # Maximum RMS current (A)
        "sense_resistor": 0.11       # Current sense resistor value (ohm)
    },
    "tmc2226": {
        "current_factor": 1.03,
        "pwm_lim": 6,                # Límite de PWM
        "pwm_reg": 10,               # Regulación PWM
        "pwm_freq_target": 38e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.35,   # Factor de conmutación automática
        "sg_filter": True,           # Filtro StallGuard activado
        "has_thermal_control": True, # Has temperature sensing and protection
        "thermal_limit": 110,        # Operating temperature limit (°C) - Más conservador
        "thermal_warning": 85,       # Warning temperature threshold (°C) - Aviso anticipado
        "thermal_shutdown": 135,     # Shutdown temperature threshold (°C) - Más seguro
        "max_current": 2.8,          # Maximum RMS current (A)
        "sense_resistor": 0.11       # Current sense resistor value (ohm)
    },
    "tmc2240": {
        "current_factor": 0.98,
        "pwm_lim": 5,                # Límite de PWM
        "pwm_reg": 11,               # Regulación PWM
        "pwm_freq_target": 25e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.25,   # Factor de conmutación automática
        "sg4_filt_en": True,         # Filtro StallGuard4 activado
        "has_thermal_control": True, # Has temperature sensing and protection
        "thermal_limit": 110,        # Operating temperature limit (°C) - Más conservador
        "thermal_warning": 85,       # Warning temperature threshold (°C) - Aviso anticipado
        "thermal_shutdown": 135,     # Shutdown temperature threshold (°C) - Más seguro
        "sg4_th": 1,                 # Umbral StallGuard4
        "slope_control": 3,          # Control de pendiente
        "max_current": 3.0,          # Maximum RMS current (A)
        "sense_resistor": 0.082      # Current sense resistor value (ohm)
    },
    "tmc2660": {
        "current_factor": 1.02,
        "pwm_lim": 5,                # Límite de PWM
        "pwm_reg": 12,               # Regulación PWM
        "pwm_freq_target": 35e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.30,   # Factor de conmutación automática
        "sg_filter": False,          # Filtro StallGuard desactivado
        "has_thermal_control": False,# No temperature sensing available
        "max_current": 4.0,          # Maximum RMS current (A)
        "sense_resistor": 0.075      # Current sense resistor value (ohm)
    },
    "tmc5160": {
        "current_factor": 1.05,
        "pwm_lim": 4,                # Límite de PWM
        "pwm_reg": 14,               # Regulación PWM
        "pwm_freq_target": 38e3,     # Frecuencia objetivo PWM
        "autoswitch_factor": 0.25,   # Factor de conmutación automática
        "sg4_filt_en": True,         # Filtro StallGuard4 activado
        "has_thermal_control": True, # Has temperature sensing and protection
        "sg4_th": 1,                 # Umbral StallGuard4
        "thermal_limit": 105,        # Operating temperature limit (°C) - Más conservador
        "thermal_warning": 80,       # Warning temperature threshold (°C) - Aviso anticipado
        "thermal_shutdown": 130,     # Shutdown temperature threshold (°C) - Más seguro
        "max_current": 3.0,          # Maximum RMS current (A)
        "sense_resistor": 0.075      # Current sense resistor value (ohm)
    }
}

class TuningGoal(str, Enum):
    AUTO = "auto"
    AUTOSWITCH = "autoswitch"
    SILENT = "silent"
    PERFORMANCE = "performance"


class RealTimeMonitor:
    """Monitorización en tiempo real y ajuste dinámico para drivers TMC.
    
    Esta clase proporciona monitorización en tiempo real de parámetros del driver TMC
    y ajuste dinámico de configuraciones basado en carga y temperatura.
    """
    
    def __init__(self, driver):
        """Inicializa el monitor en tiempo real con un driver TMC.
        
        Args:
            driver: Objeto driver TMC con métodos read_temperature y read_stallguard
        """
        self.driver = driver
        self.temperature = 0
        self.load = 0
        self.driver_type = driver.get('driver_type', None)
        self.tmc_utils = TMCUtilities(driver_type=self.driver_type)
        
        # Obtener parámetros específicos del driver desde DRIVER_SPECIFIC_PARAMS
        driver_params = DRIVER_SPECIFIC_PARAMS.get(self.driver_type, {})
        
        # Configuración de límites térmicos
        self.has_thermal_control = driver_params.get('has_thermal_control', True)
        self.thermal_limit = driver.get('thermal_limit', driver_params.get('thermal_limit', 80))
        self.thermal_warning = driver_params.get('thermal_warning', self.thermal_limit - 15)
        self.thermal_shutdown = driver_params.get('thermal_shutdown', self.thermal_limit + 20)
        
        # Configuración de corriente
        self.max_current = driver.get('max_current', driver_params.get('max_current', 2.0))
        self.sense_resistor = driver.get('sense_resistor', driver_params.get('sense_resistor', 0.11))
        if self.sense_resistor <= 0:
            raise ValueError("El valor de resistencia de detección debe ser positivo")
        
        self.last_adjustment_time = 0
        self.adjustment_interval = 2.0  # segundos entre ajustes
        self.dynamic_current_enabled = False  # Control si se ajusta dinámicamente la corriente
    
    def update(self, eventtime=None):
        """Actualiza las lecturas de temperatura y carga.
        
        Args:
            eventtime: Tiempo actual del evento (opcional)
            
        Returns:
            True si se activó la protección térmica, False en caso contrario
        """
        try:
            # Si el driver no tiene control térmico, no intentamos leer la temperatura
            if not self.has_thermal_control:
                self.load = self.driver.read_stallguard()
                return False
                
            self.temperature = self.driver.read_temperature()
            self.load = self.driver.read_stallguard()
            
            # Protección térmica por niveles
            if self.temperature >= self.thermal_shutdown:
                logging.error("¡Temperatura del driver TMC %d°C supera el umbral de apagado %d°C! Apagado de emergencia requerido.", 
                              self.temperature, self.thermal_shutdown)
                self._reduce_current_for_thermal_protection(emergency=True)
                return True
            elif self.temperature > self.thermal_limit:
                logging.warning("Temperatura del driver TMC %d°C supera el límite térmico %d°C", 
                               self.temperature, self.thermal_limit)
                self._reduce_current_for_thermal_protection()
                return True
            # Advertencia preventiva cuando se acerca al límite
            elif self.temperature > self.thermal_warning:
                logging.info("Temperatura del driver TMC %d°C acercándose al límite térmico %d°C", 
                            self.temperature, self.thermal_limit)
                # Reducción preventiva leve de corriente
                try:
                    current = self.driver.get_current()
                    reduced_current = current * 0.90  # Reduce by 10%
                    # Asegurarse de que la corriente no exceda el máximo del driver
                    reduced_current = min(reduced_current, self.max_current)
                    self.driver.set_current(reduced_current)
                    logging.info("Preventive current reduction to %.2fA", reduced_current)
                except Exception as e:
                    logging.error("Error aplicando reducción preventiva de corriente: %s", str(e))
                
            return False
        except Exception as e:
            logging.error("Error updating TMC monitor: %s", str(e))
            return False
    
    def _reduce_current_for_thermal_protection(self, emergency=False):
        """Reduce la corriente para proteger el driver de sobrecalentamiento.
        
        Args:
            emergency: Si es True, aplica una reducción más agresiva para casos críticos
        """
        try:
            current = self.driver.get_current()
            
            # Determinar el factor de reducción según la gravedad
            if emergency:
                # Reducción severa para casos de emergencia (temperatura > thermal_shutdown)
                reduction_factor = 0.50  # Reduce al 50% en emergencia
                log_level = logging.ERROR
                message = "EMERGENCY THERMAL PROTECTION: Reducing current from %.2fA to %.2fA"
            elif self.temperature > (self.thermal_limit + 5):
                # Reducción fuerte para casos críticos
                reduction_factor = 0.60  # Reduce al 60% en caso crítico
                log_level = logging.WARNING
                message = "Critical temperature! Reducing current from %.2fA to %.2fA"
            else:
                # Reducción estándar para casos normales
                reduction_factor = 0.75  # Reduce al 75% en caso normal
                log_level = logging.INFO
                message = "Reducing current from %.2fA to %.2fA due to overtemperature"
            
            # Calcular y validar la corriente reducida
            reduced_current = current * reduction_factor
            
            # Asegurarse de que la corriente no exceda el máximo del driver
            reduced_current = min(reduced_current, self.max_current)
            
            # Registrar y aplicar la reducción
            logging.log(log_level, message, current, reduced_current)
            self.driver.set_current(reduced_current)
            
        except Exception as e:
            logging.error("Error reduciendo corriente: %s", str(e))
    
    def dynamic_adjustment(self, eventtime=None):
        """Ajusta dinámicamente la corriente basado en la carga del motor.
        
        Args:
            eventtime: Tiempo actual del evento (opcional)
            
        Returns:
            Valor de corriente ajustado o None si falló el ajuste
        """
        # Limit adjustment frequency
        if eventtime and self.last_adjustment_time:
            if eventtime - self.last_adjustment_time < self.adjustment_interval:
                return None
        
        try:
            # Read current load and current setting
            load = self.driver.read_stallguard()
            current = self.driver.get_current()
            
            # Calculate load factor (0-1 range)
            load_factor = min(max(load / 100.0, 0), 1) * 0.2
            
            # Adjust current based on load
            adjusted_current = current * (1 - load_factor)
            
            # Asegurarse de que la corriente no exceda el máximo del driver
            adjusted_current = min(adjusted_current, self.max_current)
            
            # Validate the adjusted current
            self.tmc_utils.validate_current(adjusted_current, self.driver_type)
            
            # Apply the new current setting
            self.driver.set_current(adjusted_current)
            
            if eventtime:
                self.last_adjustment_time = eventtime
                
            logging.info("Ajuste dinámico de corriente: %.2fA → %.2fA (carga: %d%%)", 
                         current, adjusted_current, int(load))
                         
            return adjusted_current
        except Exception as e:
            logging.error("Failed to adjust current dynamically: %s", str(e))
            return None
            
    def get_status(self):
        """Obtiene el estado actual del driver monitorizado.
        
        Returns:
            Diccionario con información del estado actual
        """
        return {
            'temperature': self.temperature,
            'load': self.load,
            'has_thermal_control': self.has_thermal_control,
            'thermal_warning': self.thermal_warning,
            'thermal_limit': self.thermal_limit,
            'thermal_shutdown': self.thermal_shutdown,
            'max_current': self.max_current,
            'sense_resistor': self.sense_resistor
        }

class TMCUtilities:
    """Unified utility class for TMC driver configuration and optimization.
    
    This class consolidates various calculation and optimization functions
    for TMC stepper drivers, providing a clean interface for the AutotuneTMC class.
    """
    
    def __init__(self, motor_object=None, driver_type=None):
        """Initialize TMC utilities with motor object and driver type.
        
        Args:
            motor_object: MotorConstants object with motor specifications
            driver_type: TMC driver type (e.g., "tmc2209")
        """
        self.motor_object = motor_object
        self.driver_type = driver_type
        self.inductance = getattr(motor_object, 'inductance', 0)
        self.resistance = getattr(motor_object, 'resistance', 0)
        self.max_current = getattr(motor_object, 'max_current', 0)
        self.time_constant = self.inductance / self.resistance if self.resistance > 0 else 0
    
    def configure_motor(self, motor_profile):
        """Configure motor parameters from a profile.
        
        Args:
            motor_profile: Object containing motor specifications
            
        Returns:
            Self for method chaining
        """
        self.inductance = motor_profile.getfloat('inductance')
        self.resistance = motor_profile.getfloat('resistance')
        self.max_current = motor_profile.getfloat('max_current')
        self.T = motor_profile.getfloat('T')  # Time constant in seconds
        return self
    
    def calculate_max_speed(self):
        time_constant = self.inductance / self.resistance
        return (self.max_current * self.resistance) / (2 * math.pi * time_constant)
    
    def calculate_hysteresis(self, current, tuning_goal, extra_hysteresis):
        """Calculate optimal hysteresis parameters based on current and tuning goal.
        
        Args:
            current: Motor current in Amps
            tuning_goal: Tuning goal (SILENT, PERFORMANCE, AUTOSWITCH)
            extra_hysteresis: Additional hysteresis value to add
            
        Returns:
            Dictionary with hstrt and hend values
        """
        # Optimize HSTRT based on current ranges
        hstrt = 3 if current < 0.7 else 4 if current < 1.2 else 5
        
        # Adjust HSTRT based on tuning goal
        if tuning_goal == TuningGoal.SILENT:
            hstrt = max(2, hstrt - 1)  # Reduce hysteresis for silent operation
        elif tuning_goal == TuningGoal.AUTOSWITCH:
            hstrt = min(6, hstrt + 1)  # Increase hysteresis for better switching
        
        # Apply extra hysteresis with upper limit
        hstrt = min(7, hstrt + extra_hysteresis)
        
        # Optimize HEND based on current ranges
        hend = 2 if current < 0.7 else 1 if current < 1.2 else 0
        
        # Fine-tune HEND for autoswitch mode
        if tuning_goal == TuningGoal.AUTOSWITCH:
            hend = max(0, hend - 1)  # Reduce end hysteresis for better switching
        
        return {
            "hstrt": hstrt,
            "hend": hend
        }
    
    def calculate_pwm_threshold(self, vmaxpwm, coolthrs, driver_type=None):
        """Calculate PWM threshold for automatic switching between modes.
        
        Args:
            vmaxpwm: Maximum PWM velocity
            coolthrs: Coolstep threshold
            driver_type: TMC driver type
            
        Returns:
            PWM threshold value
        """
        driver_type = driver_type or self.driver_type
        
        # Get driver-specific autoswitch factor or determine based on motor time constant
        # Get driver-specific autoswitch factor if available
        factor = (DRIVER_SPECIFIC_PARAMS.get(driver_type, {}).get('autoswitch_factor', None))
        
        # If no driver-specific factor, determine based on motor time constant
        if factor is None:
            if (self.motor_object and 
                hasattr(self.motor_object, 'T') and 
                self.motor_object.T < 0.2):
                factor = AUTOSWITCH_FACTOR_HIGH
            else:
                factor = AUTOSWITCH_FACTOR_LOW
        
        # Calculate base threshold
        base_threshold = max(vmaxpwm * factor, coolthrs * 1.2)
        
        # Apply driver-specific adjustments
        if driver_type in ["tmc2209", "tmc2208"]:
            base_threshold *= 1.1
        elif driver_type in ["tmc5160", "tmc2240"]:
            base_threshold *= 0.95
        
        return base_threshold
    
    def calculate_overvoltage_threshold(self, voltage_supply):
        """Calculate overvoltage threshold register value.
        
        Args:
            voltage_supply: Supply voltage in Volts
            
        Returns:
            Overvoltage threshold register value
        """
        # Formula from TMC datasheet: VTH = (V + 0.8) / 0.009732
        return int((voltage_supply + 0.8) / 0.009732)
    
    def calculate_run_current(self, motor_params=None, driver_type=None):
        """Calculate optimal run current for the motor.
        
        Args:
            motor_params: Motor parameters object (uses self.motor_object if None)
            driver_type: TMC driver type
            
        Returns:
            Optimal run current in Amps
        """
        driver_type = driver_type or self.driver_type
        motor_params = motor_params or self.motor_object
        
        if not motor_params:
            logging.warning("No hay parámetros del motor disponibles para el cálculo de corriente")
            return 0.0
        
        # Get motor parameters
        run_current = getattr(motor_params, 'max_current', 0)
        resistance = getattr(motor_params, 'resistance', 0)
        
        if run_current <= 0:
            logging.warning("run_current inválido para el motor")
            return 0.0
        
        # Obtener parámetros específicos del driver
        driver_params = DRIVER_SPECIFIC_PARAMS.get(driver_type, {})
        driver_max_current = driver_params.get('max_current', 2.0)
        sense_resistor = driver_params.get('sense_resistor', 0.11)
        
        # Calculate optimal current based on motor resistance
        optimal_current = run_current * (1 + (resistance / 10))
        
        # Ajustar la corriente basado en la resistencia de sensado
        # Los drivers con resistencias más bajas pueden manejar corrientes más altas
        if sense_resistor < 0.1:
            # Para resistencias más bajas, podemos permitir corrientes ligeramente más altas
            optimal_current *= (0.11 / sense_resistor) * 0.9  # Factor de seguridad de 0.9
        
        # Aplicar factor de ajuste específico del driver
        optimal_current *= driver_params.get('current_factor', 1.0)
        
        # Limitar a la capacidad máxima de corriente del driver
        max_allowed = min(run_current, driver_max_current)
        return min(optimal_current, max_allowed)

    
    def validate_pwm_freq(self, value):
        """Validate PWM frequency is within acceptable range.
        
        Args:
            value: PWM frequency in Hz
            
        Raises:
            ValueError: If frequency is outside valid range
        """
        if not (10e3 <= value <= 100e3):
            raise ValueError(f"Frecuencia PWM {value} fuera de límites (10-100 kHz)")
    
    def validate_current(self, value, driver_type=None):
        """Validate current is within driver's capability.
        
        Args:
            value: Current in Amps
            driver_type: TMC driver type
            
        Raises:
            ValueError: If current exceeds driver's capability
        """
        driver_type = driver_type or self.driver_type
        
        if not driver_type:
            logging.warning("No driver type specified for current validation")
            return
            
        # Obtener parámetros específicos del driver
        driver_params = DRIVER_SPECIFIC_PARAMS.get(driver_type, {})
        driver_max_current = driver_params.get('max_current', 2.0)
        sense_resistor = driver_params.get('sense_resistor', 0.11)
            
        if value > driver_max_current:
            raise ValueError(f"Corriente {value}A excede capacidad del driver {driver_type} (máx: {driver_max_current}A)")
        
        # Validación adicional basada en la resistencia de sensado
        # Algunos drivers con resistencias de sensado más bajas tienen límites de corriente más estrictos
        if sense_resistor < 0.1 and value > (max_current * 0.95):
            logging.warning(f"Corriente {value}A está cerca del límite para el driver {driver_type} con resistencia de sensado {sense_resistor}ohm")
            
    def get_motor_time_constant(self):
        """Get motor time constant (L/R) in seconds.
        
        Returns:
            Motor time constant in seconds
        """
        if self.motor_object and hasattr(self.motor_object, 'T'):
            return self.motor_object.T
        elif self.resistance > 0 and self.inductance > 0:
            return self.inductance / self.resistance
        return 0

class AutotuneTMC:
    cmd_AUTOTUNE_TMC_help = "Apply optimized autotuning configuration to TMC stepper driver"
    
    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        self.name = config.get_name().split(None, 1)[-1]
        self.driver_type = config.get('driver_type')
        self.motor = config.get('motor')
        self.motor_name = f"motor_constants {self.motor}"
        self.tmc_utils = None  # Se inicializará después de cargar el objeto motor
        
        # Load motor database
        pconfig = self.printer.lookup_object('configfile')
        dirname = os.path.dirname(os.path.realpath(__file__))
        filename = os.path.join(dirname, 'motor_database.cfg')
        try:
            motor_db = pconfig.read_config(filename)
        except Exception:
            raise config.error(f"Cannot load motor database '{filename}'")
        for motor in motor_db.get_prefix_sections(''):
            self.printer.load_object(motor_db, motor.get_name())
        
        # Find TMC driver section
        self.tmc_section = None
        for driver in DRIVER_SPECIFIC_PARAMS:
            driver_name = f"{driver} {self.name}"
            if config.has_section(driver_name):
                self.tmc_section = config.getsection(driver_name)
                self.driver_name = driver_name
                self.driver_type = driver
                break
        if self.tmc_section is None:
            raise config.error(
                f"Could not find any TMC driver config section for '{self.name}' required by TMC autotuning"
            )
        
        # Determine which TMCtstepHelper implementation to use
        if 'pstepper' in tmc.TMCtstepHelper.__signature__.parameters:
            self._set_driver_velocity_field = self._set_driver_velocity_field_new
        else:
            self._set_driver_velocity_field = self._set_driver_velocity_field_old
        
        # Load motor configuration
        try:
            self.motor_object = self.printer.lookup_object(self.motor_name)
        except Exception:
            raise self.printer.config_error(
                f"Could not find motor definition '[{self.motor_name}]' required by TMC autotuning. "
                "It is not part of the database, please define it in your config!"
            )
        
        # Set tuning goal
        tgoal = config.get('tuning_goal', default=TUNING_GOAL).lower()
        try:
            self.tuning_goal = TuningGoal(tgoal)
        except ValueError:
            raise config.error(
                f"Tuning goal '{tgoal}' is invalid for TMC autotuning"
            )
        
        # Initialize variables
        self.auto_silent = False
        self.tmc_object = None
        self.tmc_cmdhelper = None
        self.tmc_init_registers = None
        self.run_current = 0.0
        self.fclk = None
        
        # Load configuration parameters
        self.extra_hysteresis = config.getint('extra_hysteresis', default=EXTRA_HYSTERESIS, minval=0, maxval=8)
        self.tbl = config.getint('tbl', default=TBL, minval=0, maxval=3)
        self.toff = config.getint('toff', default=TOFF, minval=1, maxval=15)
        self.tpfd = config.getint('tpfd', default=TPFD, minval=0, maxval=15)
        self.sgt = config.getint('sgt', default=SGT, minval=-64, maxval=63)
        self.sg4_thrs = config.getint('sg4_thrs', default=SG4_THRS, minval=0, maxval=255)
        self.voltage = config.getfloat('voltage', default=VOLTAGE, minval=0.0, maxval=60.0)
        self.overvoltage_vth = config.getfloat('overvoltage_vth', default=OVERVOLTAGE_VTH, minval=0.0, maxval=60.0)
        self.pwm_freq_target = config.getfloat('pwm_freq_target',
                                               default=DRIVER_SPECIFIC_PARAMS[self.driver_type].get('pwm_freq_target', 40e3),
                                               minval=10e3, maxval=100e3)
        
        # Register event handlers
        self.printer.register_event_handler("klippy:connect", self.handle_connect)
        self.printer.register_event_handler("klippy:ready", self.handle_ready)
        
        # Register G-code command
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command("AUTOTUNE_TMC", "STEPPER", self.name,
                                   self.cmd_AUTOTUNE_TMC,
                                   desc=self.cmd_AUTOTUNE_TMC_help)
    
    def handle_connect(self):
        self.tmc_object = self.printer.lookup_object(self.driver_name)
        self.tmc_cmdhelper = self.tmc_object.get_status.__self__
        
        # Inicializar la clase de utilidades TMC con el objeto motor y el tipo de driver
        self.tmc_utils = TMCUtilities(self.motor_object, self.driver_type)
        
        # Inicializar el monitor en tiempo real
        self.realtime_monitor = RealTimeMonitor(self.tmc_object)
        self.dynamic_monitoring = False
        
        # Determine tuning goal based on motor characteristics
        if self.tuning_goal == TuningGoal.AUTO:
            self.auto_silent = self.name not in AUTO_PERFORMANCE_MOTORS and self.motor_object.T > 0.3
            self.tuning_goal = TuningGoal.SILENT if self.auto_silent else TuningGoal.PERFORMANCE
        
        # Check if driver has init_registers method
        try:
            self.tmc_init_registers = self.tmc_object.init_registers
        except AttributeError:
            self.tmc_init_registers = None
    
    def handle_ready(self):
        self.printer.reactor.register_callback(self._handle_ready_deferred)
        
        # Registrar el comando G-code para el monitoreo dinámico
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command("SET_TMC_MONITOR", "STEPPER", self.name,
                               self.cmd_SET_TMC_MONITOR,
                               desc="Activar/desactivar monitoreo dinámico para un driver TMC")
    
    def _handle_ready_deferred(self, eventtime):
        if self.tmc_init_registers is not None:
            try:
                self.tmc_init_registers(print_time=eventtime)
            except Exception as e:
                logging.error(f"Error inicializando registros TMC: {str(e)}")
        
        try:
            self.fclk = self.tmc_object.mcu_tmc.get_tmc_frequency()
            logging.info(f"autotune_tmc {self.name} using clock frequency {self.fclk/1e6:.2f} MHz")
        except AttributeError:
            logging.warning(f"autotune_tmc {self.name} could not get TMC frequency, using default")
            self.fclk = 12.5e6
            logging.info(f"autotune_tmc {self.name} using default clock frequency 12.5 MHz")
        
        self.tune_driver(eventtime)
        
        # Registrar callback para monitoreo periódico
        self.printer.register_event_handler("klippy:disconnect", self._handle_disconnect)
        reactor = self.printer.get_reactor()
        self.monitor_timer = reactor.register_timer(self._monitor_callback, reactor.NOW)
    
    def _handle_disconnect(self):
        # Detener el timer de monitoreo al desconectar
        if hasattr(self, 'monitor_timer'):
            self.printer.get_reactor().unregister_timer(self.monitor_timer)
    
    def _monitor_callback(self, eventtime):
        # Actualizar el monitor en tiempo real
        if self.dynamic_monitoring:
            try:
                # Actualizar lecturas de temperatura y carga
                thermal_protection_triggered = self.realtime_monitor.update(eventtime)
                
                # Si está activado el ajuste dinámico, ajustar la corriente
                if self.realtime_monitor.dynamic_current_enabled:
                    self.realtime_monitor.dynamic_adjustment(eventtime)
                
                # Si se activó la protección térmica, informar al usuario
                if thermal_protection_triggered:
                    self.printer.invoke_shutdown(
                        f"TMC driver {self.name} thermal protection triggered")
                    return self.printer.get_reactor().NEVER
            except Exception as e:
                logging.error(f"Error en monitoreo TMC: {str(e)}")
        
        # Programar la próxima actualización en 2 segundos
        return eventtime + 2.0
    
    def cmd_AUTOTUNE_TMC(self, gcmd):
        logging.info(f"AUTOTUNE_TMC {self.name}")
        tgoal = gcmd.get('TUNING_GOAL', None)
        if tgoal is not None:
            try:
                self.tuning_goal = TuningGoal(tgoal)
            except ValueError:
                logging.error(f"Invalid tuning goal '{tgoal}' for TMC autotuning")
                return
            if self.tuning_goal == TuningGoal.AUTO:
                self.tuning_goal = TuningGoal.SILENT if self.auto_silent else TuningGoal.PERFORMANCE
        
        self._process_gcmd_parameters(gcmd)
        self.tune_driver()
        self._report_configuration(gcmd)
    
    def _process_gcmd_parameters(self, gcmd):
        self.extra_hysteresis = gcmd.get_int('EXTRA_HYSTERESIS', default=self.extra_hysteresis, minval=0, maxval=8)
        self.tbl = gcmd.get_int('TBL', default=self.tbl, minval=0, maxval=3)
        self.toff = gcmd.get_int('TOFF', default=self.toff, minval=1, maxval=15)
        self.tpfd = gcmd.get_int('TPFD', default=self.tpfd, minval=0, maxval=15)
        self.sgt = gcmd.get_int('SGT', default=self.sgt, minval=-64, maxval=63)
        self.sg4_thrs = gcmd.get_int('SG4_THRS', default=self.sg4_thrs, minval=0, maxval=255)
        self.voltage = gcmd.get_float('VOLTAGE', default=self.voltage, minval=0.0, maxval=60.0)
        self.overvoltage_vth = gcmd.get_float('OVERVOLTAGE_VTH', default=self.overvoltage_vth, minval=0.0, maxval=60.0)
    
    def _report_configuration(self, gcmd):
        msg = f"TMC autotuning for {self.name}:\n"
        msg += f"- Driver: {self.driver_type}\n"
        msg += f"- Motor: {self.motor}\n"
        msg += f"- Tuning goal: {self.tuning_goal}\n"
        msg += f"- Current: {self.run_current:.2f} A\n"
        msg += f"- Voltage: {self.voltage:.1f} V\n"
        if self.driver_type in ["tmc2240", "tmc5160"] and self.overvoltage_vth is not None:
            msg += f"- Overvoltage protection: {self.overvoltage_vth:.1f} V\n"
        
        # Añadir información sobre el monitoreo en tiempo real
        msg += f"\nMonitoreo en tiempo real:\n"
        msg += f"- Estado: {'Activo' if self.dynamic_monitoring else 'Inactivo'}\n"
        if self.dynamic_monitoring:
            status = self.realtime_monitor.get_status()
            msg += f"- Temperatura actual: {status['temperature']}°C\n"
            msg += f"- Límite térmico: {status['thermal_limit']}°C\n"
            msg += f"- Ajuste dinámico de corriente: {'Activo' if self.realtime_monitor.dynamic_current_enabled else 'Inactivo'}\n"
        
        gcmd.respond_info(msg)
    
    def tune_driver(self, print_time=None):
        _currents = self.tmc_cmdhelper.current_helper.get_current()
        self.run_current = _currents[0]
        logging.info(f"autotune_tmc {self.name} applying tuning goal: {self.tuning_goal}")
        
        self._apply_driver_specific_optimizations()
        self._set_pwmfreq()
        self._setup_spreadcycle()
        self._set_hysteresis(self.run_current)
        self._set_stallguard()
        
        motor = self.motor_object
        maxpwmrps = motor.maxpwmrps(volts=self.voltage, current=self.run_current)
        rdist, _ = self.tmc_cmdhelper.stepper.get_rotation_distance()
        vmaxpwm = maxpwmrps * rdist
        logging.info(f"autotune_tmc {self.name} using max PWM speed {vmaxpwm:.2f} mm/s")
        
        self._configure_overvoltage_protection()
        
        coolthrs = COOLSTEP_THRS_FACTOR * rdist
        pwmthrs = self._calculate_pwmthrs(vmaxpwm, coolthrs)
        
        self._setup_coolstep(coolthrs)
        self._setup_pwm(self.tuning_goal, pwmthrs)
        self._setup_highspeed(FULLSTEP_THRS_FACTOR * vmaxpwm)
        
        self._set_driver_field('multistep_filt', MULTISTEP_FILT)
        logging.info(f"autotune_tmc {self.name} configuration complete")
    
    def _apply_driver_specific_optimizations(self):
        if self.driver_type in DRIVER_SPECIFIC_PARAMS:
            params = DRIVER_SPECIFIC_PARAMS[self.driver_type]
            logging.info(f"autotune_tmc {self.name} applying {self.driver_type}-specific optimizations")
            if 'pwm_freq_target' in params:
                self.pwm_freq_target = params['pwm_freq_target']
                logging.info(f"autotune_tmc {self.name} using driver-specific PWM frequency target: {self.pwm_freq_target/1000.0:.2f} kHz")
            for param, value in params.items():
                if param in ['pwm_freq_target', 'autoswitch_factor']:
                    continue
                if self.tmc_object.fields.lookup_register(param, None) is not None:
                    self._set_driver_field(param, value)
                    logging.info(f"autotune_tmc {self.name} set {param} = {str(value)}")
    
    def _configure_overvoltage_protection(self):
        if self.overvoltage_vth is not None:
            if self.tmc_object.fields.lookup_register("overvoltage_vth", None) is not None:
                # Usar la instancia de TMCUtilities para calcular el umbral de sobrevoltaje
                vth = self.tmc_utils.calculate_overvoltage_threshold(self.overvoltage_vth)
                logging.info(f"autotune_tmc {self.name} setting overvoltage threshold to {self.overvoltage_vth:.2f} V (reg value: {vth})")
                self._set_driver_field('overvoltage_vth', vth)
            else:
                logging.info(f"autotune_tmc {self.name} driver does not support overvoltage protection")
    
    def _set_driver_field(self, field, arg):
        tmco = self.tmc_object
        register = tmco.fields.lookup_register(field, None)
        if register is None:
            return
        logging.info(f"autotune_tmc {self.name} set {field}={repr(arg)}")
        val = tmco.fields.set_field(field, arg)
        tmco.mcu_tmc.set_register(register, val, None)
    
    def _set_driver_velocity_field_new(self, field, velocity):
        tmco = self.tmc_object
        register = tmco.fields.lookup_register(field, None)
        if register is None:
            return
        arg = tmc.TMCtstepHelper(tmco.mcu_tmc, velocity, pstepper=self.tmc_cmdhelper.stepper)
        logging.info(f"autotune_tmc {self.name} set {field}={repr(arg)}({repr(velocity)})")
        tmco.fields.set_field(field, arg)
    
    def _set_driver_velocity_field_old(self, field, velocity):
        tmco = self.tmc_object
        register = tmco.fields.lookup_register(field, None)
        if register is None:
            return
        step_dist = self.tmc_cmdhelper.stepper.get_step_dist()
        mres = tmco.fields.get_field("mres")
        arg = tmc.TMCtstepHelper(step_dist, mres, self.fclk, velocity)
        logging.info(f"autotune_tmc {self.name} set {field}={repr(arg)}({repr(velocity)})")
        tmco.fields.set_field(field, arg)
    
    def _set_pwmfreq(self):
        pwm_options = [
            (3, 2./410),
            (2, 2./512),
            (1, 2./683),
            (0, 2./1024),
            (0, 0.)
        ]
        for pwm_value, factor in pwm_options:
            freq = factor * float(self.fclk) if self.fclk is not None else 0.0
            if freq <= self.pwm_freq_target or factor == 0.:
                logging.info(f"autotune_tmc {self.name} setting PWM frequency to {freq/1000.0:.2f} kHz (pwm_freq={pwm_value})")
                self._set_driver_field('pwm_freq', pwm_value)
                break
    
    def _setup_spreadcycle(self):
        self._set_driver_field('tbl', self.tbl)
        self._set_driver_field('toff', self.toff)
        if self.tpfd is not None:
            self._set_driver_field('tpfd', self.tpfd)
    
    def _set_hysteresis(self, current):
        # Usar la instancia de TMCUtilities para calcular la histéresis
        hysteresis_values = self.tmc_utils.calculate_hysteresis(current, self.tuning_goal, self.extra_hysteresis)
        self._set_driver_field('hstrt', hysteresis_values['hstrt'])
        self._set_driver_field('hend', hysteresis_values['hend'])
        logging.info(f"autotune_tmc {self.name} set hysteresis: hstrt={hysteresis_values['hstrt']}, hend={hysteresis_values['hend']}")
    
    def _set_stallguard(self):
        if self.driver_type in ["tmc5160", "tmc2240", "tmc2130", "tmc2660"]:
            self._set_driver_field('sgt', self.sgt)
        if self.driver_type in ["tmc2209", "tmc2260"]:
            self._set_driver_field('sgthrs', self.sg4_thrs)
        if self.driver_type == "tmc2209" and self.tmc_object.fields.lookup_register("sg_filter", None) is not None:
            self._set_driver_field('sg_filter', True)
        if self.driver_type in ["tmc2240", "tmc5160"] and self.tmc_object.fields.lookup_register("sg4_filt_en", None) is not None:
            self._set_driver_field('sg4_filt_en', True)
    
    def _calculate_pwmthrs(self, vmaxpwm, coolthrs):
        # Usar la instancia de TMCUtilities para calcular el umbral PWM
        pwmthrs = self.tmc_utils.calculate_pwm_threshold(vmaxpwm, coolthrs)
        logging.info(f"autotune_tmc {self.name} calculated AUTOSWITCH threshold: {pwmthrs:.2f} mm/s")
        return pwmthrs
    
    def _setup_pwm(self, tuning_goal, pwmthrs):
        self._set_driver_field('pwm_autoscale', PWM_AUTOSCALE)
        self._set_driver_field('pwm_autograd', PWM_AUTOGRAD)
        
        if self.driver_type in DRIVER_SPECIFIC_PARAMS:
            params = DRIVER_SPECIFIC_PARAMS[self.driver_type]
            pwm_reg = params.get('pwm_reg', 12)
            pwm_lim = params.get('pwm_lim', 5)
        else:
            pwm_reg = 12
            pwm_lim = 5
        
        self._set_driver_field('pwm_reg', pwm_reg)
        self._set_driver_field('pwm_lim', pwm_lim)
        
        if tuning_goal == TuningGoal.SILENT:
            self._set_driver_velocity_field('tpwmthrs', 0.0)
            logging.info(f"autotune_tmc {self.name} using StealthChop (silent mode) at all speeds")
        elif tuning_goal == TuningGoal.PERFORMANCE:
            self._set_driver_velocity_field('tpwmthrs', 1e9)
            logging.info(f"autotune_tmc {self.name} using SpreadCycle (performance mode) at all speeds")
        else:
            high_threshold = pwmthrs * (1.0 - AUTOSWITCH_HYSTERESIS)
            self._set_driver_velocity_field('tpwmthrs', pwmthrs)
            logging.info(f"autotune_tmc {self.name} using enhanced AUTOSWITCH mode:")
            logging.info(f"  - StealthChop below {high_threshold:.2f} mm/s")
            logging.info(f"  - SpreadCycle above {pwmthrs:.2f} mm/s")
            logging.info(f"  - Hysteresis zone: {pwmthrs - high_threshold:.2f} mm/s")
    
    def _setup_coolstep(self, coolthrs):
        self._set_driver_velocity_field('tcoolthrs', coolthrs)
        self._set_driver_field('semin', SEMIN)
        self._set_driver_field('semax', SEMAX)
        self._set_driver_field('seup', SEUP)
        self._set_driver_field('sedn', SEDN)
        self._set_driver_field('seimin', SEIMIN)
        self._set_driver_field('sfilt', SFILT)
        self._set_driver_field('fast_standstill', FAST_STANDSTILL)
        self._set_driver_field('iholddelay', IHOLDDELAY)
        if self.tmc_object.fields.lookup_register("irundelay", None) is not None:
            self._set_driver_field('irundelay', IRUNDELAY)
        logging.info(f"autotune_tmc {self.name} using CoolStep current reduction above {coolthrs:.2f} mm/s")
    
    def _setup_highspeed(self, fullstep_thrs):
        self._set_driver_velocity_field('thigh', fullstep_thrs)
        self._set_driver_field('vhighfs', VHIGHFS)
        self._set_driver_field('vhighchm', VHIGHCHM)
        logging.info(f"autotune_tmc {self.name} using fullstep mode above {fullstep_thrs:.2f} mm/s")

    def cmd_SET_TMC_MONITOR(self, gcmd):
        """Activar/desactivar monitoreo dinámico para un driver TMC.
        
        Este comando permite configurar el monitoreo en tiempo real
        de temperatura y carga del motor, así como el ajuste dinámico
        de corriente basado en la carga del motor.
        """
        # Obtener parámetros del comando
        enable = gcmd.get_int('ENABLE', None)
        if enable is not None:
            self.dynamic_monitoring = bool(enable)
        
        # Configurar intervalo de monitoreo
        interval = gcmd.get_float('INTERVAL', None)
        if interval is not None:
            if interval < 0.5:
                raise gcmd.error("El intervalo de monitoreo debe ser al menos 0.5 segundos")
            self.realtime_monitor.adjustment_interval = interval
        
        # Configurar límites térmicos
        thermal_limit = gcmd.get_int('THERMAL_LIMIT', None)
        if thermal_limit is not None:
            if thermal_limit < 60 or thermal_limit > 120:
                raise gcmd.error("El límite térmico debe estar entre 60°C y 120°C")
            self.realtime_monitor.thermal_limit = thermal_limit
            
        thermal_warning = gcmd.get_int('THERMAL_WARNING', None)
        if thermal_warning is not None:
            if thermal_warning < 50 or thermal_warning >= self.realtime_monitor.thermal_limit:
                raise gcmd.error(f"El umbral de advertencia térmica debe estar entre 50°C y {self.realtime_monitor.thermal_limit-1}°C")
            self.realtime_monitor.thermal_warning = thermal_warning
            
        thermal_shutdown = gcmd.get_int('THERMAL_SHUTDOWN', None)
        if thermal_shutdown is not None:
            if thermal_shutdown <= self.realtime_monitor.thermal_limit or thermal_shutdown > 150:
                raise gcmd.error(f"El umbral de apagado térmico debe estar entre {self.realtime_monitor.thermal_limit+1}°C y 150°C")
            self.realtime_monitor.thermal_shutdown = thermal_shutdown
        
        # Configurar ajuste dinámico de corriente
        dynamic_current = gcmd.get_int('DYNAMIC_CURRENT', None)
        if dynamic_current is not None:
            self.realtime_monitor.dynamic_current_enabled = bool(dynamic_current)
        
        # Reportar estado actual
        status = self.realtime_monitor.get_status()
        msg = f"Estado del monitor TMC para {self.name}:\n"
        msg += f"- Monitoreo activo: {self.dynamic_monitoring}\n"
        msg += f"- Intervalo de ajuste: {self.realtime_monitor.adjustment_interval:.1f} s\n"
        
        # Información térmica
        if status['has_thermal_control']:
            msg += f"- Control térmico: Habilitado\n"
            msg += f"- Umbral de advertencia: {status['thermal_warning']}°C\n"
            msg += f"- Límite térmico: {status['thermal_limit']}°C\n"
            msg += f"- Umbral de apagado: {status['thermal_shutdown']}°C\n"
            msg += f"- Temperatura actual: {status['temperature']}°C\n"
        else:
            msg += f"- Control térmico: No disponible para este driver\n"
        
        # Información de corriente
        msg += f"- Corriente máxima: {status['max_current']:.2f}A\n"
        msg += f"- Resistencia de sensado: {status['sense_resistor']:.3f} ohm\n"
        msg += f"- Carga actual: {status['load']}%\n"
        
        gcmd.respond_info(msg)


# Register the TMC autotune module with Klipper
def load_config_prefix(config):
    return AutotuneTMC(config)