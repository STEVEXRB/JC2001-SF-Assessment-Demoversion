// shots.js - capture the interface states used as figures in the technical report.
// Reuses the locally installed Edge (no browser download).
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const BASE = process.env.BASE || 'http://127.0.0.1:5173';
const OUT = process.env.OUT || path.join(__dirname, 'figures');
fs.mkdirSync(OUT, { recursive: true });

// 1240 px keeps the two-column detail layout (>1040) and the header in its
// full form, so one capture set serves both the overviews and the crops.
const DESKTOP = { width: 1240, height: 900 };
const PHONE = { width: 400, height: 860, deviceScaleFactor: 2, isMobile: true, hasTouch: true };


// Opening a listing has to force a hash change: logging in calls showView('home'),
// so navigating to the hash we are already on would not fire a hashchange event
// and the detail view would never render.
async function openItem(page, id) {
  await page.evaluate(() => { window.location.hash = '#home'; });
  await page.waitForTimeout(250);
  await page.evaluate(i => { window.location.hash = '#item-' + i; }, id);
  await page.waitForSelector('#detail-content .buy-card, #detail-content .gallery', { timeout: 15000 });
  await page.waitForTimeout(500);
}

async function login(page, user = 'demo_li', pass = '123456') {
  await page.click('#login-btn');
  await page.waitForSelector('#login-form');
  await page.fill('#login-username', user);
  await page.fill('#login-password', pass);
  await Promise.all([
    page.waitForResponse(r => r.url().includes('/api/login')),
    page.click('#login-form button[type="submit"]'),
  ]);
  await page.waitForTimeout(700);
}

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const errors = [];
  const bad = [];

  const ctx = await browser.newContext({ viewport: DESKTOP, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('response', r => { if (r.status() >= 400 && r.status() !== 401) bad.push(r.status() + ' ' + r.url()); });

  const shot = async (name, opts = {}) => {
    await page.waitForTimeout(opts.wait || 650);
    // The viewport capture is taken first and from the top of the page: a
    // full-page capture leaves the page scrolled, which would make the viewport
    // twin show the wrong region.
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(150);
    await page.screenshot({ path: path.join(OUT, name + '_vp.png'), fullPage: false });
    if (opts.full !== false) {
      await page.screenshot({ path: path.join(OUT, name + '.png'), fullPage: true });
    }
    console.log('shot ' + name);
  };

  // 1. home page, anonymous
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await shot('ui_home');

  // 2. keyword search
  await page.fill('#search-input', 'laptop');
  await page.click('#search-btn');
  await shot('ui_search');

  // 3. empty search result
  await page.fill('#search-input', 'zzzzz');
  await page.click('#search-btn');
  await shot('ui_empty');

  // 4. auth view
  await page.fill('#search-input', '');
  await page.click('#home-btn');
  await page.click('#login-btn');
  await shot('ui_auth');

  // 5. detail page, anonymous visitor
  await openItem(page, 3);
  await shot('ui_detail_guest');

  // 6. signed in as a buyer, viewing someone else's listing
  await login(page, 'demo_li');
  await openItem(page, 2);
  await shot('ui_detail_buyer');

  // 7. own listing, seller view with the management actions
  await openItem(page, 4);
  await shot('ui_detail_seller');

  // 8. chat panel - open an existing thread from the conversation list, so the
  //    figure shows real bubbles rather than an empty thread
  await page.evaluate(() => { window.location.hash = '#home'; });
  await page.waitForTimeout(300);
  await page.click('#user-menu-btn');
  await page.waitForSelector('#user-menu-panel:not(.hidden)');
  await page.click('#menu-messages-btn');
  await page.waitForSelector('#profile-view:not(.hidden)');
  await page.waitForSelector('.conv', { timeout: 15000 });
  await page.click('.conv');
  await page.waitForTimeout(1000);
  await shot('ui_chat', { full: false });

  // 9. publish form, half filled so the live preview shows something
  await page.keyboard.press('Escape');
  await page.click('#publish-btn');
  await page.waitForSelector('#publish-view:not(.hidden)');
  await page.fill('#item-title', 'Desktop monitor stand, aluminium');
  await page.fill('#item-desc', 'Used for one semester, no scratches. Height adjustable, fits a 27-inch screen.');
  await page.fill('#item-price', '45');
  await page.click('#item-category-chips .chip[data-value="digital"]');
  await shot('ui_publish');

  // 10. personal centre, listings tab (reached through the avatar menu)
  await page.click('#user-menu-btn');
  await page.waitForSelector('#user-menu-panel:not(.hidden)');
  await page.click('#profile-btn');
  await page.waitForSelector('#profile-view:not(.hidden)');
  await shot('ui_profile_items');

  // 11. favourites tab
  await page.click('#tab-my-favorites');
  await shot('ui_profile_favourites');

  // 12. messages tab
  await page.click('#tab-messages');
  await shot('ui_profile_messages');

  // 13. the confirmation dialog that guards a destructive action
  await openItem(page, 4);
  await page.waitForSelector('#off-shelf-btn');
  await page.click('#off-shelf-btn');
  await page.waitForTimeout(500);
  await shot('ui_confirm', { full: false });
  await page.click('#confirm-cancel');

  // 14. a toast confirmation
  await openItem(page, 2);
  await page.waitForSelector('#favorite-btn');
  await page.click('#favorite-btn');
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(OUT, 'ui_toast.png') });
  console.log('shot ui_toast');

  await ctx.close();

  // 15-16. phone layout
  const mctx = await browser.newContext({ viewport: PHONE });
  const mpage = await mctx.newPage();
  mpage.on('pageerror', e => errors.push('mobile pageerror: ' + e.message));
  await mpage.goto(BASE + '/', { waitUntil: 'networkidle' });
  await mpage.waitForTimeout(800);
  await mpage.screenshot({ path: path.join(OUT, 'ui_mobile_home.png'), fullPage: false });
  console.log('shot ui_mobile_home');
  await openItem(mpage, 3);
  await mpage.waitForTimeout(400);
  await mpage.screenshot({ path: path.join(OUT, 'ui_mobile_detail.png'), fullPage: false });
  console.log('shot ui_mobile_detail');
  await mctx.close();

  await browser.close();
  console.log('\nconsole errors: ' + errors.length);
  errors.slice(0, 12).forEach(e => console.log('  ' + e));
  console.log('unexpected 4xx/5xx: ' + bad.length);
  bad.slice(0, 12).forEach(b => console.log('  ' + b));
})();
