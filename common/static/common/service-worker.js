// Service Worker - PWAインストールを有効にするための最小限の実装
self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', () => {
  self.clients.claim();
});
