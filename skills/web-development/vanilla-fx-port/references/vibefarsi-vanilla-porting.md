# VibeFarsi to Vanilla Porting Guide (Cloudflare Workers, Dashboards & Static HTML)

When the user asks for VibeFarsi components in non-React environments (such as Cloudflare Workers SPAs, embedded HTML pages, or static dashboards), do not fall back to generic flat UI. Port the core VibeFarsi interaction physics and CSS keyframes directly.

## 1. TiltCard (3D Perspective Hover)
Simulate cursor physics without external libraries:
```css
.vibe-tilt-card {
    transform-style: preserve-3d;
    transition: transform 0.15s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.2s ease, box-shadow 0.2s ease;
    will-change: transform;
}
```
```javascript
function initTiltCards() {
    document.querySelectorAll('.vibe-tilt-card').forEach(card => {
        if (card.dataset.tiltInit) return;
        card.dataset.tiltInit = 'true';
        card.addEventListener('mousemove', e => {
            const r = card.getBoundingClientRect();
            const px = (e.clientX - r.left) / r.width - 0.5;
            const py = (e.clientY - r.top) / r.height - 0.5;
            card.style.transform = `perspective(800px) rotateX(${py * -10}deg) rotateY(${px * 10}deg) translateY(-2px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) translateY(0)';
        });
    });
}
```

## 2. SpotlightCard (Pointer-Following Radial Glow)
Dynamic radial illumination that follows the cursor:
```css
.vibe-spotlight-card {
    position: relative;
    overflow: hidden;
}
.vibe-spotlight-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(220px circle at var(--spotlight-x, -200px) var(--spotlight-y, -200px), rgba(139, 92, 246, 0.18), transparent 70%);
    pointer-events: none;
    border-radius: inherit;
    transition: opacity 0.2s ease;
    z-index: 1;
}
```
```javascript
function initSpotlightCards() {
    document.querySelectorAll('.vibe-spotlight-card').forEach(card => {
        if (card.dataset.spotlightInit) return;
        card.dataset.spotlightInit = 'true';
        card.addEventListener('mousemove', e => {
            const r = card.getBoundingClientRect();
            card.style.setProperty('--spotlight-x', `${e.clientX - r.left}px`);
            card.style.setProperty('--spotlight-y', `${e.clientY - r.top}px`);
        });
        card.addEventListener('mouseleave', () => {
            card.style.setProperty('--spotlight-x', '-200px');
            card.style.setProperty('--spotlight-y', '-200px');
        });
    });
}
```

## 3. BorderBeam (Continuous 360° Conic Light Beam)
```css
@property --beam-angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}
@keyframes beam {
    0% { --beam-angle: 0deg; }
    100% { --beam-angle: 360deg; }
}
.vibe-border-beam {
    position: relative;
    overflow: hidden;
    padding: 1px;
    border-radius: 20px;
}
.vibe-border-beam::before {
    content: '';
    position: absolute;
    inset: -100%;
    background: conic-gradient(from var(--beam-angle, 0deg), transparent 0 78%, var(--primary, #8b5cf6) 92%, transparent 100%);
    animation: beam 4s linear infinite;
    pointer-events: none;
}
```

## 4. ShineButton (Shimmer Sweep on CTAs)
```css
@keyframes shine {
    0% { transform: translateX(100%); }
    50%, 100% { transform: translateX(-100%); }
}
.btn-shine {
    position: relative;
    overflow: hidden;
}
.btn-shine::after {
    content: '';
    position: absolute;
    inset: 0;
    width: 40%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
    animation: shine 3s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    pointer-events: none;
}
```

## 5. Meteors & RetroGrid (Backdrop Atmosphere)
```css
@keyframes meteor {
    0% { transform: rotate(215deg) translateX(0); opacity: 1; }
    70% { opacity: 1; }
    100% { transform: rotate(215deg) translateX(-500px); opacity: 0; }
}
.vibe-retro-grid {
    position: absolute;
    inset: 0;
    background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
    background-size: 36px 36px;
    mask-image: radial-gradient(ellipse at 50% 0%, #000 60%, transparent 95%);
    -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 60%, transparent 95%);
    pointer-events: none;
}
```
