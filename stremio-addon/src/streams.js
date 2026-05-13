'use strict';

// Ported from streamservice.py — resolves a VRT MAX live stream URL given a liveStreamId.

const fetch = require('node-fetch');
const { getPlayerToken } = require('./auth');

const MEDIA_API_URL = 'https://media-services-public.vrt.be/media-aggregator/v2';
const CLIENT = 'vrtnu-web@PROD';
const WIDEVINE_LICENSE_URL = 'https://widevine-proxy.drm.technology/proxy';
const GEOBLOCK_CODES = new Set([
    'INVALID_LOCATION',
    'INCOMPLETE_ROAMING_CONFIG',
    'CONTENT_AVAILABLE_ONLY_IN_BE',
    'CONTENT_AVAILABLE_ONLY_FOR_BE_RESIDENTS',
]);

async function resolveStream(liveStreamId) {
    const playerToken = await getPlayerToken(true);

    const apiUrl = `${MEDIA_API_URL}/media-items/${liveStreamId}?vrtPlayerToken=${encodeURIComponent(playerToken)}&client=${encodeURIComponent(CLIENT)}`;
    const res = await fetch(apiUrl, {
        headers: { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0' },
    });

    if (!res.ok) {
        throw new Error(`Media API error ${res.status} for ${liveStreamId}`);
    }

    const json = await res.json();

    if (!json.targetUrls) {
        const code = json.code || 'UNKNOWN';
        if (GEOBLOCK_CODES.has(code)) {
            throw new Error(`Geo-blocked (${code}): stream ${liveStreamId} is only available in Belgium`);
        }
        throw new Error(`No targetUrls in response for ${liveStreamId}: ${code}`);
    }

    const vudrm = json.drm || null;

    // Protocol preference: mpeg_dash (with or without DRM), then hls_aes, then hls
    const protocolPriority = ['mpeg_dash', 'hls_aes', 'hls'];
    let chosen = null;
    for (const proto of protocolPriority) {
        chosen = json.targetUrls.find(t => t.type === proto);
        if (chosen) break;
    }

    if (!chosen) {
        throw new Error(`No usable stream protocol found for ${liveStreamId}`);
    }

    let manifestUrl = chosen.url;
    const protocol = chosen.type;

    // For HLS streams, append ?hd to prefer 720p quality (mirrors Kodi plugin behaviour)
    if (protocol === 'hls' || protocol === 'hls_aes') {
        manifestUrl = manifestUrl.includes('?')
            ? manifestUrl.replace('.m3u8?', '.m3u8?hd&')
            : manifestUrl + '?hd';
    }

    const stream = {
        url: manifestUrl,
        name: 'VRT MAX',
        description: 'Live',
        behaviorHints: { notWebReady: true },
    };

    // Attach Widevine DRM info — ExoPlayer on Android reads these
    if (vudrm && protocol === 'mpeg_dash') {
        stream.behaviorHints.drm = {
            widevine: {
                headers: { 'X-VUDRM-TOKEN': vudrm },
                licenseUrl: WIDEVINE_LICENSE_URL,
            },
        };
    }

    return stream;
}

module.exports = { resolveStream };
