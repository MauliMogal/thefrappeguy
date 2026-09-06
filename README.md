# The Frappe Guy — site files

Two files: `index.html` and `style.css`. No build step, no npm, no framework — plain HTML/CSS, so it works anywhere.

## What's real vs. placeholder
- Colors: matched exactly to julian.com (`#1e242e` background, `#e6e6e6` text, `#3fa9eb` links).
- Font: julian.com's exact typeface can't be read off a page fetch — only CSS class names and colors are visible, not licensed font files. This uses **Inter** (free, Google Fonts) as a close equivalent. If you want the real one, open julian.com in Chrome → Inspect → Computed → font-family to find the exact name, then swap it into `style.css` (`--font` variable at the top).
- Everything marked `[Dummy]` or `[PLACEHOLDER]` is a stand-in — replace with your own words once you've picked a positioning statement and written your bio. Don't skip this — a site full of bracketed placeholders live is worse than a "coming soon" page with nothing else.

## Fastest way to get this live (no coding required)

**Option A — Vercel drag-and-drop (simplest):**
1. Go to vercel.com, sign in (or create a free account).
2. Click "Add New" → "Project" → "Deploy" and drag the `frappe-guy-site` folder in, or use "Import" and drag the two files.
3. Vercel gives you a live URL in under a minute. You can attach a custom domain later (e.g. thefrappeguy.com) from Vercel's dashboard.

**Option B — fold it into your existing Next.js site (maulimogal.com):**
Since that's already on the portfolio-blog-starter, add a new route like `/frappe-guy` and paste this HTML/CSS in as a page — ask me for that version when you're ready, it needs slightly different syntax (JSX instead of plain HTML).

## When you come back to this
1. Finalize your positioning statement, replace the hero placeholder.
2. Write your own About paragraph — not me.
3. Once you have your first real post, replace one `[Dummy]` post item with the real one and link it.
4. Everything else can stay as "coming soon" until you have content to fill it.
