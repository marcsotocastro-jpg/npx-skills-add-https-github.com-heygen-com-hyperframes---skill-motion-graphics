const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 430, height: 932 }, deviceScaleFactor: 2 });
  const errs=[]; p.on('pageerror', e => errs.push(e.message)); p.on('requestfailed', r => errs.push('fail '+r.url()));
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.waitForTimeout(2500);
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 400) { await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(120); }
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(1500);
  await p.screenshot({ path: 'cap/top.png' });
  await p.screenshot({ path: 'cap/full.png', fullPage: true });
  console.log(H, errs.slice(0,5));
  const fonts = await p.evaluate(() => [...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+f.weight));
  console.log(fonts);
  await b.close();
})();
