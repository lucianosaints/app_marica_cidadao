const CACHE_NAME = 'marica-cidadao-v1';
const urlsToCache = [
  '/',
  '/logo/Logo-prefeitura.png',
  '/logo/Logo-Ictim.png',
  '/logo/fundo.png',
  '/logo/pwa_icon_512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
