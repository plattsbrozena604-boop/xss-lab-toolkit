'use strict';

/* ============================================================
   XSS EMBER · 前端
   EventSource 接 SSE，把探测过程渲染成流水线 / 控制台 / 结果
   ============================================================ */

const $ = (id) => document.getElementById(id);

const state = {
  stages: [],
  stageEls: new Map(),
  running: false,
  source: null,
  execCount: 0,
  variantCount: 0,
  reflectCount: 0,
  pocUrl: '',
  pocPayload: '',
};

const statValues = new Map();

/* ── 背景：升腾火星 ──────────────────────────────────────── */

function initEmbers() {
  const canvas = $('embers');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  let width = 0;
  let height = 0;
  const COUNT = 90;
  const sparks = [];

  const resize = () => {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * DPR;
    canvas.height = height * DPR;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  };

  const spawn = (initial = false) => ({
    x: Math.random() * width,
    y: initial ? Math.random() * height : height + Math.random() * 40,
    vx: (Math.random() - 0.5) * 0.22,
    vy: -(0.22 + Math.random() * 0.75),
    size: 0.6 + Math.random() * 1.9,
    life: 0,
    maxLife: 260 + Math.random() * 340,
    hue: 18 + Math.random() * 34,   // 橙 → 红
    flick: Math.random() * Math.PI * 2,
  });

  resize();
  for (let i = 0; i < COUNT; i++) sparks.push(spawn(true));
  window.addEventListener('resize', resize);

  let last = 0;
  const frame = (now) => {
    requestAnimationFrame(frame);
    if (now - last < 33) return;      // ~30fps
    last = now;
    ctx.clearRect(0, 0, width, height);
    ctx.globalCompositeOperation = 'lighter';

    for (let i = 0; i < sparks.length; i++) {
      const s = sparks[i];
      s.life += 1;
      s.flick += 0.18;
      s.x += s.vx + Math.sin(s.flick * 0.6) * 0.35;
      s.y += s.vy;

      const t = Math.min(1, s.life / s.maxLife);
      const alpha = (1 - t) * (0.5 + 0.5 * Math.abs(Math.sin(s.flick)));
      if (s.life > s.maxLife || s.y < -30) {
        sparks[i] = spawn(false);
        continue;
      }

      const r = s.size * (1 - t * 0.45);
      const grad = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, r * 4.5);
      grad.addColorStop(0, `hsla(${s.hue + 12}, 100%, 72%, ${alpha * 0.95})`);
      grad.addColorStop(0.45, `hsla(${s.hue}, 100%, 55%, ${alpha * 0.42})`);
      grad.addColorStop(1, `hsla(${s.hue - 6}, 100%, 48%, 0)`);
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(s.x, s.y, r * 4.5, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';
  };
  requestAnimationFrame(frame);
}

/* ── 小工具 ──────────────────────────────────────────────── */

const escapeHtml = (v) =>
  String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const escapeAttr = escapeHtml;
const clock = () => new Date().toLocaleTimeString('zh-CN', { hour12: false });

function toast(message, kind = '') {
  const box = $('toasts');
  const el = document.createElement('div');
  el.className = 'toast';
  if (kind) el.dataset.kind = kind;
  el.textContent = message;
  box.appendChild(el);
  setTimeout(() => {
    el.classList.add('hide');
    setTimeout(() => el.remove(), 260);
  }, 3200);
}

async function copyText(text, label) {
  try {
    await navigator.clipboard.writeText(text);
    toast(`已复制${label ? '：' + label : ''}`, 'ok');
  } catch {
    // 剪贴板被限制时的兜底
    const range = document.createRange();
    const pre = document.createElement('textarea');
    pre.value = text;
    document.body.appendChild(pre);
    pre.select();
    try { document.execCommand('copy'); toast('已复制', 'ok'); } catch { toast('复制失败', 'err'); }
    pre.remove();
    range.detach?.();
  }
}

function setStat(id, value) {
  const el = $(id);
  if (!el) return;
  const from = Number(statValues.get(id) ?? 0);
  statValues.set(id, value);
  const final = String(value);
  // 后台标签页 rAF 会被挂起，直接落值避免停在旧值
  if (from === value || document.hidden || !Number.isFinite(Number(value))) {
    el.textContent = final;
    return;
  }
  el.classList.remove('bump');
  void el.offsetWidth;
  el.classList.add('bump');
  const started = performance.now();
  const duration = 480;
  let settled = false;
  const tick = (now) => {
    const p = Math.min(1, (now - started) / duration);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = String(Math.round(from + (Number(value) - from) * eased));
    if (p < 1) requestAnimationFrame(tick);
    else settled = true;
  };
  requestAnimationFrame(tick);
  setTimeout(() => { if (!settled) el.textContent = final; }, duration + 150);
}

/* ── 控制台 ──────────────────────────────────────────────── */

const MAX_LINES = 800;

function classify(text) {
  if (text.startsWith('[!]')) return 'warn';
  if (text.startsWith('[+]')) return 'ok';
  if (text.startsWith('[-]')) return 'dim';
  if (text.startsWith('[*]')) return 'info';
  if (text.startsWith('>')) return 'stage';
  return 'data';
}

function logLine(text, kind) {
  const box = $('console');
  const line = document.createElement('div');
  line.className = 'line line--' + (kind || classify(text));
  const time = document.createElement('span');
  time.className = 't';
  time.textContent = clock();
  const msg = document.createElement('span');
  msg.className = 'm';
  msg.textContent = text;
  line.append(time, msg);
  box.appendChild(line);
  while (box.childElementCount > MAX_LINES) box.firstElementChild.remove();
  box.scrollTop = box.scrollHeight;
}

/* ── 流水线 ──────────────────────────────────────────────── */

function renderStages() {
  const ol = $('stages');
  ol.innerHTML = '';
  state.stageEls.clear();
  state.stages.forEach((stage, i) => {
    const li = document.createElement('li');
    li.className = 'stage';
    li.dataset.state = 'idle';
    li.dataset.label = stage.label;
    li.innerHTML = `<span class="n">${String(i + 1).padStart(2, '0')}</span>${escapeHtml(stage.label)}`;
    ol.appendChild(li);
    state.stageEls.set(stage.key, li);
  });
  updateProgress();
}

function setStage(key, stateName, detail) {
  const el = state.stageEls.get(key);
  if (!el) return;
  el.dataset.state = stateName;
  if (stateName === 'start') logLine(`> ${el.dataset.label}${detail ? ' · ' + detail : ''}`, 'stage');
  if (stateName === 'done' && detail) logLine(`[*] ${el.dataset.label} 完成 · ${detail}`, 'info');
  updateProgress();
}

function updateProgress() {
  const total = state.stageEls.size || 1;
  let done = 0;
  state.stageEls.forEach((el) => { if (el.dataset.state === 'done') done += 1; });
  $('progressBar').style.width = `${Math.round((done / total) * 100)}%`;
}

function resetStages() {
  state.stageEls.forEach((el) => { el.dataset.state = 'idle'; });
  updateProgress();
}

/* ── 运行状态 ────────────────────────────────────────────── */

function setBusy(busy) {
  state.running = busy;
  const btn = $('scanBtn');
  btn.disabled = busy;
  btn.dataset.busy = busy ? '1' : '';
  const pill = $('statusPill');
  if (busy) {
    pill.dataset.state = 'running';
    pill.querySelector('span').textContent = '扫描中';
  }
}

function setIdle(label, kind) {
  const pill = $('statusPill');
  pill.dataset.state = kind || 'idle';
  pill.querySelector('span').textContent = label || '待机';
}

function endRun() {
  if (state.source) { state.source.close(); state.source = null; }
  state.running = false;
  const btn = $('scanBtn');
  btn.disabled = false;
  btn.dataset.busy = '';
}

/* ── 结果渲染 ────────────────────────────────────────────── */

function hideEmpty() {
  const empty = $('emptyState');
  if (empty) empty.style.display = 'none';
}

function setVerdict(markState, title, sub) {
  const box = $('verdict');
  box.dataset.state = markState;
  $('verdictMark').textContent = markState === 'hit' ? '✸' : markState === 'clear' ? '✓' : '◇';
  $('verdictTitle').textContent = title;
  $('verdictSub').textContent = sub;
}

function addFact(key, value, hot = false) {
  const box = $('facts');
  const card = document.createElement('div');
  card.className = 'fact' + (hot ? ' fact--hot' : '');
  card.style.animationDelay = `${box.childElementCount * 40}ms`;
  card.innerHTML = `<span class="k">${escapeHtml(key)}</span><span class="v">${escapeHtml(value)}</span>`;
  box.appendChild(card);
}

function clearResults() {
  hideEmpty();
  $('facts').innerHTML = '';
  $('charcheck').innerHTML = '';
  $('pocBox').innerHTML = '';
  $('matrix').innerHTML = '';
  $('notes').innerHTML = '';
  $('reportLinks').innerHTML = '';
  state.execCount = 0;
  state.variantCount = 0;
  state.reflectCount = 0;
  state.pocUrl = '';
  state.pocPayload = '';
  setStat('statReflect', 0);
  setStat('statExec', 0);
  setStat('statVariants', 0);
  setStat('statElapsed', '0s');
}

function renderChars(check) {
  const box = $('charcheck');
  box.innerHTML = '';
  Object.entries(check || {}).forEach(([char, text], i) => {
    const chip = document.createElement('span');
    chip.className = 'char-chip';
    chip.dataset.state = /原样/.test(text) ? 'raw' : /编码/.test(text) ? 'encoded' : 'lost';
    chip.style.animationDelay = `${i * 40}ms`;
    chip.title = `${char} → ${text}`;
    chip.innerHTML = `<em>${escapeHtml(char)}</em>${escapeHtml(text)}`;
    box.appendChild(chip);
  });
}

function ensureMatrix() {
  let wrap = $('matrix').querySelector('.matrix-wrap');
  if (wrap) return wrap.querySelector('tbody');
  const head = document.createElement('div');
  head.className = 'matrix-head';
  head.innerHTML = '<span>payload 矩阵</span><span class="count" id="matrixCount">0 条</span>';
  const box = document.createElement('div');
  box.className = 'matrix-wrap';
  box.innerHTML = `
    <table class="matrix-table">
      <thead><tr><th>分组</th><th>手法</th><th>payload</th><th>结果</th><th>依据</th></tr></thead>
      <tbody></tbody>
    </table>`;
  $('matrix').append(head, box);
  return box.querySelector('tbody');
}

function addMatrixRow(event) {
  const tbody = ensureMatrix();
  const tr = document.createElement('tr');
  tr.dataset.outcome = event.outcome;
  const isExec = event.outcome === 'executes' || event.outcome === 'executes-on-click';
  if (isExec) tr.classList.add('is-hit');
  tr.innerHTML = `
    <td title="分组">${escapeHtml(event.group)}</td>
    <td title="手法">${escapeHtml(event.family)}</td>
    <td class="pay" title="${escapeAttr(event.payload)}">${escapeHtml(event.payload)}</td>
    <td class="out">${escapeHtml(event.label)}</td>
    <td title="${escapeAttr(event.evidence)}">${escapeHtml(event.evidence)}</td>`;
  tbody.appendChild(tr);
  const box = tbody.closest('.matrix-wrap');
  if (box) box.scrollTop = box.scrollHeight;

  state.variantCount += 1;
  if (isExec) state.execCount += 1;
  setStat('statVariants', state.variantCount);
  setStat('statExec', state.execCount);
  const counter = $('matrixCount');
  if (counter) counter.textContent = `${state.variantCount} 条`;
}

function renderPoc(event) {
  state.pocUrl = event.url;
  state.pocPayload = event.payload;
  const box = $('pocBox');
  box.innerHTML = `
    <div class="poc-card">
      <div class="poc-head">
        <span>PoC · alert(1)</span>
        <span class="tag">${escapeHtml(event.family || '')}</span>
        <span class="tag">参数 ${escapeHtml(event.name || '')}</span>
      </div>
      <div class="poc-row">
        <span class="k">payload</span>
        <code id="pocPayload">${escapeHtml(event.payload)}</code>
      </div>
      <div class="poc-row">
        <span class="k">可执行地址</span>
        <code class="url" id="pocUrl">${escapeHtml(event.url)}</code>
      </div>
      <div class="poc-actions">
        <button type="button" id="copyPayload">复制 payload</button>
        <button type="button" id="copyUrl">复制 URL</button>
        <a href="${escapeAttr(event.url)}" target="_blank" rel="noopener noreferrer"
           title="在新标签页打开（会立刻弹出 alert，属于预期行为）">在浏览器打开 ↗</a>
      </div>
    </div>`;

  $('copyPayload').addEventListener('click', () => copyText(state.pocPayload, 'payload'));
  $('copyUrl').addEventListener('click', () => copyText(state.pocUrl, 'PoC URL'));
  toast('拿到 alert(1) PoC', 'ok');
}

/* ── 事件分发 ────────────────────────────────────────────── */

function handleEvent(event) {
  switch (event.type) {
    case 'target':
      $('targetChip').textContent = event.url;
      $('targetChip').title = event.url;
      logLine(`[*] 目标 ${event.url}`, 'info');
      logLine(`[*] 参数 ${event.params.join(', ')} · Cookie ${event.cookiePresent ? '已载入' : '为空'}`, 'info');
      break;

    case 'baseline':
      addFact('基线响应', `HTTP ${event.status} · ${event.length} B`);
      addFact('响应耗时', `${Number(event.elapsed).toFixed(2)} s`);
      addFact('X-XSS-Protection', event.xxp || '(无)');
      logLine(`[*] 基线 HTTP ${event.status} · ${event.length} 字节 · ${Number(event.elapsed).toFixed(2)}s`, 'info');
      logLine(`[*] X-XSS-Protection: ${event.xxp || '(无)'}`, 'dim');
      break;

    case 'waf':
      if (event.hits && event.hits.length) {
        event.hits.forEach((hit) => {
          addFact('防护指纹', `${hit.name}`, true);
          logLine(`[!] 防护指纹：${hit.name}（${hit.evidence}）`, 'warn');
        });
        toast(`检测到防护设备：${event.hits.map((h) => h.name).join(', ')}`, 'warn');
      } else {
        logLine('[*] 基线页面未发现 WAF/防护设备特征', 'dim');
      }
      break;

    case 'param_start':
      clearResults();
      resetStages();
      logLine(`> 检测参数 ${event.name}（原值 ${JSON.stringify(event.original)}）`, 'stage');
      break;

    case 'not_reflected':
      setVerdict('clear', `${event.name} 未反射`, '参数值没有出现在响应里，不存在反射型注入');
      logLine(`[-] ${event.name}: 未反射，跳过`, 'dim');
      break;

    case 'reflection':
      state.reflectCount = event.count;
      setStat('statReflect', event.count);
      addFact('反射次数', `${event.count} 次`, true);
      addFact('反射位置', event.contexts.join(' / '), true);
      setVerdict('pending', '已确认反射', `反射 ${event.count} 次 · 继续判定上下文`);
      logLine(`[+] ${event.name}: 反射 ${event.count} 次 → ${event.contexts.join(' / ')}`, 'ok');
      break;

    case 'chars':
      renderChars(event.check);
      logLine('[+] 字符存活：' + Object.entries(event.check).map(([k, v]) => `${k}=${v}`).join('  '), 'ok');
      break;

    case 'context':
      addFact('注入上下文', event.label, true);
      logLine(`[*] 注入上下文：${event.label}`, 'info');
      break;

    case 'payload':
      addMatrixRow(event);
      if (event.outcome === 'executes' || event.outcome === 'executes-on-click') {
        logLine(`[+] 命中 [${event.label}] ${event.group}/${event.family}：${event.payload}`, 'ok');
      } else {
        logLine(`[-] [${event.label}] ${event.group}/${event.family}：${event.payload}`, 'dim');
      }
      break;

    case 'bypass_kind': {
      const badge = document.createElement('div');
      badge.className = 'kind-badge';
      badge.dataset.kind = event.kind;
      badge.textContent = `拦截性质：${event.label}`;
      $('notes').appendChild(badge);
      (event.notes || []).forEach((note) => {
        const el = document.createElement('div');
        el.className = 'note';
        el.textContent = note;
        $('notes').appendChild(el);
      });
      logLine(`[*] 拦截性质：${event.label}`, 'info');
      break;
    }

    case 'poc':
      renderPoc(event);
      setVerdict(
        'hit',
        '存在反射型 XSS · alert(1) 可执行',
        `${event.name} 参数 · ${event.family} · 已生成可执行 PoC`
      );
      logLine(`[+] PoC：${event.url}`, 'ok');
      setIdle('已确认', 'hit');
      break;

    case 'param_done':
      if (!event.vulnerable) {
        setVerdict('clear', '未发现可利用的反射型 XSS', '该参数没有可利用的执行路径');
      }
      break;

    case 'report': {
      const box = $('reportLinks');
      const add = (path, label) => {
        if (!path) return;
        const name = path.split(/[\\/]/).pop();
        const link = document.createElement('a');
        link.href = `/report/${encodeURIComponent(name)}`;
        link.target = '_blank';
        link.rel = 'noopener';
        link.textContent = `报告 · ${label}`;
        link.title = path;
        box.appendChild(link);
      };
      add(event.markdown, 'Markdown');
      add(event.json, 'JSON');
      logLine(`[+] 报告已生成：${event.markdown}`, 'ok');
      break;
    }

    case 'done':
      setStat('statElapsed', `${event.elapsed}s`);
      if (event.vulnerable) {
        setVerdict('hit', `确认反射型 XSS（${event.vulnerable} 个参数）`, '见下方 PoC，可直接在浏览器验证 alert(1)');
        setIdle('已确认', 'hit');
        toast(`确认 ${event.vulnerable} 个参数存在反射型 XSS`, 'ok');
      } else {
        setVerdict('clear', '未发现可利用的反射型 XSS', '可查看下方矩阵了解被拦截/编码的具体项');
        setIdle('未命中', 'clear');
      }
      logLine(`[+] 扫描完成 · 用时 ${event.elapsed}s`, 'ok');
      endRun();
      break;

    case 'stage':
      setStage(event.stage, event.state, event.detail);
      break;

    case 'error':
      logLine(`[!] ${event.message}`, 'err');
      toast(event.message, 'err');
      setIdle('错误', 'error');
      endRun();
      break;

    case 'end':
      endRun();
      break;

    default:
      break;
  }
}

/* ── 启动扫描 ────────────────────────────────────────────── */

function startScan() {
  if (state.running) return;
  const target = $('urlInput').value.trim();
  if (!target) {
    toast('请先填写目标 URL', 'err');
    $('urlInput').focus();
    return;
  }

  const params = new URLSearchParams();
  params.set('url', target);
  params.set('cookie', $('cookieInput').value);
  params.set('timeout', $('timeoutInput').value || '10');
  if ($('fullToggle').checked) params.set('full', '1');
  if ($('paramInput').value.trim()) params.set('param', $('paramInput').value.trim());

  clearResults();
  resetStages();
  setBusy(true);
  setVerdict('pending', '扫描进行中', '正在探测反射点与上下文…');
  logLine('[*] 启动反射型 XSS 扫描…', 'info');

  const source = new EventSource(`/api/scan?${params.toString()}`);
  state.source = source;

  source.onmessage = (e) => {
    let payload;
    try { payload = JSON.parse(e.data); } catch { return; }
    handleEvent(payload);
  };

  source.onerror = () => {
    if (!state.running) {
      if (state.source) state.source.close();
      state.source = null;
      return;
    }
    logLine('[!] 事件流中断（服务端可能拒绝了本次任务）', 'err');
    toast('事件流中断', 'err');
    setIdle('错误', 'error');
    endRun();
  };
}

/* ── 清空 / 目标解析 ─────────────────────────────────────── */

function resetAll() {
  clearResults();
  resetStages();
  $('pocBox').innerHTML = '';
  $('matrix').innerHTML = '';
  $('notes').innerHTML = '';
  $('reportLinks').innerHTML = '';
  setVerdict('idle', '等待扫描', '配置目标后点击「开始扫描」');
  setIdle('待机', 'idle');
  const empty = $('emptyState');
  if (empty) empty.style.display = '';
  logLine('[+] 结果与日志已清空', 'dim');
}

function urlParams(raw) {
  try {
    return [...new URL(raw).searchParams.keys()];
  } catch {
    const query = raw.split('?')[1];
    if (!query) return [];
    return query.split('&').map((p) => decodeURIComponent(p.split('=')[0])).filter(Boolean);
  }
}

function setAuth(present) {
  $('authDot').dataset.on = present ? '1' : '0';
  $('authText').textContent = present ? 'Cookie 已载入' : 'Cookie 为空';
}

function syncTarget() {
  const raw = $('urlInput').value.trim();
  $('targetChip').textContent = raw || '未配置目标';
  $('targetChip').title = raw;
  const params = urlParams(raw);
  $('paramList').innerHTML = params.map((n) => `<option value="${escapeAttr(n)}"></option>`).join('');
  if (params.length && !params.includes($('paramInput').value.trim())) {
    $('paramInput').value = params[0];
  }
}

/* ── 初始化 ──────────────────────────────────────────────── */

function wireEvents() {
  $('scanBtn').addEventListener('click', startScan);
  $('clearBtn').addEventListener('click', resetAll);
  $('clearConsole').addEventListener('click', () => {
    $('console').innerHTML = '';
    logLine('[*] 控制台已清空', 'dim');
  });
  $('urlInput').addEventListener('input', syncTarget);
  $('cookieInput').addEventListener('input', () => setAuth(!!$('cookieInput').value.trim()));
  $('revealCookie').addEventListener('click', (e) => {
    const masked = $('cookieInput').classList.toggle('masked');
    e.target.textContent = masked ? '显示' : '隐藏';
  });

  // 点矩阵单元格复制 payload
  document.addEventListener('click', (event) => {
    const cell = event.target.closest('table.matrix-table td');
    if (!cell || !cell.classList.contains('pay')) return;
    copyText(cell.textContent, 'payload');
  });
}

async function boot() {
  initEmbers();
  wireEvents();
  try {
    const data = await (await fetch('/api/defaults')).json();
    $('urlInput').value = data.url || '';
    $('cookieInput').value = data.cookie || '';
    if (data.timeout) $('timeoutInput').value = data.timeout;
    state.stages = data.stages || [];
    renderStages();
    setAuth(!!data.cookiePresent);
    syncTarget();
    $('matrixCount').textContent = data.matrixCount ?? '30';
    logLine('[+] 控制台就绪，等待指令', 'ok');
    logLine('[*] 判定标准：payload 落进可执行位置并弹出 alert(1)；不做任何破坏性动作', 'dim');
  } catch (err) {
    logLine(`[!] 无法载入默认配置：${err.message}`, 'err');
  }
}

boot();
