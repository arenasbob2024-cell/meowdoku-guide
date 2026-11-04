/* Cat Territory practice board for the Meowdoku fan guide.
   Original implementation: our own generated puzzles, our own visuals.
   Runs entirely in the browser; no network requests. */
(function () {
  "use strict";

  var DATA = window.MEOW_PUZZLES;
  if (!DATA || !DATA.puzzles || !DATA.puzzles.length) return;

  var PALETTE = [
    "#f6d4c2", "#cfe6d4", "#c9dcf3", "#f2e3a8", "#e5d1f0",
    "#f4c9d8", "#d2e7e7", "#e9dcc7", "#d8d3f1"
  ];

  var el = {
    board: document.getElementById("board"),
    boardWrap: document.getElementById("boardWrap"),
    sizeBtns: Array.prototype.slice.call(document.querySelectorAll("[data-size]")),
    newBtn: document.getElementById("newBtn"),
    checkBtn: document.getElementById("checkBtn"),
    hintBtn: document.getElementById("hintBtn"),
    resetBtn: document.getElementById("resetBtn"),
    timer: document.getElementById("timer"),
    counter: document.getElementById("counter"),
    status: document.getElementById("status"),
    best: document.getElementById("best"),
    win: document.getElementById("winBanner"),
    winText: document.getElementById("winText")
  };
  if (!el.board) return;

  var state = {
    n: 6,
    puzzle: null,
    marks: [],
    locked: [],
    startedAt: 0,
    timerId: null,
    solved: false,
    hints: 0,
    lastId: null
  };

  function puzzlesFor(n) {
    return DATA.puzzles.filter(function (p) { return p.n === n; });
  }

  function pickPuzzle(n) {
    var pool = puzzlesFor(n);
    if (!pool.length) return null;
    var choices = pool.filter(function (p) { return p.id !== state.lastId; });
    if (!choices.length) choices = pool;
    return choices[Math.floor(Math.random() * choices.length)];
  }

  function idx(r, c) { return r * state.n + c; }

  function regionAt(r, c) { return state.puzzle.regions[r][c]; }

  function newBoard() {
    var p = pickPuzzle(state.n);
    if (!p) return;
    state.puzzle = p;
    state.lastId = p.id;
    state.n = p.n;
    state.marks = [];
    state.locked = [];
    for (var r = 0; r < state.n; r++) {
      state.marks.push(new Array(state.n).fill(0));
      state.locked.push(new Array(state.n).fill(false));
    }
    state.solved = false;
    state.hints = 0;
    state.startedAt = Date.now();
    el.win.hidden = true;
    setStatus("Tap a cell to cycle: empty → ✕ → cat → empty.", "");
    render();
    startTimer();
    updateBestLabel();
  }

  function startTimer() {
    if (state.timerId) clearInterval(state.timerId);
    state.timerId = setInterval(function () {
      if (state.solved) return;
      var s = Math.floor((Date.now() - state.startedAt) / 1000);
      el.timer.textContent = fmt(s);
    }, 500);
    el.timer.textContent = "0:00";
  }

  function fmt(s) {
    var m = Math.floor(s / 60);
    var ss = s % 60;
    return m + ":" + (ss < 10 ? "0" : "") + ss;
  }

  function setStatus(text, cls) {
    el.status.textContent = text;
    el.status.className = "status " + (cls || "");
  }

  function render() {
    var n = state.n;
    var frag = document.createDocumentFragment();
    el.board.style.gridTemplateColumns = "repeat(" + n + ", 1fr)";
    el.boardWrap.style.setProperty("--n", n);
    var firstCell = {};
    for (var r = 0; r < n; r++) {
      for (var c = 0; c < n; c++) {
        var rid = regionAt(r, c);
        if (!(rid in firstCell)) firstCell[rid] = [r, c];
      }
    }
    for (r = 0; r < n; r++) {
      for (c = 0; c < n; c++) {
        var region = regionAt(r, c);
        var cell = document.createElement("button");
        cell.type = "button";
        cell.className = "cell";
        cell.dataset.r = r;
        cell.dataset.c = c;
        cell.style.background = PALETTE[region % PALETTE.length];
        var rid = regionAt(r, c);
        var shadows = [];
        if (r === 0 || regionAt(r - 1, c) !== rid) shadows.push("inset 0 2px 0 #2a2a2a");
        if (r === n - 1 || regionAt(r + 1, c) !== rid) shadows.push("inset 0 -2px 0 #2a2a2a");
        if (c === 0 || regionAt(r, c - 1) !== rid) shadows.push("inset 2px 0 0 #2a2a2a");
        if (c === n - 1 || regionAt(r, c + 1) !== rid) shadows.push("inset -2px 0 0 #2a2a2a");
        cell.style.boxShadow = shadows.length ? shadows.join(", ") : "none";

        var mark = state.marks[r][c];
        if (mark === 2) {
          var cat = document.createElement("span");
          cat.className = "catmark";
          cat.innerHTML = CAT_SVG;
          cell.appendChild(cat);
          cell.setAttribute("aria-label", "Row " + (r + 1) + ", column " + (c + 1) + ", cat");
        } else if (mark === 1) {
          cell.textContent = "✕";
          cell.className += " xmark";
          cell.setAttribute("aria-label", "Row " + (r + 1) + ", column " + (c + 1) + ", crossed out");
        } else {
          cell.setAttribute("aria-label", "Row " + (r + 1) + ", column " + (c + 1) + ", empty");
        }
        if (state.locked[r][c]) cell.className += " locked";
        if (firstCell[region][0] === r && firstCell[region][1] === c) {
          var tag = document.createElement("span");
          tag.className = "regiontag";
          tag.textContent = String(region + 1);
          cell.appendChild(tag);
        }
        frag.appendChild(cell);
      }
    }
    el.board.innerHTML = "";
    el.board.appendChild(frag);
    updateCounter();
  }

  var CAT_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<path d="M4 10.2 4.6 4l5 3.1a9.6 9.6 0 0 1 4.8 0L19.4 4 20 10.2a8.6 8.6 0 0 1-2.6 9.2 8.9 8.9 0 0 1-10.8 0A8.6 8.6 0 0 1 4 10.2Z" fill="#2b2b33"/>' +
    '<circle cx="9.2" cy="11.6" r="1.25" fill="#fff7e8"/><circle cx="14.8" cy="11.6" r="1.25" fill="#fff7e8"/>' +
    '<path d="M10.2 15.2c.9.9 2.7.9 3.6 0" stroke="#fff7e8" stroke-width="1.15" fill="none" stroke-linecap="round"/>' +
    "</svg>";

  function updateCounter() {
    var cats = 0;
    for (var r = 0; r < state.n; r++)
      for (var c = 0; c < state.n; c++)
        if (state.marks[r][c] === 2) cats++;
    el.counter.textContent = cats + " / " + state.n + " cats placed";
  }

  function onCellClick(ev) {
    if (state.solved) return;
    var cell = ev.target.closest(".cell");
    if (!cell) return;
    var r = +cell.dataset.r, c = +cell.dataset.c;
    if (state.locked[r][c]) return;
    state.marks[r][c] = (state.marks[r][c] + 1) % 3;
    render();
    var cats = state.marks.flat().filter(function (m) { return m === 2; }).length;
    if (cats === state.n) checkBoard(true);
  }

  function findConflicts() {
    var n = state.n;
    var bad = {};
    var rows = {}, cols = {}, regs = {};
    for (var r = 0; r < n; r++) {
      for (var c = 0; c < n; c++) {
        if (state.marks[r][c] !== 2) continue;
        (rows[r] = rows[r] || []).push([r, c]);
        (cols[c] = cols[c] || []).push([r, c]);
        var g = regionAt(r, c);
        (regs[g] = regs[g] || []).push([r, c]);
      }
    }
    function flag(list) {
      if (list && list.length > 1) list.forEach(function (p) { bad[p[0] + "," + p[1]] = true; });
    }
    Object.keys(rows).forEach(function (k) { flag(rows[k]); });
    Object.keys(cols).forEach(function (k) { flag(cols[k]); });
    Object.keys(regs).forEach(function (k) { flag(regs[k]); });
    for (r = 0; r < n; r++) {
      for (c = 0; c < n; c++) {
        if (state.marks[r][c] !== 2) continue;
        for (var dr = -1; dr <= 1; dr++) {
          for (var dc = -1; dc <= 1; dc++) {
            if (!dr && !dc) continue;
            var rr = r + dr, cc = c + dc;
            if (rr >= 0 && rr < n && cc >= 0 && cc < n && state.marks[rr][cc] === 2) {
              bad[r + "," + c] = true;
              bad[rr + "," + cc] = true;
            }
          }
        }
      }
    }
    return bad;
  }

  function checkBoard(auto) {
    var bad = findConflicts();
    var cells = el.board.querySelectorAll(".cell");
    cells.forEach(function (cell) {
      var key = cell.dataset.r + "," + cell.dataset.c;
      cell.classList.toggle("conflict", !!bad[key]);
    });
    var cats = state.marks.flat().filter(function (m) { return m === 2; }).length;
    if (Object.keys(bad).length) {
      setStatus("Conflict: " + Object.keys(bad).length + " cats break a rule (red cells).", "bad");
      return false;
    }
    if (cats === state.n) {
      win();
      return true;
    }
    if (!auto) setStatus(cats + " of " + state.n + " cats placed — no conflicts so far.", "good");
    return false;
  }

  function win() {
    state.solved = true;
    if (state.timerId) clearInterval(state.timerId);
    var secs = Math.floor((Date.now() - state.startedAt) / 1000);
    el.win.hidden = false;
    var bestKey = "meow_best_" + state.n;
    var best = 0;
    try { best = parseInt(localStorage.getItem(bestKey) || "0", 10) || 0; } catch (e) {}
    var record = !best || secs < best;
    if (record) {
      try { localStorage.setItem(bestKey, String(secs)); } catch (e) {}
    }
    el.winText.textContent = "Solved " + state.n + "×" + state.n + " in " + fmt(secs) +
      (state.hints ? " with " + state.hints + " hint" + (state.hints > 1 ? "s" : "") : "") +
      (record ? " — a new personal best!" : ". Best: " + fmt(best));
    setStatus("Puzzle solved.", "good");
    updateBestLabel();
  }

  function updateBestLabel() {
    var best = 0;
    try { best = parseInt(localStorage.getItem("meow_best_" + state.n) || "0", 10) || 0; } catch (e) {}
    el.best.textContent = best ? "Your best on " + state.n + "×" + state.n + ": " + fmt(best) : "";
  }

  function hint() {
    if (state.solved) return;
    var n = state.n;
    var sol = state.puzzle.solution;
    var open = [];
    for (var r = 0; r < n; r++) {
      var c = sol[r];
      if (state.marks[r][c] !== 2) open.push([r, c]);
    }
    if (!open.length) { checkBoard(false); return; }
    var pick = open[Math.floor(Math.random() * open.length)];
    var hr = pick[0], hc = pick[1];
    // Remove cats that would conflict with the revealed answer.
    for (r = 0; r < n; r++) {
      for (c = 0; c < n; c++) {
        if (state.marks[r][c] !== 2 || (r === hr && c === hc)) continue;
        var sameRegion = regionAt(r, c) === regionAt(hr, hc);
        var touching = Math.abs(r - hr) <= 1 && Math.abs(c - hc) <= 1;
        if (r === hr || c === hc || sameRegion || touching) {
          state.marks[r][c] = 0;
        }
      }
    }
    state.marks[hr][hc] = 2;
    state.locked[hr][hc] = true;
    state.hints++;
    render();
    setStatus("Hint placed at row " + (hr + 1) + ", column " + (hc + 1) + " (locked).", "good");
  }

  function resetMarks() {
    if (state.solved) return;
    for (var r = 0; r < state.n; r++)
      for (var c = 0; c < state.n; c++)
        if (!state.locked[r][c]) state.marks[r][c] = 0;
    render();
    setStatus("Marks cleared. Locked hint cells stay.", "");
  }

  el.board.addEventListener("click", onCellClick);
  el.newBtn.addEventListener("click", newBoard);
  el.checkBtn.addEventListener("click", function () { checkBoard(false); });
  el.hintBtn.addEventListener("click", hint);
  el.resetBtn.addEventListener("click", resetMarks);
  el.sizeBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      state.n = parseInt(btn.dataset.size, 10);
      el.sizeBtns.forEach(function (b) { b.classList.toggle("active", b === btn); });
      newBoard();
    });
  });

  // Start on 6x6.
  el.sizeBtns.forEach(function (b) { b.classList.toggle("active", b.dataset.size === "6"); });
  newBoard();
})();
