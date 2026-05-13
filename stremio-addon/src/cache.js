'use strict';

class Cache {
    constructor() {
        this._store = new Map();
    }

    set(key, value, ttlMs) {
        this._store.set(key, { value, expiresAt: Date.now() + ttlMs });
    }

    get(key) {
        const entry = this._store.get(key);
        if (!entry) return null;
        if (Date.now() > entry.expiresAt) {
            this._store.delete(key);
            return null;
        }
        return entry.value;
    }

    delete(key) {
        this._store.delete(key);
    }
}

module.exports = new Cache();
