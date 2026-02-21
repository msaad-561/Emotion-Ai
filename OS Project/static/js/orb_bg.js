/**
 * Orb Background - Mouse Parallax Only
 * Pure CSS handles the floating animation.
 * JS only adds the mouse parallax effect.
 */
(function () {
    const container = document.getElementById('orb-container');
    if (!container) return;

    const orbs = container.querySelectorAll('.orb');
    if (!orbs.length) return;

    let mouseX = 0, mouseY = 0;
    let currentX = 0, currentY = 0;
    let rafId;

    document.addEventListener('mousemove', (e) => {
        // Normalize to -1..1 from center
        mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
        mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    function animate() {
        currentX = lerp(currentX, mouseX, 0.03);
        currentY = lerp(currentY, mouseY, 0.03);

        orbs.forEach((orb, i) => {
            const strength = (i + 1) * 25; // 25px, 50px, 75px
            const tx = currentX * strength;
            const ty = currentY * strength;
            orb.style.transform = `translate(calc(-50% + ${tx}px), calc(-50% + ${ty}px))`;
        });

        rafId = requestAnimationFrame(animate);
    }

    animate();
})();
