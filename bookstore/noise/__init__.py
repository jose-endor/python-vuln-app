# Static-analysis corpus: submodules are imported for SAST line coverage; runtime is inert.
# RESEARCH-ONLY: dead branches, constants, and gates — not a second attack surface in practice.
from __future__ import annotations

from bookstore.noise import (
    assert_unreachable,
    constant_only_sinks,
    cwe_mitigated_pairs,
    dead_branches,
    fragment_sink_strings,
    http_constant_url,
    jinja_no_user,
    log_format_lookalike,
    no_op_orm,
    open_static_path,
    os_environ_gated,
    path_join_safe,
    pickle_literal,
    post_return_traps,
    redirect_lookalike,
    regex_lookalike,
    shell_literal,
    type_checking_sinks,
    weak_crypto_unused,
    xxe_string,
    yaml_safe_only,
)

__all__ = [
    "assert_unreachable",
    "constant_only_sinks",
    "cwe_mitigated_pairs",
    "dead_branches",
    "fragment_sink_strings",
    "http_constant_url",
    "jinja_no_user",
    "log_format_lookalike",
    "no_op_orm",
    "open_static_path",
    "os_environ_gated",
    "path_join_safe",
    "pickle_literal",
    "post_return_traps",
    "redirect_lookalike",
    "regex_lookalike",
    "shell_literal",
    "type_checking_sinks",
    "weak_crypto_unused",
    "xxe_string",
    "yaml_safe_only",
]

def describe_noise() -> str:
    """Inert: never registers routes; returns a static label for optional introspection."""
    return "noise-corpus-registered"
