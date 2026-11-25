const calloutText = document.getElementById("calloutText");
const broadcastFrame = document.getElementById("broadcastFrame");
const toggleTransparentBtn = document.getElementById("toggleTransparent");
const toggleCommentaryBtn = document.getElementById("toggleCommentary");
const eventButtons = document.querySelectorAll(".demo-btn[data-event]");

let commentaryEnabled = false;
const audioQueue = [];
let isPlayingAudio = false;

function playNextAudio() {
  if (isPlayingAudio || audioQueue.length === 0) return;
  const item = audioQueue.shift();
  const url = typeof item === "string" ? item : item.url;
  const pauseAfterMs = typeof item === "object" && item.pauseMs ? item.pauseMs : 450;

  isPlayingAudio = true;
  const audio = new Audio(url);
  const finish = () => {
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
  if (t === "BAN" || t.includes("BANGLADESH")) {
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
  if (t === "PAK" || t.includes("PAKISTAN")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="15" height="40" fill="#ffffff"/><rect x="15" width="45" height="40" fill="#01411c"/><circle cx="38" cy="20" r="8" fill="#ffffff"/><circle cx="40" cy="18" r="7" fill="#01411c"/></svg>`;
  }
  if (t === "SL" || t.includes("SRI LANKA")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#ffbe29"/><rect x="3" y="3" width="10" height="34" fill="#00534e"/><rect x="13" y="3" width="10" height="34" fill="#eb7400"/><rect x="25" y="3" width="32" height="34" fill="#8d153a"/></svg>`;
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

function applyLiveState(data) {
  if (!data) return;

  const battingName = document.querySelector(".team-batting .team-name");
  const bowlingName = document.querySelector(".team-bowling .team-name");
  if (battingName) battingName.textContent = data.batting_team;
  if (bowlingName) bowlingName.textContent = data.bowling_team;
  updateFlags(data.batting_team, data.bowling_team);

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

  setCallout(data.callout, data.callout_tone);

  // Sub-header stats
  const statItems = document.querySelectorAll(".stats-strip .stat-item strong");
  if (statItems.length >= 3) {
    statItems[0].textContent = data.partnership;
    statItems[1].textContent = Number(data.crr).toFixed(2);
    statItems[2].textContent = data.last_5_ov;
  }

  // Over-by-over tracker
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

  // Player cards: [0] non-striker, [1] striker, [2] bowler
  const cards = document.querySelectorAll(".players-grid .player-card");
  if (cards.length >= 3) {
    const initialsOf = (name) => {
      const parts = (name || "").trim().split(/\s+/).filter(Boolean);
      if (parts.length === 0) return "--";
      if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    };

    const updateBatCard = (card, p, isStriker) => {
      card.querySelector(".player-name").textContent = p.name;
      const crest = card.querySelector(".crest-initials");
      if (crest) crest.textContent = initialsOf(p.name);
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

    updateBatCard(cards[0], data.non_striker, false);
    updateBatCard(cards[1], data.striker, true);

    const bowlerCard = cards[2];
    bowlerCard.querySelector(".player-name").textContent = data.bowler.name;
    const bCrest = bowlerCard.querySelector(".crest-initials");
    if (bCrest) bCrest.textContent = initialsOf(data.bowler.name);
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
}

function connectWebSocket() {
  if (location.protocol !== "http:" && location.protocol !== "https:") return;
  const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${wsProto}//${location.host}/ws`);
  ws.addEventListener("message", (ev) => {
    try {
      const payload = JSON.parse(ev.data);
      if (payload.type === "commentary") {
        console.log(`[${payload.speaker || "host"}]`, payload.text);
        if (commentaryEnabled && payload.audio_url) {
          const pauseMs = payload.speaker === "host" ? 420 : 850;
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

fetch("/api/state")
  .then((r) => (r.ok ? r.json() : null))
  .then((data) => applyLiveState(data))
  .catch(() => {});

connectWebSocket();
