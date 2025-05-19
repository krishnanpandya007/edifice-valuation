// const CACHE_NAME = "offline-form-cache-v1";
// const urlsToCache = [
//     "/register/site/",  // Form page URL
//     // "/static/offline-form.js",  // JavaScript file for local storage
//     // "/static/style.css",  // CSS file (if any)
// ];

// // Install Service Worker and cache assets
// self.addEventListener("install", (event) => {
//     event.waitUntil(
//         caches.open(CACHE_NAME).then((cache) => {
//             return cache.addAll(urlsToCache);
//         })
//     );
// });

// // Intercept fetch requests and serve from cache if offline
// self.addEventListener("fetch", (event) => {
//     event.respondWith(
//         fetch(event.request).catch(() => caches.match(event.request))
//     );
// });
// Base Service Worker implementation.  To use your own Service Worker, set the PWA_SERVICE_WORKER_PATH variable in settings.py

var staticCacheName = "django-pwa-v" + new Date().getTime();

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(staticCacheName).then(function(cache) {
      return cache.addAll([
        '',
      ]);
    })
  );
});

self.addEventListener('fetch', function(event) {
  var requestUrl = new URL(event.request.url);
    if (requestUrl.origin === location.origin) {
      if ((requestUrl.pathname === '/')) {
        event.respondWith(caches.match(''));
        return;
      }
    }
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
});