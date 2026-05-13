'use strict';

// Ported from tokenresolver.py — VRT MAX SSO login and token management.
// Uses fetch-cookie to automatically handle Set-Cookie headers across redirects.

const nodeFetch = require('node-fetch');
const fetchCookie = require('fetch-cookie');
const { CookieJar } = require('tough-cookie');
const cache = require('./cache');
const { generatePlayerInfo } = require('./playerinfo');

const SSO_INIT_URL = 'https://www.vrt.be/vrtnu/sso/login?scope=openid,mid';
const SSO_LOGIN_URL = 'https://login.vrt.be/perform_login';
const SSO_REFRESH_URL = 'https://www.vrt.be/vrtnu/sso/refresh';
const PLAYERTOKEN_URL = 'https://media-services-public.vrt.be/vualto-video-aggregator-web/rest/external/v2/tokens';

const TOKEN_TTL_MS = 110 * 60 * 1000;   // access/video tokens: ~2 hours, cache 110 min
const PLAYERTOKEN_TTL_MS = 110 * 60 * 1000; // player tokens: 2 hours

// One shared cookie jar for the SSO session
const jar = new CookieJar();
const fetch = fetchCookie(nodeFetch, jar);

function cookieValue(name) {
    // Synchronous cookie lookup from the jar across all stored URLs
    const cookies = jar.toJSON().cookies || [];
    const cookie = cookies.find(c => c.key === name);
    return cookie ? cookie.value : null;
}

async function ssoLogin() {
    const username = process.env.VRT_USERNAME;
    const password = process.env.VRT_PASSWORD;
    if (!username || !password) {
        throw new Error('VRT_USERNAME and VRT_PASSWORD environment variables are required');
    }

    // Step 1: Init SSO — sets SESSION and OIDCXSRF cookies
    const initRes = await fetch(SSO_INIT_URL, { redirect: 'follow' });
    if (!initRes.ok) throw new Error(`SSO init failed: ${initRes.status}`);

    // Step 2: Perform login
    const oidcxsrf = cookieValue('OIDCXSRF');
    const session = cookieValue('SESSION');
    if (!oidcxsrf || !session) throw new Error('Missing OIDCXSRF or SESSION cookie after SSO init');

    const loginRes = await fetch(SSO_LOGIN_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'OIDCXSRF': oidcxsrf,
            'Cookie': `SESSION=${session}; OIDCXSRF=${oidcxsrf}`,
        },
        body: JSON.stringify({ clientId: 'vrtnu-site', loginID: username, password }),
    });

    const loginJson = await loginRes.json();
    if (loginJson.errorCode !== 0) {
        const detail = loginJson.errorDetails || loginJson.errorCode || 'Unknown error';
        throw new Error(`VRT MAX login failed: ${detail}`);
    }

    const redirectUrl = loginJson.redirectUrl;
    if (!redirectUrl) throw new Error('No redirectUrl in login response');

    // Step 3: Follow redirect to obtain profile tokens (vrtnu-site_profile_at, _vt, _rt)
    const oidcstate = cookieValue('oidcstate');
    const headers = {
        'Cookie': `SESSION=${session}; oidcstate=${oidcstate || ''}`,
    };

    const tokenRes1 = await fetch(redirectUrl, { method: 'GET', headers, redirect: 'follow' });
    if (!tokenRes1.ok) throw new Error(`Token redirect failed: ${tokenRes1.status}`);

    // The video token (vrtnu-site_profile_vt) is what we need for player token requests
    const videoToken = cookieValue('vrtnu-site_profile_vt');
    const refreshToken = cookieValue('vrtnu-site_profile_rt');

    if (!videoToken) throw new Error('Could not obtain vrtnu-site_profile_vt after login');

    cache.set('vrt_video_token', videoToken, TOKEN_TTL_MS);
    if (refreshToken) cache.set('vrt_refresh_token', refreshToken, 7 * 24 * 60 * 60 * 1000);

    return videoToken;
}

async function refreshVideoToken() {
    const refreshToken = cache.get('vrt_refresh_token');
    if (!refreshToken) return null;

    try {
        const res = await fetch(SSO_REFRESH_URL, {
            headers: { 'Cookie': `vrtnu-site_profile_rt=${refreshToken}` },
            redirect: 'follow',
        });
        if (!res.ok) return null;

        const newVideoToken = cookieValue('vrtnu-site_profile_vt');
        const newRefreshToken = cookieValue('vrtnu-site_profile_rt');

        if (newVideoToken) {
            cache.set('vrt_video_token', newVideoToken, TOKEN_TTL_MS);
            if (newRefreshToken) cache.set('vrt_refresh_token', newRefreshToken, 7 * 24 * 60 * 60 * 1000);
            return newVideoToken;
        }
    } catch {
        // fall through
    }
    return null;
}

async function getVideoToken() {
    const cached = cache.get('vrt_video_token');
    if (cached) return cached;

    const refreshed = await refreshVideoToken();
    if (refreshed) return refreshed;

    return ssoLogin();
}

async function getPlayerToken(isLive) {
    const cacheKey = isLive ? 'player_token_live' : 'player_token_ondemand';
    const cached = cache.get(cacheKey);
    if (cached) return cached;

    const playerInfo = await generatePlayerInfo();
    const body = { playerInfo };

    // Live streams without geo-lock don't need identity token, but geo-locked ones do.
    // We always include it when available so geo-locked channels work.
    const videoToken = await getVideoToken();
    if (videoToken) body.identityToken = videoToken;

    const res = await nodeFetch(PLAYERTOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Player token request failed ${res.status}: ${text}`);
    }

    const json = await res.json();
    const token = json.vrtPlayerToken;
    if (!token) throw new Error('No vrtPlayerToken in response');

    cache.set(cacheKey, token, PLAYERTOKEN_TTL_MS);
    return token;
}

module.exports = { getPlayerToken };
