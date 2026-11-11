# 反射型 XSS 检测工具（alert(1) 判定）

面向本机靶场 / 已授权私有环境的反射型 XSS 检测器。**判定标准只有一个：payload 能在响应里落进可执行位置并弹出 `alert(1)`。**

只做两件事：往 GET 参数里塞 `alert(1)` 类 payload、读响应判断会不会执行。不窃取 Cookie、不跳转、不发起外连、不写入任何数据。

## 运行

```powershell
cd xss-detector
pip install requests

# 默认读取 .env 里的 XSS_TARGET / XSS_COOKIE
python xsscan.py

# 完整绕过矩阵（即使首选 payload 成功也全测一遍）
python xsscan.py --full

# 指定参数 / 目标
python xsscan.py --url "http://127.0.0.1/dvwa-lab/vulnerabilities/xss_r/?name=test" --param name

# 只看首选 payload，不跑矩阵
python xsscan.py --no-bypass

# 本地报告面板（浏览 out/ 里的历次结果）
python webapp.py --port 8849 --open
```

输出：控制台摘要 + `out/xss_report_<时间戳>.md`（含逐条 payload 结果表、绕过分析、PoC）+ 同名 `.json`。

## 文件

| 文件 | 作用 |
| --- | --- |
| `xsscan.py` | CLI 主控：探测 → 上下文判定 → payload 验证 → 拦截分析 → 报告 |
| `engine.py` | HTTP 请求 + HTML 结构扫描（判断反射点落在哪种上下文）+ 可执行性判定 |
| `payloads.py` | payload 语料：按上下文分组的首选 payload + 30 条绕过矩阵 |
| `waf.py` | WAF/过滤指纹与拦截层级判定，生成绕过思路 |
| `webapp.py` | 本地面板：浏览 `out/` 里的历史报告（默认 `--port 8849`） |
| `web/` | 面板前端（原生 HTML/JS/CSS，无构建步骤） |

## 检测流程

1. **反射探测**：注入随机标记串，确认参数值是否出现在响应里、出现几次。
2. **字符存活**：分别注入 `< > " ' &`，看是原样回显、被 HTML 实体编码、还是被过滤。
3. **上下文判定**：把响应切成「区域」扫描，确定反射点落在哪：
   HTML 文本节点 / 双引号·单引号·无引号属性值 / 标签内属性之间 / `<script>` /
   `<style>` / HTML 注释 / RCDATA（textarea、title）。
4. **定向 payload**：按上下文取对应 payload（文本节点用 `<script>`、`<img onerror>`；
   属性里用 `">` 闭合跳出；`<script>` 里用 `';alert(1);//` …）。
5. **可执行性验证**（关键，不是「回显了就算」）：
   * payload 必须**原样**出现在响应里（被实体编码就判为不可执行）；
   * payload 里的标签要被浏览器真正解析成标签——不是落在注释、属性值、脚本块里；
   * 解析出的**标签名必须有效**，且**事件处理器名必须在真实事件名单里**
     （据此否掉 `<img src=x ononerrorerror=alert(1)>` 这种写坏的属性）；
   * 旧标签被吞掉的情况也会排除（`<scr<script>ipt>` 实际被解析成一个 `scr` 标签，不执行）。
6. **金丝雀复核**：如果原样字符串没回显，再扫一遍响应里「带 alert 且确实可执行」的标签。
   服务端把 payload 改写后正好还原成合法标签时（例如 `str_replace('<script>','')`
   把 `<script<script>>alert(1)</script>` 改回 `<script>alert(1)</script>`），这一步能认出来。

## 拦截分析与绕过

工具把「挡住」分成三类，因为绕过思路完全不同：

| 判定 | 依据 | 思路 |
| --- | --- | --- |
| `device-waf` 设备级 WAF | 请求被直接拒绝：403/406/429 + 拦截页/响应头特征（Cloudflare、ModSecurity、安全狗、阿里云盾…） | 换标签族、改语法特征、换长尾事件名、换 alert 调用形态、找未覆盖的参数或方法 |
| `app-blacklist` 应用层黑名单 | payload 被删掉一部分，页面仍正常回显 | 大小写混写、双写、替换标签族、改用不带尖括号的属性注入 |
| `output-encoded` 输出编码 | 反射回来是 `&lt; &gt; &quot;` | 基本无解（这是正确修复）；只再确认 `<script>`/URL 属性上下文是否有不同规则 |

绕过矩阵覆盖：大小写混写、`<script >`/换行/制表符/斜杠挂属性/多余属性分隔、
`<img/src/onerror=>`、双写（针对只删一次的过滤）、替代标签族
（svg / details / body / iframe srcdoc / video / audio / marquee / math）、
长尾事件（ontoggle / onfocus+autofocus / onstart / onanimationstart）、
`javascript:` 协议、alert 的多种调用形态（`alert\`1\``、`window.alert`、
`self['alert']`、`alert.call`、`void alert`），以及两条**编码对照项**
（HTML/十六进制实体编码——用来验证「编码」在 HTML 语境里并不构成绕过）。

## 实测结果（本机 DVWA，2026-11-07）

* **low**：`name` 参数反射在 `<pre>你好 ...</pre>` 的文本节点，`< > " ' &` 全部原样回显；
  `<script>alert(1)</script>` 直接命中，30 条矩阵里 28 条可执行，2 条编码对照不可执行。
* **medium**（服务端 `str_replace('<script>','')`）：`<script>` 被判为**被过滤**，
  `<img src=x onerror=alert(1)>` 绕过成立，判定为应用层黑名单。
* **high**（正则删除含 s…c…r…i…p…t 的标签）：同样由 `<img src=x onerror=alert(1)>` 绕过。

真实浏览器复核（Chrome）：

1. `?name=<script>document.title='XSS9f2a-SCRIPT-FIRED'</script>` → 页面标题被改写为
   `XSS9f2a-SCRIPT-FIRED`，证明注入的脚本在真实浏览器的 DVWA 页面上执行。
2. `?name=<img src=x onerror=alert(1)>` → 页面 JS 线程被模态框阻塞
   （`Runtime.evaluate` 超时），DOM 里存在 `<img onerror=...>`，证明 `onerror` 触发器执行且 `alert(1)` 弹出。

## 手工验证

把报告里的 PoC URL 贴进**已登录 DVWA** 的浏览器标签页，应立刻弹 `alert(1)`：

```
http://127.0.0.1/vulnerabilities/xss_r/?name=%3Cscript%3Ealert%281%29%3C%2Fscript%3E
```

注意：DVWA 的 `security` cookie 决定用哪份源码（`low/medium/high/impossible`）。
浏览器里的等级需为 low（或 medium/high 并改用对应的绕过 payload）；
`impossible.php` 有输出编码 + CSRF token，不存在反射型 XSS。

## 局限

* 「可执行」是**静态结构判定**（标签是否成形、事件名是否有效），不等于 100% 会在所有浏览器执行；
  交互型 payload（`onmouseover`、`javascript:`）需要用户操作。
* 不检测 DOM 型 XSS（源头在 `location`/`document.write`，需要浏览器端污点分析）。
* 不检测存储型 XSS（需要写入 + 二次访问）。
* 对 WAF 的判定基于响应特征与行为差异，可能漏判自研 WAF；矩阵结果本身比判定标签更可靠。

仅测试你拥有或明确获准测试的系统。
