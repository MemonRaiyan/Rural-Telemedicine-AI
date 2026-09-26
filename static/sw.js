/**
 * GramCare AI — Service Worker (PWA)
 * Caches app shell, locales, and static assets for offline/low-bandwidth use.
 * Cache-first for shell, network-first for API calls.
 */

const CACHE_NAME = 'gramcare-v1.2';
const SHELL_ASSETS = [
  '/',
  '/static/index.html',
  '/static/style.css',
  '/static/app.js',
  '/static/templates.js',
  '/static/locales/en.json',
  '/static/locales/hi.json',
  '/static/locales/gu.json',
  '/static/manifest.json',
];

// External CDN resources cached on first fetch
const PRECACHE_EXTERNAL = [
  'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap',
];

// ---- Install: pre-cache shell ----
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Shell assets – cache all, ignore failures for external
      return cache.addAll(SHELL_ASSETS).catch((err) => {
        console.warn('[SW] Some shell assets failed to cache:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// ---- Activate: clean old caches ----
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ---- Fetch Strategy ----
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // API calls: Network-first, no cache
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/ws/')) {
    event.respondWith(fetch(event.request).catch(() =>
      new Response(JSON.stringify({ error: 'You are offline. Please reconnect.' }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      })
    ));
    return;
  }

  // Locale files: Network-first with cache fallback
  if (url.pathname.startsWith('/static/locales/')) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // CDN fonts: Cache-first (they rarely change)
  if (url.hostname.includes('googleapis.com') || url.hostname.includes('gstatic.com') || url.hostname.includes('cloudflare.com')) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached;
        return fetch(event.request).then((res) => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(event.request, clone));
          return res;
        }).catch(() => cached || new Response('', { status: 408 }));
      })
    );
    return;
  }

  // App shell & static files: Cache-first, network fallback
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((res) => {
        // Only cache successful same-origin responses
        if (res.ok && url.origin === self.location.origin) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put(event.request, clone));
        }
        return res;
      }).catch(() => {
        // Offline fallback: return cached root for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/') || caches.match('/static/index.html');
        }
      });
    })
  );
});

// ---- Background Sync (future: queue offline appointments) ----
self.addEventListener('sync', (event) => {
  if (event.tag === 'gramcare-sync') {
    console.log('[SW] Background sync triggered');
  }
});

// ---- Push Notifications (future) ----
self.addEventListener('push', (event) => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'GramCare AI', {
      body: data.body || 'You have a new notification.',
      icon: '/static/icon-192.png',
      badge: '/static/icon-192.png',
      vibrate: [200, 100, 200],
    })
  );
});
