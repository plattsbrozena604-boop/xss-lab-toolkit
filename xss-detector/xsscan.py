"""反射型 XSS 检测工具（alert(1) 作为唯一判定标准）。

    .\\venv\\Scripts\\python.exe .\\xss_injection_tool\\xsscan.py
    .\\venv\\Scripts\\python.exe .\\xss_injection_tool\\xsscan.py --url "http://.../?name=test" --param name
    .\\venv\\Scripts\\python.exe .\\xss_injection_tool\\xsscan.py --full        # 强制跑完整绕过矩阵

只做两件事：往 GET 参数里塞 alert(1) 类 payload、读响应判断会不会执行。
不窃取 Cookie、不跳转、不发起外连、不写任何数据。
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import engine
import payloads
import waf

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

OUTCOME_LABELS = {
    "executes": "可执行",
    "executes-on-click": "需点击可执行",
    "reflected": "已反射",
    "inert": "反射但不可执行",
    "encoded": "被编码",
    "filtered": "被过滤",
    "blocked": "被拦截",
    "not-reflected": "未反射",
    "error": "请求失败",
}

BYPASS_LABELS = {
    "unfiltered": "无过滤",
    "device-waf": "设备级 WAF 拦截",
    "app-blacklist": "应用层黑名单",
    "output-encoded": "输出编码（已修复）",
    "partial": "部分过滤",
    "unclear": "不明确",
}


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip().lstrip("\ufeff")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass
class PayloadResult:
    group: str
    family: str
    payload: str
    outcome: str
    evidence: str
    status: int = 0
    length: int = 0

    @property
    def label(self) -> str:
        return OUTCOME_LABELS.get(self.outcome, self.outcome)


@dataclass
class ParamReport:
    name: str
    original: str
    reflections: list[dict] = field(default_factory=list)
    char_check: dict[str, str] = field(default_factory=dict)
    context: dict = field(default_factory=dict)
    primary: PayloadResult | None = None
    results: list[PayloadResult] = field(default_factory=list)
    bypass_kind: str = ""
    notes: list[str] = field(default_factory=list)
    poc_url: str = ""

    @property
    def vulnerable(self) -> bool:
        return self.primary is not None


# ── 探测辅助 ────────────────────────────────────────────────────


def char_survival(body: str, token: str, char: str) -> str:
    """判断某个特殊字符反射回来时的形态。"""
    if f"{token}{char}" in body:
        return "原样"
    candidates = [
        html.escape(char, quote=True),
        html.escape(char),
        urllib.parse.quote(char),
        f"&#{ord(char)};",
        f"&#x{ord(char):x};",
        f"&#X{ord(char):X};",
    ]
    for candidate in dict.fromkeys(candidates):
        if f"{token}{candidate}" in body:
            return f"编码为 {candidate}"
    return "丢失/过滤"


def test_payload(
    url: str,
    param: str,
    payload: str,
    family: str,
    cookie: str,
    timeout: float,
    baseline: engine.Response,
    baseline_tags: set[str],
    group: str = "首选",
) -> PayloadResult:
    target = engine.with_param(url, param, payload)
    response = engine.fetch(target, cookie, timeout)

    if response.error:
        return PayloadResult(group, family, payload, "error", response.error, 0, 0)

    blocked, reason = waf.looks_blocked(response, baseline)
    if blocked:
        return PayloadResult(
            group, family, payload, "blocked", reason, response.status, len(response.body)
        )

    outcome, evidence = engine.evaluate_payload(response.body, payload)

    # 原样没回显时再走一次金丝雀校验：服务端改写后的结果可能正是可执行标签
    if outcome in ("filtered", "inert"):
        injected = [tag for tag in engine.find_executable_tags(response.body) if tag not in baseline_tags]
        if injected:
            outcome = "executes"
            evidence = f"服务端改写后仍出现可执行标签：{injected[0]}"

    return PayloadResult(
        group, family, payload, outcome, evidence, response.status, len(response.body)
    )


# ── 事件流（CLI 打印 / Web SSE 共用） ──────────────────────────

STAGES: list[tuple[str, str]] = [
    ("reflect", "反射探测"),
    ("chars", "字符存活"),
    ("context", "上下文判定"),
    ("verify", "payload 验证"),
    ("bypass", "拦截分析"),
    ("report", "报告生成"),
]


def print_event(event: dict) -> None:
    """把事件渲染成命令行文本（CLI 模式）。"""
    kind = event.get("type")

    if kind == "baseline":
        print(f"[*] 基线   HTTP {event['status']} · {event['length']} 字节 · {event['elapsed']:.2f}s")
        print(f"[*] 防浏览器过滤头 X-XSS-Protection: {event.get('xxp') or '(无)'}")
    elif kind == "waf":
        if event["hits"]:
            for hit in event["hits"]:
                print(f"[!] 防护指纹：{hit['name']}（{hit['evidence']}）")
        else:
            print("[*] 基线页面未发现 WAF/防护设备特征")
    elif kind == "param_start":
        print(f"\n>> 检测参数 {event['name']}（原值 {event['original']!r}）")
    elif kind == "not_reflected":
        print(f"  [-] {event['name']}: 未反射")
    elif kind == "reflection":
        print(f"  [+] {event['name']}: 反射 {event['count']} 次 → {' / '.join(event['contexts'])}")
    elif kind == "chars":
        pretty = "  ".join(f"{ch}={state}" for ch, state in event["check"].items())
        print(f"      字符存活：{pretty}")
    elif kind == "context":
        print(f"      上下文：{event['label']}")
    elif kind == "payload":
        mark = "✔" if event["outcome"] in ("executes", "executes-on-click") else "·"
        print(f"      {mark} [{event['label']}] {event['group']}/{event['family']}: {event['payload'][:64]}")
        if event["outcome"] in ("executes", "executes-on-click") and event.get("evidence"):
            print(f"      [+] 命中：{event['evidence']}")
    elif kind == "bypass_kind":
        print(f"      拦截性质：{event['label']}")
        for note in event.get("notes", []):
            print(f"      - {note}")
    elif kind == "poc":
        print(f"      [→] PoC：{event['url']}")
    elif kind == "report":
        print(f"[*] 报告：{event['markdown']}")
        print(f"[*] 报告：{event['json']}")
    elif kind == "done":
        if event["vulnerable"]:
            print(f"\n[+] 结论：存在反射型 XSS（{event['vulnerable']} 个参数）")
            for poc in event["pocs"]:
                print(f"    参数 {poc['param']} · {poc['bypassLabel']}")
                print(f"    payload : {poc['payload']}")
                print(f"    PoC URL : {poc['url']}")
        else:
            print("\n[-] 结论：未发现可利用的反射型 XSS")
    elif kind == "error":
        print(f"[!] {event['message']}", file=sys.stderr)


# ── 单个参数检测 ────────────────────────────────────────────────


def scan_param(
    url: str,
    param: str,
    original: str,
    cookie: str,
    timeout: float,
    baseline: engine.Response,
    force_bypass: bool = False,
    skip_bypass: bool = False,
    emit=None,
) -> ParamReport:
    report = ParamReport(name=param, original=original)
    token = payloads.canary_token()
    baseline_tags = set(engine.find_executable_tags(baseline.body))
    out = emit if emit is not None else print_event

    def stage(key: str, state: str, detail: str = "") -> None:
        out(
            {
                "type": "stage",
                "stage": key,
                "label": dict(STAGES).get(key, key),
                "state": state,
                "detail": detail,
            }
        )

    out({"type": "param_start", "name": param, "original": original})

    # 1) 是否反射
    stage("reflect", "start")
    canary = engine.fetch(engine.with_param(url, param, token), cookie, timeout)
    if canary.error:
        report.notes.append(f"探测请求失败：{canary.error}")
        out({"type": "error", "message": f"{param}: 请求失败 {canary.error}"})
        stage("reflect", "error")
        return report

    reflections = engine.find_reflections(canary.body, token)
    if not reflections:
        report.notes.append("该参数的值没有出现在响应里（不反射）。")
        out({"type": "not_reflected", "name": param})
        stage("reflect", "done", "不反射")
        return report

    contexts: list[str] = []
    for item in reflections:
        if item.label not in contexts:
            contexts.append(item.label)
        report.reflections.append({"index": item.index, "context": item.label})
    out(
        {
            "type": "reflection",
            "name": param,
            "count": len(reflections),
            "contexts": contexts,
        }
    )
    stage("reflect", "done", f"反射 {len(reflections)} 次")

    # 2) 特殊字符编码情况
    stage("chars", "start")
    for char in ("<", ">", '"', "'", "&"):
        probe = engine.fetch(engine.with_param(url, param, token + char), cookie, timeout)
        report.char_check[char] = (
            char_survival(probe.body, token, char) if probe.ok else "请求失败"
        )
    out({"type": "chars", "name": param, "check": report.char_check})
    stage("chars", "done")

    # 3) 上下文判定 → 选首选 payload
    stage("context", "start")
    primary_context = next(
        (item.context for item in reflections if item.context.get("context") != "comment"),
        reflections[0].context,
    )
    report.context = primary_context
    out(
        {
            "type": "context",
            "name": param,
            "context": primary_context,
            "label": engine.describe_context(primary_context),
            "kind": primary_context.get("context"),
        }
    )
    stage("context", "done", engine.describe_context(primary_context))

    # 4) payload 验证
    stage("verify", "start")
    for family, payload in payloads.payloads_for(primary_context):
        result = test_payload(
            url, param, payload, family, cookie, timeout, baseline, baseline_tags
        )
        report.results.append(result)
        out(payload_event(result, param))
        if result.outcome in ("executes", "executes-on-click"):
            if report.primary is None:
                report.primary = result
            break
    stage("verify", "done", "命中" if report.primary else "首选未命中")

    # 5) 拦截 / 过滤分析：首选没成功就跑绕过矩阵
    need_bypass = (not skip_bypass) and (report.primary is None or force_bypass)
    if need_bypass:
        stage("bypass", "start")
        for group, family, payload in payloads.BYPASS_MATRIX:
            result = test_payload(
                url, param, payload, family, cookie, timeout, baseline, baseline_tags, group
            )
            report.results.append(result)
            out(payload_event(result, param))
            if report.primary is None and result.outcome in ("executes", "executes-on-click"):
                report.primary = result
        stage("bypass", "done", f"{len(payloads.BYPASS_MATRIX)} 条变体")

    report.bypass_kind = waf.classify_outcomes(report.results)
    report.notes.extend(waf.bypass_notes(report.bypass_kind, report.results))
    out(
        {
            "type": "bypass_kind",
            "name": param,
            "kind": report.bypass_kind,
            "label": BYPASS_LABELS.get(report.bypass_kind, report.bypass_kind),
            "notes": report.notes,
        }
    )

    if report.primary is not None:
        report.poc_url = engine.with_param(url, param, report.primary.payload)
        out(
            {
                "type": "poc",
                "name": param,
                "payload": report.primary.payload,
                "url": report.poc_url,
                "family": report.primary.family,
            }
        )

    return report


def payload_event(result: PayloadResult, param: str) -> dict:
    return {
        "type": "payload",
        "name": param,
        "group": result.group,
        "family": result.family,
        "payload": result.payload,
        "outcome": result.outcome,
        "label": result.label,
        "evidence": result.evidence,
        "status": result.status,
        "length": result.length,
    }


# ── 报告 ────────────────────────────────────────────────────────


def render_markdown(target: str, reports: list[ParamReport], waf_hits: list[tuple[str, str]], elapsed: float) -> str:
    lines: list[str] = [
        "# 反射型 XSS 检测报告",
        "",
        f"- 目标：`{target}`",
        f"- 时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- 耗时：{elapsed:.1f}s",
        f"- 判定标准：payload 能在响应中原样落进可执行位置并触发 `alert(1)`",
        "",
    ]

    wins = [r for r in reports if r.vulnerable]
    lines.append("## 结论")
    lines.append("")
    if wins:
        lines.append(f"**存在反射型 XSS**：{', '.join('`' + r.name + '`' for r in wins)} 参数。")
        for report in wins:
            lines.append("")
            lines.append(f"- 参数 `{report.name}` · 上下文：{engine.describe_context(report.context)}")
            lines.append(f"- 可用 payload：`{report.primary.payload}`")
            lines.append(f"- PoC URL：`{report.poc_url}`")
    else:
        lines.append("**未发现可利用的反射型 XSS**（详见各参数结果与拦截分析）。")
    lines.append("")

    if waf_hits:
        lines.append("## 防护指纹")
        lines.append("")
        for name, evidence in waf_hits:
            lines.append(f"- {name}：{evidence}")
        lines.append("")

    for report in reports:
        lines.append(f"## 参数 `{report.name}`")
        lines.append("")
        if report.reflections:
            lines.append(f"- 反射位置：{' / '.join(dict.fromkeys(r['context'] for r in report.reflections))}")
            lines.append(f"- 反射次数：{len(report.reflections)}")
        if report.char_check:
            lines.append(
                "- 字符存活：" + "，".join(f"`{k}` {v}" for k, v in report.char_check.items())
            )
        if report.context:
            lines.append(f"- 注入上下文：{engine.describe_context(report.context)}")
        if report.bypass_kind:
            kind_label = {
                "unfiltered": "无过滤",
                "device-waf": "设备级 WAF 拦截",
                "app-blacklist": "应用层黑名单",
                "output-encoded": "输出编码（已修复）",
                "partial": "部分过滤",
                "unclear": "不明确",
            }.get(report.bypass_kind, report.bypass_kind)
            lines.append(f"- 拦截性质：{kind_label}")
        lines.append("")

        if report.results:
            lines.append("| 分组 | 手法 | payload | 结果 | 依据 |")
            lines.append("| --- | --- | --- | --- | --- |")
            for item in report.results:
                payload_cell = item.payload.replace("|", "\\|").replace("\n", "\\n")[:70]
                evidence_cell = item.evidence.replace("|", "\\|")[:80]
                lines.append(
                    f"| {item.group} | {item.family} | `{payload_cell}` | {item.label} | {evidence_cell} |"
                )
            lines.append("")

        if report.notes:
            lines.append("**分析**")
            lines.append("")
            lines.extend(f"- {note}" for note in report.notes)
            lines.append("")

    lines.append("## 手工验证")
    lines.append("")
    if wins:
        lines.append("把下面的 URL 直接贴进**已登录目标站点**的浏览器标签页，应弹出 `alert(1)`：")
        lines.append("")
        for report in wins:
            lines.append(f"```\n{report.poc_url}\n```")
            lines.append("")
        lines.append("命令行确认（不发真实请求，只看服务端回显）：")
        lines.append("")
        lines.append("```powershell")
        lines.append('curl.exe -s -b "<你的Cookie>" "<上面的 PoC URL>" | Select-String -Pattern "alert\\(1\\)"')
        lines.append("```")
    else:
        lines.append("没有可直接使用的 PoC；如仍要深入，建议人工检查反射点的容器（属性/脚本/注释）与二次解码链路。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "本工具只使用 `alert(1)` 类无副作用 payload，不窃取凭据、不跳转、不发起外连、不修改任何数据。"
        "仅用于你拥有或已获授权的系统。"
    )
    return "\n".join(lines) + "\n"


def write_reports(out_dir: Path, target: str, reports: list[ParamReport], waf_hits, markdown: str) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    md_path = out_dir / f"xss_report_{stamp}.md"
    json_path = out_dir / f"xss_report_{stamp}.json"
    md_path.write_text(markdown, encoding="utf-8")
    payload = {
        "target": target,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "waf_fingerprint": [{"name": n, "evidence": e} for n, e in waf_hits],
        "parameters": [
            {
                "name": r.name,
                "original": r.original,
                "context": engine.describe_context(r.context) if r.context else "",
                "reflections": r.reflections,
                "char_check": r.char_check,
                "bypass_kind": r.bypass_kind,
                "vulnerable": r.vulnerable,
                "primary_payload": r.primary.payload if r.primary else None,
                "poc_url": r.poc_url,
                "results": [
                    {
                        "group": i.group,
                        "family": i.family,
                        "payload": i.payload,
                        "outcome": i.outcome,
                        "evidence": i.evidence,
                        "status": i.status,
                        "length": i.length,
                    }
                    for i in r.results
                ],
                "notes": r.notes,
            }
            for r in reports
        ],
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return md_path, json_path


# ── 入口 ────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="反射型 XSS 检测器（以 alert(1) 为判定标准，只读、无副作用）"
    )
    parser.add_argument("--url", help="目标 URL；默认读取 XSS_TARGET")
    parser.add_argument("--param", action="append", help="只测指定参数，可重复；默认测全部")
    parser.add_argument("--cookie", help="会话 Cookie；默认读取 XSS_COOKIE")
    parser.add_argument("--timeout", type=float, default=10.0, help="单请求超时秒数")
    parser.add_argument("--full", action="store_true", help="即使首选 payload 成功，也跑完整绕过矩阵")
    parser.add_argument("--no-bypass", action="store_true", help="不跑绕过矩阵（只试首选 payload）")
    parser.add_argument("--out-dir", default=str(Path(__file__).with_name("out")))
    return parser


def run_scan(
    url: str,
    params: list[tuple[str, str]],
    cookie: str,
    timeout: float = 10.0,
    force_bypass: bool = False,
    skip_bypass: bool = False,
    out_dir: Path | None = None,
    emit=None,
) -> tuple[list[ParamReport], Path | None, Path | None]:
    """完整跑一遍扫描。返回 (各参数报告, md 路径, json 路径)。"""
    out = emit if emit is not None else print_event
    started = datetime.now()

    out(
        {
            "type": "target",
            "url": url,
            "params": [name for name, _ in params],
            "cookiePresent": bool(cookie),
        }
    )

    baseline = engine.fetch(url, cookie, timeout)
    if baseline.error:
        out({"type": "error", "message": f"基线请求失败：{baseline.error}"})
        return [], None, None

    out(
        {
            "type": "baseline",
            "status": baseline.status,
            "length": len(baseline.body),
            "elapsed": baseline.elapsed,
            "xxp": baseline.header("X-XSS-Protection", ""),
            "server": baseline.header("Server", ""),
        }
    )

    waf_hits = waf.fingerprint(baseline)
    out({"type": "waf", "hits": [{"name": n, "evidence": e} for n, e in waf_hits]})

    reports: list[ParamReport] = []
    for name, original in params:
        report = scan_param(
            url=url,
            param=name,
            original=original,
            cookie=cookie,
            timeout=timeout,
            baseline=baseline,
            force_bypass=force_bypass,
            skip_bypass=skip_bypass,
            emit=emit,
        )
        reports.append(report)
        out(
            {
                "type": "param_done",
                "name": name,
                "vulnerable": report.vulnerable,
                "bypass_kind": report.bypass_kind,
            }
        )

    elapsed = (datetime.now() - started).total_seconds()
    markdown = render_markdown(url, reports, waf_hits, elapsed)

    md_path: Path | None = None
    json_path: Path | None = None
    out(
        {
            "type": "stage",
            "stage": "report",
            "label": dict(STAGES).get("report", "报告生成"),
            "state": "start",
            "detail": "",
        }
    )
    if out_dir is not None:
        md_path, json_path = write_reports(Path(out_dir), url, reports, waf_hits, markdown)
        out({"type": "report", "markdown": str(md_path), "json": str(json_path)})
    out(
        {
            "type": "stage",
            "stage": "report",
            "label": dict(STAGES).get("report", "报告生成"),
            "state": "done",
            "detail": "已落盘" if md_path else "",
        }
    )

    wins = [r for r in reports if r.vulnerable]
    out(
        {
            "type": "done",
            "elapsed": round(elapsed, 1),
            "vulnerable": len(wins),
            "pocs": [
                {
                    "param": r.name,
                    "payload": r.primary.payload,
                    "url": r.poc_url,
                    "family": r.primary.family,
                    "bypassKind": r.bypass_kind,
                    "bypassLabel": BYPASS_LABELS.get(r.bypass_kind, r.bypass_kind),
                    "context": engine.describe_context(r.context),
                }
                for r in wins
            ],
        }
    )
    return reports, md_path, json_path


def main() -> int:
    load_env(Path(__file__).with_name(".env"))
    args = build_parser().parse_args()

    url = engine.strip_fragment(args.url or os.getenv("XSS_TARGET", ""))
    cookie = args.cookie if args.cookie is not None else os.getenv("XSS_COOKIE", "")
    if not url:
        print("错误：请通过 --url 或 XSS_TARGET 设置目标", file=sys.stderr)
        return 2

    params = engine.parse_params(url)
    if not params:
        print("错误：目标 URL 没有可测试的 GET 参数", file=sys.stderr)
        return 2

    wanted = args.param or [name for name, _ in params]
    originals = dict(params)
    selected = [(name, originals.get(name, "")) for name in wanted]

    print("=" * 66)
    print("  反射型 XSS 检测 · alert(1) 判定 · 只读无副作用")
    print("=" * 66)
    print(f"[*] 目标   {url}")
    print(f"[*] 参数   {', '.join(wanted)}")
    print(f"[*] Cookie {'已载入' if cookie else '为空'}")

    reports, md_path, _ = run_scan(
        url=url,
        params=selected,
        cookie=cookie,
        timeout=args.timeout,
        force_bypass=bool(args.full),
        skip_bypass=bool(args.no_bypass),
        out_dir=Path(args.out_dir),
    )
    return 0 if any(r.vulnerable for r in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())

