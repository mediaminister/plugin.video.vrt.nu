'use strict';

// Ported from tokenresolver.py :: _generate_playerinfo()
// Scrapes VRT's player JS to extract a signing key, then builds a signed JWT.

const fetch = require('node-fetch');
const crypto = require('crypto');
const cache = require('./cache');

const PLAYER_BASE_URL = 'https://player.vrt.be/vrtmax/js/player-lib.js';
const CACHE_KEY = 'playerinfo_jwt';
const TTL_MS = 55 * 60 * 1000; // 55 minutes (token expires in 1 hour)

function base64UrlEncode(obj) {
    return Buffer.from(JSON.stringify(obj))
        .toString('base64')
        .replace(/=/g, '')
        .replace(/\+/g, '-')
        .replace(/\//g, '_');
}

async function fetchText(url) {
    const res = await fetch(url, {
        headers: { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0' },
    });
    if (!res.ok) throw new Error(`Failed to fetch ${url}: ${res.status}`);
    return res.text();
}

async function generatePlayerInfo() {
    const cached = cache.get(CACHE_KEY);
    if (cached) return cached;

    const folder = PLAYER_BASE_URL.split('/').slice(0, -1).join('/');
    const mainScript = await fetchText(PLAYER_BASE_URL);

    // Find first-level chunk paths referenced as "./path/chunk.js"
    const firstLevelRe = new RegExp('"\\./([a-z0-9\\-/]+[a-z0-9]{8}\\.js)";', 'g');
    const firstLevelPaths = [...mainScript.matchAll(firstLevelRe)].map(m => '/' + m[1]);

    const seen = new Set();
    const targetUrls = [];

    for (const path of firstLevelPaths) {
        const url = folder + path;
        if (seen.has(url)) continue;
        seen.add(url);

        if (url.includes('drm') || url.includes('bootstrapper')) {
            targetUrls.push(url);
        }

        let scriptContent;
        try {
            scriptContent = await fetchText(url);
        } catch {
            continue;
        }

        // Find second-level imports referenced as import("./chunk.js")
        const secondLevelRe = new RegExp('import\\("\\./([a-z0-9\\-]+\\.js)"\\)', 'g');
        const secondLevelPaths = [...scriptContent.matchAll(secondLevelRe)].map(m => '/' + m[1]);

        for (const subPath of secondLevelPaths) {
            const subUrl = folder + subPath;
            if (seen.has(subUrl)) continue;
            seen.add(subUrl);
            if (subUrl.includes('drm') || subUrl.includes('bootstrapper')) {
                targetUrls.push(subUrl);
            }
        }
    }

    let playerVersion = '5.2.2';
    let kid = null;
    let secret = null;

    const versionPattern = /\s"(\d\.\d\.\d-[a-zA-Z0-9\-:]*)"/;
    const atobPattern = new RegExp('atob\\("(==[A-Za-z0-9+/]*)"', 'g');

    for (const url of targetUrls) {
        let content;
        try {
            content = await fetchText(url);
        } catch {
            continue;
        }

        const versionMatch = content.match(versionPattern);
        if (versionMatch) playerVersion = versionMatch[1];

        const atobs = [...content.matchAll(atobPattern)].map(m => m[1]);
        if (atobs.length >= 2) {
            // first atob reversed → kid, last atob reversed → secret
            kid = Buffer.from(atobs[0].split('').reverse().join(''), 'base64').toString('utf8');
            secret = Buffer.from(atobs[atobs.length - 1].split('').reverse().join(''), 'base64').toString('utf8');
        }
    }

    if (!kid || !secret) {
        throw new Error('Could not extract kid/secret from VRT player scripts');
    }

    const header = { alg: 'HS256', kid };
    const payload = {
        drm: { widevine: 'L3' },
        exp: Math.round(Date.now() / 1000 + 3600),
        platform: 'desktop',
        app: { type: 'browser', name: 'Firefox', version: '137.0' },
        device: 'undefined (undefined)',
        os: { name: 'Linux', version: 'x86_64' },
        player: { name: 'VRT web player', version: playerVersion },
    };

    const headerB64 = base64UrlEncode(header);
    const payloadB64 = base64UrlEncode(payload);
    const signingInput = `${headerB64}.${payloadB64}`;
    const signature = crypto
        .createHmac('sha256', secret)
        .update(signingInput)
        .digest('base64')
        .replace(/=/g, '')
        .replace(/\+/g, '-')
        .replace(/\//g, '_');

    const jwt = `${signingInput}.${signature}`;
    cache.set(CACHE_KEY, jwt, TTL_MS);
    return jwt;
}

module.exports = { generatePlayerInfo };
