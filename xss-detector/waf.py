"""WAF / 过滤行为识别与绕过分析。

区分三种「挡住」的原因，因为绕过思路完全不同：
1. 设备级 WAF（云 WAF、ModSecurity、安全狗…）——响应头/状态码/拦截页
2. 应用层黑名单/正则过滤 —— payload 被删掉一部分，响应仍是正常页面
3. 输出编码（HTML 实体 / URL 编码）—— 这是正确修复，通常无解
"""

from __future__ import annotations

import re

from engine import Response

# (名称, 响应头特征, 响应体特征)
WAF_SIGNATURES: list[tuple[str, list[str], list[str]]] = [
    ("Cloudflare", ["cf-ray", "server:cloudflare"], ["cf-error-details", "Attention Required", "cloudflare"]),
    ("ModSecurity", ["mod_security"], ["ModSecurity", "Mod_Security", "Request rejected", "Not Acceptable"]),
    ("安全狗 SafeDog", [], ["安全狗", "safedog", "SafeDog", "网站安全狗"]),
    ("阿里云盾", ["aliyunwaf"], ["errors.aliyun.com", "阿里云", "yundun", "aliyun_waf"]),
    ("腾讯云 WAF", [], ["waf.tencent", "腾讯云", "waf.qq.com"]),
    ("F5 BIG-IP ASM", [], ["The requested URL was rejected", "BIG-IP", "support ID"]),
    ("Imperva / Incapsula", ["x-iinfo", "x-cdn:incapsula"], ["Incapsula", "Imperva", "_Incapsula_Resource"]),
    ("AWS WAF", ["x-amzn-requestid"], ["Request blocked", "AWS WAF"]),
    ("360 网站卫士", [], ["360wzws", "网站卫士", "360webscan"]),
    ("创宇盾", [], ["知道创宇", "yunaq", "创宇"]),
    ("长亭雷池", [], ["雷池", "chaitin", "safeline"]),
    ("通用防火墙/IPS 页面", [], ["Access Denied", "拦截", "禁止访问", "非法的请求", "illegal request", "blocked"]),
]

BLOCK_STATUS = {403, 406, 429, 501, 503, 999}

BLOCK_HINT_RE = re.compile(
    r"(access\s+denied|request\s+(?:rejected|blocked)|forbidden|拦截|禁止访问|非法|"
    r"waf|firewall|security\s+policy|not\s+acceptable)",
    re.IGNORECASE,
)


def fingerprint(response: Response) -> list[tuple[str, str]]:
    """返回 [(WAF 名称, 命中依据)]，空列表表示没看到 WAF 特征。"""
    header_blob = "\n".join(f"{k}:{v}" for k, v in response.headers.items()).lower()
    body = response.body[:200_000]
    found: list[tuple[str, str]] = []

    for name, headers, bodies in WAF_SIGNATURES:
        for marker in headers:
            if marker.lower() in header_blob:
                found.append((name, f"响应头命中 {marker}"))
                break
        else:
            for marker in bodies:
                if marker.lower() in body.lower():
                    found.append((name, f"响应体命中 {marker!r}"))
                    break
    return found


def looks_blocked(response: Response, baseline: Response) -> tuple[bool, str]:
    """判断这次请求是否被设备级拦截。"""
    if response.error:
        return True, f"请求失败：{response.error}"

    if response.status in BLOCK_STATUS and response.status != baseline.status:
        snippet = " ".join(response.body[:120].split())
        return True, f"HTTP {response.status}（基线 {baseline.status}）：{snippet}"

    if response.status == baseline.status and response.body:
        if BLOCK_HINT_RE.search(response.body[:4000]) and not BLOCK_HINT_RE.search(
            baseline.body[:4000]
        ):
            return True, "响应体出现拦截提示，而基线页面没有"

    return False, ""


def classify_outcomes(results: list) -> str:
    """根据整批 payload 的结果，判断拦截发生在哪一层。

    判定顺序很重要：只要有被拒绝/被删改的迹象，就不能算「无过滤」，
    哪怕同时有别的 payload 成功绕过了。
    """
    outcomes = {item.outcome for item in results}

    if "blocked" in outcomes:
        return "device-waf"
    if "filtered" in outcomes:
        return "app-blacklist"
    if "encoded" in outcomes and "executes" not in outcomes:
        return "output-encoded"
    if "executes" in outcomes or "executes-on-click" in outcomes:
        return "unfiltered"
    if "inert" in outcomes:
        return "partial"
    return "unclear"


def bypass_notes(kind: str, results: list) -> list[str]:
    """针对拦截类型给出分析结论与下一步思路。"""
    notes: list[str] = []

    if kind == "unfiltered":
        notes.append("没有任何过滤迹象：首选 payload 已原样落进可执行位置。")
        return notes

    if kind == "device-waf":
        blocked = [r for r in results if r.outcome == "blocked"][:3]
        if blocked:
            notes.append(
                "存在设备级拦截：这些请求被直接拒绝而不是正常回显 —— "
                + "；".join(f"{r.family} → {r.evidence}" for r in blocked)
            )
        notes.append(
            "WAF 场景的常规思路（按优先级）："
            "① 先找它没覆盖的参数/路径（同参数不同编码、不同 HTTP 方法）；"
            "② 用不触发规则库的标签族（svg/details/video 等，很多规则只盯 script/img）；"
            "③ 改语法特征（大小写、空白/制表符/换行分隔、多余属性、斜杠挂属性）；"
            "④ 换事件名（ontoggle/onanimationstart/onfocus 等长尾事件）；"
            "⑤ 换 alert 的调用形态（alert`1`、window.alert、self['alert']、alert.call）。"
        )
        notes.append(
            "注意：编码类绕过的前提是容器会再解码一次。HTML 实体编码（&#60;）在 HTML 语境里"
            "不会被还原成标签，属于无效绕过，本工具矩阵里专门放了对照项用来验证这一点。"
        )
        return notes

    if kind == "app-blacklist":
        filtered = [r for r in results if r.outcome == "filtered"]
        passed = [r for r in results if r.outcome == "executes"]
        sample = "；".join(f"{r.family}" for r in filtered[:4])
        notes.append(f"应用层黑名单/正则过滤：{sample} 等被移除，但页面仍正常回显。")
        if passed:
            notes.append(
                "绕过成立："
                + "；".join(f"{r.family} → {r.payload}" for r in passed[:3])
                + "（这些标签不在过滤名单里，直接可执行）"
            )
        else:
            notes.append(
                "黑名单场景优先尝试：标签名大小写混写、双写（<scr<script>ipt>）、"
                "替换标签族（img/svg/details/video/marquee/math）、"
                "改用长尾事件名，以及不带尖括号的属性注入（onmouseover=）。"
            )
        return notes

    if kind == "output-encoded":
        notes.append(
            "输出被 HTML 实体编码（&lt; &gt; &quot; &#039;），标签无法成形。"
            "这通常意味着服务端做了正确的输出转义，反射型 XSS 基本不成立。"
        )
        notes.append(
            "仍值得确认的两点：① 反射点是否在 <script> 或 URL 属性里（编码规则可能不同）；"
            "② 是否存在二次解码（某些框架会先 urlencode 再 decode）。"
        )
        return notes

    notes.append("拦截类型不明确，建议人工比对响应差异（详见报告里的逐条 payload 结果）。")
    return notes
