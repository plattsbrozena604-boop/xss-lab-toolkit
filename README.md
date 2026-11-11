# xss-lab-toolkit

一套**本地/已授权环境**用的 XSS 练习与检测组合：一个中文版 DVWA 靶场 + 一个反射型 XSS 检测器。

> 仅供本地靶场、自有资产、或获得书面授权的目标使用。仓库内的靶场代码**故意包含漏洞**，请勿部署到公网可访问的主机。

## 目录结构

```
xss-lab-toolkit/
├─ dvwa-lab/          # XSS 靶场：DVWA 的中文定制版（派生自 digininja/DVWA，GPL-3.0）
│  ├─ vulnerabilities/   # 13 个模块，low/medium/high/impossible 四档源码
│  │   ├─ xss_r/  xss_s/  xss_d/        # 反射型 / 存储型 / DOM 型
│  │   ├─ sqli/  sqli_blind/  brute/    # SQL 注入、盲注、暴力破解
│  │   ├─ exec/  fi/  upload/  csrf/    # 命令执行、文件包含、文件上传、CSRF
│  │   └─ csp/  javascript/  weak_id/   # CSP 绕过、JS 攻击、弱会话 ID
│  ├─ external/          # phpids / recaptcha（上游自带）
│  ├─ config/            # 只有 config.inc.php.dist，本地配置自己复制
│  └─ COPYING.txt        # GPL-3.0 原文
└─ xss-detector/      # 反射型 XSS 检测器（Python，自带 Web 报告面板）
   ├─ xsscan.py           # CLI 主控
   ├─ engine.py           # HTTP + HTML 结构扫描、可执行性判定
   ├─ payloads.py         # 分上下文 payload + 30 条绕过矩阵
   ├─ waf.py              # 拦截层级判定与绕过思路
   ├─ webapp.py           # 本地面板（默认 8849 端口）
   ├─ web/                # 面板前端（原生 HTML/JS，无构建）
   └─ .env.example        # 复制为 .env 填目标与会话 Cookie
```

## 一、靶场怎么跑起来

`dvwa-lab/` 是标准的 DVWA 目录，需要 PHP 7.x/8.x + MySQL/MariaDB 的 Web 环境（phpStudy、XAMPP、或 `php -S` + MySQL 均可）。

```bash
# 1) 复制配置并填数据库账号
cp dvwa-lab/config/config.inc.php.dist dvwa-lab/config/config.inc.php
#    编辑其中的 db_server / db_database / db_user / db_password

# 2) 把 dvwa-lab/ 放到站点根目录下（或整目录作为站点根）
#    浏览器访问：http://127.0.0.1/dvwa-lab/setup.php → 点 "Create / Reset Database"

# 3) 登录：http://127.0.0.1/dvwa-lab/login.php
#    默认账号 admin / password（首次 setup 生成）

# 4) 右上角 DVWA Security 选 low / medium / high / impossible 切换难度
```

> 仓库里**不含** `config.inc.php`（含数据库口令，上游 `.gitignore` 同样排除）、`external/` 之外的三方工具（phpMyAdmin 等）。数据库需自己导入，DVWA 用 `setup.php` 自动建表并灌入示例数据。

## 二、检测器怎么跑

```bash
cd xss-detector
pip install requests            # 唯一外部依赖

cp .env.example .env            # 填 XSS_TARGET（靶场 URL）与 XSS_COOKIE（登录后的会话 Cookie）
python xsscan.py                # 读 .env，跑一次完整检测
python xsscan.py --help         # 见全部参数
```

常用参数：

```bash
python xsscan.py --url "http://127.0.0.1/dvwa-lab/vulnerabilities/xss_r/?name=test" --param name
python xsscan.py --full        # 完整绕过矩阵（首选 payload 命中后仍全测）
python xsscan.py --no-bypass   # 只测首选 payload
python webapp.py --port 8849 --open   # 打开本地报告面板，浏览历次 out/ 结果
```

输出：控制台摘要 + `out/xss_report_<时间戳>.md` / `.json`（逐条 payload 结果表、上下文判定、拦截分类、PoC URL）。

判定标准只有一个：**payload 落进可执行位置并弹出 `alert(1)`**。不窃取 Cookie、不跳转、不发起外连、不写数据。详见 [xss-detector/README.md](xss-detector/README.md)。

## 三、本靶场相对上游 DVWA 的改动

`dvwa-lab/` 派生自 [digininja/DVWA](https://github.com/digininja/DVWA)（原 ethicalhack3r/DVWA），保留其 GPL-3.0 许可与 `COPYING.txt`。本仓库的增量改动：

1. **`vulnerabilities/` 中文化**：13 个模块的 `help/help.php` 说明与 `source/*.php` 中的提示文字汉化（英文结构与判分逻辑不变）。
2. **新增 `vulnerabilities/view_source_all.php`**：一页并列展示某模块 low/medium/high/impossible 四档源码，便于对照学习（上游只有单档 `view_source.php`）。
3. 移除 `phpMyAdmin` 等 Web 环境自带的三方工具，只保留 DVWA 本身。

## 四、许可与致谢

- 仓库整体按 **GPL-3.0** 发布（`LICENSE`），因为 `dvwa-lab/` 是 GPL-3.0 项目的衍生作品。
- 靶场部分版权归 DVWA 原作者（Ryan Dewhurst / digininja 及贡献者）；`xss-detector/` 为本人编写，同样以 GPL-3.0 发布以便与本仓库保持一致。

## 五、边界

靶场代码含**故意保留的漏洞**，用于学习与检测器验证。请不要把 `dvwa-lab/` 部署到任何公网可达、或含真实数据的服务器；也不要拿检测器去打你未获授权的站点。
