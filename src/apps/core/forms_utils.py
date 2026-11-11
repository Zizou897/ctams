"""Petits utilitaires partagés entre les formulaires publics."""


def first_error_message(form):
    """Premier message d'erreur d'un formulaire, pour un affichage via `messages`."""
    for field_errors in form.errors.values():
        if field_errors:
            return field_errors[0]
    return "Veuillez corriger les erreurs du formulaire."
