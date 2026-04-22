/**
 * Browser screenshot via Playwright — for AI agents.
 *
 * Usage:
 *   node browser_screenshot.js <url> [output.png]
 *   node browser_screenshot.js https://example.com webpage.png --full-page
 */

const { chromium } = require('playwright');

async function main() {
    const args = process.argv.slice(2);
    const url = args[0];
    const output = args[1] || 'webpage.png';
    const fullPage = args.includes('--full-page');
    const width = parseInt(args.find(a => a.startsWith('--width='))?.split('=')[1] || '1280');
    const height = parseInt(args.find(a => a.startsWith('--height='))?.split('=')[1] || '720');

    if (!url) {
        console.error('Usage: node browser_screenshot.js <url> [output.png] [--full-page] [--width=1280] [--height=720]');
        process.exit(1);
    }

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({
        viewport: { width, height }
    });

    await page.goto(url, { waitUntil: 'networkidle' });
    await page.screenshot({
        path: output,
        fullPage,
    });

    await browser.close();
    console.log(`OK:${require('path').resolve(output)}`);
}

main().catch(err => {
    console.error('ERROR:', err.message);
    process.exit(1);
});
