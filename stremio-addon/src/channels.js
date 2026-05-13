'use strict';

// TV channels with live streams, ported from resources/lib/data.py
const CHANNELS = [
    {
        id: 'vrt1',
        name: 'VRT 1',
        liveStreamId: 'vualto_een_geo',
        logo: 'https://images.vrt.be/orig/2023/04/28/c448d669-e5c1-11ed-91d7-02b7b76bf47f.png',
        geoLocked: true,
    },
    {
        id: 'vrt-canvas',
        name: 'Canvas',
        liveStreamId: 'vualto_canvas_geo',
        logo: 'https://images.vrt.be/orig/logo/canvas/CANVAS_logo_lichtblauw.jpg',
        geoLocked: true,
    },
    {
        id: 'ketnet',
        name: 'Ketnet',
        liveStreamId: 'vualto_ketnet_geo',
        logo: 'https://images.vrt.be/orig/logo/ketnet/ketnet_LOGO_rood_geel.png',
        geoLocked: true,
    },
    {
        id: 'ketnet-jr',
        name: 'Ketnet Junior',
        liveStreamId: 'ketnet_jr',
        logo: 'https://images.vrt.be/orig/2019/07/19/c309360a-aa10-11e9-abcc-02b7b76bf47f.png',
        geoLocked: false,
    },
    {
        id: 'sporza',
        name: 'Sporza',
        liveStreamId: 'vualto_sporza_geo',
        logo: 'https://images.vrt.be/orig/logo/sporza/sporza_logo_zwart.png',
        geoLocked: true,
    },
    {
        id: 'vrtnws',
        name: 'VRT NWS',
        liveStreamId: 'vualto_nieuws',
        logo: 'https://images.vrt.be/orig/logos/vrtnws.png',
        geoLocked: false,
    },
    {
        id: 'vrt-events1',
        name: 'VRT Events 1',
        liveStreamId: 'vualto_events1_geo',
        logo: 'https://images.vrt.be/orig/logo/vrt.png',
        geoLocked: true,
    },
    {
        id: 'vrt-events2',
        name: 'VRT Events 2',
        liveStreamId: 'vualto_events2_geo',
        logo: 'https://images.vrt.be/orig/logo/vrt.png',
        geoLocked: true,
    },
    {
        id: 'vrt-events3',
        name: 'VRT Events 3',
        liveStreamId: 'vualto_events3_geo',
        logo: 'https://images.vrt.be/orig/logo/vrt.png',
        geoLocked: true,
    },
];

const CHANNEL_BY_ID = Object.fromEntries(CHANNELS.map(c => [c.id, c]));
const CHANNEL_BY_STREAM_ID = Object.fromEntries(CHANNELS.map(c => [c.liveStreamId, c]));

module.exports = { CHANNELS, CHANNEL_BY_ID, CHANNEL_BY_STREAM_ID };
