'use strict';
const CACHE='jxxzy-signature-v4-3',LIMIT=100;
const SHELL=['./index.html','./assets/racing.css','./assets/experience.css','./assets/signature.css','./assets/signature.js','./assets/catalog.js','./assets/icon.svg','./offline.html'];
const scope=new URL('./',self.location.href);
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('jxxzy-signature-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
async function remember(req,res){if(!res.ok||res.type==='opaque')return;try{const c=await caches.open(CACHE);await c.put(req,res.clone());const keys=await c.keys();const protectedUrls=new Set(SHELL.map(s=>new URL(s,scope).href));const removable=keys.filter(k=>!protectedUrls.has(k.url));while(removable.length>LIMIT)await c.delete(removable.shift())}catch(_){/* storage can be disabled or full */}}
self.addEventListener('fetch',e=>{const req=e.request,u=new URL(req.url);if(req.method!=='GET'||u.origin!==scope.origin||!u.pathname.startsWith(scope.pathname)||/\.(pdf|mp4|webm|dxv)$/i.test(u.pathname)||req.headers.has('range'))return;
if(req.mode!=='navigate'&&!/\.(html|css|js|svg|png|webp|jpe?g)$/i.test(u.pathname))return;
e.respondWith((async()=>{try{const r=await fetch(req);await remember(req,r);return r}catch(_){const cache=await caches.open(CACHE),hit=await cache.match(req);if(hit)return hit;if(req.mode==='navigate'){if(u.pathname===scope.pathname){const home=await cache.match('./index.html');if(home)return home}return await cache.match('./offline.html')||Response.error()}return Response.error()}})())});
