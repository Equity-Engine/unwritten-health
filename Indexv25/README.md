# unwritten.health

Marketing site for Unwritten Health. Static HTML deployed to Netlify. Version 25.

## Repo

https://github.com/Equity-Engine/unwritten-health

## Structure

```
.
├── .github/workflows/
│   └── dispatches-refresh.yml   # Weekly cron: pull Beehiiv Dispatches into blog.html
├── scripts/
│   └── refresh-dispatches.mjs   # Node script the workflow runs
├── netlify.toml                 # Netlify config (publish dir + functions dir)
├── netlify/functions/
│   └── submission-created.mjs   # Scorecard auto-reply (Resend)
└── site/                        # The actual website — this is what gets published
    ├── index.html
    ├── blog.html                # Has DISPATCHES-START/END markers
    └── ...
```

## Automations already running

- **Scorecard auto-reply** — every submission of the Regulatory Readiness Scorecard triggers `netlify/functions/submission-created.mjs`, which sends a personalised email via Resend (needs `RESEND_API_KEY` env var set in Netlify).
- **Weekly Dispatches refresh** — every Monday at 10:00 UTC (11:00 UK BST) GitHub Actions fetches the latest issues from `dispatches.unwritten.health/feed`, updates `site/blog.html`, and pushes. Netlify auto-deploys the change. Also runnable on demand from GitHub → Actions → "Refresh Unwritten Dispatches on blog" → Run workflow.

## First-time setup

If you (Ashish) are reading this fresh, here's the one-time Git + Netlify wiring.

### 1. Push this folder into the GitHub repo

The repo exists at https://github.com/Equity-Engine/unwritten-health but is probably empty.

1. Download **GitHub Desktop** from https://desktop.github.com
2. Open it, sign in with your GitHub account
3. **File → Clone repository** → pick `Equity-Engine/unwritten-health` → save it somewhere local (e.g. `~/Documents/GitHub/unwritten-health`)
4. Copy everything from the `Indexv25/` folder in Google Drive **into** that local clone (all the folders and files at root: `.github/`, `netlify/`, `netlify.toml`, `scripts/`, `site/`, `README.md`, `.gitignore`)
5. Back in GitHub Desktop: you'll see all the files listed as "changed" — add a commit summary like *"Initial site upload from v25"* and click **Commit to main**
6. Click **Push origin** (top-right)

Your repo now has the full site.

### 2. Connect Netlify to the repo

1. Go to https://app.netlify.com → your `unwritten-health` project
2. **Site configuration → Build & deploy → Continuous deployment → Link to Git provider**
3. Choose **GitHub**, authorise if prompted
4. Select the `Equity-Engine/unwritten-health` repo
5. Build settings should auto-populate from `netlify.toml`. If not:
   - Base directory: (leave blank)
   - Build command: (leave blank — no build needed for static HTML)
   - Publish directory: `site`
   - Functions directory: `netlify/functions`
6. Save. Netlify runs its first Git-based build — should succeed in ~30 seconds.

### 3. Verify the automation

1. Go to https://github.com/Equity-Engine/unwritten-health/actions
2. Click **Refresh Unwritten Dispatches on blog** in the left sidebar
3. Click **Run workflow → Run workflow** (green button on the right)
4. Wait ~30 seconds. If it succeeds, `blog.html` gets updated and Netlify redeploys automatically.
5. Visit `https://unwritten.health/blog` → the "From Unwritten Dispatches" section should show your latest 6 issues.

## Going forward

- **Edit files locally** in the GitHub Desktop clone → commit → push → Netlify auto-deploys within a minute.
- **Never drag-and-drop deploy again** — every deploy comes from a Git commit, so nothing gets lost.
- **Weekly Dispatches refresh** happens hands-off every Monday.
- **Manual refresh** any time via the "Run workflow" button above.

## Env vars in Netlify (already set, listed here for reference)

- `RESEND_API_KEY` — for the Scorecard auto-reply function

## Overriding the Dispatches feed URL

If Beehiiv changes the RSS URL or you move to a different platform, edit `scripts/refresh-dispatches.mjs` at the top:

```js
const FEED_URLS = [
  process.env.FEED_URL,
  'https://dispatches.unwritten.health/feed',   // ← primary
  'https://dispatches.unwritten.health/feed.xml',
  'https://dispatches.unwritten.health/rss'
].filter(Boolean);
```

Or set a `FEED_URL` environment variable in the workflow YAML.

## Troubleshooting

- **Workflow says "All feed URLs failed"** → Beehiiv changed the RSS path, or your custom-domain DNS isn't serving `/feed`. Try `curl -I https://dispatches.unwritten.health/feed` locally to confirm.
- **Netlify deploy fails after Git integration** → check the deploy log for `netlify.toml` errors. Publish should be `site`, functions `netlify/functions`.
- **Scorecard email stopped working** → check `RESEND_API_KEY` is still set in Netlify env vars, and Resend hasn't rate-limited or suspended the domain.
