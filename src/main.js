import './styles.css';

const canvas = document.querySelector('#game');
const hud = {
  health: document.querySelector('#health'),
  food: document.querySelector('#food'),
  wood: document.querySelector('#wood'),
  score: document.querySelector('#score'),
  over: document.querySelector('#game-over'),
  final: document.querySelector('#final-time'),
};

const gl = canvas.getContext('webgl', { antialias: true, alpha: false });
if (!gl) throw new Error('WebGL is required to play Wildlight Survivors.');

gl.enable(gl.BLEND);
gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

gl.enable(gl.SAMPLE_COVERAGE);
gl.sampleCoverage(1, false);

const vertexShaderSource = `
attribute vec2 a_position;
attribute vec4 a_color;
uniform vec2 u_resolution;
varying vec4 v_color;
void main() {
  vec2 zeroToOne = a_position / u_resolution;
  vec2 clipSpace = zeroToOne * 2.0 - 1.0;
  gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
  v_color = a_color;
}`;

const fragmentShaderSource = `
precision mediump float;
varying vec4 v_color;
void main() { gl_FragColor = v_color; }`;

function compile(type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
  return shader;
}

const program = gl.createProgram();
gl.attachShader(program, compile(gl.VERTEX_SHADER, vertexShaderSource));
gl.attachShader(program, compile(gl.FRAGMENT_SHADER, fragmentShaderSource));
gl.linkProgram(program);
if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
gl.useProgram(program);

const positionBuffer = gl.createBuffer();
const colorBuffer = gl.createBuffer();
const positionLocation = gl.getAttribLocation(program, 'a_position');
const colorLocation = gl.getAttribLocation(program, 'a_color');
const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
let positions = [];
let colors = [];

const rand = (min, max) => Math.random() * (max - min) + min;
const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
const distance = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

const world = { width: 2600, height: 1800 };
const keys = new Set();
const mouse = { x: 0, y: 0, down: false };
const player = { x: world.width / 2, y: world.height / 2, r: 19, speed: 250, health: 100, food: 100, wood: 0, score: 0, swing: 0 };
let camera = { x: 0, y: 0 };
let elapsed = 0;
let gameOver = false;

const resources = Array.from({ length: 85 }, (_, i) => ({
  type: i % 3 === 0 ? 'berry' : 'tree',
  x: rand(80, world.width - 80),
  y: rand(80, world.height - 80),
  r: i % 3 === 0 ? 17 : rand(22, 34),
  amount: i % 3 === 0 ? 3 : 5,
}));
const enemies = Array.from({ length: 10 }, () => spawnEnemy());

function spawnEnemy() {
  const edge = Math.floor(rand(0, 4));
  return {
    x: edge === 0 ? 35 : edge === 1 ? world.width - 35 : rand(35, world.width - 35),
    y: edge === 2 ? 35 : edge === 3 ? world.height - 35 : rand(35, world.height - 35),
    r: rand(15, 24),
    speed: rand(75, 116),
    health: 2,
    hit: 0,
  };
}

addEventListener('keydown', (event) => {
  keys.add(event.key.toLowerCase());
  if (event.key.toLowerCase() === 'r' && gameOver) restart();
});
addEventListener('keyup', (event) => keys.delete(event.key.toLowerCase()));
canvas.addEventListener('mousemove', (event) => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = event.clientX - rect.left;
  mouse.y = event.clientY - rect.top;
});
canvas.addEventListener('mousedown', () => { mouse.down = true; player.swing = .18; strike(); });
canvas.addEventListener('mouseup', () => { mouse.down = false; });

function restart() {
  player.x = world.width / 2; player.y = world.height / 2; player.health = 100; player.food = 100; player.wood = 0; player.score = 0;
  enemies.splice(0, enemies.length, ...Array.from({ length: 10 }, () => spawnEnemy()));
  resources.forEach((r) => { r.amount = r.type === 'berry' ? 3 : 5; });
  elapsed = 0; gameOver = false; hud.over.hidden = true;
}

function resize() {
  const dpr = Math.min(devicePixelRatio || 1, 2);
  const width = Math.floor(innerWidth * dpr);
  const height = Math.floor(innerHeight * dpr);
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width; canvas.height = height;
  }
  gl.viewport(0, 0, canvas.width, canvas.height);
}

function addVertex(x, y, color) { positions.push(x, y); colors.push(...color); }
function addTriangle(a, b, c, color) { addVertex(a.x, a.y, color); addVertex(b.x, b.y, color); addVertex(c.x, c.y, color); }
function circle(x, y, r, color, segments = 28) {
  for (let i = 0; i < segments; i++) {
    const a = (i / segments) * Math.PI * 2;
    const b = ((i + 1) / segments) * Math.PI * 2;
    addTriangle({ x, y }, { x: x + Math.cos(a) * r, y: y + Math.sin(a) * r }, { x: x + Math.cos(b) * r, y: y + Math.sin(b) * r }, color);
  }
}
function rect(x, y, w, h, color) {
  addTriangle({ x, y }, { x: x + w, y }, { x, y: y + h }, color);
  addTriangle({ x: x + w, y }, { x: x + w, y: y + h }, { x, y: y + h }, color);
}

function worldToScreen(entity) { return { x: entity.x - camera.x, y: entity.y - camera.y }; }
function screenMouseWorld() { return { x: mouse.x + camera.x, y: mouse.y + camera.y }; }

function strike() {
  const aim = screenMouseWorld();
  const hitPoint = { x: player.x + Math.cos(Math.atan2(aim.y - player.y, aim.x - player.x)) * 58, y: player.y + Math.sin(Math.atan2(aim.y - player.y, aim.x - player.x)) * 58 };
  resources.forEach((resource) => {
    if (resource.amount > 0 && distance(resource, hitPoint) < resource.r + 36) {
      resource.amount -= 1;
      if (resource.type === 'tree') player.wood += 1;
      else player.food = clamp(player.food + 16, 0, 100);
      player.score += 5;
    }
  });
  enemies.forEach((enemy) => {
    if (distance(enemy, hitPoint) < enemy.r + 38) { enemy.health -= 1; enemy.hit = .15; player.score += 15; }
  });
}

function update(dt) {
  if (gameOver) return;
  elapsed += dt;
  player.food -= dt * 2.2;
  if (player.food <= 0) player.health -= dt * 7;
  if (player.health <= 0) {
    gameOver = true; hud.final.textContent = Math.floor(elapsed); hud.over.hidden = false; return;
  }
  let dx = 0, dy = 0;
  if (keys.has('w') || keys.has('arrowup')) dy -= 1;
  if (keys.has('s') || keys.has('arrowdown')) dy += 1;
  if (keys.has('a') || keys.has('arrowleft')) dx -= 1;
  if (keys.has('d') || keys.has('arrowright')) dx += 1;
  const mag = Math.hypot(dx, dy) || 1;
  player.x = clamp(player.x + (dx / mag) * player.speed * dt, player.r, world.width - player.r);
  player.y = clamp(player.y + (dy / mag) * player.speed * dt, player.r, world.height - player.r);
  player.swing = Math.max(0, player.swing - dt);

  const desired = 10 + Math.floor(elapsed / 18);
  while (enemies.length < desired) enemies.push(spawnEnemy());
  enemies.forEach((enemy, index) => {
    const nightBoost = 1 + Math.max(0, Math.sin(elapsed * .08)) * .55;
    const angle = Math.atan2(player.y - enemy.y, player.x - enemy.x);
    enemy.x += Math.cos(angle) * enemy.speed * nightBoost * dt;
    enemy.y += Math.sin(angle) * enemy.speed * nightBoost * dt;
    enemy.hit = Math.max(0, enemy.hit - dt);
    if (distance(enemy, player) < enemy.r + player.r) player.health -= 18 * dt;
    if (enemy.health <= 0) { enemies.splice(index, 1); player.score += 35; }
  });

  camera.x = clamp(player.x - canvas.width / 2, 0, world.width - canvas.width);
  camera.y = clamp(player.y - canvas.height / 2, 0, world.height - canvas.height);
}

function render() {
  resize();
  positions = []; colors = [];
  const night = (Math.sin(elapsed * .08) + 1) / 2;
  gl.clearColor(0.03 - night * .02, 0.09 - night * .04, 0.08 + night * .02, 1);
  gl.clear(gl.COLOR_BUFFER_BIT);

  for (let x = -camera.x % 96; x < canvas.width; x += 96) rect(x, 0, 2, canvas.height, [0.16, 0.31, 0.25, .28]);
  for (let y = -camera.y % 96; y < canvas.height; y += 96) rect(0, y, canvas.width, 2, [0.16, 0.31, 0.25, .28]);

  resources.forEach((resource) => {
    if (resource.amount <= 0) return;
    const p = worldToScreen(resource);
    if (resource.type === 'tree') {
      circle(p.x, p.y + resource.r * .3, resource.r * .45, [0.28, 0.16, 0.08, 1], 18);
      circle(p.x, p.y - resource.r * .25, resource.r, [0.12, 0.46, 0.22, 1], 30);
      circle(p.x - 9, p.y - 18, resource.r * .45, [0.2, 0.62, 0.3, .9], 18);
    } else {
      circle(p.x, p.y, resource.r, [0.12, 0.36, 0.16, 1], 22);
      circle(p.x - 6, p.y - 3, 4, [0.92, 0.18, 0.25, 1], 12);
      circle(p.x + 5, p.y + 4, 4, [0.97, 0.25, 0.36, 1], 12);
    }
  });

  enemies.forEach((enemy) => {
    const p = worldToScreen(enemy);
    circle(p.x, p.y, enemy.r + 4, [0.08, 0.02, 0.03, .35], 24);
    circle(p.x, p.y, enemy.r, enemy.hit > 0 ? [1, .72, .45, 1] : [0.67, 0.12, 0.13, 1], 26);
    circle(p.x - enemy.r * .35, p.y - enemy.r * .24, 3, [1, .9, .6, 1], 8);
  });

  const p = worldToScreen(player);
  const aim = screenMouseWorld();
  const angle = Math.atan2(aim.y - player.y, aim.x - player.x);
  circle(p.x, p.y + 6, player.r + 5, [0, 0, 0, .25], 28);
  circle(p.x, p.y, player.r, [0.27, 0.58, 0.92, 1], 32);
  circle(p.x + Math.cos(angle) * 9, p.y + Math.sin(angle) * 9, 6, [0.86, 0.96, 1, 1], 16);
  if (player.swing > 0) circle(p.x + Math.cos(angle) * 46, p.y + Math.sin(angle) * 46, 18 + player.swing * 60, [1, 0.91, 0.43, .36], 26);

  const darkness = .3 + night * .34;
  rect(0, 0, canvas.width, canvas.height, [0.01, 0.015, 0.04, darkness]);

  gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
  gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.DYNAMIC_DRAW);
  gl.enableVertexAttribArray(positionLocation);
  gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
  gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.DYNAMIC_DRAW);
  gl.enableVertexAttribArray(colorLocation);
  gl.vertexAttribPointer(colorLocation, 4, gl.FLOAT, false, 0, 0);
  gl.drawArrays(gl.TRIANGLES, 0, positions.length / 2);

  hud.health.textContent = `Health ${Math.max(0, Math.ceil(player.health))}`;
  hud.food.textContent = `Food ${Math.max(0, Math.ceil(player.food))}`;
  hud.wood.textContent = `Wood ${player.wood}`;
  hud.score.textContent = `Score ${Math.floor(player.score + elapsed)}`;
}

let last = performance.now();
function frame(now) {
  const dt = Math.min((now - last) / 1000, 1 / 20);
  last = now;
  update(dt);
  render();
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
