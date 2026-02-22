from enum import Enum

class Intent(Enum):
    START = 'start'
    SKILLS = 'skills'
    RULES = 'rules'
    PLOT = 'plot'
    EQUATION = 'equation'
    INEQUALITY = 'inequality'
    HISTORY = 'history'
    PAYMENTS = 'payments'
    SUPPORT = 'support'
    UNKNOWN = 'unknown'
