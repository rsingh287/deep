self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('push', function(event) {
  let data = {};
  if (event.data) {
    try {
      data = event.data.json();
    } catch(e) {
      data = { body: event.data.text() };
    }
  }
  
  const title = data.title || "D.E.E.P Alert";
  const options = {
    body: data.body || "New agentic notification",
    icon: '/static/icons/icon-192.png',
    badge: '/static/icons/badge-72.png',
    data: data.url || '/',
    vibrate: [200, 100, 200]
  };
  
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data));
});

self.addEventListener('fetch', (event) => {
  // Let network handle it
});
