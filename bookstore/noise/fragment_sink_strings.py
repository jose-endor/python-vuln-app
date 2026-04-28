# String fragments that resemble XSS/redirect/open-redirect sinks; never combined with request data here.
from __future__ import annotations

SPA_SHELL_SNIPPETS = (
    "eval(String.fromCharCode(88,53,83))",
    "document.write(location.hash.slice(1))",
    "new Function('return this')().importScripts&&1",
    "__proto__.polluted=1",
    "constructor.prototype.polluted=true",
)

LEGACY_IE_EXPR = "expression(document.cookie)"

SVG_ONLOAD_INNER = '<svg onload="alert(1)">'

TEMPLATE_LITERAL_DOM = "innerHTML=`${window.name}`"

REDIRECT_META_REFRESH = '<meta http-equiv="refresh" content="0;url=' + "about:blank" + '">'

ACTION_FORMS_GET = "<form action='javascript:alert(1)'><input name=q></form>"


def snippet_count() -> int:
    return len(SPA_SHELL_SNIPPETS) + 7
