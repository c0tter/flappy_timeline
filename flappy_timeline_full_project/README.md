# Flappy — Feature Timeline (Ultra Clean)

Folders
- assets/images/  → put your `background-day.png` here (optional)
- assets/fonts/   → put your `.ttf` fonts here (e.g., Inter-Bold.ttf)
- text/           → `textN_top.txt` and `textN_bottom.txt` pairs

Run
```bash
pip install pygame
python3 flappy_text_files_ultra.py
```

Controls
- Space / Up / Click: Flap
- R: Restart
- L: Reload text files (hot reload from ./text)
- Esc: Quit

Fonts
- Script auto-detects the first `.ttf` in `assets/fonts/` (prefers Inter-Bold.ttf if present).
- If you add both Inter-Bold.ttf and Inter-Regular.ttf, Inter-Regular will be used for milestones.

Text Files
- Create numbered pairs: `text1_top.txt` + `text1_bottom.txt`, `text2_top.txt` + `text2_bottom.txt`, ...
- Headings are uppercased automatically; milestones are sentence-cased.
