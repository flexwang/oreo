# Oreo

A floating desktop cat companion. Oreo walks back and forth across your screen and stretches when you click.

## Run

```bash
make          # with meow sound when Oreo stretches
make quiet    # silent
```

This creates a virtual environment, installs dependencies, and starts the app.

Click Oreo (or right-click → "Pet Oreo") to trigger a stretch. Drag to move.

Right-click for more options:

- **Pet Oreo** — trigger a stretch
- **Zoom In +** / **Zoom Out -** — resize Oreo (remembered across launches)
- **Reset** — restore default size
- **Quit** — exit the app

## Run in background with tmux

Start a detached tmux session so you don't need to keep a terminal open:

```bash
tmux new-session -d -s oreo 'make'
```

To reattach later:

```bash
tmux attach -t oreo
```

To stop:

```bash
tmux kill-session -t oreo
```
