# Wildlight Survivors

A from-scratch 2D survival game rendered with WebGL. Explore the wild, gather wood and berries, fight off creatures, and survive the night cycle as long as possible.

## Controls

- **WASD / Arrow keys**: Move
- **Mouse**: Aim
- **Click**: Strike, gather resources, and fight enemies
- **R**: Restart after game over

## Rendering

The game uses a WebGL canvas with anti-aliasing enabled through the context options. The main loop is driven by `requestAnimationFrame`, allowing the browser to synchronize rendering for smooth 60fps animation on capable displays.

## Run locally

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```
