// Screenshot pages at a fixed size with Chrome's DevTools protocol (used for preview cards and icons).
// Usage: node render-shots.mjs <jobs.json>
//   jobs.json: {"width": 1200, "height": 630, "jobs": [{"url": "file:///...", "out": "/path/x.jpg", "transparent": false}]}
// .jpg/.jpeg outputs are JPEG (quality 88), anything else PNG. If the page sets window.__info,
// it is written next to the output as <out>.json. Pages can set window.__ready = false until they're laid out.
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, rmSync } from 'node:fs';
import { dirname } from 'node:path';
import { tmpdir } from 'node:os';
import { setTimeout as sleep } from 'node:timers/promises';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9334;
const spec = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const profile = `${tmpdir()}/uh-shots-profile-${process.pid}`;

const chrome = spawn(CHROME, [
  '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--hide-scrollbars',
  '--allow-file-access-from-files', `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, 'about:blank'
], { stdio: 'ignore' });

async function json(path, method = 'GET') {
  for (let i = 0; i < 50; i++) {
    try { const r = await fetch(`http://127.0.0.1:${PORT}${path}`, { method }); return await r.json(); }
    catch { await sleep(200); }
  }
  throw new Error('Chrome did not start');
}

function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0; const pending = new Map(); const listeners = [];
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { const { res, rej } = pending.get(msg.id); pending.delete(msg.id); msg.error ? rej(new Error(msg.error.message)) : res(msg.result); }
    else listeners.forEach((fn) => fn(msg));
  };
  const ready = new Promise((r) => (ws.onopen = r));
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  const once = (event) => new Promise((r) => listeners.push((m) => m.method === event && r(m.params)));
  return { ready, send, once, close: () => ws.close() };
}

const evalv = async (s, expression) => (await s.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result.value;

try {
  await json('/json/version');
  const target = await json('/json/new?about:blank', 'PUT');
  const s = connect(target.webSocketDebuggerUrl); await s.ready;
  await s.send('Page.enable'); await s.send('Runtime.enable');
  for (const job of spec.jobs) {
    const width = job.width || spec.width, height = job.height || spec.height;
    await s.send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });
    await s.send('Emulation.setDefaultBackgroundColorOverride', job.transparent ? { color: { r: 0, g: 0, b: 0, a: 0 } } : {});
    // Reset first: jobs that differ only in their #hash would otherwise be same-page jumps with no load event
    let loaded = s.once('Page.loadEventFired');
    await s.send('Page.navigate', { url: 'about:blank' }); await loaded;
    loaded = s.once('Page.loadEventFired');
    await s.send('Page.navigate', { url: job.url }); await loaded;
    await evalv(s, 'document.fonts ? document.fonts.ready.then(() => true) : true');
    for (let i = 0; i < 30 && (await evalv(s, 'window.__ready === false')); i++) await sleep(100);
    await sleep(150);
    const jpeg = /\.jpe?g$/i.test(job.out);
    const shot = await s.send('Page.captureScreenshot', {
      format: jpeg ? 'jpeg' : 'png', ...(jpeg ? { quality: 88 } : {}),
      clip: { x: 0, y: 0, width, height, scale: 1 }, captureBeyondViewport: false
    });
    mkdirSync(dirname(job.out), { recursive: true });
    writeFileSync(job.out, Buffer.from(shot.data, 'base64'));
    const info = await evalv(s, 'window.__info === undefined ? null : JSON.stringify(window.__info)');
    if (info) writeFileSync(job.out + '.json', info);
    console.log(job.out.split('/').pop());
  }
  s.close();
} finally {
  chrome.kill();
  await sleep(300);
  rmSync(profile, { recursive: true, force: true });
}
