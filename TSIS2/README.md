# TSIS2 Paint Application

Extended Paint application using Pygame only.

## Features

- Pencil freehand drawing
- Straight line with live preview
- Rectangle and circle
- Square, right triangle, equilateral triangle, rhombus
- Eraser
- Color picker
- Brush sizes: 1, 2, 3 keys
- Flood fill tool
- Text tool
- Ctrl+S saves canvas as timestamped PNG

## Run

```bash
pip install pygame
python3 paint.py
```

## Controls

- Mouse: choose tool / draw
- 1: small brush, 2 px
- 2: medium brush, 5 px
- 3: large brush, 10 px
- Ctrl+S: save canvas
- Text tool: click canvas, type text, Enter to confirm, Escape to cancel
