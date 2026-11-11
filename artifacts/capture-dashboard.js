const { chromium } = require('playwright');

async function capture(viewport, outputPath) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport });
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'networkidle' });
  await page.fill('#ga-weeks', '28');
  await page.fill('#ga-days', '0');
  await page.fill('#birth-weight', '980');
  await page.selectOption('#sex', 'male');
  await page.fill('#fio2', '0.30');
  await page.selectOption('#breathing-support', 'room_air');
  await page.selectOption('#monitoring-on', 'true');
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/runs\/.+\/$/, { timeout: 15000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: outputPath, fullPage: false });
  await browser.close();
}

(async () => {
  await capture({ width: 1280, height: 720 }, 'artifacts/dashboard-1280x720.png');
  await capture({ width: 1920, height: 1080 }, 'artifacts/dashboard-1920x1080.png');
})();
