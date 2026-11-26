const pageType = document.body.dataset.page;

(function setupEmbedAndObsMode() {
  const params = new URLSearchParams(location.search);
  const isEmbed = params.get("embed") === "1" || params.get("obs") === "1" || Boolean(window.obsstudio) || window.innerWidth >= 1400;
  if (!isEmbed) return;
  document.body.classList.add("embed-mode");
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

// Inject colorful animated graphics into the 16:9 slide frame
const frameEl = document.querySelector(".page-frame");
if (frameEl && pageType !== "versus") {
  const bgMap = {
    batting: "/assets/stadium_bg.jpg",
    bowling: "/assets/stadium_bg.jpg",
    overs: "/assets/stadium_bg.jpg",
    match: "/assets/stadium_bg.jpg",
    playing11: "/assets/stadium_bg.jpg",
    info: "/assets/stadium_bg.jpg",
    partnership: "/assets/stadium_bg.jpg",
    player: "/assets/trophy_bg.jpg",
    break: "/assets/trophy_bg.jpg",
    leaders: "/assets/trophy_bg.jpg",
    toss: "/assets/trophy_bg.jpg",
    players_to_watch: "/assets/trophy_bg.jpg",
    key_battles: "/assets/stadium_bg.jpg",
    road_to_semi: "/assets/stadium_bg.jpg",
    predictions: "/assets/stadium_bg.jpg",
  };
  const bgImg = document.createElement("img");
  bgImg.className = "slide-bg-art";
  bgImg.src = bgMap[pageType] || "/assets/stadium_bg.jpg";
  bgImg.alt = "";
  frameEl.prepend(bgImg);

  if (["player", "bowling", "overs", "partnership", "break"].includes(pageType)) {
    const heroImg = document.createElement("img");
    heroImg.className = "slide-hero-art";
    heroImg.src = "/assets/cricket_action.jpg";
    heroImg.alt = "";
    frameEl.appendChild(heroImg);
  }
}

function updateHeader(data) {
  const teamEl = document.getElementById("pillTeam");
  const scoreEl = document.getElementById("pillScore");
  const oversEl = document.getElementById("pillOvers");
  if (teamEl) teamEl.textContent = `${data.batting_team} vs ${data.bowling_team}`;
  if (data.match_status === "prematch" && Number(data.runs) === 0 && String(data.overs) === "0.0") {
    if (scoreEl) scoreEl.textContent = (pageType === "toss") ? "TOSS 03:00 PM" : "PRE-MATCH";
    if (oversEl) oversEl.textContent = "03:30 PM IST";
    return;
  }
  if (scoreEl) scoreEl.textContent = `${data.runs}/${data.wickets}`;
  if (oversEl) oversEl.textContent = `OVERS ${data.overs}`;
}

let PLAYER_IMAGE_DB = {};
let __latestPageData = null;

const PLAYER_PHOTO_MAP = {
  "SOORYAVANSHI": "/assets/players/v_sooryavanshi__DBT.png",
  "SURYAVANSHI": "/assets/players/v_sooryavanshi__DBT.png",
  "TILAK": "/assets/players/tilak_varma__15Q.png",
  "KUSHAGRA": "/assets/players/k_kushagra__177.png",
  "SHEDGE": "/assets/players/s_shedge__A23.png",
  "LIYANAGE": "/assets/players/janith_liyanage__7NM.png",
  "SHAHBAZ": "/assets/players/s_ahmed__1D8.png",
  "AHMED": "/assets/players/s_ahmed__1D8.png",
  "RINKU": "/assets/players/r_singh__DR.png",
  "SINGH": "/assets/players/r_singh__DR.png",
  "ABHISHEK": "/assets/players/abhishek_sharma__1DH.png",
  "HARSHIT": "/assets/players/h_rana__8OH.png",
  "RANA": "/assets/players/h_rana__8OH.png",
  "KOTIAN": "/assets/players/t_kotian__63B.png",
  "DUBEY": "/assets/players/h_dubey__62Y.png",
  "KHAN": "/assets/players/a_khan__5SH.png",
  "MADUSHKA": "/assets/players/nishan_madushka__4XU.png",
  "RATHNAYAKE": "/assets/players/pavan_rathnayake__6UY.png",
  "VIYASKANTH": "/assets/players/vijayakanth_viyaskanth__5G5.png",
  "SAHAN": "/assets/players/wanuja_sahan__7XV.png",
  "SAMARAKOON": "/assets/players/lahiru_samarakoon__4XW.png",
  "CROOSPULLE": "/assets/players/lasith_croospulle__6UP.png",
  "JAYAWARDENA": "/assets/players/sineth_jayawardena__D1N.png",
  "DHANANJAYA": "/assets/players/nipun_dhananjaya__179.png",
  "FERNANDO": "/assets/players/ravindu_fernando__7NT.png",
  "SANKETH": "/assets/players/garuka_sanketh__D1V.png",
};

function playerPhoto(name, fallback = "/assets/batting_hero.jpg") {
  const clean = String(name || "").replace(/\((?:c|wk|vc)\)/gi, "").replace(/[^a-z0-9\s]/gi, " ").trim().toUpperCase().replace(/\s+/g, " ");
  if (clean) {
    if (PLAYER_IMAGE_DB[clean]) return PLAYER_IMAGE_DB[clean];
    const parts = clean.split(" ");
    if (parts.length >= 2) {
      const alias = `${parts[0][0]} ${parts[parts.length - 1]}`;
      if (PLAYER_IMAGE_DB[alias]) return PLAYER_IMAGE_DB[alias];
      if (PLAYER_IMAGE_DB[parts[parts.length - 1]]) return PLAYER_IMAGE_DB[parts[parts.length - 1]];
    }
    for (const [key, src] of Object.entries(PLAYER_PHOTO_MAP)) {
      if (clean.includes(key)) return src;
    }
  }
  return fallback;
}

fetch("/api/player-images")
  .then((r) => (r.ok ? r.json() : null))
  .then((d) => {
    if (d && d.images) {
      PLAYER_IMAGE_DB = d.images;
      Object.keys(sectionCache).forEach((k) => delete sectionCache[k]);
      if (__latestPageData) renderPage(__latestPageData);
    }
  })
  .catch(() => {});

function formatCountdown(targetDate) {
  const diff = Math.max(0, Math.floor((targetDate - new Date()) / 1000));
  if (diff <= 0) return null;
  const h = String(Math.floor(diff / 3600)).padStart(2, "0");
  const m = String(Math.floor((diff % 3600) / 60)).padStart(2, "0");
  const s = String(diff % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

function getIstTarget(hour, minute) {
  const now = new Date();
  const target = new Date(now);
  target.setHours(hour, minute, 0, 0);
  return target;
}

const STATE_CACHE_KEY = "cricket_live_state_v1";
const sectionCache = {};

function renderIfChanged(key, slice, fn) {
  const sig = JSON.stringify(slice);
  if (sectionCache[key] === sig) return;
  sectionCache[key] = sig;
  fn();
}

function renderPage(data) {
  if (!data) return;
  __latestPageData = data;
  try { localStorage.setItem(STATE_CACHE_KEY, JSON.stringify(data)); } catch {}
  renderIfChanged("header", [data.batting_team, data.bowling_team, data.runs, data.wickets, data.overs], () => updateHeader(data));

  if (pageType === "batting") {
    renderIfChanged("batting", [data.striker, data.batters_list], () => {
      const hName = document.getElementById("batHeroName");
      const hStat = document.getElementById("batHeroStat");
      const hImg = document.querySelector("#batHeroCard img");
      if (hName) hName.textContent = data.striker.name;
      if (hStat) hStat.textContent = `${data.striker.runs} (${data.striker.balls})`;
      if (hImg) {
        hImg.src = playerPhoto(data.striker.name, "/assets/batting_hero.jpg");
        hImg.style.objectPosition = "top center";
      }

      const tbody = document.querySelector("#battingFullTable tbody");
      if (!tbody) return;
      const list = (data.batters_list && data.batters_list.length)
        ? data.batters_list
        : [data.striker, data.non_striker];
      const maxRuns = Math.max(25, ...list.map((b) => b.runs || 0));
      tbody.innerHTML = list.map((b, idx) => {
        const pct = Math.max(4, Math.round(((b.runs || 0) / maxRuns) * 100));
        return `
        <tr class="${b.on_strike ? "active-row" : ""}" style="animation-delay:${idx * 45}ms">
          <td><div style="display:flex;align-items:center;gap:8px"><img src="${playerPhoto(b.name, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${b.name}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;object-position:top center;border:1px solid rgba(255,255,255,0.2)" /><span>${b.name}${b.on_strike ? " ★" : ""}</span></div></td>
          <td style="color:#cbd5e1;font-size:12px">${b.dismissal || (b.on_strike ? "batting" : "")}</td>
          <td><strong>${b.runs}</strong><span class="meter-track"><span class="meter-fill" style="width:${pct}%"></span></span></td>
          <td>${b.balls}</td>
          <td>${b.fours}</td>
          <td>${b.sixes}</td>
          <td>${Number(b.strike_rate).toFixed(2)}</td>
        </tr>
      `;
      }).join("");
    });
  }

  if (pageType === "bowling") {
    renderIfChanged("bowling", [data.bowler, data.bowlers_list, data.match_status], () => {
      const hName = document.getElementById("bowlHeroName");
      const hStat = document.getElementById("bowlHeroStat");
      const hImg = document.querySelector("#bowlHeroCard img");
      const heroBowler = (data.match_status === "completed" && Array.isArray(data.bowlers_list) && data.bowlers_list.length)
        ? [...data.bowlers_list].sort((a, b) => (b.wickets - a.wickets) || (a.runs_conceded - b.runs_conceded))[0]
        : data.bowler;
      if (hName) hName.textContent = heroBowler.name;
      if (hStat) hStat.textContent = `${heroBowler.wickets}-${heroBowler.runs_conceded} (${heroBowler.overs})`;
      if (hImg) {
        hImg.src = playerPhoto(heroBowler.name, "/assets/bowling_hero.jpg");
        hImg.style.objectPosition = "top center";
      }

      const tbody = document.querySelector("#bowlingFullTable tbody");
      if (!tbody) return;
      const list = (data.bowlers_list && data.bowlers_list.length)
        ? data.bowlers_list
        : [data.bowler];
      const maxRuns = Math.max(30, ...list.map((bw) => bw.runs_conceded || 0));
      tbody.innerHTML = list.map((bw, idx) => {
        const pct = Math.max(8, Math.round(((bw.runs_conceded || 0) / maxRuns) * 100));
        return `
        <tr class="${bw.name === data.bowler.name ? "active-row" : ""}" style="animation-delay:${idx * 45}ms">
          <td><div style="display:flex;align-items:center;gap:8px"><img src="${playerPhoto(bw.name, "/assets/bowling_hero.jpg")}" onerror="this.src='/assets/bowling_hero.jpg'" alt="${bw.name}" style="width:28px;height:28px;border-radius:50%;object-fit:cover;object-position:top center;border:1px solid rgba(255,255,255,0.2)" /><span>${bw.name}${bw.name === data.bowler.name ? " ●" : ""}</span></div></td>
          <td>${bw.overs}</td>
          <td>${bw.maidens ?? 0}</td>
          <td>${bw.runs_conceded}<span class="meter-track"><span class="meter-fill meter-fill-blue" style="width:${pct}%"></span></span></td>
          <td style="color:var(--gold);font-size:18px;font-weight:800">${bw.wickets}</td>
          <td>${Number(bw.economy).toFixed(2)}</td>
        </tr>
      `;
      }).join("");
    });
  }

  if (pageType === "overs") {
    const chart = document.getElementById("oversChart");
    if (chart) {
      const overs = (data.recent_overs && data.recent_overs.length)
        ? data.recent_overs
        : [data.prev_over, data.curr_over];
      const maxR = Math.max(12, ...overs.map((o) => o.total || 0));
      chart.innerHTML = overs.map((ov) => {
        const pct = Math.max(12, Math.round(((ov.total || 0) / maxR) * 100));
        return `
          <div class="bar-col">
            <span class="bar-val">${ov.total}</span>
            <div class="bar-fill" style="height:${pct}%"></div>
            <span class="bar-lbl">OV ${ov.over_number}</span>
          </div>
        `;
      }).join("");
    }
    const fowBox = document.getElementById("fowGrid");
    if (fowBox) {
      const fows = (data.fall_of_wickets && data.fall_of_wickets.length)
        ? data.fall_of_wickets
        : [`LAST WKT: ${data.last_wicket}`];
      fowBox.innerHTML = fows.map((f) => `<div class="fow-pill">${f}</div>`).join("");
    }
  }

  if (pageType === "match") {
    const titleEl = document.getElementById("matchTitle");
    if (titleEl) titleEl.textContent = data.match_title || `${data.batting_team} vs ${data.bowling_team}`;

    const cards = document.getElementById("matchCards");
    if (cards) {
      cards.innerHTML = `
        <div class="metric-card"><div class="metric-lbl">CURRENT RUN RATE</div><div class="metric-val">${Number(data.crr).toFixed(2)}</div></div>
        <div class="metric-card"><div class="metric-lbl">PARTNERSHIP</div><div class="metric-val">${data.partnership}</div></div>
        <div class="metric-card"><div class="metric-lbl">LAST 5 OVERS</div><div class="metric-val">${data.last_5_ov}</div></div>
        <div class="metric-card"><div class="metric-lbl">LAST WICKET</div><div class="metric-val" style="font-size:18px">${data.last_wicket}</div></div>
      `;
    }

    const winWrap = document.getElementById("winWrap");
    if (winWrap) {
      const batPct = Math.max(5, Math.min(95, Number(data.win_prob_batting || 50)));
      const bowlPct = 100 - batPct;
      winWrap.innerHTML = `
      <div class="win-labels">
          <span style="color:#f87171">${data.batting_team} ${batPct}%</span>
          <span style="color:#60a5fa">${data.bowling_team} ${bowlPct}%</span>
        </div>
        <div class="win-track">
          <div class="win-left" style="width:${batPct}%"></div>
          <div class="win-right" style="width:${bowlPct}%"></div>
        </div>
      `;
    }
  }

  if (pageType === "playing11") {
    const isPre = data.match_status === "prematch";
    const batTitle = document.getElementById("xiBatTitle");
    const bowlTitle = document.getElementById("xiBowlTitle");
    const batList = (data.batting_xi && data.batting_xi.length) ? data.batting_xi : [data.striker.name, data.non_striker.name];
    const bowlList = (data.bowling_xi && data.bowling_xi.length) ? data.bowling_xi : [data.bowler.name];
    if (batTitle) batTitle.textContent = `${data.batting_team} — ${isPre ? `SQUAD (${batList.length})` : "PLAYING XI"}`;
    if (bowlTitle) bowlTitle.textContent = `${data.bowling_team} — ${isPre ? `SQUAD (${bowlList.length})` : "PLAYING XI"}`;
    const batEl = document.getElementById("xiBatList");
    const bowlEl = document.getElementById("xiBowlList");
    const padXI = (arr) => {
      if (isPre && arr.length > 2) return arr.slice(0, 15);
      const copy = [...arr];
      while (copy.length < 11) copy.push(`PLAYER ${copy.length + 1}`);
      return copy.slice(0, 11);
    };
    const batXI = padXI(batList);
    const bowlXI = padXI(bowlList);

    if (batEl) {
      batEl.className = "xi-list xi-list-2col";
      batEl.innerHTML = batXI.map((n, i) => `
        <div class="xi-item" style="animation-delay:${i * 35}ms">
          <div class="xi-left">
            <div class="xi-avatar"><img src="${playerPhoto(n, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${n}" /></div>
            <span class="xi-pname"><span class="xi-num">${i + 1}.</span>${n}</span>
          </div>
          <span style="color:var(--gold);font-size:10px">${n === data.striker.name ? "★" : ""}</span>
        </div>
      `).join("");
    }
    if (bowlEl) {
      bowlEl.className = "xi-list xi-list-2col";
      bowlEl.innerHTML = bowlXI.map((n, i) => `
        <div class="xi-item" style="animation-delay:${i * 35}ms">
          <div class="xi-left">
            <div class="xi-avatar"><img src="${playerPhoto(n, "/assets/bowling_hero.jpg")}" onerror="this.src='/assets/bowling_hero.jpg'" alt="${n}" /></div>
            <span class="xi-pname"><span class="xi-num">${i + 1}.</span>${n}</span>
          </div>
          <span style="color:#60a5fa;font-size:10px">${n === data.bowler.name ? "●" : ""}</span>
        </div>
      `).join("");
    }
  }

  if (pageType === "player") {
    const box = document.getElementById("spotlightBox");
    if (box) {
      const batters = Array.isArray(data.batters_list) && data.batters_list.length ? data.batters_list : [];
      const p = (data.match_status === "completed" && batters.length)
        ? [...batters].sort((a, b) => b.runs - a.runs)[0]
        : data.striker;
      const parts = (p.name || "").trim().split(/\s+/).filter(Boolean);
      const init = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : (p.name || "--").slice(0, 2).toUpperCase();
      const milestone = data.match_status === "completed"
        ? (data.potm && data.potm.name ? `TOP SCORER • POTM: ${data.potm.name.split(" ").slice(-1)[0]}` : "TOP SCORER")
        : (p.runs >= 100 ? "CENTURY" : (p.runs >= 50 ? "HALF-CENTURY" : "AT THE CREASE"));
      box.innerHTML = `
        <div class="spotlight-photo-frame">
          <img src="${playerPhoto(p.name, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${p.name}" />
        </div>
        <div>
          <div class="page-kicker">${data.batting_team} • ${milestone}</div>
          <div class="spotlight-name">${p.name}</div>
          <div class="spotlight-score">${p.runs} <span style="font-size:38px;color:#cbd5e1">(${p.balls})</span></div>
          <div class="spotlight-stats">
            <div class="sp-stat"><span>FOURS</span><strong>${p.fours}</strong></div>
            <div class="sp-stat"><span>SIXES</span><strong>${p.sixes}</strong></div>
            <div class="sp-stat"><span>STRIKE RATE</span><strong>${Number(p.strike_rate).toFixed(2)}</strong></div>
          </div>
        </div>
      `;
    }
  }

  if (pageType === "info") {
    const grid = document.getElementById("infoCards");
    if (grid) {
      grid.innerHTML = `
        <div class="metric-card"><div class="metric-lbl">SERIES</div><div class="metric-val" style="font-size:22px">${data.series_name || "LIVE SERIES"}</div></div>
        <div class="metric-card"><div class="metric-lbl">VENUE</div><div class="metric-val" style="font-size:22px">${data.venue || "STADIUM"}</div></div>
        <div class="metric-card"><div class="metric-lbl">DATE / TIME</div><div class="metric-val" style="font-size:20px">${data.match_date || "LIVE NOW"}</div></div>
        <div class="metric-card"><div class="metric-lbl">HEAD TO HEAD</div><div class="metric-val" style="font-size:22px">${data.head_to_head || `${data.batting_team} vs ${data.bowling_team}`}</div></div>
      `;
    }
  }

  if (pageType === "partnership") {
    const photos = document.getElementById("pshipPhotos");
    if (photos) {
      photos.innerHTML = `
        <div class="pship-card">
          <img src="${playerPhoto(data.striker.name, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${data.striker.name}" />
          <div class="pship-card-overlay">
            <div>
              <div class="photo-card-tag">STRIKER</div>
              <div class="photo-card-title">${data.striker.name}</div>
            </div>
            <div class="photo-card-stat">${data.striker.runs} (${data.striker.balls})</div>
          </div>
        </div>
        <div class="pship-card">
          <img src="${playerPhoto(data.non_striker.name, "/assets/cricket_action.jpg")}" onerror="this.src='/assets/cricket_action.jpg'" alt="${data.non_striker.name}" />
          <div class="pship-card-overlay">
            <div>
              <div class="photo-card-tag">NON-STRIKER</div>
              <div class="photo-card-title">${data.non_striker.name}</div>
            </div>
            <div class="photo-card-stat">${data.non_striker.runs} (${data.non_striker.balls})</div>
          </div>
        </div>
      `;
    }
    const wrap = document.getElementById("pshipWrap");
    if (wrap) {
      const r1 = data.striker.runs || 0;
      const r2 = data.non_striker.runs || 0;
      const tot = Math.max(1, r1 + r2);
      const p1 = Math.round((r1 / tot) * 100);
      const p2 = 100 - p1;
      wrap.innerHTML = `
        <div class="win-labels" style="font-size:24px">
          <span style="color:#fb923c">${data.striker.name}: ${r1} (${data.striker.balls})</span>
          <span style="color:#facc15">${data.non_striker.name}: ${r2} (${data.non_striker.balls})</span>
        </div>
        <div class="win-track">
          <div class="win-left" style="width:${p1}%;background:linear-gradient(90deg,#ea580c,#fb923c)"></div>
          <div class="win-right" style="width:${p2}%;background:linear-gradient(90deg,#ca8a04,#facc15)"></div>
        </div>
        <div style="font-family:var(--font-ui);font-size:14px;color:#cbd5e1;text-align:center">
          Active Partnership: <strong style="color:var(--gold)">${data.partnership}</strong> • Combined Boundaries: <strong>${data.striker.fours + data.non_striker.fours} Fours, ${data.striker.sixes + data.non_striker.sixes} Sixes</strong>
        </div>
      `;
    }
  }

  if (pageType === "break") {
    const sub = document.getElementById("breakSub");
    if (sub) {
      sub.textContent = `${data.batting_team} ${data.runs}/${data.wickets} (${data.overs} ov) • ${data.callout}`;
    }
  }

  if (pageType === "leaders") {
    const topBat = document.getElementById("leadersBat");
    const topBowl = document.getElementById("leadersBowl");
    const bats = [...((data.batters_list && data.batters_list.length) ? data.batters_list : [data.striker, data.non_striker])]
      .sort((a, b) => b.runs - a.runs).slice(0, 5);
    const bowls = [...((data.bowlers_list && data.bowlers_list.length) ? data.bowlers_list : [data.bowler])]
      .sort((a, b) => b.wickets - a.wickets || a.runs_conceded - b.runs_conceded).slice(0, 5);
    if (topBat) {
      topBat.innerHTML = bats.map((b, i) => `
        <div class="xi-item" style="animation-delay:${i * 50}ms">
          <div class="xi-left">
            <div class="leader-avatar"><img src="${playerPhoto(b.name, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${b.name}" style="object-position:top center" /></div>
            <span class="xi-pname"><span class="xi-num">#${i + 1}</span>${b.name}</span>
          </div>
          <strong style="color:var(--gold);font-size:15px">${b.runs} (${b.balls})</strong>
        </div>
      `).join("");
    }
    if (topBowl) {
      topBowl.innerHTML = bowls.map((bw, i) => `
        <div class="xi-item" style="animation-delay:${i * 50}ms">
          <div class="xi-left">
            <div class="leader-avatar"><img src="${playerPhoto(bw.name, "/assets/bowling_hero.jpg")}" onerror="this.src='/assets/bowling_hero.jpg'" alt="${bw.name}" style="object-position:top center" /></div>
            <span class="xi-pname"><span class="xi-num">#${i + 1}</span>${bw.name}</span>
          </div>
          <strong style="color:#60a5fa;font-size:15px">${bw.wickets}-${bw.runs_conceded} (${bw.overs})</strong>
        </div>
      `).join("");
    }
  }

  if (pageType === "milestone") {
    const box = document.getElementById("milestoneBox");
    if (box) {
      const pool = (data.match_status === "completed" && Array.isArray(data.batters_list) && data.batters_list.length)
        ? [...data.batters_list]
        : [data.striker, data.non_striker];
      const bats = pool.sort((a, b) => b.runs - a.runs);
      const star = bats[0] || data.striker;
      const nextTarget = [50, 100, 150, 200, 250, 300].find((m) => star.runs < m) || 300;
      const prevTarget = Math.max(0, nextTarget - 50);
      const pct = Math.min(100, Math.max(5, Math.round(((star.runs - prevTarget) / 50) * 100)));
      const achieved = [300, 250, 200, 150, 100, 50].find((m) => star.runs >= m);
      const badgeLabel = achieved === 200 ? "DOUBLE CENTURY" : (achieved === 100 ? "CENTURY" : (achieved === 50 ? "HALF CENTURY" : (achieved ? `${achieved} RUNS` : `${nextTarget - star.runs} TO ${nextTarget}`)));
      box.innerHTML = `
        <div class="spotlight-photo-frame"><img src="${playerPhoto(star.name, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${star.name}" /></div>
        <div>
          <div class="page-kicker">${data.batting_team} • ${badgeLabel}</div>
          <div class="spotlight-name">${star.name}</div>
          <div class="spotlight-score">${star.runs} <span style="font-size:38px;color:#cbd5e1">(${star.balls})</span></div>
          <div style="margin-bottom:14px">
            <div style="font-family:var(--font-ui);font-size:11px;font-weight:800;color:var(--gold);margin-bottom:6px;">
              PROGRESS TO ${nextTarget}: ${star.runs}/${nextTarget} (${pct}%)
            </div>
            <div class="win-track" style="height:16px"><div class="win-left" style="width:${pct}%;background:linear-gradient(90deg,#f59e0b,#fde047)"></div></div>
          </div>
          <div class="spotlight-stats">
            <div class="sp-stat"><span>4s</span><strong>${star.fours}</strong></div>
            <div class="sp-stat"><span>6s</span><strong>${star.sixes}</strong></div>
            <div class="sp-stat"><span>SR</span><strong>${Number(star.strike_rate).toFixed(2)}</strong></div>
          </div>
        </div>
      `;
    }
  }

  if (pageType === "runrate") {
    const list = (data.batters_list && data.batters_list.length) ? data.batters_list : [data.striker, data.non_striker];
    const total4s = list.reduce((s, b) => s + (b.fours || 0), 0);
    const total6s = list.reduce((s, b) => s + (b.sixes || 0), 0);
    const boundRuns = total4s * 4 + total6s * 6;
    const otherRuns = Math.max(0, (data.runs || 0) - boundRuns);
    const total = Math.max(1, boundRuns + otherRuns);
    const bPct = Math.round((boundRuns / total) * 100);
    const oPct = 100 - bPct;
    const cards = document.getElementById("runrateCards");
    if (cards) {
      cards.innerHTML = `
        <div class="metric-card"><div class="metric-lbl">TOTAL FOURS</div><div class="metric-val">${total4s} <span style="font-size:14px;color:#94a3b8">(${total4s * 4}r)</span></div></div>
        <div class="metric-card"><div class="metric-lbl">TOTAL SIXES</div><div class="metric-val">${total6s} <span style="font-size:14px;color:#94a3b8">(${total6s * 6}r)</span></div></div>
        <div class="metric-card"><div class="metric-lbl">BOUNDARY RUNS</div><div class="metric-val">${boundRuns} <span style="font-size:14px;color:var(--gold)">(${bPct}%)</span></div></div>
        <div class="metric-card"><div class="metric-lbl">CURRENT RUN RATE</div><div class="metric-val">${Number(data.crr).toFixed(2)}</div></div>
      `;
    }
    const split = document.getElementById("boundarySplit");
    if (split) {
      split.innerHTML = `
        <div class="win-labels" style="font-size:24px">
          <span style="color:#fde047">BOUNDARIES ${boundRuns} (${bPct}%)</span>
          <span style="color:#34d399">RUNNING / EXTRAS ${otherRuns} (${oPct}%)</span>
        </div>
        <div class="win-track">
          <div class="win-left" style="width:${bPct}%;background:linear-gradient(90deg,#ca8a04,#fde047)"></div>
          <div class="win-right" style="width:${oPct}%;background:linear-gradient(90deg,#059669,#34d399)"></div>
        </div>
      `;
    }
  }
function flagSvg(teamName) {
  const t = (teamName || "").toUpperCase();
  if (t === "BAN" || t.includes("BANGLADESH")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#006a4e"/><circle cx="27" cy="20" r="11" fill="#f42a41"/></svg>`;
  }
  if (t === "SA" || t.includes("SOUTH AFRICA")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="20" fill="#e03c31"/><rect y="20" width="60" height="20" fill="#001489"/><polygon points="0,0 28,20 0,40" fill="#000"/><polyline points="0,3 24,20 0,37" fill="none" stroke="#ffb81c" stroke-width="3.5"/><path d="M0,0 L26,18 L60,18 L60,22 L26,22 L0,40" fill="none" stroke="#fff" stroke-width="6"/><path d="M0,0 L26,18 L60,18 L60,22 L26,22 L0,40" fill="none" stroke="#007749" stroke-width="4"/></svg>`;
  }
  if (t.startsWith("SL") || t.includes("SRI LANKA")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#ffbe29"/><rect x="3" y="3" width="10" height="34" fill="#00534e"/><rect x="13" y="3" width="10" height="34" fill="#eb7400"/><rect x="25" y="3" width="32" height="34" fill="#8d153a"/><circle cx="41" cy="20" r="7" fill="#ffbe29"/></svg>`;
  }
  if (t.startsWith("IND")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="13.4" fill="#ff9933"/><rect y="13.3" width="60" height="13.4" fill="#fff"/><rect y="26.6" width="60" height="13.4" fill="#138808"/><circle cx="30" cy="20" r="5" fill="none" stroke="#000080" stroke-width="1.2"/></svg>`;
  }
  if (t === "AUS" || t.includes("AUSTRALIA")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#012169"/><rect width="26" height="18" fill="#012169"/><path d="M0,0 L26,18 M26,0 L0,18" stroke="#fff" stroke-width="3"/><path d="M13,0 V18 M0,9 H26" stroke="#c8102e" stroke-width="3"/><circle cx="13" cy="29" r="3.2" fill="#fff"/><circle cx="44" cy="12" r="2.2" fill="#fff"/><circle cx="50" cy="20" r="2.2" fill="#fff"/><circle cx="42" cy="28" r="2.2" fill="#fff"/><circle cx="36" cy="19" r="2.2" fill="#fff"/></svg>`;
  }
  if (t === "ENG" || t.includes("ENGLAND")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#fff"/><rect x="26" width="8" height="40" fill="#ce1124"/><rect y="16" width="60" height="8" fill="#ce1124"/></svg>`;
  }
  if (t === "PAK" || t.includes("PAKISTAN")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="15" height="40" fill="#fff"/><rect x="15" width="45" height="40" fill="#01411c"/><circle cx="38" cy="20" r="8" fill="#fff"/><circle cx="40" cy="18" r="7" fill="#01411c"/></svg>`;
  }
  if (t === "NZ" || t.includes("NEW ZEALAND")) {
    return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#00247d"/><path d="M0,0 L24,18 M24,0 L0,18" stroke="#fff" stroke-width="2.5"/><path d="M12,0 V18 M0,9 H24" stroke="#cc142b" stroke-width="2.5"/><circle cx="45" cy="12" r="2.2" fill="#cc142b"/><circle cx="45" cy="28" r="2.2" fill="#cc142b"/><circle cx="38" cy="20" r="2" fill="#cc142b"/><circle cx="51" cy="19" r="2" fill="#cc142b"/></svg>`;
  }
  return `<svg viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#1e293b"/><text x="30" y="25" text-anchor="middle" fill="#ffd426" font-size="14" font-weight="bold" font-family="sans-serif">${t.slice(0, 3)}</text></svg>`;
}

function getTeamColors(teamName) {
  const t = (teamName || "").toUpperCase();
  if (t === "BAN" || t.includes("BANGLADESH") || t === "PAK" || t.includes("PAKISTAN")) {
    return ["#047857", "#03261c"];
  }
  if (t === "SA" || t.includes("SOUTH AFRICA")) {
    return ["#b45309", "#172554"];
  }
  if (t.startsWith("SL") || t.includes("SRI LANKA")) {
    return ["#eab308", "#1e1b4b"];
  }
  if (t.startsWith("IND") || t.includes("INDIA")) {
    return ["#1d4ed8", "#07163d"];
  }
  if (t === "AUS" || t.includes("AUSTRALIA")) {
    return ["#ca8a04", "#3b2504"];
  }
  if (t === "ENG" || t.includes("ENGLAND") || t === "UAE" || t.includes("EMIRATES")) {
    return ["#b91c1c", "#33060a"];
  }
  if (t === "NZ" || t.includes("NEW ZEALAND")) {
    return ["#334155", "#090d16"];
  }
  return ["#7c3aed", "#1e1038"];
}

function svgRing(pct, valText, subText, label, color = "#ffd426") {
  const clamped = Math.max(0, Math.min(100, Number(pct) || 0));
  const offset = +(283 - (283 * clamped) / 100).toFixed(1);
  return `
    <div class="ring-card anim-card">
      <div class="ring-wrap">
        <svg class="ring-svg" viewBox="0 0 100 100">
          <circle class="ring-bg" cx="50" cy="50" r="45"></circle>
          <circle class="ring-fg" cx="50" cy="50" r="45" stroke="${color}" style="stroke-dashoffset:${offset};"></circle>
        </svg>
        <div class="ring-center">
          <div class="ring-val">${valText}</div>
          ${subText ? `<div class="ring-sub">${subText}</div>` : ""}
        </div>
      </div>
      <div class="ring-lbl">${label}</div>
    </div>`;
}

if (pageType === "projected") {
    renderIfChanged("projected", [data.runs, data.wickets, data.overs, data.crr, data.rrr, data.target, data.fan_poll, data.batting_team, data.bowling_team], () => {
      const mBox = document.getElementById("projectedMatrixBox");
      const fBox = document.getElementById("fanPollBox");
      const oversParts = String(data.overs || "0.0").split(".");
      const ovCompleted = (parseInt(oversParts[0] || "0", 10) || 0) + ((parseInt(oversParts[1] || "0", 10) || 0) / 6);
      const isT20 = ovCompleted <= 20 && (!data.target || data.target <= 260);
      const maxOv = isT20 ? 20 : 50;
      const crr = Number(data.crr || 0);
      const rates = [crr, +(crr + 0.5).toFixed(2), +(crr + 1.5).toFixed(2), +(crr + 2.5).toFixed(2)];
      const remOv = Math.max(0, maxOv - ovCompleted);
      const finals = rates.map((r) => Math.round(data.runs + remOv * r));
      const maxVal = Math.max(...finals, 1);

      if (mBox) {
        mBox.innerHTML = `
          <div class="crex-subhead">PROJECTED ${maxOv}-OVER SCORE CHART</div>
          <div class="vchart">
            ${finals.map((score, i) => {
              const hPct = Math.max(22, Math.round((score / maxVal) * 100));
              return `
                <div class="vbar-col">
                  <div class="vbar-num">${score}</div>
                  <div class="vbar-track"><div class="vbar-fill ${i === 0 ? "alt" : ""}" style="height:${hPct}%"></div></div>
                  <div class="vbar-lbl">${rates[i].toFixed(2)}${i === 0 ? "*" : ""} RR</div>
                </div>`;
            }).join("")}
          </div>
          <div class="stat-grid-2">
            <div class="stat-box anim-card"><div class="stat-lbl">CURRENT RR</div><div class="stat-val" style="color:#38bdf8">${crr.toFixed(2)}</div></div>
            <div class="stat-box anim-card"><div class="stat-lbl">${data.target ? `TARGET ${data.target}` : "PROJECTED"}</div><div class="stat-val" style="color:var(--gold)">${data.target || finals[0]}</div></div>
          </div>`;
      }
      if (fBox) {
        const poll = data.fan_poll || { total_votes: 207850, batting_pct: data.win_prob_batting || 55, bowling_pct: 100 - (data.win_prob_batting || 55) };
        const bPct = poll.batting_pct ?? 55;
        const oPct = poll.bowling_pct ?? (100 - bPct);
        fBox.innerHTML = `
          <div class="crex-subhead">LIVE FAN POLL • ${Number(poll.total_votes || 0).toLocaleString()} VOTES</div>
          <div class="rings-row">
            ${svgRing(bPct, `${bPct}%`, data.batting_team, `${data.batting_team} WIN%`, "#38bdf8")}
            ${svgRing(oPct, `${oPct}%`, data.bowling_team, `${data.bowling_team} WIN%`, "#f59e0b")}
          </div>
          <div class="split-wrap">
            <div class="split-bar">
              <div class="split-fill-a" style="width:${bPct}%"></div>
              <div class="split-fill-b" style="width:${oPct}%"></div>
            </div>
          </div>`;
      }
    });
  }

  if (pageType === "pitch") {
    renderIfChanged("pitch", [data.venue, data.weather, data.venue_stats, data.toss], () => {
      const pw = document.getElementById("pitchWeatherBox");
      const vs = document.getElementById("venueStatsBox");
      const w = data.weather || {};
      const st = data.venue_stats || {};
      if (pw) {
        pw.innerHTML = `
          <div class="crex-subhead">CONDITIONS • ${data.venue || "STADIUM"}</div>
          <div class="weather-grid">
            <div class="weather-tile anim-card"><div class="wt-val">${w.temp || "25.5°C"}</div><div class="wt-lbl">TEMP</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${w.condition || "Clear"}</div><div class="wt-lbl">SKY</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${w.humidity || "68%"}</div><div class="wt-lbl">HUMIDITY</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${w.rain_chance || "0%"}</div><div class="wt-lbl">RAIN</div></div>
          </div>
          <div class="crex-subhead">PACE VS SPIN WICKET SHARE</div>
          <div class="rings-row">
            ${svgRing(st.pace_pct || 59, `${st.pace_pct || 59}%`, `${st.pace_wkts || 84} WKTS`, "PACE", "#38bdf8")}
            ${svgRing(st.spin_pct || 41, `${st.spin_pct || 41}%`, `${st.spin_wkts || 58} WKTS`, "SPIN", "#f59e0b")}
          </div>`;
      }
      if (vs) {
        vs.innerHTML = `
          <div class="crex-subhead">VENUE BIAS (${st.matches || 45} MATCHES)</div>
          <div class="rings-row">
            ${svgRing(st.win_bat_first || 48, `${st.win_bat_first || 48}%`, "BAT 1ST", "WIN BAT FIRST", "#22c55e")}
            ${svgRing(st.win_bowl_first || 52, `${st.win_bowl_first || 52}%`, "BOWL 1ST", "WIN CHASING", "#ffd426")}
          </div>
          <div class="stat-grid-2">
            <div class="stat-box anim-card"><div class="stat-lbl">AVG 1ST / 2ND</div><div class="stat-val">${st.avg_1st || 158} / ${st.avg_2nd || 146}</div></div>
            <div class="stat-box anim-card"><div class="stat-lbl">HIGHEST CHASED</div><div class="stat-val" style="color:#38bdf8">${st.highest_chased || "193-5"}</div></div>
            <div class="stat-box anim-card"><div class="stat-lbl">HIGHEST TOTAL</div><div class="stat-val" style="color:var(--gold)">${st.highest_total || "217-4"}</div></div>
            <div class="stat-box anim-card"><div class="stat-lbl">LOWEST TOTAL</div><div class="stat-val">${st.lowest_total || "90-10"}</div></div>
          </div>`;
      }
    });
  }

  if (pageType === "form") {
    renderIfChanged("form", [data.batting_team, data.bowling_team, data.team_form, data.team_comparison, data.recent_h2h], () => {
      const fBox = document.getElementById("teamFormBox");
      const cBox = document.getElementById("teamCompBox");
      const tf = data.team_form || { batting: ["W", "W", "L", "W", "W"], bowling: ["W", "L", "W", "W", "L"] };
      const tc = data.team_comparison || { batting: {}, bowling: {} };
      const renderBadges = (arr) => (arr || []).map((r) => {
        const cls = r === "W" ? "form-win" : r === "L" ? "form-loss" : "form-nr";
        return `<span class="form-badge ${cls}">${r}</span>`;
      }).join("");
      if (fBox) {
        fBox.innerHTML = `
          <div class="crex-subhead">LAST 5 MATCHES FORM</div>
          <div class="form-team-row anim-card">
            <span class="form-team-name">${data.batting_team}</span>
            <div class="form-badges">${renderBadges(tf.batting)}</div>
          </div>
          <div class="form-team-row anim-card">
            <span class="form-team-name">${data.bowling_team}</span>
            <div class="form-badges">${renderBadges(tf.bowling)}</div>
          </div>
          <div class="crex-subhead" style="margin-top:12px;">RECENT H2H CLASHES</div>
          ${(data.recent_h2h || []).slice(0, 3).map((h) => `
            <div class="h2h-card anim-card">
              <div><div class="h2h-match">${h.match}</div><div class="h2h-scores" style="font-size:14px;">${h.score_a} vs ${h.score_b}</div></div>
              <div class="h2h-res">${h.result}</div>
            </div>`).join("")}`;
      }
      if (cBox) {
        const a = tc.batting || {};
        const b = tc.bowling || {};
        cBox.innerHTML = `
          <div class="crex-subhead">TEAM POWER METERS</div>
          <div class="rings-row">
            ${svgRing(a.win_pct ?? 70, `${a.win_pct ?? 70}%`, data.batting_team, "WIN RATE", "#22c55e")}
            ${svgRing(b.win_pct ?? 60, `${b.win_pct ?? 60}%`, data.bowling_team, "WIN RATE", "#38bdf8")}
          </div>
          <div class="meter-row">
            <div class="meter-head"><span>AVG SCORE (${data.batting_team} ${a.avg_score ?? 150} vs ${data.bowling_team} ${b.avg_score ?? 158})</span></div>
            <div class="split-bar"><div class="split-fill-a" style="width:${Math.round(((a.avg_score ?? 150) / ((a.avg_score ?? 150) + (b.avg_score ?? 158))) * 100)}%"></div><div class="split-fill-b" style="width:${Math.round(((b.avg_score ?? 158) / ((a.avg_score ?? 150) + (b.avg_score ?? 158))) * 100)}%"></div></div>
          </div>
          <div class="stat-grid-2" style="margin-top:12px;">
            <div class="stat-box anim-card"><div class="stat-lbl">${data.batting_team} HIGH / LOW</div><div class="stat-val" style="color:var(--gold)">${a.high_score ?? 196} / ${a.low_score ?? 108}</div></div>
            <div class="stat-box anim-card"><div class="stat-lbl">${data.bowling_team} HIGH / LOW</div><div class="stat-val" style="color:#38bdf8">${b.high_score ?? 233} / ${b.low_score ?? 116}</div></div>
          </div>`;
      }
    });
  }

  if (pageType === "points") {
    renderIfChanged("points", [data.points_table, data.series_leaders, data.series_name], () => {
      const pBox = document.getElementById("pointsTableBox");
      const sBox = document.getElementById("seriesLeadersBox");
      if (pBox) {
        const rows = data.points_table || [];
        const maxPts = Math.max(...rows.map((r) => Number(r.pts || 0)), 1);
        pBox.innerHTML = `
          <div class="crex-subhead">STANDINGS • ${data.series_name || "SERIES"}</div>
          ${rows.map((r, i) => `
            <div class="meter-row anim-card">
              <div class="meter-head">
                <span><span class="rank-pill" style="margin-right:6px;">${i + 1}</span> ${r.team} (${r.w}W-${r.l}L)</span>
                <span style="color:var(--gold)">${r.pts} PTS • ${r.nrr}</span>
              </div>
              <div class="meter-track"><div class="meter-fill" style="width:${Math.max(12, Math.round((Number(r.pts || 0) / maxPts) * 100))}%;${i >= 4 ? "background:#475569;" : ""}"></div></div>
            </div>`).join("")}`;
      }
      if (sBox) {
        const ldrs = data.series_leaders || [];
        sBox.innerHTML = `
          <div class="crex-subhead">TOURNAMENT LEADERS</div>
          <div class="stat-grid-2">
            ${ldrs.map((l) => `
              <div class="stat-box anim-card">
                <div class="stat-lbl">${l.category} • ${l.team}</div>
                <div style="font-size:21px;font-weight:800;color:#fff;margin:4px 0;">${l.player}</div>
                <div class="stat-val" style="color:var(--gold);font-size:24px;">${l.value}</div>
              </div>`).join("")}
          </div>`;
      }
    });
  }

  if (pageType === "rankings") {
    renderIfChanged("rankings", [data.icc_rankings], () => {
      const tBox = document.getElementById("iccTeamsBox");
      const pBox = document.getElementById("iccPlayersBox");
      const rk = data.icc_rankings || {};
      if (tBox) {
        const odi = rk.odi_teams || [];
        const maxR = Math.max(...odi.map((t) => Number(t.rating || 0)), 1);
        tBox.innerHTML = `
          <div class="crex-subhead">ICC ODI TEAM RATINGS</div>
          ${odi.map((t) => `
            <div class="meter-row anim-card">
              <div class="meter-head"><span><span class="rank-pill" style="margin-right:6px;">#${t.rank}</span> ${t.team}</span><span style="color:var(--gold)">${t.rating}</span></div>
              <div class="meter-track"><div class="meter-fill" style="width:${Math.round((Number(t.rating || 0) / maxR) * 100)}%"></div></div>
            </div>`).join("")}`;
      }
      if (pBox) {
        pBox.innerHTML = `
          <div class="crex-subhead">ICC TOP PLAYERS</div>
          <div class="stat-grid-2" style="margin-bottom:14px;">
            ${(rk.top_players || []).map((pl) => `
              <div class="stat-box anim-card">
                <div class="stat-lbl">${pl.role} • ${pl.team}</div>
                <div style="font-size:20px;font-weight:800;color:#fff;margin:4px 0;">${pl.name}</div>
                <div class="stat-val" style="color:#38bdf8;font-size:24px;">${pl.rating}</div>
              </div>`).join("")}
          </div>
          <div class="crex-subhead">ICC T20I TOP TEAMS</div>
          <div style="display:flex;flex-wrap:wrap;gap:8px;">
            ${(rk.t20_teams || []).map((t) => `<span class="nav-link" style="cursor:default;">#${t.rank} ${t.team} • <strong style="color:var(--gold)">${t.rating}</strong></span>`).join("")}
          </div>`;
      }
    });
  }

  if (pageType === "prematch") {
    renderIfChanged("prematch", [data.batting_team, data.bowling_team, data.match_date, data.venue, data.weather, data.team_form, data.team_comparison, data.head_to_head], () => {
      const heroBox = document.getElementById("prematchHeroBox");
      const briefBox = document.getElementById("prematchBriefBox");
      const kicker = document.getElementById("prematchKicker");
      if (kicker) kicker.textContent = `PRE-MATCH SHOW • ${(data.series_name || "ASIA CUP RISING STARS 2026").toUpperCase()}`;
      const w = data.weather || {};
      const cmp = data.team_comparison || {};
      const t1 = data.batting_team || "SL-A";
      const t2 = data.bowling_team || "IND-A";
      const formA = (data.team_form && data.team_form.batting) ? data.team_form.batting : ["W", "W", "W", "L", "W"];
      const formB = (data.team_form && data.team_form.bowling) ? data.team_form.bowling : ["W", "L", "W", "W", "L"];

      if (heroBox) {
        heroBox.innerHTML = `
          <div class="crex-subhead">SEMI-FINAL SHOWDOWN • ${data.match_date || "TODAY 03:30 PM"}</div>
          <div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:14px;padding:14px;border-radius:14px;background:rgba(15,23,42,0.72);border:1px solid rgba(255,255,255,0.1)">
            <div style="display:flex;align-items:center;gap:12px">
              <div style="width:64px;height:42px;border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.2)">${flagSvg(t1)}</div>
              <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:38px;font-weight:800;line-height:1">${t1}</div>
                <div style="font-size:11px;color:#94a3b8;margin-top:4px">${formA.map((r) => `<span style="display:inline-block;padding:1px 5px;border-radius:4px;margin-right:2px;font-weight:800;background:${r === "W" ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)"};color:${r === "W" ? "#4ade80" : "#f87171"}">${r}</span>`).join("")}</div>
              </div>
            </div>
            <div style="text-align:center">
              <div style="font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;color:var(--gold)">VS</div>
              <div style="font-size:11px;color:#cbd5e1;font-weight:700">${data.head_to_head || "SL-A 1 - 2 IND-A"}</div>
            </div>
            <div style="display:flex;align-items:center;justify-content:flex-end;gap:12px;text-align:right">
              <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:38px;font-weight:800;line-height:1">${t2}</div>
                <div style="font-size:11px;color:#94a3b8;margin-top:4px">${formB.map((r) => `<span style="display:inline-block;padding:1px 5px;border-radius:4px;margin-right:2px;font-weight:800;background:${r === "W" ? "rgba(34,197,94,0.2)" : "rgba(239,68,68,0.2)"};color:${r === "W" ? "#4ade80" : "#f87171"}">${r}</span>`).join("")}</div>
              </div>
              <div style="width:64px;height:42px;border-radius:8px;overflow:hidden;border:1px solid rgba(255,255,255,0.2)">${flagSvg(t2)}</div>
            </div>
          </div>
          <div style="margin-top:12px;padding:14px 16px;border-radius:14px;background:linear-gradient(135deg,rgba(245,158,11,0.16),rgba(59,130,246,0.16));border:1px solid rgba(245,158,11,0.35);display:grid;grid-template-columns:1fr auto auto;align-items:center;gap:16px">
            <div>
              <div style="font-size:11px;letter-spacing:1.4px;color:#fcd34d;font-weight:800">MATCHDAY LIVE COUNTDOWN (IST)</div>
              <div style="font-size:13px;color:#e2e8f0;margin-top:2px">${data.venue || "West End Park International Cricket Stadium, Doha"}</div>
            </div>
            <div style="text-align:right">
              <div style="font-size:10px;letter-spacing:1.2px;color:#93c5fd;font-weight:800">TOSS 03:00 PM</div>
              <div id="prematchTossCountdown" style="font-family:'Barlow Condensed',sans-serif;font-size:32px;font-weight:800;color:#fde047;letter-spacing:1px">--:--:--</div>
            </div>
            <div style="text-align:right;padding-left:14px;border-left:1px solid rgba(255,255,255,0.16)">
              <div style="font-size:10px;letter-spacing:1.2px;color:#93c5fd;font-weight:800">1ST BALL 03:30 PM</div>
              <div id="prematchCountdown" style="font-family:'Barlow Condensed',sans-serif;font-size:34px;font-weight:800;color:#fff;letter-spacing:1px">--:--:--</div>
            </div>
          </div>
          <div class="weather-grid" style="margin-top:12px">
            <div class="weather-tile anim-card"><div class="wt-val">${w.temp || "25°C"}</div><div class="wt-lbl">TEMP</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${w.condition || "Clear"}</div><div class="wt-lbl">SKY</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${w.humidity || "69%"}</div><div class="wt-lbl">HUMIDITY</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${w.rain_chance || "1%"}</div><div class="wt-lbl">RAIN</div></div>
          </div>`;
      }
      if (briefBox) {
        const bcast = cmp.broadcast || "Sony Sports TEN Network, Sony LIV";
        briefBox.innerHTML = `
          <div class="crex-subhead">PRE-MATCH TALKING POINTS &amp; BROADCAST</div>
          <div class="info-list" style="display:grid;gap:10px">
            <div class="tp-card anim-card"><span class="tp-tag">FORM</span><div><strong>Unbeaten ${t1} vs Explosive ${t2}</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">${t1} topped Group A (3/3 Wins, NRR +2.512). ${t2} carry +3.523 NRR firepower.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">PITCH</span><div><strong>50/50 Pace vs Spin in Doha</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Last 10 matches: Pace 50% (72 wkts) vs Spin 50% (73 wkts). Surface slows in 2nd innings.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">STARS</span><div><strong>Batters vs Spin Battle</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Tilak Varma, Vaibhav Sooryavanshi &amp; Rinku Singh face Pavan Rathnayake &amp; Wanuja Sahan.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">LIVE TV</span><div><strong>${bcast}</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Toss at 03:00 PM • First Ball at 03:30 PM IST</div></div></div>
          </div>`;
      }
      if (!window.__prematchTimer) {
        const tick = () => {
          const el = document.getElementById("prematchCountdown");
          const tossEl = document.getElementById("prematchTossCountdown");
          const matchCd = formatCountdown(getIstTarget(15, 30));
          const tossCd = formatCountdown(getIstTarget(15, 0));
          if (el) el.textContent = matchCd || "LIVE NOW";
          if (tossEl) tossEl.textContent = tossCd || "TOSS LIVE";
        };
        tick();
        window.__prematchTimer = setInterval(tick, 1000);
      }
    });
  }

  if (pageType === "toss") {
    renderIfChanged("toss", [data.batting_team, data.bowling_team, data.toss, data.venue, data.venue_stats, data.weather, data.umpires, data.series_name], () => {
      const heroBox = document.getElementById("tossHeroBox");
      const impactBox = document.getElementById("tossImpactBox");
      const kicker = document.getElementById("tossKicker");
      const titleEl = document.getElementById("tossTitle");
      if (kicker) kicker.textContent = `COIN TOSS • ${(data.series_name || "ASIA CUP RISING STARS 2026").toUpperCase()}`;

      const t1 = data.batting_team || "IND-A";
      const t2 = data.bowling_team || "SL-A";
      const tossText = String(data.toss || "TOSS COMING UP SOON").trim();
      const tossUpper = tossText.toUpperCase();
      const hasResult = tossUpper.includes("WON THE TOSS") || tossUpper.includes("CHOSE") || tossUpper.includes("ELECTED") || tossUpper.includes("OPTED");
      const batFirst = tossUpper.includes("BAT");
      const vs = data.venue_stats || {};
      const batPct = Number(vs.win_bat_first ?? 42);
      const bowlPct = Number(vs.win_bowl_first ?? 58);
      const w = data.weather || {};
      const ump = data.umpires || {};

      if (titleEl) titleEl.textContent = hasResult ? "TOSS RESULT & TACTICAL CALL" : "TOSS CENTER & PITCH DECISION";

      if (heroBox) {
        const capA = t1.includes("IND") ? "TILAK VARMA (C)" : "PAVAN RATHNAYAKE (C)";
        const capB = t2.includes("SL") ? "PAVAN RATHNAYAKE (C)" : "TILAK VARMA (C)";
        const bannerHtml = hasResult
          ? `<div class="toss-winner-banner anim-card">
               <div style="font-size:11px;letter-spacing:1.4px;color:#fde047;font-weight:800">OFFICIAL TOSS UPDATE</div>
               <div style="font-family:'Barlow Condensed',sans-serif;font-size:32px;font-weight:800;color:#fff;line-height:1.08;margin-top:4px">${tossUpper}</div>
               <span class="toss-decision-badge">${batFirst ? "BATTING FIRST • SETTING A TARGET" : "BOWLING FIRST • CHASING UNDER LIGHTS"}</span>
             </div>`
          : `<div class="toss-coin-stage anim-card">
               <div class="toss-coin">TOSS</div>
               <div style="flex:1">
                 <div style="font-size:11px;letter-spacing:1.4px;color:#fde047;font-weight:800">TOSS COMING UP • 03:00 PM IST</div>
                 <div style="font-family:'Barlow Condensed',sans-serif;font-size:30px;font-weight:800;color:#fff;line-height:1.05;margin-top:2px">${tossUpper}</div>
                 <div style="font-size:12px;color:#cbd5e1;margin-top:4px">${data.venue || "West End Park International Cricket Stadium, Doha"}</div>
               </div>
               <div style="text-align:right;padding-left:12px;border-left:1px solid rgba(255,255,255,0.14)">
                 <div style="font-size:10px;letter-spacing:1.2px;color:#93c5fd;font-weight:800">TOSS IN</div>
                 <div id="tossCountdown" style="font-family:'Barlow Condensed',sans-serif;font-size:34px;font-weight:800;color:#fde047;letter-spacing:1px">--:--:--</div>
               </div>
             </div>`;

        heroBox.innerHTML = `
          <div class="crex-subhead">CAPTAINS AT THE MIDDLE • ${t1} VS ${t2}</div>
          ${bannerHtml}
          <div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;margin-top:12px;padding:12px 14px;border-radius:12px;background:rgba(15,23,42,0.72);border:1px solid rgba(255,255,255,0.1)">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:52px;height:34px;border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,0.2)">${flagSvg(t1)}</div>
              <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:26px;font-weight:800;line-height:1">${t1}</div>
                <div style="font-size:11px;color:#93c5fd;font-weight:700">${capA}</div>
              </div>
            </div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:22px;font-weight:800;color:var(--gold)">VS</div>
            <div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;text-align:right">
              <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:26px;font-weight:800;line-height:1">${t2}</div>
                <div style="font-size:11px;color:#fde047;font-weight:700">${capB}</div>
              </div>
              <div style="width:52px;height:34px;border-radius:6px;overflow:hidden;border:1px solid rgba(255,255,255,0.2)">${flagSvg(t2)}</div>
            </div>
          </div>
          <div class="weather-grid" style="margin-top:12px">
            <div class="weather-tile anim-card"><div class="wt-val">${w.temp || "25°C"}</div><div class="wt-lbl">TEMP</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${w.humidity || "69%"}</div><div class="wt-lbl">HUMIDITY</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${vs.avg_1st || 158}</div><div class="wt-lbl">AVG 1ST INN</div></div>
            <div class="weather-tile anim-card"><div class="wt-val">${vs.highest_chased || "193-5"}</div><div class="wt-lbl">HIGH CHASED</div></div>
          </div>`;
      }

      if (impactBox) {
        impactBox.innerHTML = `
          <div class="crex-subhead">DOHA TOSS BIAS &amp; TACTICAL IMPACT</div>
          <div class="anim-card" style="padding:12px 14px;border-radius:12px;background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.1);margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;font-weight:800;font-size:14px;margin-bottom:6px">
              <span style="color:#60a5fa">BAT FIRST WIN: ${batPct}%</span>
              <span style="color:#fde047">BOWL FIRST WIN: ${bowlPct}%</span>
            </div>
            <div class="split-bar" style="height:12px">
              <div class="split-fill-a" style="width:${batPct}%"></div>
              <div class="split-fill-b" style="width:${bowlPct}%"></div>
            </div>
            <div style="font-size:12px;color:#cbd5e1;margin-top:6px">Last ${vs.matches || 45} matches at venue • Pace ${vs.pace_pct ?? 50}% vs Spin ${vs.spin_pct ?? 50}%</div>
          </div>
          <div class="info-list" style="display:grid;gap:9px">
            <div class="tp-card anim-card"><span class="tp-tag">DEW</span><div><strong>Evening Dew &amp; Chasing Advantage</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Chasing sides hold a ${bowlPct}% win edge in Doha as the ball skids onto the bat under lights.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">PITCH</span><div><strong>1st Innings Par Score: ${vs.avg_1st || 158}–${Number(vs.avg_1st || 158) + 20}</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Highest total ${vs.highest_total || "217-4"} • Spinners tighten middle overs once the new-ball shine fades.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">OFFICIALS</span><div><strong>Match Officials on Duty</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Umpires: ${ump.on_field || "Ahmad Shah Pakteen, Martin Saggers"} • Referee: ${ump.referee || "Roshan Mahanama"}</div></div></div>
          </div>`;
      }
      if (!window.__tossTimer) {
        const tickToss = () => {
          const el = document.getElementById("tossCountdown");
          if (el) el.textContent = formatCountdown(getIstTarget(15, 0)) || "TOSS LIVE";
        };
        tickToss();
        window.__tossTimer = setInterval(tickToss, 1000);
      }
    });
  }

  if (pageType === "key_battles") {
    renderIfChanged("key_battles", [data.batting_team, data.bowling_team, data.series_leaders], () => {
      const leftBox = document.getElementById("battlesLeftBox");
      const rightBox = document.getElementById("battlesRightBox");
      const t1 = data.batting_team || "IND-A";
      const t2 = data.bowling_team || "SL-A";
      const battlesA = [
        { title: "POWERPLAY FIREWORKS", p1: "V SOORYAVANSHI", r1: "241 Runs • 245.92 SR • 29 Sixes", p2: "L SAMARAKOON", r2: "New-Ball Pace & Seam", pct: 64 },
        { title: "CAPTAINS' TACTICAL DUEL", p1: "TILAK VARMA (C)", r1: "Left-Hand Anchor & Spin Hitter", p2: "V VIYASKANTH", r2: "Wrist-Spin Control (Middle Overs)", pct: 56 },
      ];
      const battlesB = [
        { title: "DEATH OVERS SHOWDOWN", p1: "RINKU SINGH", r1: "Finisher • Boundary Hitter", p2: "W SAHAN", r2: "Left-Arm Spin & Variations", pct: 58 },
        { title: "PACE VS TOP ORDER", p1: "HARSHIT RANA", r1: "140+ kmph • Hit-the-Deck", p2: "N MADUSHKA", r2: "Attacking SL-A Opener", pct: 54 },
      ];
      const renderBattleList = (heading, items) => `
        <div class="crex-subhead">${heading}</div>
        <div style="display:grid;gap:12px;margin-top:8px">
          ${items.map((b, idx) => `
            <div class="battle-card anim-card" style="animation-delay:${idx * 70}ms">
              <div style="font-size:10px;letter-spacing:1.3px;color:var(--gold);font-weight:800;margin-bottom:6px">${b.title}</div>
              <div class="battle-vs-row">
                <div style="display:flex;align-items:center;gap:10px">
                  <img src="${playerPhoto(b.p1, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${b.p1}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:1.5px solid #60a5fa;flex-shrink:0" />
                  <div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:24px;font-weight:800;color:#93c5fd;line-height:1">${b.p1}</div>
                    <div style="font-size:11px;color:#cbd5e1;margin-top:2px">${b.r1}</div>
                  </div>
                </div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:20px;font-weight:800;color:var(--gold);padding:4px 10px;border-radius:999px;background:rgba(255,212,38,0.12);border:1px solid rgba(255,212,38,0.35)">VS</div>
                <div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;text-align:right">
                  <div>
                    <div style="font-family:'Barlow Condensed',sans-serif;font-size:24px;font-weight:800;color:#fde047;line-height:1">${b.p2}</div>
                    <div style="font-size:11px;color:#cbd5e1;margin-top:2px">${b.r2}</div>
                  </div>
                  <img src="${playerPhoto(b.p2, "/assets/bowling_hero.jpg")}" onerror="this.src='/assets/bowling_hero.jpg'" alt="${b.p2}" style="width:44px;height:44px;border-radius:50%;object-fit:cover;border:1.5px solid #fde047;flex-shrink:0" />
                </div>
              </div>
              <div class="split-bar" style="height:8px;margin-top:10px">
                <div class="split-fill-a" style="width:${b.pct}%"></div>
                <div class="split-fill-b" style="width:${100 - b.pct}%"></div>
              </div>
            </div>`).join("")}
        </div>`;
      if (leftBox) leftBox.innerHTML = renderBattleList(`${t1} BATTING VS ${t2} BOWLING`, battlesA);
      if (rightBox) rightBox.innerHTML = renderBattleList(`FINISHING &amp; NEW-BALL DUELS`, battlesB);
    });
  }

  if (pageType === "road_to_semi") {
    renderIfChanged("road_to_semi", [data.batting_team, data.bowling_team, data.team_form, data.points_table, data.series_leaders], () => {
      const boxA = document.getElementById("roadTeamABox");
      const boxB = document.getElementById("roadTeamBBox");
      const t1 = data.batting_team || "IND-A";
      const t2 = data.bowling_team || "SL-A";
      const formA = (data.team_form && data.team_form.batting) ? data.team_form.batting : ["W", "L", "W", "W", "L"];
      const formB = (data.team_form && data.team_form.bowling) ? data.team_form.bowling : ["W", "W", "W", "L", "W"];

      if (boxA) {
        boxA.innerHTML = `
          <div class="crex-subhead">${t1} • SEMI-FINAL JOURNEY</div>
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:12px;background:rgba(37,99,235,0.16);border:1px solid rgba(96,165,250,0.35);margin-bottom:10px">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:52px;height:34px;border-radius:6px;overflow:hidden">${flagSvg(t1)}</div>
              <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;line-height:1">${t1}</div>
                <div style="font-size:11px;color:#93c5fd;font-weight:700">GROUP STAGE NRR +3.523 • HIGH-OCTANE BATTING</div>
              </div>
            </div>
            <div>${formA.map((r) => `<span style="display:inline-block;padding:2px 6px;border-radius:4px;margin-left:3px;font-weight:800;font-size:11px;background:${r === "W" ? "rgba(34,197,94,0.22)" : "rgba(239,68,68,0.22)"};color:${r === "W" ? "#4ade80" : "#f87171"}">${r}</span>`).join("")}</div>
          </div>
          <div style="display:grid;gap:9px">
            <div class="tp-card anim-card"><span class="tp-tag">RUNS</span><div><strong>V Sooryavanshi: 241 Runs (SR 245.92)</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">29 sixes in the tournament — fastest scoring opener in Asia Cup Rising Stars 2026.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">PACE</span><div><strong>Prince Yadav &amp; Harshit Rana</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Prince Yadav leads IND-A bowling with 7 wickets; Harshit brings raw pace.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">DEPTH</span><div><strong>Tilak Varma, Abhishek, Rinku Singh</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Explosive top-to-finish batting lineup capable of chasing or setting 200+.</div></div></div>
          </div>`;
      }

      if (boxB) {
        boxB.innerHTML = `
          <div class="crex-subhead">${t2} • UNBEATEN GROUP A TOPPERS</div>
          <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-radius:12px;background:rgba(245,158,11,0.16);border:1px solid rgba(250,204,21,0.35);margin-bottom:10px">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:52px;height:34px;border-radius:6px;overflow:hidden">${flagSvg(t2)}</div>
              <div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;line-height:1">${t2}</div>
                <div style="font-size:11px;color:#fde047;font-weight:700">3/3 WINS • 6 PTS • NRR +2.512</div>
              </div>
            </div>
            <div>${formB.map((r) => `<span style="display:inline-block;padding:2px 6px;border-radius:4px;margin-left:3px;font-weight:800;font-size:11px;background:${r === "W" ? "rgba(34,197,94,0.22)" : "rgba(239,68,68,0.22)"};color:${r === "W" ? "#4ade80" : "#f87171"}">${r}</span>`).join("")}</div>
          </div>
          <div style="display:grid;gap:9px">
            <div class="tp-card anim-card"><span class="tp-tag">STREAK</span><div><strong>Unbeaten in Group A (3 Wins, 0 Losses)</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Topped Group A ahead of Bangladesh A (+2.512 NRR) with disciplined bowling.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">SPIN</span><div><strong>Wanuja Sahan &amp; V Viyaskanth</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Twin spin threat tailor-made for Doha's 50% spin-friendly middle overs.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">LEADER</span><div><strong>Pavan Rathnayake &amp; N Madushka</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Composed top order backed by all-rounders Janith Liyanage &amp; L Samarakoon.</div></div></div>
          </div>`;
      }
    });
  }

  if (pageType === "players_to_watch") {
    renderIfChanged("players_to_watch", [data.batting_team, data.bowling_team], () => {
      const boxA = document.getElementById("watchTeamABox");
      const boxB = document.getElementById("watchTeamBBox");
      const t1 = data.batting_team || "IND-A";
      const t2 = data.bowling_team || "SL-A";
      const indStars = [
        { name: "VAIBHAV SOORYAVANSHI", role: "EXPLOSIVE OPENER", stat: "241 RUNS • 245.92 SR", note: "29 sixes in the series — sets the tone inside the powerplay." },
        { name: "TILAK VARMA (C)", role: "CAPTAIN & ANCHOR", stat: "MIDDLE-ORDER ENGINE", note: "Controls spin in the middle overs and accelerates at the death." },
        { name: "PRINCE YADAV", role: "STRIKE BOWLER", stat: "7 WICKETS IN SERIES", note: "IND-A's leading wicket-taker with incisive new-ball & death spells." },
      ];
      const slStars = [
        { name: "PAVAN RATHNAYAKE (C)", role: "CAPTAIN & BATTER", stat: "3/3 GROUP WINS", note: "Calm tactical leader anchoring Sri Lanka A's unbeaten run." },
        { name: "NISHAN MADUSHKA", role: "WK • OPENER", stat: "POWERPLAY ATTACKER", note: "Aggressive stroke-maker who thrives against pace upfront." },
        { name: "WANUJA SAHAN", role: "ALL-ROUNDER", stat: "LEFT-ARM SPIN & BAT", note: "Crucial middle-overs wicket-taker on Doha's turning surface." },
      ];
      const renderWatch = (team, stars, accent) => `
        <div class="crex-subhead">${team} • KEY X-FACTORS</div>
        <div style="display:grid;gap:11px;margin-top:8px">
          ${stars.map((s, idx) => `
            <div class="watch-card anim-card" style="animation-delay:${idx * 70}ms">
              <div style="display:flex;align-items:center;gap:12px">
                <img src="${playerPhoto(s.name, team.includes("IND") ? "/assets/batting_hero.jpg" : "/assets/bowling_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${s.name}" style="width:52px;height:52px;border-radius:50%;object-fit:cover;border:2px solid ${accent};flex-shrink:0" />
                <div>
                  <span class="watch-role-tag">${s.role}</span>
                  <div style="font-family:'Barlow Condensed',sans-serif;font-size:25px;font-weight:800;color:${accent};margin-top:4px;line-height:1">${s.name}</div>
                  <div style="font-size:12px;color:#cbd5e1;margin-top:4px">${s.note}</div>
                </div>
              </div>
              <div style="text-align:right;flex-shrink:0">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:18px;font-weight:800;color:#fff;padding:6px 10px;border-radius:8px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12)">${s.stat}</div>
              </div>
            </div>`).join("")}
        </div>`;
      if (boxA) boxA.innerHTML = renderWatch(t1, t1.includes("IND") ? indStars : slStars, "#93c5fd");
      if (boxB) boxB.innerHTML = renderWatch(t2, t2.includes("SL") ? slStars : indStars, "#fde047");
    });
  }

  if (pageType === "predictions") {
    renderIfChanged("predictions", [data.batting_team, data.bowling_team, data.win_prob_batting, data.fan_poll, data.umpires, data.team_comparison], () => {
      const leftBox = document.getElementById("predLeftBox");
      const rightBox = document.getElementById("predRightBox");
      const t1 = data.batting_team || "IND-A";
      const t2 = data.bowling_team || "SL-A";
      const wpA = Number(data.win_prob_batting ?? 62);
      const wpB = Math.max(0, 100 - wpA);
      const fp = data.fan_poll || {};
      const fpA = Number(fp.batting_pct ?? 62);
      const fpB = Number(fp.bowling_pct ?? 38);
      const bcast = (data.team_comparison && data.team_comparison.broadcast) ? data.team_comparison.broadcast : "Sony Sports TEN Network, Sony LIV";

      if (leftBox) {
        leftBox.innerHTML = `
          <div class="crex-subhead">PRE-MATCH WIN PREDICTOR &amp; FAN POLL</div>
          <div class="anim-card" style="padding:14px;border-radius:12px;background:rgba(15,23,42,0.72);border:1px solid rgba(255,255,255,0.1);margin-bottom:12px">
            <div style="font-size:11px;letter-spacing:1.2px;color:#94a3b8;font-weight:800;margin-bottom:6px">AI WIN PROBABILITY MODEL</div>
            <div style="display:flex;justify-content:space-between;font-family:'Barlow Condensed',sans-serif;font-size:28px;font-weight:800;margin-bottom:6px">
              <span style="color:#60a5fa">${t1} ${wpA}%</span>
              <span style="color:#fde047">${wpB}% ${t2}</span>
            </div>
            <div class="split-bar" style="height:14px">
              <div class="split-fill-a" style="width:${wpA}%"></div>
              <div class="split-fill-b" style="width:${wpB}%"></div>
            </div>
          </div>
          <div class="anim-card" style="padding:14px;border-radius:12px;background:rgba(15,23,42,0.72);border:1px solid rgba(255,255,255,0.1);margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;font-size:11px;letter-spacing:1.2px;color:#94a3b8;font-weight:800;margin-bottom:6px">
              <span>LIVE FAN POLL</span>
              <span style="color:var(--gold)">${Number(fp.total_votes || 230523).toLocaleString()} VOTES</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-family:'Barlow Condensed',sans-serif;font-size:24px;font-weight:800;margin-bottom:6px">
              <span style="color:#60a5fa">${t1} ${fpA}%</span>
              <span style="color:#fde047">${fpB}% ${t2}</span>
            </div>
            <div class="split-bar" style="height:12px">
              <div class="split-fill-a" style="width:${fpA}%"></div>
              <div class="split-fill-b" style="width:${fpB}%"></div>
            </div>
          </div>
          <div class="tp-card anim-card"><span class="tp-tag">TV / OTT</span><div><strong>${bcast}</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Live from West End Park International Cricket Stadium, Doha</div></div></div>`;
      }

      if (rightBox) {
        rightBox.innerHTML = `
          <div class="crex-subhead">MATCHDAY BROADCAST SCHEDULE (IST)</div>
          <div style="display:grid;gap:10px;margin-top:8px">
            <div class="timeline-row anim-card"><span class="timeline-time">02:30 PM</span><div><strong>Pre-Match Build-Up &amp; Pitch Report</strong><div style="font-size:12px;color:#cbd5e1">Squad analysis, Doha surface check &amp; key battles.</div></div></div>
            <div class="timeline-row anim-card"><span class="timeline-time">03:00 PM</span><div><strong>Official Coin Toss &amp; Playing XI</strong><div style="font-size:12px;color:#cbd5e1">Captains Tilak Varma &amp; Pavan Rathnayake at the middle.</div></div></div>
            <div class="timeline-row anim-card"><span class="timeline-time">03:30 PM</span><div><strong>First Ball • 1st Semi-Final Begins</strong><div style="font-size:12px;color:#cbd5e1">Live ball-by-ball commentary &amp; real-time overlays.</div></div></div>
            <div class="timeline-row anim-card"><span class="timeline-time">POST</span><div><strong>Semi-Final Winner Advances to Final</strong><div style="font-size:12px;color:#cbd5e1">Full match report, Player of the Match &amp; reaction.</div></div></div>
          </div>`;
      }
    });
  }

  if (pageType === "comparison") {
    renderIfChanged("comparison", [data.batting_team, data.bowling_team, data.team_comparison, data.points_table], () => {
      const barsBox = document.getElementById("compBarsBox");
      const starsBox = document.getElementById("compStarsBox");
      const cmp = data.team_comparison || {};
      const t1 = data.batting_team || "SL-A";
      const t2 = data.bowling_team || "IND-A";
      const rows = [
        { lbl: "WIN RATE (LAST 10)", a: cmp.win_left || "80%", b: cmp.win_right || "50%", av: parseInt(cmp.win_left || "80", 10) || 80, bv: parseInt(cmp.win_right || "50", 10) || 50 },
        { lbl: "AVERAGE SCORE", a: cmp.avg_left || "264", b: cmp.avg_right || "279", av: parseInt(cmp.avg_left || "264", 10) || 264, bv: parseInt(cmp.avg_right || "279", 10) || 279 },
        { lbl: "HIGHEST SCORE", a: cmp.high_left || "368", b: cmp.high_right || "377", av: parseInt(cmp.high_left || "368", 10) || 368, bv: parseInt(cmp.high_right || "377", 10) || 377 },
        { lbl: "LOWEST SCORE", a: cmp.low_left || "144", b: cmp.low_right || "149", av: parseInt(cmp.low_left || "144", 10) || 144, bv: parseInt(cmp.low_right || "149", 10) || 149 },
      ];
      if (barsBox) {
        barsBox.innerHTML = `
          <div class="crex-subhead">${t1} VS ${t2} • OVERALL COMPARISON (LAST 10)</div>
          <div style="display:grid;gap:14px;margin-top:8px">
            ${rows.map((r) => {
              const tot = Math.max(r.av + r.bv, 1);
              const ap = Math.round((r.av / tot) * 100);
              const bp = 100 - ap;
              return `
                <div class="anim-card" style="padding:10px 12px;border-radius:12px;background:rgba(15,23,42,0.65);border:1px solid rgba(255,255,255,0.08)">
                  <div style="display:flex;justify-content:space-between;font-weight:800;font-size:15px;margin-bottom:6px">
                    <span style="color:${t1.includes("IND") ? "#60a5fa" : "#facc15"}">${t1}: ${r.a}</span>
                    <span style="font-size:11px;letter-spacing:1.2px;color:#94a3b8">${r.lbl}</span>
                    <span style="color:${t2.includes("IND") ? "#60a5fa" : "#facc15"}">${r.b} :${t2}</span>
                  </div>
                  <div class="split-bar" style="height:12px">
                    <div class="${t1.includes("IND") ? "split-fill-a" : "split-fill-b"}" style="width:${ap}%"></div>
                    <div class="${t2.includes("IND") ? "split-fill-a" : "split-fill-b"}" style="width:${bp}%"></div>
                  </div>
                </div>`;
            }).join("")}
          </div>`;
      }
      if (starsBox) {
        const slStars = [
          { name: "PAVAN RATHNAYAKE (C)", role: "Top-Order Anchor" },
          { name: "NISHAN MADUSHKA (WK)", role: "Attacking Opener" },
          { name: "WANUJA SAHAN", role: "Left-Arm Spin & Bat" },
          { name: "VIJAYAKANTH VIYASKANTH", role: "Wrist-Spin Threat" },
        ];
        const indStars = [
          { name: "TILAK VARMA (C)", role: "Captain & Middle Order" },
          { name: "VAIBHAV SOORYAVANSHI", role: "Explosive Opener (204*)" },
          { name: "RINKU SINGH", role: "Finisher & Power Hitter" },
          { name: "HARSHIT RANA", role: "Pace Spearhead" },
        ];
        const starsA = t1.includes("IND") ? indStars : slStars;
        const starsB = t2.includes("IND") ? indStars : slStars;
        starsBox.innerHTML = `
          <div class="crex-subhead">KEY PLAYERS TO WATCH</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
            <div style="display:grid;gap:8px">
              <div style="font-size:12px;font-weight:800;color:#facc15;letter-spacing:1px">${t1} WATCHLIST</div>
              ${starsA.map((s) => `<div class="tp-card anim-card" style="padding:10px;display:flex;align-items:center;gap:10px"><img src="${playerPhoto(s.name, "/assets/batting_hero.jpg")}" onerror="this.src='/assets/batting_hero.jpg'" alt="${s.name}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;object-position:top center;border:1px solid rgba(250,204,21,0.45);flex-shrink:0" /><div><div style="font-weight:800;font-size:13px">${s.name}</div><div style="font-size:11px;color:#94a3b8">${s.role}</div></div></div>`).join("")}
            </div>
            <div style="display:grid;gap:8px">
              <div style="font-size:12px;font-weight:800;color:#60a5fa;letter-spacing:1px">${t2} WATCHLIST</div>
              ${starsB.map((s) => `<div class="tp-card anim-card" style="padding:10px;display:flex;align-items:center;gap:10px"><img src="${playerPhoto(s.name, "/assets/bowling_hero.jpg")}" onerror="this.src='/assets/bowling_hero.jpg'" alt="${s.name}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;object-position:top center;border:1px solid rgba(96,165,250,0.45);flex-shrink:0" /><div><div style="font-weight:800;font-size:13px">${s.name}</div><div style="font-size:11px;color:#94a3b8">${s.role}</div></div></div>`).join("")}
            </div>
          </div>`;
      }
    });
  }

  if (pageType === "news") {
    const loadNews = async () => {
      const leadBox = document.getElementById("newsLeadBox");
      const feedBox = document.getElementById("newsFeedBox");
      let dbNews = [];
      try {
        const r = await fetch("/api/stories");
        if (r.ok) { const j = await r.json(); dbNews = j.news || []; }
      } catch {}
      const crexNews = Array.isArray(data.latest_news) ? data.latest_news : [];
      const combined = [
        ...crexNews.map((n) => ({ title: n.title || n.headline || "Cricket Update", summary: n.summary || n.body || "Breaking update from the live cricket newsroom.", tag: "NEWS WIRE" })),
        ...dbNews.map((n) => ({ title: n.headline || n.title || "Studio News", summary: n.summary || n.body || "", tag: "STUDIO DESK" })),
      ];
      if (!combined.length) {
        combined.push(
          { title: "Asia Cup Rising Stars 2026: SL-A vs IND-A Semi-Final Showdown in Doha", summary: "Unbeaten Sri Lanka A (3/3) face explosive India A (+3.523 NRR) at West End Park.", tag: "BREAKING" },
          { title: "Vaibhav Sooryavanshi's Historic 204* Powers India A Into Knockouts", summary: "The teenage opener's 53-ball blitz has set the tournament alight ahead of the semi-final.", tag: "HOT PICK" },
          { title: "Doha Surface Watch: 50/50 Pace vs Spin Split", summary: "Last 10 matches show 72 pace wickets and 73 spin wickets — captains eye batting first.", tag: "PITCH DESK" }
        );
      }
      const lead = combined[0];
      if (leadBox) {
        leadBox.innerHTML = `
          <div class="crex-subhead">LEAD STORY • ${lead.tag}</div>
          <div class="potm-banner anim-card" style="flex-direction:column;align-items:flex-start;gap:10px;padding:18px">
            <span class="tp-tag" style="background:rgba(239,68,68,0.22);color:#fca5a5;border-color:rgba(239,68,68,0.4)">LIVE NEWSROOM</span>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:32px;font-weight:800;line-height:1.1;color:#fff">${lead.title}</div>
            <div style="font-size:14px;line-height:1.55;color:#cbd5e1">${lead.summary}</div>
          </div>
          <div class="tp-card anim-card" style="margin-top:12px">
            <span class="tp-tag">ON AIR</span>
            <div><strong>Studio Take</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Live discussion active with Host &amp; Expert — reacting to breaking cricket headlines.</div></div>
          </div>`;
      }
      if (feedBox) {
        feedBox.innerHTML = `
          <div class="crex-subhead">TRENDING HEADLINES (${combined.length})</div>
          <div style="display:grid;gap:9px">
            ${combined.slice(1, 6).map((item, i) => `
              <div class="tp-card anim-card" style="animation-delay:${i * 45}ms;padding:11px 13px">
                <span class="tp-tag">${item.tag}</span>
                <div>
                  <div style="font-weight:800;font-size:14px;color:#fff">${item.title}</div>
                  ${item.summary ? `<div style="font-size:12px;color:#94a3b8;margin-top:2px">${item.summary.slice(0, 110)}</div>` : ""}
                </div>
              </div>`).join("")}
          </div>`;
      }
    };
    renderIfChanged("news", [data.latest_news, data.match_title], () => { loadNews(); });
  }

  if (pageType === "other_matches") {
    renderIfChanged("other_matches", [data.points_table, data.series_name, data.venue], () => {
      const mBox = document.getElementById("otherMatchesBox");
      const sBox = document.getElementById("otherStandingsBox");
      const pts = Array.isArray(data.points_table) ? data.points_table : [];
      const fixtures = [
        { comp: "12TH ONE DAY • DOHA", a: "PAK-A", as: "168 (42.0)", b: "NEP", bs: "72 (17.3)", res: "PAK-A Won by 96 runs" },
        { comp: "10TH ONE DAY • DOHA", a: "SL-A", as: "146/3 (21.5)", b: "BAN-A", bs: "145 (42.5)", res: "SL-A Won by 7 wickets" },
        { comp: "8TH ONE DAY • DOHA", a: "PAK-A", as: "313 (49.2)", b: "IND-A", bs: "265 (49.1)", res: "PAK-A Won by 48 runs" },
        { comp: "FINAL • TRI SERIES SL 2026", a: "IND-A", as: "377/9 (50.0)", b: "SL-A", bs: "311 (47.1)", res: "IND-A Won by 66 runs" },
      ];
      if (mBox) {
        mBox.innerHTML = `
          <div class="crex-subhead">RECENT RESULTS &amp; OTHER MATCHES</div>
          <div style="display:grid;gap:10px">
            ${fixtures.map((f, i) => `
              <div class="anim-card" style="animation-delay:${i * 50}ms;padding:11px 13px;border-radius:12px;background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.09)">
                <div style="display:flex;justify-content:space-between;font-size:10px;letter-spacing:1.1px;color:#94a3b8;font-weight:800;margin-bottom:5px">
                  <span>${f.comp}</span><span style="color:#4ade80">${f.res}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;font-weight:800;font-size:15px">
                  <span>${f.a} <span style="color:#fcd34d">${f.as}</span></span>
                  <span style="color:#64748b;font-size:12px">vs</span>
                  <span>${f.b} <span style="color:#93c5fd">${f.bs}</span></span>
                </div>
              </div>`).join("")}
          </div>`;
      }
      if (sBox) {
        sBox.innerHTML = `
          <div class="crex-subhead">TOURNAMENT STANDINGS • ${(data.series_name || "ASIA CUP RISING STARS").toUpperCase()}</div>
          <div style="display:grid;gap:8px">
            ${(pts.length ? pts.slice(0, 6) : [
              { team: "SRI LANKA A", won: 3, lost: 0, nrr: "+2.512", pts: 6, q: true },
              { team: "BANGLADESH A", won: 2, lost: 1, nrr: "+0.840", pts: 4, q: true },
              { team: "PAKISTAN A", won: 3, lost: 0, nrr: "+2.910", pts: 6, q: true },
              { team: "INDIA A", won: 2, lost: 1, nrr: "+3.523", pts: 4, q: true },
            ]).map((row, idx) => `
              <div class="tp-card anim-card" style="justify-content:space-between;padding:10px 13px">
                <div style="display:flex;align-items:center;gap:10px">
                  <span class="tp-tag">${idx + 1}</span>
                  <div>
                    <div style="font-weight:800;font-size:14px">${row.team || row.name}</div>
                    <div style="font-size:11px;color:#94a3b8">${row.won ?? 0}W - ${row.lost ?? 0}L • NRR ${row.nrr || "0.000"}</div>
                  </div>
                </div>
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:24px;font-weight:800;color:var(--gold)">${row.pts ?? 0} PTS</div>
              </div>`).join("")}
          </div>`;
      }
    });
  }

  if (pageType === "stories_hub") {
    const loadStories = async () => {
      const spotBox = document.getElementById("storySpotlightBox");
      const qBox = document.getElementById("storyQueueBox");
      let stories = [];
      try {
        const r = await fetch("/api/stories");
        if (r.ok) { const j = await r.json(); stories = j.stories || []; }
      } catch {}
      if (!stories.length) {
        stories = [
          { title: "The 53-Ball Storm", category: "RISING STAR", host_line: "वैभव सूर्यवंशी की 204 रन की पारी ने पूरे ड्रेसिंग रूम का माहौल बदल दिया!", expert_line: "इतनी कम उम्र में इतना बड़ा टेम्परामेंट बहुत कम देखने को मिलता है!" },
          { title: "Super Over Thriller", category: "RIVALRY", host_line: "पिछली ट्राई-सीरीज़ में श्रीलंका ए और इंडिया ए का सुपर ओवर याद है ना?", expert_line: "हाँ, आखिरी गेंद तक साँसें थम गई थीं — आज फिर वही जोश दिखेगा!" },
          { title: "Spin Trap In Doha", category: "TACTICS", host_line: "दोहा की पिच पर शाम होते ही स्पिनर्स की गेंद घूमने लगती है!", expert_line: "मिडिल ओवर्स में जो टीम डॉट बॉल कम खेलेगी, वही फाइनल में जाएगी!" },
        ];
      }
      const lead = stories[0];
      if (spotBox) {
        spotBox.innerHTML = `
          <div class="crex-subhead">FEATURED STORY • ${(lead.category || "DRESSING ROOM").toUpperCase()}</div>
          <div class="potm-banner anim-card" style="flex-direction:column;align-items:flex-start;gap:10px;padding:18px">
            <span class="tp-tag">STORY SPOTLIGHT</span>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:32px;font-weight:800;color:#fff">${lead.title || (lead.topic || lead.category || "CRICKET STORY").replace(/_/g, " ").toUpperCase()}</div>
            <div style="font-size:15px;line-height:1.55;color:#fde68a">🎙️ ${lead.host_line}</div>
            <div style="font-size:14px;line-height:1.5;color:#cbd5e1">💬 ${lead.expert_line}</div>
          </div>`;
      }
      if (qBox) {
        qBox.innerHTML = `
          <div class="crex-subhead">MORE CRICKET STORIES (${stories.length})</div>
          <div style="display:grid;gap:10px">
            ${stories.slice(1, 5).map((st, i) => `
              <div class="tp-card anim-card" style="animation-delay:${i * 45}ms;padding:11px 13px">
                <span class="tp-tag">${(st.category || st.topic || "STORY").replace(/_/g, " ").toUpperCase().slice(0, 12)}</span>
                <div>
                  <div style="font-weight:800;font-size:14px;color:#fff">${st.title || (st.topic || st.category || "DRESSING ROOM TALE").replace(/_/g, " ").toUpperCase()}</div>
                  <div style="font-size:12px;color:#94a3b8;margin-top:2px">${(st.host_line || "").slice(0, 95)}</div>
                </div>
              </div>`).join("")}
          </div>`;
      }
    };
    renderIfChanged("stories_hub", [data.match_title, data.match_status], () => { loadStories(); });
  }

  if (pageType === "experience") {
    renderIfChanged("experience", [data.venue, data.venue_stats, data.match_status], () => {
      const fBox = document.getElementById("expFieldBox");
      const nBox = document.getElementById("expNotesBox");
      if (fBox) {
        fBox.innerHTML = `
          <div class="crex-subhead">CAPTAIN'S FIELD RADAR • KNOCKOUT PRESSURE</div>
          <div style="display:flex;align-items:center;justify-content:center;padding:8px">
            <svg viewBox="0 0 260 220" style="width:100%;max-width:340px;height:auto">
              <ellipse cx="130" cy="110" rx="116" ry="96" fill="rgba(22,101,52,0.45)" stroke="#4ade80" stroke-width="2.5"/>
              <ellipse cx="130" cy="110" rx="64" ry="52" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="1.5" stroke-dasharray="5 4"/>
              <rect x="122" y="88" width="16" height="44" rx="2" fill="#d97706" opacity="0.85"/>
              <circle cx="130" cy="95" r="4" fill="#fff"/>
              <circle cx="88" cy="70" r="5" fill="#38bdf8"/><circle cx="174" cy="72" r="5" fill="#38bdf8"/>
              <circle cx="62" cy="116" r="5" fill="#38bdf8"/><circle cx="198" cy="116" r="5" fill="#38bdf8"/>
              <circle cx="94" cy="154" r="5" fill="#38bdf8"/><circle cx="168" cy="154" r="5" fill="#38bdf8"/>
              <circle cx="130" cy="24" r="5.5" fill="#facc15"/><circle cx="40" cy="148" r="5.5" fill="#facc15"/>
              <circle cx="220" cy="148" r="5.5" fill="#facc15"/>
              <text x="130" y="213" text-anchor="middle" fill="#cbd5e1" font-size="10" font-weight="700">30-YARD RING • DEEP BOUNDARY RIDERS</text>
            </svg>
          </div>
          <div class="stat-grid-2">
            <div class="stat-box anim-card"><div class="stat-lbl">IN-RING FIELDERS</div><div class="stat-val" style="color:#38bdf8">5</div></div>
            <div class="stat-box anim-card"><div class="stat-lbl">BOUNDARY RIDERS</div><div class="stat-val" style="color:var(--gold)">4</div></div>
          </div>`;
      }
      if (nBox) {
        nBox.innerHTML = `
          <div class="crex-subhead">EXPERT EXPERIENCE &amp; TACTICAL PLAYBOOK</div>
          <div style="display:grid;gap:10px">
            <div class="tp-card anim-card"><span class="tp-tag">TEMPERAMENT</span><div><strong>Knockout First 10 Overs</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">New ball swings under Doha lights — leave wide deliveries early before accelerating.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">SPIN CRAFT</span><div><strong>Speed &amp; Length Variation</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Slowing pace into the pitch (84–88 km/h) forces miscues toward the long square boundary.</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">DEATH BOWLING</span><div><strong>Wide Yorkers &amp; Slower Bouncers</strong><div style="font-size:12px;color:#cbd5e1;margin-top:2px">Protect the straight boundary with deep mid-on and hit hard lengths into the body.</div></div></div>
          </div>`;
      }
    });
  }

  if (pageType === "stats_deep") {
    renderIfChanged("stats_deep", [data.venue_stats, data.team_comparison, data.crr, data.runs], () => {
      const pBox = document.getElementById("statsPhaseBox");
      const sBox = document.getElementById("statsSplitBox");
      const st = data.venue_stats || {};
      const cmp = data.team_comparison || {};
      const phases = [
        { lbl: "PP (1-10 OV)", rr: "6.4", pct: 68 },
        { lbl: "MID (11-40 OV)", rr: "5.2", pct: 55 },
        { lbl: "DEATH (41-50)", rr: "8.9", pct: 92 },
      ];
      if (pBox) {
        pBox.innerHTML = `
          <div class="crex-subhead">PHASE-BY-PHASE SCORING RATE</div>
          <div class="vchart cols-3" style="height:150px">
            ${phases.map((ph, i) => `
              <div class="vbar-col">
                <div class="vbar-num">${ph.rr} RR</div>
                <div class="vbar-track"><div class="vbar-fill ${i === 2 ? "" : "alt"}" style="height:${ph.pct}%"></div></div>
                <div class="vbar-lbl">${ph.lbl}</div>
              </div>`).join("")}
          </div>
          <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:8px 12px;margin-bottom:10px">
            <div style="font-size:10px;font-weight:800;letter-spacing:1px;color:#94a3b8;margin-bottom:4px">INNINGS RUN-RATE TRAJECTORY (OV 1 → 50)</div>
            <svg viewBox="0 0 320 54" style="width:100%;height:50px;display:block">
              <defs><linearGradient id="rrGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#38bdf8" stop-opacity="0.35"/><stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/></linearGradient></defs>
              <path d="M8,40 Q70,22 140,30 T240,18 T312,6 L312,52 L8,52 Z" fill="url(#rrGrad)"/>
              <path class="svg-line-anim" d="M8,40 Q70,22 140,30 T240,18 T312,6" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="8" cy="40" r="3.5" fill="#38bdf8"/><circle cx="140" cy="30" r="3.5" fill="#38bdf8"/><circle cx="312" cy="6" r="4" fill="#ffd426"/>
            </svg>
          </div>
          <div class="stat-grid-2">
            <div class="stat-box anim-card"><div class="stat-lbl">AVG 1ST INNINGS</div><div class="stat-val" style="color:#38bdf8">${st.avg_1st || 268}</div></div>
            <div class="stat-box anim-card"><div class="stat-lbl">HIGHEST CHASED</div><div class="stat-val" style="color:var(--gold)">${st.highest_chased || "319/7"}</div></div>
          </div>`;
      }
      if (sBox) {
        const pacePct = Number(st.pace_pct || 50);
        const spinPct = Number(st.spin_pct || 50);
        sBox.innerHTML = `
          <div class="crex-subhead">BOWLING &amp; WIN BIAS ANALYTICS</div>
          <div class="rings-row">
            ${svgRing(pacePct, `${pacePct}%`, `${st.pace_wkts || 72} WKTS`, "PACE SHARE", "#38bdf8")}
            ${svgRing(spinPct, `${spinPct}%`, `${st.spin_wkts || 73} WKTS`, "SPIN SHARE", "#f59e0b")}
          </div>
          <div style="display:grid;gap:10px;margin-top:12px">
            <div class="tp-card anim-card"><span class="tp-tag">AVG SCORE</span><div><strong>${data.batting_team}: ${cmp.avg_left || "279"} vs ${data.bowling_team}: ${cmp.avg_right || "264"}</strong><div style="font-size:12px;color:#94a3b8;margin-top:2px">Last 10 One-Day averages across all venues</div></div></div>
            <div class="tp-card anim-card"><span class="tp-tag">CEILING</span><div><strong>Highest Total: ${cmp.high_left || "377"} vs ${cmp.high_right || "368"}</strong><div style="font-size:12px;color:#94a3b8;margin-top:2px">Both batting units have 360+ firepower</div></div></div>
          </div>`;
      }
    });
  }

  if (pageType === "versus") {
    const poster = document.querySelector(".vs-poster");
    if (poster) {
      const [l1, l2] = getTeamColors(data.batting_team);
      const [r1, r2] = getTeamColors(data.bowling_team);
      poster.style.setProperty("--vs-left-1", l1);
      poster.style.setProperty("--vs-left-2", l2);
      poster.style.setProperty("--vs-right-1", r1);
      poster.style.setProperty("--vs-right-2", r2);
    }
    const banner = document.getElementById("vsBanner");
    if (banner) {
      const cleanSeries = (data.series_name && !/theme|language/i.test(data.series_name))
        ? data.series_name
        : `${data.batting_team} VS ${data.bowling_team}`;
      const cleanVenue = (data.venue && !/theme|language/i.test(data.venue))
        ? ` • ${data.venue.toUpperCase()}`
        : "";
      banner.textContent = `MATCHDAY SHOWDOWN • ${cleanSeries.toUpperCase()}${cleanVenue}`;
    }
    const fl = document.getElementById("vsFlagLeft");
    const fr = document.getElementById("vsFlagRight");
    if (fl) fl.innerHTML = flagSvg(data.batting_team);
    if (fr) fr.innerHTML = flagSvg(data.bowling_team);
    const tl = document.getElementById("vsTeamLeft");
    const tr = document.getElementById("vsTeamRight");
    const wl = document.getElementById("vsWatermarkL");
    const wr = document.getElementById("vsWatermarkR");
    if (tl) tl.textContent = data.batting_team;
    if (tr) tr.textContent = data.bowling_team;
    if (wl) wl.textContent = data.batting_team;
    if (wr) wr.textContent = data.bowling_team;
  }

  if (pageType === "report") {
    renderIfChanged("report", [data.match_result, data.match_status, data.player_of_match, data.first_innings, data.batters_list, data.bowlers_list, data.fall_of_wickets], () => {
      const sBox = document.getElementById("reportSummaryBox");
      const tBox = document.getElementById("reportTurningBox");
      const potm = data.player_of_match || {};
      const inn1 = data.first_innings || {};
      const inn1Runs = parseInt(String(inn1.score || (data.target ? data.target - 1 : 0)).split("-")[0], 10) || 0;
      const totSum = Math.max(inn1Runs + (Number(data.runs) || 0), 1);
      const inn1Bats = (inn1.batters || []).slice(0, 2);
      const topBat2 = [...(data.batters_list || [])].sort((a, b) => b.runs - a.runs).slice(0, 2);
      const topBatters = [...inn1Bats.map((b) => ({ ...b, tm: inn1.team || data.bowling_team })), ...topBat2.map((b) => ({ ...b, tm: data.batting_team }))];
      const maxBatRuns = Math.max(...topBatters.map((b) => Number(b.runs || 0)), 1);
      const topBowls = [...(data.bowlers_list || [])].sort((a, b) => (b.wickets - a.wickets) || (a.runs_conceded - b.runs_conceded)).slice(0, 4);
      const maxWkts = Math.max(...topBowls.map((bw) => Number(bw.wickets || 0)), 1);

      if (sBox) {
        sBox.innerHTML = `
          <div class="crex-subhead">OFFICIAL VERDICT • ${data.series_name || "MATCH REPORT"}</div>
          <div class="potm-banner anim-card">
            <div>
              <div class="potm-title">${(data.match_result || data.callout || "MATCH REVIEW").toUpperCase()}</div>
              <div class="potm-sub">${data.venue || ""}</div>
            </div>
            ${potm.name ? `
              <div style="text-align:right;">
                <div style="font-family:var(--font-ui);font-size:10px;font-weight:800;color:var(--gold);letter-spacing:0.12em;">PLAYER OF THE MATCH</div>
                <div style="font-size:22px;font-weight:800;color:#fff;">${potm.name}</div>
                <div style="font-family:var(--font-ui);font-size:13px;font-weight:700;color:#38bdf8;">${potm.figures || ""}</div>
              </div>` : ""}
          </div>
          <div class="split-wrap">
            <div class="split-labels">
              <span>${inn1.team || data.bowling_team} ${inn1.score || inn1Runs} (${inn1.overs || "20.0"})</span>
              <span>${data.batting_team} ${data.runs}/${data.wickets} (${data.overs})</span>
            </div>
            <div class="split-bar">
              <div class="split-fill-a" style="width:${Math.round((inn1Runs / totSum) * 100)}%"></div>
              <div class="split-fill-b" style="width:${Math.round((data.runs / totSum) * 100)}%"></div>
            </div>
          </div>
          <div class="crex-subhead">TOP RUN SCORERS</div>
          ${topBatters.map((b) => `
            <div class="meter-row anim-card">
              <div class="meter-head"><span>[${b.tm}] ${b.name}</span><span style="color:var(--gold)">${b.runs} (${b.balls}) • SR ${Number(b.strike_rate || 0).toFixed(0)}</span></div>
              <div class="meter-track"><div class="meter-fill" style="width:${Math.max(12, Math.round((Number(b.runs || 0) / maxBatRuns) * 100))}%"></div></div>
            </div>`).join("")}`;
      }
      if (tBox) {
        const fows = (data.fall_of_wickets || []).slice(0, 8);
        tBox.innerHTML = `
          <div class="crex-subhead">KEY BOWLING SPELLS</div>
          ${topBowls.map((bw) => `
            <div class="meter-row anim-card">
              <div class="meter-head"><span>${bw.name} (${bw.overs} ov)</span><span style="color:#38bdf8">${bw.wickets}/${bw.runs_conceded} • ER ${Number(bw.economy || 0).toFixed(2)}</span></div>
              <div class="meter-track"><div class="meter-fill" style="width:${Math.max(15, Math.round((Number(bw.wickets || 0) / maxWkts) * 100))}%;background:linear-gradient(90deg,#f59e0b,#ef4444);"></div></div>
            </div>`).join("")}
          <div class="crex-subhead" style="margin-top:14px;">WICKET COLLAPSE TIMELINE</div>
          <div class="fow-timeline">
            ${fows.map((f) => {
              const parts = f.split("•");
              return `<div class="fow-pin"><strong>${(parts[1] || f).trim()}</strong><span>${(parts[0] || "").trim()}</span></div>`;
            }).join("") || `<div class="fow-pin"><strong>${data.last_wicket || "Complete"}</strong></div>`}
          </div>`;
      }
    });
  }

  if (pageType === "story") {
    renderStudioStoryPage(data);
  }

  if (pageType === "audience") {
    renderIfChanged("audience", [data.batting_team, data.bowling_team, data.fan_poll, data.quiz_prompt, data.points_table, data.player_of_match], () => {
      const pBox = document.getElementById("audiencePollBox");
      const qBox = document.getElementById("audienceQuizBox");
      const fp = data.fan_poll || { total_votes: 230523, batting_pct: 62, bowling_pct: 38 };
      const bPct = fp.batting_pct ?? 62;
      const oPct = fp.bowling_pct ?? (100 - bPct);
      const potm = data.player_of_match || {};
      const quiz = data.quiz_prompt || {};
      if (pBox) {
        pBox.innerHTML = `
          <div class="crex-subhead">CROWD POLL • ${Number(fp.total_votes || 0).toLocaleString()} VOTES</div>
          <div class="rings-row">
            ${svgRing(bPct, `${bPct}%`, data.batting_team, "FAN PICK", "#38bdf8")}
            ${svgRing(oPct, `${oPct}%`, data.bowling_team, "FAN PICK", "#f59e0b")}
          </div>
          <div class="crex-subhead">LIVE CHAT VOTE • COMMENT A / B / C</div>
          <div class="debate-grid">
            <div class="debate-tile"><div class="debate-letter">A</div><div class="debate-lbl">${potm.name ? `${potm.name} (${potm.figures})` : "BOWLERS"}</div></div>
            <div class="debate-tile"><div class="debate-letter" style="background:#38bdf8;">B</div><div class="debate-lbl">${data.first_innings?.team || data.bowling_team} TOTAL</div></div>
            <div class="debate-tile"><div class="debate-letter" style="background:#22c55e;">C</div><div class="debate-lbl">MIDDLE OVERS</div></div>
          </div>`;
      }
      if (qBox) {
        const pt = (data.points_table || []).slice(0, 4);
        const maxPts = Math.max(...pt.map((r) => Number(r.pts || 0)), 1);
        qBox.innerHTML = `
          <div class="crex-subhead">LIVE TRIVIA QUIZ</div>
          <div class="onair-card anim-card" style="background:rgba(56,189,248,0.1);border-color:rgba(56,189,248,0.4);">
            <div style="font-family:var(--font-ui);font-size:17px;font-weight:800;color:#fff;line-height:1.35;">${quiz.question || `Who was MVP in ${data.match_title}?`}</div>
            <div style="font-family:var(--font-ui);font-size:12px;font-weight:700;color:var(--gold);margin-top:8px;">${quiz.players || "Answer in chat!"}</div>
          </div>
          <div class="crex-subhead">POINTS TABLE TOP 4</div>
          ${pt.map((r, i) => `
            <div class="meter-row anim-card">
              <div class="meter-head"><span><span class="rank-pill" style="margin-right:6px;">${i + 1}</span> ${r.team}</span><span style="color:var(--gold)">${r.pts} PTS • ${r.nrr}</span></div>
              <div class="meter-track"><div class="meter-fill" style="width:${Math.max(15, Math.round((Number(r.pts || 0) / maxPts) * 100))}%"></div></div>
            </div>`).join("")}`;
      }
    });
  }
}

let studioRecentLines = [];
try {
  const savedTalk = localStorage.getItem("cricket_live_studio_talk");
  if (savedTalk) studioRecentLines = JSON.parse(savedTalk);
} catch {}

function renderStudioStoryPage(data) {
  const airBox = document.getElementById("storyOnAirBox");
  const newsBox = document.getElementById("storyNewsBox");
  if (airBox) {
    const latest = studioRecentLines.length ? studioRecentLines[studioRecentLines.length - 1] : null;
    const prev = studioRecentLines.slice(-3, -1).reverse();
    const spk = latest ? (latest.speaker || "host").toLowerCase() : "host";
    airBox.innerHTML = `
      <div class="crex-subhead">STUDIO LIVE MIC</div>
      <div class="onair-card anim-card">
        <span class="speaker-tag ${spk === "expert" ? "expert" : ""}">
          ${spk === "expert" ? "EXPERT ANALYST" : "STUDIO HOST"}
          <span class="eq-bars"><span></span><span></span><span></span><span></span></span>
        </span>
        <div class="caption-hindi">${latest ? latest.text : (data?.live_commentary || "स्टूडियो चर्चा जारी है...")}</div>
      </div>
      <div class="crex-subhead">PREVIOUS TURN</div>
      ${prev.slice(0, 1).map((l) => `<div class="h2h-card anim-card"><div><div class="h2h-match">${String(l.speaker || "host").toUpperCase()}</div><div class="h2h-scores" style="font-size:14px;">${l.text}</div></div></div>`).join("") || `<div class="h2h-card"><div class="h2h-scores" style="font-size:14px;">${data?.match_result || data?.match_title || "Live"}</div></div>`}`;
  }
  if (newsBox && data) {
    renderIfChanged("story_news", [data.latest_news, data.player_of_match], () => {
      const newsList = (data.latest_news || []).slice(0, 3);
      const potm = data.player_of_match || {};
      newsBox.innerHTML = `
        <div class="crex-subhead">HEADLINE STORYLINE</div>
        <div class="potm-banner anim-card" style="padding:12px 14px;">
          <div>
            <div class="potm-title" style="font-size:20px;">${(data.match_result || data.match_title || "").toUpperCase()}</div>
            <div class="potm-sub">${potm.name ? `MVP: ${potm.name} (${potm.figures})` : (data.venue || "")}</div>
          </div>
        </div>
        <div class="crex-subhead">CRICKET NEWS WIRE</div>
        ${newsList.map((n) => `<div class="news-item-card anim-card">${n.title.slice(0, 90)}${n.title.length > 90 ? "..." : ""}</div>`).join("") || `<div class="news-item-card">${(data.ticker_items || []).slice(0, 2).join(" • ")}</div>`}`;
    });
  }
}

if (pageType === "story") {
  fetch("/api/commentary/status").then((r) => (r.ok ? r.json() : null)).then((st) => {
    if (st && Array.isArray(st.recent_lines) && st.recent_lines.length) {
      studioRecentLines = st.recent_lines;
      try { localStorage.setItem("cricket_live_studio_talk", JSON.stringify(studioRecentLines.slice(-12))); } catch {}
      renderStudioStoryPage(null);
    }
  }).catch(() => {});
}

// Render shared navigation bar across all template pages
const navEl = document.querySelector(".page-nav");
if (navEl) {
  const links = [
    ["/", "Scoreboard", "home"],
    ["/prematch.html", "Pre-Match", "prematch"],
    ["/toss.html", "Toss Center", "toss"],
    ["/key_battles.html", "Key Battles", "key_battles"],
    ["/road_to_semi.html", "Road to Semi", "road_to_semi"],
    ["/players_to_watch.html", "Players Watch", "players_to_watch"],
    ["/predictions.html", "Predictions", "predictions"],
    ["/comparison.html", "Team Radar", "comparison"],
    ["/versus.html", "Versus", "versus"],
    ["/batting.html", "Batting", "batting"],
    ["/bowling.html", "Bowling", "bowling"],
    ["/overs.html", "Overs & FOW", "overs"],
    ["/match.html", "Match & Win%", "match"],
    ["/playing11.html", "Playing XI", "playing11"],
    ["/player.html", "Player Card", "player"],
    ["/info.html", "Match Info", "info"],
    ["/partnership.html", "Partnership", "partnership"],
    ["/break.html", "Break Screen", "break"],
    ["/leaders.html", "Top Performers", "leaders"],
    ["/milestone.html", "Milestone", "milestone"],
    ["/runrate.html", "Boundaries", "runrate"],
    ["/projected.html", "Projected", "projected"],
    ["/pitch.html", "Pitch & Venue", "pitch"],
    ["/form.html", "Team Form", "form"],
    ["/points.html", "Points Table", "points"],
    ["/rankings.html", "ICC Rankings", "rankings"],
    ["/report.html", "Match Report", "report"],
    ["/story.html", "Match Talks", "story"],
    ["/audience.html", "Audience Zone", "audience"],
    ["/news.html", "Live News", "news"],
    ["/other_matches.html", "Other Matches", "other_matches"],
    ["/stories_hub.html", "Small Stories", "stories_hub"],
    ["/experience.html", "Experience", "experience"],
    ["/stats_deep.html", "Deep Stats", "stats_deep"],
  ];
  navEl.innerHTML = `<span class="nav-label">Pages:</span>` + links.map(([href, label, key]) =>
    `<a class="nav-link ${pageType === key ? "active" : ""}" href="${href}">${label}</a>`
  ).join("");
}

function connect() {
  const wsProto = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${wsProto}//${location.host}/ws`);
  ws.addEventListener("message", (ev) => {
    try {
      const payload = JSON.parse(ev.data);
      if (payload.type === "commentary") {
        studioRecentLines.push({ speaker: payload.speaker || "host", text: payload.text || "" });
        if (studioRecentLines.length > 12) studioRecentLines.shift();
        try { localStorage.setItem("cricket_live_studio_talk", JSON.stringify(studioRecentLines)); } catch {}
        if (pageType === "story") renderStudioStoryPage(null);
        return;
      }
      if (payload.type) return;
      renderPage(payload);
    } catch {}
  });
  ws.addEventListener("close", () => setTimeout(connect, 3000));
}

try {
  const cached = localStorage.getItem(STATE_CACHE_KEY);
  if (cached) renderPage(JSON.parse(cached));
} catch {}

fetch("/api/state").then((r) => (r.ok ? r.json() : null)).then(renderPage).catch(() => {});
connect();
