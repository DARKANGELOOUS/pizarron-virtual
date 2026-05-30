self.addEventListener('install', (event) => {
    console.log('Service Worker instalado');
});

self.addEventListener('fetch', (event) => {
    // Para el MVP, simplemente dejamos pasar todas las peticiones
    event.respondWith(fetch(event.request));
});