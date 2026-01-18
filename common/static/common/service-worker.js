// Service Worker - 静的ファイルキャッシュ対応
const CACHE_NAME = 'genbanote-v1';

// キャッシュする静的ファイルの拡張子
const CACHEABLE_EXTENSIONS = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf'];

// キャッシュ対象か判定
function isCacheable(url) {
  return CACHEABLE_EXTENSIONS.some(ext => url.pathname.endsWith(ext));
}

// インストール時
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

// アクティベート時（古いキャッシュを削除）
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// リクエスト時（静的ファイルはキャッシュ優先）
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // 静的ファイルのみキャッシュ対象
  if (event.request.method === 'GET' && isCacheable(url)) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request).then((response) => {
          // 正常なレスポンスのみキャッシュ
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        });
      })
    );
  }
});
