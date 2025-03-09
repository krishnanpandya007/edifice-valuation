const CACHE_NAME = "offline-form-cache-v1";
const urlsToCache = [
    "/register/site/",  // Form page URL
    // "/static/offline-form.js",  // JavaScript file for local storage
    // "/static/style.css",  // CSS file (if any)
];

// Install Service Worker and cache assets
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(urlsToCache);
        })
    );
});

// Intercept fetch requests and serve from cache if offline
self.addEventListener("fetch", (event) => {
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});
