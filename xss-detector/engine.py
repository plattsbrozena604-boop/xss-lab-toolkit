"""HTTP 请求与反射上下文分析。

这个模块只做两件事：
1. 发 GET 请求（带 Cookie），拿回响应；
2. 判断「注入的字符串落在 HTML 的什么位置」——文本节点 / 属性值 /
   <script> / 注释 / RCDATA，因为这决定了要用哪种 payload 才能跳出来。
"""

from __future__ import annotations

import html as html_lib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

TAG_OPEN_RE = re.compile(r"<\s*([a-zA-Z][\w:-]*)")
ATTR_RE = re.compile(r"""([\w:.-]+)\s*=\s*("[^"]*"|'[^']*'|[^\s>]+)""", re.DOTALL)

RAW_TEXT_TAGS = {"script", "style", "textarea", "title"}
RAW_TEXT_CONTEXT = {"script": "script", "style": "style", "textarea": "rcdata", "title": "rcdata"}


@dataclass
class Response:
    status: int
    body: str
    headers: dict[str, str] = field(default_factory=dict)
    url: str = ""
    elapsed: float = 0.0
    error: str | None = None

    def header(self, name: str, default: str = "") -> str:
        wanted = name.lower()
        for key, value in self.headers.items():
            if key.lower() == wanted:
                return value
        return default

    @property
    def ok(self) -> bool:
        return self.error is None and self.status != 0


def fetch(url: str, cookie: str = "", timeout: float = 10.0, ua: str | None = None) -> Response:
    headers = {
        "User-Agent": ua
        or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if cookie:
        headers["Cookie"] = cookie

    started = time.perf_counter()
    request = urllib.request.Request(url, headers=headers, method="GET")

    def build(status: int, raw: bytes, hdrs, final_url: str) -> Response:
        charset = "utf-8"
        try:
            if hdrs is not None:
                charset = hdrs.get_content_charset() or "utf-8"
        except Exception:
            charset = "utf-8"
        return Response(
            status=status,
            body=raw.decode(charset, "replace"),
            headers={k: v for k, v in (hdrs.items() if hdrs else [])},
            url=final_url,
            elapsed=time.perf_counter() - started,
        )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return build(response.status, response.read(3_000_000), response.headers, response.url)
    except urllib.error.HTTPError as exc:
        raw = b""
        try:
            raw = exc.read(3_000_000)
        except Exception:
            pass
        return build(exc.code, raw, exc.headers, exc.url or url)
    except Exception as exc:  # 连接失败 / 超时
        return Response(
            status=0,
            body="",
            headers={},
            url=url,
            elapsed=time.perf_counter() - started,
            error=f"{type(exc).__name__}: {exc}",
        )


def strip_fragment(url: str) -> str:
    return urllib.parse.urlsplit(url)._replace(fragment="").geturl()


def parse_params(url: str) -> list[tuple[str, str]]:
    return urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query, keep_blank_values=True)


def with_param(url: str, name: str, value: str) -> str:
    """替换（不存在则追加）某个 GET 参数，丢弃 fragment。"""
    parts = urllib.parse.urlsplit(url)
    pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    replaced = False
    out: list[tuple[str, str]] = []
    for key, old in pairs:
        if key == name and not replaced:
            out.append((key, value))
            replaced = True
        else:
            out.append((key, old))
    if not replaced:
        out.append((name, value))
    query = urllib.parse.urlencode(out, doseq=True)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))


# ── HTML 结构扫描：把响应切成「上下文区域」 ─────────────────────────


def scan_regions(html: str) -> list[tuple[int, int, dict]]:
    regions: list[tuple[int, int, dict]] = []
    n = len(html)
    i = 0
    text_start = 0

    def push_text(end: int) -> None:
        nonlocal text_start
        if end > text_start:
            regions.append((text_start, end, {"context": "html_text"}))
        text_start = end

    while i < n:
        # 注释
        if html.startswith("<!--", i):
            push_text(i)
            end = html.find("-->", i + 4)
            end = n if end < 0 else end + 3
            regions.append((i, end, {"context": "comment"}))
            i = text_start = end
            continue

        if html[i] != "<":
            i += 1
            continue

        match = TAG_OPEN_RE.match(html, i)
        if match is None:  # </ 闭合标签、比较符等，按文本处理
            i += 1
            continue

        name = match.group(1).lower()
        push_text(i)

        # 找标签结束（跳过引号内的 >）
        j = match.end()
        quote = ""
        while j < n:
            char = html[j]
            if quote:
                if char == quote:
                    quote = ""
            elif char in "\"'":
                quote = char
            elif char == ">":
                j += 1
                break
            j += 1

        tag_text = html[i:j]
        base = {"tag": name, "tag_text": tag_text}
        regions.append((i, j, {"context": "tag", **base}))

        if name in RAW_TEXT_TAGS:
            close = html.lower().find(f"</{name}", j)
            raw_end = n if close < 0 else close
            regions.append((j, raw_end, {"context": RAW_TEXT_CONTEXT[name], **base}))
            if close < 0:
                i = text_start = n
                break
            close_end = html.find(">", close)
            close_end = n if close_end < 0 else close_end + 1
            regions.append((close, close_end, {"context": "tag", **base, "closing": True}))
            i = text_start = close_end
            continue

        i = text_start = j

    push_text(n)
    return regions


def context_at(html: str, index: int, regions: list | None = None) -> dict:
    """返回 index 位置所处的上下文（index 指向待插入的字符位置）。"""
    regions = regions if regions is not None else scan_regions(html)
    for position, (start, end, info) in enumerate(regions):
        if start <= index < end:
            if info["context"] != "tag":
                return dict(info)

            # index 正好落在标签起始处：真正要看的是这个标签「所处的容器」，
            # 向前跳过相邻的标签区域，找到第一个非标签容器
            if index == start:
                cursor = start
                for back in range(position - 1, -1, -1):
                    prev_start, prev_end, prev_info = regions[back]
                    if prev_end != cursor:
                        break
                    if prev_info.get("context") != "tag":
                        return dict(prev_info)
                    cursor = prev_start
                return {"context": "html_text"}

            tag_text = info.get("tag_text", "")
            offset = index - start
            for match in ATTR_RE.finditer(tag_text):
                value_start, value_end = match.start(2), match.end(2)
                if value_start <= offset <= value_end:
                    raw = match.group(2)
                    quote = raw[0] if raw[:1] in ("\"", "'") else ""
                    ctx = {"\"": "attr_dq", "'": "attr_sq"}.get(quote, "attr_unq")
                    return {
                        "context": ctx,
                        "tag": info.get("tag"),
                        "attr": match.group(1).lower(),
                    }
            return {"context": "tag_space", "tag": info.get("tag")}
    return {"context": "html_text"}


CONTEXT_LABELS = {
    "html_text": "HTML 文本节点",
    "attr_dq": "双引号属性值",
    "attr_sq": "单引号属性值",
    "attr_unq": "无引号属性值",
    "tag_space": "标签内（属性之间）",
    "script": "<script> 脚本块",
    "style": "<style> 样式块",
    "comment": "HTML 注释",
    "rcdata": "RCDATA（textarea/title）",
}

URL_ATTRS = {"href", "src", "action", "formaction", "data", "poster", "srcset", "xlink:href"}


def describe_context(ctx: dict) -> str:
    label = CONTEXT_LABELS.get(ctx.get("context", ""), ctx.get("context", "未知"))
    if ctx.get("tag"):
        label += f" · <{ctx['tag']}"
        if ctx.get("attr"):
            label += f" {ctx['attr']}='...'"
        label += ">"
    return label


# ── 反射分析 ────────────────────────────────────────────────────


@dataclass
class Reflection:
    index: int
    context: dict

    @property
    def label(self) -> str:
        return describe_context(self.context)


def find_reflections(body: str, needle: str) -> list[Reflection]:
    regions = scan_regions(body)
    hits: list[Reflection] = []
    start = 0
    while True:
        index = body.find(needle, start)
        if index < 0:
            break
        hits.append(Reflection(index=index, context=context_at(body, index, regions)))
        start = index + len(needle)
    return hits


def html_encoded_forms(payload: str) -> list[str]:
    """payload 被 HTML 实体编码后的常见形态。"""
    escaped = html_lib.escape(payload, quote=True)
    return [
        escaped,
        payload.replace("<", "&lt;").replace(">", "&gt;"),
        payload.replace("<", "&#60;").replace(">", "&#62;"),
        payload.replace("<", "&#x3c;").replace(">", "&#x3e;"),
        urllib.parse.quote(payload),
        urllib.parse.quote(payload, safe=""),
    ]


JS_PAYLOAD_RE = re.compile(r"^\s*javascript\s*:", re.IGNORECASE)
INNER_TAG_RE = re.compile(r"<\s*([a-zA-Z][\w:-]*)")

# 能承载执行行为的标签
EXECUTABLE_TAGS = {
    "script", "img", "svg", "body", "iframe", "video", "audio", "source",
    "details", "input", "select", "textarea", "marquee", "math", "a", "div",
    "p", "object", "embed", "frame", "frameset", "form", "button", "table",
    "td", "b", "i", "u", "xmp", "nobr", "template", "mtext", "annotation-xml",
    "isindex", "keygen", "link", "meta", "style", "image",
}

# 真实存在的事件处理器名（用来否掉 ononerrorerror 这类写坏的属性）
KNOWN_HANDLERS = {
    "onerror", "onload", "onfocus", "onblur", "ontoggle", "onmouseover",
    "onmouseenter", "onmouseout", "onanimationstart", "onanimationend",
    "ontransitionend", "onstart", "onend", "onbegin", "onclick",
    "onpointerover", "onpointerenter", "oninput", "onchange", "onsubmit",
    "onscroll", "onwheel", "oncontextmenu", "ondrag", "ondrop", "onplay",
    "onplaying", "oncanplay", "onerrorcapture", "onfocusin",
}


def parse_tag(body: str, index: int) -> tuple[str, str] | None:
    """从 index（指向 '<'）解析出标签名与整个标签文本。"""
    match = TAG_OPEN_RE.match(body, index)
    if match is None:
        return None
    name = match.group(1).lower()
    j = match.end()
    quote = ""
    while j < len(body):
        char = body[j]
        if quote:
            if char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char == ">":
            j += 1
            break
        j += 1
    return name, body[index:j]


def _classify_tag(body: str, index: int, ctx: dict) -> tuple[str, str] | None:
    """判断响应里某个标签是否会执行。返回 None 表示「这个标签不行，继续看下一个」。"""
    parsed = parse_tag(body, index)
    if parsed is None:
        return None
    name, tag_text = parsed

    if name not in EXECUTABLE_TAGS:
        return "inert", f"解析出的标签是 <{name}>，不是有效可执行标签（payload 写坏或被过滤）"

    if name == "script":
        return "executes", f"<script> 落于 {describe_context(ctx)}，脚本块直接执行"

    lowered = tag_text.lower()
    if name == "iframe" and "srcdoc" in lowered:
        return "executes", "iframe srcdoc 的内容按 HTML 解析，脚本在内嵌文档里执行"

    attrs = [m.group(1).lower() for m in ATTR_RE.finditer(tag_text)]
    handlers = [a for a in attrs if a.startswith("on")]
    valid = [a for a in handlers if a in KNOWN_HANDLERS]
    if valid:
        return (
            "executes",
            f"<{name} {' '.join(valid)}> 落于 {describe_context(ctx)}，事件处理器有效",
        )

    if re.search(r"javascript\s*:", lowered) and any(a in URL_ATTRS for a in attrs):
        return "executes-on-click", f"<{name}> 的 URL 属性里是 javascript:，需用户点击"

    if handlers:
        return "inert", f"<{name}> 的事件名无效（{', '.join(handlers)}），不会触发"
    return "inert", f"<{name}> 内没有事件处理器（属性：{', '.join(attrs) or '无'}）"


def evaluate_payload(body: str, payload: str) -> tuple[str, str]:
    """判定一个 payload 在响应里的性质。

    返回 (outcome, 说明)：
      executes          —— 会被浏览器解析成可执行标签并触发
      executes-on-click —— javascript: 协议落在 URL 属性里（需点击）
      encoded           —— 被 HTML/URL 编码，不执行
      filtered          —— 被过滤/替换掉（找不到原样）
      inert             —— 原样存在，但标签/事件不成立，或仍被约束在属性/注释/脚本内
      not-reflected     —— 完全没反射
    """
    verbatim = body.find(payload)
    if verbatim < 0:
        for form in html_encoded_forms(payload):
            if form and form in body:
                return "encoded", f"响应里是编码后的形态：{form[:60]}"
        return "filtered", "响应中找不到原样 payload（被过滤/替换）"

    regions = scan_regions(body)
    first_reason: str | None = None

    # 逐个检查 payload 中出现的标签，取第一个「确实会执行」的
    for match in INNER_TAG_RE.finditer(payload):
        absolute = verbatim + match.start()
        ctx = context_at(body, absolute, regions)
        kind = ctx.get("context")

        if kind in ("attr_dq", "attr_sq", "attr_unq"):
            if first_reason is None:
                first_reason = f"标签仍落在属性值内（{describe_context(ctx)}）"
            continue
        if kind == "comment":
            if first_reason is None:
                first_reason = "标签落在 HTML 注释里"
            continue
        if kind == "script":
            if first_reason is None:
                first_reason = "标签落在 <script> 内部，不会被当作标签解析"
            continue
        if kind in ("tag_space", "tag"):
            # 这个位置已经在另一个标签内部（如 <scr<script>ipt>），不是新标签
            if first_reason is None:
                first_reason = "payload 里的标签被吞进了前一个标签"
            continue
        if kind in ("rcdata", "style") and not payload.lstrip().startswith("</"):
            if first_reason is None:
                first_reason = f"标签落在 {CONTEXT_LABELS.get(kind, kind)} 内"
            continue

        verdict = _classify_tag(body, absolute, ctx)
        if verdict is None:
            continue
        if verdict[0] in ("executes", "executes-on-click"):
            return verdict
        if first_reason is None:
            first_reason = verdict[1]

    if first_reason is not None:
        return "inert", first_reason

    if JS_PAYLOAD_RE.match(payload):
        ctx = context_at(body, verbatim, regions)
        if ctx.get("context") in ("attr_dq", "attr_sq", "attr_unq") and ctx.get("attr") in URL_ATTRS:
            return "executes-on-click", f"javascript: 落在 {ctx.get('attr')} 属性，需用户点击"
        return "inert", f"javascript: 未落在 URL 属性（{describe_context(ctx)}）"

    return "inert", "没有可执行标签"


# ── 金丝雀校验：直接看响应里出现了哪些「含 alert 的可执行标签」 ──────

ALERT_RE = re.compile(
    r"alert\s*[(`（]|alert\.call|self\s*\[\s*['\"]alert['\"]\]|window\.alert", re.IGNORECASE
)

EXEC_TAG_RE = re.compile(
    r"<\s*(script|img|svg|body|iframe|details|video|audio|source|input|select|textarea|"
    r"marquee|math|a|div|p|b|i|u|object|embed|frame|form|button|table|td|link|meta)\b[^>]*>",
    re.IGNORECASE,
)


def find_executable_tags(body: str) -> list[str]:
    """返回响应里所有「带 alert 且确实会执行」的标签片段。

    这是绕过验证的关键：过滤型 payload 被服务端改写后，原样字符串不再出现，
    但改写结果可能正好是一个合法可执行标签。
    只认真正的标签起点（排除 <scr<script> 这种被吞进上一个标签的情况）。
    """
    found: list[str] = []
    lowered = body.lower()
    regions = scan_regions(body)
    for match in EXEC_TAG_RE.finditer(body):
        start = match.start()
        if contextual_start(body, start, regions) is False:
            continue
        name = match.group(1).lower()
        tag_text = match.group(0)
        if name == "script":
            close = lowered.find("</script", match.end())
            content = body[match.end() : close if close >= 0 else len(body)]
            if ALERT_RE.search(content):
                found.append((tag_text + content.strip())[:100])
            continue
        if not ALERT_RE.search(tag_text):
            continue
        verdict = _classify_tag(body, start, {"context": "html_text"})
        if verdict is not None and verdict[0] in ("executes", "executes-on-click"):
            found.append(tag_text[:100])
    return found


def contextual_start(body: str, index: int, regions: list | None = None) -> bool:
    """index 处的 '<' 是否是真正的标签起点（而不是已处在标签/注释/脚本/RCDATA 内部）。"""
    ctx = context_at(body, index, regions)
    return ctx.get("context") == "html_text"
