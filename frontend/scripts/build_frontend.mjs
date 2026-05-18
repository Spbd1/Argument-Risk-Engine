import { mkdirSync, copyFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
const root = dirname(dirname(fileURLToPath(import.meta.url)))
const dist = join(root, 'dist')
mkdirSync(join(dist, 'src/styles'), { recursive: true })
copyFileSync(join(root, 'index.html'), join(dist, 'index.html'))
copyFileSync(join(root, 'src/styles/global.css'), join(dist, 'src/styles/global.css'))
copyFileSync(join(root, 'src/runtime-dashboard.js'), join(dist, 'app.js'))
console.log('Built frontend dashboard into dist/')
