# Flappy Timeline — Synthesia Feature History

## 📖 Overview
This project is a playful re-imagining of **Flappy Bird**, rebuilt in Python with **Pygame**, where instead of dodging plain green pipes, you fly through a **timeline of Synthesia’s key feature releases**.

Each pipe pair represents a **date** (top) and a **milestone** (bottom).  
By playing the game, you progress through the **history of Synthesia’s product evolution** — from the company’s founding in 2017 through to the launch of Synthesia 3.0 in 2025.

---

## 🕹 Features
- **Timeline Pipes**:  
  - Top pipe shows a **date**.  
  - Bottom pipe shows a **feature or milestone**.  
- **Custom Assets**:  
  - Replace `assets/images/bird.png` with your own sprite.  
  - Replace `assets/images/background-day.png` with any background.  
- **Text Files for Content**:  
  - `text/textN_top.txt` → Date or Heading  
  - `text/textN_bottom.txt` → Event or Feature  
- **Fonts**:  
  - Drop any `.ttf` font into `assets/fonts/` and the game will auto-detect it.  
- **Simple Controls**:  
  - `Space` / `↑` / Mouse click = Flap  
  - `R` = Restart  
  - `L` = Reload text files on the fly  
  - `Esc` = Quit  

---

## 📂 Project Structure
