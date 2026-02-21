/**
 * Ghost Cursor Effect
 * Adds a trailing cursor follower using spring physics/lerp.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Create the ghost element
    const ghost = document.createElement("div");
    ghost.classList.add("ghost-cursor");
    document.body.appendChild(ghost);

    let mouseX = 0;
    let mouseY = 0;
    let ghostX = 0;
    let ghostY = 0;

    // Configuration
    const speed = 0.15; // 0.1 to 1.0 (lower is smoother/slower)

    // Track mouse
    document.addEventListener("mousemove", (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Animation Loop
    function animate() {
        // Linear Interpolation (Lerp) for smooth following
        ghostX += (mouseX - ghostX) * speed;
        ghostY += (mouseY - ghostY) * speed;

        ghost.style.transform = `translate(${ghostX}px, ${ghostY}px)`;

        requestAnimationFrame(animate);
    }

    animate();
});
