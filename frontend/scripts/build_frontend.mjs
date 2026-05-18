import { mkdirSync, copyFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
const root = dirname(dirname(fileURLToPath(import.meta.url)))
const dist = join(root, 'dist')
mkdirSync(dist, { recursive: true })
copyFileSync(join(root, 'index.html'), join(dist, 'index.html'))
writeFileSync(join(dist, 'app.js'), 'console.log("Argument-Risk-Engine dashboard build");\n')
console.log('Built frontend MVP into dist/')
