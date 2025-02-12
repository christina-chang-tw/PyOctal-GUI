import math

def si_convert(value: float, unit_from: str, unit_to: str) -> float:
    """Convert between SI units with prefixes (e.g., ns, ms, nm)"""
    si_prefixes = {
        "y": 1E-24,  # yocto
        "z": 1E-21,  # zepto
        "a": 1E-18,  # atto
        "f": 1E-15,  # femto
        "p": 1E-12,  # pico
        "n": 1E-9,   # nano
        "u": 1E-6,   # micro
        "m": 1E-3,   # milli
        "": 1,       # base unit
        "k": 1E3,    # kilo
        "M": 1E6,    # mega
        "G": 1E9,    # giga
        "T": 1E12,   # tera
        "P": 1E15,   # peta
        "E": 1E18,   # exa
        "Z": 1E21,   # zetta
        "Y": 1E24    # yotta
    }
    
    # Split prefix and base unit (e.g., "ms" -> "m" and "s")
    prefix_from = unit_from[0] if len(unit_from) > 1 else ""
    prefix_to = unit_to[0] if len(unit_to) > 1 else ""
    
    # Get base unit (e.g., "s" or "m")
    base_from = unit_from[1:] if len(unit_from) > 1 else unit_from
    base_to = unit_to[1:] if len(unit_to) > 1 else unit_to
    
    # Verify same base unit
    if base_from != base_to:
        raise ValueError(f"Cannot convert between different base units: {base_from} and {base_to}")
        
    return value * si_prefixes[prefix_from] / si_prefixes[prefix_to]


def power_convert(value: float, unit_from: str, unit_to: str) -> float:
    """
    Convert between power units (W, mW, uW, etc. and dBm)
    
    Examples:
        power_convert(1, "W", "dBm")    # 30.0 dBm
        power_convert(1, "mW", "dBm")   # 0.0 dBm
        power_convert(0, "dBm", "mW")   # 1.0 mW
        power_convert(0, "dBm", "W")    # 0.001 W
    """
    si_prefixes = {
        "n": 1E-9,   # nano
        "u": 1E-6,   # micro
        "m": 1E-3,   # milli
        "": 1,       # base unit
        "k": 1E3,    # kilo
        "M": 1E6,    # mega
        "G": 1E9     # giga
    }
    
    # Handle watts with SI prefixes
    if unit_from != "dBm":
        prefix = unit_from[0] if len(unit_from) > 1 else ""
        watts = value * si_prefixes[prefix]
    else:
        # Convert from dBm to W
        watts = 10 ** ((value - 30) / 10)
        
    # Convert to target unit
    if unit_to == "dBm":
        return 10 * math.log10(watts) + 30
    else:
        # Handle SI prefix for watts
        prefix = unit_to[0] if len(unit_to) > 1 else ""
        return watts / si_prefixes[prefix]