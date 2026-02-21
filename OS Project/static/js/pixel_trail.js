/**
 * Pixel Trail Background
 * Inspired by ReactBits
 * a grid of squares that light up and fade.
 */

const canvas = document.getElementById('pixelCanvas');
const ctx = canvas.getContext('2d');

let pixelSize = 40; // Size of grid squares
let grid = [];
let mouseX = -100;
let mouseY = -100;

// Resize
window.addEventListener('resize', () => {
    resize();
});

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    initGrid();
}

// Mouse
window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

class Pixel {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.alpha = 0;
        this.targetAlpha = 0;
    }

    update() {
        // Distance to mouse
        const dx = mouseX - (this.x + pixelSize / 2);
        const dy = mouseY - (this.y + pixelSize / 2);
        const dist = Math.sqrt(dx * dx + dy * dy);

        // Activate if mouse is close
        if (dist < 100) {
            this.targetAlpha = 1; // Fully lit
        } else {
            this.targetAlpha = 0; // Fade out
        }

        // Smooth fading (Lerp)
        // Fade in fast, fade out slow
        if (this.targetAlpha > this.alpha) {
            this.alpha += (this.targetAlpha - this.alpha) * 0.2;
        } else {
            this.alpha += (this.targetAlpha - this.alpha) * 0.05;
        }

        this.draw();
    }

    draw() {
        if (this.alpha > 0.01) {
            ctx.fillStyle = `rgba(79, 70, 229, ${this.alpha * 0.4})`; // Indigo, max 0.4 opacity
            ctx.fillRect(this.x, this.y, pixelSize - 1, pixelSize - 1); // -1 for grid gap effect
        }
    }
}

function initGrid() {
    grid = [];
    const cols = Math.ceil(canvas.width / pixelSize);
    const rows = Math.ceil(canvas.height / pixelSize);

    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            grid.push(new Pixel(c * pixelSize, r * pixelSize));
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Optional: Draw faint grid lines always? 
    // Let's keep it clean: only draw active pixels.

    for (let p of grid) {
        p.update();
    }

    requestAnimationFrame(animate);
}

// Start
resize();
animate();
