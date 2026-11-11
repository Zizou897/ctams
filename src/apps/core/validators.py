"""Validateurs anti-spam réutilisables pour les formulaires publics (contact, devis)."""
import re

from django.core.exceptions import ValidationError

_LINK_PATTERN = re.compile(r"(https?://|www\.)", re.IGNORECASE)
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


def reject_links(value):
    """Refuse toute valeur contenant un lien (http://, https:// ou www.)."""
    if value and _LINK_PATTERN.search(value):
        raise ValidationError("Les liens ne sont pas autorisés dans ce champ.")


def reject_html_and_newlines(value):
    """Refuse les balises HTML et les retours à la ligne."""
    if not value:
        return
    if _HTML_TAG_PATTERN.search(value):
        raise ValidationError("Les balises HTML ne sont pas autorisées dans ce champ.")
    if "\n" in value or "\r" in value:
        raise ValidationError("Ce champ ne doit pas contenir de retour à la ligne.")


def reject_links_html_and_newlines(value):
    """Refuse les liens, les balises HTML et les retours à la ligne (champs courts :
    nom, entreprise, téléphone, email)."""
    reject_links(value)
    reject_html_and_newlines(value)
