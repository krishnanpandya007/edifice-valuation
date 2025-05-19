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

// var staticCacheName = "django-pwa-v" + new Date().getTime();

const staticCacheName = 'edifice-pwa-v1';
const assets = [
    '/',
    // '/static/css/style.css', // Add your CSS files
    // '/static/js/main.js',   // Add your JS files
    // '/static/images/icon.png' // Add your image files
];

self.addEventListener('install', event => {
    event.waitUntil(
    caches.open(staticCacheName)
        .then(cache => {
        return cache.addAll(assets);
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(async function () {
        try {
            // Try to find a cached version
            const cachedResponse = await caches.match(event.request);
            if (cachedResponse) {
                console.log("CACHED RESPONSE");
                console.log(cachedResponse);
                return cachedResponse;
            }

            // Not in cache, try to fetch from the network
            const networkResponse = await fetch(event.request);

            console.log("NETWORK RESPONSE");
            console.log(networkResponse);

            return networkResponse;

        } catch (error) {
            // Fetch failed — log the error and return fallback
            console.error('Fetch failed for:', event.request.url, error);

            // Return fallback response
            return new Response('Offline or failed to fetch the requested resource.', {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'text/plain' }
            });
        }
    }());
});