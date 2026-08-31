# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Vanilla-JS Tetris (HTML5 Canvas). No package.json, no bundler, no transpiler, no tests, no dependencies. Three source files: `index.html`, `style.css`, `game.js`. UI text and README are in Spanish.

## Running

Open `index.html` directly (`start index.html` on Windows) or serve statically (`python3 -m http.server 8000`, `npx serve .`). There is no build, lint, or test command — verifying a change means loading the page in a browser and playing.

## Architecture (`game.js`)

Single IIFE-less script in strict mode with module-level mutable state (`board`, `current`, `next`, `score`, `lines`, `level`, `paused`, `gameOver`, `dropAccum`, `dropInterval`, `animId`). `init()` resets all of it and is also the restart-button handler; it runs at the bottom of the file on load.

Key invariants worth knowing before editing:

- **Board** is `ROWS × COLS` of `0` (empty) or a color index `1–7`. That index is both the piece type and the index into `COLORS` and `PIECES` — the shape matrices are filled with their own type number, so merging a piece into the board preserves its color for free. Adding a piece means adding entries to *both* arrays at the same index.
- **Rotation** is a fresh matrix from `rotateCW` (transpose + reverse); `tryRotate` applies wall kicks by trying x-offsets `[0,-1,1,-2,2]` and keeps the first that doesn't collide. Not SRS — no kick tables, no rotation-state tracking.
- **`collide(shape, ox, oy)`** reads the module-level `board` but takes the candidate position as arguments; all movement code is "test then commit", never move-then-undo. `ny < 0` is allowed (spawn above the top) — only `ny >= ROWS` and horizontal bounds fail.
- **Game loop** (`loop`) accumulates `dt` into `dropAccum` and drops one row when it exceeds `dropInterval`, then redraws the whole canvas every frame (grid, board, ghost, current piece). Pause/game-over work by `cancelAnimationFrame(animId)`; resuming must reset `lastTime` to `performance.now()` or the first `dt` will be huge.
- **`clearLines`** splices completed rows and unshifts empty ones, incrementing `r` after a removal to re-check the same index. It also owns level/speed progression: `level = floor(lines/10)+1`, `dropInterval = max(100, 1000 - (level-1)*90)`.
- **`lockPiece`** = merge → clearLines → spawn. `spawn()` promotes `next` to `current`, generates a new `next`, and calls `endGame()` if the new piece already collides.
- **Drawing** goes through `drawBlock(context, x, y, colorIndex, size, alpha)`, shared by the main canvas and the NEXT preview — the preview passes `nextCtx` and centers the shape in a 4×4 grid.

Canvas dimensions are hardcoded in `index.html` (`300 × 600`). Changing `COLS`, `ROWS`, or `BLOCK` in `game.js` requires updating the `<canvas id="board">` `width`/`height` to match `COLS*BLOCK × ROWS*BLOCK`.

Input is one `keydown` listener on `document`; `KeyP` is handled before the paused/gameOver guard so pause can be toggled off. `Space` calls `preventDefault()` to stop page scroll.
