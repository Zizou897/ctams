from typing import Any
from config.constants import SECTORS


def get_context_base() -> dict[str, Any]:
    return {
        'company_name': 'CTAMS',
        'company_phone': '07 77 90 68 45',
        'company_email': 'Sasava221@gmail.com',
        'company_address': "Riviera Bonoumin, Abidjan, Côte d'Ivoire",
        'sectors': SECTORS,
    }
