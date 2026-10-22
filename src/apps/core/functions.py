from typing import Any
from config.constants import SECTORS


def get_context_base() -> dict[str, Any]:
    return {
        'company_name': 'CTAMS',
        'company_phone': '07 04 73 04 99',
        'company_email': 'commercial@ctams.net',
        'company_address': "Angré nouveau CHU, non loin de Val d'Oise, Abidjan, Côte d'Ivoire",
        'sectors': SECTORS,
    }
