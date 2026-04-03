/* ══════════════════════════════════════
   ASOS -- script.js
   AI-Assisted Storage Optimization System
══════════════════════════════════════ */

/* ── TYPING ANIMATION ── */
(function initTyping() {
  const el = document.getElementById('typingTarget');
  if (!el) return;
  const lines = ['AI-Assisted', 'Storage Optimization', 'System.'];
  const fullText = lines.join('\n');
  let i = 0;

  function type() {
    if (i <= fullText.length) {
      const slice = fullText.slice(0, i);
      el.innerHTML = slice.replace(/\n/g, '<br />') + '<span class="cursor">|</span>';
      i++;
      setTimeout(type, i === 1 ? 500 : 48);
    } else {
      // keep blinking cursor
      el.innerHTML = fullText.replace(/\n/g, '<br />') + '<span class="cursor">|</span>';
    }
  }
  setTimeout(type, 700);
})();

/* ── NAV: HAMBURGER ── */
(function initNav() {
  const btn = document.getElementById('hamburger');
  const mob = document.getElementById('mobileNav');
  btn.addEventListener('click', () => mob.classList.toggle('open'));
  document.querySelectorAll('.mobile-nav__link').forEach(l => {
    l.addEventListener('click', () => mob.classList.remove('open'));
  });
})();

/* ── PIPELINE STEP REVEAL ── */
(function initPipeline() {
  const steps = document.querySelectorAll('.pipe-step');
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const allSteps = document.querySelectorAll('.pipe-step');
        allSteps.forEach((s, i) => {
          setTimeout(() => s.classList.add('visible'), i * 75);
        });
        observer.disconnect();
      }
    });
  }, { threshold: 0.2 });
  const pipeline = document.querySelector('.pipeline');
  if (pipeline) observer.observe(pipeline);
})();

/* ── ANIMATED COUNTERS ── */
(function initCounters() {
  const counters = document.querySelectorAll('.counter');
  const seen = new Set();

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !seen.has(entry.target)) {
        seen.add(entry.target);
        const el       = entry.target;
        const target   = parseFloat(el.dataset.target);
        const decimals = parseInt(el.dataset.decimals) || 0;
        const suffix   = el.dataset.suffix || '';
        const duration = 1600;
        const start    = performance.now();

        // animate bar
        const card = el.closest('.stat');
        if (card) {
          const fill = card.querySelector('.stat__fill');
          if (fill) setTimeout(() => fill.classList.add('animated'), 150);
        }

        function easeOut(t) { return 1 - Math.pow(1 - t, 3); }
        function tick(now) {
          const p = Math.min((now - start) / duration, 1);
          const v = target * easeOut(p);
          el.textContent = v.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suffix;
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      }
    });
  }, { threshold: 0.3 });

  counters.forEach(c => observer.observe(c));
})();

/* ── CARD STAGGER ── */
(function initStagger() {
  const items = document.querySelectorAll('.feat, .stack-card, .stat');
  items.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(14px)';
  });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const siblings = Array.from(entry.target.parentElement.children);
        const idx = siblings.indexOf(entry.target);
        setTimeout(() => {
          entry.target.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, idx * 60);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  items.forEach(el => observer.observe(el));
})();

/* ── TERMINAL SIMULATION ── */
(function initTerminal() {
  const output   = document.getElementById('terminalOutput');
  const inputEl  = document.getElementById('terminalInput');
  const runBtn   = document.getElementById('runBtn');
  const clearBtn = document.getElementById('clearBtn');
  const body     = document.getElementById('terminalBody');
  let running    = false;

  const LOGS = [
    { t: 0,    c: 'head', s: '--- ASOS Cleanup Simulation ---' },
    { t: 60,   c: 'cmd',  s: '$ asos run --path /data --mode full' },
    { t: 200,  c: 'blank',s: '.' },
    { t: 300,  c: 'head', s: '[PHASE 1] Scanning filesystem...' },
    { t: 460,  c: 'info', s: '  -> traversing /data/documents ...' },
    { t: 600,  c: 'info', s: '  -> traversing /data/media ...' },
    { t: 740,  c: 'info', s: '  -> traversing /data/cache ...' },
    { t: 880,  c: 'ok',   s: '  [OK] 128,450 files indexed in 1.24s' },
    { t: 980,  c: 'blank',s: '.' },
    { t: 1060, c: 'head', s: '[PHASE 2] Building metadata graph...' },
    { t: 1220, c: 'info', s: '  -> extracting timestamps, sizes, MIME types' },
    { t: 1380, c: 'info', s: '  -> resolving symlinks and hardlinks' },
    { t: 1540, c: 'ok',   s: '  [OK] metadata graph built -- 128,450 nodes' },
    { t: 1640, c: 'blank',s: '.' },
    { t: 1740, c: 'head', s: '[PHASE 3] Computing SHA-256 hashes...' },
    { t: 1900, c: 'info', s: '  -> hashing in parallel (8 workers)' },
    { t: 2100, c: 'info', s: '  -> 45,230 unique hashes found' },
    { t: 2260, c: 'warn', s: '  [WARN] 34,217 duplicate hash clusters detected' },
    { t: 2400, c: 'ok',   s: '  [OK] hashing complete in 3.78s' },
    { t: 2500, c: 'blank',s: '.' },
    { t: 2600, c: 'head', s: '[PHASE 4] AI classification...' },
    { t: 2760, c: 'data', s: '  -> model: asos-classifier-v3' },
    { t: 2920, c: 'data', s: '  -> critical   : 42,018 files' },
    { t: 3060, c: 'data', s: '  -> archive    : 31,445 files' },
    { t: 3200, c: 'warn', s: '  -> redundant  : 34,217 files' },
    { t: 3340, c: 'err',  s: '  -> junk/temp  : 20,770 files' },
    { t: 3460, c: 'ok',   s: '  [OK] classification complete in 2.11s' },
    { t: 3560, c: 'blank',s: '.' },
    { t: 3660, c: 'head', s: '[PHASE 5] Deduplication...' },
    { t: 3820, c: 'info', s: '  -> replacing duplicates with references' },
    { t: 3980, c: 'ok',   s: '  [OK] 22.4 GB freed via deduplication' },
    { t: 4080, c: 'blank',s: '.' },
    { t: 4180, c: 'head', s: '[PHASE 6] Garbage collection...' },
    { t: 4340, c: 'info', s: '  -> staging junk files in /quarantine' },
    { t: 4500, c: 'info', s: '  -> dry-run passed -- proceeding' },
    { t: 4680, c: 'warn', s: '  -> deleting 20,770 temp/junk files...' },
    { t: 4880, c: 'ok',   s: '  [OK] 24.9 GB freed via garbage collection' },
    { t: 4980, c: 'blank',s: '.' },
    { t: 5080, c: 'head', s: '[PHASE 7] Generating report...' },
    { t: 5240, c: 'data', s: '  -> writing /data/asos-report.json' },
    { t: 5380, c: 'ok',   s: '  [OK] report saved' },
    { t: 5480, c: 'blank',s: '.' },
    { t: 5580, c: 'head', s: '--- RESULTS ---' },
    { t: 5720, c: 'data', s: '  Files scanned    : 128,450' },
    { t: 5840, c: 'data', s: '  Duplicates found : 34,217' },
    { t: 5960, c: 'ok',   s: '  Storage freed    : 47.3 GB' },
    { t: 6080, c: 'ok',   s: '  Efficiency gain  : 73%' },
    { t: 6200, c: 'data', s: '  Total time       : 8.42s' },
    { t: 6320, c: 'blank',s: '.' },
    { t: 6420, c: 'ok',   s: 'Optimization complete. Storage healthy.' },
  ];

  const clsMap = { head:'t-head', cmd:'t-cmd', info:'t-info', ok:'t-ok',
                   warn:'t-warn', err:'t-err', data:'t-data', blank:'t-blank' };

  function addLine(text, cls) {
    const span = document.createElement('span');
    span.className = `t-line ${clsMap[cls] || ''}`;
    span.textContent = text === '.' ? '\u00a0' : text;
    output.appendChild(span);
    body.scrollTop = body.scrollHeight;
  }

  function run() {
    if (running) return;
    running = true;
    runBtn.disabled = true;
    runBtn.textContent = '[ Running... ]';

    LOGS.forEach(({ t, c, s }) => setTimeout(() => addLine(s, c), t));

    const total = LOGS[LOGS.length - 1].t + 300;
    setTimeout(() => {
      running = false;
      runBtn.disabled = false;
      runBtn.textContent = '[ Run Again ]';
    }, total);
  }

  function clear() {
    output.innerHTML = '';
    running = false;
    runBtn.disabled = false;
    runBtn.textContent = '[ Run Cleanup Simulation ]';
  }

  runBtn.addEventListener('click', run);
  clearBtn.addEventListener('click', clear);

  inputEl.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const cmd = inputEl.value.trim().toLowerCase();
    inputEl.value = '';
    addLine('asos@system:~$ ' + cmd, 'cmd');
    if (['run cleanup', 'run', 'asos run'].includes(cmd)) { run(); }
    else if (['clear', 'cls'].includes(cmd)) { clear(); }
    else if (cmd === 'help') {
      addLine('  run cleanup  -- start simulation', 'info');
      addLine('  clear        -- clear terminal', 'info');
      addLine('  help         -- this message', 'info');
    } else if (cmd !== '') {
      addLine('  command not found: ' + cmd, 'err');
    }
  });

  document.getElementById('terminal').addEventListener('click', () => inputEl.focus());
})();

/* ── SMOOTH SCROLL ── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth' }); }
  });
});