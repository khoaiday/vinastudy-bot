const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const ROOT_DIR = path.resolve(__dirname, '..');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.mp3': 'audio/mpeg',
  '.ogg': 'audio/ogg',
  '.wav': 'audio/wav',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.ico': 'image/x-icon',
};

const server = http.createServer((req, res) => {
  // Prevent path traversal
  let safeUrl = req.url.split('?')[0];
  if (safeUrl === '/') {
    safeUrl = '/intro.html'; // Default landing page
  } else if (safeUrl === '/game' || safeUrl === '/map') {
    safeUrl = '/map.html'; // Campaign map
  }

  const filePath = path.join(ROOT_DIR, safeUrl);
  console.log(`[REQUEST] ${req.method} ${req.url} -> ${filePath}`);

  // Check if file exists within workspace root
  // We resolve paths to ensure robust comparison, lowercasing drive letters for Windows compatibility
  const resolvedRoot = path.resolve(ROOT_DIR).toLowerCase();
  const resolvedPath = path.resolve(filePath).toLowerCase();

  if (!resolvedPath.startsWith(resolvedRoot)) {
    console.warn(`[DENIED] Path traversal attempt blocked: ${filePath}`);
    res.statusCode = 403;
    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    res.end('Access Denied');
    return;
  }

  // Helper to handle clean URLs (auto-appending .html if request lacks extension)
  const tryServeFile = (pathToCheck) => {
    fs.stat(pathToCheck, (err, stats) => {
      if (!err && stats.isFile()) {
        const ext = path.extname(pathToCheck).toLowerCase();
        const contentType = MIME_TYPES[ext] || 'application/octet-stream';

        res.statusCode = 200;
        res.setHeader('Content-Type', contentType);

        const stream = fs.createReadStream(pathToCheck);
        stream.on('error', () => {
          res.statusCode = 500;
          res.setHeader('Content-Type', 'text/plain; charset=utf-8');
          res.end('Internal Server Error');
        });
        stream.pipe(res);
      } else if (pathToCheck === filePath && !path.extname(filePath)) {
        // Try appending .html
        console.log(`[CLEAN URL] Trying fallback: ${filePath}.html`);
        tryServeFile(filePath + '.html');
      } else {
        console.warn(`[NOT FOUND] File not found: ${filePath}`);
        res.statusCode = 404;
        res.setHeader('Content-Type', 'text/plain; charset=utf-8');
        res.end('404 Not Found');
      }
    });
  };

  tryServeFile(filePath);
});

server.listen(PORT, () => {
  console.log('=====================================================');
  console.log(`🎮 ĐẠI VIỆT DEFENSE — Local Server Started Successfully`);
  console.log(`🔗 Link chơi game: http://localhost:${PORT}/daiviet_defense/index.html`);
  console.log('=====================================================');
  console.log('Nhấn Ctrl+C trong terminal để dừng server.');
});
