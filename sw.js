const CACHE_NAME = 'gemini-watermark-remover-v2';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './about.html',
  './contact.html',
  './disclaimer.html',
  './privacy-policy.html',
  './terms-of-service.html',
  './style.css',
  './main.js',
  './assets/gemini-watermark-remover-logo.webp',
  './assets/gemini-watermark-remover-before.webp',
  './assets/gemini-watermark-remover-after.webp',
  './assets/gemini-watermark-remover-preview-left.webp',
  './assets/veo-video-watermark-cleaner-preview-right.webp',
  './assets/site.webmanifest',
  './assets/favicon.ico',
  './assets/favicon-96x96.png',
  './assets/favicon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch((err) => {
        console.warn('Some assets could not be cached:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Network-First with Cache Fallback for dynamic development & fresh assets
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = event.request.url;

  // Skip ad requests, analytics, and external tracking
  if (
    url.includes('pagead2') ||
    url.includes('googletagmanager') ||
    url.includes('google-analytics') ||
    url.includes('buymeacoffee') ||
    url.includes('iconify')
  ) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => caches.match(event.request))
  );
});
