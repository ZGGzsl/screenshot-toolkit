#!/usr/bin/env node
/**
 * Smart Browser Screenshot via CDP (Chrome DevTools Protocol)
 *
 * Unlike simple Playwright screenshot(), this script:
 *   1. Opens a URL and optionally waits for a specific element to appear
 *   2. Supports multiple viewport sizes and device emulation
 *   3. Captures the full page or just the viewport
 *   4. Saves base64 PNG or writes to file directly
 *
 * Usage:
 *   node smart_capture.js <url> [output.png]
 *   node smart_capture.js <url> out.png --wait "#article-content"  # wait for element
 *   node smart_capture.js <url> out.png --wait-selector ".main"    # CSS selector
 *   node smart_capture.js <url> out.png --wait-time 3000           # wait ms
 *   node smart_capture.js <url> out.png --full-page
 *   node smart_capture.js <url> out.png --viewport=1920,1080
 *   node smart_capture.js <url> out.png --clip=0,0,800,600          # viewport clip
 *   node smart_capture.js <url> out.png --emulate="iPhone 12"      # device name
 */

const { chromium } = require('playwright');

const args = process.argv.slice(2);

// Parse named args manually (no external lib needed)
function getArg(flags) {
    for (const flag of flags) {
        const idx = args.indexOf(flag);
        if (idx !== -1) return args[idx + 1];
    }
    return null;
}
function hasArg(flags) {
    return flags.some(f => args.includes(f));
}

const url          = args.find(a => !a.startsWith('--') && !a.startsWith('-'));
const outputFile   = args.find((a, i) => {
    const prev = args[i - 1];
    return !a.startsWith('--') && !a.startsWith('-') && i > 0 && prev && !prev.startsWith('--');
}) || 'smart_capture.png';

const waitSelector = getArg(['--wait', '-s', '--wait-selector']) || null;
const waitMs       = parseInt(getArg(['--wait-time', '--wait']) || '0');
const fullPage     = hasArg(['--full-page', '-f']);
const viewportStr  = getArg(['--viewport', '-v']) || null;
const clipStr      = getArg(['--clip', '-c']) || null;
const deviceName   = getArg(['--emulate', '-d']) || null;

if (!url) {
    console.error('Usage: node smart_capture.js <url> [output.png] [--wait-selector CSS] [--wait-time MS] [--full-page] [--viewport=W,H] [--clip=X,Y,W,H] [--emulate="Device Name"]');
    process.exit(1);
}

// Parse viewport
let viewport = { width: 1280, height: 720 };
if (viewportStr) {
    const [w, h] = viewportStr.split(',').map(Number);
    viewport = { width: w || 1280, height: h || 720 };
}

// Parse clip
let clip = null;
if (clipStr) {
    const [x, y, w, h] = clipStr.split(',').map(Number);
    clip = { x: x || 0, y: y || 0, width: w || viewport.width, height: h || viewport.height };
}

// Load device emulators
const devices = {
    'iPhone 12':       { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1', viewport: { width: 390, height: 844 }, deviceScaleFactor: 3 },
    'iPhone 12 Pro':   { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1', viewport: { width: 390, height: 844 }, deviceScaleFactor: 3 },
    'Pixel 5':         { userAgent: 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36', viewport: { width: 393, height: 851 }, deviceScaleFactor: 2.75 },
    'iPad Pro 11':     { userAgent: 'Mozilla/5.0 (iPad; CPU OS 13_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.4 Mobile/15E148 Safari/604.1', viewport: { width: 1024, height: 1366 }, deviceScaleFactor: 2 },
};

const deviceOverride = deviceName ? devices[deviceName] : null;

async function main() {
    const browser = await chromium.launch({ headless: true });

    // Connect to CDP directly for more control
    const context = await browser.newContext({
        viewport: deviceOverride ? deviceOverride.viewport : viewport,
        userAgent: deviceOverride ? deviceOverride.userAgent : undefined,
        deviceScaleFactor: deviceOverride ? deviceOverride.deviceScaleFactor : undefined,
    });

    const page = await context.newPage();

    // ── Navigate ──────────────────────────────────────────────────────────────
    await page.goto(url, { waitUntil: 'domcontentloaded' });

    // ── Smart wait ────────────────────────────────────────────────────────────
    if (waitSelector) {
        try {
            await page.waitForSelector(waitSelector, { timeout: 15000 });
        } catch {
            console.warn(`WARN: Selector "${waitSelector}" not found within 15s — capturing anyway`);
        }
    }

    if (waitMs > 0) {
        await page.waitForTimeout(waitMs);
    }

    // ── Capture ────────────────────────────────────────────────────────────────
    const screenshotOptions = {
        path: outputFile,
        fullPage,
    };
    if (clip) screenshotOptions.clip = clip;

    await page.screenshot(screenshotOptions);

    await browser.close();

    const resolved = require('path').resolve(outputFile);
    console.log(`OK:${resolved}`);

    // Also output metadata for AI agent consumption
    const fs = require('fs');
    const meta = {
        file: resolved,
        url,
        viewport: deviceOverride ? deviceOverride.viewport : viewport,
        fullPage,
        waitSelector: waitSelector || null,
        waitMs,
    };
    console.log(`META:${JSON.stringify(meta)}`);
}

main().catch(err => {
    console.error('ERROR:', err.message);
    process.exit(1);
});