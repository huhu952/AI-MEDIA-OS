const { chromium } = require("playwright");

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto("data:text/html,<html><body><h1 id='t'>Playwright OK</h1></body></html>");
    const text = await page.textContent("#t");
    console.log("BROWSER TEST RESULT:", text);
    await browser.close();
    if (text !== "Playwright OK") process.exit(1);
})().catch((e) => {
    console.error("BROWSER TEST FAIL:", e.message);
    process.exit(1);
});
