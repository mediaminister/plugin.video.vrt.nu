'use strict';

require('dotenv').config();

const { addonBuilder, serveHTTP } = require('stremio-addon-sdk');
const { CHANNELS, CHANNEL_BY_ID } = require('./src/channels');
const { resolveStream } = require('./src/streams');

const manifest = {
    id: 'community.vrtmax.livetv',
    version: '1.0.0',
    name: 'VRT MAX Live TV',
    description: 'Live TV channels from VRT MAX (Belgian public broadcaster). Requires a VRT MAX account.',
    logo: 'https://images.vrt.be/orig/2023/04/28/c448d669-e5c1-11ed-91d7-02b7b76bf47f.png',
    resources: ['catalog', 'meta', 'stream'],
    types: ['tv'],
    catalogs: [
        {
            type: 'tv',
            id: 'vrtmax-live',
            name: 'VRT MAX Live',
            extra: [],
        },
    ],
    idPrefixes: ['vrtmax-'],
    behaviorHints: { configurable: false, adult: false },
};

const builder = new addonBuilder(manifest);

// Catalog: list all channels as meta items
builder.defineCatalogHandler(({ type, id }) => {
    if (type !== 'tv' || id !== 'vrtmax-live') {
        return Promise.resolve({ metas: [] });
    }

    const metas = CHANNELS.map(ch => ({
        id: `vrtmax-${ch.id}`,
        type: 'tv',
        name: ch.name,
        poster: ch.logo,
        logo: ch.logo,
        background: ch.logo,
        posterShape: 'square',
        description: ch.geoLocked ? 'VRT MAX Live (Belgium only)' : 'VRT MAX Live',
    }));

    return Promise.resolve({ metas });
});

// Meta: single channel detail
builder.defineMetaHandler(({ type, id }) => {
    if (type !== 'tv' || !id.startsWith('vrtmax-')) {
        return Promise.resolve({ meta: null });
    }

    const channelId = id.replace('vrtmax-', '');
    const ch = CHANNEL_BY_ID[channelId];
    if (!ch) return Promise.resolve({ meta: null });

    return Promise.resolve({
        meta: {
            id,
            type: 'tv',
            name: ch.name,
            poster: ch.logo,
            logo: ch.logo,
            background: ch.logo,
            posterShape: 'square',
            description: ch.geoLocked ? 'VRT MAX Live (Belgium only)' : 'VRT MAX Live',
        },
    });
});

// Stream: resolve live stream URL for a channel
builder.defineStreamHandler(async ({ type, id }) => {
    if (type !== 'tv' || !id.startsWith('vrtmax-')) {
        return { streams: [] };
    }

    const channelId = id.replace('vrtmax-', '');
    const ch = CHANNEL_BY_ID[channelId];
    if (!ch) return { streams: [] };

    try {
        const stream = await resolveStream(ch.liveStreamId);
        return { streams: [stream] };
    } catch (err) {
        console.error(`[vrtmax] Stream error for ${ch.name}:`, err.message);
        return { streams: [] };
    }
});

const port = parseInt(process.env.PORT || '7000', 10);
serveHTTP(builder.getInterface(), { port });
console.log(`VRT MAX Live TV addon running on http://localhost:${port}`);
console.log(`Add to Stremio: http://localhost:${port}/manifest.json`);
