import http from 'node:http'
import { readFileSync, existsSync } from 'node:fs'
import { extname, join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
const root = dirname(dirname(fileURLToPath(import.meta.url)))
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript', '.json': 'application/json' }
const server = http.createServer((req, res) => {
  const urlPath = req.url === '/' ? '/index.html' : req.url.split('?')[0]
  const mappedPath = urlPath === '/app.js' ? '/src/runtime-dashboard.js' : urlPath
  let file = join(root, mappedPath)
  if (!existsSync(file)) file = join(root, 'index.html')
  res.writeHead(200, { 'Content-Type': types[extname(file)] || 'text/plain' })
  res.end(readFileSync(file))
})
server.listen(5173, '127.0.0.1', () => console.log('Frontend: http://localhost:5173'))
