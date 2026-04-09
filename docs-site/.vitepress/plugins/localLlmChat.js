import { spawn } from 'child_process'
import { resolve } from 'path'

/**
 * Vite plugin: adds /api/chat endpoint in dev mode.
 * Spawns `claude -p` with --add-dir for project context.
 */
export function localLlmChatPlugin(options = {}) {
  const projectRoot = options.projectRoot || process.cwd()
  const cliCommand = options.cliCommand || 'claude'

  return {
    name: 'local-llm-chat',
    apply: 'serve', // dev mode only

    configureServer(server) {
      server.middlewares.use('/api/chat', async (req, res) => {
        if (req.method === 'OPTIONS') {
          res.writeHead(200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
          })
          res.end()
          return
        }

        if (req.method !== 'POST') {
          res.writeHead(405, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ error: 'Method not allowed' }))
          return
        }

        let body = ''
        for await (const chunk of req) {
          body += chunk
        }

        let parsed
        try {
          parsed = JSON.parse(body)
        } catch {
          res.writeHead(400, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ error: 'Invalid JSON' }))
          return
        }

        const { project, question } = parsed
        if (!question) {
          res.writeHead(400, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({ error: 'Missing question field' }))
          return
        }

        const systemPrompt = [
          '你是一個專業的原始碼分析助手，專門針對開源專案進行深度分析。',
          '請用 zh-TW（繁體中文）回答，技術術語保持英文。',
          '回答時請引用具體的檔案路徑與程式碼片段。',
          '如果不確定，請誠實說明而非猜測。',
          '請用標準 Markdown 回答，不要使用 Mermaid 圖表語法；若要表達流程或架構，改用標題、清單、表格或一般程式碼區塊。',
        ].join('\n')

        const contextHint = project
          ? `請基於 ./${project}/ 目錄下的原始碼以及 ./docs-site/${project}/ 的分析文件來回答。`
          : '請基於整個專案來回答。'

        const fullPrompt = `${contextHint}\n\n使用者問題：${question}`

        const args = [
          '-p', fullPrompt,
          '--append-system-prompt', systemPrompt,
          '--output-format', 'json',
        ]

        if (project) {
          const projectDir = resolve(projectRoot, project)
          const docsDir = resolve(projectRoot, 'docs-site', project)
          args.push('--add-dir', projectDir, '--add-dir', docsDir)
        }

        // SSE for streaming progress
        res.writeHead(200, {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          'Access-Control-Allow-Origin': '*',
        })

        const heartbeat = setInterval(() => {
          res.write('event: ping\ndata: {}\n\n')
        }, 5000)

        res.write(`event: status\ndata: ${JSON.stringify({ status: 'thinking', message: '正在分析原始碼...' })}\n\n`)

        try {
          const result = await runClaude(cliCommand, args, projectRoot)
          res.write(`event: result\ndata: ${JSON.stringify({ result })}\n\n`)
        } catch (err) {
          res.write(`event: error\ndata: ${JSON.stringify({ error: err.message })}\n\n`)
        } finally {
          clearInterval(heartbeat)
          res.write('event: done\ndata: {}\n\n')
          res.end()
        }
      })
    },
  }
}

function runClaude(command, args, cwd) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'],
      timeout: 300000, // 5 min timeout
    })

    let stdout = ''
    let stderr = ''

    child.stdout.on('data', (data) => { stdout += data.toString() })
    child.stderr.on('data', (data) => { stderr += data.toString() })

    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`claude exited with code ${code}: ${stderr.slice(0, 500)}`))
        return
      }

      try {
        const parsed = JSON.parse(stdout)
        resolve(parsed.result || parsed.text || stdout)
      } catch {
        resolve(stdout.trim())
      }
    })

    child.on('error', (err) => {
      reject(new Error(`Failed to spawn claude: ${err.message}`))
    })
  })
}
