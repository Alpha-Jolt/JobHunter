import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { authenticate } from '@mail-bridge/shared'

export function createDashboardRouter(pool: Pool): Router {
  const router = Router()

  router.get('/', authenticate, async (req: Request, res: Response, next: NextFunction) => {
    try {
      const workspaceId = req.user!.workspace_id

      const [wsResult, credCount, emailToday, recentEmails] = await Promise.all([
        pool.query<{ name: string; tier: string }>('SELECT name, tier FROM workspaces WHERE workspace_id = $1', [workspaceId]),
        pool.query<{ count: string }>('SELECT COUNT(*) FROM credentials WHERE workspace_id = $1 AND is_active = TRUE', [workspaceId]),
        pool.query<{ count: string }>(`SELECT COUNT(*) FROM email_logs WHERE workspace_id = $1 AND created_at >= CURRENT_DATE`, [workspaceId]),
        pool.query<{ to_email: string; subject: string; status: string; created_at: Date }>(
          `SELECT to_email, subject, status, created_at FROM email_logs WHERE workspace_id = $1 ORDER BY created_at DESC LIMIT 10`,
          [workspaceId]
        )
      ])

      const ws = wsResult.rows[0] ?? { name: 'Unknown', tier: 'free' }
      const rows = recentEmails.rows.map(r =>
        `<tr><td>${r.to_email}</td><td>${r.subject}</td><td>${r.status}</td><td>${new Date(r.created_at).toLocaleString()}</td></tr>`
      ).join('')

      res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mail-Bridge | Dashboard</title>
  <style>
    :root { --bg: #0f172a; --card: rgba(30,41,59,0.8); --text: #f1f5f9; --muted: #94a3b8; --accent: #6366f1; --success: #10b981; }
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: system-ui, sans-serif; }
    body { background: var(--bg); color: var(--text); min-height: 100vh; padding: 2rem; }
    h1 { font-size: 1.5rem; margin-bottom: 1.5rem; }
    h1 span { color: var(--accent); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .card { background: var(--card); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1.25rem; }
    .card-label { color: var(--muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .card-value { font-size: 1.5rem; font-weight: 700; }
    table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; }
    th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.875rem; }
    th { color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 0.05em; }
    h2 { margin-bottom: 0.75rem; font-size: 1rem; color: var(--muted); }
  </style>
</head>
<body>
  <h1>Mail<span>-Bridge</span></h1>
  <div class="grid">
    <div class="card"><div class="card-label">Workspace</div><div class="card-value">${ws.name}</div></div>
    <div class="card"><div class="card-label">Tier</div><div class="card-value">${ws.tier}</div></div>
    <div class="card"><div class="card-label">Credentials</div><div class="card-value">${credCount.rows[0].count}</div></div>
    <div class="card"><div class="card-label">Emails Today</div><div class="card-value">${emailToday.rows[0].count}</div></div>
  </div>
  <h2>Recent Emails</h2>
  <table>
    <thead><tr><th>To</th><th>Subject</th><th>Status</th><th>Sent At</th></tr></thead>
    <tbody>${rows || '<tr><td colspan="4" style="color:var(--muted);text-align:center">No emails yet</td></tr>'}</tbody>
  </table>
</body>
</html>`)
    } catch (err) { next(err) }
  })

  return router
}
