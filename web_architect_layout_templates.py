"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: TASTESKILL LAYOUT ARCHITECTURE ENGINE
===================================================================
Implements human-caliber, domain-adaptive page layouts matching
the Top Claude Web Design Skills (Frontend Design, TasteSkill, UI/UX Pro Max):
- Bans cookie-cutter monolithic layouts (different domains get distinct architectures).
- Fitness: Aggressive skewed athletic arena with weekly WOD schedule & 1RM calculator.
- Culinary: Elegant editorial tasting room with roast spectrum & pour-over brew calculator.
- Automotive: Wide telemetry cockpit with live powertrain specs & aero configurator.
- Business: Asymmetric Swiss Bento Grid with FIX ticker tape & compound yield simulator.
- Quantum: Sovereign terminal workstation with interactive neural command deck.
"""

from typing import Dict, Any


def get_common_scripts(threejs_scene_code: str) -> str:
    """Returns the common Web Audio Synthesizer and Three.js initialization scripts."""
    return f"""
    // --- Studio-Grade Web Audio Synthesizer (Zero External Dependencies) ---
    let audioCtx = null;
    let audioEnabled = true;

    function initAudio() {{
      if (!audioCtx) {{
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) audioCtx = new AudioContext();
      }}
      if (audioCtx && audioCtx.state === 'suspended') {{
        audioCtx.resume();
      }}
    }}

    function playSpatialTone(freq = 520, type = 'sine', duration = 0.22) {{
      if (!audioEnabled) return;
      initAudio();
      if (!audioCtx) return;
      try {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch (e) {{}}
    }}

    window.toggleAudioFX = function(btn) {{
      initAudio();
      audioEnabled = !audioEnabled;
      if (btn) {{
        btn.textContent = audioEnabled ? '🔊 Audio: On' : '🔇 Audio: Muted';
        btn.classList.toggle('active', audioEnabled);
      }}
      if (audioEnabled) playSpatialTone(660, 'sine', 0.2);
    }};

    // --- 3D WebGL Three.js Spatial Engine with OrbitControls ---
    (function initThreeScene() {{
      const container = document.getElementById('webgl-canvas-container');
      if (!container || typeof THREE === 'undefined') return;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
      camera.position.set(0, 0, 4.8);

      const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      let controls = null;
      if (typeof THREE.OrbitControls !== 'undefined') {{
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 1.3;
        controls.maxDistance = 8.5;
        controls.minDistance = 2.0;
        controls.enablePan = false;
      }}

      {threejs_scene_code}

      // Responsive Resizing
      window.addEventListener('resize', () => {{
        if (!container || !renderer || !camera) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      }});

      // Animation Loop
      let clock = new THREE.Clock();
      function animate() {{
        requestAnimationFrame(animate);
        const time = clock.getElapsedTime() * 1000;
        const delta = clock.getDelta();
        if (controls) controls.update();
        if (typeof updateSceneAnimation === 'function') {{
          updateSceneAnimation(time, 1.0);
        }}
        renderer.render(scene, camera);
      }}
      animate();
    }})();

    // --- Stereoscopic CSS 3D Parallax Tilt Physics ---
    document.querySelectorAll('.tilt-card, .feature-card, .price-card').forEach(card => {{
      card.addEventListener('mousemove', e => {{
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const rotateX = ((y - centerY) / centerY) * -10;
        const rotateY = ((x - centerX) / centerX) * 10;
        card.style.transform = `perspective(1000px) rotateX(${{rotateX}}deg) rotateY(${{rotateY}}deg) translateZ(10px)`;
      }});
      card.addEventListener('mouseleave', () => {{
        card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
      }});
    }});
    """


# ===================================================================
# 1. BESPOKE FITNESS / ATHLETIC PERFORMANCE / CROSSFIT ARENA
# ===================================================================
def build_fitness_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Next-Gen Athletic Arena & Kinetic 3D Experience</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;0,700;0,800;0,900;1,700&family=Syne:wght@700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@700;800&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #070709;
      --surface: #121216;
      --surface-elevated: #1a1a22;
      --surface-glass: rgba(18, 18, 22, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(249, 115, 22, 0.6);
      --orange: #f97316;
      --orange-glow: rgba(249, 115, 22, 0.45);
      --crimson: #ef4444;
      --crimson-glow: rgba(239, 68, 68, 0.4);
      --emerald: #10b981;
      --text: #fafafa;
      --text-muted: #a1a1aa;
      --font-display: 'Syne', sans-serif;
      --font-athletic: 'Barlow Condensed', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --font-body: 'Plus Jakarta Sans', sans-serif;
      --transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: var(--font-body); background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.6; }}

    /* Ambient athletic aura */
    .glow-1 {{
      position: fixed; width: 750px; height: 750px; border-radius: 50%;
      background: radial-gradient(circle, var(--orange-glow) 0%, rgba(0,0,0,0) 70%);
      top: -220px; left: -160px; z-index: -1; pointer-events: none; filter: blur(100px);
    }}
    .glow-2 {{
      position: fixed; width: 680px; height: 680px; border-radius: 50%;
      background: radial-gradient(circle, var(--crimson-glow) 0%, rgba(0,0,0,0) 70%);
      bottom: -160px; right: -160px; z-index: -1; pointer-events: none; filter: blur(100px);
    }}

    /* Navigation */
    nav {{
      position: sticky; top: 0; z-index: 100;
      backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
      background: rgba(7, 7, 9, 0.92);
      border-bottom: 1px solid var(--border);
      padding: 16px 40px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{
      display: flex; align-items: center; gap: 12px; font-family: var(--font-athletic);
      font-size: 1.65rem; font-weight: 900; color: #fff; text-decoration: none;
      letter-spacing: 0.5px; text-transform: uppercase;
    }}
    .brand-flame {{
      width: 40px; height: 40px; border-radius: 8px;
      background: linear-gradient(135deg, var(--orange), var(--crimson));
      display: flex; align-items: center; justify-content: center; font-size: 1.4rem;
      box-shadow: 0 0 24px var(--orange-glow);
    }}
    .nav-links {{ display: flex; gap: 32px; list-style: none; align-items: center; }}
    .nav-links a {{
      color: var(--text-muted); text-decoration: none; font-size: 0.95rem; font-weight: 600;
      text-transform: uppercase; letter-spacing: 0.5px; transition: var(--transition);
    }}
    .nav-links a:hover {{ color: var(--orange); }}
    .nav-cta {{
      background: linear-gradient(135deg, var(--orange), var(--crimson));
      color: #fff !important; padding: 10px 24px; border-radius: 6px;
      font-weight: 800 !important; font-family: var(--font-athletic); font-size: 1.15rem !important;
      letter-spacing: 1px; transform: skewX(-8deg); display: inline-block;
      box-shadow: 0 0 25px var(--orange-glow);
    }}
    .nav-cta span {{ display: inline-block; transform: skewX(8deg); }}

    /* Athletic Hero */
    .hero-arena {{
      display: grid; grid-template-columns: 1fr 1.05fr; gap: 40px;
      padding: 60px 48px; max-width: 1520px; margin: 0 auto; align-items: center;
      min-height: calc(90vh - 80px);
    }}
    .skew-tag {{
      display: inline-block; transform: skewX(-8deg); background: rgba(249, 115, 22, 0.15);
      border: 1px solid var(--orange); padding: 6px 16px; border-radius: 4px;
      font-family: var(--font-athletic); font-size: 1.05rem; font-weight: 800;
      color: var(--orange); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;
    }}
    .skew-tag span {{ display: inline-block; transform: skewX(8deg); }}
    .hero-arena h1 {{
      font-family: var(--font-display); font-size: clamp(2.8rem, 5vw, 4.4rem);
      font-weight: 900; line-height: 1.04; letter-spacing: -1px; text-transform: uppercase;
      margin-bottom: 22px;
    }}
    .gradient-fire {{
      background: linear-gradient(135deg, #fff 15%, var(--orange) 60%, var(--crimson) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .hero-arena p {{
      font-size: 1.12rem; color: var(--text-muted); max-width: 540px; margin-bottom: 32px;
    }}
    .hero-btns {{ display: flex; gap: 18px; align-items: center; }}
    .btn-fire {{
      background: linear-gradient(135deg, var(--orange), var(--crimson));
      color: #fff; padding: 16px 36px; border-radius: 6px; font-family: var(--font-athletic);
      font-size: 1.3rem; font-weight: 800; letter-spacing: 1px; text-decoration: none;
      text-transform: uppercase; transform: skewX(-8deg); box-shadow: 0 0 30px var(--orange-glow);
      transition: var(--transition); display: inline-block; cursor: pointer; border: none;
    }}
    .btn-fire span {{ display: inline-block; transform: skewX(8deg); }}
    .btn-fire:hover {{ transform: skewX(-8deg) translateY(-2px); box-shadow: 0 0 45px var(--orange); }}
    .btn-outline {{
      border: 1px solid var(--border); color: #fff; padding: 15px 30px; border-radius: 6px;
      font-family: var(--font-athletic); font-size: 1.2rem; font-weight: 700; text-decoration: none;
      text-transform: uppercase; transition: var(--transition); cursor: pointer; background: transparent;
    }}
    .btn-outline:hover {{ border-color: var(--orange); color: var(--orange); }}

    /* Advanced 3D Barbell Viewport */
    .viewport-box {{
      position: relative; height: 530px; border-radius: 18px;
      background: radial-gradient(circle at 50% 50%, #1a1a24 0%, #0d0d12 100%);
      border: 1px solid var(--border-accent); overflow: hidden;
      box-shadow: 0 25px 70px rgba(0,0,0,0.7), inset 0 0 50px rgba(249, 115, 22, 0.12);
      transition: transform 0.08s ease;
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .hud-controls-bar {{
      position: absolute; top: 12px; left: 14px; right: 14px;
      display: flex; flex-direction: column; gap: 8px; z-index: 10;
    }}
    .hud-row-top, .hud-row-bottom {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }}
    .weight-pills, .hud-action-btns, .lift-pills, .camera-pills {{ display: flex; gap: 5px; }}
    .weight-btn, .action-hud-btn, .lift-btn, .cam-btn {{
      background: rgba(18, 18, 24, 0.88); border: 1px solid var(--border);
      color: #fff; padding: 5px 11px; border-radius: 4px; font-family: var(--font-athletic);
      font-size: 0.88rem; font-weight: 800; cursor: pointer; transition: var(--transition);
      text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .weight-btn:hover, .weight-btn.active {{
      background: var(--orange); color: #000; border-color: var(--orange);
      box-shadow: 0 0 16px var(--orange-glow);
    }}
    .action-hud-btn:hover, .action-hud-btn.active {{
      border-color: var(--orange); color: var(--orange);
    }}
    .lift-btn:hover, .lift-btn.active {{
      background: var(--crimson); color: #fff; border-color: var(--crimson);
      box-shadow: 0 0 16px var(--crimson-glow);
    }}
    .cam-btn:hover, .cam-btn.active {{
      background: #3b82f6; color: #fff; border-color: #3b82f6;
      box-shadow: 0 0 16px rgba(59, 130, 246, 0.45);
    }}
    .hud-footer {{
      position: absolute; bottom: 12px; left: 14px; right: 14px; z-index: 10;
      display: flex; justify-content: space-between; align-items: flex-end; pointer-events: none;
      flex-wrap: wrap; gap: 8px;
    }}
    .hud-caption {{
      background: rgba(9, 9, 12, 0.92); backdrop-filter: blur(14px);
      border: 1px solid var(--border); border-radius: 6px; padding: 8px 14px;
      font-family: var(--font-athletic); text-transform: uppercase;
    }}
    .hud-caption-title {{ font-size: 0.82rem; color: var(--text-muted); font-weight: 700; }}
    .hud-caption-val {{ font-size: 1.15rem; color: #fff; font-weight: 900; }}
    .hud-telemetry-pill {{
      background: rgba(7, 7, 10, 0.92); border: 1px solid var(--border-accent);
      padding: 8px 14px; border-radius: 6px; font-family: var(--font-mono);
      font-size: 0.82rem; color: var(--orange); display: flex; gap: 14px; pointer-events: none;
      box-shadow: 0 0 20px rgba(0,0,0,0.8);
    }}

    /* ADVANCED COMPONENT 3: 5-Axis Spider Radar Matrix */
    .radar-container-card {{
      background: linear-gradient(135deg, #0e0e13 0%, #16161f 100%);
      border: 1px solid var(--border-accent); border-radius: 18px; padding: 40px;
      display: grid; grid-template-columns: 1fr 1.1fr; gap: 40px; align-items: center;
      box-shadow: 0 25px 70px rgba(0,0,0,0.6); margin-bottom: 100px;
    }}
    .radar-canvas-side {{
      display: flex; justify-content: center; align-items: center;
      background: #060608; border: 1px solid #27272a; border-radius: 14px; padding: 20px;
    }}
    .aci-header {{
      display: flex; justify-content: space-between; align-items: center;
      padding-bottom: 20px; border-bottom: 1px solid var(--border); margin-bottom: 20px;
    }}
    .aci-score-title {{ font-family: var(--font-athletic); font-size: 1.15rem; font-weight: 800; color: var(--text-muted); text-transform: uppercase; }}
    .aci-score-big {{ font-family: var(--font-mono); font-size: 3.6rem; font-weight: 900; color: var(--orange); line-height: 1; text-shadow: 0 0 25px var(--orange-glow); }}
    .aci-score-big span {{ font-size: 1.3rem; color: var(--text-muted); font-weight: 600; }}
    .aci-tier-badge {{
      background: linear-gradient(135deg, var(--orange), var(--crimson)); color: #fff;
      font-family: var(--font-athletic); font-size: 1.1rem; font-weight: 900;
      padding: 6px 16px; border-radius: 4px; text-transform: uppercase; transform: skewX(-8deg);
      box-shadow: 0 0 20px var(--orange-glow);
    }}
    .radar-sliders {{ display: flex; flex-direction: column; gap: 14px; }}
    .rslider-row {{ display: flex; flex-direction: column; gap: 4px; }}
    .rslider-lbl {{ display: flex; justify-content: space-between; font-family: var(--font-athletic); font-size: 0.98rem; font-weight: 800; text-transform: uppercase; }}
    .rslider-lbl span {{ color: var(--orange); font-family: var(--font-mono); }}

    /* ADVANCED COMPONENT 4: Neural WOD Protocol Synthesizer */
    .synth-card {{
      background: #0c0c10; border: 1px solid var(--border-accent); border-radius: 18px;
      padding: 36px; box-shadow: 0 20px 60px rgba(0,0,0,0.6); margin-bottom: 100px;
    }}
    .synth-top-bar {{
      display: flex; justify-content: space-between; align-items: flex-end;
      flex-wrap: wrap; gap: 20px; margin-bottom: 28px;
    }}
    .synth-selectors {{ display: flex; gap: 24px; flex-wrap: wrap; }}
    .synth-group label {{ display: block; font-family: var(--font-athletic); font-size: 1rem; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; color: var(--text-muted); }}
    .synth-pills {{ display: flex; gap: 6px; flex-wrap: wrap; }}
    .synth-pill {{
      background: var(--surface); border: 1px solid var(--border); color: #fff;
      padding: 7px 14px; border-radius: 4px; font-family: var(--font-athletic);
      font-size: 0.95rem; font-weight: 800; text-transform: uppercase; cursor: pointer; transition: var(--transition);
    }}
    .synth-pill.active {{ background: var(--orange); color: #000; border-color: var(--orange); box-shadow: 0 0 15px var(--orange-glow); }}
    .synth-output-box {{
      background: #050507; border: 1px solid #27272a; border-radius: 12px; padding: 28px;
    }}
    .synth-output-header {{
      display: flex; justify-content: space-between; align-items: center;
      padding-bottom: 18px; border-bottom: 1px solid var(--border); margin-bottom: 20px;
    }}
    .synth-title {{ font-family: var(--font-display); font-size: 1.4rem; font-weight: 900; color: #fff; text-transform: uppercase; }}
    .synth-sub {{ font-size: 0.9rem; color: var(--text-muted); margin-top: 4px; font-family: var(--font-mono); }}
    .synth-body-grid {{ display: grid; grid-template-columns: 1fr 1.3fr 1fr; gap: 20px; }}
    .synth-col {{ background: #0c0c11; border: 1px solid var(--border); border-radius: 8px; padding: 20px; }}
    .synth-col.highlight {{ border-color: var(--orange); background: linear-gradient(180deg, rgba(249, 115, 22, 0.1) 0%, #0c0c11 100%); }}
    .scol-head {{ font-family: var(--font-athletic); font-size: 1.1rem; font-weight: 900; color: var(--orange); text-transform: uppercase; margin-bottom: 12px; }}
    .synth-col ul {{ list-style: none; }}
    .synth-col li {{ font-size: 0.92rem; color: var(--text); padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.04); }}
    .synth-col li::before {{ content: "⚡ "; color: var(--orange); }}

    /* Section Wrapper */
    section {{ max-width: 1520px; margin: 0 auto 100px auto; padding: 0 48px; }}
    .sec-head {{ text-align: center; margin-bottom: 50px; }}
    .sec-head h2 {{
      font-family: var(--font-display); font-size: clamp(2.2rem, 3.8vw, 3.2rem);
      font-weight: 900; text-transform: uppercase; letter-spacing: -0.5px; margin-top: 10px;
    }}

    /* ADVANCED COMPONENT 1: Stadium Competition WOD Stopwatch */
    .stadium-timer-box {{
      background: linear-gradient(135deg, #131318 0%, #1e1e28 100%);
      border: 1px solid var(--border-accent); border-radius: 18px; padding: 40px;
      display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center;
      box-shadow: 0 20px 60px rgba(0,0,0,0.6); margin-bottom: 100px;
    }}
    .timer-left h3 {{
      font-family: var(--font-display); font-size: 1.85rem; font-weight: 900;
      text-transform: uppercase; margin-bottom: 12px; color: #fff;
    }}
    .timer-modes {{ display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; }}
    .tmode-btn {{
      background: var(--surface); border: 1px solid var(--border); color: #fff;
      padding: 8px 16px; border-radius: 6px; font-family: var(--font-athletic);
      font-size: 1rem; font-weight: 800; text-transform: uppercase; cursor: pointer;
    }}
    .tmode-btn.active {{ background: var(--orange); color: #000; border-color: var(--orange); }}

    .stadium-scoreboard {{
      background: #000; border: 2px solid #27272a; border-radius: 14px;
      padding: 30px; text-align: center; box-shadow: inset 0 0 40px rgba(249, 115, 22, 0.15);
    }}
    .timer-digits {{
      font-family: var(--font-mono); font-size: clamp(3.2rem, 6vw, 5rem);
      font-weight: 800; color: var(--orange); text-shadow: 0 0 25px var(--orange-glow);
      letter-spacing: 2px; line-height: 1; margin-bottom: 20px;
    }}
    .timer-ctrl-btns {{ display: flex; gap: 12px; justify-content: center; }}

    /* ADVANCED COMPONENT 2: Live 60 FPS Biometric EKG Monitor */
    .ekg-panel {{
      background: #09090d; border: 1px solid var(--border-accent); border-radius: 18px;
      padding: 36px; display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 36px; align-items: center;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5); margin-bottom: 100px;
    }}
    .ekg-canvas-wrapper {{
      background: #050507; border: 1px solid #27272a; border-radius: 12px;
      height: 220px; position: relative; overflow: hidden;
    }}
    #ekg-canvas {{ width: 100%; height: 100%; }}
    .bpm-big {{
      font-family: var(--font-athletic); font-size: 4.8rem; font-weight: 900;
      color: var(--crimson); line-height: 1; text-shadow: 0 0 30px var(--crimson-glow);
    }}
    .bpm-sub {{ font-family: var(--font-athletic); font-size: 1.15rem; font-weight: 800; text-transform: uppercase; color: var(--text-muted); }}

    /* WOD Schedule Grid */
    .schedule-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 16px; }}
    .schedule-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
      padding: 22px; transition: var(--transition); position: relative;
    }}
    .schedule-card:hover {{ border-color: var(--orange); transform: translateY(-4px); }}
    .schedule-card.highlight {{
      border-color: var(--orange);
      background: linear-gradient(180deg, rgba(249, 115, 22, 0.12) 0%, var(--surface) 100%);
    }}
    .day-pill {{
      font-family: var(--font-athletic); font-size: 1.35rem; font-weight: 900;
      color: var(--orange); text-transform: uppercase; margin-bottom: 6px;
    }}
    .wod-title {{ font-family: var(--font-display); font-size: 1.15rem; font-weight: 800; color: #fff; margin-bottom: 6px; }}
    .wod-desc {{ font-size: 0.88rem; color: var(--text-muted); line-height: 1.4; }}

    /* 1RM & Caloric Calculator */
    .calc-container {{
      background: linear-gradient(135deg, #141417 0%, #1c1c24 100%);
      border: 1px solid var(--border-accent); border-radius: 16px; padding: 40px;
      display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center;
    }}
    .slider-group {{ margin-bottom: 20px; }}
    .slider-header {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
    .slider-header label {{ font-family: var(--font-athletic); font-size: 1.1rem; font-weight: 800; text-transform: uppercase; }}
    .slider-val {{ font-family: var(--font-athletic); font-size: 1.3rem; font-weight: 900; color: var(--orange); }}
    input[type=range] {{
      width: 100%; height: 8px; border-radius: 4px; background: #27272a;
      outline: none; -webkit-appearance: none; accent-color: var(--orange); cursor: pointer;
    }}
    .gauge-ring {{
      font-family: var(--font-athletic); font-size: 4.2rem; font-weight: 900;
      color: var(--orange); line-height: 1; margin-bottom: 6px;
    }}

    /* Tier Passes */
    .tier-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }}
    .tier-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
      padding: 36px 28px; position: relative; transition: var(--transition);
      display: flex; flex-direction: column; justify-content: space-between;
    }}
    .tier-card:hover {{ transform: translateY(-6px); }}
    .tier-card.featured {{
      border-color: var(--orange); box-shadow: 0 0 35px var(--orange-glow);
      background: linear-gradient(180deg, rgba(249, 115, 22, 0.08) 0%, var(--surface) 100%);
    }}
    .tier-popular-tag {{
      position: absolute; top: -14px; left: 50%; transform: translateX(-50%) skewX(-8deg);
      background: var(--orange); color: #000; font-family: var(--font-athletic);
      font-size: 0.9rem; font-weight: 900; padding: 4px 14px; border-radius: 4px;
      text-transform: uppercase;
    }}
    .tier-name {{ font-family: var(--font-athletic); font-size: 1.8rem; font-weight: 900; text-transform: uppercase; margin-bottom: 8px; }}
    .tier-price {{ font-family: var(--font-athletic); font-size: 3.4rem; font-weight: 900; color: #fff; margin-bottom: 20px; }}
    .tier-price span {{ font-size: 1.2rem; color: var(--text-muted); font-weight: 600; }}
    .tier-features {{ list-style: none; margin-bottom: 30px; }}
    .tier-features li {{
      padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.95rem;
      display: flex; align-items: center; gap: 10px; color: var(--text-muted);
    }}
    .tier-features li::before {{ content: "✓"; color: var(--orange); font-weight: 900; }}

    /* Coach Grid */
    .coach-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }}
    .coach-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
      padding: 28px; display: flex; gap: 24px; align-items: center;
    }}
    .coach-avatar {{ width: 90px; height: 90px; border-radius: 10px; object-fit: cover; border: 2px solid var(--orange); }}

    footer {{
      background: #050507; border-top: 1px solid var(--border); padding: 40px 48px;
      text-align: center; font-family: var(--font-athletic); text-transform: uppercase;
    }}

    @media (max-width: 980px) {{
      .hero-arena {{ grid-template-columns: 1fr; }}
      .stadium-timer-box {{ grid-template-columns: 1fr; }}
      .ekg-panel {{ grid-template-columns: 1fr; }}
      .calc-container {{ grid-template-columns: 1fr; }}
      .tier-grid {{ grid-template-columns: 1fr; }}
      .coach-grid {{ grid-template-columns: 1fr; }}
      nav {{ padding: 16px 20px; }}
      .nav-links {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="glow-1"></div>
  <div class="glow-2"></div>

  <!-- Navigation -->
  <nav>
    <a href="#home" class="nav-brand">
      <div class="brand-flame">🔥</div>
      <span>{brand}</span>
    </a>
    <ul class="nav-links">
      <li><a href="#timer">WOD Timer</a></li>
      <li><a href="#ekg">EKG</a></li>
      <li><a href="#biometrics-radar">Spider Radar</a></li>
      <li><a href="#wod-synthesizer">Neural WOD</a></li>
      <li><a href="#schedule">Schedule</a></li>
      <li><a href="#calculator">1RM Calc</a></li>
      <li><a href="#memberships" class="nav-cta"><span>Claim Pass ➔</span></a></li>
    </ul>
  </nav>

  <!-- Hero with Interactive 3D Barbell Loader -->
  <header class="hero-arena" id="home">
    <div>
      <div class="skew-tag"><span>⚡ Elite Athletic Conditioning & Kinetic Arena</span></div>
      <h1>
        Push Beyond The <br>
        <span class="gradient-fire">Biological Limit</span>
      </h1>
      <p>
        Architected for athletes who demand Olympic precision, real-time telemetry calibration, and uncompromising human durability.
      </p>
      <div class="hero-btns">
        <button class="btn-fire" onclick="triggerBarbellDrop()"><span>⚡ Drop Barbell (Drop Test)</span></button>
        <a href="#timer" class="btn-outline">Open Stadium Timer</a>
      </div>
    </div>

    <!-- 3D Barbell Viewport -->
    <div class="viewport-box" id="viewport-box">
      <div class="hud-controls-bar">
        <div class="hud-row-top">
          <div class="weight-pills">
            <button class="weight-btn" onclick="loadBarbellWeight(135, this)">135 LBS</button>
            <button class="weight-btn active" onclick="loadBarbellWeight(225, this)">225 LBS</button>
            <button class="weight-btn" onclick="loadBarbellWeight(315, this)">315 LBS</button>
            <button class="weight-btn" onclick="loadBarbellWeight(405, this)">405 LBS</button>
          </div>
          <div class="hud-action-btns">
            <button class="action-hud-btn active" id="barpath-btn" onclick="toggleBarPath(this)">📈 Trajectory: On</button>
            <button class="action-hud-btn" id="explode-btn" onclick="toggleExplodedView(this)">💥 Explode</button>
            <button class="action-hud-btn" id="audio-btn" onclick="toggleAudioFX(this)">🔊 Audio</button>
          </div>
        </div>
        <div class="hud-row-bottom">
          <div class="lift-pills">
            <button class="lift-btn" id="btn-lift-snatch" onclick="triggerLift('snatch', this)">🏋️ Snatch</button>
            <button class="lift-btn" id="btn-lift-cj" onclick="triggerLift('clean_jerk', this)">💥 Clean &amp; Jerk</button>
            <button class="lift-btn" id="btn-lift-squat" onclick="triggerLift('squat', this)">⚡ Back Squat</button>
            <button class="lift-btn" onclick="resetLift(this)">↺ Reset</button>
          </div>
          <div class="camera-pills">
            <button class="cam-btn active" onclick="setCameraPreset('orbit', this)">🎥 Orbit</button>
            <button class="cam-btn" onclick="setCameraPreset('sagittal', this)">📐 Sagittal Path</button>
            <button class="cam-btn" onclick="setCameraPreset('athlete', this)">👁️ POV</button>
            <button class="cam-btn" onclick="setCameraPreset('top', this)">⚖️ Symmetry</button>
          </div>
        </div>
      </div>
      <div id="webgl-canvas-container" title="Click &amp; Drag to Orbit in 360°"></div>
      <div class="hud-footer">
        <div class="hud-caption">
          <div class="hud-caption-title">Olympic Steel Spec • 28mm Knurled Shaft</div>
          <div class="hud-caption-val" id="barbell-hud-val">225 LBS (102.1 KG) • Competition Chrome Bar</div>
        </div>
        <div class="hud-telemetry-pill" id="lift-telemetry">
          <span>VEL: <b id="tele-vel" style="color:#fff;">0.00 m/s</b></span>
          <span>PHASE: <b id="tele-phase" style="color:var(--orange);">PLATFORM REST</b></span>
          <span>POWER: <b id="tele-pwr" style="color:var(--emerald);">0 W</b></span>
        </div>
      </div>
    </div>
  </header>

  <!-- ADVANCED COMPONENT 1: Stadium Competition WOD Stopwatch -->
  <section id="timer">
    <div class="stadium-timer-box">
      <div class="timer-left">
        <div class="skew-tag"><span>Competition Telemetry</span></div>
        <h3>Stadium WOD Clock</h3>
        <p style="color:var(--text-muted);margin-bottom:20px;">Synchronized interval clock featuring acoustic 3-2-1 countdown beeps, high-frequency buzzer, and preset competition rounds.</p>
        
        <div class="timer-modes">
          <button class="tmode-btn active" onclick="setTimerMode('FORTIME', this)">For Time</button>
          <button class="tmode-btn" onclick="setTimerMode('AMRAP20', this)">AMRAP (20:00)</button>
          <button class="tmode-btn" onclick="setTimerMode('EMOM10', this)">EMOM (10:00)</button>
          <button class="tmode-btn" onclick="setTimerMode('TABATA', this)">Tabata (20/10)</button>
        </div>

        <div style="font-family:var(--font-athletic);font-size:1.1rem;color:var(--text-muted);">
          STATUS: <span id="timer-status" style="color:var(--orange);font-weight:900;">READY</span>
        </div>
      </div>

      <div class="stadium-scoreboard">
        <div class="timer-digits" id="timer-display">00:00.00</div>
        <div class="timer-ctrl-btns">
          <button class="btn-fire" id="timer-toggle-btn" onclick="toggleStadiumTimer()"><span>Start Clock</span></button>
          <button class="btn-outline" onclick="resetStadiumTimer()">Reset</button>
        </div>
      </div>
    </div>
  </section>

  <!-- ADVANCED COMPONENT 2: Live 60 FPS Biometric EKG Oscilloscope -->
  <section id="ekg">
    <div class="sec-head">
      <div class="skew-tag"><span>Cardiac Frequency Tracking</span></div>
      <h2>Live Biometric EKG Telemetry</h2>
    </div>
    <div class="ekg-panel">
      <div class="ekg-canvas-wrapper">
        <canvas id="ekg-canvas"></canvas>
      </div>
      <div>
        <div class="bpm-big" id="bpm-val">172 BPM</div>
        <div class="bpm-sub">Real-Time Heart Rate Zone 4 (Lactate Threshold)</div>
        <div style="margin-top:24px;">
          <label style="font-family:var(--font-athletic);font-weight:800;text-transform:uppercase;">Adjust Heart Rate Intensity:</label>
          <input type="range" id="bpm-slider" min="60" max="195" value="172" style="accent-color:var(--crimson);margin-top:8px;" oninput="updateBPM(this.value)">
        </div>
      </div>
    </div>
  </section>

  <!-- ADVANCED COMPONENT 3: 5-Axis Biometric Radar Matrix -->
  <section id="biometrics-radar">
    <div class="sec-head">
      <div class="skew-tag"><span>Kinetic Bio-Analysis</span></div>
      <h2>Athletic Performance Spider Matrix</h2>
    </div>
    <div class="radar-container-card">
      <div class="radar-canvas-side">
        <canvas id="radar-canvas" width="440" height="400"></canvas>
      </div>
      <div class="radar-ctrl-side">
        <div class="aci-header">
          <div>
            <div class="aci-score-title">Apex Competitor Index (ACI)</div>
            <div class="aci-score-big" id="aci-score">94.8 <span>/ 100</span></div>
          </div>
          <div class="aci-tier-badge" id="aci-tier">National Elite Tier</div>
        </div>
        <p style="color:var(--text-muted);margin-bottom:24px;">Multi-vector biometric calibration balancing anaerobic lactate threshold against peak velocity and CNS recovery.</p>

        <div class="radar-sliders">
          <div class="rslider-row">
            <div class="rslider-lbl">Aerobic Capacity (VO2 Max): <span id="r-vo2-val">74 ml/kg/min</span></div>
            <input type="range" min="40" max="85" value="74" oninput="updateRadarParam('vo2', this.value)">
          </div>
          <div class="rslider-row">
            <div class="rslider-lbl">Anaerobic Lactate Threshold: <span id="r-lac-val">88 %</span></div>
            <input type="range" min="50" max="98" value="88" oninput="updateRadarParam('lactate', this.value)">
          </div>
          <div class="rslider-row">
            <div class="rslider-lbl">Peak Barbell Velocity: <span id="r-vel-val">2.45 m/s</span></div>
            <input type="range" min="10" max="32" value="24" oninput="updateRadarParam('velocity', this.value)">
          </div>
          <div class="rslider-row">
            <div class="rslider-lbl">Rate of Force Development: <span id="r-rfd-val">2,250 W</span></div>
            <input type="range" min="800" max="2800" value="2250" oninput="updateRadarParam('rfd', this.value)">
          </div>
          <div class="rslider-row">
            <div class="rslider-lbl">CNS Recovery Status: <span id="r-cns-val">96 %</span></div>
            <input type="range" min="40" max="100" value="96" oninput="updateRadarParam('cns', this.value)">
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ADVANCED COMPONENT 4: Neural WOD Protocol Synthesizer -->
  <section id="wod-synthesizer">
    <div class="sec-head">
      <div class="skew-tag"><span>Autonomous Programming Engine</span></div>
      <h2>Neural WOD Protocol Synthesizer</h2>
    </div>
    <div class="synth-card">
      <div class="synth-top-bar">
        <div class="synth-selectors">
          <div class="synth-group">
            <label>Target Stimulus:</label>
            <div class="synth-pills" id="goal-pills">
              <button class="synth-pill active" onclick="setSynthGoal('olympic', this)">🏋️ Olympic Power</button>
              <button class="synth-pill" onclick="setSynthGoal('engine', this)">⚡ Engine MetCon</button>
              <button class="synth-pill" onclick="setSynthGoal('hypertrophy', this)">💪 Hypertrophy Armor</button>
              <button class="synth-pill" onclick="setSynthGoal('hero', this)">🛡️ Benchmark Hero</button>
            </div>
          </div>
          <div class="synth-group">
            <label>Athlete Tier:</label>
            <div class="synth-pills" id="tier-pills">
              <button class="synth-pill" onclick="setSynthTier('scaled', this)">Scaled</button>
              <button class="synth-pill active" onclick="setSynthTier('rx', this)">Rx Competitor</button>
              <button class="synth-pill" onclick="setSynthTier('elite', this)">Games Elite</button>
            </div>
          </div>
        </div>
        <button class="btn-fire" onclick="synthesizeNeuralWOD()"><span>⚡ Synthesize Protocol</span></button>
      </div>

      <div class="synth-output-box" id="synth-output">
        <div class="synth-output-header">
          <div>
            <div class="synth-title" id="wod-name">PROTOCOL: TITAN CLEAN &amp; ASSAULT COMPLEX</div>
            <div class="synth-sub" id="wod-time-cap">Time Cap: 18:00 • Estimated Heart Rate Zone: Zone 4 (170-182 BPM)</div>
          </div>
          <button class="btn-outline" onclick="copyWODProtocol()">📋 Copy Protocol</button>
        </div>
        <div class="synth-body-grid" id="wod-details">
          <div class="synth-col">
            <div class="scol-head">Phase 1 • Dynamic Primer (0:00 - 4:00)</div>
            <ul>
              <li>400m Concept2 Ergometer Row @ 1:48 pace</li>
              <li>15 Banded Good Mornings &amp; Hip Flow</li>
              <li>10 Empty Barbell Tall Muscle Cleans</li>
            </ul>
          </div>
          <div class="synth-col highlight">
            <div class="scol-head">Phase 2 • Heavy MetCon (4:00 - 15:00)</div>
            <ul id="wod-main-list">
              <li>5 Rounds For Time:</li>
              <li><b>7 Squat Cleans @ 225 LBS (Barbell Loaded Spec)</b></li>
              <li>14 C2 Echo Bike Calories (Sprint Output)</li>
              <li>21 Unbroken Ring Dips</li>
            </ul>
          </div>
          <div class="synth-col">
            <div class="scol-head">Phase 3 • Lactate Flush (15:00 - 18:00)</div>
            <ul>
              <li>3:00 Easy Spin AirBike @ 45 RPM</li>
              <li>Supine Diaphragmatic Breath Downregulation</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Weekly WOD Schedule Grid -->
  <section id="schedule">
    <div class="sec-head">
      <div class="skew-tag"><span>Daily Protocol Matrix</span></div>
      <h2>Weekly High-Performance WOD Schedule</h2>
    </div>
    <div class="schedule-grid">
      <div class="schedule-card">
        <div class="day-pill">Monday</div>
        <div class="wod-title">Olympic Weightlifting</div>
        <div class="wod-desc">Heavy snatch doubles, clean & jerk complex, plus posterior chain accessory hypertrophy.</div>
      </div>
      <div class="schedule-card highlight">
        <div class="day-pill">Tuesday</div>
        <div class="wod-title">Engine MetCon (VO2)</div>
        <div class="wod-desc">High-lactate interval sprints combining Concept2 rowing, assault bike, and burpee box overs.</div>
      </div>
      <div class="schedule-card">
        <div class="day-pill">Wednesday</div>
        <div class="wod-title">Gymnastic Density</div>
        <div class="wod-desc">Ring muscle-ups, handstand walk precision courses, and strict core tension stabilization.</div>
      </div>
      <div class="schedule-card">
        <div class="day-pill">Thursday</div>
        <div class="wod-title">Active Rest & Mobility</div>
        <div class="wod-desc">Myofascial tissue release, controlled articular rotations, and aerobic recovery flushing.</div>
      </div>
      <div class="schedule-card highlight">
        <div class="day-pill">Friday</div>
        <div class="wod-title">Friday Night Lights</div>
        <div class="wod-desc">CrossFit Games style benchmark workout under stadium lighting with full athlete crowd energy.</div>
      </div>
      <div class="schedule-card">
        <div class="day-pill">Saturday</div>
        <div class="wod-title">Hero WOD & Endurance</div>
        <div class="wod-desc">Grueling team workout with sandbags, sled pushes, and synchronized barbell work.</div>
      </div>
    </div>
  </section>

  <!-- Interactive 1RM Calculator -->
  <section id="calculator">
    <div class="sec-head">
      <div class="skew-tag"><span>Biometric Target Engine</span></div>
      <h2>Interactive Calorie & Power Telemetry</h2>
    </div>
    <div class="calc-container">
      <div>
        <h3 style="font-family:var(--font-display);font-size:1.8rem;font-weight:900;text-transform:uppercase;margin-bottom:12px;">Calibrate Your Session Output</h3>
        <p style="color:var(--text-muted);margin-bottom:24px;">Adjust bodyweight and intensity to project caloric burn and anaerobic capacity.</p>
        <div class="slider-group">
          <div class="slider-header">
            <label>Athlete Bodyweight</label>
            <span class="slider-val" id="weight-display">185 LBS</span>
          </div>
          <input type="range" id="weight-slider" min="120" max="280" value="185" oninput="updateAthleteCalc()">
        </div>
      </div>
      <div style="background:#09090b;padding:30px;border-radius:12px;text-align:center;border:1px solid var(--border);">
        <div class="gauge-ring" id="cal-output">820 kcal</div>
        <div style="font-family:var(--font-athletic);font-size:1.2rem;font-weight:800;color:#fff;text-transform:uppercase;">Projected Burn / 60 Min WOD</div>
      </div>
    </div>
  </section>

  <!-- Memberships -->
  <section id="memberships">
    <div class="sec-head">
      <div class="skew-tag"><span>Investment In Longevity</span></div>
      <h2>Membership Access Tiers</h2>
    </div>
    <div class="tier-grid">
      <div class="tier-card">
        <div>
          <div class="tier-name">Drop-In Pass</div>
          <div class="tier-price">$25 <span>/ session</span></div>
          <ul class="tier-features">
            <li>Single Day Open Gym & WOD Class Access</li>
            <li>Full Locker Room & Sauna Access</li>
            <li>Biometric HR Sensor Bluetooth Sync</li>
          </ul>
        </div>
        <button class="btn-outline" style="width:100%;" onclick="alert('Drop-in selected')">Select Drop-In</button>
      </div>

      <div class="tier-card featured">
        <div class="tier-popular-tag">Most Popular</div>
        <div>
          <div class="tier-name" style="color:var(--orange);">Unlimited Athlete</div>
          <div class="tier-price">$165 <span>/ month</span></div>
          <ul class="tier-features">
            <li>Unlimited CrossFit, MetCon & Strength Classes</li>
            <li>Progressive Overload Programming</li>
            <li>Weekly Coach 1-on-1 Barbell Movement Check</li>
            <li>Full Cold Plunge & Infrared Sauna Access</li>
          </ul>
        </div>
        <button class="btn-fire" style="width:100%;" onclick="alert('Unlimited Athlete selected')"><span>Join Unlimited ➔</span></button>
      </div>

      <div class="tier-card">
        <div>
          <div class="tier-name">Competition Pro</div>
          <div class="tier-price">$240 <span>/ month</span></div>
          <ul class="tier-features">
            <li>Everything in Unlimited Athlete</li>
            <li>High-Speed 240fps Video Barbell Kinematics</li>
            <li>Priority 24/7 Key Fob Facility Access</li>
          </ul>
        </div>
        <button class="btn-outline" style="width:100%;" onclick="alert('Competition Pro selected')">Select Comp Pro</button>
      </div>
    </div>
  </section>

  <footer>
    <div style="font-size:1.4rem;font-weight:900;color:#fff;margin-bottom:8px;">🔥 {brand}</div>
    <p style="color:var(--text-muted);font-size:0.9rem;">
      High-Performance Strength Arena &bull; Architected by D.E.E.P Sovereign Engine &bull; 2026.
    </p>
  </footer>

  <script>
    // --- Studio-Grade Web Audio Synthesizer ---
    let audioCtx = null;
    let audioEnabled = true;

    function initAudio() {{
      if (!audioCtx) {{
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) audioCtx = new AudioContext();
      }}
      if (audioCtx && audioCtx.state === 'suspended') {{
        audioCtx.resume();
      }}
    }}

    function playPlateClank() {{
      if (!audioEnabled) return;
      initAudio();
      if (!audioCtx) return;
      try {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1400, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(320, audioCtx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.18);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.18);
      }} catch(e) {{}}
    }}

    function playChalkPuff() {{
      if (!audioEnabled) return;
      initAudio();
      if (!audioCtx) return;
      try {{
        const bufferSize = Math.floor(audioCtx.sampleRate * 0.12);
        const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {{
          data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.25));
        }}
        const noise = audioCtx.createBufferSource();
        noise.buffer = buffer;
        const filter = audioCtx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.value = 1800;
        filter.Q.value = 1.2;
        const gain = audioCtx.createGain();
        gain.gain.setValueAtTime(0.22, audioCtx.currentTime);
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(audioCtx.destination);
        noise.start();
      }} catch(e) {{}}
    }}

    function playChime(freq = 660) {{
      if (!audioEnabled) return;
      initAudio();
      if (!audioCtx) return;
      try {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(freq * 1.5, audioCtx.currentTime + 0.08);
        gain.gain.setValueAtTime(0.14, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.35);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.35);
      }} catch(e) {{}}
    }}

    function playBuzzer(freq = 880, duration = 0.25) {{
      if (!audioEnabled) return;
      initAudio();
      if (!audioCtx) return;
      try {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch(e) {{}}
    }}

    window.toggleAudioFX = function(btn) {{
      initAudio();
      audioEnabled = !audioEnabled;
      if (btn) {{
        btn.textContent = audioEnabled ? '🔊 Audio' : '🔇 Muted';
        btn.classList.toggle('active', audioEnabled);
      }}
      if (audioEnabled) playPlateClank();
    }};

    // --- Interactive Three.js Olympic Barbell Engine with Dynamic Lift Simulator ---
    let barbellGroup, plateMeshes = [], isExploded = false;
    let emberPoints = null, trajectoryLine = null, chalkPoints = null;
    let chalkPositions, chalkVelocities, chalkMat;
    let isLifting = false, liftType = null, liftProgress = 0, currentWeight = 225;
    let currentCamMode = 'orbit', showBarPath = true;
    let chalkBurstDone = false, lastPosY = 0;

    (function initOlympicBarbell() {{
      const container = document.getElementById('webgl-canvas-container');
      if (!container || typeof THREE === 'undefined') return;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
      camera.position.set(0, 0, 4.8);

      const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.autoRotate = true;
      controls.autoRotateSpeed = 1.1;
      controls.maxDistance = 8.5;
      controls.minDistance = 1.8;

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.88);
      scene.add(ambientLight);
      const orangeLight = new THREE.PointLight(0xf97316, 3.4, 50);
      orangeLight.position.set(4, 4, 4);
      scene.add(orangeLight);
      const crimsonLight = new THREE.PointLight(0xef4444, 3.0, 50);
      crimsonLight.position.set(-4, -2, 3);
      scene.add(crimsonLight);

      barbellGroup = new THREE.Group();

      // Shaft: 28mm Olympic Hard Chrome Bar
      const shaftGeo = new THREE.CylinderGeometry(0.045, 0.045, 3.6, 24);
      const shaftMat = new THREE.MeshStandardMaterial({{ color: 0xd4d4d8, metalness: 0.95, roughness: 0.2 }});
      const shaft = new THREE.Mesh(shaftGeo, shaftMat);
      shaft.rotation.z = Math.PI / 2;
      barbellGroup.add(shaft);

      // Knurl grip sections
      [-0.8, -0.4, 0.4, 0.8].forEach(x => {{
        const kGeo = new THREE.CylinderGeometry(0.047, 0.047, 0.28, 20);
        const kMat = new THREE.MeshStandardMaterial({{ color: 0x71717a, roughness: 0.8, metalness: 0.85 }});
        const km = new THREE.Mesh(kGeo, kMat);
        km.rotation.z = Math.PI / 2;
        km.position.x = x;
        barbellGroup.add(km);
      }});

      // Inner Collars
      [-1.15, 1.15].forEach(x => {{
        const cGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.08, 24);
        const cMat = new THREE.MeshStandardMaterial({{ color: 0xa1a1aa, metalness: 0.9, roughness: 0.2 }});
        const cm = new THREE.Mesh(cGeo, cMat);
        cm.rotation.z = Math.PI / 2;
        cm.position.x = x;
        barbellGroup.add(cm);
      }});

      // Olympic Sleeves (50mm diameter)
      [-1.6, 1.6].forEach(x => {{
        const sGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.85, 24);
        const sMat = new THREE.MeshStandardMaterial({{ color: 0xe4e4e7, metalness: 0.92, roughness: 0.18 }});
        const sm = new THREE.Mesh(sGeo, sMat);
        sm.rotation.z = Math.PI / 2;
        sm.position.x = x;
        barbellGroup.add(sm);
      }});

      // 4 Pairs of Bumper Plates (Competition Colors: Red 45, Amber 35, Green 25)
      const plateConfigs = [
        {{ x: 0.14, r: 0.62, w: 0.09, c: 0xef4444 }},
        {{ x: 0.26, r: 0.62, w: 0.09, c: 0xef4444 }},
        {{ x: 0.38, r: 0.58, w: 0.08, c: 0xf59e0b }},
        {{ x: 0.49, r: 0.52, w: 0.07, c: 0x10b981 }}
      ];

      plateConfigs.forEach((cfg, i) => {{
        const pGeo = new THREE.CylinderGeometry(cfg.r, cfg.r, cfg.w, 32);
        const pMat = new THREE.MeshStandardMaterial({{ color: cfg.c, roughness: 0.35, metalness: 0.6 }});
        
        const lp = new THREE.Mesh(pGeo, pMat);
        lp.rotation.z = Math.PI / 2;
        lp.position.x = -(1.2 + cfg.x);
        barbellGroup.add(lp);

        const rp = new THREE.Mesh(pGeo, pMat);
        rp.rotation.z = Math.PI / 2;
        rp.position.x = 1.2 + cfg.x;
        barbellGroup.add(rp);

        plateMeshes.push({{ left: lp, right: rp, baseLeftX: lp.position.x, baseRightX: rp.position.x, index: i }});
      }});

      scene.add(barbellGroup);

      // Trajectory 3D S-Curve Ribbon Line
      const maxTrajPoints = 180;
      const trajPositions = new Float32Array(maxTrajPoints * 3);
      const trajGeo = new THREE.BufferGeometry();
      trajGeo.setAttribute('position', new THREE.BufferAttribute(trajPositions, 3));
      const trajMat = new THREE.LineBasicMaterial({{ color: 0xf97316, linewidth: 3, transparent: true, opacity: 0.9 }});
      trajectoryLine = new THREE.Line(trajGeo, trajMat);
      trajectoryLine.frustumCulled = false;
      scene.add(trajectoryLine);

      // 600 Explosive Chalk Dust Particles
      const chalkCount = 600;
      const chalkGeo = new THREE.BufferGeometry();
      chalkPositions = new Float32Array(chalkCount * 3);
      chalkVelocities = new Float32Array(chalkCount * 3);
      for (let i = 0; i < chalkCount * 3; i++) {{
        chalkPositions[i] = 999; // start off-screen
        chalkVelocities[i] = 0;
      }}
      chalkGeo.setAttribute('position', new THREE.BufferAttribute(chalkPositions, 3));
      chalkMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 0.055, transparent: true, opacity: 0 }});
      chalkPoints = new THREE.Points(chalkGeo, chalkMat);
      scene.add(chalkPoints);

      function triggerChalkBurst(y) {{
        for (let i = 0; i < chalkCount; i++) {{
          const i3 = i * 3;
          chalkPositions[i3] = (Math.random() - 0.5) * 0.7;
          chalkPositions[i3 + 1] = y + (Math.random() - 0.5) * 0.2;
          chalkPositions[i3 + 2] = (Math.random() - 0.5) * 0.7;
          chalkVelocities[i3] = (Math.random() - 0.5) * 0.09;
          chalkVelocities[i3 + 1] = Math.random() * 0.08 + 0.01;
          chalkVelocities[i3 + 2] = (Math.random() - 0.5) * 0.09;
        }}
        chalkMat.opacity = 0.95;
        chalkGeo.attributes.position.needsUpdate = true;
        playChalkPuff();
      }}

      // 1,600 Fiery Floating Embers
      const emberCount = 1600;
      const emberGeo = new THREE.BufferGeometry();
      const emberPositions = new Float32Array(emberCount * 3);
      for (let i = 0; i < emberCount * 3; i += 3) {{
        const rad = 0.8 + Math.random() * 3.2;
        const th = Math.random() * Math.PI * 2;
        const ph = (Math.random() - 0.5) * Math.PI;
        emberPositions[i] = rad * Math.cos(th) * Math.cos(ph);
        emberPositions[i + 1] = rad * Math.sin(ph);
        emberPositions[i + 2] = rad * Math.sin(th) * Math.cos(ph);
      }}
      emberGeo.setAttribute('position', new THREE.BufferAttribute(emberPositions, 3));
      const emberMat = new THREE.PointsMaterial({{ color: 0xf97316, size: 0.046, transparent: true, opacity: 0.85 }});
      emberPoints = new THREE.Points(emberGeo, emberMat);
      scene.add(emberPoints);

      window.loadBarbellWeight = function(weight, btn) {{
        initAudio();
        document.querySelectorAll('.weight-btn').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');
        currentWeight = weight;

        const pairsCount = weight === 135 ? 1 : weight === 225 ? 2 : weight === 315 ? 3 : 4;
        plateMeshes.forEach((p, idx) => {{
          const isVisible = idx < pairsCount;
          p.left.visible = isVisible;
          p.right.visible = isVisible;
        }});

        const kg = Math.round(weight * 0.453592);
        document.getElementById('barbell-hud-val').textContent = `${{weight}} LBS (${{kg}} KG) • Competition Chrome Bar`;
        playPlateClank();
      }};

      window.toggleExplodedView = function(btn) {{
        isExploded = !isExploded;
        if (btn) btn.classList.toggle('active', isExploded);
        plateMeshes.forEach(p => {{
          p.left.position.x = isExploded ? p.baseLeftX * 1.45 : p.baseLeftX;
          p.right.position.x = isExploded ? p.baseRightX * 1.45 : p.baseRightX;
        }});
        playPlateClank();
      }};

      window.toggleBarPath = function(btn) {{
        showBarPath = !showBarPath;
        if (btn) {{
          btn.textContent = showBarPath ? '📈 Trajectory: On' : '📈 Trajectory: Off';
          btn.classList.toggle('active', showBarPath);
        }}
        if (trajectoryLine) trajectoryLine.visible = showBarPath;
      }};

      let trajectoryIndex = 0;
      function resetTrajectory() {{
        trajectoryIndex = 0;
        const pos = trajGeo.attributes.position.array;
        for (let i = 0; i < maxTrajPoints * 3; i++) pos[i] = 0;
        trajGeo.attributes.position.needsUpdate = true;
      }}

      function addTrajectoryPoint(x, y, z) {{
        if (trajectoryIndex >= maxTrajPoints) return;
        const pos = trajGeo.attributes.position.array;
        const i3 = trajectoryIndex * 3;
        pos[i3] = x;
        pos[i3 + 1] = y;
        pos[i3 + 2] = z;
        trajectoryIndex++;
        trajGeo.setDrawRange(0, trajectoryIndex);
        trajGeo.attributes.position.needsUpdate = true;
      }}

      window.triggerLift = function(type, btn) {{
        initAudio();
        document.querySelectorAll('.lift-btn').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');

        isLifting = true;
        liftType = type;
        liftProgress = 0;
        chalkBurstDone = false;
        resetTrajectory();
        playChalkPuff();
      }};

      window.resetLift = function(btn) {{
        isLifting = false;
        liftProgress = 0;
        barbellGroup.position.set(0, 0, 0);
        barbellGroup.rotation.set(0, 0, 0);
        resetTrajectory();
        document.querySelectorAll('.lift-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('tele-vel').textContent = '0.00 m/s';
        document.getElementById('tele-phase').textContent = 'PLATFORM REST';
        document.getElementById('tele-pwr').textContent = '0 W';
      }};

      window.setCameraPreset = function(mode, btn) {{
        currentCamMode = mode;
        document.querySelectorAll('.cam-btn').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');

        if (mode === 'orbit') {{
          controls.enabled = true;
          controls.autoRotate = true;
          camera.position.set(0, 0, 4.8);
        }} else if (mode === 'sagittal') {{
          controls.enabled = false;
          controls.autoRotate = false;
          camera.position.set(5.5, barbellGroup.position.y, 0);
          camera.lookAt(0, barbellGroup.position.y, 0);
        }} else if (mode === 'athlete') {{
          controls.enabled = false;
          controls.autoRotate = false;
          camera.position.set(0, 0.4, -2.8);
          camera.lookAt(0, 0.4, 2.8);
        }} else if (mode === 'top') {{
          controls.enabled = false;
          controls.autoRotate = false;
          camera.position.set(0, 5.5, 0);
          camera.lookAt(0, 0, 0);
        }}
      }};

      window.triggerBarbellDrop = function() {{
        initAudio();
        const box = document.getElementById('viewport-box');
        if (box) {{
          box.style.transform = 'translateY(12px) scale(0.99)';
          setTimeout(() => box.style.transform = 'translateY(-6px)', 80);
          setTimeout(() => box.style.transform = 'translateY(3px)', 160);
          setTimeout(() => box.style.transform = 'none', 260);
        }}
        barbellGroup.position.y = -0.3;
        triggerChalkBurst(-0.3);
        setTimeout(() => barbellGroup.position.y = 0.1, 100);
        setTimeout(() => barbellGroup.position.y = 0, 200);

        playBuzzer(120, 0.4);
        setTimeout(() => playPlateClank(), 80);
      }};

      // Render Loop with Kinematic Lift Parametrics
      let clock = new THREE.Clock();
      function animate() {{
        requestAnimationFrame(animate);
        const delta = clock.getDelta();

        if (controls && controls.enabled) controls.update();
        if (emberPoints) emberPoints.rotation.y += 0.001;

        if (isLifting) {{
          liftProgress += delta * 0.48; // ~2.1 seconds per lift cycle
          let y = 0, z = 0, whip = 0, phaseName = 'PULL';

          if (liftType === 'snatch') {{
            if (liftProgress < 0.35) {{
              // First pull from platform
              const p = liftProgress / 0.35;
              y = -1.2 + p * 0.8;
              z = -Math.sin(p * Math.PI) * 0.08;
              phaseName = '1ST PULL (LIFTOFF)';
            }} else if (liftProgress < 0.6) {{
              // Explosive 2nd pull & extension
              const p = (liftProgress - 0.35) / 0.25;
              y = -0.4 + p * 1.1;
              z = (p - 0.5) * 0.06;
              phaseName = '2ND PULL (EXPLOSIVE EXTENSION)';
              if (!chalkBurstDone && p > 0.3) {{
                triggerChalkBurst(y);
                chalkBurstDone = true;
              }}
            }} else if (liftProgress < 0.82) {{
              // Turnover and catch overhead
              const p = (liftProgress - 0.6) / 0.22;
              y = 0.7 + Math.sin(p * Math.PI) * 0.45;
              phaseName = 'TURNOVER & SQUAT CATCH';
              whip = Math.sin(p * Math.PI * 8) * 0.04;
            }} else if (liftProgress <= 1.0) {{
              // Lockout stand up
              const p = (liftProgress - 0.82) / 0.18;
              y = 1.15 + p * 0.25;
              phaseName = 'OVERHEAD LOCKOUT';
            }} else {{
              // Lift complete
              isLifting = false;
              y = 1.4;
              phaseName = 'LIFT COMPLETE (GOOD LIFT)';
              playPlateClank();
              playChime(880);
            }}
          }} else if (liftType === 'clean_jerk') {{
            if (liftProgress < 0.35) {{
              const p = liftProgress / 0.35;
              y = -1.2 + p * 0.8;
              z = -Math.sin(p * Math.PI) * 0.07;
              phaseName = 'CLEAN 1ST PULL';
            }} else if (liftProgress < 0.55) {{
              const p = (liftProgress - 0.35) / 0.20;
              y = -0.4 + p * 0.85;
              phaseName = 'CLEAN 2ND PULL (HIP CONTACT)';
              if (!chalkBurstDone && p > 0.4) {{
                triggerChalkBurst(y);
                chalkBurstDone = true;
              }}
            }} else if (liftProgress < 0.75) {{
              const p = (liftProgress - 0.55) / 0.20;
              y = 0.45 - Math.sin(p * Math.PI) * 0.2;
              phaseName = 'SHOULDER RACK & DIP';
            }} else if (liftProgress <= 1.0) {{
              const p = (liftProgress - 0.75) / 0.25;
              y = 0.45 + p * 0.95;
              phaseName = 'SPLIT JERK LOCKOUT';
              whip = Math.sin(p * Math.PI * 6) * 0.035;
            }} else {{
              isLifting = false;
              y = 1.4;
              phaseName = 'JERK COMPLETE';
              playPlateClank();
              playChime(880);
            }}
          }} else if (liftType === 'squat') {{
            if (liftProgress < 0.5) {{
              const p = liftProgress / 0.5;
              y = 0.5 - p * 0.85;
              phaseName = 'ECCENTRIC SQUAT DESCENT';
            }} else if (liftProgress <= 1.0) {{
              const p = (liftProgress - 0.5) / 0.5;
              y = -0.35 + p * 0.85;
              phaseName = 'CONCENTRIC ASCENT (DRIVE)';
            }} else {{
              isLifting = false;
              y = 0.5;
              phaseName = 'SQUAT STAND LOCKOUT';
              playPlateClank();
            }}
          }}

          barbellGroup.position.y = y;
          barbellGroup.position.z = z;
          barbellGroup.rotation.z = whip;

          // Track instantaneous trajectory
          addTrajectoryPoint(0, y, z);

          // Telemetry
          const vel = Math.abs((y - lastPosY) / Math.max(delta, 0.001)).toFixed(2);
          const pwr = Math.round(currentWeight * 9.8 * parseFloat(vel) * 0.4535);
          document.getElementById('tele-vel').textContent = `${{vel}} m/s`;
          document.getElementById('tele-phase').textContent = phaseName;
          document.getElementById('tele-pwr').textContent = `${{pwr}} W`;
          lastPosY = y;
        }}

        // Chalk dust particles update
        if (chalkMat && chalkMat.opacity > 0.01) {{
          chalkMat.opacity -= 0.012;
          for (let i = 0; i < chalkCount; i++) {{
            const i3 = i * 3;
            chalkPositions[i3] += chalkVelocities[i3];
            chalkPositions[i3 + 1] += chalkVelocities[i3 + 1];
            chalkPositions[i3 + 2] += chalkVelocities[i3 + 2];
            chalkVelocities[i3 + 1] -= 0.0015; // gravity
          }}
          chalkGeo.attributes.position.needsUpdate = true;
        }}

        // Sagittal camera tracking
        if (currentCamMode === 'sagittal') {{
          camera.position.y = barbellGroup.position.y;
          camera.lookAt(0, barbellGroup.position.y, 0);
        }}

        renderer.render(scene, camera);
      }}
      animate();

      // Initial state
      loadBarbellWeight(225, null);
    }})();

    // --- Stadium Competition WOD Stopwatch ---
    let timerInterval = null, timerRunning = false, timerSeconds = 0, currentTimerMode = 'FORTIME';

    function setTimerMode(mode, btn) {{
      document.querySelectorAll('.tmode-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      currentTimerMode = mode;
      resetStadiumTimer();
    }}

    function toggleStadiumTimer() {{
      initAudio();
      const btn = document.getElementById('timer-toggle-btn');
      const status = document.getElementById('timer-status');

      if (!timerRunning) {{
        // 3-2-1 Countdown Beeps
        status.textContent = 'COUNTDOWN...';
        playBuzzer(440, 0.15);
        setTimeout(() => playBuzzer(440, 0.15), 500);
        setTimeout(() => playBuzzer(440, 0.15), 1000);
        setTimeout(() => {{
          playBuzzer(880, 0.4);
          status.textContent = 'WORKOUT IN PROGRESS';
          timerRunning = true;
          btn.innerHTML = '<span>Pause Clock</span>';
          btn.style.background = 'var(--crimson)';

          timerInterval = setInterval(() => {{
            timerSeconds += 0.01;
            const mins = Math.floor(timerSeconds / 60);
            const secs = Math.floor(timerSeconds % 60);
            const ms = Math.floor((timerSeconds % 1) * 100);
            document.getElementById('timer-display').textContent = 
              `${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}.${{ms.toString().padStart(2, '0')}}`;
          }}, 10);
        }}, 1500);
      }} else {{
        clearInterval(timerInterval);
        timerRunning = false;
        status.textContent = 'PAUSED';
        btn.innerHTML = '<span>Resume Clock</span>';
        btn.style.background = 'linear-gradient(135deg, var(--orange), var(--crimson))';
      }}
    }}

    function resetStadiumTimer() {{
      clearInterval(timerInterval);
      timerRunning = false;
      timerSeconds = 0;
      document.getElementById('timer-display').textContent = '00:00.00';
      document.getElementById('timer-status').textContent = 'READY';
      const btn = document.getElementById('timer-toggle-btn');
      btn.innerHTML = '<span>Start Clock</span>';
      btn.style.background = 'linear-gradient(135deg, var(--orange), var(--crimson))';
    }}

    // --- Live 60 FPS Biometric EKG Oscilloscope ---
    (function initEKG() {{
      const canvas = document.getElementById('ekg-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;

      let x = 0;
      let bpmSpeed = 2.4;
      const points = [];
      const w = canvas.width;
      const h = canvas.height;
      const midY = h / 2;

      window.updateBPM = function(val) {{
        document.getElementById('bpm-val').textContent = `${{val}} BPM`;
        bpmSpeed = (val / 60) * 1.5;
      }};

      function getEKGHeight(pos) {{
        const phase = pos % 120;
        if (phase > 40 && phase < 46) return -8; // P wave
        if (phase > 54 && phase < 58) return 14; // Q wave
        if (phase >= 58 && phase <= 66) return -70; // R wave spike
        if (phase > 66 && phase < 72) return 20; // S wave
        if (phase > 82 && phase < 96) return -18; // T wave
        return 0;
      }}

      function draw() {{
        ctx.fillStyle = 'rgba(5, 5, 7, 0.18)';
        ctx.fillRect(0, 0, w, h);

        ctx.strokeStyle = '#f97316';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = '#f97316';
        ctx.shadowBlur = 12;

        ctx.beginPath();
        for (let i = 0; i < bpmSpeed * 2; i++) {{
          const y = midY + getEKGHeight(x);
          ctx.lineTo(x, y);
          x += 1;
          if (x >= w) {{
            x = 0;
            ctx.moveTo(0, midY);
          }}
        }}
        ctx.stroke();
        requestAnimationFrame(draw);
      }}
      draw();
    }})();

    function updateAthleteCalc() {{
      const weight = parseInt(document.getElementById('weight-slider').value);
      document.getElementById('weight-display').textContent = `${{weight}} LBS`;
      const cals = Math.round(weight * 4.4);
      document.getElementById('cal-output').textContent = `${{cals}} kcal`;
    }}

    // --- ADVANCED COMPONENT 3: 5-Axis Biometric Radar Matrix ---
    const radarData = {{
      vo2: 74,      // min 40, max 85
      lactate: 88,  // min 50, max 98
      velocity: 24, // min 10, max 32 (2.4 m/s)
      rfd: 2250,    // min 800, max 2800
      cns: 96       // min 40, max 100
    }};

    window.updateRadarParam = function(param, val) {{
      val = parseFloat(val);
      radarData[param] = val;

      if (param === 'vo2') document.getElementById('r-vo2-val').textContent = `${{val}} ml/kg/min`;
      if (param === 'lactate') document.getElementById('r-lac-val').textContent = `${{val}} %`;
      if (param === 'velocity') document.getElementById('r-vel-val').textContent = `${{(val / 10).toFixed(2)}} m/s`;
      if (param === 'rfd') document.getElementById('r-rfd-val').textContent = `${{val}} W`;
      if (param === 'cns') document.getElementById('r-cns-val').textContent = `${{val}} %`;

      drawRadar();
    }};

    function drawRadar() {{
      const canvas = document.getElementById('radar-canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width, h = canvas.height;
      const cx = w / 2, cy = h / 2;
      const radius = 145;

      ctx.clearRect(0, 0, w, h);

      const labels = ['VO2 Max', 'Lactate Threshold', 'Bar Velocity', 'Peak RFD', 'CNS Recovery'];
      const axesCount = 5;
      const angleStep = (Math.PI * 2) / axesCount;

      // Draw Concentric Webs
      for (let level = 1; level <= 5; level++) {{
        const r = (radius / 5) * level;
        ctx.beginPath();
        ctx.strokeStyle = level === 5 ? 'rgba(249, 115, 22, 0.4)' : 'rgba(255, 255, 255, 0.08)';
        ctx.lineWidth = level === 5 ? 1.5 : 1;
        for (let i = 0; i < axesCount; i++) {{
          const angle = i * angleStep - Math.PI / 2;
          const x = cx + Math.cos(angle) * r;
          const y = cy + Math.sin(angle) * r;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }}
        ctx.closePath();
        ctx.stroke();
      }}

      // Draw Radial Axis Lines & Labels
      ctx.font = 'bold 12px "Barlow Condensed", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      for (let i = 0; i < axesCount; i++) {{
        const angle = i * angleStep - Math.PI / 2;
        const x = cx + Math.cos(angle) * radius;
        const y = cy + Math.sin(angle) * radius;

        ctx.beginPath();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.moveTo(cx, cy);
        ctx.lineTo(x, y);
        ctx.stroke();

        const lx = cx + Math.cos(angle) * (radius + 24);
        const ly = cy + Math.sin(angle) * (radius + 24);
        ctx.fillStyle = '#a1a1aa';
        ctx.fillText(labels[i], lx, ly);
      }}

      // Calculate Normalized Values (0 to 1)
      const normValues = [
        (radarData.vo2 - 40) / (85 - 40),
        (radarData.lactate - 50) / (98 - 50),
        (radarData.velocity - 10) / (32 - 10),
        (radarData.rfd - 800) / (2800 - 800),
        (radarData.cns - 40) / (100 - 40)
      ];

      // Draw Filled Radar Polygon
      ctx.beginPath();
      for (let i = 0; i < axesCount; i++) {{
        const angle = i * angleStep - Math.PI / 2;
        const val = Math.max(0.08, Math.min(1, normValues[i]));
        const r = radius * val;
        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }}
      ctx.closePath();
      ctx.fillStyle = 'rgba(249, 115, 22, 0.32)';
      ctx.fill();
      ctx.strokeStyle = '#f97316';
      ctx.lineWidth = 2.5;
      ctx.shadowColor = '#f97316';
      ctx.shadowBlur = 14;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Draw Glowing Vertex Points
      for (let i = 0; i < axesCount; i++) {{
        const angle = i * angleStep - Math.PI / 2;
        const val = Math.max(0.08, Math.min(1, normValues[i]));
        const r = radius * val;
        const x = cx + Math.cos(angle) * r;
        const y = cy + Math.sin(angle) * r;

        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#fff';
        ctx.fill();
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.stroke();
      }}

      // Calculate Composite Apex Competitor Index (ACI)
      const composite = (
        normValues[0] * 0.22 +
        normValues[1] * 0.22 +
        normValues[2] * 0.20 +
        normValues[3] * 0.20 +
        normValues[4] * 0.16
      ) * 100;

      const aciScoreEl = document.getElementById('aci-score');
      const aciTierEl = document.getElementById('aci-tier');
      if (aciScoreEl) aciScoreEl.innerHTML = `${{composite.toFixed(1)}} <span>/ 100</span>`;
      if (aciTierEl) {{
        if (composite >= 92) aciTierEl.textContent = 'National Elite Tier';
        else if (composite >= 80) aciTierEl.textContent = 'Rx Competitor Podium';
        else aciTierEl.textContent = 'Athletic Conditioning Tier';
      }}
    }}
    drawRadar();

    // --- ADVANCED COMPONENT 4: Neural WOD Protocol Synthesizer ---
    let currentSynthGoal = 'olympic';
    let currentSynthTier = 'rx';

    window.setSynthGoal = function(goal, btn) {{
      currentSynthGoal = goal;
      document.querySelectorAll('#goal-pills .synth-pill').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }};

    window.setSynthTier = function(tier, btn) {{
      currentSynthTier = tier;
      document.querySelectorAll('#tier-pills .synth-pill').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }};

    window.synthesizeNeuralWOD = function() {{
      initAudio();
      playChime(740);

      const barLb = currentWeight || 225;
      const protocols = {{
        olympic: {{
          title: `PROTOCOL: TITAN OLYMPIC ACCELERATION COMPLEX (@ ${{barLb}} LBS)`,
          time: 'Time Cap: 16:00 • Target Zone: Zone 4 (172-184 BPM)',
          primer: [
            '500m SkiErg @ 1:52 pace',
            '10 Tall Snatch Balances & Duck Walks',
            '8 Halting Clean Deadlifts (Paused at Knee)'
          ],
          main: [
            'Every 2:00 for 7 Rounds (Heavy Wave):',
            `<b>1 Squat Clean + 2 Front Squats + 1 Split Jerk @ ${{barLb}} LBS</b>`,
            '12 Chest-to-Bar Pull-Ups Unbroken',
            '10 Strict Handstand Push-Ups'
          ],
          flush: [
            '4:00 Easy Spin Concept2 BikeErg @ 85 RPM',
            'Thoracic Foam Roller Spine Extension'
          ]
        }},
        engine: {{
          title: `PROTOCOL: VO2 LACTATE INFERNO (@ ${{barLb}} LBS)`,
          time: 'Time Cap: 20:00 • Target Zone: Zone 5 Threshold (185+ BPM)',
          primer: [
            '3 Rounds: 200m Run + 10 Air Squats + 10 Cossack Squats',
            'Wrist & Ankle Articular Rotations'
          ],
          main: [
            '4 Rounds For Time:',
            '25 Calorie Assault AirBike Sprint',
            `<b>9 Deadlifts @ ${{barLb}} LBS (Unbroken Cadence)</b>`,
            '15 Burpee Box Jump Overs (24" / 30")',
            '50 Double Unders'
          ],
          flush: [
            '400m Walking Cool-Down',
            'Box Breathing (4s In / 4s Hold / 4s Out / 4s Hold)'
          ]
        }},
        hypertrophy: {{
          title: `PROTOCOL: POSTERIOR CHAIN ARMOR & DENSITY (@ ${{barLb}} LBS)`,
          time: 'Time Cap: 24:00 • Target Zone: Zone 3 Steady State',
          primer: [
            '15 Banded Good Mornings',
            '12 Cuban Presses with Light Dumbbells',
            '1:00 Sorenson Back Extension Hold'
          ],
          main: [
            '5 Working Sets for Quality:',
            `<b>6 Heavy Barbell Good Mornings @ ${{Math.round(barLb * 0.65)}} LBS</b>`,
            `<b>8 Pendlay Deficit Rows @ ${{Math.round(barLb * 0.75)}} LBS</b>`,
            '12 GHD Sit-Ups (Strict Controlled)',
            '20 Heavy Dumbbell Hammer Curls'
          ],
          flush: [
            'Hamstring PNF Stretch with Resistance Band',
            'Couch Stretch (2:00 per side)'
          ]
        }},
        hero: {{
          title: `PROTOCOL: HERO BENCHMARK 'IRON VANGUARD' (@ ${{barLb}} LBS)`,
          time: 'Time Cap: 28:00 • Target Zone: Competitive Willpower Zone 5',
          primer: [
            '800m Jog + 20 Walking Lunges',
            '15 PVC Pipe Dislocates + 10 Inchworms'
          ],
          main: [
            'For Time (Wear 20 LBS Weight Vest if Rx+):',
            '1 Mile Echo Bike Buy-In',
            `<b>21 Power Cleans @ ${{barLb}} LBS</b>`,
            '21 Ring Muscle-Ups',
            `<b>15 Power Cleans @ ${{barLb}} LBS</b>`,
            '15 Ring Muscle-Ups',
            `<b>9 Power Cleans @ ${{barLb}} LBS</b>`,
            '9 Ring Muscle-Ups',
            '1 Mile Echo Bike Cash-Out'
          ],
          flush: [
            'Cold Shower / Plunge Protocol @ 42°F',
            '500ml Electrolyte Replenishment Flush'
          ]
        }}
      }};

      const selected = protocols[currentSynthGoal] || protocols.olympic;
      document.getElementById('wod-name').textContent = selected.title;
      document.getElementById('wod-time-cap').textContent = selected.time;

      const mainList = document.getElementById('wod-main-list');
      if (mainList) {{
        mainList.innerHTML = selected.main.map(m => `<li>${{m}}</li>`).join('');
      }}

      const box = document.getElementById('synth-output');
      if (box) {{
        box.style.opacity = '0.3';
        setTimeout(() => box.style.opacity = '1', 120);
      }}
    }};

    window.copyWODProtocol = function() {{
      const title = document.getElementById('wod-name').textContent;
      const sub = document.getElementById('wod-time-cap').textContent;
      const text = `${{title}}\n${{sub}}\n\nGenerated by Apex Athletic AI Engine.`;
      navigator.clipboard.writeText(text).then(() => {{
        initAudio();
        playChime(920);
        alert('📋 WOD Protocol successfully copied to clipboard!');
      }}).catch(() => {{
        alert('📋 Protocol copied: ' + title);
      }});
    }};
  </script>
</body>
</html>
"""


# ===================================================================
# 2. BESPOKE CULINARY / ARTISAN COFFEE ROASTERY LAYOUT
# ===================================================================
def build_culinary_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Master Artisanal Roastery & Editorial Tasting Room</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,500;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #0c0a09;
      --surface: #171412;
      --surface-glass: rgba(23, 20, 18, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --amber: #f59e0b;
      --amber-glow: rgba(245, 158, 11, 0.35);
      --terracotta: #ea580c;
      --text: #fafaf9;
      --text-muted: #a8a29e;
      --font-serif: 'Playfair Display', serif;
      --font-body: 'Plus Jakarta Sans', sans-serif;
      --transition: all 0.3s ease;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: var(--font-body); background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.7; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(12, 10, 9, 0.9); border-bottom: 1px solid var(--border);
      padding: 20px 48px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-family: var(--font-serif); font-size: 1.5rem; font-weight: 700; color: #fff; text-decoration: none; }}
    .nav-links {{ display: flex; gap: 32px; list-style: none; align-items: center; }}
    .nav-links a {{ color: var(--text-muted); text-decoration: none; font-size: 0.95rem; font-weight: 500; transition: var(--transition); }}
    .nav-links a:hover {{ color: var(--amber); }}
    .nav-cta {{
      background: var(--amber); color: #000 !important; font-weight: 700 !important;
      padding: 10px 22px; border-radius: 30px;
    }}

    .hero-editorial {{
      text-align: center; padding: 80px 24px 40px 24px; max-width: 900px; margin: 0 auto;
    }}
    .vintage-tag {{
      display: inline-block; font-family: var(--font-serif); font-style: italic;
      color: var(--amber); font-size: 1.1rem; margin-bottom: 16px; letter-spacing: 1px;
    }}
    .hero-editorial h1 {{
      font-family: var(--font-serif); font-size: clamp(3rem, 6vw, 4.8rem);
      font-weight: 900; line-height: 1.1; margin-bottom: 24px;
    }}
    .hero-editorial p {{ font-size: 1.2rem; color: var(--text-muted); margin-bottom: 36px; }}
    
    .canvas-center {{
      max-width: 960px; height: 460px; margin: 0 auto 80px auto; border-radius: 24px;
      background: radial-gradient(circle, #241c17 0%, #100d0b 100%);
      border: 1px solid rgba(245, 158, 11, 0.25); position: relative; overflow: hidden;
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .hud-steam-ctrl {{
      position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10;
    }}
    .steam-btn {{
      background: rgba(12, 10, 9, 0.85); border: 1px solid var(--border);
      color: #fff; padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer;
    }}
    .steam-btn.active {{ background: var(--amber); color: #000; border-color: var(--amber); }}

    /* Single Origin Cards */
    section {{ max-width: 1200px; margin: 0 auto 100px auto; padding: 0 32px; }}
    .sec-head {{ text-align: center; margin-bottom: 48px; }}
    .sec-head h2 {{ font-family: var(--font-serif); font-size: 2.8rem; margin-top: 8px; }}
    
    .origins-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }}
    .origin-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
      overflow: hidden; transition: var(--transition);
    }}
    .origin-card:hover {{ border-color: var(--amber); transform: translateY(-6px); }}
    .origin-card img {{ width: 100%; height: 220px; object-fit: cover; }}
    .origin-body {{ padding: 24px; }}
    .origin-score {{
      display: inline-block; background: rgba(245, 158, 11, 0.15); color: var(--amber);
      font-weight: 700; font-size: 0.85rem; padding: 4px 10px; border-radius: 20px; margin-bottom: 12px;
    }}
    .origin-body h3 {{ font-family: var(--font-serif); font-size: 1.5rem; margin-bottom: 8px; }}
    .origin-body p {{ color: var(--text-muted); font-size: 0.95rem; margin-bottom: 16px; }}
    .notes-tag {{ color: var(--amber); font-weight: 600; font-size: 0.9rem; }}

    /* Interactive Brew Ratio Calculator */
    .brew-box {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
      padding: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center;
    }}
    .brew-dial {{ font-family: var(--font-serif); font-size: 3.8rem; color: var(--amber); font-weight: 900; line-height: 1; }}

    footer {{ text-align: center; padding: 60px 24px; border-top: 1px solid var(--border); }}

    @media (max-width: 900px) {{
      .origins-grid {{ grid-template-columns: 1fr; }}
      .brew-box {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">☕ {brand}</a>
    <ul class="nav-links">
      <li><a href="#origins">Single-Origin Harvests</a></li>
      <li><a href="#brew-calc">Pour-Over Calculator</a></li>
      <li><a href="#roastery">The Roastery</a></li>
      <li><a href="#origins" class="nav-cta">Order Fresh Beans</a></li>
    </ul>
  </nav>

  <header class="hero-editorial" id="home">
    <div class="vintage-tag">Specialty Grade 1 &bull; Direct Farm Micro-Lots</div>
    <h1>The Art of The Perfect Extraction</h1>
    <p>Hand-selected single-origin arabica coffees, roasted in small batches to preserve terroir, delicate floral aromatics, and rich velvety mouthfeel.</p>
  </header>

  <div class="canvas-center">
    <div class="hud-steam-ctrl">
      <button class="steam-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Steam: On</button>
      <button class="steam-btn" id="btn-custom-2" onclick="toggleCustom2(this)">Heat: 205°F</button>
      <button class="steam-btn" id="btn-sound" onclick="toggleAudioFX(this)">🔊 Audio</button>
    </div>
    <div id="webgl-canvas-container" title="Drag to Orbit in 360°"></div>
  </div>

  <section id="origins">
    <div class="sec-head">
      <div class="vintage-tag">Current Harvest Vault</div>
      <h2>Exceptional Terroirs</h2>
    </div>
    <div class="origins-grid">
      <div class="origin-card">
        <img src="{c1}" alt="Ethiopia Yirgacheffe">
        <div class="origin-body">
          <span class="origin-score">Q-Score: 91.5 &bull; Natural</span>
          <h3>Ethiopia Yirgacheffe</h3>
          <p>Grown at 2,100 meters on volcanic soil. Sun-dried on raised African beds for 21 days.</p>
          <div class="notes-tag">Notes: Bergamot, Jasmine, Wild Peach</div>
        </div>
      </div>
      <div class="origin-card">
        <img src="{c2}" alt="Colombia Huila">
        <div class="origin-body">
          <span class="origin-score">Q-Score: 89.2 &bull; Washed</span>
          <h3>Colombia Huila Reserve</h3>
          <p>Hand-harvested Pink Bourbon variety. Fermented for 36 hours in temperature-controlled tanks.</p>
          <div class="notes-tag">Notes: Panela, Red Apple, Dark Cocoa</div>
        </div>
      </div>
      <div class="origin-card">
        <img src="{c3}" alt="Guatemala Antigua">
        <div class="origin-body">
          <span class="origin-score">Q-Score: 88.8 &bull; Anaerobic</span>
          <h3>Guatemala Antigua San Marcos</h3>
          <p>Shade-grown under gravilea canopies in the shadows of the Fuego volcano.</p>
          <div class="notes-tag">Notes: Caramelized Honey, Blood Orange</div>
        </div>
      </div>
    </div>
  </section>

  <section id="brew-calc">
    <div class="sec-head">
      <div class="vintage-tag">Precision Brew Ratio</div>
      <h2>Pour-Over Brew Calculator</h2>
    </div>
    <div class="brew-box">
      <div>
        <h3 style="font-family:var(--font-serif);font-size:1.8rem;margin-bottom:12px;">Dial In Your Golden Cup</h3>
        <p style="color:var(--text-muted);margin-bottom:24px;">Adjust ground coffee grams to compute exact water mass (1:16.5 ratio) and pour intervals.</p>
        <label style="font-weight:600;display:block;margin-bottom:8px;">Coffee Dose: <span id="dose-val" style="color:var(--amber);">20 grams</span></label>
        <input type="range" id="coffee-dose" min="12" max="45" value="20" style="width:100%;accent-color:var(--amber);" oninput="updateBrewCalc()">
      </div>
      <div style="background:#100d0b;padding:30px;border-radius:14px;text-align:center;">
        <div class="brew-dial" id="water-val">330 ml</div>
        <div style="color:var(--text-muted);font-weight:600;text-transform:uppercase;margin-top:6px;">Filtered Water @ 205°F</div>
        <div style="color:var(--amber);margin-top:16px;font-weight:700;">Extraction Window: 3 min 15 sec</div>
      </div>
    </div>
  </section>

  <footer>
    <h3 style="font-family:var(--font-serif);font-size:1.5rem;margin-bottom:8px;">{brand}</h3>
    <p style="color:var(--text-muted);font-size:0.9rem;">Specialty Roastery & Tasting Room &bull; Crafted by D.E.E.P Sovereign Engine &bull; 2026</p>
  </footer>

  <script>
    function updateBrewCalc() {{
      const dose = parseInt(document.getElementById('coffee-dose').value);
      document.getElementById('dose-val').textContent = `${{dose}} grams`;
      const water = Math.round(dose * 16.5);
      document.getElementById('water-val').textContent = `${{water}} ml`;
    }}
    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 3. BESPOKE AUTOMOTIVE / HYPERCAR COCKPIT LAYOUT
# ===================================================================
def build_automotive_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Electric Hypercar Telemetry</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Space+Grotesk:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #07090e;
      --surface: #0f141f;
      --border: rgba(255, 255, 255, 0.09);
      --cyan: #00f0ff;
      --redline: #ef4444;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --font-tech: 'Space Grotesk', sans-serif;
      --font-hud: 'Rajdhani', sans-serif;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.6; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(7, 9, 14, 0.9); border-bottom: 1px solid var(--border);
      padding: 16px 40px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-family: var(--font-tech); font-size: 1.4rem; font-weight: 800; color: #fff; text-decoration: none; }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; }}
    .nav-links a {{ color: var(--text-muted); text-decoration: none; font-size: 0.95rem; font-weight: 600; }}
    .nav-links a:hover {{ color: var(--cyan); }}

    .cockpit-hero {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 40px;
      padding: 60px 48px; max-width: 1440px; margin: 0 auto; align-items: center;
    }}
    .cockpit-hero h1 {{
      font-family: var(--font-tech); font-size: clamp(2.8rem, 5vw, 4.4rem);
      font-weight: 800; line-height: 1.1; margin-bottom: 20px;
    }}
    .cyan-text {{ color: var(--cyan); text-shadow: 0 0 25px rgba(0, 240, 255, 0.5); }}
    
    .canvas-hud-box {{
      height: 480px; border-radius: 16px; background: radial-gradient(circle, #131c2b 0%, #080c14 100%);
      border: 1px solid rgba(0, 240, 255, 0.3); position: relative; overflow: hidden;
      box-shadow: 0 0 50px rgba(0, 240, 255, 0.15);
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .hud-controls-top {{ position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10; }}
    .hud-btn {{
      background: rgba(15, 20, 31, 0.85); border: 1px solid var(--border);
      color: #fff; padding: 6px 12px; border-radius: 6px; font-family: var(--font-hud);
      font-size: 0.95rem; font-weight: 700; text-transform: uppercase; cursor: pointer;
    }}
    .hud-btn.active {{ background: var(--cyan); color: #000; border-color: var(--cyan); }}

    /* Telemetry Telemetry Strip */
    .telemetry-grid {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
      max-width: 1440px; margin: 0 auto 80px auto; padding: 0 48px;
    }}
    .tele-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
      padding: 24px; text-align: center;
    }}
    .tele-val {{ font-family: var(--font-hud); font-size: 3.4rem; font-weight: 800; color: var(--cyan); line-height: 1; }}
    .tele-lbl {{ font-family: var(--font-hud); font-size: 1.1rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; }}

    /* Track Lap Times */
    section {{ max-width: 1440px; margin: 0 auto 100px auto; padding: 0 48px; }}
    .track-table {{
      width: 100%; border-collapse: collapse; background: var(--surface);
      border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
    }}
    .track-table th, .track-table td {{
      padding: 18px 24px; text-align: left; border-bottom: 1px solid var(--border);
    }}
    .track-table th {{ font-family: var(--font-hud); font-size: 1.2rem; text-transform: uppercase; color: var(--cyan); }}
    .lap-record {{ font-family: var(--font-hud); font-size: 1.4rem; font-weight: 700; color: #fff; }}

    footer {{ text-align: center; padding: 40px; border-top: 1px solid var(--border); }}

    @media (max-width: 900px) {{
      .cockpit-hero {{ grid-template-columns: 1fr; }}
      .telemetry-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">⚡ {brand}</a>
    <ul class="nav-links">
      <li><a href="#telemetry">Telemetry</a></li>
      <li><a href="#records">Lap Records</a></li>
      <li><a href="#config">Configurator</a></li>
    </ul>
  </nav>

  <header class="cockpit-hero" id="home">
    <div>
      <div style="font-family:var(--font-hud);font-size:1.2rem;font-weight:700;color:var(--cyan);margin-bottom:12px;letter-spacing:1px;">SYNCHRONOUS ELECTRIC ARCHITECTURE &bull; 800V</div>
      <h1>Sub-Second Aero Velocity: <span class="cyan-text">{brand}</span></h1>
      <p style="color:var(--text-muted);font-size:1.15rem;margin-bottom:32px;">Quad-motor torque vectoring delivering 1,900 brake horsepower with dynamic wind-tunnel active downforce.</p>
      <a href="#telemetry" style="background:var(--cyan);color:#000;padding:14px 32px;border-radius:6px;font-family:var(--font-hud);font-size:1.2rem;font-weight:800;text-decoration:none;text-transform:uppercase;">Inspect Telemetry ➔</a>
    </div>

    <div class="canvas-hud-box">
      <div class="hud-controls-top">
        <button class="hud-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Aero Wing: Active</button>
        <button class="hud-btn" id="btn-custom-2" onclick="toggleCustom2(this)">Speed: 300 MPH</button>
        <button class="hud-btn" id="btn-theme" onclick="cycleCustomTheme(this)">🎨 Livery</button>
        <button class="hud-btn" id="btn-sound" onclick="toggleAudioFX(this)">🔊 Audio</button>
      </div>
      <div id="webgl-canvas-container" title="Drag to Orbit in 360°"></div>
    </div>
  </header>

  <div class="telemetry-grid" id="telemetry">
    <div class="tele-card">
      <div class="tele-val">1.74s</div>
      <div class="tele-lbl">0-60 MPH Acceleration</div>
    </div>
    <div class="tele-card">
      <div class="tele-val">320 MPH</div>
      <div class="tele-lbl">Terminal Velocity</div>
    </div>
    <div class="tele-card">
      <div class="tele-val">1,200 kg</div>
      <div class="tele-lbl">Peak Ground Downforce</div>
    </div>
    <div class="tele-card">
      <div class="tele-val">1,900 HP</div>
      <div class="tele-lbl">Quad Motor Output</div>
    </div>
  </div>

  <section id="records">
    <h2 style="font-family:var(--font-tech);font-size:2.2rem;margin-bottom:24px;">Global Circuit Records</h2>
    <table class="track-table">
      <thead>
        <tr>
          <th>Circuit</th>
          <th>Sector 1</th>
          <th>Sector 2</th>
          <th>Official Lap Record</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Nürburgring Nordschleife (Germany)</td>
          <td>1:22.4</td>
          <td>2:14.8</td>
          <td class="lap-record" style="color:var(--cyan);">6:38.20</td>
        </tr>
        <tr>
          <td>WeatherTech Raceway Laguna Seca (USA)</td>
          <td>0:24.1</td>
          <td>0:31.9</td>
          <td class="lap-record">1:21.45</td>
        </tr>
        <tr>
          <td>Circuit de Spa-Francorchamps (Belgium)</td>
          <td>0:42.5</td>
          <td>0:48.2</td>
          <td class="lap-record">2:09.12</td>
        </tr>
      </tbody>
    </table>
  </section>

  <footer>
    <div style="font-family:var(--font-tech);font-size:1.2rem;font-weight:700;">{brand} High-Performance Telemetry</div>
    <p style="color:var(--text-muted);font-size:0.85rem;margin-top:6px;">Engineered by D.E.E.P Sovereign Engine &bull; 2026</p>
  </footer>

  <script>
    {scripts}
  </script>
</body>
</html>
"""



# ===================================================================
# 4. BESPOKE CYBERSECURITY / DEVSECOPS SOC COMMAND CENTER LAYOUT
# ===================================================================
def build_cybersecurity_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Autonomous Threat Defense & Next-Gen SOC Command</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Space+Grotesk:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #05080f;
      --surface: #0a101d;
      --surface-glass: rgba(10, 16, 29, 0.88);
      --border: rgba(0, 240, 255, 0.18);
      --border-alert: rgba(239, 68, 68, 0.35);
      --cyan: #00f0ff;
      --cyan-glow: rgba(0, 240, 255, 0.35);
      --emerald: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --font-mono: 'JetBrains Mono', monospace;
      --font-heading: 'Space Grotesk', sans-serif;
      --transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); }}
    body {{
      overflow-x: hidden; min-height: 100vh; line-height: 1.6;
      background-image: radial-gradient(rgba(0, 240, 255, 0.05) 1px, transparent 1px);
      background-size: 32px 32px;
    }}

    /* Tactical Terminal Nav */
    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(5, 8, 15, 0.92); border-bottom: 1px solid var(--border);
      padding: 14px 40px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{
      display: flex; align-items: center; gap: 12px; font-family: var(--font-mono);
      font-size: 1.25rem; font-weight: 800; color: #fff; text-decoration: none;
    }}
    .sec-badge {{
      display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px;
      background: rgba(16, 185, 129, 0.15); border: 1px solid var(--emerald);
      border-radius: 4px; font-size: 0.72rem; color: var(--emerald); font-weight: 700;
    }}
    .pulse-dot {{
      width: 6px; height: 6px; border-radius: 50%; background: var(--emerald);
      box-shadow: 0 0 8px var(--emerald); animation: radar-blink 1.5s infinite;
    }}
    @keyframes radar-blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}

    .nav-links {{ display: flex; gap: 28px; list-style: none; align-items: center; }}
    .nav-links a {{
      font-family: var(--font-mono); font-size: 0.88rem; color: var(--text-muted);
      text-decoration: none; transition: var(--transition);
    }}
    .nav-links a:hover {{ color: var(--cyan); }}
    .nav-cta {{
      background: var(--cyan) !important; color: #000 !important; font-weight: 800 !important;
      padding: 8px 18px; border-radius: 4px; box-shadow: 0 0 15px var(--cyan-glow);
    }}

    /* Threat Status Bar */
    .status-bar {{
      background: #020408; border-bottom: 1px solid var(--border);
      padding: 8px 40px; display: flex; justify-content: space-between; align-items: center;
      font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted);
    }}
    .status-bar span b {{ color: var(--cyan); }}

    /* Hero SOC Command */
    .hero-soc {{
      max-width: 1400px; margin: 0 auto; padding: 60px 40px;
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 40px; align-items: center;
    }}
    .hero-soc h1 {{
      font-family: var(--font-heading); font-size: clamp(2.6rem, 5vw, 4.2rem);
      font-weight: 800; line-height: 1.1; margin-bottom: 20px;
    }}
    .hero-soc p {{
      color: var(--text-muted); font-size: 1.15rem; line-height: 1.7; margin-bottom: 32px;
    }}
    .hero-actions {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
    .btn-tactical {{
      background: linear-gradient(135deg, var(--cyan), #0284c7); color: #000;
      font-family: var(--font-mono); font-weight: 800; font-size: 0.95rem;
      padding: 14px 28px; border-radius: 6px; text-decoration: none; text-transform: uppercase;
      box-shadow: 0 0 25px var(--cyan-glow); display: inline-flex; align-items: center; gap: 10px;
    }}
    .btn-tactical:hover {{ transform: translateY(-2px); box-shadow: 0 0 35px var(--cyan-glow); }}
    .btn-secondary {{
      background: var(--surface-glass); border: 1px solid var(--border); color: #fff;
      font-family: var(--font-mono); font-size: 0.9rem; font-weight: 600; padding: 14px 24px;
      border-radius: 6px; text-decoration: none;
    }}

    /* 3D Laser Firewall Canvas */
    .canvas-soc-box {{
      height: 480px; border-radius: 12px; background: radial-gradient(circle, #0e172a 0%, #05080f 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
      box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 40px var(--cyan-glow);
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .soc-hud {{
      position: absolute; top: 14px; left: 18px; right: 18px;
      display: flex; justify-content: space-between; align-items: center; z-index: 10;
    }}
    .soc-hud-badge {{
      font-family: var(--font-mono); font-size: 0.75rem; color: var(--cyan);
      background: rgba(5, 8, 15, 0.85); padding: 5px 12px; border-radius: 4px;
      border: 1px solid var(--border); text-transform: uppercase;
    }}
    .soc-hud-btns {{ display: flex; gap: 8px; }}
    .soc-btn {{
      background: rgba(10, 16, 29, 0.9); border: 1px solid var(--border);
      color: #fff; font-family: var(--font-mono); font-size: 0.78rem; font-weight: 700;
      padding: 5px 12px; border-radius: 4px; cursor: pointer; transition: var(--transition);
    }}
    .soc-btn.active {{ background: var(--cyan); color: #000; border-color: var(--cyan); }}

    /* Live Telemetry KPI Strip */
    .kpi-strip {{
      max-width: 1400px; margin: 0 auto 70px auto; padding: 0 40px;
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
    }}
    .kpi-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
      padding: 24px; position: relative; overflow: hidden;
    }}
    .kpi-card::before {{
      content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
      background: var(--cyan);
    }}
    .kpi-card h3 {{
      font-family: var(--font-mono); font-size: 2.8rem; font-weight: 800; color: var(--cyan); line-height: 1;
    }}
    .kpi-card p {{
      font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-muted); margin-top: 6px; text-transform: uppercase;
    }}

    /* Interactive CVE Threat Simulator */
    .sim-section {{ max-width: 1400px; margin: 0 auto 100px auto; padding: 0 40px; }}
    .sec-header {{ margin-bottom: 32px; }}
    .sec-tag {{
      font-family: var(--font-mono); font-size: 0.82rem; color: var(--cyan);
      text-transform: uppercase; letter-spacing: 1px;
    }}
    .sec-header h2 {{ font-family: var(--font-heading); font-size: 2.4rem; margin-top: 6px; }}
    
    .sim-grid {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 32px;
      background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 36px;
    }}
    .sim-vectors {{ display: flex; flex-direction: column; gap: 12px; }}
    .vector-btn {{
      background: #060b14; border: 1px solid var(--border); padding: 16px 20px;
      border-radius: 6px; color: #fff; font-family: var(--font-mono); text-align: left;
      cursor: pointer; transition: var(--transition); display: flex; justify-content: space-between; align-items: center;
    }}
    .vector-btn:hover {{ border-color: var(--cyan); background: rgba(0, 240, 255, 0.05); }}
    .vector-btn.active {{
      border-color: var(--cyan); background: rgba(0, 240, 255, 0.12);
      box-shadow: inset 4px 0 0 var(--cyan);
    }}
    .vector-title {{ font-weight: 700; font-size: 0.95rem; }}
    .vector-meta {{ font-size: 0.78rem; color: var(--text-muted); }}

    .sim-console {{
      background: #020408; border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px;
      padding: 24px; font-family: var(--font-mono); font-size: 0.85rem; display: flex;
      flex-direction: column; justify-content: space-between;
    }}
    .console-header {{
      display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1);
      padding-bottom: 12px; margin-bottom: 16px; color: var(--cyan); font-weight: 700;
    }}
    .console-log {{
      flex: 1; overflow-y: auto; max-height: 220px; line-height: 1.8; color: #cbd5e1;
    }}
    .console-log .log-crit {{ color: var(--red); font-weight: 700; }}
    .console-log .log-mit {{ color: var(--emerald); font-weight: 700; }}
    .console-log .log-info {{ color: var(--cyan); }}

    /* Zero Trust Pillars */
    .pillars-grid {{
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px;
      max-width: 1400px; margin: 0 auto 100px auto; padding: 0 40px;
    }}
    .pillar-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
      overflow: hidden; transition: var(--transition);
    }}
    .pillar-card:hover {{ border-color: var(--cyan); transform: translateY(-5px); }}
    .pillar-card img {{ width: 100%; height: 200px; object-fit: cover; }}
    .pillar-body {{ padding: 24px; }}
    .pillar-tag {{
      display: inline-block; font-family: var(--font-mono); font-size: 0.75rem;
      color: var(--cyan); background: rgba(0, 240, 255, 0.1); padding: 4px 10px; border-radius: 4px; margin-bottom: 12px;
    }}
    .pillar-body h3 {{ font-family: var(--font-heading); font-size: 1.35rem; margin-bottom: 10px; }}
    .pillar-body p {{ color: var(--text-muted); font-size: 0.92rem; line-height: 1.6; }}

    footer {{
      text-align: center; padding: 50px 24px; border-top: 1px solid var(--border);
      font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-muted);
    }}

    @media (max-width: 960px) {{
      .hero-soc {{ grid-template-columns: 1fr; }}
      .kpi-strip {{ grid-template-columns: 1fr 1fr; }}
      .sim-grid {{ grid-template-columns: 1fr; }}
      .pillars-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">
      🛡️ {brand}
      <span class="sec-badge"><span class="pulse-dot"></span> ZERO-TRUST SOC</span>
    </a>
    <ul class="nav-links">
      <li><a href="#threat-sim">CVE Simulator</a></li>
      <li><a href="#architecture">Zero-Trust Matrix</a></li>
      <li><a href="#telemetry">Telemetry Feed</a></li>
      <li><a href="#threat-sim" class="nav-cta">Deploy Shield</a></li>
    </ul>
  </nav>

  <div class="status-bar">
    <span>SYSTEM STATUS: <b style="color:var(--emerald);">ALL DEFENSE TIERS GREEN</b></span>
    <span>GLOBAL THREAT INDEX: <b>DEFCON 2 (ELEVATED RESILIENCE)</b></span>
    <span>ENCRYPT: <b>AES-256-GCM / POST-QUANTUM KYBER</b></span>
  </div>

  <header class="hero-soc" id="home">
    <div>
      <div style="font-family:var(--font-mono);font-size:0.85rem;color:var(--cyan);margin-bottom:12px;letter-spacing:1.5px;font-weight:700;">
        ⚡ AUTONOMOUS AGENTIC CYBER DEFENSE
      </div>
      <h1>Sovereign Zero-Trust Defense: <span style="color:var(--cyan);">{brand}</span></h1>
      <p>Sub-millisecond automated threat containment, kernel-level eBPF behavioral telemetry, and quantum-resistant cryptographic shields guarding mission-critical enterprise infrastructure.</p>
      <div class="hero-actions">
        <a href="#threat-sim" class="btn-tactical">Launch Threat Simulator ➔</a>
        <a href="#architecture" class="btn-secondary">Inspect Architecture</a>
      </div>
    </div>

    <div class="canvas-soc-box">
      <div class="soc-hud">
        <div class="soc-hud-badge">Laser Firewall: ACTIVE &bull; 60 FPS</div>
        <div class="soc-hud-btns">
          <button class="soc-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Beam: Scan</button>
          <button class="soc-btn" id="btn-custom-2" onclick="toggleCustom2(this)">Matrix: Fast</button>
          <button class="soc-btn" id="btn-sound" onclick="toggleAudioFX(this)">🔊 Audio</button>
        </div>
      </div>
      <div id="webgl-canvas-container" title="360° Threat Radar Mesh"></div>
    </div>
  </header>

  <div class="kpi-strip" id="telemetry">
    <div class="kpi-card">
      <h3>0.04ms</h3>
      <p>Mean Containment Time</p>
    </div>
    <div class="kpi-card">
      <h3>100%</h3>
      <p>Zero-Day Exploit Catch</p>
    </div>
    <div class="kpi-card">
      <h3>2.4 TB/s</h3>
      <p>DDoS Scrubbing Capacity</p>
    </div>
    <div class="kpi-card">
      <h3>Post-Q</h3>
      <p>Kyber-1024 Lattice Security</p>
    </div>
  </div>

  <section class="sim-section" id="threat-sim">
    <div class="sec-header">
      <div class="sec-tag">Interactive Incident Playground</div>
      <h2>Automated CVE Exploit & Containment Engine</h2>
    </div>
    <div class="sim-grid">
      <div class="sim-vectors">
        <div class="vector-btn active" onclick="simulateAttack('cve1', this)">
          <div>
            <div class="vector-title">CVE-2026-9041: Linux Kernel eBPF Privilege Escalation</div>
            <div class="vector-meta">Severity: CVSS 9.8 Critical &bull; Vector: Local Root Exploit</div>
          </div>
          <span style="color:var(--red);font-weight:800;">CRITICAL</span>
        </div>
        <div class="vector-btn" onclick="simulateAttack('cve2', this)">
          <div>
            <div class="vector-title">Zero-Day Blind SQL Injection via GraphQL API</div>
            <div class="vector-meta">Severity: CVSS 8.6 High &bull; Vector: Remote Data Exfiltration</div>
          </div>
          <span style="color:var(--amber);font-weight:800;">HIGH</span>
        </div>
        <div class="vector-btn" onclick="simulateAttack('cve3', this)">
          <div>
            <div class="vector-title">BGP Anycast Routing Hijack & Man-in-the-Middle</div>
            <div class="vector-meta">Severity: CVSS 8.9 High &bull; Vector: Autonomous System Spoofing</div>
          </div>
          <span style="color:var(--amber);font-weight:800;">HIGH</span>
        </div>
        <div class="vector-btn" onclick="simulateAttack('cve4', this)">
          <div>
            <div class="vector-title">Volumetric SYN/UDP Flood (1.8 Tbps Multi-Vector)</div>
            <div class="vector-meta">Severity: CVSS 7.5 Medium &bull; Vector: L4 Edge Exhaustion</div>
          </div>
          <span style="color:var(--cyan);font-weight:800;">VOLUMETRIC</span>
        </div>
      </div>

      <div class="sim-console">
        <div class="console-header">
          <span>TERMINAL // INCIDENT REMEDIATION FEED</span>
          <span id="threat-timer">T+0.00ms</span>
        </div>
        <div class="console-log" id="sim-log">
          <div>[00:00:01] <span class="log-info">INIT:</span> Sensor telemetry synchronized across 128 microservices.</div>
          <div>[00:00:02] <span class="log-crit">ALERT [CVE-2026-9041]:</span> Anomaly detected in syscall ring buffer. Unverified eBPF bytecode loaded.</div>
          <div>[00:00:02] <span class="log-info">ISOLATE:</span> Container cgroup frozen in 0.038ms. Memory dump quarantined.</div>
          <div>[00:00:03] <span class="log-mit">MITIGATED:</span> Immutable kernel image re-instantiated. Zero data exfiltration verified.</div>
        </div>
        <div style="margin-top:16px;display:flex;gap:12px;">
          <button onclick="retriggerSimulation()" style="background:var(--cyan);color:#000;border:none;padding:8px 16px;border-radius:4px;font-family:var(--font-mono);font-weight:800;cursor:pointer;">⚡ RE-TRIGGER CONTAINMENT</button>
        </div>
      </div>
    </div>
  </section>

  <section class="pillars-grid" id="architecture">
    <div class="pillar-card">
      <img src="{c1}" alt="Zero Trust Architecture">
      <div class="pillar-body">
        <span class="pillar-tag">ARCHITECTURE</span>
        <h3>Continuous Identity Verification</h3>
        <p>Every packet, API call, and RPC transmission requires cryptographically signed mTLS identity tokens with ephemeral 60-second TTLs.</p>
      </div>
    </div>
    <div class="pillar-card">
      <img src="{c2}" alt="eBPF Threat Detection">
      <div class="pillar-body">
        <span class="pillar-tag">RUNTIME SENSORS</span>
        <h3>eBPF Behavioral Sentinel</h3>
        <p>Observes kernel system calls directly with zero overhead, spotting unauthorized privilege escalations and shell spawns instantaneously.</p>
      </div>
    </div>
    <div class="pillar-card">
      <img src="{c3}" alt="Lattice Cryptography">
      <div class="pillar-body">
        <span class="pillar-tag">POST-QUANTUM</span>
        <h3>ML-KEM / Kyber Lattice Vault</h3>
        <p>Future-proofs customer databases against quantum decryption harvesting with NIST-standardized module lattice key encapsulation.</p>
      </div>
    </div>
  </section>

  <footer>
    <p>🛡️ {brand} SOC &bull; Autonomous Cyber Defense Architecture &bull; 2026</p>
  </footer>

  <script>
    const attackScenarios = {{
      cve1: [
        '[00:00:01] <span class="log-info">INIT:</span> eBPF probes actively monitoring kernel ring buffers.',
        '[00:00:02] <span class="log-crit">ALERT [CVE-2026-9041]:</span> Unprivileged process attempted malicious BPF bytecode injection.',
        '[00:00:02] <span class="log-info">ACTION:</span> Process PID 4091 SIGKILL dispatched. PID namespace severed in 0.024ms.',
        '[00:00:03] <span class="log-mit">CONTAINED:</span> Zero-trust kernel integrity restored. Zero credentials compromised.'
      ],
      cve2: [
        '[00:00:01] <span class="log-info">INIT:</span> WAF deep packet inspection enabled on GraphQL gateway.',
        '[00:00:02] <span class="log-crit">ALERT [SQLi ZERO-DAY]:</span> Malformed boolean blind injection payload detected in query variable.',
        '[00:00:02] <span class="log-info">ACTION:</span> Upstream source IP 198.51.100.44 blackholed across BGP edge within 1.2ms.',
        '[00:00:03] <span class="log-mit">CONTAINED:</span> Sanitized dummy response returned to adversary. DB AST guardrail intact.'
      ],
      cve3: [
        '[00:00:01] <span class="log-info">INIT:</span> RPKI ROV (Route Origin Validation) monitoring BGP prefixes.',
        '[00:00:02] <span class="log-crit">ALERT [BGP HIJACK]:</span> AS65001 announcing unauthorized route for /24 sovereign prefix.',
        '[00:00:02] <span class="log-info">ACTION:</span> Automated peering tear-down with rogue transit provider initiated.',
        '[00:00:03] <span class="log-mit">CONTAINED:</span> Traffic re-routed via encrypted fiber backbone. MITM averted completely.'
      ],
      cve4: [
        '[00:00:01] <span class="log-info">INIT:</span> Anycast scrubbers receiving 120 Gbps baseline traffic.',
        '[00:00:02] <span class="log-crit">ALERT [VOLUMETRIC FLOOD]:</span> Sudden ingress spike: 1.84 Tbps UDP reflection from NTP amplifiers.',
        '[00:00:02] <span class="log-info">ACTION:</span> eBPF XDP hardware drop filters activated at edge NICs in sub-microsecond latency.',
        '[00:00:03] <span class="log-mit">CONTAINED:</span> 99.998% malicious UDP packets dropped at line rate. Legitimate users unaffected.'
      ]
    }};

    let currentAttack = 'cve1';
    window.simulateAttack = function(key, btn) {{
      currentAttack = key;
      document.querySelectorAll('.vector-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      retriggerSimulation();
    }};

    window.retriggerSimulation = function() {{
      initAudio();
      playSpatialTone(880, 'sine', 0.15);
      const logBox = document.getElementById('sim-log');
      logBox.innerHTML = '<div style="color:var(--cyan);">>>> RUNNING AUTOMATED THREAT MITIGATION PROTOCOL...</div>';
      
      const lines = attackScenarios[currentAttack];
      lines.forEach((line, idx) => {{
        setTimeout(() => {{
          logBox.innerHTML += `<div>${{line}}</div>`;
          logBox.scrollTop = logBox.scrollHeight;
          if (idx === 1) playSpatialTone(280, 'sawtooth', 0.2); // Alert buzz
          if (idx === lines.length - 1) playSpatialTone(660, 'sine', 0.25); // Mitigated chime
        }}, (idx + 1) * 320);
      }});
    }};

    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 5. BESPOKE LUXURY SWISS HORLOGERIE / SKELETON TOURBILLON LAYOUT
# ===================================================================
def build_luxury_watch_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Haute Horlogerie & Hand-Finished Skeleton Tourbillon</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;800;900&family=Playfair+Display:ital,wght@0,400;0,600;0,800;1,400&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #0a0908;
      --surface: #141210;
      --surface-glass: rgba(20, 18, 16, 0.82);
      --border: rgba(212, 175, 55, 0.16);
      --border-hover: rgba(212, 175, 55, 0.45);
      --gold: #d4af37;
      --gold-light: #fef08a;
      --gold-glow: rgba(212, 175, 55, 0.35);
      --text: #fdfbf7;
      --text-muted: #a8a29e;
      --font-display: 'Cinzel', serif;
      --font-serif: 'Playfair Display', serif;
      --font-body: 'Outfit', sans-serif;
      --transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: var(--font-body); background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.8; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(25px);
      background: rgba(10, 9, 8, 0.9); border-bottom: 1px solid var(--border);
      padding: 22px 60px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{
      font-family: var(--font-display); font-size: 1.4rem; font-weight: 800;
      color: #fff; text-decoration: none; letter-spacing: 2.5px;
    }}
    .nav-links {{ display: flex; gap: 36px; list-style: none; align-items: center; }}
    .nav-links a {{
      font-family: var(--font-body); font-size: 0.92rem; color: var(--text-muted);
      text-decoration: none; letter-spacing: 1px; text-transform: uppercase; transition: var(--transition);
    }}
    .nav-links a:hover {{ color: var(--gold); }}
    .nav-cta {{
      background: transparent !important; color: var(--gold) !important;
      border: 1px solid var(--gold); padding: 8px 24px; border-radius: 30px;
    }}
    .nav-cta:hover {{ background: var(--gold) !important; color: #000 !important; }}

    /* Centered Haute Horlogerie Hero */
    .hero-watch {{
      text-align: center; padding: 80px 24px 40px; max-width: 1000px; margin: 0 auto;
    }}
    .watch-crest {{
      font-family: var(--font-display); color: var(--gold); font-size: 0.9rem;
      letter-spacing: 3px; text-transform: uppercase; margin-bottom: 20px;
    }}
    .hero-watch h1 {{
      font-family: var(--font-display); font-size: clamp(2.8rem, 5.5vw, 4.8rem);
      font-weight: 700; line-height: 1.15; letter-spacing: 1px; margin-bottom: 24px;
    }}
    .gold-gradient {{
      background: linear-gradient(135deg, #fff 20%, var(--gold) 70%, var(--gold-light) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .hero-watch p {{
      color: var(--text-muted); font-size: 1.2rem; font-weight: 300; max-width: 680px;
      margin: 0 auto 36px; line-height: 1.8;
    }}

    /* 3D Skeleton Tourbillon Viewport */
    .canvas-watch-wrapper {{
      max-width: 1040px; height: 500px; margin: 0 auto 80px auto; border-radius: 24px;
      background: radial-gradient(circle at center, #1c1813 0%, #0a0908 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
      box-shadow: 0 25px 70px rgba(0,0,0,0.9), 0 0 50px var(--gold-glow);
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .watch-hud {{
      position: absolute; top: 18px; right: 24px; display: flex; gap: 10px; z-index: 10;
    }}
    .watch-btn {{
      background: rgba(15, 13, 11, 0.85); border: 1px solid var(--border);
      color: #fff; font-family: var(--font-body); font-size: 0.85rem; padding: 6px 16px;
      border-radius: 20px; cursor: pointer; transition: var(--transition);
    }}
    .watch-btn.active {{ background: var(--gold); color: #000; border-color: var(--gold); }}

    /* Interactive Mechanical Chronometer Widget */
    .chrono-sec {{ max-width: 1200px; margin: 0 auto 100px auto; padding: 0 40px; }}
    .chrono-box {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
      padding: 48px; display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center;
    }}
    .chrono-dial-wrap {{ text-align: center; }}
    .chrono-time {{
      font-family: var(--font-display); font-size: clamp(3rem, 5vw, 4.4rem);
      color: var(--gold); font-weight: 700; letter-spacing: 2px;
    }}
    .chrono-sub {{
      font-family: var(--font-body); font-size: 0.95rem; color: var(--text-muted);
      text-transform: uppercase; letter-spacing: 2px; margin-top: 6px;
    }}
    .chrono-btns {{ display: flex; gap: 12px; justify-content: center; margin-top: 28px; }}
    .chrono-btn {{
      background: transparent; border: 1px solid var(--gold); color: var(--gold);
      padding: 10px 24px; border-radius: 30px; font-family: var(--font-body);
      font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
      cursor: pointer; transition: var(--transition);
    }}
    .chrono-btn:hover {{ background: var(--gold); color: #000; }}
    .chrono-btn.primary {{ background: var(--gold); color: #000; }}

    /* Complications Grid */
    .complications-list {{ display: flex; flex-direction: column; gap: 16px; }}
    .comp-item {{
      background: #0d0c0a; border: 1px solid var(--border); padding: 18px 24px;
      border-radius: 10px; cursor: pointer; transition: var(--transition);
    }}
    .comp-item:hover, .comp-item.active {{
      border-color: var(--gold); background: rgba(212, 175, 55, 0.08);
    }}
    .comp-name {{ font-family: var(--font-display); font-size: 1.15rem; color: #fff; margin-bottom: 4px; }}
    .comp-desc {{ color: var(--text-muted); font-size: 0.88rem; }}

    /* Atelier Heritage Cards */
    .heritage-grid {{
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px;
      max-width: 1200px; margin: 0 auto 100px auto; padding: 0 40px;
    }}
    .heritage-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
      overflow: hidden; transition: var(--transition);
    }}
    .heritage-card:hover {{ border-color: var(--border-hover); transform: translateY(-6px); }}
    .heritage-card img {{ width: 100%; height: 240px; object-fit: cover; filter: brightness(0.9); }}
    .heritage-body {{ padding: 28px; }}
    .heritage-tag {{
      font-family: var(--font-display); font-size: 0.75rem; color: var(--gold);
      letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; display: inline-block;
    }}
    .heritage-body h3 {{ font-family: var(--font-serif); font-size: 1.45rem; margin-bottom: 12px; }}
    .heritage-body p {{ color: var(--text-muted); font-size: 0.95rem; font-weight: 300; }}

    footer {{
      text-align: center; padding: 60px 24px; border-top: 1px solid var(--border);
      font-family: var(--font-display); font-size: 0.88rem; color: var(--text-muted); letter-spacing: 1px;
    }}

    @media (max-width: 900px) {{
      .chrono-box {{ grid-template-columns: 1fr; }}
      .heritage-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">👑 {brand}</a>
    <ul class="nav-links">
      <li><a href="#chronometer">Chronometer</a></li>
      <li><a href="#calibre">Calibre 9000</a></li>
      <li><a href="#atelier">Atelier</a></li>
      <li><a href="#chronometer" class="nav-cta">Reserve Timepiece</a></li>
    </ul>
  </nav>

  <header class="hero-watch" id="home">
    <div class="watch-crest">GENÈVE POINÇON &bull; INDEPENDENT MANUFACTURE</div>
    <h1>The Sovereign Art of <span class="gold-gradient">{brand}</span></h1>
    <p>Engineered with a titanium flying tourbillon cage revolving once every 60 seconds, compensating gravitational distortion with 21,600 vph escapement precision.</p>
  </header>

  <div class="canvas-watch-wrapper">
    <div class="watch-hud">
      <button class="watch-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Tourbillon: 60s</button>
      <button class="watch-btn" id="btn-custom-2" onclick="toggleCustom2(this)">Bezel: Gold</button>
      <button class="watch-btn" id="btn-sound" onclick="toggleAudioFX(this)">🔊 Escapement Tick</button>
    </div>
    <div id="webgl-canvas-container" title="360° Skeleton Tourbillon Movement"></div>
  </div>

  <section class="chrono-sec" id="chronometer">
    <div class="chrono-box">
      <div class="chrono-dial-wrap">
        <div class="chrono-time" id="chrono-display">00:00.00</div>
        <div class="chrono-sub">COSC-Certified Mechanical Stopwatch</div>
        <div class="chrono-btns">
          <button class="chrono-btn primary" id="btn-chrono-start" onclick="toggleChrono()">Start</button>
          <button class="chrono-btn" onclick="splitLap()">Split Lap</button>
          <button class="chrono-btn" onclick="resetChrono()">Reset</button>
        </div>
      </div>

      <div class="complications-list">
        <div class="comp-item active" onclick="selectComplication('tourbillon', this)">
          <div class="comp-name">Single-Axis Flying Tourbillon</div>
          <div class="comp-desc">0.29g titanium cage with sapphire balance bridge and variable-inertia gyromax balance.</div>
        </div>
        <div class="comp-item" onclick="selectComplication('perpetual', this)">
          <div class="comp-name">Instantaneous Perpetual Calendar</div>
          <div class="comp-desc">Mechanical memory accounts for leap years and 30/31-day months until the year 2100.</div>
        </div>
        <div class="comp-item" onclick="selectComplication('repeater', this)">
          <div class="comp-name">Cathedral Gong Minute Repeater</div>
          <div class="comp-desc">Dual tempered steel gongs wrapped twice around the movement for acoustic resonance.</div>
        </div>
      </div>
    </div>
  </section>

  <section class="heritage-grid" id="atelier">
    <div class="heritage-card">
      <img src="{c1}" alt="Hand Anglage">
      <div class="heritage-body">
        <span class="heritage-tag">FINISHING</span>
        <h3>Hand-Beveled Anglage</h3>
        <p>Every bridge corner is chamfered to a precise 45-degree mirror polish using gentian wood pegs and diamond paste.</p>
      </div>
    </div>
    <div class="heritage-card">
      <img src="{c2}" alt="Côtes de Genève">
      <div class="heritage-body">
        <span class="heritage-tag">DECORATION</span>
        <h3>Côtes de Genève Guilloché</h3>
        <p>Straight-line circular damaskeening waves applied by hand to the nickel silver mainplates in the Val-de-Travers atelier.</p>
      </div>
    </div>
    <div class="heritage-card">
      <img src="{c3}" alt="Flame Blued Screws">
      <div class="heritage-body">
        <span class="heritage-tag">TEMPERING</span>
        <h3>Flame-Blued Steel Screws</h3>
        <p>Heated to exactly 295°C to form an ultra-durable specular blue oxide layer protecting against friction and wear.</p>
      </div>
    </div>
  </section>

  <footer>
    <p>👑 {brand} Haute Horlogerie &bull; Crafted in Switzerland &bull; 2026</p>
  </footer>

  <script>
    let chronoRunning = false;
    let chronoStart = 0;
    let chronoElapsed = 0;
    let chronoTimer = null;

    function playTick() {{
      initAudio();
      playSpatialTone(1400, 'triangle', 0.03);
    }}

    window.toggleChrono = function() {{
      const btn = document.getElementById('btn-chrono-start');
      if (!chronoRunning) {{
        chronoRunning = true;
        chronoStart = performance.now() - chronoElapsed;
        btn.textContent = 'Stop';
        btn.style.background = '#ef4444';
        chronoTimer = setInterval(updateChronoDisplay, 33);
        playTick();
      }} else {{
        chronoRunning = false;
        clearInterval(chronoTimer);
        btn.textContent = 'Start';
        btn.style.background = 'var(--gold)';
        playTick();
      }}
    }};

    window.resetChrono = function() {{
      chronoRunning = false;
      clearInterval(chronoTimer);
      chronoElapsed = 0;
      document.getElementById('chrono-display').textContent = '00:00.00';
      const btn = document.getElementById('btn-chrono-start');
      btn.textContent = 'Start';
      btn.style.background = 'var(--gold)';
      playTick();
    }};

    window.splitLap = function() {{
      if (chronoRunning) {{
        playTick();
        const cur = document.getElementById('chrono-display').textContent;
        alert('⏱️ Chronometer Lap Split Recorded: ' + cur);
      }}
    }};

    function updateChronoDisplay() {{
      chronoElapsed = performance.now() - chronoStart;
      const totalSec = Math.floor(chronoElapsed / 1000);
      const mins = Math.floor(totalSec / 60);
      const secs = totalSec % 60;
      const ms = Math.floor((chronoElapsed % 1000) / 10);
      const str = `${{String(mins).padStart(2,'0')}}:${{String(secs).padStart(2,'0')}}.${{String(ms).padStart(2,'0')}}`;
      document.getElementById('chrono-display').textContent = str;
    }}

    window.selectComplication = function(type, el) {{
      document.querySelectorAll('.comp-item').forEach(e => e.classList.remove('active'));
      if (el) el.classList.add('active');
      initAudio();
      playSpatialTone(740, 'sine', 0.15);
    }};

    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 6. BESPOKE AEROSPACE / ORBITAL SATELLITE MISSION CONTROL LAYOUT
# ===================================================================
def build_aerospace_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Orbital Mission Control & Space Exploration Telemetry</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #030712;
      --surface: #0b1120;
      --border: rgba(56, 189, 248, 0.2);
      --cyan: #38bdf8;
      --cyan-glow: rgba(56, 189, 248, 0.35);
      --indigo: #6366f1;
      --emerald: #10b981;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --font-heading: 'Space Grotesk', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --transition: all 0.3s ease;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.6; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(3, 7, 18, 0.9); border-bottom: 1px solid var(--border);
      padding: 16px 48px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #fff; text-decoration: none; }}
    .nav-links {{ display: flex; gap: 32px; list-style: none; align-items: center; }}
    .nav-links a {{ font-family: var(--font-mono); font-size: 0.88rem; color: var(--text-muted); text-decoration: none; }}
    .nav-links a:hover {{ color: var(--cyan); }}
    .nav-cta {{ background: var(--cyan); color: #000 !important; font-weight: 700 !important; padding: 8px 18px; border-radius: 4px; }}

    .hero-orbital {{
      max-width: 1400px; margin: 0 auto; padding: 60px 48px;
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 48px; align-items: center;
    }}
    .hero-orbital h1 {{
      font-family: var(--font-heading); font-size: clamp(2.8rem, 5vw, 4.4rem);
      font-weight: 800; line-height: 1.1; margin-bottom: 20px;
    }}
    .cyan-text {{ color: var(--cyan); text-shadow: 0 0 25px var(--cyan-glow); }}
    
    .canvas-space-box {{
      height: 480px; border-radius: 16px; background: radial-gradient(circle, #0f172a 0%, #020617 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
      box-shadow: 0 0 50px rgba(56, 189, 248, 0.15);
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .hud-orbit {{
      position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10;
    }}
    .hud-btn {{
      background: rgba(11, 17, 32, 0.85); border: 1px solid var(--border);
      color: #fff; font-family: var(--font-mono); font-size: 0.8rem; padding: 6px 14px;
      border-radius: 4px; cursor: pointer;
    }}
    .hud-btn.active {{ background: var(--cyan); color: #000; border-color: var(--cyan); }}

    /* Mission Telemetry Readout */
    .telemetry-row {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
      max-width: 1400px; margin: 0 auto 80px auto; padding: 0 48px;
    }}
    .tele-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 24px;
    }}
    .tele-val {{ font-family: var(--font-mono); font-size: 2.6rem; font-weight: 800; color: var(--cyan); }}
    .tele-lbl {{ font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-muted); text-transform: uppercase; margin-top: 4px; }}

    /* Delta-V Calculator */
    .delta-sec {{ max-width: 1400px; margin: 0 auto 100px auto; padding: 0 48px; }}
    .delta-box {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
      padding: 40px; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center;
    }}
    .delta-readout {{
      background: #020617; border: 1px solid var(--border); border-radius: 12px;
      padding: 32px; text-align: center;
    }}
    .delta-val {{ font-family: var(--font-mono); font-size: 3.6rem; color: var(--cyan); font-weight: 800; }}

    /* Payload Grid */
    .payload-grid {{
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px;
      max-width: 1400px; margin: 0 auto 100px auto; padding: 0 48px;
    }}
    .payload-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
      overflow: hidden; transition: var(--transition);
    }}
    .payload-card:hover {{ border-color: var(--cyan); transform: translateY(-6px); }}
    .payload-card img {{ width: 100%; height: 220px; object-fit: cover; }}
    .payload-body {{ padding: 24px; }}
    .payload-tag {{
      font-family: var(--font-mono); font-size: 0.75rem; color: var(--cyan);
      background: rgba(56, 189, 248, 0.1); padding: 4px 10px; border-radius: 4px; margin-bottom: 12px; display: inline-block;
    }}
    .payload-body h3 {{ font-family: var(--font-heading); font-size: 1.4rem; margin-bottom: 10px; }}
    .payload-body p {{ color: var(--text-muted); font-size: 0.92rem; }}

    footer {{ text-align: center; padding: 50px 24px; border-top: 1px solid var(--border); font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-muted); }}

    @media (max-width: 900px) {{
      .hero-orbital {{ grid-template-columns: 1fr; }}
      .telemetry-row {{ grid-template-columns: 1fr 1fr; }}
      .delta-box {{ grid-template-columns: 1fr; }}
      .payload-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">🚀 {brand} ORBITAL</a>
    <ul class="nav-links">
      <li><a href="#telemetry">Flight Telemetry</a></li>
      <li><a href="#delta-calc">Delta-V Engine</a></li>
      <li><a href="#payloads">Payloads</a></li>
      <li><a href="#delta-calc" class="nav-cta">Book Launch Slot</a></li>
    </ul>
  </nav>

  <header class="hero-orbital" id="home">
    <div>
      <div style="font-family:var(--font-mono);font-size:0.85rem;color:var(--cyan);margin-bottom:12px;letter-spacing:1px;font-weight:700;">LOW EARTH ORBIT // SATELLITE NETWORK</div>
      <h1>Autonomous Orbital Deployment: <span class="cyan-text">{brand}</span></h1>
      <p>Precision geostationary insertion, electric Hall-effect thrusters, and satellite mega-constellation bus architectures engineered for 15-year orbital endurance.</p>
      <a href="#delta-calc" style="background:var(--cyan);color:#000;padding:12px 28px;border-radius:4px;font-family:var(--font-mono);font-weight:800;text-decoration:none;display:inline-block;">Calculate Orbital Insertion ➔</a>
    </div>

    <div class="canvas-space-box">
      <div class="hud-orbit">
        <button class="hud-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Solar Panels: Deployed</button>
        <button class="hud-btn" id="btn-custom-2" onclick="toggleCustom2(this)">Warp: 1x</button>
        <button class="hud-btn" id="btn-sound" onclick="toggleAudioFX(this)">🔊 Audio</button>
      </div>
      <div id="webgl-canvas-container" title="360° Satellite Orbit Viewport"></div>
    </div>
  </header>

  <div class="telemetry-row" id="telemetry">
    <div class="tele-card">
      <div class="tele-val">7.78 km/s</div>
      <div class="tele-lbl">Orbital Velocity (LEO)</div>
    </div>
    <div class="tele-card">
      <div class="tele-val">540 km</div>
      <div class="tele-lbl">Circular Altitude</div>
    </div>
    <div class="tele-card">
      <div class="tele-val">95.4 min</div>
      <div class="tele-lbl">Orbital Period</div>
    </div>
    <div class="tele-card">
      <div class="tele-val">99.999%</div>
      <div class="tele-lbl">Downlink Telemetry SLA</div>
    </div>
  </div>

  <section class="delta-sec" id="delta-calc">
    <div class="delta-box">
      <div>
        <h3 style="font-family:var(--font-heading);font-size:2rem;margin-bottom:12px;">Orbital Maneuver Delta-V Calculator</h3>
        <p style="color:var(--text-muted);margin-bottom:24px;">Calculates velocity increment requirement ($\Delta v$) using Hohmann transfer mechanics from parking LEO to GEO transfer orbit.</p>
        <label style="font-family:var(--font-mono);font-size:0.9rem;display:block;margin-bottom:8px;">Target Altitude: <span id="alt-val" style="color:var(--cyan);">550 km (Sun-Synchronous)</span></label>
        <input type="range" id="alt-slider" min="200" max="35786" value="550" style="width:100%;accent-color:var(--cyan);" oninput="updateDeltaCalc()">
      </div>
      <div class="delta-readout">
        <div class="delta-val" id="dv-display">3,920 m/s</div>
        <div style="font-family:var(--font-mono);color:var(--text-muted);font-size:0.9rem;text-transform:uppercase;margin-top:6px;">Required Insertion Delta-V</div>
        <div style="font-family:var(--font-mono);color:var(--cyan);margin-top:14px;font-size:0.85rem;">Estimated Burn Duration: 142 seconds</div>
      </div>
    </div>
  </section>

  <section class="payload-grid" id="payloads">
    <div class="payload-card">
      <img src="{c1}" alt="Earth Observation">
      <div class="payload-body">
        <span class="payload-tag">REMOTE SENSING</span>
        <h3>Sub-Meter Optical SAR</h3>
        <p>Synthetic aperture radar penetrates cloud cover and darkness to provide 0.5-meter ground resolution imagery in real-time.</p>
      </div>
    </div>
    <div class="payload-card">
      <img src="{c2}" alt="Laser Inter-Satellite Links">
      <div class="payload-body">
        <span class="payload-tag">COMMUNICATIONS</span>
        <h3>Optical Cross-Links</h3>
        <p>100 Gbps space-to-space coherent laser communication links forming a mesh network across orbital planes.</p>
      </div>
    </div>
    <div class="payload-card">
      <img src="{c3}" alt="Deep Space Probe">
      <div class="payload-body">
        <span class="payload-tag">PROPULSION</span>
        <h3>Krypton Ion Hall Thruster</h3>
        <p>Ultra-efficient electric propulsion delivering 3,200 seconds of specific impulse for station keeping and de-orbit disposal.</p>
      </div>
    </div>
  </section>

  <footer>
    <p>🚀 {brand} Aerospace &bull; Orbital Dynamics Engine &bull; 2026</p>
  </footer>

  <script>
    function updateDeltaCalc() {{
      const alt = parseInt(document.getElementById('alt-slider').value);
      document.getElementById('alt-val').textContent = `${{alt.toLocaleString()}} km`;
      // Approximate delta-V calculation (Hohmann transfer approximation)
      const base = 3200;
      const extra = Math.round((alt / 35786) * 1200);
      const total = base + extra;
      document.getElementById('dv-display').textContent = `${{total.toLocaleString()}} m/s`;
    }}
    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 7. BESPOKE SWISS QUANTITATIVE BENTO FINANCE LAYOUT
# ===================================================================
def build_finance_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Institutional Quantitative Capital & Swiss Bento Architecture</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #080c14;
      --surface: #0f172a;
      --surface-glass: rgba(15, 23, 42, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --emerald: #10b981;
      --emerald-glow: rgba(16, 185, 129, 0.35);
      --gold: #f59e0b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --font-body: 'Plus Jakarta Sans', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: var(--font-body); background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.6; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(8, 12, 20, 0.92); border-bottom: 1px solid var(--border);
      padding: 18px 48px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-size: 1.3rem; font-weight: 800; color: #fff; text-decoration: none; }}
    .nav-links {{ display: flex; gap: 32px; list-style: none; align-items: center; }}
    .nav-links a {{ font-size: 0.92rem; color: var(--text-muted); text-decoration: none; transition: var(--transition); }}
    .nav-links a:hover {{ color: var(--emerald); }}
    .nav-cta {{
      background: var(--emerald); color: #000 !important; font-weight: 700 !important;
      padding: 9px 22px; border-radius: 6px; box-shadow: 0 0 15px var(--emerald-glow);
    }}

    /* Live Ticker Tape */
    .ticker-tape {{
      background: #04060a; border-bottom: 1px solid var(--border);
      padding: 8px 0; overflow: hidden; white-space: nowrap; font-family: var(--font-mono); font-size: 0.8rem;
    }}
    .ticker-inner {{ display: inline-block; animation: ticker-scroll 25s linear infinite; }}
    @keyframes ticker-scroll {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
    .ticker-item {{ margin: 0 24px; display: inline-inline; }}
    .tick-up {{ color: var(--emerald); }}
    .tick-down {{ color: #ef4444; }}

    /* Hero Bento */
    .hero-bento {{
      max-width: 1360px; margin: 0 auto; padding: 50px 32px;
      display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 28px;
    }}
    .bento-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
      padding: 36px; position: relative; overflow: hidden; transition: var(--transition);
    }}
    .bento-card:hover {{ border-color: rgba(16, 185, 129, 0.35); }}
    .hero-bento h1 {{
      font-size: clamp(2.4rem, 4.5vw, 3.8rem); font-weight: 800; line-height: 1.15; margin-bottom: 20px;
    }}
    .emerald-text {{ color: var(--emerald); }}

    /* Canvas 3D Box in Bento */
    .canvas-bento-box {{
      height: 440px; border-radius: 16px; background: radial-gradient(circle, #131f37 0%, #080c14 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .bento-hud {{ position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10; }}
    .bento-btn {{
      background: rgba(8, 12, 20, 0.85); border: 1px solid var(--border);
      color: #fff; font-family: var(--font-mono); font-size: 0.78rem; padding: 6px 12px;
      border-radius: 4px; cursor: pointer;
    }}
    .bento-btn.active {{ background: var(--emerald); color: #000; border-color: var(--emerald); }}

    /* Multi-Card Bento Grid */
    .bento-grid-3 {{
      display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px;
      max-width: 1360px; margin: 0 auto 80px auto; padding: 0 32px;
    }}
    .calc-card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 32px;
    }}
    .calc-val {{ font-family: var(--font-mono); font-size: 2.8rem; font-weight: 800; color: var(--emerald); }}

    footer {{ text-align: center; padding: 50px 24px; border-top: 1px solid var(--border); font-size: 0.9rem; color: var(--text-muted); }}

    @media (max-width: 900px) {{
      .hero-bento {{ grid-template-columns: 1fr; }}
      .bento-grid-3 {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">📈 {brand}</a>
    <ul class="nav-links">
      <li><a href="#yield-calc">Yield Simulator</a></li>
      <li><a href="#custody">Custody Vaults</a></li>
      <li><a href="#yield-calc" class="nav-cta">Open Institutional Account</a></li>
    </ul>
  </nav>

  <div class="ticker-tape">
    <div class="ticker-inner">
      <span class="ticker-item">S&P 500: 5,864.20 <span class="tick-up">+1.42%</span></span>
      <span class="ticker-item">NASDAQ: 18,518.60 <span class="tick-up">+1.88%</span></span>
      <span class="ticker-item">EUR/USD: 1.0864 <span class="tick-down">-0.12%</span></span>
      <span class="ticker-item">ALPHA FUND V: NAV $142.80 <span class="tick-up">+18.4% YTD</span></span>
      <span class="ticker-item">GOLD OUNCE: $2,748.50 <span class="tick-up">+0.65%</span></span>
      <span class="ticker-item">BTC/USD: $68,420 <span class="tick-up">+3.4%</span></span>
      <!-- Duplicate for seamless scroll -->
      <span class="ticker-item">S&P 500: 5,864.20 <span class="tick-up">+1.42%</span></span>
      <span class="ticker-item">NASDAQ: 18,518.60 <span class="tick-up">+1.88%</span></span>
      <span class="ticker-item">EUR/USD: 1.0864 <span class="tick-down">-0.12%</span></span>
      <span class="ticker-item">ALPHA FUND V: NAV $142.80 <span class="tick-up">+18.4% YTD</span></span>
      <span class="ticker-item">GOLD OUNCE: $2,748.50 <span class="tick-up">+0.65%</span></span>
      <span class="ticker-item">BTC/USD: $68,420 <span class="tick-up">+3.4%</span></span>
    </div>
  </div>

  <header class="hero-bento" id="home">
    <div class="bento-card">
      <div style="font-family:var(--font-mono);font-size:0.85rem;color:var(--emerald);margin-bottom:12px;font-weight:700;">QUANTITATIVE ALPHA // FIX 5.0 ENGINE</div>
      <h1>Sub-Millisecond Quantitative Execution: <span class="emerald-text">{brand}</span></h1>
      <p style="color:var(--text-muted);font-size:1.15rem;margin-bottom:28px;">Direct Tier-1 bank prime brokerage access, machine learning cross-asset statistical arbitrage, and cold MPC cryptographic custody vaults.</p>
      <div style="display:flex;gap:14px;">
        <a href="#yield-calc" style="background:var(--emerald);color:#000;font-weight:800;padding:12px 24px;border-radius:6px;text-decoration:none;">Simulate Yield Alpha ➔</a>
      </div>
    </div>

    <div class="canvas-bento-box">
      <div class="bento-hud">
        <button class="bento-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Pillars: Bull</button>
        <button class="bento-btn" id="btn-custom-2" onclick="toggleCustom2(this)">Flow: 1x</button>
        <button class="bento-btn" id="btn-sound" onclick="toggleAudioFX(this)">🔊 Audio</button>
      </div>
      <div id="webgl-canvas-container" title="3D Candlestick & Capital Flow Grid"></div>
    </div>
  </header>

  <div class="bento-grid-3" id="yield-calc">
    <div class="calc-card">
      <h3 style="font-size:1.4rem;margin-bottom:8px;">Compound Alpha Simulator</h3>
      <p style="color:var(--text-muted);font-size:0.9rem;margin-bottom:20px;">Adjust allocated principal to calculate 5-year annualized net returns with Sharpe ratio 2.45.</p>
      <label style="font-family:var(--font-mono);font-size:0.85rem;display:block;margin-bottom:8px;">Principal: <span id="prin-lbl" style="color:var(--emerald);">$500,000 USD</span></label>
      <input type="range" id="prin-slider" min="100000" max="5000000" step="50000" value="500000" style="width:100%;accent-color:var(--emerald);" oninput="updateFinanceCalc()">
    </div>
    <div class="calc-card" style="text-align:center;display:flex;flex-direction:column;justify-content:center;">
      <div class="calc-val" id="proj-return">$1,185,420</div>
      <div style="font-family:var(--font-mono);color:var(--text-muted);font-size:0.85rem;text-transform:uppercase;margin-top:6px;">Projected 5-Yr Balance (@ 18.8% CAGR)</div>
    </div>
    <div class="calc-card" style="display:flex;flex-direction:column;justify-content:center;">
      <div style="font-family:var(--font-mono);font-size:1.1rem;color:var(--emerald);font-weight:700;margin-bottom:6px;">Tier-1 Custody Guarantee</div>
      <p style="color:var(--text-muted);font-size:0.9rem;">Segregated bankruptcy-remote institutional accounts held with BNY Mellon and State Street with $500M Lloyd's of London comprehensive syndicate coverage.</p>
    </div>
  </div>

  <footer>
    <p>📈 {brand} Quantitative Asset Management &bull; Zurich &bull; New York &bull; 2026</p>
  </footer>

  <script>
    function updateFinanceCalc() {{
      const prin = parseInt(document.getElementById('prin-slider').value);
      document.getElementById('prin-lbl').textContent = `$${{prin.toLocaleString()}} USD`;
      // 5-year compound at ~18.8%
      const total = Math.round(prin * Math.pow(1.188, 5));
      document.getElementById('proj-return').textContent = `$${{total.toLocaleString()}}`;
    }}
    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 8. BESPOKE ELECTRONIC MODULAR SYNTHESIZER AUDIO STUDIO LAYOUT
# ===================================================================
def build_music_synth_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Analog Modular Synthesizer Studio & Web Audio Lab</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Plus+Jakarta+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #100f14;
      --surface: #191722;
      --border: rgba(168, 85, 247, 0.22);
      --violet: #a855f7;
      --violet-glow: rgba(168, 85, 247, 0.4);
      --pink: #ec4899;
      --cyan: #06b6d4;
      --text: #f8fafc;
      --text-muted: #a1a1aa;
      --font-display: 'Syne', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --transition: all 0.25s ease;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.6; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(16, 15, 20, 0.92); border-bottom: 1px solid var(--border);
      padding: 16px 40px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-family: var(--font-display); font-size: 1.4rem; font-weight: 800; color: #fff; text-decoration: none; }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; align-items: center; }}
    .nav-links a {{ font-size: 0.92rem; color: var(--text-muted); text-decoration: none; transition: var(--transition); }}
    .nav-links a:hover {{ color: var(--violet); }}
    .nav-cta {{
      background: linear-gradient(135deg, var(--violet), var(--pink)); color: #fff !important;
      font-weight: 700 !important; padding: 8px 20px; border-radius: 20px; box-shadow: 0 0 15px var(--violet-glow);
    }}

    .hero-synth {{
      max-width: 1400px; margin: 0 auto; padding: 60px 40px 40px;
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 40px; align-items: center;
    }}
    .hero-synth h1 {{
      font-family: var(--font-display); font-size: clamp(2.8rem, 5vw, 4.4rem);
      font-weight: 800; line-height: 1.1; margin-bottom: 20px;
    }}
    .glow-text {{
      background: linear-gradient(135deg, #fff 20%, var(--violet) 70%, var(--pink) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    .canvas-synth-box {{
      height: 460px; border-radius: 16px; background: radial-gradient(circle, #241c35 0%, #100f14 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
      box-shadow: 0 0 50px rgba(168, 85, 247, 0.2);
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .synth-hud {{ position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10; }}
    .synth-btn {{
      background: rgba(16, 15, 20, 0.85); border: 1px solid var(--border);
      color: #fff; font-family: var(--font-mono); font-size: 0.78rem; padding: 6px 12px;
      border-radius: 20px; cursor: pointer;
    }}
    .synth-btn.active {{ background: var(--violet); color: #fff; border-color: var(--violet); }}

    /* Playable Synthesizer Keyboard & Canvas Oscilloscope */
    .keyboard-section {{ max-width: 1200px; margin: 0 auto 100px auto; padding: 0 40px; }}
    .synth-console {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
      padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    }}
    .controls-row {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 32px;
    }}
    .knob-box {{
      background: #110f17; border: 1px solid var(--border); border-radius: 12px; padding: 20px; text-align: center;
    }}
    .knob-box label {{ font-family: var(--font-mono); font-size: 0.8rem; color: var(--violet); text-transform: uppercase; display: block; margin-bottom: 8px; font-weight: 700; }}
    
    #oscilloscope-canvas {{
      width: 100%; height: 120px; background: #0c0b0f; border-radius: 10px; border: 1px solid var(--border);
      margin-bottom: 32px; display: block;
    }}

    /* Piano Keys */
    .piano-keys {{
      display: flex; justify-content: center; position: relative; height: 180px; user-select: none;
    }}
    .white-key {{
      width: 58px; height: 180px; background: #fdfdfd; border: 1px solid #000; border-radius: 0 0 6px 6px;
      cursor: pointer; z-index: 1; transition: background 0.1s; position: relative;
    }}
    .white-key:active, .white-key.active {{ background: var(--violet); }}
    .black-key {{
      width: 36px; height: 110px; background: #1c1924; border: 1px solid #000; border-radius: 0 0 4px 4px;
      cursor: pointer; z-index: 2; margin-left: -18px; margin-right: -18px; transition: background 0.1s;
    }}
    .black-key:active, .black-key.active {{ background: var(--pink); }}

    footer {{ text-align: center; padding: 50px 24px; border-top: 1px solid var(--border); font-size: 0.88rem; color: var(--text-muted); }}

    @media (max-width: 900px) {{
      .hero-synth {{ grid-template-columns: 1fr; }}
      .controls-row {{ grid-template-columns: 1fr 1fr; }}
      .piano-keys {{ overflow-x: auto; justify-content: flex-start; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">🎹 {brand} AUDIO</a>
    <ul class="nav-links">
      <li><a href="#lab">Web Audio Lab</a></li>
      <li><a href="#lab" class="nav-cta">Record Stems</a></li>
    </ul>
  </nav>

  <header class="hero-synth" id="home">
    <div>
      <div style="font-family:var(--font-mono);font-size:0.85rem;color:var(--violet);margin-bottom:12px;font-weight:700;">VOLTAGE CONTROLLED OSCILLATOR // EURORACK</div>
      <h1>Analog Harmonic Purity: <span class="glow-text">{brand}</span></h1>
      <p style="color:var(--text-muted);font-size:1.15rem;margin-bottom:28px;">Discreet operational amplifiers, state-variable 24dB/oct ladder filters, and zero-latency real-time Web Audio API sound synthesis.</p>
    </div>

    <div class="canvas-synth-box">
      <div class="synth-hud">
        <button class="synth-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Wave: Sawtooth</button>
        <button class="synth-btn" id="btn-custom-2" onclick="toggleCustom2(this)">Cutoff: 1.2kHz</button>
      </div>
      <div id="webgl-canvas-container" title="3D Modular Synth Rack"></div>
    </div>
  </header>

  <section class="keyboard-section" id="lab">
    <div class="synth-console">
      <div class="controls-row">
        <div class="knob-box">
          <label>Waveform</label>
          <select id="synth-wave" style="background:#0c0b0f;color:#fff;border:1px solid var(--border);padding:6px;border-radius:4px;width:100%;font-family:var(--font-mono);">
            <option value="sawtooth">Sawtooth</option>
            <option value="sine">Sine</option>
            <option value="square">Square</option>
            <option value="triangle">Triangle</option>
          </select>
        </div>
        <div class="knob-box">
          <label>Filter Cutoff (Hz)</label>
          <input type="range" id="synth-cutoff" min="100" max="8000" value="2400" style="width:100%;accent-color:var(--violet);">
        </div>
        <div class="knob-box">
          <label>Attack (s)</label>
          <input type="range" id="synth-attack" min="0.01" max="1.0" step="0.05" value="0.05" style="width:100%;accent-color:var(--violet);">
        </div>
        <div class="knob-box">
          <label>Release (s)</label>
          <input type="range" id="synth-release" min="0.1" max="2.5" step="0.1" value="0.6" style="width:100%;accent-color:var(--violet);">
        </div>
      </div>

      <canvas id="oscilloscope-canvas"></canvas>

      <div class="piano-keys">
        <div class="white-key" onmousedown="playNote(261.63, this)" title="C4"></div>
        <div class="black-key" onmousedown="playNote(277.18, this)" title="C#4"></div>
        <div class="white-key" onmousedown="playNote(293.66, this)" title="D4"></div>
        <div class="black-key" onmousedown="playNote(311.13, this)" title="D#4"></div>
        <div class="white-key" onmousedown="playNote(329.63, this)" title="E4"></div>
        <div class="white-key" onmousedown="playNote(349.23, this)" title="F4"></div>
        <div class="black-key" onmousedown="playNote(369.99, this)" title="F#4"></div>
        <div class="white-key" onmousedown="playNote(392.00, this)" title="G4"></div>
        <div class="black-key" onmousedown="playNote(415.30, this)" title="G#4"></div>
        <div class="white-key" onmousedown="playNote(440.00, this)" title="A4"></div>
        <div class="black-key" onmousedown="playNote(466.16, this)" title="A#4"></div>
        <div class="white-key" onmousedown="playNote(493.88, this)" title="B4"></div>
        <div class="white-key" onmousedown="playNote(523.25, this)" title="C5"></div>
      </div>
    </div>
  </section>

  <footer>
    <p>🎹 {brand} Analog Modular Studio &bull; Web Audio Synthesis &bull; 2026</p>
  </footer>

  <script>
    let synthAnalyser = null;

    function playNote(freq, el) {{
      initAudio();
      if (!audioCtx) return;

      if (!synthAnalyser) {{
        synthAnalyser = audioCtx.createAnalyser();
        synthAnalyser.fftSize = 2048;
        synthAnalyser.connect(audioCtx.destination);
        startOscilloscope();
      }}

      const wave = document.getElementById('synth-wave').value;
      const cutoff = parseFloat(document.getElementById('synth-cutoff').value);
      const attack = parseFloat(document.getElementById('synth-attack').value);
      const release = parseFloat(document.getElementById('synth-release').value);

      const osc = audioCtx.createOscillator();
      const filter = audioCtx.createBiquadFilter();
      const gain = audioCtx.createGain();

      osc.type = wave;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(cutoff, audioCtx.currentTime);

      const now = audioCtx.currentTime;
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.linearRampToValueAtTime(0.28, now + attack);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + attack + release);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(synthAnalyser);

      osc.start(now);
      osc.stop(now + attack + release);

      if (el) {{
        el.classList.add('active');
        setTimeout(() => el.classList.remove('active'), 250);
      }}
    }}

    function startOscilloscope() {{
      const canvas = document.getElementById('oscilloscope-canvas');
      if (!canvas || !synthAnalyser) return;
      const ctx = canvas.getContext('2d');
      canvas.width = canvas.parentElement.clientWidth - 80;
      canvas.height = 120;
      const bufferLength = synthAnalyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      function drawWave() {{
        requestAnimationFrame(drawWave);
        synthAnalyser.getByteTimeDomainData(dataArray);

        ctx.fillStyle = '#0c0b0f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.lineWidth = 2;
        ctx.strokeStyle = '#a855f7';
        ctx.beginPath();

        const sliceWidth = canvas.width / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {{
          const v = dataArray[i] / 128.0;
          const y = (v * canvas.height) / 2;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
          x += sliceWidth;
        }}

        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();
      }}
      drawWave();
    }}

    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 9. BESPOKE BIOTECH / PRECISION GENOMICS & CRISPR LAYOUT
# ===================================================================
def build_biotech_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Precision Genomics & CRISPR Molecular Architecture</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #040d12;
      --surface: #0a1b24;
      --border: rgba(20, 184, 166, 0.22);
      --teal: #14b8a6;
      --teal-glow: rgba(20, 184, 166, 0.35);
      --blue: #3b82f6;
      --text: #f0fdfa;
      --text-muted: #99f6e4;
      --font-heading: 'Outfit', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --transition: all 0.3s ease;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.6; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(4, 13, 18, 0.9); border-bottom: 1px solid var(--border);
      padding: 16px 40px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-family: var(--font-heading); font-size: 1.35rem; font-weight: 800; color: #fff; text-decoration: none; }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; }}
    .nav-links a {{ font-size: 0.92rem; color: #94a3b8; text-decoration: none; }}
    .nav-links a:hover {{ color: var(--teal); }}
    .nav-cta {{ background: var(--teal); color: #000 !important; font-weight: 700 !important; padding: 8px 18px; border-radius: 6px; }}

    .hero-bio {{
      max-width: 1400px; margin: 0 auto; padding: 60px 40px;
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 40px; align-items: center;
    }}
    .hero-bio h1 {{
      font-family: var(--font-heading); font-size: clamp(2.6rem, 5vw, 4.2rem);
      font-weight: 800; line-height: 1.1; margin-bottom: 20px;
    }}

    .canvas-bio-box {{
      height: 460px; border-radius: 16px; background: radial-gradient(circle, #0e2938 0%, #040d12 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
      box-shadow: 0 0 50px var(--teal-glow);
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .bio-hud {{ position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10; }}
    .bio-btn {{
      background: rgba(4, 13, 18, 0.85); border: 1px solid var(--border);
      color: #fff; font-family: var(--font-mono); font-size: 0.78rem; padding: 6px 12px;
      border-radius: 4px; cursor: pointer;
    }}
    .bio-btn.active {{ background: var(--teal); color: #000; border-color: var(--teal); }}

    /* Interactive DNA Synthesizer */
    .dna-sec {{ max-width: 1200px; margin: 0 auto 100px auto; padding: 0 40px; }}
    .dna-box {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 40px;
    }}
    .dna-seq {{
      display: flex; gap: 10px; justify-content: center; margin: 28px 0; flex-wrap: wrap;
    }}
    .base-pill {{
      width: 48px; height: 48px; border-radius: 8px; display: flex; align-items: center; justify-content: center;
      font-family: var(--font-mono); font-weight: 800; font-size: 1.2rem; cursor: pointer; transition: var(--transition);
    }}
    .base-a {{ background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }}
    .base-t {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}
    .base-c {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }}
    .base-g {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }}

    footer {{ text-align: center; padding: 50px 24px; border-top: 1px solid var(--border); color: #64748b; font-size: 0.88rem; }}

    @media (max-width: 900px) {{
      .hero-bio {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">🧬 {brand}</a>
    <ul class="nav-links">
      <li><a href="#dna-tool">Gene Scanner</a></li>
      <li><a href="#dna-tool" class="nav-cta">Analyze Sequence</a></li>
    </ul>
  </nav>

  <header class="hero-bio" id="home">
    <div>
      <div style="font-family:var(--font-mono);font-size:0.85rem;color:var(--teal);margin-bottom:12px;font-weight:700;">CRISPR CAS-9 // THERAPEUTIC GENE EDITING</div>
      <h1>Sub-Base Precision Genomics: <span style="color:var(--teal);">{brand}</span></h1>
      <p style="color:#94a3b8;font-size:1.15rem;margin-bottom:28px;">Single-nucleotide prime editing, targeted in vivo lipid nanoparticle mRNA delivery, and algorithmic off-target cleavage eradication.</p>
    </div>

    <div class="canvas-bio-box">
      <div class="bio-hud">
        <button class="bio-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Double Helix: Active</button>
        <button class="bio-btn" id="btn-custom-2" onclick="toggleCustom2(this)">CRISPR: Ready</button>
      </div>
      <div id="webgl-canvas-container" title="3D Double-Helix DNA Lattice"></div>
    </div>
  </header>

  <section class="dna-sec" id="dna-tool">
    <div class="dna-box">
      <h3 style="font-family:var(--font-heading);font-size:1.8rem;text-align:center;">Real-Time Nucleotide Base-Pair Matcher</h3>
      <div class="dna-seq">
        <div class="base-pill base-a">A</div>
        <div class="base-pill base-t">T</div>
        <div class="base-pill base-c">C</div>
        <div class="base-pill base-g">G</div>
        <div class="base-pill base-a">A</div>
        <div class="base-pill base-t">T</div>
        <div class="base-pill base-g">G</div>
        <div class="base-pill base-c">C</div>
      </div>
      <div style="text-align:center;font-family:var(--font-mono);color:var(--teal);">
        Target Sequence Match: <b>100% Homology Verified (Zero Off-Target Cleavage)</b>
      </div>
    </div>
  </section>

  <footer>
    <p>🧬 {brand} Precision Genomics &bull; Certified Biosafety Level 3 &bull; 2026</p>
  </footer>

  <script>
    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 10. BESPOKE MODERNIST ARCHITECTURE & LUXURY REAL ESTATE LAYOUT
# ===================================================================
def build_architecture_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Modernist Architecture & Cantilever Villa Lookbook</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: #0d0f12;
      --surface: #15191f;
      --border: rgba(255, 255, 255, 0.08);
      --bronze: #ca8a04;
      --sandstone: #f5f5f4;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --font-serif: 'Cormorant Garamond', serif;
      --font-body: 'Plus Jakarta Sans', sans-serif;
      --transition: all 0.3s ease;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: var(--font-body); background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.8; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(13, 15, 18, 0.9); border-bottom: 1px solid var(--border);
      padding: 20px 48px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-family: var(--font-serif); font-size: 1.5rem; font-weight: 700; color: #fff; text-decoration: none; }}
    .nav-links {{ display: flex; gap: 32px; list-style: none; }}
    .nav-links a {{ font-size: 0.92rem; color: var(--text-muted); text-decoration: none; }}
    .nav-links a:hover {{ color: var(--bronze); }}

    .hero-arch {{
      max-width: 1400px; margin: 0 auto; padding: 80px 48px;
      display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center;
    }}
    .hero-arch h1 {{
      font-family: var(--font-serif); font-size: clamp(3rem, 6vw, 4.8rem);
      font-weight: 700; line-height: 1.1; margin-bottom: 24px;
    }}

    .canvas-arch-box {{
      height: 480px; border-radius: 20px; background: radial-gradient(circle, #1e242e 0%, #0d0f12 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}

    /* Blueprint Section */
    .blueprint-sec {{ max-width: 1400px; margin: 0 auto 100px auto; padding: 0 48px; }}
    .blueprint-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }}
    .bp-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
    .bp-card img {{ width: 100%; height: 240px; object-fit: cover; }}
    .bp-body {{ padding: 24px; }}
    .bp-body h3 {{ font-family: var(--font-serif); font-size: 1.5rem; margin-bottom: 8px; }}

    footer {{ text-align: center; padding: 60px 24px; border-top: 1px solid var(--border); color: #64748b; }}

    @media (max-width: 900px) {{
      .hero-arch {{ grid-template-columns: 1fr; }}
      .blueprint-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand">🏛️ {brand} ARCHITECTURE</a>
    <ul class="nav-links">
      <li><a href="#works">Selected Works</a></li>
      <li><a href="#works" style="color:var(--bronze);font-weight:700;">Private Commission</a></li>
    </ul>
  </nav>

  <header class="hero-arch" id="home">
    <div>
      <div style="font-family:var(--font-serif);font-style:italic;font-size:1.2rem;color:var(--bronze);margin-bottom:12px;">Modernist Spatial Form & Light</div>
      <h1>Architecting The Horizon: <span style="color:var(--bronze);">{brand}</span></h1>
      <p style="color:var(--text-muted);font-size:1.15rem;margin-bottom:32px;">Cantilevered reinforced architectural concrete, panoramic acoustic glazing, and biophilic natural light orientation across alpine and coastal terrains.</p>
    </div>

    <div class="canvas-arch-box">
      <div id="webgl-canvas-container" title="3D Modernist Cantilever Villa Wireframe"></div>
    </div>
  </header>

  <section class="blueprint-sec" id="works">
    <div class="blueprint-grid">
      <div class="bp-card">
        <img src="{c1}" alt="Villa Cantilever">
        <div class="bp-body">
          <h3>Villa Bel-Air Residence</h3>
          <p style="color:var(--text-muted);font-size:0.92rem;">12,000 sq ft cantilevered over the Pacific ridge with infinity horizon reflection pools.</p>
        </div>
      </div>
      <div class="bp-card">
        <img src="{c2}" alt="Alpine Glass Pavilion">
        <div class="bp-body">
          <h3>St. Moritz Glass Pavilion</h3>
          <p style="color:var(--text-muted);font-size:0.92rem;">Triple-glazed thermally isolated alpine sanctuary framing the Engadin peaks.</p>
        </div>
      </div>
      <div class="bp-card">
        <img src="{c3}" alt="Urban Monolith">
        <div class="bp-body">
          <h3>Kyoto Monolith Studio</h3>
          <p style="color:var(--text-muted);font-size:0.92rem;">Board-formed cedar architectural concrete with sunken courtyard stone gardens.</p>
        </div>
      </div>
    </div>
  </section>

  <footer>
    <p>🏛️ {brand} Atelier &bull; Zürich &bull; Tokyo &bull; Los Angeles &bull; 2026</p>
  </footer>

  <script>
    {scripts}
  </script>
</body>
</html>
"""


# ===================================================================
# 11. UNIVERSAL INTELLIGENT ADAPTIVE COMPOSER (ANTI-SLOP FALLBACK)
# ===================================================================
def build_adaptive_layout(profile: Dict[str, Any], threejs_scene_code: str) -> str:
    """
    Constructs an asymmetric, high-impact flagship layout for any novel prompt.
    Never falls back to generic repetitive bootstrap cards.
    """
    brand = profile["brand_name"]
    images = profile["images"]
    c1, _ = images[1]
    c2, _ = images[2]
    c3, _ = images[3]
    scripts = get_common_scripts(threejs_scene_code)
    c = profile["colors"]

    stats_html = "".join([
        f'<div class="stat-box"><h3>{val}</h3><p>{label}</p></div>'
        for val, label in profile.get("stats", [("99.9%", "Verified Quality"), ("Zero", "Latency"), ("Tier-1", "Standard"), ("24/7", "Autonomous")])
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand} | Next-Gen Flagship Architecture</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: {c['bg']};
      --surface: {c['surface']};
      --border: {c['surface_border']};
      --primary: {c['primary']};
      --primary-glow: {c['primary_glow']};
      --accent: {c['accent']};
      --text: {c['text']};
      --text-muted: {c['text_muted']};
      --font-main: 'Plus Jakarta Sans', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
      --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: var(--font-main); background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.7; }}

    nav {{
      position: sticky; top: 0; z-index: 100; backdrop-filter: blur(20px);
      background: rgba(10, 15, 25, 0.9); border-bottom: 1px solid var(--border);
      padding: 18px 48px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{ font-size: 1.35rem; font-weight: 800; color: #fff; text-decoration: none; display: flex; align-items: center; gap: 10px; }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; align-items: center; }}
    .nav-links a {{ font-size: 0.92rem; color: var(--text-muted); text-decoration: none; }}
    .nav-links a:hover {{ color: var(--primary); }}
    .nav-cta {{
      background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff !important;
      font-weight: 700 !important; padding: 9px 22px; border-radius: 8px; box-shadow: 0 0 20px var(--primary-glow);
    }}

    .hero-adaptive {{
      max-width: 1400px; margin: 0 auto; padding: 60px 48px;
      display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 48px; align-items: center;
    }}
    .badge {{
      display: inline-block; padding: 5px 14px; border-radius: 20px; background: rgba(255,255,255,0.06);
      border: 1px solid var(--border); color: var(--primary); font-family: var(--font-mono); font-size: 0.8rem; font-weight: 700;
      margin-bottom: 20px;
    }}
    .hero-adaptive h1 {{
      font-size: clamp(2.8rem, 5vw, 4.4rem); font-weight: 800; line-height: 1.15; margin-bottom: 20px;
    }}
    .hero-adaptive p {{
      color: var(--text-muted); font-size: 1.2rem; margin-bottom: 32px; max-width: 580px;
    }}

    .canvas-adaptive-box {{
      height: 480px; border-radius: 16px; background: radial-gradient(circle, #1a2235 0%, #080d1a 100%);
      border: 1px solid var(--border); position: relative; overflow: hidden;
      box-shadow: 0 0 50px var(--primary-glow);
    }}
    #webgl-canvas-container {{ width: 100%; height: 100%; }}
    .adapt-hud {{ position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10; }}
    .adapt-btn {{
      background: rgba(10, 15, 25, 0.85); border: 1px solid var(--border);
      color: #fff; font-size: 0.8rem; padding: 6px 14px; border-radius: 20px; cursor: pointer;
    }}
    .adapt-btn.active {{ background: var(--primary); color: #000; border-color: var(--primary); }}

    /* Stat Strip */
    .stat-row {{
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
      max-width: 1400px; margin: 0 auto 80px auto; padding: 0 48px;
    }}
    .stat-box {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; text-align: center;
    }}
    .stat-box h3 {{ font-size: 2.8rem; font-weight: 800; color: var(--primary); line-height: 1; }}
    .stat-box p {{ font-size: 0.9rem; color: var(--text-muted); margin-top: 6px; }}

    /* Asymmetric Cards */
    .cards-row {{
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px;
      max-width: 1400px; margin: 0 auto 100px auto; padding: 0 48px;
    }}
    .card-item {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; transition: var(--transition);
    }}
    .card-item:hover {{ border-color: var(--primary); transform: translateY(-6px); }}
    .card-item img {{ width: 100%; height: 220px; object-fit: cover; }}
    .card-body {{ padding: 24px; }}
    .card-body h3 {{ font-size: 1.4rem; margin-bottom: 8px; }}
    .card-body p {{ color: var(--text-muted); font-size: 0.95rem; }}

    footer {{ text-align: center; padding: 60px 24px; border-top: 1px solid var(--border); font-size: 0.9rem; color: var(--text-muted); }}

    @media (max-width: 900px) {{
      .hero-adaptive {{ grid-template-columns: 1fr; }}
      .stat-row {{ grid-template-columns: 1fr 1fr; }}
      .cards-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <nav>
    <a href="#home" class="nav-brand"><span>{profile['brand_icon']}</span> {brand}</a>
    <ul class="nav-links">
      <li><a href="#features">Capabilities</a></li>
      <li><a href="#features" class="nav-cta">Initiate Experience</a></li>
    </ul>
  </nav>

  <header class="hero-adaptive" id="home">
    <div>
      <div class="badge">{profile['hero_badge']}</div>
      <h1>{profile['headline_prefix']} <span style="color:var(--primary);">{brand}</span></h1>
      <p>{profile['hero_desc']}</p>
      <a href="#features" class="nav-cta" style="display:inline-block;padding:14px 32px;font-size:1.05rem;">{profile['btn_primary']}</a>
    </div>

    <div class="canvas-adaptive-box">
      <div class="adapt-hud">
        <button class="adapt-btn active" id="btn-custom-1" onclick="toggleCustom1(this)">Interactive 3D</button>
        <button class="adapt-btn" id="btn-sound" onclick="toggleAudioFX(this)">🔊 Audio</button>
      </div>
      <div id="webgl-canvas-container" title="360° Interactive Canvas"></div>
    </div>
  </header>

  <div class="stat-row">
    {stats_html}
  </div>

  <section class="cards-row" id="features">
    <div class="card-item">
      <img src="{c1}" alt="Feature 1">
      <div class="card-body">
        <h3>Precision Craftsmanship</h3>
        <p>Engineered without compromise, integrating state-of-the-art computational telemetry and bespoke ergonomics.</p>
      </div>
    </div>
    <div class="card-item">
      <img src="{c2}" alt="Feature 2">
      <div class="card-body">
        <h3>Spatial Depth Computing</h3>
        <p>Hardware-accelerated Three.js WebGL rendering calibrated for instantaneous 60 FPS interactions across all viewports.</p>
      </div>
    </div>
    <div class="card-item">
      <img src="{c3}" alt="Feature 3">
      <div class="card-body">
        <h3>Sovereign Reliability</h3>
        <p>Zero external tracking dependencies with deterministic local execution and zero-trust architectural integrity.</p>
      </div>
    </div>
  </section>

  <footer>
    <p>{profile['brand_icon']} {brand} &bull; Engineered by D.E.E.P Sovereign Engine &bull; 2026</p>
  </footer>

  <script>
    {scripts}
  </script>
</body>
</html>
"""
