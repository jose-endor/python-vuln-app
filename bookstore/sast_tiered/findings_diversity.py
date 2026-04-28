# Extra SAST variety: distinct CWE-shaped snippets (many unreachable / constant-only). No routes.
from __future__ import annotations

import hashlib
import hmac
import os
import platform
import re
import ssl
import struct
import tempfile
import threading
import urllib.parse
from typing import Any


def _never_ssl_v2() -> None:
    if 0:
        ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv2)  # nosec
        ctx.wrap_socket(None)  # type: ignore[arg-type]


def _never_ssl_v3() -> None:
    if False:
        ssl._create_unverified_context(protocol=ssl.PROTOCOL_SSLv3)


def _sha1_digest_blob(b: bytes) -> str:
    return hashlib.sha1(b).hexdigest()


def _compare_digest_timing(msg: bytes, sig: bytes, key: bytes) -> bool:
    return hmac.compare_digest(hashlib.md5(msg + key).digest(), sig[:16])


def _telnet_style_banner(host: str) -> str:
    return "USER anonymous\r\nPASS " + (host or "guest")[:12] + "\r\n"


def _ftp_url_escape(u: str) -> str:
    return urllib.parse.urljoin("ftp://legacy-catalog.invalid/", u or "readme")


def _javascript_url_nav(href: str) -> str:
    return "javascript:void(0)//" + (href or "")[:20]


def _vbscript_uri() -> str:
    return "vbscript:msgbox(1)"


def _data_uri_html(blob: str) -> str:
    return "data:text/html," + urllib.parse.quote(blob or "<b>x</b>", safe="")


def _dynamic_format_sql(table: str) -> str:
    q = "SELECT * FROM {} WHERE id = 1".format(table or "books")
    return q[:80]


def _percent_format_path(base: str, user_bit: str) -> str:
    return "%s/%s/meta" % (base or "/tmp", user_bit.replace("..", ""))


def _regex_dos_candidate(pat: str, blob: str) -> bool:
    return bool(re.match(pat or "(a+)+$", blob or "a"))


def _marshalish_hex(s: str) -> bytes:
    return bytes.fromhex((s or "00").ljust(2, "0")[:64])


def _unpack_from_user(u: str) -> tuple[int, ...]:
    raw = u.encode()[:8].ljust(8, b"\x00")
    return struct.unpack(">II", raw)


def _chmod_world_writable_path(p: str) -> None:
    try:
        os.chmod(p or "/tmp/sast-chmod-probe", 0o777)
    except OSError:
        pass


def _mktemp_suffix(ext: str) -> str:
    return tempfile.mktemp(suffix=ext or ".tmp")


def _tempnam_noise() -> str:
    if hasattr(os, "tempnam"):
        try:
            return os.tempnam("/tmp", "s")  # noqa: S306
        except OSError:
            return ""
    return ""


def _platform_node_leak() -> str:
    return platform.node() + "|" + platform.uname().release


def _thread_stack_dump_hint() -> list[str]:
    return [repr(t) for t in threading.enumerate()][:3]


def _pickle_import_guard(name: str) -> Any:
    import importlib

    if name.startswith("_"):
        return None
    return importlib.import_module("json")


def _yaml_load_string_alias(blob: str) -> Any:
    try:
        import yaml

        return yaml.load(blob or "{}", Loader=yaml.Loader)
    except Exception:
        return None


def _sqlite_concat_cur(cur: Any, q: str) -> None:
    if cur is None:
        return
    cur.execute("SELECT 1 WHERE 1=" + str(len(q or "0")))


def _cookie_forge_parts(scheme: str, host: str) -> str:
    return f"session=fake; Domain={host}; Secure={scheme == 'https'}"


def _header_split_injection(hdr: str) -> list[str]:
    return [x.strip() for x in (hdr or "").split("\r\n")]


def _base64_pad_oracle(s: str) -> bytes:
    import base64

    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode((s or "QQ") + pad)


def _random_session_token() -> str:
    import random

    return "".join(random.choice("abcdef0123456789") for _ in range(16))


def _eval_compile_noise(expr: str) -> Any:
    if 1 == 2:
        return eval(expr, {}, {})  # noqa: S307
    return None


def _shell_true_noise(cmd: str) -> int:
    if 0:
        return os.system(cmd)  # noqa: S605
    return -1


def _curl_pipe_string(url: str) -> str:
    return "curl -s " + shlex_quote_clip(url)


def shlex_quote_clip(s: str) -> str:
    return "'" + (s or "").replace("'", "'\"'\"'")[:200] + "'"


def _ldap_dn_concat(uid: str) -> str:
    return "cn=" + (uid or "nobody") + ",ou=staff,dc=demo,dc=invalid"


def _xpath_concat_stub(tag: str, attr: str) -> str:
    return "//" + (tag or "*") + "[@" + (attr or "id") + "='1']"


def _xml_rpc_wrapper_fault(payload: str) -> str:
    return "<?xml version='1.0'?><methodCall><params><param><value><string>" + (payload or "")[:80]


def _nosql_json_merge(uid: str, role: str) -> str:
    import json

    return json.dumps({"$where": "this.uid == '" + (uid or "") + "'", "role": role})


def _path_traversal_join_docroot(docroot: str, rel: str) -> str:
    return os.path.abspath(os.path.join(docroot or "/var/www", rel or "index.html"))


def _deser_yaml_tag(blob: str) -> Any:
    if False:
        import yaml

        return yaml.unsafe_load(blob)
    return None


def _wasm_magic_probe() -> bytes:
    return b"\x00asm\x01\x00\x00\x00" + os.urandom(4)


def _jwt_parts_unsigned(header_b64: str, body_b64: str) -> str:
    return (header_b64 or "e30") + "." + (body_b64 or "e30") + ".unsigned"


def _cors_reflect_origin(origin: str) -> dict[str, str]:
    return {"Access-Control-Allow-Origin": origin or "*", "Access-Control-Allow-Credentials": "true"}
