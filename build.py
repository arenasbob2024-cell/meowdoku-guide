# -*- coding: utf-8 -*-
"""Static site builder for the Meowdoku Guide (independent fan site)."""
import json, os, html

BASE = "https://meowdoku-guide.vercel.app"
NAME = "Meowdoku Guide"
DATE = "2026-11-04"

NAV = [
    ("", "Home"),
    ("practice", "Play"),
    ("how-to-play", "How to play"),
    ("strategy", "Strategy"),
    ("about", "About"),
]

DISCLAIMER = (
    "Independent fan guide and original practice game. Not affiliated with, endorsed by or sponsored "
    "by Oakever Games. “Meowdoku” is the name of a game owned by its developer; all rights stay with its "
    "owner. Our Cat Territory boards are generated for this site and use no Oakever levels, artwork or "
    "assets. The official app is on Google Play and the Galaxy Store."
)

PALETTE = ["#f6d4c2", "#cfe6d4", "#c9dcf3", "#f2e3a8", "#e5d1f0",
           "#f4c9d8", "#d2e7e7", "#e9dcc7", "#d8d3f1"]

PUZZLES = json.load(open("puzzles.json"))["puzzles"]
P1 = [p for p in PUZZLES if p["n"] == 6][0]


def url_for(slug):
    return BASE + "/" + (slug + "/" if slug else "")


def mini(regions, cats=(), bad=(), xs=(), caption=""):
    n = len(regions)
    cells = []
    for r in range(n):
        for c in range(n):
            cls = ""
            content = ""
            if (r, c) in cats:
                cls = "cat"
                content = "🐱"
            elif (r, c) in xs:
                content = "✕"
            if (r, c) in bad:
                cls += " bad"
            cells.append('<div class="%s" style="background:%s">%s</div>' % (
                cls.strip(), PALETTE[regions[r][c] % len(PALETTE)], content))
    cap = '<figcaption>%s</figcaption>' % caption if caption else ""
    return ('<figure class="figure"><div class="mini" style="grid-template-columns:repeat(%d,1fr)">%s</div>%s</figure>'
            % (n, "".join(cells), cap))


# hand-built 5x5 region maps for the rule diagrams
A = [[0, 0, 0, 1, 1],
     [0, 0, 1, 1, 1],
     [2, 2, 1, 1, 3],
     [2, 2, 4, 4, 3],
     [2, 4, 4, 3, 3]]
B = [[0, 1, 1, 2, 2],
     [0, 1, 3, 3, 2],
     [0, 1, 3, 4, 2],
     [0, 1, 3, 4, 2],
     [0, 1, 3, 4, 2]]


def ld_graph(slug, title, desc, faqs=None, app=False):
    url = url_for(slug)
    graph = [{
        "@type": "WebPage", "@id": url + "#page", "url": url, "name": title,
        "description": desc, "inLanguage": "en", "datePublished": DATE,
        "dateModified": DATE, "isPartOf": {"@type": "WebSite", "@id": BASE + "/#site"},
    }]
    if app:
        graph.append({
            "@type": "WebApplication", "@id": BASE + "/practice/#app",
            "name": "Cat Territory Practice",
            "url": url_for("practice"),
            "description": "An original browser logic puzzle: one cat per coloured region, row and column, and no touching cats, even diagonally.",
            "applicationCategory": "GameApplication",
            "operatingSystem": "Any (web browser)",
            "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        })
    if slug:
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": title.split(":")[0], "item": url},
            ],
        })
    if faqs:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs],
        })
    return {"@context": "https://schema.org", "@graph": graph}


def nav_html(slug):
    out = []
    for s, label in NAV:
        cur = ' aria-current="page"' if s == slug else ""
        out.append('<a href="/%s"%s>%s</a>' % (s + "/" if s else "", cur, label))
    return '<nav class="site" aria-label="Site">' + "".join(out) + "</nav>"


def crumb(title):
    return '<p class="breadcrumb"><a href="/">Home</a> › ' + html.escape(title.split(":")[0]) + "</p>"


def page(slug, title, desc, h1, lede, body, faqs=None, app=False, extra_head="", scripts=""):
    url = url_for(slug)
    ld = json.dumps(ld_graph(slug, title, desc, faqs, app), ensure_ascii=False).replace("</", "<\\/")
    faq_html = ""
    if faqs:
        faq_html = '<section id="faq"><h2>Frequently asked questions</h2>' + "".join(
            "<h3>%s</h3><p>%s</p>" % (html.escape(q), html.escape(a)) for q, a in faqs
        ) + "</section>"
    doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="google-site-verification" content="v3fOBTrnUxrsOgGbxsQZ7I0o6ZaDt9COHdEH5fEkBDA" />
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="robots" content="index,follow">
<link rel="canonical" href="%(url)s">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css?v=20261104">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%(name)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#fbf7ef">
<script type="application/ld+json">%(ld)s</script>
%(extra)s
</head>
<body>
<main>
<header class="site">
  <a class="brand" href="/">Meowdoku <span>Guide</span></a>
  %(nav)s
</header>
%(crumb)s
<h1>%(h1)s</h1>
%(lede)s
%(body)s
%(faq)s
<div class="disclaimer">%(disclaimer)s</div>
<footer class="site">
  <p><a href="/about/">About &amp; editorial policy</a> · <a href="/privacy/">Privacy</a> · <a href="/how-to-play/">Rules</a> · <a href="/strategy/">Strategy</a> · <a href="/practice/">Play</a></p>
  <p>Updated %(date)s. Official app: <a href="https://play.google.com/store/apps/details?id=com.oakever.meowdoku" rel="noopener nofollow">Google Play</a>.</p>
</footer>
</main>
%(scripts)s
</body>
</html>
""" % dict(title=html.escape(title), desc=html.escape(desc), url=url, name=NAME, ld=ld,
           extra=extra_head, nav=nav_html(slug), crumb=crumb(title) if slug else "",
           h1=h1, lede=lede, body=body, faq=faq_html, disclaimer=DISCLAIMER,
           date=DATE, scripts=scripts)
    path = os.path.join(slug, "index.html") if slug else "index.html"
    if slug:
        os.makedirs(slug, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


def split_lede(body):
    first, rest = body.split("</p>", 1)
    return first + "</p>", rest


def card(href, h, p):
    return '<div class="card"><h3><a href="%s">%s</a></h3><p>%s</p></div>' % (href, h, p)


def board_js(p):
    return '<div class="mini" style="grid-template-columns:repeat(%d,1fr)">%s</div>' % (
        p["n"], "".join(
            '<div style="background:%s">%s</div>' % (
                PALETTE[p["regions"][r][c] % len(PALETTE)],
                "🐱" if p["solution"][r] == c else "")
            for r in range(p["n"]) for c in range(p["n"])
        ))


# ---------------------------------------------------------------- home
home_body = """
<p class="lede">Meowdoku is a cat-themed logic puzzle from Oakever Games that blends Sudoku-style line thinking with Minesweeper-style deduction. You place one cat in every coloured region, one per row and column, and never let two cats touch — not even at a corner. This independent guide explains the rules, collects practical solving techniques and includes a free browser puzzle generator you can play right now.</p>

<p><a class="button" href="/practice/">Play a free puzzle</a> <a class="button ghost" href="https://play.google.com/store/apps/details?id=com.oakever.meowdoku" rel="noopener nofollow">Get the official app ↗</a></p>

<div class="note"><b>The official game is a mobile/Windows app by Oakever Games.</b> There is no official browser version of Meowdoku. The board on this site is an <b>original practice game</b> that follows the same public rules — it is not the official app and does not use its levels or artwork.</div>

<h2>Meowdoku at a glance</h2>
<table>
<tr><th>What</th><th>Details</th></tr>
<tr><td>Game</td><td>Meowdoku: Brain Puzzle Games</td></tr>
<tr><td>Developer</td><td>Oakever Games</td></tr>
<tr><td>Platforms</td><td>Android and Windows (Google Play listing; also on the Galaxy Store)</td></tr>
<tr><td>Price</td><td>Free, with ads and optional in-app purchases</td></tr>
<tr><td>Google Play</td><td>4.7 stars, 598K reviews, 10M+ downloads (checked 4 Nov 2026)</td></tr>
<tr><td>Last store update</td><td>30 October 2026</td></tr>
<tr><td>Core rules</td><td>One cat per coloured region, per row, per column; no cats touching, even diagonally</td></tr>
<tr><td>Mistakes</td><td>Three hearts per level</td></tr>
<tr><td>Modes</td><td>Levels, a daily puzzle, global leaderboards, offline play</td></tr>
</table>
<p class="small">Store figures are the public Google Play listing values on the check date; they change over time.</p>

<h2>The three rules</h2>
<ol>
<li><b>One cat per coloured region.</b> Every colour is a territory, whatever its shape. Exactly one tile in each territory holds a cat.</li>
<li><b>One cat per row and column.</b> A cat blocks the rest of its row and its column.</li>
<li><b>No touching.</b> Two cats may not share an edge <i>or a corner</i>. Every placement also blocks the eight surrounding tiles.</li>
</ol>
""" + mini(A, cats=[(2, 2)], xs=[(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)],
          caption="A cat claims its row, its column and all eight neighbouring tiles.") + """
<p>Those three rules interact. A region that sits entirely inside one column claims that column. A row that already contains a cat cannot host another. And a candidate tile that touches an existing cat is dead even if its colour still needs a cat. Most of the game is reading those interactions in the right order — see the <a href="/strategy/">strategy guide</a>.</p>

<h2>Meowdoku or Sudoku?</h2>
<table>
<tr><th></th><th>Meowdoku</th><th>Classic Sudoku</th></tr>
<tr><td>Board</td><td>Coloured irregular regions</td><td>Fixed boxes</td></tr>
<tr><td>Placement</td><td>One cat per region, row and column</td><td>Digits 1–9 once per row, column and box</td></tr>
<tr><td>Extra constraint</td><td>Cats cannot touch, including diagonally</td><td>No diagonal rule in standard Sudoku</td></tr>
<tr><td>Mistakes</td><td>Three hearts per level</td><td>Usually unlimited, with error highlighting</td></tr>
<tr><td>Typical size</td><td>Small boards that grow with level</td><td>9×9 from the start</td></tr>
</table>
<p>Players often compare it to “Queens” logic puzzles: one piece per row, column and colour, with the no-touching rule on top. If you have solved Queens-style boards before, the first Meowdoku levels will feel familiar.</p>

<div class="cta">
<h2>Play a free Cat Territory puzzle</h2>
<p>Our <a href="/practice/">practice board</a> generates original puzzles from 6×6 to 9×9, checks for a unique solution, and gives you marks, hints and a timer. It runs entirely in your browser — no account, no download.</p>
<p><a class="button" href="/practice/">Play a puzzle</a></p>
</div>

<h2>What the app includes</h2>
<div class="grid">
""" + card("/how-to-play/", "Levels and hearts", "Tap once to mark a tile, double-tap to place a cat. Three wrong placements cost the level.") + card("/strategy/", "A daily puzzle", "New daily boards and global leaderboards for fastest completion times.") + card("/practice/", "Offline play", "The mobile app works without a connection; this browser practice game also runs offline once loaded.") + """
</div>

<h2>Getting the official app</h2>
<p>The official Meowdoku is published by Oakever Games on <a href="https://play.google.com/store/apps/details?id=com.oakever.meowdoku" rel="noopener nofollow">Google Play</a> and the Samsung Galaxy Store, with a Windows version listed on Google Play’s PC store. We do not host, mirror or redistribute the app.</p>

<p class="small"><b>Sources checked 2026-11-04:</b> the Google Play listing for <i>Meowdoku: Brain Puzzle Games</i> (developer, rating, downloads, update date, rules, hearts, platforms) and the public store description. Rules described here are the public game rules; all puzzles on this site are our own.</p>
"""

home_faq = [
    ("What is Meowdoku?", "Meowdoku is a cat-themed logic puzzle by Oakever Games. You place one cat in every coloured region, one per row and column, and cats may not touch — not even diagonally."),
    ("Who makes Meowdoku?", "Oakever Games publishes the official app on Google Play, the Galaxy Store and Windows via Google Play Games on PC."),
    ("Is Meowdoku free?", "Yes. The app is free with ads and optional in-app purchases."),
    ("Is there an official Meowdoku web version?", "No. The official product is the Oakever Games app. The playable board on this site is an independent practice game with original puzzles, not the official app."),
    ("How many mistakes can you make in Meowdoku?", "Three per level — the game shows three hearts."),
    ("What is the difference between Meowdoku and a Queens puzzle?", "Both use one piece per row, column and coloured region. Meowdoku adds the rule that cats cannot touch, including diagonally."),
    ("Is this site affiliated with Oakever Games?", "No. It is an independent fan guide and practice game; we use no Oakever levels, art or assets."),
]

page("", "Meowdoku: Rules, Strategy & a Free Playable Puzzle",
     "Meowdoku guide: the three rules explained, Sudoku vs Meowdoku, practical solving strategy, and a free original Cat Territory puzzle you can play in the browser.",
     "Meowdoku: Rules, Strategy and a Free Practice Puzzle",
     *split_lede(home_body), faqs=home_faq)


# ---------------------------------------------------------------- how to play
how_body = """
<p class="lede">Meowdoku looks simple for about ten seconds, then the three rules start interacting. This page explains each rule with a diagram, shows how the controls work in the official app, and walks through the opening deductions of a real board.</p>

<h2>Rule 1 — one cat per coloured region</h2>
<p>The board is divided into coloured territories of different shapes. Every territory needs exactly one cat: no empty territory, no territory with two. A one-tile region is a free placement; a large sprawling region is where elimination does the work.</p>
""" + mini(A, cats=[(0, 2), (1, 0)], bad=[(0, 2), (1, 0)],
          caption="Illegal: two cats in the same region (even though they are not touching).") + """
<h2>Rule 2 — one cat per row and column</h2>
<p>A cat controls its entire row and column. Place one and every other tile in those two lines becomes impossible, no matter which colour it belongs to.</p>
""" + mini(A, cats=[(2, 0), (2, 2)], bad=[(2, 0), (2, 2)],
          caption="Illegal: two cats share row 3.") + """
<h2>Rule 3 — cats cannot touch, even diagonally</h2>
<p>The eight tiles around a cat are forbidden: four orthogonal neighbours and four diagonal corners. This is the rule that catches most beginners, because a diagonal contact looks harmless on a wide board.</p>
""" + mini(A, cats=[(1, 1), (2, 2)], bad=[(1, 1), (2, 2)],
          caption="Illegal: two cats touch at a corner.") + """
<h2>Controls in the official app</h2>
<table>
<tr><th>Action</th><th>What happens</th></tr>
<tr><td>Tap a tile once</td><td>Places a marker / cross to note that a tile cannot hold a cat.</td></tr>
<tr><td>Double-tap a tile</td><td>Places a cat. Wrong placements cost one of your three hearts.</td></tr>
<tr><td>Clear a mark</td><td>Tap the marked tile again (the exact gesture is shown in the app’s tutorial).</td></tr>
</table>
<p>Controls can change between app versions; the in-app tutorial is authoritative. Our browser practice board uses a single tap to cycle empty → cross → cat, so it works the same on a phone and a desktop.</p>

<h2>Hearts and level flow</h2>
<p>Each level gives you <b>three hearts</b>. A wrong cat placement removes one; run out and the level restarts. Because the game punishes guessing, the correct habit is to place a cat only when a tile is logically forced. Use marks to record what you have eliminated, not guesses.</p>
<p>Boards start small and grow as you progress. The daily puzzle gives everyone the same new board each day and feeds a global fastest-time leaderboard.</p>

<h2>Beginner walkthrough: the opening of a 6×6 board</h2>
<p>Here is one of our own practice boards with its solution. Follow the opening deductions before you look at the cats.</p>
""" + board_js(P1) + """
<p class="small">Our original 6×6 practice board, solved. Colours are regions; each cat is a solution cell.</p>
<ol>
<li><b>Count the regions and find the smallest.</b> The three-cell strip in the leftmost column (rows 4–6) is the smallest territory.</li>
<li><b>Claim its line.</b> That region must put its cat in the leftmost column, so no other region may use that column.</li>
<li><b>Follow the consequence.</b> The four-cell region at the top-left has two cells in the leftmost column; both are now dead. Its cat must be in the second column.</li>
<li><b>Chain it once more.</b> The second column is now claimed too. The bottom region has three cells in the second column and one in the third; all three second-column cells are dead, so its only remaining cell — row 6, column 3 — is forced.</li>
<li><b>Mark the halo.</b> Cross out the row, column and eight neighbours of every cat you place. The next forced tile usually appears at the edge of that halo.</li>
</ol>
<p>You do not need to see the whole solution at once. Each forced cat removes possibilities, and the board slowly collapses. The <a href="/strategy/">strategy guide</a> covers the standard deduction patterns in order.</p>

<h2>Five beginner mistakes</h2>
<ol>
<li><b>Guessing to “test” a tile.</b> With three hearts, a guess is expensive. Mark it instead and keep deducing.</li>
<li><b>Forgetting diagonals.</b> The corner rule kills more candidates than any other constraint.</li>
<li><b>Ignoring large regions.</b> Big regions look unconstrained, but every cell outside them is a constraint on where they can go.</li>
<li><b>Not clearing a region when it is solved.</b> Once a region has its cat, all its other tiles are dead; mark them so you do not revisit them.</li>
<li><b>Playing too fast for the leaderboard.</b> Speed comes from clean notation; guessing for a fast time usually ends in a lost heart.</li>
</ol>

<h2>Practise the rules</h2>
<p>Our <a href="/practice/">Cat Territory board</a> lets you play the same rule set with original puzzles and no hearts — make mistakes, use hints, and learn the patterns before you spend hearts in the app.</p>

<p class="small"><b>Sources checked 2026-11-04:</b> Google Play listing for <i>Meowdoku: Brain Puzzle Games</i> (rules, hearts, double-tap control, daily puzzles, leaderboards, offline play, Android and Windows). The in-app tutorial is authoritative for current controls.</p>
"""

how_faq = [
    ("How do you play Meowdoku?", "Place one cat in every coloured region, one per row and one per column, and never let two cats touch — not even diagonally."),
    ("What happens if you make a mistake in Meowdoku?", "You lose one of three hearts. Lose all three and the level restarts."),
    ("Do cats touch diagonally in Meowdoku?", "No. Diagonal contact is illegal, just like sharing an edge."),
    ("How big are Meowdoku boards?", "They start small and grow as you progress through the levels; the daily puzzle uses its own board."),
    ("Is there a daily Meowdoku puzzle?", "Yes. The app adds a new daily puzzle and tracks fastest completion times on a global leaderboard."),
]

page("how-to-play", "How to Play Meowdoku: The Three Rules Explained",
     "Meowdoku rules with diagrams: one cat per coloured region, row and column, no touching even diagonally, three hearts, controls, and a beginner walkthrough.",
     "How to Play Meowdoku: The Three Rules Explained",
     *split_lede(how_body), faqs=how_faq)


# ---------------------------------------------------------------- strategy
strategy_body = """
<p class="lede">Meowdoku is solved by forced moves, not by inspiration. These seven patterns cover almost every deduction you need, in the order a strong player usually applies them. All diagrams come from our own practice boards, not from Oakever levels.</p>

<h2>1. Start with the smallest region</h2>
<p>Small regions have fewer possible homes, so they produce the first forced cat. Count the tiles in each colour and begin with the shortest list. A one-tile region is an immediate cat; a two- or three-tile region usually collapses after one row or column is blocked.</p>
""" + mini(B, cats=[(2, 0)], xs=[(0, 0), (1, 0), (3, 0), (4, 0)],
          caption="The region made of the entire first column claims that column; every other tile in it is dead.") + """
<h2>2. A region confined to one line claims that line</h2>
<p>If every tile of a region sits in a single row or column, that line belongs to the region. No other colour may place a cat there. This is the fastest way to open a board with a long, thin region.</p>

<h2>3. Cross out the whole row and column</h2>
<p>After every cat, mark the rest of its row and column. It feels wasteful to mark ten tiles at once, but those marks are the deduction: they turn a big board into a small one. Do it consistently and you will stop re-checking the same cells.</p>

<h2>4. Mark the eight-neighbour halo</h2>
<p>The no-touching rule is what separates Meowdoku from a plain Queens puzzle. Every cat kills up to eight nearby tiles. Mark them immediately — especially the diagonals, which are easy to forget and expensive to miss.</p>
""" + mini(A, cats=[(2, 2)], xs=[(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)],
          caption="One cat removes its row, column and all eight neighbours.") + """
<h2>5. Use region + line intersections</h2>
<p>Combine constraints one at a time. If a region has cells in three rows but two of those rows already contain cats, the region’s cat must be in the third row. If that leaves only one cell in the third row, it is forced. Most mid-game moves are exactly this intersection.</p>

<h2>6. Look for two-region pairs</h2>
<p>When two regions together occupy only two rows, those two rows are closed to every other region: the pair must place both of its cats there. The same logic works for two columns. This pattern unlocks boards that look stuck after the easy cats are gone.</p>

<h2>7. Never guess — use a mark</h2>
<p>A guess costs a heart and teaches you nothing when it fails. If a cell looks promising but is not forced, mark it as “maybe” and keep deducing elsewhere. On paper and in our practice board you can mark freely; in the app, use the single-tap marker. The board eventually forces the cell, and you keep all three hearts.</p>

<h2>Putting it together: an opening sequence</h2>
<ol>
<li>Count region sizes; find the smallest.</li>
<li>Check whether it is confined to one row or column; if so, claim that line.</li>
<li>Place the cat, then mark its row, column and halo.</li>
<li>Re-count the remaining candidates in each region. A region with one candidate is forced.</li>
<li>Repeat. When no region has one candidate, look for a two-region pair or a region confined by occupied lines.</li>
</ol>

<h2>Speed and the leaderboard</h2>
<p>Fast solvers are not guessing faster; they are marking less. Good notation means you never re-derive the same elimination. If you are chasing a leaderboard time, practise the patterns until they are automatic, then work on board scanning: sweep rows, columns and regions in the same order every time so a missed candidate stands out.</p>

<h2>Drill the patterns</h2>
<p>Our <a href="/practice/">practice board</a> generates original 6×6 to 9×9 puzzles with a guaranteed unique solution. It has no hearts, so you can test a deduction, undo it and learn the pattern without losing a level. Start at 6×6 until the first four patterns are automatic, then move up.</p>

<p class="small">All diagrams on this page are original boards generated for this site. No Meowdoku level layouts or artwork are reproduced.</p>
"""

strategy_faq = [
    ("What is the best way to start a Meowdoku puzzle?", "Find the smallest coloured region and check whether it is confined to one row or column. That usually produces the first forced cat."),
    ("Why do I keep losing hearts in Meowdoku?", "Guessing. Only place a cat when a tile is logically forced; use the single-tap marker to record eliminations instead."),
    ("What is the most missed rule in Meowdoku?", "Diagonal contact. Cats cannot touch at corners, so every placement also blocks eight neighbouring tiles."),
    ("Does the practice board use Meowdoku levels?", "No. Every practice puzzle is generated for this site with a verified unique solution; no Oakever levels or assets are used."),
]

page("strategy", "Meowdoku Strategy: 7 Deduction Techniques That Work",
     "Meowdoku strategy with diagrams: smallest region first, line-confined regions, row and column elimination, adjacency halos, intersections and pairs.",
     "Meowdoku Strategy: 7 Deduction Techniques",
     *split_lede(strategy_body), faqs=strategy_faq)


# ---------------------------------------------------------------- practice
practice_body = """
<p class="lede">Cat Territory is our original browser puzzle in the Meowdoku style: one cat per coloured region, one per row and column, and no cats touching — not even diagonally. Every board is generated for this site and checked to have exactly one solution. It is a practice tool, not the official Meowdoku app.</p>

<section class="game" aria-label="Cat Territory practice puzzle">
  <div class="game-top">
    <div class="sizes" role="group" aria-label="Board size">
      <button type="button" data-size="6" class="active">6×6</button>
      <button type="button" data-size="7">7×7</button>
      <button type="button" data-size="8">8×8</button>
      <button type="button" data-size="9">9×9</button>
    </div>
  </div>
  <div class="game-meta">
    <span>Time: <span id="timer">0:00</span></span>
    <span id="counter">0 / 6 cats placed</span>
    <span id="best"></span>
  </div>
  <div class="board-wrap" id="boardWrap">
    <div id="board" role="group" aria-label="Cat Territory board"></div>
  </div>
  <div class="board-tools">
    <button type="button" id="newBtn">New puzzle</button>
    <button type="button" id="checkBtn" class="ghost">Check</button>
    <button type="button" id="hintBtn" class="ghost">Hint</button>
    <button type="button" id="resetBtn" class="ghost">Clear marks</button>
  </div>
  <p class="status" id="status" role="status" aria-live="polite"></p>
  <div id="winBanner" hidden><strong>Solved!</strong> <span id="winText"></span></div>
</section>

<h2>How to play this board</h2>
<ul>
<li><b>Tap a cell</b> to cycle: empty → ✕ (not a cat) → cat → empty.</li>
<li><b>Check</b> validates the current cats and marks rule conflicts in red. The board also checks automatically when you place the last cat.</li>
<li><b>Hint</b> reveals one correct cat from the solution and locks it. It clears any of your cats that would conflict with the revealed answer.</li>
<li><b>Clear marks</b> removes your marks but keeps hinted cats.</li>
<li><b>Timer</b> starts with each new puzzle; your best time per board size is stored in your browser.</li>
</ul>

<h2>What is generated, and how</h2>
<p>Each puzzle starts from a valid solution — one cat per row and column, with no two cats adjacent. We then grow nine connected coloured regions around that solution, one cat per region, and run a solver that counts solutions. A board is only published if the solver finds <b>exactly one</b> solution. The same generator produced the diagrams on the rules and strategy pages.</p>

<h2>Practice vs the official app</h2>
<table>
<tr><th></th><th>This practice board</th><th>Official Meowdoku</th></tr>
<tr><td>Price</td><td>Free, no ads, no account</td><td>Free with ads and in-app purchases</td></tr>
<tr><td>Boards</td><td>Original 6×6–9×9 puzzles generated here</td><td>Oakever’s levels and daily puzzles</td></tr>
<tr><td>Mistakes</td><td>No hearts; check and retry freely</td><td>Three hearts per level</td></tr>
<tr><td>Hints</td><td>Unlimited, reveals a correct cat</td><td>App-specific</td></tr>
<tr><td>Data</td><td>Stays in your browser</td><td>See the app’s own privacy policy</td></tr>
</table>

<h2>Tips for using it as training</h2>
<ol>
<li>Start on 6×6 and solve three boards without hints before moving up.</li>
<li>Say the deduction out loud: “this region is confined to column 2, so column 2 is taken.”</li>
<li>Use ✕ marks instead of guessing; the habit transfers directly to the app.</li>
<li>When stuck, press Check rather than Hint. A conflict tells you which rule you misread.</li>
<li>Once a size feels easy, move up rather than repeating the same board size for speed.</li>
</ol>

<h2>Play the official game</h2>
<p>The official Meowdoku is published by Oakever Games on <a href="https://play.google.com/store/apps/details?id=com.oakever.meowdoku" rel="noopener nofollow">Google Play</a>. Our board follows the same public rules but is an independent implementation; scores and progress are separate.</p>
"""

page("practice", "Cat Territory: Free Meowdoku-Style Puzzle (Original Boards)",
     "Play an original Meowdoku-style logic puzzle in your browser: one cat per region, row and column, no touching. Unique-solution boards from 6×6 to 9×9.",
     "Cat Territory Practice Board",
     *split_lede(practice_body), app=True,
     extra_head='<script src="/puzzles.js?v=20261104c" defer></script>\n<script src="/app.js?v=20261104c" defer></script>')


# ---------------------------------------------------------------- about
about_body = """
<p class="lede">Meowdoku Guide is an independent fan project: a rules reference, a strategy guide and an original browser puzzle for a game we play. It is not the official app and has no connection to Oakever Games.</p>

<h2>Who runs this site</h2>
<p>The site is built and maintained by an independent developer as part of a small collection of free browser tools. We do not publish a personal name or a fabricated biography; the work is the site itself. If that changes, this page will say so.</p>

<h2>Editorial policy</h2>
<ul>
<li><b>Rules and store facts are sourced.</b> Game rules, platforms, price, rating and download figures are checked against the public Google Play listing on the date shown.</li>
<li><b>Our puzzles are ours.</b> Every practice board is generated for this site and verified to have exactly one solution. No Oakever level layouts, artwork, branding or assets are copied.</li>
<li><b>Guides are written from the rules.</b> Strategy pages explain deduction patterns; they do not reproduce the app’s tutorial text.</li>
<li><b>Corrections.</b> If the app changes a rule or control, the app wins; we update the page.</li>
<li><b>No fake credentials.</b> We do not claim to be the developer, an official partner or a professional puzzle organisation.</li>
</ul>

<h2>Intellectual property</h2>
<p>“Meowdoku” and the official app belong to Oakever Games. We use the name only to describe and discuss the game, with a clear non-affiliation notice on every page. The game’s rules are functional mechanics; our expression of them — text, diagrams, code and generated puzzles — is original. We do not host, embed or redistribute the official app or its assets. If the owner has a concern about this fan site, we will respond and change or remove material as appropriate.</p>

<h2>What we do not do</h2>
<ul>
<li>We do not provide the official app, APK files or mods.</li>
<li>We do not sell anything, run ads or collect accounts.</li>
<li>We do not publish Oakever’s daily puzzle answers.</li>
</ul>

<h2>Privacy</h2>
<p>See the <a href="/privacy/">privacy page</a>: no analytics, no cookies, no account, and only local browser storage for your best times.</p>
"""

page("about", "About Meowdoku Guide — Independent Fan Site",
     "About Meowdoku Guide: an independent fan project with a rules reference, strategy guide and original Cat Territory puzzle. Not affiliated with Oakever Games.",
     "About Meowdoku Guide",
     *split_lede(about_body))


# ---------------------------------------------------------------- privacy
privacy_body = """
<p class="lede">This page explains what data this website does and does not handle. The short version: no accounts, no analytics, no advertising scripts and no cookies set by us.</p>

<h2>What we collect</h2>
<p><b>Nothing that identifies you.</b> We do not run analytics, advertising pixels, social embeds or third-party scripts. There is no contact form, newsletter or login.</p>

<h2>Local storage</h2>
<p>The puzzle stores your best completion time for each board size in your browser’s <code>localStorage</code>. It never leaves your device and is not transmitted to us. Clearing browser storage deletes it.</p>

<h2>Server logs</h2>
<p>The site is served by Vercel, a static hosting provider. Like any web server, Vercel may process standard request data (IP address, user agent, requested URL, timestamp) to deliver the site and protect it from abuse. We do not receive or analyse that data in this project. See Vercel’s privacy policy for details.</p>

<h2>External links</h2>
<p>Pages link to the official app listing on Google Play. Once you follow an external link, that site’s privacy policy applies. We do not control it.</p>

<h2>Children</h2>
<p>The site is a general-audience guide and does not knowingly collect personal information from anyone, including children.</p>

<h2>Changes</h2>
<p>If this site ever adds analytics or another data-processing feature, this page will be updated first and the change date below will move.</p>

<p class="small">Last updated: 2026-11-04.</p>
"""

page("privacy", "Privacy Policy — Meowdoku Guide",
     "Meowdoku Guide privacy policy: no analytics, no cookies, no accounts. Only local best times are stored in your browser.",
     "Privacy Policy",
     *split_lede(privacy_body))


# ---------------------------------------------------------------- sitemap / config
slugs = ["", "practice", "how-to-play", "strategy", "about", "privacy"]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for s in slugs:
    sm.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (url_for(s), DATE))
sm.append("</urlset>")
open("sitemap.xml", "w", encoding="utf-8").write("\n".join(sm) + "\n")
open("robots.txt", "w", encoding="utf-8").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE)

vercel = {
    "framework": None,
    "buildCommand": None,
    "installCommand": None,
    "outputDirectory": ".",
    "cleanUrls": True,
    "headers": [{
        "source": "/(.*)",
        "headers": [
            {"key": "X-Content-Type-Options", "value": "nosniff"},
            {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
            {"key": "Content-Security-Policy",
             "value": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"}
        ]
    }]
}
open("vercel.json", "w", encoding="utf-8").write(json.dumps(vercel, indent=2) + "\n")
vi = ["*", "!index.html", "!style.css", "!app.js", "!puzzles.js", "!icon.svg",
      "!robots.txt", "!sitemap.xml", "!vercel.json"]
for s in ["practice", "how-to-play", "strategy", "about", "privacy"]:
    vi += ["!" + s, "!" + s + "/", "!" + s + "/**"]
open(".vercelignore", "w", encoding="utf-8").write("\n".join(vi) + "\n")
open(".gitignore", "w", encoding="utf-8").write("__pycache__/\n.DS_Store\n.vercel/\n")

print("built:", len(slugs), "pages,", len(PUZZLES), "puzzles")
