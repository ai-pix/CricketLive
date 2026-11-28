(function setupEmbedAndObsMode() {
  const params = new URLSearchParams(location.search);
  const showControls = params.get("controls") === "1";
  if (!showControls) {
    document.body.classList.add("embed-mode");
  }
  const updateScale = () => {
    const s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    document.documentElement.style.setProperty("--embed-scale", String(s));
  };
  updateScale();
  window.addEventListener("resize", updateScale);
  document.addEventListener("keydown", (e) => {
    if (e.key.toLowerCase() === "c" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      document.body.classList.toggle("embed-mode");
      updateScale();
    }
  });
})();

const calloutText = document.getElementById("calloutText");
const broadcastFrame = document.getElementById("broadcastFrame");
const toggleTransparentBtn = document.getElementById("toggleTransparent");
const toggleCommentaryBtn = document.getElementById("toggleCommentary");
const eventButtons = document.querySelectorAll(".demo-btn[data-event]");

let commentaryEnabled = false;
const audioQueue = [];
let isPlayingAudio = false;

const isTopLevelWindow = window.self === window.top;
const crowdBgStandalone = isTopLevelWindow ? new Audio("/assets/crowd_bg.mp3") : null;
if (crowdBgStandalone) {
  crowdBgStandalone.loop = true;
  crowdBgStandalone.volume = 0.32;
  crowdBgStandalone.play().catch(() => {});
  window.addEventListener("pointerdown", () => {
    if (crowdBgStandalone.paused) crowdBgStandalone.play().catch(() => {});
  }, { once: true });
}

function playStandaloneRoar() {
  if (!isTopLevelWindow) return;
  try {
    const r = new Audio("/assets/crowd_roar.mp3");
    r.volume = 0.65;
    r.play().catch(() => {});
  } catch {}
}

function playNextAudio() {
  if (isPlayingAudio || audioQueue.length === 0) {
    if (crowdBgStandalone && !isPlayingAudio && audioQueue.length === 0) crowdBgStandalone.volume = 0.32;
    return;
  }
  const item = audioQueue.shift();
  const url = typeof item === "string" ? item : item.url;
  const pauseAfterMs = typeof item === "object" && item.pauseMs ? item.pauseMs : 450;

  isPlayingAudio = true;
  if (crowdBgStandalone) crowdBgStandalone.volume = 0.14;
  const audio = new Audio(url);
  window._activeAudioEl = audio;
  const finish = () => {
    if (window._activeAudioEl === audio) window._activeAudioEl = null;
    setTimeout(() => {
      isPlayingAudio = false;
      playNextAudio();
    }, pauseAfterMs);
  };
  audio.addEventListener("ended", finish);
  audio.addEventListener("error", finish);
  audio.play().catch(finish);
}

const teamScoreEl = document.getElementById("teamScore");
const teamOversEl = document.getElementById("teamOvers");

function setCallout(label, tone = "neutral") {
  calloutText.textContent = label;
  calloutText.classList.remove("tone-four", "tone-six", "tone-wicket", "pop-change");

  if (tone === "four") calloutText.classList.add("tone-four");
  if (tone === "six") calloutText.classList.add("tone-six");
  if (tone === "wicket") calloutText.classList.add("tone-wicket");

  void calloutText.offsetWidth;
  calloutText.classList.add("pop-change");
}

function renderBalls(container, balls) {
  container.innerHTML = "";
  balls.forEach((b, idx) => {
    const span = document.createElement("span");
    span.className = "ball";
    if (b === "0") span.classList.add("ball-dot");
    else if (b === "6") span.classList.add("ball-six");
    else if (b.toUpperCase() === "W") span.classList.add("ball-wicket");
    else span.classList.add("ball-run");
    if (idx === balls.length - 1) span.classList.add("ball-active");
    span.textContent = b;
    container.appendChild(span);
  });
}

function getFlagSvg(teamName) {
  const t = (teamName || "").toUpperCase();
  if (t.startsWith("BAN") || t.includes("BANGLADESH")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#006a4e"/><circle cx="27" cy="20" r="11" fill="#f42a41"/></svg>`;
  }
  if (t === "SA" || t.includes("SOUTH AFRICA")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none">
      <rect width="60" height="20" fill="#e03c31"/>
      <rect y="20" width="60" height="20" fill="#001489"/>
      <polygon points="0,0 28,20 0,40" fill="#000000"/>
      <polyline points="0,3 24,20 0,37" fill="none" stroke="#ffb81c" stroke-width="3.5"/>
      <path d="M0,0 L26,18 L60,18 L60,22 L26,22 L0,40" fill="none" stroke="#ffffff" stroke-width="6"/>
      <path d="M0,0 L26,18 L60,18 L60,22 L26,22 L0,40" fill="none" stroke="#007749" stroke-width="4"/>
    </svg>`;
  }
  if (t.startsWith("IND") || t.includes("INDIA")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none">
      <rect width="60" height="13.4" fill="#ff9933"/>
      <rect y="13.3" width="60" height="13.4" fill="#ffffff"/>
      <rect y="26.6" width="60" height="13.4" fill="#138808"/>
      <circle cx="30" cy="20" r="5" fill="none" stroke="#000080" stroke-width="1.2"/>
    </svg>`;
  }
  if (t === "UAE" || t.includes("EMIRATES")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none">
      <rect width="16" height="40" fill="#ce1126"/>
      <rect x="16" width="44" height="13.4" fill="#00732f"/>
      <rect x="16" y="13.3" width="44" height="13.4" fill="#ffffff"/>
      <rect x="16" y="26.6" width="44" height="13.4" fill="#111111"/>
    </svg>`;
  }
  if (t === "AUS" || t.includes("AUSTRALIA")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#012169"/><rect width="26" height="18" fill="#012169"/><path d="M0,0 L26,18 M26,0 L0,18" stroke="#fff" stroke-width="3"/><path d="M13,0 V18 M0,9 H26" stroke="#c8102e" stroke-width="3"/><circle cx="44" cy="14" r="2.2" fill="#fff"/><circle cx="48" cy="24" r="2.2" fill="#fff"/><circle cx="40" cy="28" r="2.2" fill="#fff"/></svg>`;
  }
  if (t === "ENG" || t.includes("ENGLAND")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#ffffff"/><rect x="26" width="8" height="40" fill="#ce1124"/><rect y="16" width="60" height="8" fill="#ce1124"/></svg>`;
  }
  if (t.startsWith("PAK") || t.includes("PAKISTAN")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="15" height="40" fill="#ffffff"/><rect x="15" width="45" height="40" fill="#01411c"/><circle cx="38" cy="20" r="8" fill="#ffffff"/><circle cx="40" cy="18" r="7" fill="#01411c"/></svg>`;
  }
  if (t.startsWith("SL") || t.includes("SRI LANKA")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#ffbe29"/><rect x="3" y="3" width="10" height="34" fill="#00534e"/><rect x="13" y="3" width="10" height="34" fill="#eb7400"/><rect x="25" y="3" width="32" height="34" fill="#8d153a"/><circle cx="41" cy="20" r="7" fill="#ffbe29"/></svg>`;
  }
  if (t === "NZ" || t.includes("NEW ZEALAND")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#00247d"/><path d="M0,0 L24,18 M24,0 L0,18" stroke="#fff" stroke-width="2.5"/><path d="M12,0 V18 M0,9 H24" stroke="#cc142b" stroke-width="2.5"/><circle cx="45" cy="12" r="2.2" fill="#cc142b"/><circle cx="45" cy="28" r="2.2" fill="#cc142b"/><circle cx="38" cy="20" r="2" fill="#cc142b"/><circle cx="51" cy="19" r="2" fill="#cc142b"/></svg>`;
  }
  return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#1e293b"/><text x="30" y="25" text-anchor="middle" fill="#ffd400" font-size="14" font-weight="bold" font-family="sans-serif">${t.slice(0, 3)}</text></svg>`;
}

function updateFlags(battingTeam, bowlingTeam) {
  const leftWing = document.querySelector(".flag-left");
  const rightWing = document.querySelector(".flag-right");
  if (leftWing) {
    leftWing.innerHTML = `<div class="flag-dynamic">${getFlagSvg(battingTeam)}</div><div class="flag-wave-sheen"></div>`;
  }
  if (rightWing) {
    rightWing.innerHTML = `<div class="flag-dynamic">${getFlagSvg(bowlingTeam)}</div><div class="flag-wave-sheen"></div>`;
  }
  const cards = document.querySelectorAll(".players-grid .player-card");
  if (cards.length >= 3) {
    const f0 = cards[0].querySelector(".mini-flag");
    const f1 = cards[1].querySelector(".mini-flag");
    const f2 = cards[2].querySelector(".mini-flag");
    if (f0) f0.innerHTML = getFlagSvg(battingTeam);
    if (f1) f1.innerHTML = getFlagSvg(battingTeam);
    if (f2) f2.innerHTML = getFlagSvg(bowlingTeam);
  }
}

const STATE_CACHE_KEY = "cricket_live_state_v1";
const mainSectionCache = {};

function renderMainIfChanged(key, slice, fn) {
  const sig = JSON.stringify(slice);
  if (mainSectionCache[key] === sig) return;
  mainSectionCache[key] = sig;
  fn();
}

let playerImageDb = {};
let lastMainState = null;

function resolvePlayerPhoto(name) {
  const clean = String(name || "").replace(/\((?:c|wk|vc)\)/gi, "").replace(/[^a-z0-9\s]/gi, " ").trim().toUpperCase().replace(/\s+/g, " ");
  if (!clean) return "";
  if (playerImageDb[clean]) return playerImageDb[clean];
  const parts = clean.split(" ");
  if (parts.length >= 2) {
    const alias = `${parts[0][0]} ${parts[parts.length - 1]}`;
    if (playerImageDb[alias]) return playerImageDb[alias];
    if (playerImageDb[parts[parts.length - 1]]) return playerImageDb[parts[parts.length - 1]];
  }
  return "";
}

fetch("/api/player-images")
  .then((r) => (r.ok ? r.json() : null))
  .then((d) => {
    if (d && d.images) {
      playerImageDb = d.images;
      if (lastMainState) applyLiveState(lastMainState);
    }
  })
  .catch(() => {});

function applyLiveState(data) {
  if (!data) return;
  lastMainState = data;
  try { localStorage.setItem(STATE_CACHE_KEY, JSON.stringify(data)); } catch {}

  renderMainIfChanged("teams", [data.batting_team, data.bowling_team], () => {
    const battingName = document.querySelector(".team-batting .team-name");
    const bowlingName = document.querySelector(".team-bowling .team-name");
    if (battingName) battingName.textContent = data.batting_team;
    if (bowlingName) bowlingName.textContent = data.bowling_team;
    updateFlags(data.batting_team, data.bowling_team);
  });

  if (teamScoreEl) {
    const nextScore = `${data.runs}/${data.wickets}`;
    if (teamScoreEl.textContent !== nextScore) {
      teamScoreEl.textContent = nextScore;
      teamScoreEl.classList.remove("score-flash");
      void teamScoreEl.offsetWidth;
      teamScoreEl.classList.add("score-flash");
    }
  }
  if (teamOversEl) teamOversEl.textContent = data.overs;

  renderMainIfChanged("callout", [data.callout, data.callout_tone], () => {
    setCallout(data.callout, data.callout_tone);
  });

  // Sub-header stats
  const statItems = document.querySelectorAll(".stats-strip .stat-item strong");
  if (statItems.length >= 3) {
    statItems[0].textContent = data.partnership;
    statItems[1].textContent = Number(data.crr).toFixed(2);
    statItems[2].textContent = data.last_5_ov;
  }

  // Over-by-over tracker (only re-render when overs/balls change)
  renderMainIfChanged("overs", [data.prev_over, data.curr_over], () => {
    const overGroups = document.querySelectorAll(".overs-bar .over-group");
    if (overGroups.length >= 2 && data.prev_over && data.curr_over) {
      overGroups[0].querySelector(".over-label strong").textContent = data.prev_over.over_number;
      renderBalls(overGroups[0].querySelector(".balls-row"), data.prev_over.balls);
      overGroups[0].querySelector(".over-total").textContent = `=${data.prev_over.total}`;

      overGroups[1].querySelector(".over-label strong").textContent = data.curr_over.over_number;
      const currRow = overGroups[1].querySelector(".balls-row");
      renderBalls(currRow, data.curr_over.balls);
      if (data.curr_over.balls.length < 6) {
        const liveBall = document.createElement("span");
        liveBall.className = "ball ball-live";
        liveBall.title = "Next delivery";
        liveBall.innerHTML = '<span class="seam"></span>';
        currRow.appendChild(liveBall);
      }
      overGroups[1].querySelector(".over-total").textContent = `=${data.curr_over.total}`;
    }
  });

  // Player cards: [0] STRIKER (always left), [1] NON-STRIKER (middle), [2] BOWLER (right)
  const cards = document.querySelectorAll(".players-grid .player-card");
  if (cards.length >= 3) {
    const initialsOf = (name) => {
      const parts = (name || "").trim().split(/\s+/).filter(Boolean);
      if (parts.length === 0) return "--";
      if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    };

    const prevStrikerName = cards[0].querySelector(".player-name")?.textContent || "";
    const strikerSwitched = prevStrikerName && prevStrikerName !== data.striker.name;

    const renderCrest = (card, name) => {
      const crestWrap = card.querySelector(".player-crest");
      if (!crestWrap) return;
      const photo = resolvePlayerPhoto(name);
      const init = initialsOf(name);
      if (photo) {
        const curImg = crestWrap.querySelector("img");
        if (!curImg || curImg.getAttribute("src") !== photo) {
          crestWrap.innerHTML = `<img src="${photo}" alt="${name}" onerror="this.parentElement.innerHTML='<span class=\\'crest-initials\\'>${init}</span>'" />`;
        }
      } else {
        crestWrap.innerHTML = `<span class="crest-initials">${init}</span>`;
      }
    };

    const updateBatCard = (card, p, isStriker) => {
      card.querySelector(".player-name").textContent = p.name;
      renderCrest(card, p.name);
      card.querySelector(".big-num").textContent = p.runs;
      card.querySelector(".sub-num").textContent = `(${p.balls})`;
      const footers = card.querySelectorAll(".card-footer strong");
      if (footers.length >= 3) {
        footers[0].textContent = p.fours;
        footers[1].textContent = p.sixes;
        footers[2].textContent = Number(p.strike_rate).toFixed(2);
      }
      card.classList.toggle("card-striker", Boolean(isStriker));
    };

    updateBatCard(cards[0], data.striker, true);
    updateBatCard(cards[1], data.non_striker, false);

    if (strikerSwitched) {
      cards[0].classList.remove("strike-swap-left");
      cards[1].classList.remove("strike-swap-right");
      void cards[0].offsetWidth;
      cards[0].classList.add("strike-swap-left");
      cards[1].classList.add("strike-swap-right");
    }

    const bowlerCard = cards[2];
    bowlerCard.querySelector(".player-name").textContent = data.bowler.name;
    renderCrest(bowlerCard, data.bowler.name);
    bowlerCard.querySelector(".big-num").textContent = `${data.bowler.wickets}-${data.bowler.runs_conceded}`;
    bowlerCard.querySelector(".sub-num").textContent = `(${data.bowler.overs})`;
    const econEl = bowlerCard.querySelector(".card-footer strong");
    if (econEl) econEl.textContent = Number(data.bowler.economy).toFixed(2);
  }

  // Last wicket
  const lastWktEl = document.querySelector(".tag-wicket span");
  if (lastWktEl && data.last_wicket) {
    lastWktEl.textContent = `LAST WKT: ${data.last_wicket}`;
  }

  renderSlides(data);
}

function renderSlides(data) {
  // Slide 1: Batting Scorecard
  const batBody = document.querySelector("#battingTable tbody");
  if (batBody) {
    const list = (data.batters_list && data.batters_list.length)
      ? data.batters_list
      : [data.striker, data.non_striker];
    batBody.innerHTML = list.slice(0, 5).map((b) => `
      <tr class="${b.on_strike ? "is-active" : ""}">
        <td>${b.name}${b.on_strike ? " *" : ""}</td>
        <td>${b.runs}</td>
        <td>${b.balls}</td>
        <td>${b.fours}</td>
        <td>${b.sixes}</td>
        <td>${Number(b.strike_rate).toFixed(2)}</td>
      </tr>
    `).join("");
  }

  // Slide 2: Bowling Figures
  const bowlBody = document.querySelector("#bowlingTable tbody");
  if (bowlBody) {
    const list = (data.bowlers_list && data.bowlers_list.length)
      ? data.bowlers_list
      : [data.bowler];
    bowlBody.innerHTML = list.slice(0, 5).map((bw) => `
      <tr class="${bw.name === data.bowler.name ? "is-active" : ""}">
        <td>${bw.name}</td>
        <td>${bw.overs}</td>
        <td>${bw.runs_conceded}</td>
        <td>${bw.wickets}</td>
        <td>${Number(bw.economy).toFixed(2)}</td>
      </tr>
    `).join("");
  }

  // Slide 3: Over Progression & Fall of Wickets
  const overBars = document.getElementById("overBars");
  if (overBars) {
    const overs = (data.recent_overs && data.recent_overs.length)
      ? data.recent_overs
      : [data.prev_over, data.curr_over];
    const maxRuns = Math.max(12, ...overs.map((o) => o.total || 0));
    overBars.innerHTML = overs.map((ov) => {
      const pct = Math.max(10, Math.round(((ov.total || 0) / maxRuns) * 100));
      return `
        <div class="obar-col">
          <span class="obar-val">${ov.total}</span>
          <div class="obar-fill" style="height:${pct}%"></div>
          <span class="obar-lbl">OV ${ov.over_number}</span>
        </div>
      `;
    }).join("");
  }

  const fowList = document.getElementById("fowList");
  if (fowList) {
    const fows = (data.fall_of_wickets && data.fall_of_wickets.length)
      ? data.fall_of_wickets
      : [`LAST WKT: ${data.last_wicket}`];
    fowList.innerHTML = fows.slice(-4).map((f) => `<div class="fow-chip">${f}</div>`).join("");
  }

  // Slide 4: Match Center
  const infoGrid = document.getElementById("matchInfoGrid");
  if (infoGrid) {
    infoGrid.innerHTML = `
      <div class="info-tile"><div class="info-tile-lbl">MATCH</div><div class="info-tile-val">${data.match_title || `${data.batting_team} vs ${data.bowling_team}`}</div></div>
      <div class="info-tile"><div class="info-tile-lbl">LIVE STATUS</div><div class="info-tile-val">${data.callout}</div></div>
      <div class="info-tile"><div class="info-tile-lbl">PARTNERSHIP</div><div class="info-tile-val">${data.partnership}</div></div>
      <div class="info-tile"><div class="info-tile-lbl">RUN RATE</div><div class="info-tile-val">CRR ${Number(data.crr).toFixed(2)}</div></div>
    `;
  }

  // Slide 5: Win Probability
  const winBox = document.getElementById("winProbBox");
  if (winBox) {
    const batPct = Math.max(5, Math.min(95, Number(data.win_prob_batting || 50)));
    const bowlPct = 100 - batPct;
    winBox.innerHTML = `
      <div class="win-prob-labels">
        <span style="color:#f87171">${data.batting_team} ${batPct}%</span>
        <span style="color:#60a5fa">${data.bowling_team} ${bowlPct}%</span>
      </div>
      <div class="win-prob-bar">
        <div class="win-bar-bat" style="width:${batPct}%"></div>
        <div class="win-bar-bowl" style="width:${bowlPct}%"></div>
      </div>
      <div class="win-prob-note">Live momentum estimate based on current score (${data.runs}/${data.wickets}) &amp; run rate (${Number(data.crr).toFixed(2)})</div>
    `;
  }
}

// Slide Carousel Controller
const slides = document.querySelectorAll(".broadcast-slide");
const slideDots = document.querySelectorAll(".sdot");
const slideTitleEl = document.getElementById("slideTitle");
const slideBtns = document.querySelectorAll(".slide-btn");
let currentSlide = 0;
let autoSlide = true;

function showSlide(idx) {
  currentSlide = ((idx % slides.length) + slides.length) % slides.length;
  slides.forEach((s, i) => s.classList.toggle("active", i === currentSlide));
  slideDots.forEach((d, i) => d.classList.toggle("active", i === currentSlide));
  if (slideTitleEl && slides[currentSlide]) {
    slideTitleEl.textContent = slides[currentSlide].dataset.title || "";
  }
}

slideDots.forEach((dot) => {
  dot.addEventListener("click", () => {
    autoSlide = false;
    showSlide(Number(dot.dataset.slide));
  });
});

slideBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    slideBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    if (btn.dataset.slide === "auto") {
      autoSlide = true;
    } else {
      autoSlide = false;
      showSlide(Number(btn.dataset.slide));
    }
  });
});

setInterval(() => {
  if (autoSlide && slides.length > 0) {
    showSlide(currentSlide + 1);
  }
}, 12000);

function connectWebSocket() {
  if (location.protocol !== "http:" && location.protocol !== "https:") return;
  const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${wsProto}//${location.host}/ws`);
  ws.addEventListener("message", (ev) => {
    try {
      const payload = JSON.parse(ev.data);
      if (payload.type === "event_fx" && payload.event && window.triggerEventFx) {
        if (isTopLevelWindow) {
          window.triggerEventFx(payload.event, payload.subtitle || "");
          if (["FOUR", "SIX", "WICKET"].includes(String(payload.event || "").toUpperCase())) playStandaloneRoar();
        }
        return;
      }
      if (payload.type === "milestone" && window.triggerMilestoneFx) {
        if (isTopLevelWindow) {
          window.triggerMilestoneFx(payload);
          playStandaloneRoar();
        }
        return;
      }
      if (payload.type === "commentary_interrupt") {
        audioQueue.length = 0;
        if (window._activeAudioEl) {
          try { window._activeAudioEl.pause(); } catch {}
          window._activeAudioEl = null;
        }
        isPlayingAudio = false;
        return;
      }
      if (payload.type === "commentary") {
        console.log(`[${payload.speaker || "host"}]`, payload.text);
        if (commentaryEnabled && payload.audio_url) {
          const pauseMs = payload.speaker === "host" ? 180 : 320;
          audioQueue.push({ url: payload.audio_url, pauseMs });
          playNextAudio();
        }
        return;
      }
      applyLiveState(payload);
    } catch (err) {
      console.error("Invalid scoreboard payload:", err);
    }
  });
  ws.addEventListener("close", () => {
    setTimeout(connectWebSocket, 3000);
  });
}

eventButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    eventButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    setCallout(btn.dataset.event, btn.dataset.tone);
    if (["four", "six", "wicket"].includes(btn.dataset.tone) && window.triggerEventFx) {
      window.triggerEventFx(btn.dataset.event, "");
      playStandaloneRoar();
    }
  });
});

toggleTransparentBtn.addEventListener("click", () => {
  const isTransparent = broadcastFrame.classList.toggle("obs-transparent");
  toggleTransparentBtn.classList.toggle("active", isTransparent);
});

if (toggleCommentaryBtn) {
  toggleCommentaryBtn.addEventListener("click", () => {
    commentaryEnabled = !commentaryEnabled;
    toggleCommentaryBtn.classList.toggle("active", commentaryEnabled);
    toggleCommentaryBtn.textContent = commentaryEnabled
      ? "Commentary Audio: ON"
      : "Commentary Audio: OFF";
  });
}

try {
  const cached = localStorage.getItem(STATE_CACHE_KEY);
  if (cached) applyLiveState(JSON.parse(cached));
} catch {}

fetch("/api/state")
  .then((r) => (r.ok ? r.json() : null))
  .then((data) => applyLiveState(data))
  .catch(() => {});

connectWebSocket();
