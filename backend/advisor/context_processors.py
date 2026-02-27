from .i18n import get_lang_from_request, get_ui_strings


def ui_text(request):
    """
    Adds `ui` + `ui_lang` into every template context.
    Session-based preference set on /login/.
    """
    ui_lang = get_lang_from_request(request)
    return {
        "ui_lang": ui_lang,
        "ui": get_ui_strings(ui_lang),
    }

