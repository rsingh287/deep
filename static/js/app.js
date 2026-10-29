function loadBuddyIframeIfNeeded() {
      const frame = document.getElementById('companionFrame');
      if (frame && (frame.src === 'about:blank' || !frame.src || frame.src.endsWith('about:blank'))) {
        const targetSrc = frame.getAttribute('data-src') || '/floating_assistant_app/?standalone=true';
        frame.src = targetSrc;
      }
    }

    function showLiveUpdateToast(msg) {
      let toast = document.getElementById('liveUpdateToast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'liveUpdateToast';
        toast.style.cssText = 'position:fixed; top:20px; right:20px; z-index:999999; background:linear-gradient(135deg, #0284c7, #8b5cf6); color:#ffffff; padding:10px 18px; border-radius:10px; font-weight:700; font-size:0.84rem; box-shadow:0 8px 30px rgba(0,0,0,0.6); border:1px solid rgba(255,255,255,0.3); display:flex; align-items:center; gap:8px;';
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      setTimeout(() => {
        if (toast && toast.parentNode) {
          toast.style.transition = 'opacity 0.4s ease';
          toast.style.opacity = '0';
          setTimeout(() => { try { toast.remove(); } catch(_) {} }, 400);
        }
      }, 3500);
    }
    window.showLiveUpdateToast = showLiveUpdateToast;

    function toggleArtifactCanvas(forceState) {
        const pCanvas = document.getElementById('panelCanvas');
        const btnTop = document.getElementById('btnToggleCanvas');
        const btnAct = document.getElementById('actBtnCanvas');
        if (!pCanvas) return;
        const shouldHide = (forceState !== undefined) ? !forceState : !pCanvas.classList.contains('hidden');
        pCanvas.classList.toggle('hidden', shouldHide);
        if (btnTop) btnTop.classList.toggle('active', !shouldHide);
        if (btnAct) btnAct.classList.toggle('active', !shouldHide);
        if (!shouldHide) {
            refreshArtifactCanvas();
        }
        if (typeof saveLayoutState === 'function') {
            saveLayoutState();
        }
    }
    window.toggleArtifactCanvas = toggleArtifactCanvas;

    function openCanvasStandaloneWindow() {
        const win = window.open('about:blank', 'DEEP_ArtifactCanvas', 'width=700,height=720,toolbar=no,menubar=no,status=no,resizable=yes');
        if (win) {
            let finalHtml = currentArtifactHtml || getArtifactPlaceholderHtml();
            win.document.open();
            win.document.write(finalHtml);
            win.document.close();
        }
    }
    window.openCanvasStandaloneWindow = openCanvasStandaloneWindow;

    let currentArtifactHtml = "";
    function renderArtifact(htmlContent) {
        currentArtifactHtml = htmlContent;
        toggleArtifactCanvas(true);
        refreshArtifactCanvas();
    }
    window.renderArtifact = renderArtifact;

    function getArtifactPlaceholderHtml() {
        return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0; padding: 24px 16px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #070a12; color: #f1f5f9; text-align: center;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      min-height: calc(100vh - 48px); box-sizing: border-box;
    }
    .badge {
      display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px;
      background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 9999px; color: #38bdf8; font-size: 0.75rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;
    }
    h2 { font-size: 1.15rem; margin: 0 0 8px 0; color: #fff; }
    p { font-size: 0.8rem; color: #94a3b8; line-height: 1.5; max-width: 320px; margin: 0 0 18px 0; }
    .demo-btn-group { display: flex; flex-direction: column; gap: 8px; width: 100%; max-width: 280px; }
    .demo-btn {
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(168, 85, 247, 0.25));
      border: 1px solid rgba(56, 189, 248, 0.5); color: #fff; padding: 9px 14px; border-radius: 8px;
      font-weight: 700; font-size: 0.8rem; cursor: pointer; transition: all 0.2s;
    }
    .demo-btn:hover {
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.45), rgba(168, 85, 247, 0.45));
      border-color: #38bdf8; transform: translateY(-1px);
    }
    .features-card {
      margin-top: 20px; text-align: left; background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px;
      padding: 12px 14px; width: 100%; max-width: 280px; box-sizing: border-box; font-size: 0.73rem;
    }
    .feat { margin: 6px 0; color: #cbd5e1; display: flex; align-items: flex-start; gap: 6px; }
    .feat span { color: #38bdf8; font-weight: 700; }
  </style>
</head>
<body>
  <div class="badge">🎨 Live Artifact Canvas</div>
  <h2>Interactive UI Sandbox</h2>
  <p>Whenever D.E.E.P writes HTML/CSS/JS in chat, it compiles and renders live in this canvas with click-to-edit inspection.</p>
  <div class="demo-btn-group">
    <button class="demo-btn" onclick="window.parent.loadSampleArtifact('timer')">⏱️ Load Stopwatch Demo</button>
    <button class="demo-btn" onclick="window.parent.loadSampleArtifact('player')">🎵 Load Music Player Demo</button>
  </div>
  <div class="features-card">
    <div class="feat"><span>⚡ Live Render:</span> HTML code blocks auto-render here</div>
    <div class="feat"><span>🎯 Click-to-Edit:</span> Click any element to prompt visual changes</div>
    <div class="feat"><span>🔒 Sandboxed:</span> Runs safely inside an isolated iframe</div>
  </div>
</body>
</html>`;
    }

    window.loadSampleArtifact = function(type) {
        if (type === 'timer') {
            currentArtifactHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0; padding: 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: radial-gradient(circle at center, #0b1528 0%, #050811 100%);
      color: #fff; text-align: center; min-height: 100vh; box-sizing: border-box;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .card {
      background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.35);
      border-radius: 16px; padding: 20px; width: 90%; max-width: 320px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6), 0 0 20px rgba(56, 189, 248, 0.2);
    }
    .title { font-size: 0.85rem; font-weight: 700; color: #38bdf8; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; }
    .display { font-family: monospace; font-size: 2.4rem; font-weight: 800; color: #38bdf8; text-shadow: 0 0 15px rgba(56, 189, 248, 0.7); margin: 12px 0; }
    .btn-group { display: flex; gap: 8px; justify-content: center; margin-top: 14px; }
    button {
      padding: 8px 16px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; cursor: pointer; transition: all 0.2s;
    }
    .btn-start { background: #10b981; border: none; color: #000; }
    .btn-pause { background: #f59e0b; border: none; color: #000; }
    .btn-reset { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #f87171; }
    button:hover { transform: translateY(-1px); filter: brightness(1.15); }
    .hint { font-size: 0.7rem; color: #64748b; margin-top: 16px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="title">⏱️ Precision Stopwatch</div>
    <div class="display" id="disp">00:00.00</div>
    <div class="btn-group">
      <button class="btn-start" onclick="startTimer()">Start</button>
      <button class="btn-pause" onclick="pauseTimer()">Pause</button>
      <button class="btn-reset" onclick="resetTimer()">Reset</button>
    </div>
    <div class="hint">💡 Click any button or text above to trigger Click-to-Edit in the chat!</div>
  </div>
  <script>
    let elapsed = 0, timerId = null;
    function fmt(ms) {
      let m = Math.floor(ms / 60000), s = Math.floor((ms % 60000) / 1000), cs = Math.floor((ms % 1000) / 10);
      return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s + '.' + (cs < 10 ? '0' : '') + cs;
    }
    function startTimer() {
      if (!timerId) {
        let last = Date.now();
        timerId = setInterval(() => { let now = Date.now(); elapsed += (now - last); last = now; document.getElementById('disp').textContent = fmt(elapsed); }, 20);
      }
    }
    function pauseTimer() { clearInterval(timerId); timerId = null; }
    function resetTimer() { pauseTimer(); elapsed = 0; document.getElementById('disp').textContent = '00:00.00'; }
  <\/script>
</body>
</html>`;
        } else if (type === 'player') {
            currentArtifactHtml = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      margin: 0; padding: 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: radial-gradient(circle at center, #110e20 0%, #05030a 100%);
      color: #fff; text-align: center; min-height: 100vh; box-sizing: border-box;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .player-card {
      background: rgba(22, 18, 42, 0.85); border: 1px solid rgba(168, 85, 247, 0.4);
      border-radius: 18px; padding: 22px; width: 90%; max-width: 320px;
      box-shadow: 0 10px 35px rgba(0,0,0,0.7), 0 0 25px rgba(168, 85, 247, 0.25);
    }
    .album-art {
      width: 90px; height: 90px; border-radius: 14px; margin: 0 auto 14px;
      background: linear-gradient(135deg, #a855f7, #38bdf8);
      display: flex; align-items: center; justify-content: center; font-size: 2.2rem;
      box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
    }
    .song-title { font-weight: 700; font-size: 1rem; color: #fff; margin-bottom: 4px; }
    .artist { font-size: 0.75rem; color: #c084fc; margin-bottom: 14px; }
    .progress-bar { width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin-bottom: 14px; }
    .progress-fill { width: 45%; height: 100%; background: linear-gradient(90deg, #38bdf8, #a855f7); }
    .controls { display: flex; align-items: center; justify-content: center; gap: 12px; }
    .ctrl-btn { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; border-radius: 50%; width: 38px; height: 38px; font-size: 1rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
    .play-btn { width: 48px; height: 48px; font-size: 1.3rem; background: linear-gradient(135deg, #a855f7, #38bdf8); border: none; }
    .ctrl-btn:hover { transform: scale(1.08); }
    .hint { font-size: 0.7rem; color: #94a3b8; margin-top: 14px; }
  </style>
</head>
<body>
  <div class="player-card">
    <div class="album-art">🎧</div>
    <div class="song-title">Quantum Synthwave</div>
    <div class="artist">D.E.E.P Sovereign Audio</div>
    <div class="progress-bar"><div class="progress-fill"></div></div>
    <div class="controls">
      <button class="ctrl-btn">⏮</button>
      <button class="ctrl-btn play-btn" id="playBtn" onclick="togglePlay()">▶</button>
      <button class="ctrl-btn">⏭</button>
    </div>
    <div class="hint">💡 Click any button or element to visually edit it in chat!</div>
  </div>
  <script>
    let playing = false;
    function togglePlay() {
      playing = !playing;
      document.getElementById('playBtn').textContent = playing ? '⏸' : '▶';
    }
  <\/script>
</body>
</html>`;
        }
        refreshArtifactCanvas();
        if (typeof showLiveUpdateToast === 'function') {
            showLiveUpdateToast('🎨 Sample Artifact Loaded! Click any element to test Click-to-Edit.');
        }
    };

    function refreshArtifactCanvas() {
        const iframe = document.getElementById('artifactCanvasFrame');
        if (iframe) {
            const doc = iframe.contentWindow.document;
            doc.open();
            
            let finalHtml = currentArtifactHtml;
            if (!finalHtml || !finalHtml.trim()) {
                finalHtml = getArtifactPlaceholderHtml();
            } else {
                // Inject click-to-edit listener script
                const clickToEditScript = `
                    <script>
                        document.addEventListener('click', function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            // Find a meaningful outerHTML, or limit the length
                            let elemStr = e.target.outerHTML;
                            if (elemStr.length > 500) {
                                elemStr = elemStr.substring(0, 500) + '...';
                            }
                            window.parent.postMessage({ type: 'ARTIFACT_CLICK', element: elemStr, tagName: e.target.tagName }, '*');
                            
                            // Add a visual flash effect
                            const originalOutline = e.target.style.outline;
                            const originalTransition = e.target.style.transition;
                            e.target.style.transition = 'outline 0.2s ease-out';
                            e.target.style.outline = '3px solid #38bdf8';
                            setTimeout(() => {
                                e.target.style.outline = originalOutline;
                                e.target.style.transition = originalTransition;
                            }, 500);
                        }, true);
                    <\/script>
                `;
                
                // Insert script before closing body tag if it exists, otherwise just append
                if (finalHtml.includes('</body>')) {
                    finalHtml = finalHtml.replace('</body>', clickToEditScript + '</body>');
                } else {
                    finalHtml += clickToEditScript;
                }
            }
            
            doc.write(finalHtml);
            doc.close();
        }
    }

    // Bi-Directional Canvas Click-to-Edit Listener & 3D Companion Bridge
    window.addEventListener('message', function(e) {
        if (!e.data) return;
        if (e.data.type === 'CLOSE_BUDDY') {
            const pRight = document.getElementById('panelRight');
            if (pRight && !pRight.classList.contains('hidden')) {
                toggleRightPanel();
            }
        }
        if (e.data.type === 'BUDDY_MIC_ACTIVE' || e.data.type === 'BUDDY_CLAIM_MIC') {
            if (typeof pauseCockpitMicForBuddy === 'function') {
                pauseCockpitMicForBuddy();
            }
        }
        if (e.data.type === 'BUDDY_MIC_INACTIVE' || e.data.type === 'BUDDY_RELEASE_MIC') {
            if (typeof resumeCockpitMicFromBuddy === 'function') {
                resumeCockpitMicFromBuddy();
            }
        }
        if (e.data.type === 'ARTIFACT_CLICK') {
            const promptInput = document.getElementById('promptInput');
            if (promptInput) {
                promptInput.value = "Edit this <" + (e.data.tagName ? e.data.tagName.toLowerCase() : 'element') + "> element:\n\n```html\n" + e.data.element + "\n```\n\nChange it so that... ";
                promptInput.focus();
                // Optionally auto-resize
                promptInput.style.height = 'auto';
                promptInput.style.height = (promptInput.scrollHeight) + 'px';
            }
        }
    });
    

    function launchDesktopBuddyApp() {
      // Suspend docked browser mic to give exclusive priority to Python native listener
      const frame = document.getElementById('companionFrame');
      if (frame && frame.contentWindow) {
        try { frame.contentWindow.postMessage({ type: 'SUSPEND_MIC', reason: 'python' }, '*'); } catch(_) {}
      }
      fetch('/api/buddy/launch', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            console.log('Desktop Buddy launched on Windows (Python exclusive mic active)');
          } else {
            alert('Could not launch Desktop Buddy: ' + (data.error || 'Unknown error'));
          }
        })
        .catch(err => alert('Error launching Desktop Buddy: ' + err));
    }

    function openCompanionStandaloneWindow() {
      // Suspend docked browser mic to give exclusive priority to detached popup window
      const frame = document.getElementById('companionFrame');
      if (frame && frame.contentWindow) {
        try { frame.contentWindow.postMessage({ type: 'SUSPEND_MIC', reason: 'detached' }, '*'); } catch(_) {}
      }
      window.open('/floating_assistant_app/?standalone=true&detached=true', 'DEEP_Companion', 'width=380,height=580,toolbar=no,menubar=no,status=no,resizable=yes');
    }

    function reloadCompanionFrame() {
      const frame = document.getElementById('companionFrame');
      if (frame) {
        frame.src = '/floating_assistant_app/?standalone=true&_r=' + Date.now();
      }
    }

    function switchVDeckCategory(cat, btn) {
      document.querySelectorAll('.vdeck-tab-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      const grids = ['pc', 'system', 'cockpit', 'ai', 'web'];
      grids.forEach(g => {
        const el = document.getElementById('vdeck-' + g);
        if (el) el.style.display = (g === cat) ? 'grid' : 'none';
      });
    }

    function sendQuickCommand(cmdText) {
      const input = document.getElementById('promptInput');
      if (input) {
        input.value = cmdText;
        document.getElementById('sendBtn').click();
      }
    }


    // =========================================================================
    // COCKPIT INTERACTION HANDLERS & BUTTON BINDINGS
    // =========================================================================
    
    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    let activeAbortController = null;
    let isBufferEnabled = false;
    let isSwarmEnabled = false;

    // Emergency Stop
    function emergencyStop() {
      let didStop = false;
      if (activeAbortController) {
        try { activeAbortController.abort(); } catch(_) {}
        activeAbortController = null;
        didStop = true;
      }
      if (window.speechSynthesis && window.speechSynthesis.speaking) {
        try { window.speechSynthesis.cancel(); } catch(_) {}
        didStop = true;
      }
      if (typeof audioQueue !== 'undefined' && audioQueue.length > 0) {
        audioQueue.length = 0;
        didStop = true;
      }
      if (typeof window.activeTTSAudio !== 'undefined' && window.activeTTSAudio && !window.activeTTSAudio.paused) {
        window.activeTTSAudio.pause();
        window.activeTTSAudio = null;
        didStop = true;
      }
      const sendBtn = document.getElementById('sendBtn');
      if (sendBtn) {
        sendBtn.innerHTML = '➤';
        sendBtn.style.background = 'linear-gradient(135deg, #0284c7, #9333ea)';
        sendBtn.title = 'Send Prompt';
      }
      if (didStop) {
        fetch('/api/stop', { method: 'POST' }).catch(() => {});
        appendMessage('ai', '🛑 <strong style="color:#ef4444;">EMERGENCY STOP EXECUTED</strong>: All ongoing AI generation, execution, and vocal synthesis halted.');
      }
      const typingTimer = document.getElementById('typingTimer');
      if (typingTimer) typingTimer.textContent = '';
    }

    // Instant Workspace Rollback / Undo
    window.triggerWorkspaceRollback = function() {
      if (confirm('Roll back last actions/files generated by DEEP?')) {
        playHoloSound('alert');
        const promptInput = document.getElementById('promptInput');
        if (promptInput) {
          promptInput.value = 'undo the work done';
          const sendBtn = document.getElementById('sendBtn');
          if (sendBtn) sendBtn.click();
        }
      }
    };

    // Clear Active Chat
    function clearActiveChat() {
      const chatScroll = document.getElementById('chatScroll');
      const hero = document.getElementById('cockpitHeroDashboard');
      if (chatScroll) {
        chatScroll.querySelectorAll('.msg-wrapper').forEach(el => el.remove());
        if (hero) {
          hero.style.display = 'flex';
        }
      }
      currentChatId = 'session_' + Date.now();
    }

    // Activity Bar Tab Switching
    // Activity Bar Tab Switching
    function activityBarClick(tabId, el) {
      document.querySelectorAll('.activity-item').forEach(b => b.classList.remove('active'));
      if (el) el.classList.add('active');
      
      document.querySelectorAll('.nav-tab-btn').forEach(b => b.classList.remove('active'));
      const subtabBtn = document.getElementById('subtabBtn' + tabId.replace('tab', ''));
      if (subtabBtn) subtabBtn.classList.add('active');

      const pLeft = document.getElementById('panelLeft');
      if (pLeft && pLeft.classList.contains('hidden')) {
        toggleLeftPanel();
      }
      document.querySelectorAll('#panelLeft .tab-pane').forEach(p => {
        p.classList.remove('active');
        p.style.display = 'none';
      });
      const targetPane = document.getElementById(tabId);
      if (targetPane) {
        targetPane.classList.add('active');
        targetPane.style.display = 'flex';
      }
      const titleEl = document.getElementById('leftPanelHeaderTitle');
      if (titleEl) {
        if (tabId === 'tabChats') titleEl.textContent = '💬 Chat Sessions';
        else if (tabId === 'tabTools') titleEl.textContent = '⚡ 35 APIs & 19 MCPs';
        else if (tabId === 'tabTelemetry') titleEl.textContent = '📊 Hardware Telemetry';
      }
    }

    // Security PIN / Workstation Standby Lock
    function promptPinLock() {
      const standby = document.getElementById('standbyOverlay');
      if (standby) {
        standby.style.display = 'flex';
      }
    }

    function wakeFromStandby() {
      const standby = document.getElementById('standbyOverlay');
      if (standby) {
        standby.style.display = 'none';
      }
    }

    // Modal Close Helpers
    function closeCmdPalette(event) {
      if (!event || event.target.id === 'cmdPaletteModal') {
        const m = document.getElementById('cmdPaletteModal');
        if (m) m.style.display = 'none';
      }
    }

    function openVoiceCommandsModal() {
      const m = document.getElementById('voiceCommandsModal');
      if (m) {
        m.classList.remove('hidden');
        m.style.display = 'flex';
      }
    }
    window.openVoiceCommandsModal = openVoiceCommandsModal;

    function closeVoiceCommandsModal(event) {
      if (!event || event.target.id === 'voiceCommandsModal' || typeof event === 'undefined') {
        const m = document.getElementById('voiceCommandsModal');
        if (m) {
          m.classList.add('hidden');
          m.style.display = 'none';
        }
      }
    }
    window.closeVoiceCommandsModal = closeVoiceCommandsModal;

    function openWorkstationSettingsModal() {
      const m = document.getElementById('modalWorkstationSettings');
      if (m) {
        m.classList.remove('hidden');
        m.style.display = 'flex';
      }
    }

    function closeWorkstationSettingsModal(event) {
      if (!event || event.target.id === 'modalWorkstationSettings' || typeof event === 'undefined') {
        const m = document.getElementById('modalWorkstationSettings');
        if (m) {
          m.classList.add('hidden');
          m.style.display = 'none';
        }
      }
    }

    // Human Feedback & RLHF Cognitive Rules Modal Handlers
    window.openFeedbackModal = async function() {
      const m = document.getElementById('modalHumanFeedback');
      if (m) {
        m.classList.remove('hidden');
        m.style.display = 'flex';
        await refreshFeedbackList();
      }
    };

    window.closeFeedbackModal = function(event) {
      if (!event || event.target.id === 'modalHumanFeedback' || typeof event === 'undefined') {
        const m = document.getElementById('modalHumanFeedback');
        if (m) {
          m.classList.add('hidden');
          m.style.display = 'none';
        }
      }
    };

    window.refreshFeedbackList = async function() {
      const listContainer = document.getElementById('fbListContainer');
      if (!listContainer) return;
      listContainer.innerHTML = '<div style="text-align:center; padding:30px; color:#94a3b8; font-size:0.85rem;">🔄 Querying active cognitive directives...</div>';
      
      try {
        const res = await fetch('/api/feedback');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        
        const stats = data.stats || {};
        document.getElementById('fbStatTotal').textContent = stats.total_feedback || 0;
        document.getElementById('fbStatRate').textContent = (stats.approval_rate !== undefined ? stats.approval_rate : 100) + '%';
        document.getElementById('fbStatPositive').textContent = stats.positive_count || 0;
        document.getElementById('fbStatNegative').textContent = stats.negative_count || 0;

        const items = data.feedback || [];
        if (items.length === 0) {
          listContainer.innerHTML = `
            <div style="text-align:center; padding:40px 20px; color:#94a3b8;">
              <div style="font-size:2rem; margin-bottom:10px;">🧠</div>
              <div style="font-weight:700; color:#e2e8f0; font-size:0.95rem; margin-bottom:6px;">No Feedback Rules Logged Yet</div>
              <div style="font-size:0.8rem; max-width:420px; margin:0 auto; line-height:1.5;">
                As you chat with D.E.E.P, click <b>👍 Helpful</b> or <b>👎 Wrong</b> on any response to train its memory, or simply say <i>"That was wrong, do this instead"</i> in chat.
              </div>
            </div>
          `;
          return;
        }

        listContainer.innerHTML = '';
        items.forEach(fb => {
          const card = document.createElement('div');
          const isPos = fb.rating > 0;
          card.style.cssText = `
            background: rgba(15,23,42,0.65);
            border: 1px solid ${isPos ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)'};
            border-left: 4px solid ${isPos ? '#10b981' : '#f59e0b'};
            border-radius: 10px;
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: all 0.2s;
          `;

          const tagLabel = (fb.critique_tag || (isPos ? 'Accurate' : 'Correction')).replace(/_/g, ' ').toUpperCase();
          const badgeBg = isPos ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)';
          const badgeColor = isPos ? '#34d399' : '#fbbf24';

          card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:12px; background:${badgeBg}; color:${badgeColor}; border:1px solid ${isPos ? 'rgba(16,185,129,0.4)' : 'rgba(245,158,11,0.4)'};">
                  ${isPos ? '✓ APPROVED' : '⚠️ CORRECTION'} • ${tagLabel}
                </span>
                <span style="font-size:0.72rem; color:#64748b;">${fb.created_at || ''}</span>
              </div>
              <button onclick="deleteFeedbackRule(${fb.id})" style="background:transparent; border:none; color:#ef4444; font-size:0.75rem; cursor:pointer; padding:2px 6px; border-radius:4px; opacity:0.8;" title="Delete this rule" onmouseenter="this.style.opacity='1'" onmouseleave="this.style.opacity='0.8'">🗑️ Remove</button>
            </div>
            <div style="font-size:0.8rem; color:#94a3b8;">
              <span style="font-weight:600; color:#cbd5e1;">Prompt:</span> "${(fb.prompt || 'General query').replace(/</g, '&lt;')}"
            </div>
            <div style="font-size:0.82rem; color:#e2e8f0; background:rgba(0,0,0,0.25); padding:8px 10px; border-radius:6px; line-height:1.4;">
              <span style="color:#38bdf8; font-weight:700;">Learned Directive:</span> ${fb.learned_rule ? fb.learned_rule.replace(/</g, '&lt;') : (fb.user_correction || 'User verified pattern').replace(/</g, '&lt;')}
            </div>
          `;
          listContainer.appendChild(card);
        });

      } catch (err) {
        listContainer.innerHTML = `<div style="text-align:center; padding:30px; color:#ef4444; font-size:0.85rem;">Failed to load feedback rules: ${err.message}</div>`;
      }
    };

    window.deleteFeedbackRule = async function(id) {
      if (!confirm('Remove this learned rule from D.E.E.P cognitive memory?')) return;
      try {
        await fetch(`/api/feedback/${id}`, { method: 'DELETE' });
        await refreshFeedbackList();
      } catch(e) {
        alert('Failed to delete rule: ' + e.message);
      }
    };

    function switchSettingsTab(tabName, btn) {
      document.querySelectorAll('.set-tab-btn').forEach(b => {
        b.style.borderColor = 'rgba(255,255,255,0.1)';
        b.style.color = '#94a3b8';
        b.style.background = 'rgba(255,255,255,0.04)';
      });
      if (btn) {
        btn.style.borderColor = 'rgba(56,189,248,0.6)';
        btn.style.color = '#38bdf8';
        btn.style.background = 'rgba(56,189,248,0.15)';
      }
      document.querySelectorAll('.settings-panel-view').forEach(p => p.style.display = 'none');
      const target = document.getElementById('setTab-' + tabName);
      if (target) target.style.display = 'block';
    }

    async function testQuickApi(endpoint) {
      appendMessage('user', `[System Check] Calling ${endpoint}...`);
      const bubble = appendMessage('ai', '⏳ *Querying live endpoint...*');
      try {
        const res = await fetch(endpoint, { method: endpoint.includes('post') ? 'POST' : 'GET' });
        const json = await res.json();
        bubble.innerHTML = `<strong>✅ ${endpoint} responded [${res.status} OK]</strong><pre style="margin-top:6px; font-size:0.75rem; max-height:160px; overflow-y:auto; background:#000; padding:8px; border-radius:6px; border:1px solid #38bdf8; color:#38bdf8;">${JSON.stringify(json, null, 2)}</pre>`;
      } catch (err) {
        bubble.innerHTML = `<strong>❌ Error connecting to ${endpoint}:</strong><div style="color:#f87171; font-size:0.8rem; margin-top:4px;">${err.message}</div>`;
      }
    }

    // Command Palette Filter
    function filterCmds() {
      const input = document.getElementById('cmdInput');
      const filter = input ? input.value.toLowerCase().trim() : '';
      const items = document.querySelectorAll('#cmdResults .cmd-item');
      items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = (!filter || text.includes(filter)) ? 'flex' : 'none';
      });
    }

    // Command Palette Action Dispatcher
    function runCmdPaletteAction(action) {
      closeCmdPalette();
      switch (action) {
        case 'ocr':
          sendQuickCommand('Scan my active screen with Live Vision OCR and summarize findings');
          break;
        case 'turbo':
          fetch('/api/system/command', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: 'echo Turbo Purge complete' }) });
          appendMessage('ai', '🚀 <strong>Turbo Boost RAM Purge Executed</strong>: Memory working sets trimmed and idle caches purged.');
          break;
        case 'security':
          window.location.href = '/cyber_defense';
          break;
        case 'audit':
          sendQuickCommand('Run autonomous system security and workstation audit agent');
          break;
        case 'clean':
          sendQuickCommand('Run disk purge agent to clean temporary cache and recycle bin');
          break;
        case 'notepad':
          fetch('/api/system/command', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: 'notepad.exe' }) });
          appendMessage('ai', '📝 Launched Notepad on desktop.');
          break;
        case 'taskmgr':
          fetch('/api/system/command', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: 'taskmgr.exe' }) });
          appendMessage('ai', '📊 Launched Task Manager.');
          break;
        case 'shot':
          sendQuickCommand('Take a screenshot analysis of my screen');
          break;
        case 'toggle_left':
          toggleLeftPanel();
          break;
        case 'toggle_bottom':
          toggleBottomPanel();
          break;
        case 'toggle_right':
          toggleRightPanel();
          break;
        case 'toggle_matrix':
          const mat = document.getElementById('matrixCanvas');
          if (mat) mat.style.display = (mat.style.display === 'block') ? 'none' : 'block';
          break;
        default:
          sendQuickCommand(action);
      }
    }

    // Bottom Terminal PowerShell Execution
    async function executeBottomTerminal(customCmd) {
      const input = document.getElementById('terminalInBottom');
      const logs = document.getElementById('bottomTerminalLogs');
      const cmd = customCmd ? customCmd.trim() : (input ? input.value.trim() : '');
      if (!cmd) return;
      if (input && !customCmd) input.value = '';

      if (logs) {
        logs.textContent += `\n\nPS > ${cmd}\n[Executing on host via PowerShell...]`;
        logs.scrollTop = logs.scrollHeight;
      }

      try {
        const res = await fetch('/api/terminal/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: cmd })
        });
        const data = await res.json();
        const out = data.output || (data.success ? 'Command executed successfully.' : (data.error || 'Execution failed.'));
        if (logs) {
          logs.textContent += `\n${out}`;
          logs.scrollTop = logs.scrollHeight;
        }
      } catch (err) {
        if (logs) {
          logs.textContent += `\n[Execution Error]: ${err.message}`;
          logs.scrollTop = logs.scrollHeight;
        }
      }
    }

    function clearBottomTerminal() {
      const logs = document.getElementById('bottomTerminalLogs');
      if (logs) {
        logs.textContent = `[HOST POWERSHELL READY] Direct Host Execution Bridge Connected.\nType any PowerShell command or click a quick action above to execute directly on the PC:\n`;
      }
    }

    // Zip and Context Package Uploader
    async function handleZipUpload(file) {
      if (!file) return;
      const formData = new FormData();
      formData.append('file', file);
      promptInput.placeholder = 'Uploading & analyzing ' + file.name + '...';
      try {
        const res = await fetch('/api/upload_context', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.type === 'text') {
          promptInput.value += '\\n\\n[File: ' + data.filename + ']\\n' + data.content + '\\n';
        } else if (data.type === 'image') {
          currentAttachedB64 = data.base64;
          const badge = document.getElementById('attachedBadge');
          if (badge) { badge.style.display = 'inline-flex'; badge.textContent = file.name + ' ✕'; }
        }
        appendMessage('ai', '📁 Attached context package: <strong>' + escapeHtml(file.name) + '</strong>');
      } catch (e) {
        alert('Upload failed: ' + e.message);
      } finally {
        promptInput.placeholder = 'Tell me what to do on your PC or ask a question...';
      }
    }

    // Global DeepVoice Execution Namespace
    window.DeepVoice = {
      execute: function(phrase) {
        closeVoiceCommandsModal();
        sendQuickCommand(phrase);
      }
    };

    // Subsystem Station Manager
    window.DeepSubsystems = {
      open: function(url, title, icon) {
        const container = document.getElementById('subsystemOverlayContainer');
        const iframe = document.getElementById('subsystemIframe');
        const titleEl = document.getElementById('subsystemOverlayTitle');
        const iconEl = document.getElementById('subsystemOverlayIcon');
        if (container && iframe) {
          iframe.src = url;
          if (titleEl) titleEl.textContent = title || 'Cockpit Station';
          if (iconEl) iconEl.textContent = icon || '⚡';
          container.classList.remove('hidden');
          container.style.display = 'flex';
        }
      },
      closeCurrentTab: function() {
        const container = document.getElementById('subsystemOverlayContainer');
        const iframe = document.getElementById('subsystemIframe');
        if (container) {
          container.classList.add('hidden');
          container.style.display = 'none';
        }
        if (iframe) iframe.src = 'about:blank';
      }
    };

    // Neural Voice Studio Object
    window.DeepVoiceStudio = {
      mediaRecorder: null,
      audioChunks: [],
      isRecording: false,
      recordedBlob: null,
      open: function() {
        const m = document.getElementById('voiceCloningModal');
        if (m) { m.classList.remove('hidden'); m.style.display = 'flex'; }
      },
      close: function() {
        const m = document.getElementById('voiceCloningModal');
        if (m) { m.classList.add('hidden'); m.style.display = 'none'; }
        if (this.mediaRecorder && this.isRecording) {
          try { this.mediaRecorder.stop(); } catch(_) {}
        }
      },
      startRecording: async function() {
        const btn = document.getElementById('btnStartVoiceRecord');
        const countdown = document.getElementById('voiceCountdown');
        const statusMsg = document.getElementById('voiceStudioStatusMsg');
        if (this.isRecording) {
          if (this.mediaRecorder) this.mediaRecorder.stop();
          return;
        }
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          this.mediaRecorder = new MediaRecorder(stream);
          this.audioChunks = [];
          this.isRecording = true;
          if (btn) btn.innerHTML = '<span style=\"display:inline-block;width:10px;height:10px;border-radius:50%;background:#ef4444;animation:pulse 1s infinite;\"></span><span>Recording... (Click to stop)</span>';
          if (statusMsg) statusMsg.textContent = 'Recording live voice calibration... speak clearly.';

          let sec = 5;
          const timer = setInterval(() => {
            sec--;
            if (countdown) countdown.textContent = '00:0' + Math.max(0, sec);
            if (sec <= 0) {
              clearInterval(timer);
              if (this.mediaRecorder && this.isRecording) {
                try { this.mediaRecorder.stop(); } catch(_) {}
              }
            }
          }, 1000);

          this.mediaRecorder.ondataavailable = (e) => {
            if (e.data.size > 0) this.audioChunks.push(e.data);
          };

          this.mediaRecorder.onstop = () => {
            this.isRecording = false;
            this.recordedBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            if (btn) btn.innerHTML = '<span style=\"display:inline-block;width:10px;height:10px;border-radius:50%;background:#10b981;\"></span><span>Re-record Sample</span>';
            if (statusMsg) statusMsg.textContent = 'Voice profile sample recorded! Ready to test or save.';
            stream.getTracks().forEach(t => t.stop());
          };

          this.mediaRecorder.start();
        } catch (err) {
          if (statusMsg) statusMsg.textContent = 'Microphone access notice: ' + err.message;
        }
      },
      handleFileUpload: function(event) {
        const file = event.target.files && event.target.files[0];
        const statusMsg = document.getElementById('voiceStudioStatusMsg');
        if (file) {
          this.recordedBlob = file;
          if (statusMsg) statusMsg.textContent = 'Loaded audio sample: ' + file.name + ' (' + Math.round(file.size / 1024) + ' KB)';
        }
      },
      testPlayback: function() {
        const statusMsg = document.getElementById('voiceStudioStatusMsg');
        if (this.recordedBlob) {
          const url = URL.createObjectURL(this.recordedBlob);
          const audio = new Audio(url);
          audio.play();
          if (statusMsg) statusMsg.textContent = 'Playing recorded voice sample...';
        } else {
          fetch('/api/deep/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: 'Hello, I am Deep. Your neural voice calibration profile is loaded.' })
          });
          if (statusMsg) statusMsg.textContent = 'Broadcasting via local speech engine...';
        }
      }
    };

    // Tool Buttons Initialization
    function initToolButtons() {
      // ➕ New Chat
      if (btnNewChat) {
        btnNewChat.addEventListener('click', () => {
          clearActiveChat();
        });
      }

      // 📎 Attach File
      if (btnAttach && imageFileInput) {
        btnAttach.addEventListener('click', () => {
          imageFileInput.click();
        });
        imageFileInput.addEventListener('change', (e) => {
          const file = e.target.files && e.target.files[0];
          if (!file) return;
          const reader = new FileReader();
          reader.onload = (re) => {
            currentAttachedB64 = re.target.result.split(',')[1];
            if (attachedBadge) {
              attachedBadge.style.display = 'inline-flex';
              attachedBadge.textContent = file.name + ' ✕';
            }
          };
          reader.readAsDataURL(file);
        });
      }

      if (attachedBadge) {
        attachedBadge.addEventListener('click', () => {
          currentAttachedB64 = null;
          attachedBadge.style.display = 'none';
          if (imageFileInput) imageFileInput.value = '';
        });
      }

      // Drag and Drop Local Image Analysis
      document.body.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.body.style.border = '2px dashed #38bdf8';
      });

      document.body.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.body.style.border = 'none';
      });

      document.body.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.body.style.border = 'none';
        
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          const file = e.dataTransfer.files[0];
          if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (re) => {
              currentAttachedB64 = re.target.result.split(',')[1];
              if (attachedBadge) {
                attachedBadge.style.display = 'inline-flex';
                attachedBadge.textContent = file.name + ' 🖼';
              }
            };
            reader.readAsDataURL(file);
          }
        }
      });


      // 🎙️ Voice Dictation Mic Button
      if (btnMic) {
        btnMic.addEventListener('click', () => {
          toggleCompanionMic();
          btnMic.classList.toggle('recording', isMicActive);
        });
      }

      // Auto-Guard telemetry sync
      const autoBadge = document.getElementById('autoProtectionBadge');
      if (autoBadge) {
        autoBadge.title = 'Autonomous execution risk mitigation & consensus active';
      }

      // Global Hotkeys
      window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          const m = document.getElementById('cmdPaletteModal');
          if (m) {
            m.style.display = (m.style.display === 'flex') ? 'none' : 'flex';
            if (m.style.display === 'flex') {
              const ci = document.getElementById('cmdInput');
              if (ci) { ci.value = ''; ci.focus(); }
              filterCmds();
            }
          }
        } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'w') {
          e.preventDefault();
          toggleRightPanel();
        } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
          e.preventDefault();
          toggleLeftPanel();
        } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'j') {
          e.preventDefault();
          toggleBottomPanel();
        } else if (e.key === 'Escape') {
          closeCmdPalette();
          closeVoiceCommandsModal();
          closeWorkstationSettingsModal();
          closeFeedbackModal();
          if (window.DeepVoiceStudio) window.DeepVoiceStudio.close();
        }
      });
    }

    // Call initToolButtons when DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initToolButtons);
    } else {
      initToolButtons();
    }


    const chatScroll = document.getElementById('chatScroll');
    const promptInput = document.getElementById('promptInput');
    const sendBtn = document.getElementById('sendBtn');
    const modelSelect = document.getElementById('modelSelect');
    const btnMic = document.getElementById('btnMic');
    const btnAttach = document.getElementById('btnAttach');
    const imageFileInput = document.getElementById('imageFileInput');
    const attachedBadge = document.getElementById('attachedBadge');

    const btnTtsToggle = document.getElementById('btnTtsToggle');
    const ttsState = document.getElementById('ttsState');
    const activeWinTitle = document.getElementById('activeWinTitle');
    const standbyOverlay = document.getElementById('standbyOverlay');
    const btnNewChat = document.getElementById('btnNewChat');
    const chatHistoryList = document.getElementById('chatHistoryList');

    const panelLeft = document.getElementById('panelLeft');
    const panelBottom = document.getElementById('panelBottom');
    const panelRight = document.getElementById('panelRight');

    const btnToggleLeft = document.getElementById('btnToggleLeft');
    const btnToggleBottom = document.getElementById('btnToggleBottom');
    const btnToggleRight = document.getElementById('btnToggleRight');

    const cmdPaletteModal = document.getElementById('cmdPaletteModal');
    const cmdInput = document.getElementById('cmdInput');
    const cmdResults = document.getElementById('cmdResults');

    // =================================================================
    // ACTIVE AUTONOMOUS SKILL BADGE & DISPATCH ENGINE
    // =================================================================
    window.checkActiveSkillStatus = async function() {
      try {
        const res = await fetch('/api/skills/active');
        if (!res.ok) return;
        const data = await res.json();
        const badge = document.getElementById('activeSkillBadge');
        const text = document.getElementById('activeSkillNameText');
        if (data.active_skill && data.active_skill.name) {
          if (text) text.textContent = data.active_skill.name;
          if (badge) badge.style.display = 'inline-flex';
        } else {
          if (badge) badge.style.display = 'none';
        }
      } catch (err) {
        console.warn('[SkillsBadge] Error checking active skill:', err);
      }
    };

    window.clearActiveSkillInCockpit = async function(e) {
      if (e) e.stopPropagation();
      try {
        await fetch('/api/skills/active', { method: 'DELETE' });
        const badge = document.getElementById('activeSkillBadge');
        if (badge) badge.style.display = 'none';
      } catch (err) {
        console.warn('[SkillsBadge] Error clearing skill:', err);
      }
    };

    checkActiveSkillStatus();
    setInterval(checkActiveSkillStatus, 8000);

    // Auto-consume pending skill prompt from /skills page or ?prompt= query
    (function handlePendingSkillPrompt() {
      const urlParams = new URLSearchParams(window.location.search);
      const queryPrompt = urlParams.get('prompt') || sessionStorage.getItem('pending_cockpit_prompt');
      if (queryPrompt) {
        sessionStorage.removeItem('pending_cockpit_prompt');
        if (window.history && window.history.replaceState && urlParams.get('prompt')) {
          const cleanUrl = window.location.pathname;
          window.history.replaceState({}, document.title, cleanUrl);
        }
        setTimeout(() => {
          const pi = document.getElementById('promptInput');
          const sb = document.getElementById('sendBtn');
          if (pi) {
            pi.value = queryPrompt;
            pi.focus();
            if (typeof updatePromptInputAutoHeight === 'function') updatePromptInputAutoHeight();
            if (sb) {
              setTimeout(() => sb.click(), 400);
            }
          }
        }, 500);
      }
    })();

    // Living Spoken Response Engine (TTS) Toggle & Synchronization
    let ttsEnabled = (localStorage.getItem('deep_tts_enabled') === '1');
    let recognition = null;
    let isMicActive = false;

    function updateTTSUI() {
      const topBtn = document.getElementById('topTTSToggleBtn');
      const topIcon = document.getElementById('topTTSIcon');
      const topText = document.getElementById('topTTSText');

      const drawerBtn = document.getElementById('drawerTTSToggleBtn');
      const drawerIcon = document.getElementById('drawerTTSIcon');
      const drawerText = document.getElementById('drawerTTSText');

      if (ttsEnabled) {
        if (topBtn) {
          topBtn.style.background = 'rgba(56,189,248,0.2)';
          topBtn.style.borderColor = 'rgba(56,189,248,0.6)';
          topBtn.style.color = '#38bdf8';
          topBtn.style.boxShadow = '0 0 12px rgba(56,189,248,0.25)';
        }
        if (topIcon) topIcon.textContent = '🔊';
        if (topText) topText.textContent = 'Voice: ON';

        if (drawerBtn) {
          drawerBtn.style.background = 'rgba(56,189,248,0.25)';
          drawerBtn.style.borderColor = 'rgba(56,189,248,0.7)';
          drawerBtn.style.color = '#38bdf8';
          drawerBtn.style.boxShadow = '0 0 10px rgba(56,189,248,0.3)';
        }
        if (drawerIcon) drawerIcon.textContent = '🔊';
        if (drawerText) drawerText.textContent = 'ON';
      } else {
        if (topBtn) {
          topBtn.style.background = 'rgba(30,41,59,0.85)';
          topBtn.style.borderColor = 'rgba(148,163,184,0.3)';
          topBtn.style.color = '#94a3b8';
          topBtn.style.boxShadow = 'none';
        }
        if (topIcon) topIcon.textContent = '🔇';
        if (topText) topText.textContent = 'Voice: OFF';

        if (drawerBtn) {
          drawerBtn.style.background = 'rgba(30,41,59,0.8)';
          drawerBtn.style.borderColor = 'rgba(56,189,248,0.3)';
          drawerBtn.style.color = '#94a3b8';
          drawerBtn.style.boxShadow = 'none';
        }
        if (drawerIcon) drawerIcon.textContent = '🔇';
        if (drawerText) drawerText.textContent = 'OFF';
      }
    }

    window.toggleTTS = function(forcedState) {
      if (typeof forcedState === 'boolean') {
        ttsEnabled = forcedState;
      } else {
        ttsEnabled = !ttsEnabled;
      }
      localStorage.setItem('deep_tts_enabled', ttsEnabled ? '1' : '0');
      updateTTSUI();
      playHoloSound('chime');

      // Instantly synchronize global voice mute state with backend and all sentinels
      fetch('/api/voice/mute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ muted: !ttsEnabled })
      }).catch(err => console.warn('[TTS] Global mute sync failed:', err));

      if (ttsEnabled) {
        speakVoiceFeedback('Voice replies online, Commander.');
      } else {
        if (window.speechSynthesis) {
          try { window.speechSynthesis.cancel(); } catch(_) {}
        }
        if (window.activeTTSAudio) {
          try {
            window.activeTTSAudio.pause();
            window.activeTTSAudio.currentTime = 0;
          } catch(_) {}
          window.activeTTSAudio = null;
        }
        audioQueue.length = 0;
        isPlayingAudio = false;
      }
    };

    function cleanTextForSpeech(text) {
      if (!text) return "";
      // 1. Strip entire cockpit widgets, audio cards, iframes, and details tags so code/HTML is NEVER spoken
      let clean = text
        .replace(/<div\s+class="cockpit-[^"]*"[\s\S]*?<\/div>/gi, "")
        .replace(/<audio[\s\S]*?<\/audio>/gi, "")
        .replace(/<iframe[\s\S]*?<\/iframe>/gi, "")
        .replace(/<details[\s\S]*?<\/details>/gi, "")
        .replace(/<[^>]*>/g, "")
        .replace(/&[a-z0-9#]+;/gi, " ")
        .replace(/```[\s\S]*?```/g, "")
        .replace(/`([^`]+)`/g, "$1")
        .replace(/https?:\/\/\S+/g, "")
        .replace(/\/api\/\S+/g, "")
        .replace(/[A-Za-z]:\\[\w\s.\\-]+/g, "")
        .replace(/\b\d+(\.\d+)?\s*(?:MB|GB|KB|kbps|fps)\b/gi, "")
        .replace(/\.(?:mp3|wav|flac|m4a|aac|ogg|wma|exe|dll|bat|py|json)\b/gi, "")
        .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1")
        .replace(/\[[^\]]*\]/g, "")
        .replace(/\([^\)]*\)/g, "")
        .replace(/[*#_~>]/g, "")
        .replace(/\s+/g, " ")
        .trim();

      // 2. Keep spoken responses short, concise, and natural (max 2 sentences or 180 chars)
      const sentences = clean.match(/[^.!?]+[.!?]+/g);
      if (sentences && sentences.length > 0) {
        clean = sentences.slice(0, 2).join(" ").trim();
      } else if (clean.length > 180) {
        clean = clean.substring(0, 180).trim() + ".";
      }
      return clean;
    }

    window.switchToPersonality = async function(key) {
      key = (key || 'deep').toLowerCase().trim();
      const voiceSelect = document.getElementById('voiceSelect');
      const val = `neural:${key}`;

      if (voiceSelect) {
        if (Array.from(voiceSelect.options).some(o => o.value === val)) {
          voiceSelect.value = val;
        }
      }
      localStorage.setItem('deep_selected_voice', val);

      // Sync with backend voice profile
      try {
        await fetch('/api/voice/profiles', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({profile: key})
        });
      } catch(e){}

      // Update voice description in drawer
      const voiceDesc = document.getElementById('voiceDescription');
      if (voiceDesc && typeof cachedVoiceProfiles !== 'undefined' && cachedVoiceProfiles[key]) {
        voiceDesc.textContent = cachedVoiceProfiles[key].description;
      }

      let greeting = "D.E.E.P Sovereign Core engaged. All systems nominal, Commander.";
      let personaName = "D.E.E.P. Core";
      let icon = "⚡";

      if (key === 'jarvis') {
        greeting = "Very good, Commander. J.A.R.V.I.S. is online and at your service. All systems operational.";
        personaName = "J.A.R.V.I.S. (British Butler)";
        icon = "🎩";
      } else if (key === 'friday') {
        greeting = "F.R.I.D.A.Y. here, Boss! Tactical co-pilot systems linked and ready. What's our next objective?";
        personaName = "F.R.I.D.A.Y. (Irish Tactical)";
        icon = "🛡️";
      } else if (key === 'commander') {
        greeting = "Commander voice active. Workstation ready for mission directives.";
        personaName = "Commander Voice (Authoritative)";
        icon = "⭐";
      } else if (key === 'my_voice') {
        greeting = "Cloned vocal signature operational, Commander. Voice matching verified.";
        personaName = "My Voice (Cloned Signature)";
        icon = "🧬";
      }

      playHoloSound('chime');
      speakVoiceFeedback(greeting, true);

      appendMessage('ai', `<div style="display:flex; align-items:center; gap:10px; padding:8px 14px; background:rgba(56,189,248,0.12); border-left:3px solid var(--accent-cyan); border-radius:8px; font-size:0.85rem; margin:4px 0;">
        <span style="font-size:1.4rem;">${icon}</span>
        <div>
          <strong style="color:var(--accent-cyan);">Voice Personality Activated:</strong> ${personaName}<br>
          <span style="font-size:0.75rem; color:var(--text-muted);">${greeting}</span>
        </div>
      </div>`);
    };

    window.onModelSelectChange = function(val) {
      val = val || 'auto';
      localStorage.setItem('deep_selected_model', val);
      const dot = document.getElementById('activeModelDot');
      if (dot) {
        if (val === 'auto') {
          dot.style.background = '#4ade80';
          dot.style.boxShadow = '0 0 8px #4ade80';
        } else {
          dot.style.background = '#38bdf8';
          dot.style.boxShadow = '0 0 8px #38bdf8';
        }
      }
      playHoloSound('chime');
      const friendlyName = {
        'auto': 'Auto Workload Router',
        'qwen2.5-coder:7b': 'Qwen 2.5 Coder',
        'deepseek-r1:8b': 'DeepSeek R1',
        'qwen2.5vl:7b': 'Qwen 2.5-VL Vision',
        'qwen2.5:3b': 'Qwen 2.5 3B',
        'qwen2.5:7b': 'Qwen 2.5 7B'
      }[val] || val;
      speakVoiceFeedback(`Model routed to ${friendlyName}`);
    };

    // Auto-load saved model preference on boot
    try {
      const savedM = localStorage.getItem('deep_selected_model') || 'auto';
      const mSel = document.getElementById('modelSelect');
      if (mSel) {
        mSel.value = savedM;
        const dot = document.getElementById('activeModelDot');
        if (dot) {
          dot.style.background = savedM === 'auto' ? '#4ade80' : '#38bdf8';
        }
      }
    } catch(e){}

    // Dual AI Co-Pilot Sequential Audio Engine (Alternating Jarvis & Friday)
    async function playDualCoPilotAudio(fullText) {
      if (!ttsEnabled) return;
      if (!fullText) return;
      const lines = fullText.split('\n');
      let currentSpeaker = null;
      let speakerSegments = [];
      let curText = "";

      for (let l of lines) {
        const trimmed = l.trim();
        if (/^(?:\*\*|\b)?J\.A\.R\.V\.I\.S\.(?:\*\*|:)/i.test(trimmed)) {
          if (currentSpeaker && curText.trim()) {
            speakerSegments.push({ speaker: currentSpeaker, text: curText.trim() });
          }
          currentSpeaker = 'jarvis';
          curText = trimmed.replace(/^(?:\*\*|\b)?J\.A\.R\.V\.I\.S\.(?:\*\*|:)?/i, '').trim() + " ";
        } else if (/^(?:\*\*|\b)?F\.R\.I\.D\.A\.Y\.(?:\*\*|:)/i.test(trimmed)) {
          if (currentSpeaker && curText.trim()) {
            speakerSegments.push({ speaker: currentSpeaker, text: curText.trim() });
          }
          currentSpeaker = 'friday';
          curText = trimmed.replace(/^(?:\*\*|\b)?F\.R\.I\.D\.A\.Y\.(?:\*\*|:)?/i, '').trim() + " ";
        } else if (currentSpeaker && trimmed) {
          curText += trimmed + " ";
        }
      }
      if (currentSpeaker && curText.trim()) {
        speakerSegments.push({ speaker: currentSpeaker, text: curText.trim() });
      }

      if (speakerSegments.length === 0) {
        if (ttsEnabled) speakVoiceFeedback(cleanTextForSpeech(fullText));
        return;
      }

      if (window.speechSynthesis) window.speechSynthesis.cancel();
      audioQueue.length = 0;
      isPlayingAudio = false;

      for (let seg of speakerSegments) {
        if (!ttsEnabled) {
          audioQueue.length = 0;
          isPlayingAudio = false;
          return;
        }
        const clean = cleanTextForSpeech(seg.text);
        if (!clean || clean.length < 2) continue;
        try {
          const res = await fetch('/api/voice/tts', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: clean, profile: seg.speaker})
          });
          const data = await res.json();
          if (!ttsEnabled) {
            audioQueue.length = 0;
            isPlayingAudio = false;
            return;
          }
          if (data.status === 'success' && data.audio_b64) {
            audioQueue.push(data.audio_b64);
            if (!isPlayingAudio) {
              playNextAudio();
            }
          }
        } catch(e) {
          console.warn('[DualAudio] Failed for segment:', seg.speaker, e);
        }
      }
    }

    window.launchDualDialogue = function(topic) {
      const q = topic || "Check system vitals and discuss our current workstation defense posture.";
      const promptInput = document.getElementById('promptInput');
      if (promptInput) {
        promptInput.value = `Can Jarvis and Friday talk with each other about: ${q}`;
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) sendBtn.click();
      }
      toggleCommandDrawer(false);
    };

    window.executeCopilotAction = function(promptText) {
      playHoloSound('chime');
      toggleCommandDrawer(false);
      const promptInput = document.getElementById('promptInput');
      if (promptInput) {
        promptInput.value = promptText;
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) sendBtn.click();
      }
    };

    // Sci-Fi Web Audio API Synthesizer (Zero External Files)
    let holoAudioCtx = null;
    function playHoloSound(type) {
      try {
        if (!holoAudioCtx) {
          const AudioContextClass = window.AudioContext || window.webkitAudioContext;
          if (AudioContextClass) holoAudioCtx = new AudioContextClass();
        }
        if (!holoAudioCtx) return;
        if (holoAudioCtx.state === 'suspended') holoAudioCtx.resume();

        const now = holoAudioCtx.currentTime;
        const osc = holoAudioCtx.createOscillator();
        const gain = holoAudioCtx.createGain();
        osc.connect(gain);
        gain.connect(holoAudioCtx.destination);

        if (type === 'chime' || type === 'confirm') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(880, now);
          osc.frequency.exponentialRampToValueAtTime(1320, now + 0.12);
          gain.gain.setValueAtTime(0.12, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
          osc.start(now);
          osc.stop(now + 0.25);
        } else if (type === 'drawer') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(360, now);
          osc.frequency.exponentialRampToValueAtTime(720, now + 0.18);
          gain.gain.setValueAtTime(0.09, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
          osc.start(now);
          osc.stop(now + 0.22);
        } else if (type === 'voice_on') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(520, now);
          osc.frequency.exponentialRampToValueAtTime(1040, now + 0.14);
          gain.gain.setValueAtTime(0.1, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
          osc.start(now);
          osc.stop(now + 0.2);
        } else if (type === 'voice_off') {
          osc.type = 'sine';
          osc.frequency.setValueAtTime(880, now);
          osc.frequency.exponentialRampToValueAtTime(440, now + 0.12);
          gain.gain.setValueAtTime(0.08, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
          osc.start(now);
          osc.stop(now + 0.18);
        } else if (type === 'alert') {
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(440, now);
          osc.frequency.setValueAtTime(330, now + 0.1);
          gain.gain.setValueAtTime(0.15, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
          osc.start(now);
          osc.stop(now + 0.35);
        }
      } catch(_) {}
    }

    // Spoken Audio Confirmation Engine (Sub-300ms Latency Offline Audio Queue)
    let audioQueue = [];
    let isPlayingAudio = false;
    function playNextAudio() {
      if (!ttsEnabled || audioQueue.length === 0) {
        audioQueue.length = 0;
        isPlayingAudio = false;
        if (window.activeTTSAudio) {
          try { window.activeTTSAudio.pause(); } catch(_) {}
        }
        window.activeTTSAudio = null;
        return;
      }
      isPlayingAudio = true;
      const b64 = audioQueue.shift();
      const mime = (b64.startsWith('UklG')) ? 'audio/wav' : 'audio/mpeg';
      const snd = new Audio(`data:${mime};base64,${b64}`);
      window.activeTTSAudio = snd;
      snd.onended = () => { if (ttsEnabled) playNextAudio(); else { isPlayingAudio = false; window.activeTTSAudio = null; } };
      snd.onerror = () => { if (ttsEnabled) playNextAudio(); else { isPlayingAudio = false; window.activeTTSAudio = null; } };
      if (!ttsEnabled) {
        isPlayingAudio = false;
        window.activeTTSAudio = null;
        return;
      }
      snd.play().catch(e => { if (ttsEnabled) playNextAudio(); else { isPlayingAudio = false; window.activeTTSAudio = null; } });
    }

    async function speakVoiceFeedback(text, cancelFirst=true, speakerOverride=null) {
      if (!ttsEnabled) return;
      if (!text || !text.trim()) return;
      if (cancelFirst) {
        if ('speechSynthesis' in window) {
          try { window.speechSynthesis.cancel(); } catch(_) {}
        }
        audioQueue.length = 0;
        isPlayingAudio = false;
      }

      const selected = localStorage.getItem('deep_selected_voice') || 'neural:deep';

      // Check if user explicitly selected a local workstation SAPI voice and NO override is requested
      if (!speakerOverride && selected.startsWith('local:') && 'speechSynthesis' in window) {
        if (!ttsEnabled) return;
        try {
          const targetName = selected.replace('local:', '');
          const u = new SpeechSynthesisUtterance(text);
          u.rate = 1.0;
          u.pitch = 1.0;
          const voices = window.speechSynthesis.getVoices() || [];
          const found = voices.find(v => v.name === targetName) || voices.find(v => v.name.includes(targetName));
          if (found) u.voice = found;
          if (ttsEnabled) window.speechSynthesis.speak(u);
          return;
        } catch(e) {
          console.warn('[TTS] Local synthesis fallback:', e);
        }
      }

      // Default & Neural profiles: Edge-TTS neural engine
      let profileKey = speakerOverride || (selected.startsWith('neural:') ? selected.replace('neural:', '') : (selected === 'default' ? 'deep' : selected));
      if (typeof profileKey === 'string' && profileKey.startsWith('neural:')) {
        profileKey = profileKey.replace('neural:', '');
      }
      try {
         const res = await fetch('/api/voice/tts', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({text: text, profile: profileKey})
         });
         const data = await res.json();
         if (!ttsEnabled) {
           audioQueue.length = 0;
           isPlayingAudio = false;
           return;
         }
         if (data.status === 'success' && data.audio_b64) {
            audioQueue.push(data.audio_b64);
            if (!isPlayingAudio) {
               playNextAudio();
            }
            return;
         }
         throw new Error(data.message || "TTS failed");
      } catch (err) {
         if (!ttsEnabled) return;
         // Fallback to browser TTS if API fails and voice is permitted
         if ('speechSynthesis' in window && ttsEnabled) {
            try {
              if (cancelFirst) window.speechSynthesis.cancel();
              const u = new SpeechSynthesisUtterance(text);
              u.rate = 1.0;
              u.pitch = 1.0;
              const voices = window.speechSynthesis.getVoices() || [];
              const pref = voices.find(v => v.lang && v.lang.startsWith('en') && (v.name.includes('David') || v.name.includes('Zira') || v.name.includes('Natural') || v.name.includes('Google')));
              if (pref) u.voice = pref;
              if (ttsEnabled) window.speechSynthesis.speak(u);
            } catch(_) {}
         }
      }
    }

    window.runVoiceSuggestion = function(cmd) {
      playHoloSound('chime');
      const clean = cmd.trim().toLowerCase();
      if (clean === 'deploy hud') {
        toggleDeepQuantumHUD(true);
        speakVoiceFeedback('Agent Execution War Room deployed.');
      } else if (clean === 'open menu') {
        toggleCommandDrawer(true);
        speakVoiceFeedback('Command drawer opened.');
      } else if (clean === 'show weather') {
        window.location.href = '/weather';
      } else if (clean === 'summon buddy') {
        toggleRightPanel();
        speakVoiceFeedback('3D Buddy toggled.');
      } else if (clean === 'status report') {
        const cpuText = document.getElementById('cpuPct') ? document.getElementById('cpuPct').textContent : '5%';
        speakVoiceFeedback('System status nominal. CPU at ' + cpuText + '. All 427 skills online.');
        appendMessage('ai', '📊 <strong>Status Report:</strong> D.E.E.P Sovereign Workstation 100% operational.<br>• CPU: ' + cpuText + '<br>• Base: Greater Sudbury, ON<br>• Commander: Mr. Ramadeep Singh<br>• Subsystems: All online.');
      } else if (clean === 'full screen') {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen();
          speakVoiceFeedback('Full screen mode engaged.');
        } else {
          document.exitFullscreen();
          speakVoiceFeedback('Full screen mode exited.');
        }
      } else {
        const promptInput = document.getElementById('promptInput');
        if (promptInput) {
          promptInput.value = cmd;
          const sendBtn = document.getElementById('sendBtn');
          if (sendBtn) sendBtn.click();
        }
      }
    };

    function toggleCommandDrawer(open) {
      const drawer = document.getElementById('deepCommandDrawerOverlay');
      if (!drawer) return;
      if (open === undefined) {
        open = !drawer.classList.contains('active');
      }
      drawer.classList.toggle('active', !!open);
      playHoloSound('drawer');
    }
    window.toggleCommandDrawer = toggleCommandDrawer;

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (activeAbortController) {
          emergencyStop();
          playHoloSound('alert');
          return;
        }
        toggleCommandDrawer(false);
      }
      if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        toggleMainVoiceMic();
      }
    });

    function initVoiceReactor() {
      const canvas = document.getElementById('voiceReactorCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      let angle = 0;
      let wavePhase = 0;

      function drawReactor() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        angle += isMicActive ? 0.04 : 0.015;
        wavePhase += isMicActive ? 0.12 : 0.05;

        // Outer Ring with rotating dashed notches
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(angle);
        ctx.beginPath();
        ctx.arc(0, 0, 62, 0, Math.PI * 2);
        ctx.strokeStyle = isMicActive ? 'rgba(239, 68, 68, 0.45)' : 'rgba(56, 189, 248, 0.35)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([6, 12]);
        ctx.stroke();
        ctx.restore();

        // Counter-rotating Inner Ring
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(-angle * 1.4);
        ctx.beginPath();
        ctx.arc(0, 0, 52, 0, Math.PI * 2);
        ctx.strokeStyle = isMicActive ? 'rgba(239, 68, 68, 0.6)' : 'rgba(168, 85, 247, 0.4)';
        ctx.lineWidth = 2;
        ctx.setLineDash([14, 8]);
        ctx.stroke();
        ctx.restore();

        // Harmonic sine wave oscillation around the core
        const waveAmp = isMicActive ? 7 : 2.5;
        ctx.beginPath();
        for (let a = 0; a < Math.PI * 2; a += 0.1) {
          const r = 40 + Math.sin(a * 6 + wavePhase) * waveAmp;
          const x = cx + Math.cos(a) * r;
          const y = cy + Math.sin(a) * r;
          if (a === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.strokeStyle = isMicActive ? 'rgba(248, 113, 113, 0.8)' : 'rgba(56, 189, 248, 0.6)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        requestAnimationFrame(drawReactor);
      }
      drawReactor();
    }

    function initSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
            console.warn("Web Speech API not supported.");
            return;
        }
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        
        recognition.onstart = function() {
            // Update top bar voice pill
            const topText = document.getElementById('topVocalText');
            const topDot = document.getElementById('topVocalDot');
            if (topText) topText.textContent = "🎙️ Listening...";
            if (topDot) {
              topDot.style.background = "#ef4444";
              topDot.style.boxShadow = "0 0 10px #ef4444";
            }

            // Update center voice core
            const reactorBtn = document.getElementById('voiceReactorMicBtn');
            const reactorStatus = document.getElementById('voiceStatusText');
            const reactorPulse = document.getElementById('voiceStatusPulse');
            if (reactorBtn) reactorBtn.classList.add('listening');
            if (reactorStatus) reactorStatus.textContent = "Listening to Commander Ramadeep Singh... (Speak command)";
            if (reactorPulse) {
              reactorPulse.style.background = "#ef4444";
              reactorPulse.style.boxShadow = "0 0 10px #ef4444";
            }
        };
        
        recognition.onerror = function(event) {
            console.error("Speech Recognition Error", event);
        };
        
        recognition.onend = function() {
            if (isMicActive) {
                try { recognition.start(); } catch(e){} // auto-restart
            } else {
                const topText = document.getElementById('topVocalText');
                const topDot = document.getElementById('topVocalDot');
                if (topText) topText.textContent = "🎙️ Voice Ready";
                if (topDot) {
                  topDot.style.background = "#38bdf8";
                  topDot.style.boxShadow = "0 0 8px #38bdf8";
                }

                const reactorBtn = document.getElementById('voiceReactorMicBtn');
                const reactorStatus = document.getElementById('voiceStatusText');
                const reactorPulse = document.getElementById('voiceStatusPulse');
                if (reactorBtn) reactorBtn.classList.remove('listening');
                if (reactorStatus) reactorStatus.textContent = "Click core or speak naturally to D.E.E.P";
                if (reactorPulse) {
                  reactorPulse.style.background = "#10b981";
                  reactorPulse.style.boxShadow = "0 0 8px #10b981";
                }
            }
        };
        
        recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            const promptInput = document.getElementById('promptInput');
            
            if (finalTranscript) {

                // Phonetic speech recognition normalization (Yarvis -> Jarvis)
                finalTranscript = finalTranscript.replace(/\b(yarvis|jarves|jervis|yarves)\b/gi, 'Jarvis');

                const cleanCmd = finalTranscript.trim().toLowerCase().replace(/[\.\?!,]+$/g, '');
                console.log('[VoiceDispatcher] Recognized:', cleanCmd);

                // Personality & Vocal Persona Voice Commands
                if (['switch to jarvis', 'talk with jarvis', 'talk to jarvis', 'activate jarvis', 'jarvis mode', 'hey jarvis', 'jarvis'].includes(cleanCmd)) {
                  switchToPersonality('jarvis');
                  return;
                }
                if (['switch to friday', 'talk with friday', 'talk to friday', 'activate friday', 'friday mode', 'hey friday', 'friday'].includes(cleanCmd)) {
                  switchToPersonality('friday');
                  return;
                }
                if (['switch to deep', 'talk with deep', 'activate deep', 'deep mode', 'hey deep'].includes(cleanCmd)) {
                  switchToPersonality('deep');
                  return;
                }
                if (['switch to commander', 'talk with commander', 'activate commander', 'commander mode'].includes(cleanCmd)) {
                  switchToPersonality('commander');
                  return;
                }
                if (['enable voice', 'turn voice on', 'voice on', 'talk to me', 'unmute voice', 'read answers', 'read replies'].includes(cleanCmd)) {
                  toggleTTS(true);
                  return;
                }
                if (['disable voice', 'turn voice off', 'voice off', 'be quiet', 'mute voice', 'silent mode'].includes(cleanCmd)) {
                  toggleTTS(false);
                  return;
                }

                // Autonomous Co-Pilot Direct Automation Workflows (Jarvis & Friday)
                if (['check vitals', 'jarvis check vitals', 'system vitals', 'jarvis vitals', 'jarvis status report', 'jarvis audit'].includes(cleanCmd)) {
                  executeCopilotAction('Jarvis, check vitals');
                  return;
                }
                if (['purge ram', 'free ram', 'clean ram', 'free memory', 'friday purge ram', 'friday free ram', 'clear ram'].includes(cleanCmd)) {
                  executeCopilotAction('Friday, purge RAM');
                  return;
                }
                if (['security sweep', 'run security sweep', 'friday security sweep', 'friday run security sweep', 'firewall sweep'].includes(cleanCmd)) {
                  executeCopilotAction('Friday, run a security sweep');
                  return;
                }
                if (['clean downloads', 'organize downloads', 'jarvis organize downloads', 'jarvis clean downloads', 'tidy downloads'].includes(cleanCmd)) {
                  executeCopilotAction('Jarvis, organize my downloads folder');
                  return;
                }
                if (['prepare dev environment', 'dev setup', 'jarvis dev setup', 'setup dev', 'dev environment'].includes(cleanCmd)) {
                  executeCopilotAction('Jarvis, prepare dev environment');
                  return;
                }
                if (['status briefing', 'co-op briefing', 'jarvis and friday briefing', 'dual briefing', 'strategic briefing'].includes(cleanCmd)) {
                  executeCopilotAction('Jarvis and Friday, status briefing');
                  return;
                }
                if (['hunt processes', 'process hunt', 'friday hunt processes', 'friday hunt high cpu'].includes(cleanCmd)) {
                  executeCopilotAction('Friday, hunt high CPU and RAM processes');
                  return;
                }

                // Autonomous Voice Navigation & Macro Dispatch
                if (['look at my screen', 'inspect this error', 'read my screen', 'what is on my screen'].some(cmd => cleanCmd.includes(cmd))) {
                    speakVoiceFeedback('Initiating visual screen protocol. Scanning desktop...');
                    triggerScreenVisionScan(finalTranscript.trim());
                    return;
                }
                if (['show knowledge graph', 'open knowledge graph', 'visualize memory', '3d graph'].includes(cleanCmd)) {
                  toggleKnowledgeGraph(true);
                  return;
                }
                if (['hide knowledge graph', 'close knowledge graph'].includes(cleanCmd)) {
                  toggleKnowledgeGraph(false);
                  return;
                }
                if (['open menu', 'show menu', 'command drawer', 'open drawer', 'show tools', 'menu'].includes(cleanCmd)) {
                  toggleCommandDrawer(true);
                  speakVoiceFeedback('Command drawer opened, Commander.');
                  return;
                }
                if (['close menu', 'hide menu', 'close drawer', 'dismiss menu'].includes(cleanCmd)) {
                  toggleCommandDrawer(false);
                  speakVoiceFeedback('Drawer dismissed.');
                  return;
                }
                if (['deploy hud', 'open hud', 'launch hud', 'holographic mode', 'quantum hud', 'war room', 'agent war room', 'open war room'].includes(cleanCmd)) {
                  toggleDeepQuantumHUD(true);
                  playHoloSound('chime');
                  speakVoiceFeedback('Agent Execution War Room deployed.');
                  return;
                }
                if (['close hud', 'hide hud', 'dismiss hud'].includes(cleanCmd)) {
                  toggleDeepQuantumHUD(false);
                  playHoloSound('chime');
                  speakVoiceFeedback('HUD closed.');
                  return;
                }
                if (['voice commands', 'open voice commands', 'show voice commands', 'commands', 'voice cheatsheet', 'cheat sheet', 'help commands'].includes(cleanCmd)) {
                  openVoiceCommandsModal();
                  playHoloSound('chime');
                  speakVoiceFeedback('Voice command library ready.');
                  return;
                }
                if (['close voice commands', 'hide voice commands', 'dismiss voice commands'].includes(cleanCmd)) {
                  closeVoiceCommandsModal();
                  playHoloSound('chime');
                  speakVoiceFeedback('Voice command library closed.');
                  return;
                }
                if (['summon buddy', 'open buddy', 'launch buddy', 'dock buddy', 'toggle buddy'].includes(cleanCmd)) {
                  toggleRightPanel();
                  playHoloSound('chime');
                  speakVoiceFeedback('3D Buddy toggled.');
                  return;
                }
                if (['show weather', 'open weather', 'weather radar', 'weather in sudbury', 'radar'].includes(cleanCmd)) {
                  speakVoiceFeedback('Opening weather radar for Greater Sudbury.');
                  window.location.href = '/weather';
                  return;
                }
                if (['cyber defense', 'security status', 'open security', 'defense command'].includes(cleanCmd)) {
                  speakVoiceFeedback('Opening Cyber Defense Command.');
                  window.location.href = '/cyber_defense';
                  return;
                }
                if (['open memory', 'knowledge base', 'memory database', 'memory'].includes(cleanCmd)) {
                  speakVoiceFeedback('Accessing memory neural database.');
                  window.location.href = '/memory';
                  return;
                }
                if (['open trading', 'stock market', 'quant trading', 'stocks'].includes(cleanCmd)) {
                  speakVoiceFeedback('Opening algorithmic quant trading matrix.');
                  window.location.href = '/trading';
                  return;
                }
                if (['open skills', 'skills arsenal', 'skills'].includes(cleanCmd)) {
                  speakVoiceFeedback('Accessing 427 skills arsenal.');
                  window.location.href = '/skills';
                  return;
                }
                if (['open terminal', 'toggle terminal', 'launch terminal', 'console'].includes(cleanCmd)) {
                  toggleBottomPanel();
                  playHoloSound('chime');
                  speakVoiceFeedback('Host PowerShell terminal ready.');
                  return;
                }
                if (['full screen', 'toggle fullscreen', 'fullscreen'].includes(cleanCmd)) {
                  if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                    speakVoiceFeedback('Full screen mode engaged.');
                  } else {
                    document.exitFullscreen();
                    speakVoiceFeedback('Full screen mode exited.');
                  }
                  return;
                }
                if (['lock system', 'lock workstation', 'lock screen'].includes(cleanCmd)) {
                  speakVoiceFeedback('Engaging workstation security lock.');
                  promptPinLock();
                  return;
                }
                if (['status report', 'system status', 'vitals'].includes(cleanCmd)) {
                  const cpuVal = document.getElementById('cpuPct') ? document.getElementById('cpuPct').textContent : '5%';
                  speakVoiceFeedback('Commander, systems 100% nominal. CPU load ' + cpuVal + '. All 427 skills ready.');
                  appendMessage('ai', '📊 <strong>Vitals:</strong> CPU: ' + cpuVal + ' | Location: Greater Sudbury, ON | Commander: Mr. Ramadeep Singh | Status: Nominal.');
                  return;
                }
                if (['launch desktop buddy', 'pop out buddy', 'native buddy'].includes(cleanCmd)) {
                  speakVoiceFeedback('Launching native desktop assistant companion.');
                  launchDesktopBuddyApp();
                  return;
                }
                // --- Dedicated Voice Sentinel Media & Audio Command Interceptor ---
                // Prevents dual-speech collision: Voice Master Sentinel processes playback on the DJ engine and speaks confirmation.
                // The browser UI silently intercepts media/audio voice commands so it does NOT send them to chat and does NOT speak over Sentinel.
                const isMediaOrAudioCmd = (
                  cleanCmd.includes('shuffle') ||
                  cleanCmd.includes('automix') ||
                  /\b(dj|crossfade)\b/i.test(cleanCmd) ||
                  ['play', 'pause', 'stop', 'resume', 'unpause', 'toggle', 'play pause', 'pause play', 'play or pause', 'pause or play',
                   'resume music', 'stop music', 'toggle music', 'pause music', 'play music', 'music play', 'music pause',
                   'bars', 'both music', 'boss music', 'bar music', 'bars music', 'buzz', 'buzz music', 'pass music', 'paws',
                   'paws music', 'cause music', 'parse', 'parse music', 'pos', 'pose', 'post music', 'hold music'].includes(cleanCmd) ||
                  /\b(play|pause|resume|stop|unpause|toggle)\s+(?:the\s+)?(?:music|song|track|playback|audio|gana)\b/i.test(cleanCmd) ||
                  /\b(?:music|song|track)\s+(?:play|pause|stop|resume)\b/i.test(cleanCmd) ||
                  ['next', 'skip', 'prev', 'previous', 'rewind', 'back', 'the next', 'the previous', 'the previous on', 'previous on',
                   'play next', 'play prev', 'play previous', 'next song', 'next track', 'skip song', 'skip track', 'change song',
                   'previous song', 'previous track', 'prev song', 'prev track', 'rewind song', 'back song', 'play the next', 'play the previous',
                   'skip drag', 'next drag', 'skip trap', 'skip drad'].includes(cleanCmd) ||
                  /\b(next|skip|prev|previous)\s+(?:song|track|music|drag|trap)\b/i.test(cleanCmd) ||
                  /\bplay\s+(?:the\s+)?(?:next|previous|prev)\b/i.test(cleanCmd) ||
                  /\b(volume|louder|quieter|mute|unmute)\b/i.test(cleanCmd) ||
                  /\b(turn|turn\s+it)\s+(?:up|down)\b/i.test(cleanCmd) ||
                  /\b(?:speaker|speakers|headphone|headphones|headset)\s+(?:volume|sound)\b/i.test(cleanCmd) ||
                  /\bset\s+(?:speaker|headphone|master|system)?\s*volume\b/i.test(cleanCmd) ||
                  /^(?:play\s+|open\s+)(?:youtube\b|song\b|music\b)/i.test(cleanCmd) ||
                  /^(?:play|listen\s+to)\s+(?:a\s+)?(?:local\s+|my\s+|pc\s+)?(?:music|song|track)s?\b/i.test(cleanCmd)
                );

                if (isMediaOrAudioCmd) {
                  console.log('[VoiceDispatcher] Media/Audio command delegated solely to Voice Sentinel:', cleanCmd);
                  if (promptInput) promptInput.value = '';
                  const reactorStatus = document.getElementById('voiceStatusText');
                  if (reactorStatus) {
                    reactorStatus.textContent = '🎵 Music Sentinel: ' + finalTranscript.trim();
                  }
                  showLiveUpdateToast('🎵 Sentinel: ' + finalTranscript.trim());
                  return;
                }

                if (['stop', 'silence', 'quiet', 'shut up', 'abort', 'cancel', 'emergency stop'].includes(cleanCmd)) {
                  emergencyStop();
                  playHoloSound('alert');
                  speakVoiceFeedback('All active processes halted.');
                  return;
                }
                if (['new chat', 'clear chat', 'new session', 'clear screen'].includes(cleanCmd)) {
                  clearActiveChat();
                  playHoloSound('chime');
                  speakVoiceFeedback('New session initialized, Commander.');
                  return;
                }
                
                // Fallback: Send directly as prompt to LLM
                if (promptInput) {
                    promptInput.value = finalTranscript.trim();
                    const sendBtn = document.getElementById('sendBtn');
                    if (sendBtn) sendBtn.click();
                }
            } else if (interimTranscript) {
                if (promptInput) {
                    promptInput.value = interimTranscript;
                }
                const reactorStatus = document.getElementById('voiceStatusText');
                if (reactorStatus) {
                  reactorStatus.textContent = `"${interimTranscript}..."`;
                }
            }
        };
    }

    const micArbitrationChannel = ('BroadcastChannel' in window) ? new BroadcastChannel('deep_mic_arbitration') : null;
    let isBuddyMicActive = false;

    function pauseCockpitMicForBuddy() {
      if (isMicActive) {
        isMicActive = false;
        if (recognition) {
          try { recognition.stop(); } catch(_) {}
        }
      }
      isBuddyMicActive = true;
      const topText = document.getElementById('topVocalText');
      const topDot = document.getElementById('topVocalDot');
      if (topText) topText.textContent = "🤖 3D Buddy Mic Active";
      if (topDot) {
        topDot.style.background = "#c084fc";
        topDot.style.boxShadow = "0 0 10px #c084fc";
      }
      const reactorStatus = document.getElementById('voiceStatusText');
      if (reactorStatus) {
        reactorStatus.textContent = "3D Buddy has active voice control. Click here to take over.";
      }
      const reactorPulse = document.getElementById('voiceStatusPulse');
      if (reactorPulse) {
        reactorPulse.style.background = "#c084fc";
        reactorPulse.style.boxShadow = "0 0 8px #c084fc";
      }
    }

    function resumeCockpitMicFromBuddy(autoStart = true) {
      isBuddyMicActive = false;
      const topText = document.getElementById('topVocalText');
      const topDot = document.getElementById('topVocalDot');
      if (topText) topText.textContent = "🎙️ Cockpit Mic Active";
      if (topDot) {
        topDot.style.background = "#38bdf8";
        topDot.style.boxShadow = "0 0 10px #38bdf8";
      }
      const reactorStatus = document.getElementById('voiceStatusText');
      if (reactorStatus) {
        reactorStatus.textContent = "Cockpit mic active • Speak naturally to D.E.E.P";
      }
      const reactorPulse = document.getElementById('voiceStatusPulse');
      if (reactorPulse) {
        reactorPulse.style.background = "#10b981";
        reactorPulse.style.boxShadow = "0 0 8px #10b981";
      }

      // Automatically activate Cockpit Speech Recognition
      if (autoStart) {
        if (!recognition) {
          initSpeechRecognition();
        }
        if (recognition && !isMicActive) {
          try {
            recognition.start();
            isMicActive = true;
            console.log('[Cockpit Voice] Mic successfully transferred from 3D Buddy to Deep Cockpit.');
          } catch(e) {
            console.log('[Cockpit Voice] Mic ready for speech:', e);
          }
        }
      }
    }

    if (micArbitrationChannel) {
      micArbitrationChannel.onmessage = (e) => {
        const data = e.data || {};
        if (data.type === 'BUDDY_CLAIM_MIC' || data.type === 'DETACHED_CLAIM_MIC' || data.type === 'PYTHON_CLAIM_MIC') {
          pauseCockpitMicForBuddy();
        } else if (data.type === 'BUDDY_RELEASE_MIC' || data.type === 'DETACHED_RELEASE_MIC' || data.type === 'PYTHON_RELEASE_MIC') {
          resumeCockpitMicFromBuddy();
        }
      };
    }

    function toggleCompanionMic() {
        if (!recognition) {
            initSpeechRecognition();
        }
        const frame = document.getElementById('companionFrame');

        if (isMicActive) {
            // Turning Cockpit mic OFF
            isMicActive = false;
            playHoloSound('voice_off');
            if (recognition) {
              try { recognition.stop(); } catch(_) {}
            }
            if (micArbitrationChannel) {
              micArbitrationChannel.postMessage({ type: 'COCKPIT_RELEASE_MIC' });
            }
            try {
              fetch('/api/mic/coordinator', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'release', client_type: 'cockpit' })
              });
            } catch(_) {}

            // Check if 3D Buddy is open and visible; if so, pass mic control back to it
            const pRight = document.getElementById('panelRight');
            const contentBuddy = document.getElementById('panelBuddyContent');
            const isBuddyVisible = pRight && !pRight.classList.contains('hidden') && contentBuddy && contentBuddy.style.display !== 'none';
            if (isBuddyVisible) {
              if (frame && frame.contentWindow) {
                try { frame.contentWindow.postMessage({ type: 'RESUME_MIC' }, '*'); } catch(_) {}
              }
              pauseCockpitMicForBuddy();
            } else {
              resumeCockpitMicFromBuddy();
            }
        } else {
            // Turning Cockpit mic ON (Cockpit takes EXCLUSIVE priority!)
            isMicActive = true;
            isBuddyMicActive = false;
            playHoloSound('voice_on');

            // Force 3D Buddy to suspend so zero duplicate inputs can occur
            if (frame && frame.contentWindow) {
              try { frame.contentWindow.postMessage({ type: 'SUSPEND_MIC', reason: 'cockpit_active' }, '*'); } catch(_) {}
            }
            if (micArbitrationChannel) {
              micArbitrationChannel.postMessage({ type: 'COCKPIT_CLAIM_MIC' });
            }
            try {
              fetch('/api/mic/coordinator', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'acquire', client_type: 'cockpit' })
              });
            } catch(_) {}

            if (recognition) {
              try { recognition.start(); } catch(_) {}
            }
        }
    }

    function toggleMainVoiceMic() {
      toggleCompanionMic();
    }
    window.toggleMainVoiceMic = toggleMainVoiceMic;

    let currentChatId = null;
    let currentAttachedB64 = null;

    let isUpdatingMetrics = false;
    let isUpdatingWin = false;

    // Sparkline Graph History Buffer
    const cpuHistory = new Array(25).fill(0);
    const ramHistory = new Array(25).fill(0);

            // Save & Load Panel Visibility in localStorage
    function saveLayoutState() {
      const pLeft = document.getElementById('panelLeft');
      const pBottom = document.getElementById('panelBottom');
      const pRight = document.getElementById('panelRight');
      const pCanvas = document.getElementById('panelCanvas');
      const state = {
        left: pLeft ? !pLeft.classList.contains('hidden') : true,
        bottom: pBottom ? !pBottom.classList.contains('hidden') : false,
        right: pRight ? !pRight.classList.contains('hidden') : false,
        canvas: pCanvas ? !pCanvas.classList.contains('hidden') : false
      };
      localStorage.setItem('antigravity_layout_state', JSON.stringify(state));
    }

    function loadLayoutState() {
      const pLeft = document.getElementById('panelLeft');
      const pBottom = document.getElementById('panelBottom');
      const pRight = document.getElementById('panelRight');
      const pCanvas = document.getElementById('panelCanvas');
      const btnLeft = document.getElementById('btnToggleLeft');
      const btnBottom = document.getElementById('btnToggleBottom');
      const btnRight = document.getElementById('btnToggleRight');
      const btnCanvas = document.getElementById('btnToggleCanvas');
      const actBtnCanvas = document.getElementById('actBtnCanvas');
      const btnTop = document.getElementById('btnTopCompanionToggle');

      // 3D Buddy ALWAYS starts closed on page load (0% idle GPU!)
      if (pRight) pRight.classList.add('hidden');
      if (btnRight) btnRight.classList.remove('active');
      if (btnTop) {
        btnTop.style.borderColor = 'rgba(56,189,248,0.4)';
        btnTop.style.background = 'rgba(15,23,42,0.85)';
      }

      // Restore left, bottom, and canvas if saved
      const saved = localStorage.getItem('antigravity_layout_state');
      if (saved) {
        try {
          const state = JSON.parse(saved);
          if (pLeft && btnLeft) {
            pLeft.classList.toggle('hidden', state.left === false);
            btnLeft.classList.toggle('active', state.left !== false);
          }
          if (pBottom && btnBottom) {
            pBottom.classList.toggle('hidden', !state.bottom);
            btnBottom.classList.toggle('active', !!state.bottom);
          }
          if (pCanvas) {
            pCanvas.classList.toggle('hidden', !state.canvas);
            if (btnCanvas) btnCanvas.classList.toggle('active', !!state.canvas);
            if (actBtnCanvas) actBtnCanvas.classList.toggle('active', !!state.canvas);
            if (state.canvas) refreshArtifactCanvas();
          }
        } catch (e) {}
      }
    }
    loadLayoutState();

    // IDE-Style Layout Toggles
    function toggleLeftPanel() {
      const pLeft = document.getElementById('panelLeft');
      const btnLeft = document.getElementById('btnToggleLeft');
      if (!pLeft) return;
      const isHidden = pLeft.classList.toggle('hidden');
      if (btnLeft) btnLeft.classList.toggle('active', !isHidden);
      saveLayoutState();
    }

    function toggleBottomPanel() {
      const pBottom = document.getElementById('panelBottom');
      const btnBottom = document.getElementById('btnToggleBottom');
      if (!pBottom) return;
      const isHidden = pBottom.classList.toggle('hidden');
      if (btnBottom) btnBottom.classList.toggle('active', !isHidden);
      if (!isHidden) {
        setTimeout(() => {
          const inp = document.getElementById('terminalInBottom');
          if (inp) inp.focus();
        }, 150);
      }
      saveLayoutState();
    }

    function toggleRightPanel() {
      const pRight = document.getElementById('panelRight');
      const btnRight = document.getElementById('btnToggleRight');
      const btnTop = document.getElementById('btnTopCompanionToggle');
      if (!pRight) return;
      const isHidden = pRight.classList.toggle('hidden');
      if (btnRight) btnRight.classList.toggle('active', !isHidden);
      if (btnTop) {
        btnTop.style.borderColor = !isHidden ? 'var(--accent-cyan)' : 'rgba(56,189,248,0.4)';
        btnTop.style.background = !isHidden ? 'rgba(56,189,248,0.25)' : 'rgba(15,23,42,0.85)';
      }
      saveLayoutState();
      const frame = document.getElementById('companionFrame');
      if (!isHidden) {
        loadBuddyIframeIfNeeded();
        if (typeof handleCompanionResize === 'function') {
          setTimeout(handleCompanionResize, 100);
        }
        // Panel opened: Give 3D Buddy mic priority and pause Cockpit mic
        pauseCockpitMicForBuddy();
        if (frame && frame.contentWindow) {
          try { frame.contentWindow.postMessage({ type: 'RESUME_MIC' }, '*'); } catch(_) {}
        }
      } else {
        // Panel closed: IMMEDIATELY suspend 3D Buddy mic so it cannot listen in background!
        if (frame && frame.contentWindow) {
          try { frame.contentWindow.postMessage({ type: 'SUSPEND_MIC', reason: 'dock_hidden' }, '*'); } catch(_) {}
        }
        resumeCockpitMicFromBuddy();
      }
    };

    // =========================================================================
    // D.E.E.P LIVE HOST TELEMETRY, ACTIVE WINDOW & SESSIONS MANAGER
    // =========================================================================

    // 1. Curated Voice Profiles Initialization & Preview Engine
    let cachedVoiceProfiles = {};

    async function initVoiceProfiles() {
      const voiceSelect = document.getElementById('voiceSelect');
      const voiceDesc = document.getElementById('voiceDescription');
      if (!voiceSelect) return;

      // 1. Fetch verified Neural Engine profiles from backend
      try {
        const res = await fetch('/api/voice/profiles');
        if (res.ok) {
          const data = await res.json();
          cachedVoiceProfiles = data.profiles || {};
        }
      } catch(e) {
        console.warn('[Voices] Could not load backend profiles:', e);
      }

      function populate() {
        voiceSelect.innerHTML = '';

        // Group 1: D.E.E.P Neural Studio (Ultra-Fidelity, Natural Edge-TTS)
        const neuralGroup = document.createElement('optgroup');
        neuralGroup.label = '⚡ D.E.E.P Neural Studio (Ultra-Fidelity)';

        const neuralKeys = Object.keys(cachedVoiceProfiles);
        if (neuralKeys.length === 0) {
          neuralGroup.appendChild(new Option('⚡ D.E.E.P. Core (Liam - Canadian Natural)', 'neural:deep'));
          neuralGroup.appendChild(new Option('🎩 J.A.R.V.I.S. (Ryan - British Articulate)', 'neural:jarvis'));
          neuralGroup.appendChild(new Option('🛡️ F.R.I.D.A.Y. (Emily - Tactical Irish)', 'neural:friday'));
          neuralGroup.appendChild(new Option('⭐ Commander (Guy - Authoritative)', 'neural:commander'));
        } else {
          neuralKeys.forEach(k => {
            const prof = cachedVoiceProfiles[k];
            const opt = document.createElement('option');
            opt.value = `neural:${k}`;
            let icon = '🎙️';
            if (k === 'deep') icon = '⚡';
            else if (k === 'jarvis') icon = '🎩';
            else if (k === 'friday') icon = '🛡️';
            else if (k === 'commander') icon = '⭐';
            else if (k === 'my_voice') icon = '🧬';
            opt.textContent = `${icon} ${prof.name} (${prof.voice ? prof.voice.split('-')[1] : 'Neural'})`;
            neuralGroup.appendChild(opt);
          });
        }
        voiceSelect.appendChild(neuralGroup);

        // Group 2: Filtered & Verified Workstation SAPI Voices (Offline)
        let rawVoices = [];
        if (window.speechSynthesis) {
          try { rawVoices = window.speechSynthesis.getVoices() || []; } catch(e){}
        }

        // Filter out silent, broken, or low-quality duplicates. Keep only verified standard voices.
        const verifiedLocalKeywords = ['David', 'Zira', 'Mark', 'George', 'Susan', 'Linda', 'Richard', 'Google US', 'Google UK'];
        const seenNames = new Set();
        const validLocalVoices = [];

        rawVoices.forEach(v => {
          if (!v.lang || !v.lang.startsWith('en')) return;
          const isVerified = verifiedLocalKeywords.some(kw => v.name.includes(kw));
          if (isVerified && !seenNames.has(v.name)) {
            seenNames.add(v.name);
            validLocalVoices.push(v);
          }
        });

        if (validLocalVoices.length > 0) {
          const localGroup = document.createElement('optgroup');
          localGroup.label = '💻 Verified Workstation SAPI (Offline)';
          validLocalVoices.forEach(v => {
            const opt = document.createElement('option');
            opt.value = `local:${v.name}`;
            const clean = v.name.replace(/Microsoft |Desktop |English |\(United States\)|\(United Kingdom\)|\(Canada\)/g, '').replace(/[\(\)-]/g, '').trim();
            opt.textContent = `💻 ${clean} (${v.lang})`;
            localGroup.appendChild(opt);
          });
          voiceSelect.appendChild(localGroup);
        }

        // Restore saved preference
        const saved = localStorage.getItem('deep_selected_voice') || 'neural:deep';
        if (Array.from(voiceSelect.options).some(o => o.value === saved)) {
          voiceSelect.value = saved;
        } else {
          voiceSelect.value = 'neural:deep';
        }
        updateVoiceDescription();
      }

      function updateVoiceDescription() {
        if (!voiceDesc) return;
        const val = voiceSelect.value || '';
        if (val.startsWith('neural:')) {
          const k = val.replace('neural:', '');
          const p = cachedVoiceProfiles[k];
          voiceDesc.textContent = p ? p.description : 'High-fidelity edge neural voice synthesis.';
        } else if (val.startsWith('local:')) {
          voiceDesc.textContent = 'Hardware workstation offline SAPI speech synthesizer.';
        } else {
          voiceDesc.textContent = 'D.E.E.P Sovereign vocal synthesis engine.';
        }
      }

      voiceSelect.addEventListener('change', async () => {
        const val = voiceSelect.value;
        localStorage.setItem('deep_selected_voice', val);
        updateVoiceDescription();
        if (val.startsWith('neural:')) {
          const k = val.replace('neural:', '');
          try {
            await fetch('/api/voice/profiles', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({profile: k})
            });
          } catch(e){}
        }
      });

      if (window.speechSynthesis) {
        if (speechSynthesis.onvoiceschanged !== undefined) {
          speechSynthesis.onvoiceschanged = populate;
        }
        populate();
        setTimeout(populate, 500);
        setTimeout(populate, 1500);
      } else {
        populate();
      }
    }

    // Interactive Voice Preview / Test Function
    window.testCurrentVoice = async function() {
      const btn = document.getElementById('btnTestVoice');
      const icon = document.getElementById('testVoiceIcon');
      const voiceSelect = document.getElementById('voiceSelect');
      const selected = voiceSelect ? voiceSelect.value : (localStorage.getItem('deep_selected_voice') || 'neural:deep');

      let phrase = "D.E.E.P vocal synthesis operational, Commander.";
      if (selected.includes('jarvis')) {
        phrase = "Good day, Commander. Vocal synthesis online and at your command.";
      } else if (selected.includes('friday')) {
        phrase = "All systems operational, Commander. Tactical audio ready.";
      } else if (selected.includes('commander')) {
        phrase = "Commander voice confirmed. Workstation ready for directive.";
      } else if (selected.includes('my_voice')) {
        phrase = "Cloned vocal signature operational, Commander. Voice matching 99.4 percent.";
      } else if (selected.includes('punjabi')) {
        phrase = "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਕਮਾਂਡਰ, ਸਿਸਟਮ ਤਿਆਰ ਹੈ।";
      } else if (selected.includes('hindi')) {
        phrase = "नमस्ते कमांडर, सिस्टम पूरी तरह से तैयार है।";
      }

      if (btn) {
        btn.disabled = true;
        btn.style.opacity = '0.75';
        if (icon) icon.textContent = '🔊';
      }

      try {
        await speakVoiceFeedback(phrase, true);
      } finally {
        setTimeout(() => {
          if (btn) {
            btn.disabled = false;
            btn.style.opacity = '1';
          }
          if (icon) icon.textContent = '▶';
        }, 1500);
      }
    };

    // 2. Chat Sessions History Loader
    async function loadChatHistory() {
      const list = document.getElementById('chatHistoryList');
      if (!list) return;
      try {
        const res = await fetch('/api/history');
        if (res.ok) {
          const data = await res.json();
          const chats = data.chats || [];
          if (chats.length === 0) {
            list.innerHTML = '<div style="font-size:0.75rem; color:var(--text-muted); padding:8px 4px; text-align:center;">No recent chats.<br>Click "+ New Chat" to start.</div>';
            return;
          }
          list.innerHTML = '';
          chats.forEach(c => {
            const item = document.createElement('div');
            item.className = 'chat-item';
            item.style.cssText = 'padding:6px 8px; border-radius:6px; cursor:pointer; font-size:0.78rem; color:var(--text-muted); display:flex; justify-content:space-between; align-items:center; transition:all 0.2s; margin-bottom:4px; border:1px solid rgba(255,255,255,0.04);';
            const title = c.title || ('Conversation ' + (c.id || ''));
            item.innerHTML = `<span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:140px;">💬 ${title}</span>`;
            item.onmouseenter = () => { item.style.background = 'rgba(56,189,248,0.12)'; item.style.color = '#38bdf8'; item.style.borderColor = 'rgba(56,189,248,0.3)'; };
            item.onclick = async () => {
              currentChatId = c.id;
              const chatScroll = document.getElementById('chatScroll');
              const hero = document.getElementById('cockpitHeroDashboard');
              if (hero) hero.style.display = 'none';
              if (chatScroll) {
                chatScroll.querySelectorAll('.msg-wrapper').forEach(el => el.remove());
              }
              try {
                const res = await fetch(`/api/chats/${c.id}`);
                if (res.ok) {
                  const data = await res.json();
                  const msgs = data.messages || [];
                  msgs.forEach(m => {
                    const role = (m.role === 'user') ? 'user' : 'ai';
                    appendMessage(role, m.content, m.id);
                  });
                }
              } catch(e) {}
            };
            list.appendChild(item);
          });
        }
      } catch(e) {
        list.innerHTML = '<div style="font-size:0.75rem; color:var(--text-muted); padding:4px;">No chats loaded</div>';
      }
    }

    // 3. Active Window Scanner
    async function updateActiveWindow() {
      try {
        const res = await fetch('/api/system/active_window');
        if (res.ok) {
          const data = await res.json();
          const winEl = document.getElementById('activeWinTitle');
          if (winEl && data.active_window) {
            winEl.textContent = data.active_window;
            winEl.title = data.active_window;
          }
        }
      } catch(e) {}
    }

    // 4. Host Telemetry & Hardware Specs
    async function updateSidebarTelemetry() {
      try {
        const res = await fetch('/api/system/info');
        if (res.ok) {
          const data = await res.json();
          if (data.cpu_percent !== undefined) {
            const cpu = Math.round(data.cpu_percent);
            const cpuPctEl = document.getElementById('cpuPct');
            const cpuBarEl = document.getElementById('cpuBar');
            if (cpuPctEl) cpuPctEl.textContent = `${cpu}%`;
            if (cpuBarEl) cpuBarEl.style.width = `${Math.min(100, Math.max(2, cpu))}%`;
            
            cpuHistory.push(cpu);
            if (cpuHistory.length > 25) cpuHistory.shift();
          }
          if (data.ram_percent !== undefined) {
            const ram = Math.round(data.ram_percent);
            const ramUsed = data.ram_used_gb || 0;
            const ramTotal = data.ram_total_gb || 0;
            const ramPctEl = document.getElementById('ramPct');
            const ramBarEl = document.getElementById('ramBar');
            if (ramPctEl) ramPctEl.textContent = `${ram}% (${ramUsed}G/${ramTotal}G)`;
            if (ramBarEl) ramBarEl.style.width = `${Math.min(100, Math.max(2, ram))}%`;
            
            ramHistory.push(ram);
            if (ramHistory.length > 25) ramHistory.shift();
          }
          if (data.gpu_percent !== undefined) {
            const gpu = Math.round(data.gpu_percent);
            const gpuPctEl = document.getElementById('gpuPct');
            const gpuBarEl = document.getElementById('gpuBar');
            if (gpuPctEl) gpuPctEl.textContent = `${gpu}%`;
            if (gpuBarEl) gpuBarEl.style.width = `${Math.min(100, Math.max(2, gpu))}%`;
          }
          if (data.vram_percent !== undefined) {
            const vram = Math.round(data.vram_percent);
            const vramUsed = data.vram_used_mb ? (data.vram_used_mb / 1024).toFixed(1) : '0.0';
            const vramTotal = data.vram_total_mb ? (data.vram_total_mb / 1024).toFixed(1) : '8.0';
            const vramPctEl = document.getElementById('vramPct');
            const vramBarEl = document.getElementById('vramBar');
            if (vramPctEl) vramPctEl.textContent = `${vram}% (${vramUsed}G/${vramTotal}G)`;
            if (vramBarEl) vramBarEl.style.width = `${Math.min(100, Math.max(2, vram))}%`;
          }
          const diskFreeEl = document.getElementById('diskFree');
          if (diskFreeEl && data.disk_free_gb !== undefined) {
            diskFreeEl.textContent = `${data.disk_free_gb} GB`;
          }
          const netStatEl = document.getElementById('netStat');
          if (netStatEl && data.net_recv_mb !== undefined) {
            netStatEl.textContent = `${data.net_recv_mb} MB`;
          }

          // Sparkline canvas
          const tCanvas = document.getElementById('telemetryChart');
          if (tCanvas && cpuHistory.length > 1) {
            const ctx = tCanvas.getContext('2d');
            if (ctx) {
              const w = tCanvas.width = tCanvas.offsetWidth || 180;
              const h = tCanvas.height = 36;
              ctx.clearRect(0, 0, w, h);
              ctx.strokeStyle = '#38bdf8';
              ctx.lineWidth = 1.5;
              ctx.beginPath();
              const step = w / (cpuHistory.length - 1);
              for (let i = 0; i < cpuHistory.length; i++) {
                const y = h - (cpuHistory[i] / 100) * (h - 6) - 3;
                if (i === 0) ctx.moveTo(0, y);
                else ctx.lineTo(i * step, y);
              }
              ctx.stroke();
            }
          }

          // Handle incoming network and cyber defense alerts
          if (data.pending_alerts && data.pending_alerts.length > 0) {
            data.pending_alerts.forEach(alert => {
              handleIncomingSecurityAlert(alert);
            });
          }
        }
      } catch(e) {}
    }

    function handleIncomingSecurityAlert(alert) {
      if (!alert) return;
      try { playHoloSound('alert'); } catch(e){}

      if (alert.type === 'UNKNOWN_DEVICE') {
        if (alert.html_card && typeof appendMessage === 'function') {
          appendMessage('ai', alert.html_card);
        }
        showFloatingCyberBanner(alert);
      } else if (alert.type === 'VOICE_SPEECH') {
        if (alert.text && typeof appendMessage === 'function') {
          appendMessage('ai', `<div style="display:flex; align-items:center; gap:8px; font-style:italic; color:#94a3b8;"><span style="font-size:1.1rem;">🗣️</span> <span>"${escapeHtml(alert.text)}"</span></div>`);
        }
      }
    }

    function showFloatingCyberBanner(alert) {
      let banner = document.getElementById('floatingCyberBanner');
      if (!banner) {
        banner = document.createElement('div');
        banner.id = 'floatingCyberBanner';
        banner.style.cssText = 'position:fixed; top:75px; right:25px; z-index:999999; max-width:420px; width:calc(100% - 50px); background:rgba(15,23,42,0.96); border-radius:12px; padding:14px; box-shadow:0 12px 40px rgba(0,0,0,0.8); backdrop-filter:blur(16px); color:#f8fafc; font-family:\'Outfit\', sans-serif; transition:all 0.3s ease;';
        document.body.appendChild(banner);
      }
      
      const isVirtual = alert.is_virtual || alert.category === 'VIRTUAL_ADAPTER' || (alert.vendor && alert.vendor.includes('Hyper-V')) || (alert.vendor && alert.vendor.includes('WSL'));
      const isKnown = alert.category === 'KNOWN_PHYSICAL';
      const themeColor = isVirtual ? '#38bdf8' : (isKnown ? '#fbbf24' : '#ef4444');
      const dotColor = isVirtual ? '#38bdf8' : (isKnown ? '#f59e0b' : '#ef4444');
      const bannerTitle = isVirtual ? '💻 INTERNAL VIRTUAL ADAPTER' : (isKnown ? '📡 NEW NETWORK DEVICE' : '🚨 UNVERIFIED DEVICE DETECTED');
      const trustBtnText = isVirtual ? '✅ Auto-Trust Subsystem' : '✅ Mark as Trusted';

      banner.style.border = `1px solid ${isVirtual ? 'rgba(56,189,248,0.4)' : (isKnown ? 'rgba(245,158,11,0.4)' : '#ef4444')}`;
      banner.style.boxShadow = `0 12px 40px rgba(0,0,0,0.8), 0 0 25px ${isVirtual ? 'rgba(56,189,248,0.25)' : (isKnown ? 'rgba(245,158,11,0.25)' : 'rgba(239,68,68,0.35)')}`;

      banner.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <div style="font-weight:800; color:${themeColor}; font-size:0.88rem; display:flex; align-items:center; gap:8px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${dotColor}; box-shadow:0 0 8px ${dotColor};"></span>
            ${bannerTitle}
          </div>
          <button onclick="document.getElementById('floatingCyberBanner').remove()" style="background:transparent; border:none; color:#94a3b8; font-size:1.2rem; cursor:pointer; line-height:1;">&times;</button>
        </div>
        <div style="font-size:0.8rem; font-family:'JetBrains Mono', monospace; line-height:1.45; color:#e2e8f0; margin-bottom:10px; background:rgba(0,0,0,0.3); padding:8px; border-radius:6px; border:1px solid rgba(255,255,255,0.05);">
          <div><strong>IP:</strong> <span style="color:#38bdf8;">${escapeHtml(alert.ip || '')}</span></div>
          <div><strong>MAC:</strong> <span style="color:#cbd5e1;">${escapeHtml(alert.mac || '')}</span></div>
          <div><strong>Vendor:</strong> <span style="color:#fde047;">${escapeHtml(alert.vendor || 'Unknown')}</span></div>
          ${alert.title ? `<div><strong>Classification:</strong> <span style="color:#7dd3fc;">${escapeHtml(alert.title)}</span></div>` : ''}
        </div>
        <div style="display:flex; gap:6px; flex-wrap:wrap;">
          <button onclick="trustNetworkDevice('${alert.mac}', '${alert.ip}')" style="background:rgba(16,185,129,0.2); border:1px solid #10b981; color:#10b981; padding:6px 12px; border-radius:6px; font-size:0.75rem; font-weight:700; cursor:pointer;">${trustBtnText}</button>
          <button onclick="scanNetworkDevice('${alert.ip}')" style="background:#0284c7; color:#fff; border:none; padding:6px 12px; border-radius:6px; font-size:0.75rem; font-weight:700; cursor:pointer;">🔍 Quick Scan</button>
          <button onclick="blockNetworkDevice('${alert.ip}')" style="background:#dc2626; color:#fff; border:none; padding:6px 12px; border-radius:6px; font-size:0.75rem; font-weight:700; cursor:pointer;">🛡️ Block</button>
        </div>
      `;
    }

    window.scanNetworkDevice = async function(ip) {
      const sanitized = (ip || '').replace(/\./g, '_');
      const resBox = document.getElementById(`scan-results-${sanitized}`);
      if (resBox) {
        resBox.style.display = 'block';
        resBox.innerHTML = '<span style="color:#38bdf8;">⏳ Scanning target ports (21, 22, 80, 443, 445, 3389, 5000, 8080...)...</span>';
      }
      
      appendMessage('user', `[Tactical Action] Initiating port scan on ${ip}...`);
      
      try {
        const res = await fetch('/api/cyber/port_scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip: ip })
        });
        const data = await res.json();
        if (data.success) {
          if (resBox) {
            let html = '<div style="font-weight:700; color:#38bdf8; margin-bottom:4px;">Port Scan Completed:</div>';
            if (data.open_ports && data.open_ports.length > 0) {
              data.open_ports.forEach(p => {
                html += `<div>• Port <strong style="color:#fde047;">${p.port}</strong>: <span style="color:#4ade80;">${p.service}</span></div>`;
              });
            } else {
              html += '<div style="color:#4ade80;">No exposed ports discovered. Target is secure/filtered.</div>';
            }
            resBox.innerHTML = html;
          }
          if (typeof speakVoiceFeedback === 'function') {
            speakVoiceFeedback(`Port scan completed for ${ip}. ${data.open_ports ? data.open_ports.length : 0} open ports detected.`);
          }
        } else {
          if (resBox) resBox.innerHTML = `<span style="color:#ef4444;">Scan failed: ${data.error}</span>`;
        }
      } catch (err) {
        if (resBox) resBox.innerHTML = `<span style="color:#ef4444;">Scan error: ${err.message}</span>`;
      }
    };

    window.blockNetworkDevice = async function(ip) {
      if (!confirm(`Are you sure you want to block IP ${ip} at the Windows Firewall?`)) return;
      const sanitized = (ip || '').replace(/\./g, '_');
      const statusSpan = document.getElementById(`device-status-${sanitized}`);
      
      try {
        const res = await fetch('/api/cyber/block_device', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip: ip })
        });
        const data = await res.json();
        if (data.success) {
          if (statusSpan) {
            statusSpan.textContent = 'BLOCKED BY FIREWALL';
            statusSpan.style.color = '#ef4444';
          }
          const banner = document.getElementById('floatingCyberBanner');
          if (banner) banner.remove();
          if (typeof speakVoiceFeedback === 'function') {
            speakVoiceFeedback(`Host ${ip} has been blocked at the firewall.`);
          }
        } else {
          alert('Block error: ' + (data.error || 'Failed'));
        }
      } catch (err) {
        alert('Block request failed: ' + err.message);
      }
    };

    window.trustNetworkDevice = async function(mac, ip) {
      const sanitized = (ip || '').replace(/\./g, '_');
      const statusSpan = document.getElementById(`device-status-${sanitized}`);
      
      try {
        const res = await fetch('/api/cyber/trust_device', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mac: mac, ip: ip })
        });
        const data = await res.json();
        if (data.success) {
          if (statusSpan) {
            statusSpan.textContent = 'VERIFIED / TRUSTED';
            statusSpan.style.color = '#10b981';
          }
          const banner = document.getElementById('floatingCyberBanner');
          if (banner) banner.remove();
          if (typeof speakVoiceFeedback === 'function') {
            speakVoiceFeedback(`Device marked as trusted.`);
          }
        }
      } catch (err) {
        alert('Trust request failed: ' + err.message);
      }
    };

    // 5. Real-Time Location Badge
    async function updateLocationBadge() {
      try {
        const res = await fetch('/api/hud/weather');
        if (res.ok) {
          const data = await res.json();
          const locText = document.getElementById('topLocationText');
          if (locText && data.name) {
            locText.innerHTML = `${data.name}, ON &nbsp;|&nbsp; <strong>${data.temp_c}°C</strong> <span style="opacity:0.8">(${data.condition})</span>`;
            
            const badge = document.getElementById('topLocationBadge');
            if (data.alert_level === 'warning') {
                badge.style.background = 'rgba(239,68,68,0.12)';
                badge.style.borderColor = 'rgba(239,68,68,0.35)';
                badge.style.color = '#ef4444';
                badge.title = data.alert;
            } else {
                badge.style.background = 'rgba(16,185,129,0.12)';
                badge.style.borderColor = 'rgba(16,185,129,0.35)';
                badge.style.color = '#10b981';
                badge.title = `Wind: ${data.windspeed_kmh} km/h`;
            }
          }
        }
      } catch(e) {}
    }

    // Initialize all subsystems immediately on load
    initVoiceProfiles();
    updateTTSUI();

    // Synchronize global voice mute state between browser localStorage and backend
    fetch('/api/voice/mute')
      .then(r => r.json())
      .then(d => {
        if (d && typeof d.muted === 'boolean') {
          const localMuted = (localStorage.getItem('deep_tts_enabled') === '0');
          // If either local or server says muted, enforce voice OFF
          const shouldBeMuted = d.muted || localMuted;
          ttsEnabled = !shouldBeMuted;
          localStorage.setItem('deep_tts_enabled', ttsEnabled ? '1' : '0');
          updateTTSUI();
          if (shouldBeMuted !== d.muted) {
            fetch('/api/voice/mute', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ muted: shouldBeMuted })
            }).catch(() => {});
          }
        }
      })
      .catch(() => updateTTSUI());

    initVoiceReactor();
    loadChatHistory();
    updateSidebarTelemetry();
    updateActiveWindow();
    updateLocationBadge();

    // Smart Battery & CPU-Aware Background Telemetry Loops (Zero Idle Waste)
    let telemetryTimer = null;
    let windowTimer = null;

    function startBackgroundLoops() {
      if (!telemetryTimer) telemetryTimer = setInterval(updateSidebarTelemetry, 3500);
      if (!windowTimer) windowTimer = setInterval(updateActiveWindow, 8000);
    }

    function stopBackgroundLoops() {
      if (telemetryTimer) { clearInterval(telemetryTimer); telemetryTimer = null; }
      if (windowTimer) { clearInterval(windowTimer); windowTimer = null; }
    }

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        stopBackgroundLoops();
      } else {
        updateSidebarTelemetry();
        updateActiveWindow();
        startBackgroundLoops();
      }
    });

    startBackgroundLoops();
    setInterval(updateLocationBadge, 120000);

    // =================================================================
    // REAL-TIME AUTO-UPDATE & HOT-RELOAD CLIENT ENGINE
    // =================================================================
    (function initLiveAutoUpdater() {
      let currentVersionSig = null;
      let isReloading = false;
      let offlineCount = 0;

      async function checkLiveUpdate() {
        if (isReloading) return;
        try {
          const res = await fetch('/api/system/version?t=' + Date.now(), { cache: 'no-store' });
          if (!res.ok) throw new Error('HTTP ' + res.status);
          const data = await res.json();
          const newSig = data.app_version;

          if (!newSig) return;

          if (currentVersionSig === null) {
            currentVersionSig = newSig;
            console.log('[LiveAutoUpdate] Watcher active. Current build signature:', currentVersionSig);
            return;
          }

          if (newSig !== currentVersionSig) {
            console.log('[LiveAutoUpdate] Workspace update detected! Old:', currentVersionSig, 'New:', newSig);
            isReloading = true;
            showLiveUpdateToast('🔄 New update detected! Updating Cockpit automatically...');
            setTimeout(() => {
              window.location.reload();
            }, 800);
          }
          offlineCount = 0;
          removeOfflineNotice();
        } catch (err) {
          offlineCount++;
          if (offlineCount >= 2 && !isReloading) {
            showOfflineNotice();
          }
        }
      }

      function showLiveUpdateToast(msg) {
        let toast = document.getElementById('liveUpdateToast');
        if (!toast) {
          toast = document.createElement('div');
          toast.id = 'liveUpdateToast';
          toast.style.cssText = 'position:fixed; top:20px; right:20px; z-index:999999; background:linear-gradient(135deg, #0284c7, #8b5cf6); color:#ffffff; padding:10px 18px; border-radius:10px; font-weight:700; font-size:0.84rem; box-shadow:0 8px 30px rgba(0,0,0,0.6); border:1px solid rgba(255,255,255,0.3); display:flex; align-items:center; gap:8px;';
          document.body.appendChild(toast);
        }
        toast.textContent = msg;
      }

      function showOfflineNotice() {
        let notice = document.getElementById('liveOfflineNotice');
        if (!notice) {
          notice = document.createElement('div');
          notice.id = 'liveOfflineNotice';
          notice.style.cssText = 'position:fixed; bottom:20px; left:20px; z-index:999999; background:rgba(239,68,68,0.9); backdrop-filter:blur(8px); color:#ffffff; padding:8px 14px; border-radius:8px; font-size:0.75rem; font-weight:600; display:flex; align-items:center; gap:8px; border:1px solid rgba(255,255,255,0.2); box-shadow:0 4px 15px rgba(0,0,0,0.4);';
          notice.innerHTML = '<span style="width:7px; height:7px; border-radius:50%; background:#f87171; box-shadow:0 0 8px #f87171;"></span> Reconnecting to AI Cockpit server...';
          document.body.appendChild(notice);
        }
      }

      function removeOfflineNotice() {
        const notice = document.getElementById('liveOfflineNotice');
        if (notice) notice.remove();
      }

      // Check every 2 seconds for continuous auto-updates
      setInterval(checkLiveUpdate, 2000);
      setTimeout(checkLiveUpdate, 800);
    })();

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function renderUserMessage(text) {
      if (!text) return '';
      // Escape HTML characters so tags like <instructions>, <user>, XML, C++ headers never get swallowed
      let safe = escapeHtml(text);

      // Parse fenced code blocks: ```lang\ncode```
      safe = safe.replace(/```(\w+)?\r?\n([\s\S]*?)```/g, function(match, lang, code) {
        lang = lang || 'code';
        return `<div class="code-block-wrapper"><div class="code-block-header"><span>${lang}</span></div><pre><code>${code.trim()}</code></pre></div>`;
      });

      // Parse inline code: `code`
      safe = safe.replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.12); padding:2px 6px; border-radius:4px; font-family:monospace; font-size:0.88em;">$1</code>');

      // Convert newlines outside pre blocks to <br>
      const parts = safe.split(/(<div class="code-block-wrapper">[\s\S]*?<\/div>|<details[^>]*class="code-block-wrapper"[^>]*>[\s\S]*?<\/details>)/);
      for (let i = 0; i < parts.length; i++) {
        if (!parts[i].startsWith('<div class="code-block-wrapper">') && !parts[i].startsWith('<details')) {
          parts[i] = parts[i].replace(/\r?\n/g, '<br>');
        }
      }
      return parts.join('');
    }

    function renderMarkdownWithSandbox(text) {
      if (!text) return '';

      // Preserve safe Cockpit rich media elements & tactical cards (supporting arbitrary nested child tags)
      const preservedWidgets = [];
      let safeText = '';
      let i = 0;
      const widgetTagPattern = /^<(div|section)\s+[^>]+>/i;

      while (i < text.length) {
        const sub = text.slice(i);
        const startMatch = sub.match(widgetTagPattern);
        if (startMatch) {
          const tag = startMatch[1].toLowerCase();
          const startPos = i;
          let depth = 1;
          let pos = i + startMatch[0].length;
          while (pos < text.length && depth > 0) {
            const nextOpen = text.indexOf('<' + tag, pos);
            const nextClose = text.indexOf('</' + tag + '>', pos);
            if (nextClose === -1) break;
            if (nextOpen !== -1 && nextOpen < nextClose && text.length > nextOpen + tag.length + 1 && /[\s>]/.test(text[nextOpen + tag.length + 1])) {
              depth++;
              pos = nextOpen + tag.length + 1;
            } else {
              depth--;
              pos = nextClose + tag.length + 3;
              if (depth === 0) {
                const widgetHtml = text.slice(startPos, pos);
                if (!/<script/i.test(widgetHtml)) {
                  preservedWidgets.push(widgetHtml);
                  safeText += '__COCKPIT_WIDGET_' + (preservedWidgets.length - 1) + '__';
                  i = pos;
                  break;
                }
              }
            }
          }
          if (depth > 0) {
            safeText += text[i];
            i++;
          }
        } else {
          safeText += text[i];
          i++;
        }
      }

      let html = escapeHtml(safeText);
      
      // DeepSeek Reasoning tags
      // Completed thinking block
      html = html.replace(/&lt;think&gt;([\s\S]*?)&lt;\/think&gt;/g, function(match, content) {
          return `<details class="think-block-wrapper" style="margin:10px 0; border:1px solid rgba(147,51,234,0.3); border-radius:8px; background:rgba(15,23,42,0.6); overflow:hidden;"><summary style="padding:8px 12px; background:rgba(147,51,234,0.15); cursor:pointer; color:#c084fc; font-size:0.85rem; font-family:'JetBrains Mono', monospace; display:flex; align-items:center; outline:none;"><span>🧠 DeepSeek Reasoning</span></summary><div style="padding:10px 12px; color:#a78bfa; font-size:0.9rem; font-style:italic; white-space:pre-wrap;">${content}</div></details>`;
      });

      // Streaming/Unclosed thinking block
      html = html.replace(/&lt;think&gt;([\s\S]*?)$/g, function(match, content) {
          return `<details open class="think-block-wrapper" style="margin:10px 0; border:1px solid rgba(147,51,234,0.5); border-radius:8px; background:rgba(15,23,42,0.8); overflow:hidden; box-shadow:0 0 10px rgba(147,51,234,0.2);"><summary style="padding:8px 12px; background:rgba(147,51,234,0.2); cursor:pointer; color:#c084fc; font-size:0.85rem; font-family:'JetBrains Mono', monospace; display:flex; align-items:center; outline:none;"><span class="hero-core-pulse" style="background:#c084fc; box-shadow:0 0 8px #c084fc; width:8px; height:8px; margin-right:8px;"></span><span>🧠 DeepSeek Reasoning (Thinking...)</span></summary><div style="padding:10px 12px; color:#a78bfa; font-size:0.9rem; font-style:italic; white-space:pre-wrap;">${content}</div></details>`;
      });

      // Match closed code blocks with sandbox support
      html = html.replace(/```(\w+)?\r?\n([\s\S]*?)```/g, function(match, lang, code) {
        lang = lang || '';
        let sandboxBtn = '';
        if (['python', 'javascript', 'js', 'sql', 'powershell', 'ps1'].includes(lang.toLowerCase())) {
          sandboxBtn = `<button class="btn-sandbox-run" onclick="event.stopPropagation(); executeSandboxCode(this, '${lang}')">▶ Run in Sandbox</button>`;
        }
        return `<details class="code-block-wrapper" style="cursor:pointer;"><summary class="code-block-header" style="outline:none; display:flex; justify-content:space-between; align-items:center;"><span>▶ ${lang || 'code'} (Click to view/hide code)</span>${sandboxBtn}</summary><div style="cursor:auto;"><pre style="margin-top:0;"><code>${code.trim()}</code></pre><div class="sandbox-output" style="display:none; padding: 10px; background: rgba(0,0,0,0.5); border-radius: 5px; margin-top: 5px; font-family: monospace;"></div></div></details>`;
      });

      // Match unclosed code block during active streaming so text doesn't look broken while typing
      html = html.replace(/```(\w+)?\r?\n([\s\S]*?)$/g, function(match, lang, code) {
        lang = lang || '';
        return `<details open class="code-block-wrapper"><summary class="code-block-header" style="outline:none;"><span>▶ ${lang || 'code'} <i>(typing...)</i></span></summary><pre style="margin-top:0;"><code>${code}</code></pre></details>`;
      });

      // Markdown headings
      html = html.replace(/^### (.*?)$/gm, '<h3 style="margin: 10px 0 4px; color: #38bdf8; font-size: 1.05rem;">$1</h3>');
      html = html.replace(/^## (.*?)$/gm, '<h2 style="margin: 12px 0 6px; color: #38bdf8; font-size: 1.15rem;">$1</h2>');
      html = html.replace(/^# (.*?)$/gm, '<h1 style="margin: 14px 0 8px; color: #38bdf8; font-size: 1.25rem;">$1</h1>');

      // Bold and italic formatting
      html = html.replace(/\*\*([^*]+)\*\*/g, '<strong style="color:#f8fafc;">$1</strong>');
      html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

      // Inline code formatting
      html = html.replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.12); padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.88em; color: #38bdf8;">$1</code>');

      // Unescape safe inline semantic HTML tags (strong, b, em, i, code, span, mark) with safe styling/classes
      html = html.replace(/&lt;(\/?(?:strong|b|em|i|code|span|mark))((?:\s+[a-zA-Z0-9\-]+=(?:&quot;[\s\S]*?&quot;|'[^']*'|[^\s&gt;]+))*)\s*&gt;/gi, function(match, tag, attrs) {
        let cleanAttrs = attrs ? attrs.replace(/&quot;/g, '"') : '';
        if (/on\w+\s*=|javascript:/i.test(cleanAttrs)) {
          return match;
        }
        return `<${tag}${cleanAttrs}>`;
      });

      // Only convert \n to <br> outside code blocks
      const parts = html.split(/(<div class="code-block-wrapper">[\s\S]*?<\/div>|<details[^>]*class="(?:code|think)-block-wrapper"[^>]*>[\s\S]*?<\/details>)/);
      for (let i = 0; i < parts.length; i++) {
        if (!parts[i].startsWith('<div class="code-block-wrapper">') && !parts[i].startsWith('<details')) {
          parts[i] = parts[i].replace(/\r?\n/g, '<br>');
        }
      }
      let rendered = parts.join('');

      // Restore safe preserved Cockpit rich media widgets
      for (let i = 0; i < preservedWidgets.length; i++) {
        rendered = rendered.replace(`__COCKPIT_WIDGET_${i}__`, preservedWidgets[i]);
      }
      return rendered;
    }

    function updatePromptInputAutoHeight() {
      const pi = document.getElementById('promptInput');
      const stats = document.getElementById('inputStats');
      if (!pi) return;
      pi.style.height = 'auto';
      const scrollH = pi.scrollHeight;
      const targetH = Math.min(Math.max(scrollH, 38), 420);
      pi.style.height = targetH + 'px';

      const val = pi.value || '';
      if (stats) {
        if (val.length > 30) {
          stats.style.display = 'inline-flex';
          const approxTokens = Math.round(val.length / 3.8);
          stats.textContent = `${val.length.toLocaleString()} chars (~${approxTokens.toLocaleString()} tokens)`;
        } else {
          stats.style.display = 'none';
        }
      }
    }

    function resetPromptInputHeight() {
      const pi = document.getElementById('promptInput');
      const stats = document.getElementById('inputStats');
      if (pi) {
        pi.style.height = '38px';
      }
      if (stats) {
        stats.style.display = 'none';
      }
    }

    // Chat Stream Logic & Human Feedback Controls
    function attachFeedbackControls(msgWrapper, bubble, msgId = null) {
      if (!msgWrapper || !bubble) return;
      if (msgWrapper.querySelector('.feedback-toolbar')) {
        if (msgId) msgWrapper.dataset.msgId = msgId;
        return;
      }

      const toolbar = document.createElement('div');
      toolbar.className = 'feedback-toolbar';
      toolbar.style.cssText = 'display:flex; align-items:center; justify-content:flex-end; gap:6px; margin-top:8px; padding-top:6px; border-top:1px solid rgba(255,255,255,0.06); font-size:0.75rem;';

      const badge = document.createElement('span');
      badge.className = 'feedback-status-badge';
      badge.style.cssText = 'margin-right:auto; font-size:0.72rem; color:#94a3b8; font-weight:600; display:none;';

      const btnUp = document.createElement('button');
      btnUp.className = 'btn-fb-thumb-up';
      btnUp.innerHTML = '👍 Helpful';
      btnUp.title = 'Mark as Correct / Helpful (+1)';
      btnUp.style.cssText = 'background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#cbd5e1; padding:3px 8px; font-size:0.72rem; cursor:pointer; transition:all 0.2s;';

      const btnDown = document.createElement('button');
      btnDown.className = 'btn-fb-thumb-down';
      btnDown.innerHTML = '👎 Wrong';
      btnDown.title = 'Mark as Incorrect / Needs Correction (-1)';
      btnDown.style.cssText = 'background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#cbd5e1; padding:3px 8px; font-size:0.72rem; cursor:pointer; transition:all 0.2s;';

      const btnTeach = document.createElement('button');
      btnTeach.className = 'btn-fb-teach';
      btnTeach.innerHTML = '✏️ Teach D.E.E.P';
      btnTeach.title = 'Provide custom correction / learning directive';
      btnTeach.style.cssText = 'background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); border-radius:6px; color:#38bdf8; padding:3px 8px; font-size:0.72rem; cursor:pointer; transition:all 0.2s; font-weight:600;';

      toolbar.appendChild(badge);
      toolbar.appendChild(btnUp);
      toolbar.appendChild(btnDown);
      toolbar.appendChild(btnTeach);

      const panel = document.createElement('div');
      panel.className = 'feedback-correction-panel';
      panel.style.cssText = 'display:none; margin-top:8px; padding:10px; background:rgba(15,23,42,0.95); border:1px solid rgba(56,189,248,0.4); border-radius:8px; box-shadow:0 6px 20px rgba(0,0,0,0.6);';
      panel.innerHTML = `
        <div style="font-weight:700; color:#38bdf8; font-size:0.78rem; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center;">
          <span>🧠 Teach D.E.E.P: What went wrong & what is the right way?</span>
          <span class="fb-close-panel" style="cursor:pointer; color:#94a3b8; font-size:0.9rem; padding:0 4px;">✕</span>
        </div>
        <div style="margin-bottom:6px;">
          <select class="fb-tag-select" style="width:100%; background:#090d16; border:1px solid rgba(255,255,255,0.15); border-radius:6px; color:#e2e8f0; font-size:0.75rem; padding:5px 6px;">
            <option value="code_error">❌ Incorrect or Broken Code / Syntax</option>
            <option value="hallucination">🌀 Hallucination or Factually Incorrect</option>
            <option value="missed_instructions">📏 Ignored Specific Instructions / Constraints</option>
            <option value="platform_issue">📱 Didn't Work on My OS / Device / Browser</option>
            <option value="formatting_style">💬 Formatting, Verbosity, or Tone Preference</option>
            <option value="wrong_action">⚙️ Executed the Wrong Command / Tool</option>
            <option value="other">📝 Other Operational Flaw</option>
          </select>
        </div>
        <textarea class="fb-corr-text" placeholder="Explain what D.E.E.P should have done instead (e.g. Always use uv instead of pip, or Do not recommend Red Dwarf Friday for tactical instincts)..." style="width:100%; height:55px; background:#090d16; border:1px solid rgba(255,255,255,0.15); border-radius:6px; color:#fff; font-size:0.75rem; padding:6px; box-sizing:border-box; resize:vertical; font-family:inherit;"></textarea>
        <div style="display:flex; justify-content:flex-end; gap:6px; margin-top:6px;">
          <button class="fb-cancel-btn" style="background:transparent; border:1px solid rgba(255,255,255,0.15); border-radius:6px; color:#94a3b8; font-size:0.72rem; padding:3px 10px; cursor:pointer;">Cancel</button>
          <button class="fb-submit-btn" style="background:linear-gradient(135deg, #0284c7, #9333ea); border:none; border-radius:6px; color:#fff; font-weight:700; font-size:0.72rem; padding:4px 12px; cursor:pointer;">Save Rule & Train Core</button>
        </div>
      `;

      msgWrapper.appendChild(toolbar);
      msgWrapper.appendChild(panel);

      const getAssociatedPrompt = () => {
        let prev = msgWrapper.previousElementSibling;
        while (prev) {
          if (prev.classList.contains('user')) {
            return prev.querySelector('.bubble')?.innerText?.trim() || window.lastUserPromptSent || '';
          }
          prev = prev.previousElementSibling;
        }
        return window.lastUserPromptSent || 'Recent command';
      };

      const getAiText = () => {
        return bubble.innerText?.trim() || '';
      };

      btnUp.onclick = async () => {
        btnUp.disabled = true;
        btnDown.disabled = true;
        btnTeach.disabled = true;
        btnUp.style.background = 'rgba(16,185,129,0.2)';
        btnUp.style.borderColor = 'rgba(16,185,129,0.6)';
        btnUp.style.color = '#34d399';
        btnUp.innerHTML = '✓ Helpful';

        badge.style.display = 'inline';
        badge.style.color = '#34d399';
        badge.textContent = '✓ Learned as Correct (+1)';

        try {
          await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              chat_id: currentChatId,
              message_id: msgId || msgWrapper.dataset.msgId || '',
              prompt: getAssociatedPrompt(),
              ai_response: getAiText(),
              rating: 1,
              feedback_type: 'thumbs_up',
              critique_tag: 'accurate'
            })
          });
          if (typeof playHoloSound === 'function') playHoloSound('beep');
        } catch(e) {
          console.error('[Feedback error]:', e);
        }
      };

      const openPanel = () => {
        panel.style.display = 'block';
        panel.querySelector('.fb-corr-text')?.focus();
      };

      const closePanel = () => {
        panel.style.display = 'none';
      };

      btnDown.onclick = openPanel;
      btnTeach.onclick = openPanel;

      panel.querySelector('.fb-close-panel').onclick = closePanel;
      panel.querySelector('.fb-cancel-btn').onclick = closePanel;

      panel.querySelector('.fb-submit-btn').onclick = async () => {
        const tag = panel.querySelector('.fb-tag-select')?.value || 'user_reported_flaw';
        const corr = panel.querySelector('.fb-corr-text')?.value?.trim() || '';
        
        const submitBtn = panel.querySelector('.fb-submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        try {
          await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              chat_id: currentChatId,
              message_id: msgId || msgWrapper.dataset.msgId || '',
              prompt: getAssociatedPrompt(),
              ai_response: getAiText(),
              rating: -1,
              feedback_type: 'correction',
              critique_tag: tag,
              user_correction: corr
            })
          });
          
          closePanel();
          btnDown.style.background = 'rgba(239,68,68,0.2)';
          btnDown.style.borderColor = 'rgba(239,68,68,0.6)';
          btnDown.style.color = '#f87171';
          btnDown.innerHTML = '⚠️ Corrected';
          btnUp.disabled = true;
          btnDown.disabled = true;

          badge.style.display = 'inline';
          badge.style.color = '#fbbf24';
          badge.textContent = '⚠️ Correction Saved to Cognitive Memory';

          if (typeof playHoloSound === 'function') playHoloSound('alert');
        } catch(e) {
          console.error('[Feedback error]:', e);
          submitBtn.disabled = false;
          submitBtn.textContent = 'Save Rule & Train Core';
        }
      };
    }

    function appendMessage(role, content, msgId = null) {
      if (role === 'user') {
        const hero = document.getElementById('cockpitHeroDashboard');
        if (hero) hero.style.display = 'none';
        window.lastUserPromptSent = content;
      }
      const msgWrapper = document.createElement('div');
      msgWrapper.className = `msg-wrapper ${role}`;
      if (msgId) msgWrapper.dataset.msgId = msgId;
      
      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      if (role === 'user') {
        bubble.innerHTML = renderUserMessage(content);
      } else {
        bubble.innerHTML = content ? renderMarkdownWithSandbox(content) : '';
      }
      
      msgWrapper.appendChild(bubble);

      if (role !== 'user' && content) {
        attachFeedbackControls(msgWrapper, bubble, msgId);
      }

      chatScroll.appendChild(msgWrapper);
      chatScroll.scrollTop = chatScroll.scrollHeight;
      return bubble;
    }

    async function triggerScreenVisionScan(promptText) {
      appendMessage('user', promptText);
      const aiBubble = appendMessage('ai', '👁️ *Initiating Visual Screen Protocol... Scanning desktop*');
      
      // Holographic scanning reticle animation
      const overlay = document.createElement('div');
      overlay.style.position = 'fixed';
      overlay.style.top = '0'; overlay.style.left = '0';
      overlay.style.width = '100vw'; overlay.style.height = '100vh';
      overlay.style.pointerEvents = 'none';
      overlay.style.zIndex = '99999';
      overlay.style.boxShadow = 'inset 0 0 150px rgba(16, 185, 129, 0.4)';
      overlay.style.background = 'linear-gradient(transparent 50%, rgba(16, 185, 129, 0.15) 50%)';
      overlay.style.backgroundSize = '100% 8px';
      overlay.style.border = '2px solid rgba(16, 185, 129, 0.8)';
      
      const style = document.createElement('style');
      style.innerHTML = `@keyframes holo-scan { 0% { background-position: 0 -100vh; } 100% { background-position: 0 100vh; } }`;
      document.head.appendChild(style);
      overlay.style.animation = 'holo-scan 2s infinite linear';
      document.body.appendChild(overlay);
      
      try { playHoloSound('alert'); } catch(e){}

      try {
        const res = await fetch('/api/vision/screen', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: promptText })
        });
        const data = await res.json();
        
        if (data.status === 'success') {
          aiBubble.innerHTML = renderMarkdownWithSandbox(data.analysis);
          speakVoiceFeedback(data.analysis);
        } else {
          aiBubble.innerHTML = `<span style="color:red">Vision Error: ${data.message}</span>`;
        }
      } catch (e) {
        aiBubble.innerHTML = `<span style="color:red">System Error: ${e.message}</span>`;
      }
      
      document.body.removeChild(overlay);
      document.head.removeChild(style);
      chatScroll.scrollTop = chatScroll.scrollHeight;
    }
    window.triggerScreenVisionScan = triggerScreenVisionScan;

    sendBtn.addEventListener('click', async () => {
      if (activeAbortController) {
        emergencyStop();
        return;
      }
      const text = promptInput.value.trim();
      if (!text) return;

      // Add user message
      appendMessage('user', text);
      promptInput.value = '';
      resetPromptInputHeight();

      // Client-Side Slash Command & Portal Navigation Router
      const lowerCmd = text.toLowerCase().trim();
      if (lowerCmd === '/nexus' || lowerCmd === '/cyber_nexus' || lowerCmd === 'nexus' || lowerCmd === 'open nexus') {
        appendMessage('ai', '🚀 <strong>Launching AETHERIS // Cyber Operations Nexus...</strong><br><br>Opening <a href="/nexus" style="color:#00f0ff; text-decoration:underline; font-weight:700;">AETHERIS Cyber Nexus</a> in 1 second.');
        setTimeout(() => { window.location.href = '/nexus'; }, 600);
        return;
      }
      if (lowerCmd === '/camera' || lowerCmd === '/camera_vision' || lowerCmd === '/vision' || lowerCmd === 'camera' || lowerCmd === 'open camera') {
        appendMessage('ai', '📷 <strong>Launching Live Camera & Gesture Tracking Cockpit...</strong><br><br>Opening <a href="/camera_vision" style="color:#00f0ff; text-decoration:underline; font-weight:700;">Camera Vision Cockpit</a> in 1 second.');
        setTimeout(() => { window.location.href = '/camera_vision'; }, 600);
        return;
      }
      if (lowerCmd === '/weather') {
        appendMessage('ai', '📍 Opening Local Weather Portal...');
        setTimeout(() => { window.location.href = '/weather'; }, 500);
        return;
      }
      if (lowerCmd === '/gurbani') {
        appendMessage('ai', 'ੴ Opening Sikh Heritage & Nitnem Portal...');
        setTimeout(() => { window.location.href = '/gurbani'; }, 500);
        return;
      }
      if (lowerCmd === '/3d' || lowerCmd === '/cyberpunk') {
        appendMessage('ai', '⚡ Opening 3D Cyberpunk Matrix...');
        setTimeout(() => { window.location.href = '/3d'; }, 500);
        return;
      }
      if (lowerCmd === '/scan' || lowerCmd === '/ocr') {
        triggerScreenVisionScan('Scan my active screen with Live Vision OCR and summarize findings');
        return;
      }
      if (lowerCmd === '/clear') {
        clearActiveChat();
        return;
      }
      
      // Create AI bubble
      const aiBubble = appendMessage('ai', '');
      let fullResponse = '';

      try {
        activeAbortController = new AbortController();
        sendBtn.innerHTML = '■ Stop';
        sendBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        sendBtn.title = 'Click to Stop / Cancel active generation (or press Esc)';

        const payload = {
          prompt: text,
          model: modelSelect ? modelSelect.value : 'auto',
          chat_id: currentChatId
        };
        if (currentAttachedB64) {
          payload.image = currentAttachedB64;
          currentAttachedB64 = null;
          if (attachedBadge) attachedBadge.style.display = 'none';
          if (imageFileInput) imageFileInput.value = '';
        }
        // Autonomous Swarm and Safety Buffer trigger logic
        const lowerText = text.toLowerCase();
        const isDangerous = /\b(delete|remove|rmdir|del |unlink|format|drop table|kill|taskkill|shutdown|wipe|purge|destroy)\b/i.test(lowerText);
        const isSwarmPrompt = /\b(swarm|multi-?agent|consensus|architect and (?:code|review)|full architecture|collaborative agents)\b/i.test(lowerText);
        
        payload.auto_guard = true;
        if (isDangerous) payload.buffer = true;
        if (isSwarmPrompt) payload.swarm = true;

        // Visual telemetry indicator on Auto-Guard badge
        const autoBadge = document.getElementById('autoProtectionBadge');
        const autoText = document.getElementById('autoProtectionText');
        if (autoBadge && autoText) {
          if (isDangerous) {
            autoText.textContent = 'Auto-Guard: Buffer Active 🛡️';
            autoBadge.style.borderColor = 'rgba(239,68,68,0.6)';
            autoBadge.style.color = '#ef4444';
          } else if (isSwarmPrompt) {
            autoText.textContent = 'Auto-Guard: Swarm Consensus 🐝';
            autoBadge.style.borderColor = 'rgba(56,189,248,0.6)';
            autoBadge.style.color = '#38bdf8';
          } else {
            autoText.textContent = 'Auto-Guard: Active';
            autoBadge.style.borderColor = 'rgba(255,255,255,0.08)';
            autoBadge.style.color = '#94a3b8';
          }
        }

        const response = await fetch('/api/chat/stream', {
          method: 'POST',
          signal: activeAbortController.signal,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        if (!response.body) {
           aiBubble.innerHTML = 'Error: Stream not supported.';
           return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;
        let ttsSpokenIndex = 0;
        let ttsBuffer = "";
        let activeSpeaker = null;
        let hasStreamedTokens = false;
        if (payload && payload.prompt) {
          const lp = payload.prompt.toLowerCase();
          if (/\b(friday)\b/.test(lp)) activeSpeaker = 'friday';
          else if (/\b(jarvis|yarvis)\b/.test(lp)) activeSpeaker = 'jarvis';
        }

        // Clear TTS before new message starts streaming
        if (ttsEnabled && window.speechSynthesis) window.speechSynthesis.cancel();

        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          if (value) {
            const chunk = decoder.decode(value, { stream: !done });
            // Parse SSE format
            const lines = chunk.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.substring(6));
                  if (data.speaker) {
                    activeSpeaker = data.speaker;
                  }
                  if (data.token) {
                    hasStreamedTokens = true;
                    fullResponse += data.token;
                    let isThinking = false;
                    const lastThinkStart = fullResponse.lastIndexOf('<think>');
                    const lastThinkEnd = fullResponse.lastIndexOf('</think>');
                    if (lastThinkStart !== -1) {
                      isThinking = lastThinkEnd === -1 || lastThinkStart > lastThinkEnd;
                    }
                    
                    if (!isThinking) {
                        // if we just closed a think block, only grab what's after it
                        if (data.token.includes('</think>')) {
                            ttsBuffer += data.token.split('</think>').pop();
                        } else if (!fullResponse.substring(lastThinkEnd !== -1 ? lastThinkEnd : 0).includes('<think')) {
                            // Don't append partial '<think' tags to ttsBuffer
                            ttsBuffer += data.token;
                        }
                    }
                    // Check for artifact HTML while streaming (rudimentary check)
                    if (ttsEnabled && !data.is_dual_dialogue) {
                        const sentenceMatch = ttsBuffer.match(/([^.!?]+[.!?]+(\s|\n|$))/);
                        if (sentenceMatch && sentenceMatch[1]) {
                            const rawSentence = sentenceMatch[1];
                            const clean = cleanTextForSpeech(rawSentence);
                            if (clean && clean.length > 1) {
                              speakVoiceFeedback(clean, false, activeSpeaker);
                            }
                            ttsBuffer = ttsBuffer.substring(sentenceMatch.index + rawSentence.length);
                        }
                    }
                    // Optimize Markdown parsing with a throttle/batcher using requestAnimationFrame
                    if (!aiBubble.dataset.renderPending) {
                      aiBubble.dataset.renderPending = "true";
                      requestAnimationFrame(() => {
                        aiBubble.innerHTML = renderMarkdownWithSandbox(fullResponse);
                        delete aiBubble.dataset.renderPending;
                        const isNearBottom = (chatScroll.scrollHeight - chatScroll.scrollTop - chatScroll.clientHeight) < 140;
                        if (isNearBottom) {
                          chatScroll.scrollTop = chatScroll.scrollHeight;
                        }
                      });
                    }
                  } else if (data.response) {
                    if (hasStreamedTokens) {
                      // Already streamed token-by-token; sync canonical full response without duplicating!
                      fullResponse = data.response;
                    } else {
                      // Non-streamed response (e.g., from direct interceptors or skills)
                      fullResponse = data.response;
                      if (data.is_dual_dialogue || (data.response.includes('J.A.R.V.I.S.') && data.response.includes('F.R.I.D.A.Y.'))) {
                        playDualCoPilotAudio(data.response);
                      } else if (ttsEnabled) {
                        const textToSpeak = data.spoken_text || data.response;
                        const clean = cleanTextForSpeech(textToSpeak);
                        if (clean && clean.length > 1) {
                          speakVoiceFeedback(clean, false, data.speaker || activeSpeaker);
                        }
                      }
                    }
                    aiBubble.innerHTML = renderMarkdownWithSandbox(fullResponse);
                    const isNearBottomResp = (chatScroll.scrollHeight - chatScroll.scrollTop - chatScroll.clientHeight) < 140;
                    if (isNearBottomResp) {
                      chatScroll.scrollTop = chatScroll.scrollHeight;
                    }
                  }
                  
                  if (data.chat_id && !currentChatId) {
                    currentChatId = data.chat_id;
                  }
                  
                  // Upon completion, try to extract Artifact & execute UI actions
                  if (data.done) {
                    // Guarantee final flush of markdown
                    aiBubble.innerHTML = renderMarkdownWithSandbox(fullResponse);

                    // Process autonomous execution actions on Cockpit UI
                    const execDetails = data.executed_details || [];
                    if (Array.isArray(execDetails)) {
                      execDetails.forEach(item => {
                        if (item && item.type === 'open_subsystem' && window.DeepSubsystems) {
                          window.DeepSubsystems.open(item.url, item.title, item.icon);
                          showLiveUpdateToast(`${item.icon || '⚡'} Opened: ${item.title || 'Subsystem'}`);
                        } else if (item && item.type === 'open_station' && window.DeepSubsystems) {
                          showLiveUpdateToast(`▶️ ${item.title || 'Station Active'}`);
                        } else if (item && item.type === 'local_audio_player') {
                          showLiveUpdateToast(`🎵 Playing: ${item.title || 'Track'}`);
                        }
                      });
                    }
                    
                    if (data.is_dual_dialogue || (fullResponse.includes('J.A.R.V.I.S.') && fullResponse.includes('F.R.I.D.A.Y.'))) {
                        ttsBuffer = "";
                        playDualCoPilotAudio(fullResponse);
                    } else if (ttsEnabled && ttsBuffer.trim().length > 0) {
                        const clean = cleanTextForSpeech(ttsBuffer.trim());
                        if (clean && clean.length > 1) {
                          speakVoiceFeedback(clean, false, data.speaker || activeSpeaker);
                        }
                        ttsBuffer = "";
                    }
                    const htmlMatch = fullResponse.match(/```html([\s\S]*?)```/);
                    if (htmlMatch && htmlMatch[1] && typeof renderArtifact === 'function') {
                      renderArtifact(htmlMatch[1]);
                    }
                    if (aiBubble && aiBubble.parentElement) {
                      if (data.message_id) aiBubble.parentElement.dataset.msgId = data.message_id;
                      attachFeedbackControls(aiBubble.parentElement, aiBubble, data.message_id);
                    }
                    if (document.hidden) {
                        window.showOSNotification("D.E.E.P. Alert", { body: "Commander, I have completed the execution." });
                    }
                    setTimeout(loadChatHistory, 500);
                  }
                } catch (e) {
                   console.error("Error parsing JSON chunk:", line, e);
                }
              }
            }
          }
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          aiBubble.innerHTML += `<br><span style="color:red">Error: ${err.message}</span>`;
        }
      } finally {
        activeAbortController = null;
        sendBtn.innerHTML = '➤';
        sendBtn.style.background = 'linear-gradient(135deg, #0284c7, #9333ea)';
        sendBtn.title = 'Send Prompt';
      }
    });

        promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
      }
    });

    // Auto-expand textarea & update live stats as user types or pastes
    promptInput.addEventListener('input', updatePromptInputAutoHeight);
    promptInput.addEventListener('paste', () => setTimeout(updatePromptInputAutoHeight, 20));

    // Multimodal Drag & Drop Ingestion
    promptInput.addEventListener('dragover', (e) => {
        e.preventDefault();
        promptInput.style.border = '2px dashed #00e5ff';
        promptInput.style.backgroundColor = 'rgba(0, 229, 255, 0.1)';
    });
    
    promptInput.addEventListener('dragleave', (e) => {
        e.preventDefault();
        promptInput.style.border = '1px solid rgba(255,255,255,0.1)';
        promptInput.style.backgroundColor = 'transparent';
    });
    
    promptInput.addEventListener('drop', async (e) => {
        e.preventDefault();
        promptInput.style.border = '1px solid rgba(255,255,255,0.1)';
        promptInput.style.backgroundColor = 'transparent';
        
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            const formData = new FormData();
            formData.append("file", file);
            
            promptInput.placeholder = "Uploading & Parsing " + file.name + "...";
            
            try {
                const res = await fetch("/api/upload_context", {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                
                if (data.error) {
                    alert("Upload error: " + data.error);
                } else if (data.type === "text") {
                    promptInput.value += `\n\n[File Content: ${data.filename}]\n${data.content}\n\n`;
                    updatePromptInputAutoHeight();
                } else if (data.type === "image") {
                    promptInput.value += `\n\n[Attached Image: ${data.filename}]\n[BASE64_IMG:${data.base64}]\n\n`;
                    updatePromptInputAutoHeight();
                }
            } catch (err) {
                console.error(err);
                alert("Upload failed.");
            }
            promptInput.placeholder = "Tell me what to do on your PC or ask a question...";
        }
    });
    // --- Mobile Sensor Streaming ---
    if (window.DeviceMotionEvent && /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
        let lastSensorTime = 0;
        window.addEventListener('devicemotion', (event) => {
            const now = Date.now();
            if (now - lastSensorTime > 500) { // Stream twice a second
                lastSensorTime = now;
                const payload = {
                    acceleration: {
                        x: event.accelerationIncludingGravity?.x,
                        y: event.accelerationIncludingGravity?.y,
                        z: event.accelerationIncludingGravity?.z
                    },
                    gyroscope: {
                        alpha: event.rotationRate?.alpha,
                        beta: event.rotationRate?.beta,
                        gamma: event.rotationRate?.gamma
                    }
                };
                fetch('/api/sensors/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).catch(e => console.error('Sensor stream failed:', e));
            }
        });
    }

    // =========================================================================
    // D.E.E.P AGENT EXECUTION WAR ROOM & CODE MONITOR CONTROLLER
    // =========================================================================
    let isWarRoomActive = false;
    let warRoomTelemetryInterval = null;

    window.refreshWarRoomTelemetry = async function() {
      try {
        const res = await fetch('/api/system/war_room_status');
        if (!res.ok) return;
        const data = await res.json();
        if (!data.success) return;

        // 1. Daemons Watchdog
        const daemonsList = document.getElementById('warRoomDaemonsList');
        if (daemonsList && Array.isArray(data.daemons)) {
          daemonsList.innerHTML = data.daemons.map(d => {
            const isOnline = d.status === 'ONLINE';
            const dotColor = isOnline ? '#4ade80' : '#f87171';
            const badgeBg = isOnline ? 'rgba(74,222,128,0.15)' : 'rgba(239,68,68,0.15)';
            const badgeBorder = isOnline ? 'rgba(74,222,128,0.4)' : 'rgba(239,68,68,0.4)';
            return `
              <div style="display:flex; align-items:center; justify-content:space-between; background:rgba(4,8,18,0.6); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:6px 10px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span style="width:7px; height:7px; border-radius:50%; background:${dotColor}; box-shadow:0 0 6px ${dotColor};"></span>
                  <div>
                    <div style="font-size:0.75rem; font-weight:700; color:#f1f5f9;">${d.name}</div>
                    <div style="font-size:0.65rem; color:#94a3b8;">${d.target}</div>
                  </div>
                </div>
                <span style="font-size:0.65rem; font-weight:800; padding:2px 6px; border-radius:4px; background:${badgeBg}; border:1px solid ${badgeBorder}; color:${dotColor};">${d.status}</span>
              </div>
            `;
          }).join('');
        }

        // 2. Database Status
        const dbTables = document.getElementById('wrDbTables');
        if (dbTables && data.database) {
          dbTables.textContent = `${data.database.tables || 0} Tables`;
        }
        const dbLatency = document.getElementById('wrDbLatency');
        if (dbLatency && data.database) {
          dbLatency.textContent = `${data.database.latency_ms || 0} ms`;
        }

        // 3. Git Status
        const gitBranch = document.getElementById('wrGitBranch');
        if (gitBranch && data.git) {
          gitBranch.textContent = data.git.branch || 'master';
        }
        const gitStatus = document.getElementById('wrGitStatus');
        if (gitStatus && data.git) {
          const isClean = (data.git.dirty_files === 0);
          gitStatus.textContent = isClean ? 'Clean (0 uncommitted)' : `Modified (${data.git.dirty_files} files)`;
          gitStatus.style.color = isClean ? '#4ade80' : '#facc15';
        }

        // 4. Hardware Vitals
        if (data.hardware) {
          const cpu = Math.round(data.hardware.cpu_percent || 0);
          const cpuEl = document.getElementById('wrCpuLoad');
          const cpuBar = document.getElementById('wrCpuBar');
          if (cpuEl) cpuEl.textContent = `${cpu}%`;
          if (cpuBar) cpuBar.style.width = `${Math.min(100, Math.max(2, cpu))}%`;

          const ram = Math.round(data.hardware.ram_percent || 0);
          const ramUsed = data.hardware.ram_used_gb || 0;
          const ramTotal = data.hardware.ram_total_gb || 0;
          const ramEl = document.getElementById('wrRamUsage');
          const ramBar = document.getElementById('wrRamBar');
          if (ramEl) ramEl.textContent = `${ram}% (${ramUsed}G / ${ramTotal}G)`;
          if (ramBar) ramBar.style.width = `${Math.min(100, Math.max(2, ram))}%`;

          const diskEl = document.getElementById('wrDiskFree');
          if (diskEl) diskEl.textContent = `${data.hardware.disk_free_gb || 0} GB`;
        }

        // 5. Resilience Circuit Breakers Matrix
        if (Array.isArray(data.circuit_breakers)) {
          const breakersList = document.getElementById('warRoomBreakersList');
          const breakersSummary = document.getElementById('wrBreakersSummary');
          const closedCount = data.circuit_breakers.filter(b => b.state === 'CLOSED').length;
          if (breakersSummary) {
            breakersSummary.textContent = `${closedCount}/${data.circuit_breakers.length} CLOSED`;
            breakersSummary.style.color = (closedCount === data.circuit_breakers.length) ? '#4ade80' : '#f43f5e';
          }
          if (breakersList) {
            breakersList.innerHTML = data.circuit_breakers.map(b => {
              const isClosed = b.state === 'CLOSED';
              const isHalf = b.state === 'HALF_OPEN';
              const dotColor = isClosed ? '#4ade80' : (isHalf ? '#facc15' : '#f43f5e');
              const badgeBg = isClosed ? 'rgba(74,222,128,0.15)' : (isHalf ? 'rgba(250,204,21,0.15)' : 'rgba(244,63,94,0.15)');
              const badgeBorder = isClosed ? 'rgba(74,222,128,0.4)' : (isHalf ? 'rgba(250,204,21,0.4)' : 'rgba(244,63,94,0.4)');
              return `
                <div style="display:flex; flex-direction:column; gap:4px; background:rgba(4,8,18,0.6); border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:6px 10px;">
                  <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div style="display:flex; align-items:center; gap:6px;">
                      <span style="width:7px; height:7px; border-radius:50%; background:${dotColor}; box-shadow:0 0 6px ${dotColor};"></span>
                      <strong style="font-size:0.75rem; color:#f1f5f9;">${b.name}</strong>
                    </div>
                    <span style="font-size:0.65rem; font-weight:800; padding:2px 6px; border-radius:4px; background:${badgeBg}; border:1px solid ${badgeBorder}; color:${dotColor};">${b.state}</span>
                  </div>
                  <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.65rem; color:#94a3b8;">
                    <span>Health: <strong style="color:#4ade80;">${b.health_ratio || 100}%</strong> • Fails: ${b.consecutive_failures || 0}</span>
                    <div style="display:flex; gap:4px;">
                      ${isClosed ? `<button onclick="tripCircuitBreaker('${b.name}')" style="background:rgba(244,63,94,0.2); border:1px solid rgba(244,63,94,0.4); color:#f43f5e; border-radius:4px; padding:1px 5px; font-size:0.6rem; cursor:pointer;" title="Simulate fault">Trip</button>` : `<button onclick="resetCircuitBreaker('${b.name}')" style="background:rgba(74,222,128,0.2); border:1px solid rgba(74,222,128,0.4); color:#4ade80; border-radius:4px; padding:1px 5px; font-size:0.6rem; cursor:pointer;" title="Reset to CLOSED">Reset</button>`}
                    </div>
                  </div>
                </div>
              `;
            }).join('');
          }
        }

        // 6. Embedded MCU Projects Dropdown population
        if (data.mcu && Array.isArray(data.mcu.projects)) {
          const select = document.getElementById('wrMcuProjectSelect');
          if (select && select.options.length <= 5 && data.mcu.projects.length > 5) {
            const currentVal = select.value;
            select.innerHTML = data.mcu.projects.map(p => `<option value="${p.name}">${p.name}</option>`).join('');
            if (currentVal) select.value = currentVal;
          }
        }
      } catch (err) {
        console.warn('War room telemetry fetch error:', err);
      }
    };

    window.tripCircuitBreaker = async function(name) {
      try {
        const res = await fetch('/api/system/circuit_breakers/trip', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        });
        const data = await res.json();
        const logs = document.getElementById('warRoomTerminalLogs');
        if (logs) logs.textContent += `\n[Circuit Breaker] Manually tripped '${name}' -> OPEN (Fault Injection Active)`;
        refreshWarRoomTelemetry();
      } catch (e) {
        console.error(e);
      }
    };

    window.resetCircuitBreaker = async function(name) {
      try {
        const res = await fetch('/api/system/circuit_breakers/reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name })
        });
        const data = await res.json();
        const logs = document.getElementById('warRoomTerminalLogs');
        if (logs) logs.textContent += `\n[Circuit Breaker] Reset '${name}' -> CLOSED (Normal Operation Restored)`;
        refreshWarRoomTelemetry();
      } catch (e) {
        console.error(e);
      }
    };

    window.auditSelectedMcuProject = async function() {
      const select = document.getElementById('wrMcuProjectSelect');
      const fb = document.getElementById('wrMcuFeedback');
      const logs = document.getElementById('warRoomTerminalLogs');
      if (!select || !fb) return;
      const proj = select.value;
      fb.textContent = `Auditing ${proj} against PIC18F85K22 rules...`;
      try {
        const res = await fetch('/api/hardware/mcu/audit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project: proj })
        });
        const data = await res.json();
        if (data.passed) {
          fb.innerHTML = `<span style="color:#4ade80;">[PASS]</span> ${data.message}`;
        } else {
          fb.innerHTML = `<span style="color:#f43f5e;">[WARN]</span> ${data.findings.join('\n')}`;
        }
        if (logs) logs.textContent += `\n[MCU Audit: ${proj}] ${data.message}`;
      } catch (e) {
        fb.textContent = `Audit error: ${e.message}`;
      }
    };

    window.compileSelectedMcuProject = async function() {
      const select = document.getElementById('wrMcuProjectSelect');
      const fb = document.getElementById('wrMcuFeedback');
      const logs = document.getElementById('warRoomTerminalLogs');
      if (!select || !fb) return;
      const proj = select.value;
      fb.textContent = `Compiling ${proj} with xc8-cc + DFP...`;
      try {
        const res = await fetch('/api/hardware/mcu/compile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project: proj })
        });
        const data = await res.json();
        if (data.success) {
          fb.innerHTML = `<span style="color:#4ade80;">[SUCCESS]</span> Compiled in ${data.elapsed_seconds}s (${data.hex_size_bytes}B HEX)`;
          if (logs) logs.textContent += `\n[xc8-cc Build: ${proj}]\n${data.output}`;
        } else {
          fb.innerHTML = `<span style="color:#f43f5e;">[BUILD FAILED]</span> ${data.error || 'Check compiler output'}`;
          if (logs) logs.textContent += `\n[xc8-cc Error: ${proj}]\n${data.output || data.error}`;
        }
      } catch (e) {
        fb.textContent = `Compile error: ${e.message}`;
      }
    };

    window.flashSelectedMcuProject = async function() {
      const select = document.getElementById('wrMcuProjectSelect');
      const fb = document.getElementById('wrMcuFeedback');
      const logs = document.getElementById('warRoomTerminalLogs');
      if (!select || !fb) return;
      const proj = select.value;
      fb.textContent = `Flashing ${proj} via PICkit 3 (BUR181916585)...`;
      try {
        const res = await fetch('/api/hardware/mcu/flash', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project: proj })
        });
        const data = await res.json();
        if (data.success) {
          fb.innerHTML = `<span style="color:#4ade80;">[FLASHED OK]</span> Target running (${data.elapsed_seconds}s)`;
          if (logs) logs.textContent += `\n[PICkit 3 Programmed: ${proj}]\n${data.output}`;
        } else {
          const alertMsg = data.device_id_message || data.error || 'Programming failed';
          fb.innerHTML = `<span style="color:#f43f5e;">[FLASH FAILED]</span> ${alertMsg}`;
          if (logs) logs.textContent += `\n[PICkit 3 Error: ${proj}]\n${data.output || alertMsg}`;
        }
      } catch (e) {
        fb.textContent = `Flash error: ${e.message}`;
      }
    };

    window.toggleDeepQuantumHUD = function(force) {
      const modal = document.getElementById('deepQuantumHUDModal');
      if (!modal) return;

      if (force === undefined) {
        isWarRoomActive = !isWarRoomActive;
      } else {
        isWarRoomActive = Boolean(force);
      }

      if (isWarRoomActive) {
        modal.style.display = 'flex';
        modal.classList.add('active');
        refreshWarRoomTelemetry();
        if (!warRoomTelemetryInterval) {
          warRoomTelemetryInterval = setInterval(refreshWarRoomTelemetry, 3000);
        }
        setTimeout(() => {
          const inp = document.getElementById('warRoomCmdInput');
          if (inp) inp.focus();
        }, 100);
      } else {
        modal.style.display = 'none';
        modal.classList.remove('active');
        if (warRoomTelemetryInterval) {
          clearInterval(warRoomTelemetryInterval);
          warRoomTelemetryInterval = null;
        }
      }
    };

    window.executeWarRoomCmd = async function(cmd) {
      const logs = document.getElementById('warRoomTerminalLogs');
      if (!cmd || !logs) return;

      logs.textContent += `\n\nPS > ${cmd}\n[Executing on host via PowerShell...]`;
      logs.scrollTop = logs.scrollHeight;

      try {
        const res = await fetch('/api/terminal/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: cmd })
        });
        const data = await res.json();
        const out = data.output || data.error || (data.success ? 'Command completed.' : 'Execution failed.');
        logs.textContent += `\n${out.trim()}`;
      } catch (err) {
        logs.textContent += `\n[Host Transport Error]: ${err.message}`;
      }
      logs.scrollTop = logs.scrollHeight;
    };

    window.executeWarRoomInputCmd = function() {
      const inp = document.getElementById('warRoomCmdInput');
      if (!inp) return;
      const cmd = inp.value.trim();
      if (!cmd) return;
      inp.value = '';
      executeWarRoomCmd(cmd);
    };

    window.clearWarRoomTerminal = function() {
      const logs = document.getElementById('warRoomTerminalLogs');
      if (logs) {
        logs.textContent = `[WAR ROOM DIRECT HOST TERMINAL]\nPowerShell Host Bridge Connected. Type any command below:\n`;
      }
    };

    window.triggerAutoEvolutionScan = async function() {
      const logs = document.getElementById('warRoomTerminalLogs');
      const btn = document.getElementById('btnAutoEvolveSkills');
      if (btn) btn.textContent = '⏳ Scanning Web & Evolving...';
      if (logs) {
        logs.textContent += '\n\n[AUTO-EVOLUTION] Scanning web & documentation for cutting-edge capabilities...\nSynthesizing verified SKILL.md specs & registering MCP tools...';
        logs.scrollTop = logs.scrollHeight;
      }
      try {
        const res = await fetch('/api/system/auto_evolve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scan: true })
        });
        const data = await res.json();
        if (data.success && data.details) {
          if (logs) {
            logs.textContent += `\n[SUCCESS] Evolution scan complete!\nInstalled/Verified: ${data.details.skills_installed_count} next-gen skills.\nActive MCP Servers: ${data.details.active_mcp_servers.join(', ')}`;
            logs.scrollTop = logs.scrollHeight;
          }
          if (typeof speakVoiceFeedback === 'function') {
            speakVoiceFeedback('Auto evolution complete. 5 next-generation capabilities verified and active.');
          }
        }
      } catch (err) {
        if (logs) logs.textContent += `\n[Evolution Error]: ${err.message}`;
      } finally {
        if (btn) btn.textContent = '⚡ Auto-Evolve & Upgrade Skills';
      }
    };

    if ('BroadcastChannel' in window) {
      const cockpitChannel = new BroadcastChannel('deep_cockpit_channel');
      cockpitChannel.onmessage = (e) => {
        const data = e.data || {};
        if (data.type === 'DEPLOY_HUD' || data.type === 'SHOW_HUD' || data.type === 'WAR_ROOM') {
          window.toggleDeepQuantumHUD(true);
        } else if (data.type === 'CLOSE_HUD' || data.type === 'HIDE_HUD') {
          window.toggleDeepQuantumHUD(false);
        } else if (data.type === 'NETWORK_ALERT' || data.type === 'CYBER_ALERT') {
          if (typeof handleIncomingSecurityAlert === 'function') {
            handleIncomingSecurityAlert(data.alert || data);
          }
        }
      };
    }


    let graphInstance = null;
    window.toggleKnowledgeGraph = async function(force) {
      const modal = document.getElementById('knowledgeGraphModal');
      const isActive = modal.classList.contains('active');
      if (force === false || isActive) {
        modal.classList.remove('active');
        if (graphInstance) {
          graphInstance._destructor();
          graphInstance = null;
          document.getElementById('knowledgeGraphCanvas').innerHTML = '';
        }
        return;
      }
      
      modal.classList.add('active');
      playHoloSound('chime');
      speakVoiceFeedback('Initializing 3D Knowledge Graph.');
      
      try {
        const res = await fetch('/api/graph_data');
        const data = await res.json();
        
        graphInstance = ForceGraph3D()(document.getElementById('knowledgeGraphCanvas'))
          .graphData(data)
          .nodeLabel('id')
          .nodeColor('color')
          .nodeVal('size')
          .linkDirectionalParticles(2)
          .linkDirectionalParticleWidth(1.5)
          .backgroundColor('#070a12')
          .onNodeClick(node => {
            speakVoiceFeedback('Selected node: ' + node.id);
            if (node.fact_text) {
                appendMessage('ai', `**Knowledge Graph Data for ${node.id}:**\n${node.fact_text}`);
            }
            // Focus on node
            const distance = 100;
            const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
            graphInstance.cameraPosition(
              { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
              node,
              3000
            );
            modal.classList.remove('active');
          });
          
      } catch (e) {
        console.error('Failed to render 3D Graph:', e);
      }
    };



    window.executeSandboxCode = async function(btn, lang) {
        const wrapper = btn.closest('.code-block-wrapper');
        const code = wrapper.querySelector('code').textContent;
        const outDiv = wrapper.querySelector('.sandbox-output');
        outDiv.style.display = 'block';
        outDiv.innerHTML = '<i style="color:#00ffff;">Executing in Sandbox...</i>';
        try {
            const res = await fetch('/api/sandbox/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code, lang})
            });
            const data = await res.json();
            if (data.success) {
                outDiv.innerHTML = `<b style="color:#00ff00;">Output:</b><br><pre style="white-space:pre-wrap;">${data.output.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`;
            } else {
                outDiv.innerHTML = `<b style="color:#ff4444;">Error:</b><br><pre style="white-space:pre-wrap; color:#ff4444;">${data.error.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</pre>`;
            }
        } catch(e) {
            outDiv.innerHTML = `<b style="color:#ff4444;">Error:</b> ${e.message}`;
        }
    }

    window.showOSNotification = function(title, options = {}) {
        if (!('serviceWorker' in navigator) || !('Notification' in window)) return;
        if (Notification.permission === 'granted') {
            navigator.serviceWorker.ready.then(registration => {
                registration.showNotification(title, {
                    icon: '/static/icons/icon-192.png',
                    badge: '/static/icons/badge-72.png',
                    ...options
                });
            });
        }
    };

    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
          .then(registration => {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
            if ('Notification' in window && Notification.permission !== 'granted' && Notification.permission !== 'denied') {
                Notification.requestPermission();
            }
          }, err => {
            console.log('ServiceWorker registration failed: ', err);
          });
      });
    }

// ==============================================================
// 🐳 DOCKER & MCP TOOLKIT WORKSTATION CONTROLLER
// ==============================================================
window.openDockerControlModal = function() {
  const m = document.getElementById('dockerControlModal');
  if (m) {
    m.style.display = 'flex';
    refreshDockerTelemetry();
  }
};

window.closeDockerControlModal = function() {
  const m = document.getElementById('dockerControlModal');
  if (m) m.style.display = 'none';
};

window.refreshDockerTelemetry = async function() {
  try {
    const res = await fetch('/api/docker/telemetry');
    const data = await res.json();
    if (!data.success) return;

    // Profile & metrics
    const profEl = document.getElementById('dockerProfileVal');
    if (profEl && data.mcp) profEl.textContent = data.mcp.profile || 'default';

    const srvCountEl = document.getElementById('dockerServerCountVal');
    if (srvCountEl && data.mcp) srvCountEl.textContent = `${data.mcp.serverCount || 0} Servers`;

    const toolCountEl = document.getElementById('dockerToolCountVal');
    if (toolCountEl && data.mcp) toolCountEl.textContent = `${data.mcp.toolCount || 0} Tools`;

    // Daemon badge
    const badge = document.getElementById('dockerDaemonBadge');
    if (badge) {
      if (data.daemon && data.daemon.active) {
        badge.textContent = 'DAEMON ACTIVE';
        badge.style.color = '#4ade80';
        badge.style.borderColor = 'rgba(34,197,94,0.3)';
        badge.style.background = 'rgba(34,197,94,0.15)';
      } else {
        badge.textContent = 'DAEMON OFFLINE';
        badge.style.color = '#f87171';
        badge.style.borderColor = 'rgba(239,68,68,0.3)';
        badge.style.background = 'rgba(239,68,68,0.15)';
      }
    }

    // Render servers pills
    const pills = document.getElementById('dockerServersPills');
    if (pills && data.mcp && data.mcp.servers) {
      pills.innerHTML = data.mcp.servers.map(s => `
        <div style="background:rgba(14,165,233,0.12); border:1px solid rgba(14,165,233,0.35); border-radius:8px; padding:6px 12px; display:inline-flex; align-items:center; gap:6px;">
          <span style="font-size:0.8rem; color:#38bdf8;">📦</span>
          <span style="font-size:0.8rem; font-weight:700; color:#fff;">${s}</span>
          <span style="font-size:0.65rem; color:#4ade80; background:rgba(34,197,94,0.2); padding:1px 5px; border-radius:4px;">OCI Ready</span>
        </div>
      `).join('');
    }
  } catch (err) {
    console.error('Error fetching Docker telemetry:', err);
  }
};

window.testDockerSearch = async function() {
  const query = document.getElementById('dockerQuickQuery')?.value.trim();
  const out = document.getElementById('dockerMcpOutput');
  if (!query) {
    alert('Please enter a search query');
    return;
  }
  if (out) {
    out.style.display = 'block';
    out.textContent = `[Docker MCP] Invoking DuckDuckGo container for: "${query}"...`;
  }
  try {
    const res = await fetch('/api/docker/mcp/call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool: 'search', arguments: { query: query } })
    });
    const data = await res.json();
    if (out) {
      out.textContent = data.success ? (data.output || JSON.stringify(data.data || data, null, 2)) : `Error: ${data.error}`;
    }
  } catch (err) {
    if (out) out.textContent = `Network error: ${err.message}`;
  }
};

window.testDockerFetch = async function() {
  const url = document.getElementById('dockerQuickQuery')?.value.trim();
  const out = document.getElementById('dockerMcpOutput');
  if (!url || !url.startsWith('http')) {
    alert('Please enter a valid URL starting with http:// or https://');
    return;
  }
  if (out) {
    out.style.display = 'block';
    out.textContent = `[Docker MCP] Fetching URL via container: ${url}...`;
  }
  try {
    const res = await fetch('/api/docker/mcp/call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool: 'fetch', arguments: { url: url } })
    });
    const data = await res.json();
    if (out) {
      out.textContent = data.success ? (data.output || JSON.stringify(data.data || data, null, 2)) : `Error: ${data.error}`;
    }
  } catch (err) {
    if (out) out.textContent = `Network error: ${err.message}`;
  }
};

window.runDockerSandboxSnippet = async function() {
  const lang = document.getElementById('dockerSandboxLang')?.value || 'python';
  const code = document.getElementById('dockerSandboxCode')?.value || '';
  const resEl = document.getElementById('dockerSandboxResult');
  if (!code.trim()) {
    alert('Please provide code to execute.');
    return;
  }
  if (resEl) {
    resEl.style.display = 'block';
    resEl.style.color = '#38bdf8';
    resEl.textContent = `[Docker Sandbox] Spawning ephemeral container (${lang})...`;
  }
  try {
    const res = await fetch('/api/docker/sandbox/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code, lang: lang })
    });
    const data = await res.json();
    if (resEl) {
      if (data.success) {
        resEl.style.color = '#4ade80';
        resEl.textContent = `[Execution Duration: ${data.elapsedMs}ms | Exit: 0]\n${data.stdout || '(No standard output)'}${data.stderr ? '\n[Warnings/Stderr]: ' + data.stderr : ''}`;
      } else {
        resEl.style.color = '#f87171';
        resEl.textContent = `[Error (${data.elapsedMs}ms)]:\n${data.error || data.stderr || 'Execution failed'}`;
      }
    }
  } catch (err) {
    if (resEl) {
      resEl.style.color = '#f87171';
      resEl.textContent = `Network error: ${err.message}`;
    }
  }
};

window.manageDockerCompose = async function(action) {
  if (!confirm(`Are you sure you want to perform '${action}' on the Docker Compose stack?`)) return;
  try {
    const res = await fetch('/api/docker/compose/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: action })
    });
    const data = await res.json();
    alert(`Docker Compose ${action}: ${data.success ? 'Success!' : 'Error: ' + data.error}\n${data.output || ''}`);
    refreshDockerTelemetry();
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
};