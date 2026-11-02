const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 430, height: 932 }, deviceScaleFactor: 2 });
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.waitForTimeout(2000);
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 500) { await p.evaluate(y => window.scrollTo(0, y), y); await p.waitForTimeout(60); }
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(1500);
  // hide fixed header/fab for section shots
  const ids = ['inicio','especialidades','promos','crea','carta','nosotros'];
  const r = await p.evaluate(ids => ids.map(id => { const e=document.getElementById(id).getBoundingClientRect(); return [id, e.top+scrollY, e.height]; }), ids);
  console.log(JSON.stringify(r));
  await p.addStyleTag({content:'header,.fab,.toast{display:none!important}'});
  for (const [id, top, h] of r) {
    const hh = Math.min(h, id==='carta'? 2600 : h);
    await p.screenshot({ path: `cap/sec-${id}.png`, clip: { x: 0, y: top, width: 430, height: hh }, fullPage: true });
  }
  await b.close();
})();
