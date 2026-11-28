const REFERENCE_PREVIEW_STATE = {
  batting_team: "BAN-A",
  bowling_team: "PAK-A",
  runs: 36,
  wickets: 2,
  overs: "12.0",
  partnership: "21(46)",
  crr: 3.0,
  rrr: 0.0,
  target: 0,
  callout: "DOT BALL",
  callout_tone: "neutral",
  match_title: "BAN-A Vs PAK-A, 2nd Semi Final One Day, Asia Cup Rising Stars 2026",
  series_name: "Asia Cup Rising Stars 2026",
  venue: "West End Park International Cricket Stadium, Doha",
  match_date: "Friday, 27 November, 3:30 PM",
  toss: "BAN-A WON THE TOSS AND CHOSE TO BAT",
  weather: { temp: "27.8°C", condition: "Sunny", humidity: "44%", rain_chance: "1%" },
  venue_stats: { matches: 45, win_bat_first: 48, win_bowl_first: 52, avg_1st: 268, avg_2nd: 234, highest_total: "356/5", lowest_total: "112/10", pace_pct: 50, spin_pct: 50 },
  prev_over: { over_number: 11, balls: ["1", "0", "4", "0", "1", "0"], total: 6 },
  curr_over: { over_number: 12, balls: ["0", "0", "1", "0", "0", "0"], total: 1 },
  striker: { name: "MAHMUDUL HASAN JOY", runs: 14, balls: 28, fours: 1, sixes: 0, strike_rate: 50.0, on_strike: true },
  non_striker: { name: "SHAHADAT HOSSAIN DIPU", runs: 9, balls: 20, fours: 1, sixes: 0, strike_rate: 45.0, on_strike: false },
  bowler: { name: "ALI RAZA", wickets: 1, runs_conceded: 12, overs: "4.0", maidens: 1, economy: 3.00 },
  batters_list: [
    { name: "SAIF HASSAN", runs: 6, balls: 11, fours: 1, sixes: 0, strike_rate: 54.55, on_strike: false, dismissal: "b Ali Raza" },
    { name: "AFIF HOSSAIN", runs: 4, balls: 13, fours: 0, sixes: 0, strike_rate: 30.77, on_strike: false, dismissal: "c Rohail Nazir b Ahmed Daniyal" },
    { name: "SHAHADAT HOSSAIN DIPU", runs: 9, balls: 20, fours: 1, sixes: 0, strike_rate: 45.0, on_strike: false, dismissal: "" },
    { name: "MAHMUDUL HASAN JOY", runs: 14, balls: 28, fours: 1, sixes: 0, strike_rate: 50.0, on_strike: true, dismissal: "" },
  ],
  bowlers_list: [
    { name: "ALI RAZA", wickets: 1, runs_conceded: 12, overs: "4.0", maidens: 1, economy: 3.00 },
    { name: "AHMED DANIYAL", wickets: 1, runs_conceded: 10, overs: "4.0", maidens: 0, economy: 2.50 },
    { name: "MUHAMMAD IMRAN RANDHAWA", wickets: 0, runs_conceded: 8, overs: "2.0", maidens: 0, economy: 4.00 },
    { name: "SUFYAN MOQIM", wickets: 0, runs_conceded: 6, overs: "2.0", maidens: 0, economy: 3.00 },
  ],
  batting_xi: [
    "S HASSAN (C)", "A HOSSAIN", "S H DIPU", "M H JOY", "S RAHMAN",
    "M I ANKON (WK)", "R HASAN", "S M M HASAN", "M RUBEL", "R MONDOL", "I H EMMON",
  ],
  bowling_xi: [
    "S HUSSAIN", "M SADAQAT", "S KHAN", "R NAZIR (WK)", "H NAWAZ",
    "A SAMAD (C)", "F YOUSAF", "M I RANDHAWA", "A DANIYAL", "S MOQIM", "A RAZA",
  ],
  ticker_items: [
    "BAN-A VS PAK-A 2ND SEMI-FINAL • ASIA CUP RISING STARS 2026",
    "WEST END PARK INTERNATIONAL CRICKET STADIUM, DOHA",
    "BAN-A WON THE TOSS AND CHOSE TO BAT",
    "ALI RAZA 8 WICKETS IN SERIES • PAK-A VS BAN-A LIVE",
  ],
};

// Built-in local asset map for players in /assets/players/
const BUILTIN_PLAYER_IMAGES = {
  "TOM LATHAM": "/assets/players/tom_latham__F0.png",
  "T LATHAM": "/assets/players/tom_latham__F0.png",
  "DEVON CONWAY": "/assets/players/devon_conway__4W1.png",
  "D CONWAY": "/assets/players/devon_conway__4W1.png",
  "HENRY NICHOLLS": "/assets/players/henry_nicholls__EW.png",
  "H NICHOLLS": "/assets/players/henry_nicholls__EW.png",
  "RACHIN RAVINDRA": "/assets/players/rachin_ravindra__4W3.png",
  "R RAVINDRA": "/assets/players/rachin_ravindra__4W3.png",
  "DARYL MITCHELL": "/assets/players/daryl_mitchell__K5.png",
  "D MITCHELL": "/assets/players/daryl_mitchell__K5.png",
  "TOM BLUNDELL": "/assets/players/tom_blundell__KN.png",
  "T BLUNDELL": "/assets/players/tom_blundell__KN.png",
  "GLENN PHILLIPS": "/assets/players/glenn_phillips__MP.png",
  "G PHILLIPS": "/assets/players/glenn_phillips__MP.png",
  "NATHAN SMITH": "/assets/players/nathan_smith__4X2.png",
  "N SMITH": "/assets/players/nathan_smith__4X2.png",
  "KYLE JAMIESON": "/assets/players/kyle_jamieson__13F.png",
  "K JAMIESON": "/assets/players/kyle_jamieson__13F.png",
  "MATT HENRY": "/assets/players/matt_henry__AS.png",
  "M HENRY": "/assets/players/matt_henry__AS.png",
  "JACOB DUFFY": "/assets/players/jacob_duffy__4X4.png",
  "J DUFFY": "/assets/players/jacob_duffy__4X4.png",
  "YASHASVI JAISWAL": "/assets/players/yashasvi_jaiswal__15K.png",
  "Y JAISWAL": "/assets/players/yashasvi_jaiswal__15K.png",
  "KL RAHUL": "/assets/players/kl_rahul__AK.png",
  "K RAHUL": "/assets/players/kl_rahul__AK.png",
  "DEVDUTT PADIKKAL": "/assets/players/devdutt_padikkal__EI.png",
  "D PADIKKAL": "/assets/players/devdutt_padikkal__EI.png",
  "SHUBMAN GILL": "/assets/players/shubman_gill__O5.png",
  "S GILL": "/assets/players/shubman_gill__O5.png",
  "RISHABH PANT": "/assets/players/rishabh_pant__CL.png",
  "R PANT": "/assets/players/rishabh_pant__CL.png",
  "DHRUV JUREL": "/assets/players/dhruv_jurel__16J.png",
  "D JUREL": "/assets/players/dhruv_jurel__16J.png",
  "WASHINGTON SUNDAR": "/assets/players/washington_sundar__LQ.png",
  "W SUNDAR": "/assets/players/washington_sundar__LQ.png",
  "ANSHUL KAMBOJ": "/assets/players/anshul_kamboj__8C5.png",
  "A KAMBOJ": "/assets/players/anshul_kamboj__8C5.png",
  "JASPRIT BUMRAH": "/assets/players/jasprit_bumrah__AJ.png",
  "J BUMRAH": "/assets/players/jasprit_bumrah__AJ.png",
  "AKASH DEEP": "/assets/players/akash_deep__5KW.png",
  "A DEEP": "/assets/players/akash_deep__5KW.png",
  "GURNOOR BRAR": "/assets/players/gurnoor_brar__7O3.png",
  "G BRAR": "/assets/players/gurnoor_brar__7O3.png",
  "A SHARMA": "/assets/players/abhishek_sharma__1DH.png",
  "ABHISHEK SHARMA": "/assets/players/abhishek_sharma__1DH.png",
  "V SOORYAVANSHI": "/assets/players/v_sooryavanshi__DBT.png",
  "VAIBHAV SOORYAVANSHI": "/assets/players/v_sooryavanshi__DBT.png",
  "R FERNANDO": "/assets/players/ravindu_fernando__7NT.png",
  "RAVINDU FERNANDO": "/assets/players/ravindu_fernando__7NT.png",
  "H RANA": "/assets/players/h_rana__8OH.png",
  "HARSHIT RANA": "/assets/players/h_rana__8OH.png",
  "H DUBEY": "/assets/players/h_dubey__62Y.png",
  "HARSH DUBEY": "/assets/players/h_dubey__62Y.png",
  "S AHMED": "/assets/players/s_ahmed__1D8.png",
  "SHAHBAZ AHMED": "/assets/players/s_ahmed__1D8.png",
  "S SHEDGE": "/assets/players/s_shedge__A23.png",
  "SURYANSH SHEDGE": "/assets/players/s_shedge__A23.png",
  "T KOTIAN": "/assets/players/t_kotian__63B.png",
  "TANUSH KOTIAN": "/assets/players/t_kotian__63B.png",
  "T VARMA": "/assets/players/tilak_varma__15Q.png",
  "TILAK VARMA": "/assets/players/tilak_varma__15Q.png",
  "K KUSHAGRA": "/assets/players/k_kushagra__177.png",
  "KUMAR KUSHAGRA": "/assets/players/k_kushagra__177.png",
  "J LIYANAGE": "/assets/players/janith_liyanage__7NM.png",
  "JANITH LIYANAGE": "/assets/players/janith_liyanage__7NM.png",
  "L SAMARAKOON": "/assets/players/lahiru_samarakoon__4XW.png",
  "L CROOSPULLE": "/assets/players/lasith_croospulle__6UP.png",
  "N DHANANJAYA": "/assets/players/nipun_dhananjaya__179.png",
  "N MADUSHKA": "/assets/players/nishan_madushka__4XU.png",
  "P RATHNAYAKE": "/assets/players/pavan_rathnayake__6UY.png",
  "R SINGH": "/assets/players/r_singh__DR.png",
  "S JAYAWARDENA": "/assets/players/sineth_jayawardena__D1N.png",
  "V VIYASKANTH": "/assets/players/vijayakanth_viyaskanth__5G5.png",
  "W SAHAN": "/assets/players/wanuja_sahan__7XV.png",
  "G SANKETH": "/assets/players/garuka_sanketh__D1V.png",
  "A KHAN": "/assets/players/a_khan__5SH.png",
  "ARSHAD KHAN": "/assets/players/a_khan__5SH.png",
  "RINKU SINGH": "/assets/players/r_singh__DR.png",
};

// Real photographs used ONLY inside the Player Card drawer
const REAL_PLAYER_IMAGES = {
  "AFIF HOSSAIN": "/assets/players/real/afif_hossain.png",
  "A HOSSAIN": "/assets/players/real/afif_hossain.png",
  "MAHMUDUL HASAN JOY": "/assets/players/real/mahmudul_hasan_joy.png",
  "M H JOY": "/assets/players/real/mahmudul_hasan_joy.png",
  "SABBIR RAHMAN": "/assets/players/real/sabbir_rahman.png",
  "S RAHMAN": "/assets/players/real/sabbir_rahman.png",
  "MAHIDUL ISLAM ANKON": "/assets/players/real/mahidul_islam_ankon.png",
  "M I ANKON": "/assets/players/real/mahidul_islam_ankon.png",
  "RAKIBUL HASAN": "/assets/players/real/rakibul_hasan.png",
  "R HASAN": "/assets/players/real/rakibul_hasan.png",
  "IQBAL HOSSAIN EMON": "/assets/players/real/iqbal_hossain_emon.png",
  "I H EMMON": "/assets/players/real/iqbal_hossain_emon.png",
  "I H EMON": "/assets/players/real/iqbal_hossain_emon.png",
  "PARVEZ HOSSAIN EMON": "/assets/players/real/parvez_hossain_emon.png",
  "MD SAMIUN BASIR RATUL": "/assets/players/real/md_samiun_basir_ratul.png",
  "YASIR ALI": "/assets/players/real/yasir_ali.png",
  "MOHAMMAD SAIFUDDIN": "/assets/players/real/mohammad_saifuddin.png",
  "ROHAIL NAZIR": "/assets/players/real/rohail_nazir.png",
  "R NAZIR": "/assets/players/real/rohail_nazir.png",
  "FARHAN YOUSAF": "/assets/players/real/farhan_yousaf.png",
  "F YOUSAF": "/assets/players/real/farhan_yousaf.png",
  "ALI RAZA": "/assets/players/real/ali_raza.png",
  "A RAZA": "/assets/players/real/ali_raza.png",
  "HAIDER ALI": "/assets/players/real/haider_ali.png",
  "MOHAMMAD HASNAIN": "/assets/players/real/mohammad_hasnain.png",
  "TOM LATHAM": "/assets/players/real/tom_latham.png",
  "T LATHAM": "/assets/players/real/tom_latham.png",
  "DEVON CONWAY": "/assets/players/real/devon_conway.png",
  "D CONWAY": "/assets/players/real/devon_conway.png",
  "HENRY NICHOLLS": "/assets/players/real/henry_nicholls.png",
  "H NICHOLLS": "/assets/players/real/henry_nicholls.png",
  "RACHIN RAVINDRA": "/assets/players/real/rachin_ravindra.png",
  "R RAVINDRA": "/assets/players/real/rachin_ravindra.png",
  "DARYL MITCHELL": "/assets/players/real/daryl_mitchell.png",
  "D MITCHELL": "/assets/players/real/daryl_mitchell.png",
  "TOM BLUNDELL": "/assets/players/real/tom_blundell.png",
  "T BLUNDELL": "/assets/players/real/tom_blundell.png",
  "GLENN PHILLIPS": "/assets/players/real/glenn_phillips.png",
  "G PHILLIPS": "/assets/players/real/glenn_phillips.png",
  "NATHAN SMITH": "/assets/players/real/nathan_smith.png",
  "N SMITH": "/assets/players/real/nathan_smith.png",
  "KYLE JAMIESON": "/assets/players/real/kyle_jamieson.png",
  "K JAMIESON": "/assets/players/real/kyle_jamieson.png",
  "MATT HENRY": "/assets/players/real/matt_henry.png",
  "M HENRY": "/assets/players/real/matt_henry.png",
  "JACOB DUFFY": "/assets/players/real/jacob_duffy.png",
  "J DUFFY": "/assets/players/real/jacob_duffy.png",
  "YASHASVI JAISWAL": "/assets/players/real/yashasvi_jaiswal.png",
  "Y JAISWAL": "/assets/players/real/yashasvi_jaiswal.png",
  "KL RAHUL": "/assets/players/real/kl_rahul.png",
  "K RAHUL": "/assets/players/real/kl_rahul.png",
  "DEVDUTT PADIKKAL": "/assets/players/real/devdutt_padikkal.png",
  "D PADIKKAL": "/assets/players/real/devdutt_padikkal.png",
  "SHUBMAN GILL": "/assets/players/real/shubman_gill.png",
  "S GILL": "/assets/players/real/shubman_gill.png",
  "RISHABH PANT": "/assets/players/real/rishabh_pant.png",
  "R PANT": "/assets/players/real/rishabh_pant.png",
  "DHRUV JUREL": "/assets/players/real/dhruv_jurel.png",
  "D JUREL": "/assets/players/real/dhruv_jurel.png",
  "WASHINGTON SUNDAR": "/assets/players/real/washington_sundar.png",
  "W SUNDAR": "/assets/players/real/washington_sundar.png",
  "ANSHUL KAMBOJ": "/assets/players/real/anshul_kamboj.png",
  "A KAMBOJ": "/assets/players/real/anshul_kamboj.png",
  "JASPRIT BUMRAH": "/assets/players/real/jasprit_bumrah.png",
  "J BUMRAH": "/assets/players/real/jasprit_bumrah.png",
  "AKASH DEEP": "/assets/players/real/akash_deep.png",
  "A DEEP": "/assets/players/real/akash_deep.png",
  "GURNOOR BRAR": "/assets/players/real/gurnoor_brar.png",
  "G BRAR": "/assets/players/real/gurnoor_brar.png",
  "A SHARMA": "/assets/players/real/abhishek_sharma.jpg",
  "ABHISHEK SHARMA": "/assets/players/real/abhishek_sharma.jpg",
  "V SOORYAVANSHI": "/assets/players/real/vaibhav_sooryavanshi.jpg",
  "VAIBHAV SOORYAVANSHI": "/assets/players/real/vaibhav_sooryavanshi.jpg",
  "T VARMA": "/assets/players/real/tilak_varma.jpg",
  "TILAK VARMA": "/assets/players/real/tilak_varma.jpg",
  "K KUSHAGRA": "/assets/players/real/kumar_kushagra.png",
  "KUMAR KUSHAGRA": "/assets/players/real/kumar_kushagra.png",
  "R SINGH": "/assets/players/real/rinku_singh.png",
  "RINKU SINGH": "/assets/players/real/rinku_singh.png",
  "S AHMED": "/assets/players/real/shahbaz_ahmed.png",
  "SHAHBAZ AHMED": "/assets/players/real/shahbaz_ahmed.png",
  "S SHEDGE": "/assets/players/real/suryansh_shedge.jpg",
  "SURYANSH SHEDGE": "/assets/players/real/suryansh_shedge.jpg",
  "T KOTIAN": "/assets/players/real/tanush_kotian.png",
  "TANUSH KOTIAN": "/assets/players/real/tanush_kotian.png",
  "H DUBEY": "/assets/players/real/harsh_dubey.png",
  "HARSH DUBEY": "/assets/players/real/harsh_dubey.png",
  "H RANA": "/assets/players/real/harshit_rana.jpg",
  "HARSHIT RANA": "/assets/players/real/harshit_rana.jpg",
  "A KHAN": "/assets/players/real/arshad_khan.png",
  "ARSHAD KHAN": "/assets/players/real/arshad_khan.png",
  "N MADUSHKA": "/assets/players/real/nishan_madushka.jpg",
  "NISHAN MADUSHKA": "/assets/players/real/nishan_madushka.jpg",
  "L CROOSPULLE": "/assets/players/real/lasith_croospulle.png",
  "LASITH CROOSPULLE": "/assets/players/real/lasith_croospulle.png",
  "N DHANANJAYA": "/assets/players/real/nipun_dhananjaya.jpg",
  "NIPUN DHANANJAYA": "/assets/players/real/nipun_dhananjaya.jpg",
  "P RATHNAYAKE": "/assets/players/real/pavan_rathnayake.jpg",
  "PAVAN RATHNAYAKE": "/assets/players/real/pavan_rathnayake.jpg",
  "J LIYANAGE": "/assets/players/real/janith_liyanage.jpg",
  "JANITH LIYANAGE": "/assets/players/real/janith_liyanage.jpg",
  "W SAHAN": "/assets/players/real/wanuja_sahan.jpg",
  "WANUJA SAHAN": "/assets/players/real/wanuja_sahan.jpg",
  "L SAMARAKOON": "/assets/players/real/lahiru_samarakoon.jpg",
  "LAHIRU SAMARAKOON": "/assets/players/real/lahiru_samarakoon.jpg",
  "R FERNANDO": "/assets/players/real/ravindu_fernando.jpg",
  "RAVINDU FERNANDO": "/assets/players/real/ravindu_fernando.jpg",
  "V VIYASKANTH": "/assets/players/real/vijayakanth_viyaskanth.jpg",
  "VIJAYAKANTH VIYASKANTH": "/assets/players/real/vijayakanth_viyaskanth.jpg",
  "G SANKETH": "/assets/players/real/garuka_sanketh.png",
  "GARUKA SANKETH": "/assets/players/real/garuka_sanketh.png",
  "S JAYAWARDENA": "/assets/players/real/sineth_jayawardena.jpg",
  "SINETH JAYAWARDENA": "/assets/players/real/sineth_jayawardena.jpg",
};

let currentState = null;
let liveStateCache = null;
let playerImageDb = { ...BUILTIN_PLAYER_IMAGES };
let lastPlayerNames = { striker: "", nonStriker: "", bowler: "" };
let previewMode = false;
let prematchMode = false;
let prematchSecondsLeft = 26 * 60 + 22;
let prematchTimer = null;
let autoPlayToss = false;
let autoPlayPitch = false;
let autoPlayWeather = false;
let tossRevealTimer = null;
const tossConfig = {
  winnerSide: "left",
  choice: "BAT",
  face: "HEADS",
};

(function initScaleAndControls() {
  const params = new URLSearchParams(location.search);
  if (params.get("transparent") === "1") {
    document.body.classList.add("transparent-mode");
  }
  if (params.get("controls") === "1") {
    document.body.classList.add("show-controls");
  }
  if (params.get("preview") === "1") {
    previewMode = true;
  }
  if (params.get("toss") === "1") {
    autoPlayToss = true;
  }
  if (params.get("prematch") === "1") {
    prematchMode = true;
  }
  if (params.get("pitch") === "1") {
    autoPlayPitch = true;
  }
  if (params.get("weather") === "1") {
    autoPlayWeather = true;
  }

  const updateScale = () => {
    const s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    document.documentElement.style.setProperty("--embed-scale", String(s));
  };
  updateScale();
  window.addEventListener("resize", updateScale);

  const btnTrans = document.getElementById("btnToggleTransparent");
  const syncTransBtn = () => {
    if (btnTrans) {
      btnTrans.textContent = `OBS Transparent: ${document.body.classList.contains("transparent-mode") ? "ON" : "OFF"}`;
    }
  };
  syncTransBtn();
  if (btnTrans) {
    btnTrans.addEventListener("click", () => {
      document.body.classList.toggle("transparent-mode");
      syncTransBtn();
    });
  }

  const btnPrev = document.getElementById("btnTogglePreview");
  const syncPrevBtn = () => {
    if (btnPrev) {
      btnPrev.textContent = `Reference Match: ${previewMode ? "ON" : "OFF"}`;
    }
  };
  syncPrevBtn();
  if (btnPrev) {
    btnPrev.addEventListener("click", () => {
      previewMode = !previewMode;
      syncPrevBtn();
      if (previewMode) {
        applyState(REFERENCE_PREVIEW_STATE);
      } else if (liveStateCache) {
        applyState(liveStateCache);
      }
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAllModals();
    } else if (e.key.toLowerCase() === "c" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      document.body.classList.toggle("show-controls");
    } else if (e.key.toLowerCase() === "t" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      const tossModal = document.getElementById("tossModal");
      if (tossModal && !tossModal.hidden) {
        closeAllModals();
      } else {
        openTossModal();
      }
    } else if (e.key.toLowerCase() === "p" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      setPrematchMode(!prematchMode);
    } else if (e.key.toLowerCase() === "r" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      const pitchModal = document.getElementById("pitchModal");
      if (pitchModal && !pitchModal.hidden) {
        closeAllModals();
      } else {
        openPitchModal();
      }
    } else if (e.key.toLowerCase() === "w" && !["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName)) {
      const weatherModal = document.getElementById("weatherModal");
      if (weatherModal && !weatherModal.hidden) {
        closeAllModals();
      } else {
        openWeatherModal();
      }
    }
  });
})();

function getInitials(name) {
  const parts = String(name || "").trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function resolvePlayerPhoto(name) {
  const clean = String(name || "")
    .replace(/\((?:c|wk|vc)\)/gi, "")
    .replace(/[^a-z0-9\s]/gi, " ")
    .trim()
    .toUpperCase()
    .replace(/\s+/g, " ");
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

const FLAG_IMAGE_MAP = [
  [/^AFG|AFGHANISTAN/, "/assets/flags/afg.png"],
  [/^AUS|AUSTRALIA/, "/assets/flags/aus.png"],
  [/^BAN|BANGLADESH/, "/assets/flags/ban.jpg"],
  [/^ENG|ENGLAND/, "/assets/flags/eng.png"],
  [/^IND|INDIA/, "/assets/flags/ind.png"],
  [/^NEP|NEPAL/, "/assets/flags/nep.png"],
  [/^NZ|NEW ZEALAND/, "/assets/flags/nz.png"],
  [/^PAK|PAKISTAN/, "/assets/flags/pak.png"],
  [/^SA\b|SOUTH AFRICA/, "/assets/flags/sa.png"],
  [/^SL|SRI LANKA/, "/assets/flags/sl.png"],
  [/^NED|NETHERLANDS|HOLLAND/, "/assets/flags/ned.png"],
];

function getFlagSvg(teamName) {
  const t = (teamName || "").trim().toUpperCase();
  for (const [pattern, src] of FLAG_IMAGE_MAP) {
    if (pattern.test(t)) {
      return `<img class="flag-img" src="${src}" alt="${escapeHtml(t)}" />`;
    }
  }
  if (t === "UAE" || t.includes("EMIRATES")) {
    return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="16" height="40" fill="#ce1126"/><rect x="16" width="44" height="13.4" fill="#00732f"/><rect x="16" y="13.3" width="44" height="13.4" fill="#ffffff"/><rect x="16" y="26.6" width="44" height="13.4" fill="#111111"/></svg>`;
  }
  return `<svg class="flag-svg" viewBox="0 0 60 40" preserveAspectRatio="none"><rect width="60" height="40" fill="#1e293b"/><text x="30" y="25" text-anchor="middle" fill="#facc15" font-size="14" font-weight="bold" font-family="sans-serif">${t.slice(0, 3)}</text></svg>`;
}

function getJerseyColors(teamName) {
  const t = (teamName || "").toUpperCase();
  if (t.startsWith("IND") || t.includes("INDIA")) return { main: "#1d4ed8", dark: "#1e3a8a", trim: "#f97316" };
  if (t.startsWith("SL") || t.includes("SRI LANKA")) return { main: "#1e40af", dark: "#0f172a", trim: "#facc15" };
  if (t === "AUS" || t.includes("AUSTRALIA")) return { main: "#eab308", dark: "#a16207", trim: "#15803d" };
  if (t === "SA" || t.includes("SOUTH AFRICA")) return { main: "#15803d", dark: "#052e16", trim: "#facc15" };
  if (t.startsWith("PAK") || t.includes("PAKISTAN")) return { main: "#15803d", dark: "#064e3b", trim: "#86efac" };
  if (t === "ENG" || t.includes("ENGLAND")) return { main: "#dc2626", dark: "#7f1d1d", trim: "#3b82f6" };
  if (t === "NZ" || t.includes("NEW ZEALAND")) return { main: "#1e293b", dark: "#090d16", trim: "#e2e8f0" };
  if (t.startsWith("BAN") || t.includes("BANGLADESH")) return { main: "#047857", dark: "#064e3b", trim: "#ef4444" };
  return { main: "#1e3a8a", dark: "#0f172a", trim: "#60a5fa" };
}

function getJerseySvg(teamName) {
  const c = getJerseyColors(teamName);
  return `<svg viewBox="0 0 126 54" width="126" height="54" aria-hidden="true">
    <defs>
      <linearGradient id="jGrad_${c.main.slice(1)}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${c.main}"/>
        <stop offset="100%" stop-color="${c.dark}"/>
      </linearGradient>
    </defs>
    <path d="M8 54 C10 26 26 14 44 10 L52 22 L74 22 L82 10 C100 14 116 26 118 54 Z" fill="url(#jGrad_${c.main.slice(1)})" stroke="rgba(255,255,255,0.22)" stroke-width="1"/>
    <path d="M44 10 L54 24 L63 24 L72 24 L82 10" fill="none" stroke="${c.trim}" stroke-width="3" stroke-linecap="round"/>
    <path d="M18 32 L36 22 M108 32 L90 22" stroke="${c.trim}" stroke-width="2.5" stroke-linecap="round" opacity="0.85"/>
  </svg>`;
}

function resolveRealPlayerPhoto(name) {
  const clean = String(name || "")
    .replace(/\((?:c|wk|vc)\)/gi, "")
    .replace(/[^a-z0-9\s]/gi, " ")
    .trim()
    .toUpperCase()
    .replace(/\s+/g, " ");
  if (!clean) return "";
  if (REAL_PLAYER_IMAGES[clean]) return `${REAL_PLAYER_IMAGES[clean]}?v=58`;
  const parts = clean.split(" ");
  if (parts.length >= 2) {
    const alias = `${parts[0][0]} ${parts[parts.length - 1]}`;
    if (REAL_PLAYER_IMAGES[alias]) return `${REAL_PLAYER_IMAGES[alias]}?v=58`;
  }
  return resolvePlayerPhoto(name);
}

function isIndNzTestMatch() {
  const b1 = String(currentState?.batting_team || "").toUpperCase();
  const b2 = String(currentState?.bowling_team || "").toUpperCase();
  const title = String(currentState?.match_title || "").toUpperCase();
  const teams = `${b1} ${b2} ${title}`;
  return (/\bIND\b|INDIA/.test(teams) && /\bNZ\b|NEW ZEALAND/.test(teams));
}

function setPortrait(imgEl, initialsEl, name, jerseyEl, teamName) {
  const useOriginal = isIndNzTestMatch();
  const photo = useOriginal ? resolveRealPlayerPhoto(name) : resolvePlayerPhoto(name);
  if (initialsEl) initialsEl.textContent = getInitials(name);
  if (jerseyEl) {
    jerseyEl.innerHTML = (photo && !useOriginal) ? getJerseySvg(teamName) : "";
  }
  if (imgEl) {
    imgEl.classList.toggle("real-bust-portrait", Boolean(photo && useOriginal));
    if (photo) {
      imgEl.src = photo;
      imgEl.alt = name || "";
    } else {
      imgEl.removeAttribute("src");
    }
  }
}

let dualSwapTimer = null;

function triggerDualCardSlideSwap(strikerCard, nonStrikerCard) {
  if (!strikerCard || !nonStrikerCard) return;
  if (dualSwapTimer) {
    clearTimeout(dualSwapTimer);
    dualSwapTimer = null;
  }

  strikerCard.classList.remove("player-swap", "player-slide-ltr");
  nonStrikerCard.classList.remove("player-swap", "player-slide-ltr");
  strikerCard.classList.add("bat-hidden");

  const strRect = strikerCard.getBoundingClientRect();
  const nonRect = nonStrikerCard.getBoundingClientRect();
  const deltaX = nonRect.left - strRect.left || 360;

  strikerCard.style.transition = "none";
  nonStrikerCard.style.transition = "none";
  strikerCard.style.transform = `translateX(${deltaX}px)`;
  nonStrikerCard.style.transform = `translateX(${-deltaX}px)`;
  strikerCard.style.zIndex = "5";
  nonStrikerCard.style.zIndex = "4";

  void strikerCard.offsetWidth;

  const ease = "transform 0.65s cubic-bezier(0.22, 1, 0.36, 1)";
  strikerCard.style.transition = ease;
  nonStrikerCard.style.transition = ease;
  strikerCard.style.transform = "translateX(0)";
  nonStrikerCard.style.transform = "translateX(0)";

  dualSwapTimer = setTimeout(() => {
    dualSwapTimer = null;
    strikerCard.style.transition = "";
    nonStrikerCard.style.transition = "";
    strikerCard.style.transform = "";
    nonStrikerCard.style.transform = "";
    strikerCard.style.zIndex = "";
    nonStrikerCard.style.zIndex = "";
    strikerCard.classList.remove("bat-hidden");
  }, 670);
}

function triggerSwapAnimation(cardEl) {
  if (!cardEl) return;
  cardEl.classList.remove("player-swap");
  void cardEl.offsetWidth;
  cardEl.classList.add("player-swap");
}

let overResetTimer = null;
let overResetDoneKey = "";
let trackedPrevOver = null;
let lastCurrOverSnapshot = null;
let lastAnimatedOverTransition = "";
let overRollTimer = null;

function renderSingleOverPill(numEl, listEl, totEl, overObj) {
  if (!overObj) return;
  const overNum = Number(overObj.over_number ?? 1);
  const balls = Array.isArray(overObj.balls) ? overObj.balls : [];
  if (numEl) numEl.textContent = overNum;
  if (totEl) totEl.textContent = `= ${overObj.total ?? 0}`;
  if (listEl) {
    listEl.innerHTML = "";
    balls.forEach((b) => {
      const span = document.createElement("span");
      const val = String(b);
      span.className = "ball-dot-circle";
      if (val === "0" || val === "\u2022") span.classList.add("b-dot");
      else if (val === "4") span.classList.add("b-four");
      else if (val === "6") span.classList.add("b-six");
      else if (val.toUpperCase().includes("W")) span.classList.add("b-wicket");
      else span.classList.add("b-run");
      span.textContent = val;
      listEl.appendChild(span);
    });
  }
}

function triggerOverRollAnimation(prevPill, currPill, transitionKey) {
  if (!currPill || lastAnimatedOverTransition === transitionKey) return;
  lastAnimatedOverTransition = transitionKey;
  if (overRollTimer) {
    clearTimeout(overRollTimer);
    overRollTimer = null;
  }

  if (prevPill && prevPill.style.display !== "none") {
    const prevRect = prevPill.getBoundingClientRect();
    const currRect = currPill.getBoundingClientRect();
    const deltaX = currRect.left - prevRect.left || 240;
    prevPill.style.transition = "none";
    prevPill.style.transform = `translateX(${deltaX}px)`;
    void prevPill.offsetWidth;
    prevPill.style.transition = "transform 0.55s cubic-bezier(0.22, 1, 0.36, 1)";
    prevPill.style.transform = "translateX(0)";
    overRollTimer = setTimeout(() => {
      overRollTimer = null;
      prevPill.style.transition = "";
      prevPill.style.transform = "";
    }, 580);
  }

  currPill.classList.remove("over-slide-in-right");
  void currPill.offsetWidth;
  currPill.classList.add("over-slide-in-right");
}

function renderPrevOverPill(prevOverObj) {
  const prevPill = document.getElementById("prevOverPill");
  if (!prevPill) return;
  const hasBalls = prevOverObj && Array.isArray(prevOverObj.balls) && prevOverObj.balls.length > 0;
  if (!hasBalls) {
    prevPill.style.display = "none";
    return;
  }
  prevPill.style.display = "flex";
  renderSingleOverPill(
    document.getElementById("prevOverNum"),
    document.getElementById("prevOverBalls"),
    document.getElementById("prevOverTotal"),
    prevOverObj
  );
}

function resetOverBallsDisplay(completedOverObj) {
  const nextOverNum = Number(completedOverObj?.over_number ?? 0) + 1;
  if (completedOverObj && Array.isArray(completedOverObj.balls) && completedOverObj.balls.length > 0) {
    trackedPrevOver = {
      over_number: Number(completedOverObj.over_number ?? 1),
      balls: [...completedOverObj.balls],
      total: Number(completedOverObj.total ?? 0),
    };
    renderPrevOverPill(trackedPrevOver);
  }
  renderSingleOverPill(
    document.getElementById("currOverNum"),
    document.getElementById("currOverBalls"),
    document.getElementById("currOverTotal"),
    { over_number: nextOverNum, balls: [], total: 0 }
  );
  triggerOverRollAnimation(
    document.getElementById("prevOverPill"),
    document.getElementById("overTrackerBtn"),
    `roll:${nextOverNum}`
  );
}

function renderOverBalls(currOver, oversStr, prevOver) {
  const numEl = document.getElementById("currOverNum");
  const listEl = document.getElementById("currOverBalls");
  const totEl = document.getElementById("currOverTotal");
  if (!currOver) return;

  const incomingPrev =
    prevOver && Array.isArray(prevOver.balls) && prevOver.balls.length > 0
      ? prevOver
      : trackedPrevOver;

  const ovInfo = parseOversParts(oversStr);
  const overNum = Number(currOver.over_number ?? 1);
  const balls = Array.isArray(currOver.balls) ? currOver.balls : [];
  const isOverComplete = ovInfo.completed > 0 && ovInfo.balls === 0 && overNum === ovInfo.completed && balls.length > 0;
  const stateKey = `${ovInfo.completed}:${overNum}:${balls.join(",")}`;

  const prevSnapNum = Number(lastCurrOverSnapshot?.over_number ?? 0);
  if (prevSnapNum > 0 && overNum > prevSnapNum && Array.isArray(lastCurrOverSnapshot?.balls) && lastCurrOverSnapshot.balls.length > 0) {
    trackedPrevOver = {
      over_number: prevSnapNum,
      balls: [...lastCurrOverSnapshot.balls],
      total: Number(lastCurrOverSnapshot.total ?? 0),
    };
  }

  const effectivePrev =
    prevOver && Array.isArray(prevOver.balls) && prevOver.balls.length > 0 && Number(prevOver.over_number ?? 0) >= Number(trackedPrevOver?.over_number ?? 0)
      ? prevOver
      : trackedPrevOver;

  renderPrevOverPill(effectivePrev);

  if (isOverComplete) {
    if (overResetDoneKey === stateKey) {
      resetOverBallsDisplay(currOver);
      return;
    }
    if (!overResetTimer) {
      overResetTimer = setTimeout(() => {
        overResetTimer = null;
        overResetDoneKey = stateKey;
        resetOverBallsDisplay(currOver);
      }, 3000);
    }
  } else {
    if (overResetTimer) {
      clearTimeout(overResetTimer);
      overResetTimer = null;
    }
    overResetDoneKey = "";
  }

  renderSingleOverPill(numEl, listEl, totEl, currOver);

  if (prevSnapNum > 0 && overNum > prevSnapNum) {
    triggerOverRollAnimation(
      document.getElementById("prevOverPill"),
      document.getElementById("overTrackerBtn"),
      `roll:${overNum}`
    );
  }

  lastCurrOverSnapshot = {
    over_number: overNum,
    balls: [...balls],
    total: Number(currOver.total ?? 0),
  };
}

function formatTickerText(text) {
  const safe = escapeHtml(text);
  return safe.replace(/(AVG:\s*[0-9.]+)/gi, `<span class="ticker-gold">$1</span>`);
}

function renderTicker(data) {
  const track = document.getElementById("tickerTrack");
  if (!track) return;

  let items = Array.isArray(data.ticker_items) && data.ticker_items.length ? data.ticker_items : [];
  if (!items.length && Array.isArray(data.batting_xi) && data.batting_xi.length) {
    items = data.batting_xi;
  }
  if (!items.length) {
    items = ["LIVE CRICKET TELEMETRY", "CLICK FLAGS FOR PLAYING XI", "CLICK ANY PLAYER FOR STATS CARD"];
  }

  const doubled = [...items, ...items, ...items, ...items];
  track.innerHTML = doubled
    .map((text) => `<span>${formatTickerText(text)}</span><span class="ticker-dot"></span>`)
    .join("");
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

let batterOutTimers = { striker: null, nonStriker: null };
let awaitingNewBatter = { striker: false, nonStriker: false };

function triggerSlideLtrAnimation(cardEl) {
  if (!cardEl) return;
  cardEl.classList.remove("player-out-bw", "player-swap", "player-slide-ltr");
  void cardEl.offsetWidth;
  cardEl.classList.add("player-slide-ltr");
}

function renderBatterCardDom(side, b, teamName) {
  const isStriker = side === "striker";
  const prefix = isStriker ? "striker" : "nonStriker";
  const fallbackName = isStriker ? "BATSMAN 1" : "BATSMAN 2";
  document.getElementById(`${prefix}Name`).textContent = b?.name || fallbackName;
  document.getElementById(`${prefix}Runs`).textContent = b?.runs ?? 0;
  document.getElementById(`${prefix}Balls`).textContent = `(${b?.balls ?? 0})`;
  document.getElementById(`${prefix}4s`).textContent = b?.fours ?? 0;
  document.getElementById(`${prefix}6s`).textContent = b?.sixes ?? 0;
  document.getElementById(`${prefix}Sr`).textContent = Number(b?.strike_rate || 0).toFixed(2);
  document.getElementById(`${prefix}Flag`).innerHTML = getFlagSvg(teamName);
  setPortrait(
    document.getElementById(`${prefix}Img`),
    document.getElementById(`${prefix}Initials`),
    b?.name,
    document.getElementById(`${prefix}Jersey`),
    teamName
  );
}

function isBatterDismissed(batter) {
  return Boolean(batter?.dismissal && !/batting|not out|yet to bat/i.test(batter.dismissal));
}

let lockedOutStriker = null; // { key, batter } locked on striker card in B&W until new batsman arrives
let wicketOutTimer = null;
let lastWicketOverlayKey = "";

function hideWicketOutCard() {
  if (wicketOutTimer) {
    clearTimeout(wicketOutTimer);
    wicketOutTimer = null;
  }
  const el = document.getElementById("wicketOutOverlay");
  if (el) el.hidden = true;
}

function showWicketOutCard(batter, teamName) {
  const overlay = document.getElementById("wicketOutOverlay");
  if (!overlay || !batter || !batter.name) return;

  const runs = Number(batter.runs ?? 0);
  const balls = Number(batter.balls ?? 0);
  const fours = Number(batter.fours ?? 0);
  const sixes = Number(batter.sixes ?? 0);
  const sr = Number(batter.strike_rate || (balls > 0 ? (runs / balls) * 100 : 0)).toFixed(2);
  const dismissal = (batter.dismissal && !/batting|not out|yet to bat/i.test(batter.dismissal))
    ? batter.dismissal.toUpperCase()
    : "DISMISSED";

  document.getElementById("woFlag").innerHTML = getFlagSvg(teamName);
  document.getElementById("woTeamCode").textContent = (teamName || "").toUpperCase();
  document.getElementById("woWatermark").textContent = String(runs);
  document.getElementById("woHeadline").textContent = `OUT FOR ${runs}`;
  document.getElementById("woPlayerName").textContent = String(batter.name).toUpperCase();
  document.getElementById("woDismissal").textContent = dismissal;

  const realPhoto = resolveRealPlayerPhoto(batter.name);
  const imgEl = document.getElementById("woImg");
  const initEl = document.getElementById("woInitials");
  if (initEl) initEl.textContent = getInitials(batter.name);
  if (imgEl) {
    if (realPhoto) {
      imgEl.src = realPhoto;
      imgEl.alt = batter.name;
    } else {
      imgEl.removeAttribute("src");
    }
  }

  document.getElementById("woStatsRow").innerHTML = [
    ["RUNS", runs],
    ["BALLS", balls],
    ["4S", fours],
    ["6S", sixes],
    ["SR", sr],
  ].map(([k, v]) => `<div class="wo-stat-box"><div class="wo-stat-k">${k}</div><div class="wo-stat-v">${escapeHtml(v)}</div></div>`).join("");

  overlay.hidden = false;
  if (wicketOutTimer) clearTimeout(wicketOutTimer);
  wicketOutTimer = setTimeout(() => {
    wicketOutTimer = null;
    overlay.hidden = true;
  }, 5000);
}

document.getElementById("wicketOutOverlay")?.addEventListener("click", hideWicketOutCard);

function updateBatterCardWithWicketTransition(side, cardEl, prevBatter, nextBatter, prevPartner, nextPartner, teamName, wicketFell) {
  const prevKey = normalizePlayerKey(prevBatter?.name);
  const nextKey = normalizePlayerKey(nextBatter?.name);
  const prevPartnerKey = normalizePlayerKey(prevPartner?.name);
  const nextPartnerKey = normalizePlayerKey(nextPartner?.name);
  const samePersonRotated = Boolean(nextKey && nextKey === prevPartnerKey);
  const isNewBatter = Boolean(prevKey && nextKey && prevKey !== nextKey && !samePersonRotated);
  const markedOut = Boolean(nextBatter?.dismissal && !/batting|not out/i.test(nextBatter.dismissal));

  // Non-striker card NEVER turns black & white — remains normal color
  if (side !== "striker") {
    cardEl?.classList.remove("player-out-bw");
    if (isNewBatter) {
      renderBatterCardDom(side, nextBatter, teamName);
      triggerSlideLtrAnimation(cardEl);
      return;
    }
    if (prevKey && nextKey && prevKey !== nextKey) {
      triggerSwapAnimation(cardEl);
    }
    renderBatterCardDom(side, nextBatter, teamName);
    return;
  }

  // Striker card: if already locked B&W awaiting new batsman, keep it locked B&W until a brand-new batsman appears
  if (lockedOutStriker) {
    const newBatsmanArrived = Boolean(
      nextKey &&
      nextKey !== lockedOutStriker.key &&
      nextKey !== nextPartnerKey &&
      !markedOut
    );
    if (newBatsmanArrived) {
      lockedOutStriker = null;
      renderBatterCardDom(side, nextBatter, teamName);
      triggerSlideLtrAnimation(cardEl);
    } else {
      renderBatterCardDom(side, lockedOutStriker.batter || nextBatter, teamName);
      cardEl?.classList.remove("player-slide-ltr", "player-swap");
      cardEl?.classList.add("player-out-bw");
    }
    return;
  }

  // Case A: Wicket fell AND new batter already arrived in same poll -> show dismissed striker in B&W for 1.6s, then slide-in new batter LTR
  if (wicketFell && isNewBatter) {
    if (batterOutTimers.striker) clearTimeout(batterOutTimers.striker);
    renderBatterCardDom(side, prevBatter, teamName);
    cardEl?.classList.remove("player-slide-ltr", "player-swap");
    cardEl?.classList.add("player-out-bw");
    batterOutTimers.striker = setTimeout(() => {
      batterOutTimers.striker = null;
      renderBatterCardDom(side, nextBatter, teamName);
      triggerSlideLtrAnimation(cardEl);
    }, 1600);
    return;
  }

  // Case B: Wicket fell (or striker marked out) and replacement hasn't arrived yet -> lock striker card in B&W until new batsman appears
  if (wicketFell || markedOut) {
    const outObj = (prevKey && samePersonRotated) ? prevBatter : (nextBatter || prevBatter);
    const outKey = normalizePlayerKey(outObj?.name) || prevKey || nextKey;
    lockedOutStriker = { key: outKey, batter: outObj };
    renderBatterCardDom(side, outObj, teamName);
    cardEl?.classList.remove("player-slide-ltr", "player-swap");
    cardEl?.classList.add("player-out-bw");
    return;
  }

  if (batterOutTimers.striker) return;
  cardEl?.classList.remove("player-out-bw");
  if (isNewBatter) {
    renderBatterCardDom(side, nextBatter, teamName);
    triggerSlideLtrAnimation(cardEl);
    return;
  }
  if (prevKey && nextKey && prevKey !== nextKey) {
    triggerSwapAnimation(cardEl);
  }
  renderBatterCardDom(side, nextBatter, teamName);
}

function applyState(data) {
  if (!data) return;
  const prevState = currentState;
  const prevOversRaw = prevState ? String(prevState.overs || "0.0") : null;
  currentState = data;
  maybeTriggerOverBreakShowcase(prevOversRaw, data);

  document.getElementById("battingTeamName").textContent = data.batting_team || "BATTING";
  document.getElementById("bowlingTeamName").textContent = data.bowling_team || "BOWLING";
  document.getElementById("battingFlagSvg").innerHTML = getFlagSvg(data.batting_team);
  document.getElementById("bowlingFlagSvg").innerHTML = getFlagSvg(data.bowling_team);

  const scoreEl = document.getElementById("battingScore");
  const nextScore = `${data.runs ?? 0}/${data.wickets ?? 0}`;
  if (scoreEl.textContent !== nextScore) {
    scoreEl.textContent = nextScore;
    scoreEl.classList.remove("score-flash");
    void scoreEl.offsetWidth;
    scoreEl.classList.add("score-flash");
  }
  document.getElementById("battingOvers").textContent = data.overs || "0.0";

  const isSecondInnings = Number(data.target) > 0;
  const inningsBottomEl = document.getElementById("inningsBottom");
  if (inningsBottomEl) {
    inningsBottomEl.textContent = isSecondInnings ? "TW" : "NE";
  }
  const bowlStatus = document.getElementById("bowlingStatus");
  const targetSub = document.getElementById("targetSub");
  if (isSecondInnings) {
    bowlStatus.textContent = `TARGET ${data.target}`;
    const rem = Math.max(0, Number(data.target) - Number(data.runs || 0));
    targetSub.textContent = rem > 0 ? `NEED ${rem} RUNS` : "TARGET REACHED";
    targetSub.style.display = "block";
  } else {
    bowlStatus.textContent = "BOWLING";
    targetSub.style.display = "none";
  }

  const eventPill = document.getElementById("eventPill");
  const tone = data.callout_tone || "neutral";
  if (tone !== "neutral" && data.callout) {
    eventPill.textContent = data.callout;
    eventPill.className = `event-pill show tone-${tone}`;
  } else {
    eventPill.className = "event-pill";
  }

  document.getElementById("statPship").textContent = data.partnership || "0(0)";
  document.getElementById("statCrr").textContent = Number(data.crr || 0).toFixed(2);
  document.getElementById("statRrr").textContent = Number(data.rrr || 0) > 0 ? Number(data.rrr).toFixed(2) : "--";

  const batters = Array.isArray(data.batters_list) && data.batters_list.length
    ? data.batters_list
    : [data.striker, data.non_striker].filter(Boolean);
  const total4s = batters.reduce((acc, b) => acc + Number(b?.fours || 0), 0);
  const total6s = batters.reduce((acc, b) => acc + Number(b?.sixes || 0), 0);
  document.getElementById("statFours").textContent = total4s;
  document.getElementById("statSixes").textContent = total6s;

  renderOverBalls(data.curr_over, data.overs, data.prev_over);

  const s = data.striker || {};
  const ns = data.non_striker || {};
  const wicketFell = Boolean(prevState && Number(data.wickets || 0) > Number(prevState.wickets || 0));
  const lastWicketHint =
    wicketFell && data.last_wicket && data.last_wicket !== prevState?.last_wicket
      ? data.last_wicket
      : "";

  const prevSKey = normalizePlayerKey(prevState?.striker?.name);
  const prevNsKey = normalizePlayerKey(prevState?.non_striker?.name);
  const nextSKey = normalizePlayerKey(s.name);
  const nextNsKey = normalizePlayerKey(ns.name);
  const isTrueStrikeSwap = Boolean(
    !wicketFell &&
    !lockedOutStriker &&
    !awaitingNewBatter.striker &&
    !awaitingNewBatter.nonStriker &&
    prevSKey &&
    prevNsKey &&
    prevSKey !== prevNsKey &&
    nextSKey === prevNsKey &&
    nextNsKey === prevSKey
  );

  const cardStrikerEl = document.getElementById("cardStriker");
  const cardNonStrikerEl = document.getElementById("cardNonStriker");

  lastPlayerNames.striker = s.name || "";
  lastPlayerNames.nonStriker = ns.name || "";

  if (isTrueStrikeSwap) {
    cardStrikerEl?.classList.remove("player-out-bw");
    cardNonStrikerEl?.classList.remove("player-out-bw");
    renderBatterCardDom("striker", s, data.batting_team);
    renderBatterCardDom("nonStriker", ns, data.batting_team);
    triggerDualCardSlideSwap(cardStrikerEl, cardNonStrikerEl);
  } else {
    updateBatterCardWithWicketTransition(
      "striker",
      cardStrikerEl,
      prevState?.striker,
      s,
      prevState?.non_striker,
      ns,
      data.batting_team,
      wicketFell,
      lastWicketHint
    );

    updateBatterCardWithWicketTransition(
      "nonStriker",
      cardNonStrikerEl,
      prevState?.non_striker,
      ns,
      prevState?.striker,
      s,
      data.batting_team,
      wicketFell,
      lastWicketHint
    );
  }

  if (wicketFell) {
    let outBatter = null;
    const prevS = prevState?.striker;
    const prevNs = prevState?.non_striker;
    if (lockedOutStriker?.batter?.name) {
      outBatter = lockedOutStriker.batter;
    } else if (prevS?.name && !playerNamesMatch(prevS.name, s.name) && !playerNamesMatch(prevS.name, ns.name)) {
      outBatter = prevS;
    } else if (prevNs?.name && !playerNamesMatch(prevNs.name, s.name) && !playerNamesMatch(prevNs.name, ns.name)) {
      outBatter = prevNs;
    } else if (isBatterDismissed(s)) {
      outBatter = s;
    } else if (isBatterDismissed(ns)) {
      outBatter = ns;
    }

    if (outBatter?.name) {
      const fromList = (data.batters_list || []).find((b) => playerNamesMatch(b.name, outBatter.name));
      const mergedOut = fromList ? { ...outBatter, ...fromList } : outBatter;
      const wKey = `${data.wickets}:${normalizePlayerKey(mergedOut.name)}`;
      if (wKey !== lastWicketOverlayKey) {
        lastWicketOverlayKey = wKey;
        showWicketOutCard(mergedOut, data.batting_team);
      }
    }
  }

  const bw = data.bowler || {};
  const incomingBowlerKey = normalizePlayerKey(bw.name);
  const prevBowlerKey = normalizePlayerKey(lastPlayerNames.bowler);
  if (prevBowlerKey && incomingBowlerKey && prevBowlerKey !== incomingBowlerKey) {
    triggerSlideLtrAnimation(document.getElementById("cardBowler"));
  }
  const displayBowler = bw;

  lastPlayerNames.bowler = displayBowler.name || "";
  document.getElementById("bowlerName").textContent = displayBowler.name || "BOWLER";
  document.getElementById("bowlerFigs").textContent = `${displayBowler.wickets ?? 0}-${displayBowler.runs_conceded ?? 0}`;
  document.getElementById("bowlerOvers").textContent = `(${displayBowler.overs || "0.0"})`;
  document.getElementById("bowlerEcon").textContent = Number(displayBowler.economy || 0).toFixed(2);
  document.getElementById("bowlerFlag").innerHTML = getFlagSvg(data.bowling_team);
  setPortrait(
    document.getElementById("bowlerImg"),
    document.getElementById("bowlerInitials"),
    displayBowler.name,
    document.getElementById("bowlerJersey"),
    data.bowling_team
  );

  renderTicker(data);
}

/* ===== INTERACTIVE POPUPS (PLAYING XI & PLAYER CARD) ===== */
function closeAllModals() {
  document.getElementById("xiModal").hidden = true;
  document.getElementById("playerModal").hidden = true;
  const tossModal = document.getElementById("tossModal");
  if (tossModal) tossModal.hidden = true;
  const scorecardModal = document.getElementById("scorecardModal");
  if (scorecardModal) scorecardModal.hidden = true;
  const pitchModal = document.getElementById("pitchModal");
  if (pitchModal) pitchModal.hidden = true;
  const weatherModal = document.getElementById("weatherModal");
  if (weatherModal) weatherModal.hidden = true;
  if (tossRevealTimer) {
    clearTimeout(tossRevealTimer);
    tossRevealTimer = null;
  }
  clearOverBreakTimers();
}

function playerNamesMatch(nameA, nameB) {
  const keyA = normalizePlayerKey(nameA);
  const keyB = normalizePlayerKey(nameB);
  if (!keyA || !keyB) return false;
  if (keyA === keyB) return true;
  const partsA = keyA.split(" ");
  const partsB = keyB.split(" ");
  if (partsA.length < 2 || partsB.length < 2) return false;
  const lastA = partsA[partsA.length - 1];
  const lastB = partsB[partsB.length - 1];
  if (lastA !== lastB) return false;
  const firstA = partsA[0];
  const firstB = partsB[0];
  if (firstA.length > 2 && firstB.length > 2) return firstA === firstB;
  return firstA[0] === firstB[0];
}

function findBatterRecord(name) {
  if (!currentState) return null;
  if (playerNamesMatch(currentState.striker?.name, name)) return currentState.striker;
  if (playerNamesMatch(currentState.non_striker?.name, name)) return currentState.non_striker;
  return (currentState.batters_list || []).find((b) => playerNamesMatch(b.name, name)) || null;
}

function findBowlerRecord(name) {
  if (!currentState) return null;
  if (playerNamesMatch(currentState.bowler?.name, name)) return currentState.bowler;
  return (currentState.bowlers_list || []).find((b) => playerNamesMatch(b.name, name)) || null;
}

function openPlayingXI(side) {
  if (!currentState) return;
  closeAllModals();

  const isBatting = side === "batting";
  const teamName = isBatting ? currentState.batting_team : currentState.bowling_team;
  let xiNames = isBatting ? currentState.batting_xi : currentState.bowling_xi;

  if (!Array.isArray(xiNames) || !xiNames.length) {
    if (isBatting) {
      const fromList = (currentState.batters_list || []).map((b) => b.name);
      xiNames = Array.from(new Set([currentState.striker?.name, currentState.non_striker?.name, ...fromList].filter(Boolean)));
    } else {
      const fromList = (currentState.bowlers_list || []).map((b) => b.name);
      xiNames = Array.from(new Set([currentState.bowler?.name, ...fromList].filter(Boolean)));
    }
  }

  document.getElementById("xiModalFlag").innerHTML = getFlagSvg(teamName);
  document.getElementById("xiModalKicker").textContent = isBatting ? "BATTING TEAM SQUAD" : "BOWLING TEAM SQUAD";
  document.getElementById("xiModalTitle").textContent = `${teamName} \u2014 PLAYING XI`;

  const grid = document.getElementById("xiModalGrid");
  grid.innerHTML = "";

  xiNames.slice(0, 11).forEach((rawName) => {
    const isCapt = /\(C\)/i.test(rawName);
    const isWk = /\(WK\)/i.test(rawName);
    const cleanName = rawName.replace(/\((?:C|WK|VC)\)/gi, "").trim();
    const parts = cleanName.split(/\s+/).filter(Boolean);
    const firstName = parts.length > 1 ? parts.slice(0, -1).join(" ") : "";
    const lastName = parts.length > 0 ? parts[parts.length - 1] : cleanName;

    const useOriginal = isIndNzTestMatch();
    const photo = useOriginal ? resolveRealPlayerPhoto(cleanName) : resolvePlayerPhoto(cleanName);
    const bat = findBatterRecord(cleanName);
    const bowl = findBowlerRecord(cleanName);
    let sub = isBatting ? "BATTER" : "BOWLER";
    if (isWk) sub = "WICKET-KEEPER";
    if (bat) {
      const star = playerNamesMatch(currentState.striker?.name, cleanName) ? " \u2605" : "";
      sub = `${bat.runs} (${bat.balls})${star}`;
    } else if (bowl) {
      sub = `${bowl.wickets}-${bowl.runs_conceded} (${bowl.overs})`;
    }

    const badgeHtml = isCapt
      ? `<span class="xi-badge xi-badge-c">C</span>`
      : (isWk ? `<span class="xi-badge xi-badge-wk">WK</span>` : "");

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `xi-card${isCapt ? " is-captain" : ""}`;
    btn.innerHTML = `
      <div class="xi-card-top">
        ${badgeHtml}
        ${photo ? `${useOriginal ? "" : `<div class="xi-jersey">${getJerseySvg(teamName)}</div>`}<img class="xi-portrait${useOriginal ? " real-bust-portrait" : ""}" src="${photo}" alt="${escapeHtml(cleanName)}" />` : `<div class="xi-initials">${getInitials(cleanName)}</div>`}
      </div>
      <div class="xi-card-bottom">
        <div class="xi-fname">${escapeHtml(firstName || " ")}</div>
        <div class="xi-lname">${escapeHtml(lastName)}</div>
        <div class="xi-role">${escapeHtml(sub)}</div>
      </div>
    `;
    btn.addEventListener("click", () => {
      openPlayerCard({
        name: bat?.name || bowl?.name || cleanName,
        team: teamName,
        role: isBatting ? (bat ? "BATTER" : "SQUAD PLAYER") : "BOWLER",
        batter: bat,
        bowler: bowl,
      });
    });
    grid.appendChild(btn);
  });

  document.getElementById("xiModal").hidden = false;
}

function openPlayerCard({ name, team, role, batter, bowler }) {
  closeAllModals();

  document.getElementById("pmFlag").innerHTML = getFlagSvg(team);
  document.getElementById("pmRole").textContent = role || "PLAYER";
  document.getElementById("pmName").textContent = name || "PLAYER";
  document.getElementById("pmTeam").textContent = team || "";
  const realPhoto = resolveRealPlayerPhoto(name);
  const pmImg = document.getElementById("pmImg");
  const pmInit = document.getElementById("pmInitials");
  const pmJersey = document.getElementById("pmJersey");
  if (realPhoto) {
    if (pmJersey) pmJersey.innerHTML = "";
    if (pmInit) pmInit.textContent = getInitials(name);
    if (pmImg) {
      pmImg.src = realPhoto;
      pmImg.alt = name || "";
    }
  } else {
    setPortrait(pmImg, pmInit, name, pmJersey, team);
  }

  const statsGrid = document.getElementById("pmStatsGrid");
  const statusBar = document.getElementById("pmStatus");
  let tiles = [];

  if (bowler && !batter) {
    tiles = [
      ["FIGURES", `${bowler.wickets ?? 0}-${bowler.runs_conceded ?? 0}`],
      ["OVERS", bowler.overs || "0.0"],
      ["ECONOMY", Number(bowler.economy || 0).toFixed(2)],
      ["WICKETS", bowler.wickets ?? 0],
      ["RUNS CONCEDED", bowler.runs_conceded ?? 0],
      ["MAIDENS", bowler.maidens ?? 0],
    ];
    statusBar.textContent = playerNamesMatch(currentState?.bowler?.name, name)
      ? "CURRENTLY BOWLING"
      : "BOWLING SPELL RECORDED";
  } else {
    const b = batter || { runs: 0, balls: 0, fours: 0, sixes: 0, strike_rate: 0, dismissal: "" };
    tiles = [
      ["RUNS", b.runs ?? 0],
      ["BALLS", b.balls ?? 0],
      ["STRIKE RATE", Number(b.strike_rate || 0).toFixed(2)],
      ["FOURS (4s)", b.fours ?? 0],
      ["SIXES (6s)", b.sixes ?? 0],
      ["BOUNDARY RUNS", (b.fours || 0) * 4 + (b.sixes || 0) * 6],
    ];
    const isOut = Boolean(b.dismissal && !/batting|not out|yet to bat/i.test(b.dismissal));
    statusBar.textContent = isOut
      ? `OUT \u2022 ${b.dismissal.toUpperCase()}`
      : (batter ? "AT THE CREASE \u2022 NOT OUT" : "IN PLAYING XI \u2022 YET TO BAT");
  }

  statsGrid.innerHTML = tiles
    .map(([k, v]) => `<div class="pm-stat-box"><div class="pm-stat-k">${k}</div><div class="pm-stat-v">${escapeHtml(v)}</div></div>`)
    .join("");

  document.getElementById("playerModal").hidden = false;
}

document.getElementById("btnBattingFlag").addEventListener("click", () => openPlayingXI("batting"));
document.getElementById("btnBowlingFlag").addEventListener("click", () => openPlayingXI("bowling"));

document.getElementById("cardStriker").addEventListener("click", () => {
  if (!currentState) return;
  openPlayerCard({
    name: currentState.striker?.name,
    team: currentState.batting_team,
    role: "STRIKER",
    batter: currentState.striker,
  });
});

document.getElementById("cardNonStriker").addEventListener("click", () => {
  if (!currentState) return;
  openPlayerCard({
    name: currentState.non_striker?.name,
    team: currentState.batting_team,
    role: "NON-STRIKER",
    batter: currentState.non_striker,
  });
});

document.getElementById("cardBowler").addEventListener("click", () => {
  if (!currentState) return;
  openPlayerCard({
    name: currentState.bowler?.name,
    team: currentState.bowling_team,
    role: "BOWLER",
    bowler: currentState.bowler,
  });
});

function getTossTeams() {
  const left = (currentState && currentState.batting_team) || REFERENCE_PREVIEW_STATE.batting_team || "INDIA A";
  const right = (currentState && currentState.bowling_team) || REFERENCE_PREVIEW_STATE.bowling_team || "SRI LANKA A";
  return { left, right };
}

function updateTossDecisionText() {
  const { left, right } = getTossTeams();
  const winnerTeam = tossConfig.winnerSide === "left" ? left : right;
  const decisionEl = document.getElementById("tossDecisionText");
  const choiceBtn = document.getElementById("btnToggleTossChoice");
  if (decisionEl) {
    decisionEl.textContent = `${winnerTeam} WON THE TOSS & ELECTED TO ${tossConfig.choice} FIRST`;
  }
  if (choiceBtn) {
    choiceBtn.textContent = `Choice: ${tossConfig.choice}`;
  }
}

function openTossModal() {
  closeAllModals();
  const modal = document.getElementById("tossModal");
  if (!modal) return;

  const { left, right } = getTossTeams();
  const leftCard = document.getElementById("tossTeamLeft");
  const rightCard = document.getElementById("tossTeamRight");
  const resultEl = document.getElementById("tossCoinResult");

  document.getElementById("tossFlagLeft").innerHTML = getFlagSvg(left);
  document.getElementById("tossFlagRight").innerHTML = getFlagSvg(right);
  document.getElementById("tossNameLeft").textContent = left;
  document.getElementById("tossNameRight").textContent = right;

  const callFace = tossConfig.face;
  document.getElementById("tossCallLeft").textContent =
    tossConfig.winnerSide === "left" ? `CALLS ${callFace}` : "AWAITING CALL";
  document.getElementById("tossCallRight").textContent =
    tossConfig.winnerSide === "right" ? `CALLS ${callFace}` : "AWAITING CALL";

  leftCard.classList.remove("is-winner", "is-loser");
  rightCard.classList.remove("is-winner", "is-loser");
  modal.classList.remove("is-flipping", "is-revealed", "land-heads", "land-tails");

  if (resultEl) resultEl.textContent = "FLIPPING...";
  updateTossDecisionText();

  modal.hidden = false;
  void modal.offsetWidth;

  modal.classList.add(
    "is-flipping",
    tossConfig.face === "TAILS" ? "land-tails" : "land-heads"
  );

  tossRevealTimer = setTimeout(() => {
    if (resultEl) resultEl.textContent = tossConfig.face;
    modal.classList.add("is-revealed");
    if (tossConfig.winnerSide === "left") {
      leftCard.classList.add("is-winner");
      rightCard.classList.add("is-loser");
    } else {
      rightCard.classList.add("is-winner");
      leftCard.classList.add("is-loser");
    }
    tossRevealTimer = null;
  }, 2250);
}

function normalizePlayerKey(name) {
  return String(name || "")
    .replace(/\((?:c|wk|vc)\)/gi, "")
    .replace(/[^a-z0-9\s]/gi, " ")
    .trim()
    .toUpperCase()
    .replace(/\s+/g, " ");
}

function openScorecardModal() {
  const data = currentState || REFERENCE_PREVIEW_STATE;
  closeAllModals();
  const modal = document.getElementById("scorecardModal");
  if (!modal) return;

  const battingTeam = data.batting_team || "BATTING";
  const bowlingTeam = data.bowling_team || "BOWLING";
  const crr = Number(data.crr || 0).toFixed(2);
  const oversText = data.overs || "0.0";

  document.getElementById("scBattingFlag").innerHTML = getFlagSvg(battingTeam);
  document.getElementById("scBattingTeam").textContent = battingTeam;
  document.getElementById("scTotalScore").textContent = `${data.runs ?? 0}/${data.wickets ?? 0}`;
  document.getElementById("scTotalOvers").textContent = `${oversText} OVERS \u2022 CRR ${crr}`;

  document.getElementById("scBowlingFlag").innerHTML = getFlagSvg(bowlingTeam);
  document.getElementById("scBowlingTeam").textContent = `${bowlingTeam} \u2014 BOWLING`;
  document.getElementById("scOversDelivered").textContent = `${oversText} OVERS DELIVERED`;

  // Merge batters_list with active striker & non-striker so playing batters always appear
  const battersMap = new Map();
  const addBatter = (b, forceActiveRole = "") => {
    if (!b || !b.name) return;
    const key = normalizePlayerKey(b.name);
    const prev = battersMap.get(key) || {};
    battersMap.set(key, {
      ...prev,
      ...b,
      activeRole: forceActiveRole || prev.activeRole || "",
    });
  };
  (data.batters_list || []).forEach((b) => addBatter(b));
  addBatter(data.striker, "STRIKER");
  addBatter(data.non_striker, "NON-STRIKER");

  const batters = Array.from(battersMap.values());
  const battingBody = document.getElementById("scBattingBody");
  battingBody.innerHTML = "";

  if (!batters.length) {
    battingBody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#94a3b8;padding:18px;">No batting data yet</td></tr>`;
  } else {
    batters.forEach((b) => {
      const isPlaying = Boolean(b.activeRole) || (!b.dismissal && (b.on_strike || normalizePlayerKey(b.name) === normalizePlayerKey(data.striker?.name) || normalizePlayerKey(b.name) === normalizePlayerKey(data.non_striker?.name)));
      const isStriker = b.activeRole === "STRIKER" || normalizePlayerKey(b.name) === normalizePlayerKey(data.striker?.name);
      const tr = document.createElement("tr");
      tr.className = isPlaying ? "is-active" : "is-out";

      const badgeHtml = isPlaying
        ? `<span class="sc-badge ${isStriker ? "playing" : "notout"}">${isStriker ? "STRIKER *" : "NOT OUT"}</span>`
        : `<span class="sc-badge out">OUT</span>`;
      const statusText = isPlaying
        ? (isStriker ? "At the crease (on strike)" : "At the crease")
        : escapeHtml(b.dismissal || "Dismissed");

      tr.innerHTML = `
        <td><span class="sc-player-cell">${escapeHtml(b.name)}${badgeHtml}</span></td>
        <td><span class="sc-status-text">${statusText}</span></td>
        <td>${b.runs ?? 0}</td>
        <td>${b.balls ?? 0}</td>
        <td>${b.fours ?? 0}</td>
        <td>${b.sixes ?? 0}</td>
        <td>${Number(b.strike_rate || 0).toFixed(1)}</td>
      `;
      battingBody.appendChild(tr);
    });
  }

  // Yet to bat: batting_xi minus players already in battersMap
  const xi = Array.isArray(data.batting_xi) ? data.batting_xi : [];
  const yetToBat = xi.filter((name) => !batters.some((b) => playerNamesMatch(b.name, name)));
  const yetEl = document.getElementById("scYetToBat");
  yetEl.innerHTML = yetToBat.length
    ? yetToBat.map((name) => `<span class="sc-yet-chip">${escapeHtml(name)}</span>`).join("")
    : `<span class="sc-status-text">All listed batters have batted</span>`;

  document.getElementById("scBattingSummary").textContent =
    `${batters.length} BATTED \u2022 ${yetToBat.length} YET TO BAT`;

  // Merge bowlers_list with active bowler
  const bowlersMap = new Map();
  const addBowler = (bw, isCurrent = false) => {
    if (!bw || !bw.name) return;
    const key = normalizePlayerKey(bw.name);
    const prev = bowlersMap.get(key) || {};
    bowlersMap.set(key, {
      ...prev,
      ...bw,
      isCurrent: isCurrent || prev.isCurrent || false,
    });
  };
  (data.bowlers_list || []).forEach((bw) => addBowler(bw));
  addBowler(data.bowler, true);

  const bowlers = Array.from(bowlersMap.values());
  const bowlingBody = document.getElementById("scBowlingBody");
  bowlingBody.innerHTML = "";

  if (!bowlers.length) {
    bowlingBody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#94a3b8;padding:18px;">No bowling data yet</td></tr>`;
  } else {
    bowlers.forEach((bw) => {
      const tr = document.createElement("tr");
      if (bw.isCurrent) tr.className = "is-active";
      const badgeHtml = bw.isCurrent ? `<span class="sc-badge bowling">BOWLING</span>` : "";
      tr.innerHTML = `
        <td><span class="sc-player-cell">${escapeHtml(bw.name)}${badgeHtml}</span></td>
        <td>${escapeHtml(bw.overs || "0.0")}</td>
        <td>${bw.maidens ?? 0}</td>
        <td>${bw.runs_conceded ?? 0}</td>
        <td>${bw.wickets ?? 0}</td>
        <td>${Number(bw.economy || 0).toFixed(2)}</td>
      `;
      bowlingBody.appendChild(tr);
    });
  }

  const bowlFooter = document.getElementById("scBowlFooter");
  if (bowlFooter) {
    const curName = data.bowler?.name ? `CURRENT: ${escapeHtml(data.bowler.name)}` : "BOWLING ATTACK";
    const targetTxt = Number(data.target) > 0 ? `TARGET: ${data.target}` : `CRR: ${crr}`;
    bowlFooter.innerHTML = `<span>${curName}</span><span>${targetTxt}</span>`;
  }

  modal.hidden = false;
}

document.getElementById("prevOverPill")?.addEventListener("click", () => openScorecardModal());
document.getElementById("prevOverPill")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    openScorecardModal();
  }
});
document.getElementById("overTrackerBtn")?.addEventListener("click", () => openScorecardModal());
document.getElementById("overTrackerBtn")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    openScorecardModal();
  }
});

function formatCountdown(totalSec) {
  const s = Math.max(0, Math.floor(totalSec));
  const hrs = String(Math.floor(s / 3600)).padStart(2, "0");
  const mins = String(Math.floor((s % 3600) / 60)).padStart(2, "0");
  const secs = String(s % 60).padStart(2, "0");
  return `${hrs}:${mins}:${secs}`;
}

const CAPTAIN_CUTOUT_IMAGES = {
  "A SHARMA": "/assets/players/cutout/abhishek_sharma.png",
  "ABHISHEK SHARMA": "/assets/players/cutout/abhishek_sharma.png",
  "V SOORYAVANSHI": "/assets/players/cutout/vaibhav_sooryavanshi.png",
  "VAIBHAV SOORYAVANSHI": "/assets/players/cutout/vaibhav_sooryavanshi.png",
  "T VARMA": "/assets/players/cutout/tilak_varma.png",
  "TILAK VARMA": "/assets/players/cutout/tilak_varma.png",
  "K KUSHAGRA": "/assets/players/cutout/kumar_kushagra.png",
  "KUMAR KUSHAGRA": "/assets/players/cutout/kumar_kushagra.png",
  "R SINGH": "/assets/players/cutout/rinku_singh.png",
  "RINKU SINGH": "/assets/players/cutout/rinku_singh.png",
  "S AHMED": "/assets/players/cutout/shahbaz_ahmed.png",
  "SHAHBAZ AHMED": "/assets/players/cutout/shahbaz_ahmed.png",
  "S SHEDGE": "/assets/players/cutout/suryansh_shedge.png",
  "SURYANSH SHEDGE": "/assets/players/cutout/suryansh_shedge.png",
  "T KOTIAN": "/assets/players/cutout/tanush_kotian.png",
  "TANUSH KOTIAN": "/assets/players/cutout/tanush_kotian.png",
  "H DUBEY": "/assets/players/cutout/harsh_dubey.png",
  "HARSH DUBEY": "/assets/players/cutout/harsh_dubey.png",
  "H RANA": "/assets/players/cutout/harshit_rana.png",
  "HARSHIT RANA": "/assets/players/cutout/harshit_rana.png",
  "A KHAN": "/assets/players/cutout/arshad_khan.png",
  "ARSHAD KHAN": "/assets/players/cutout/arshad_khan.png",
  "J LIYANAGE": "/assets/players/cutout/janith_liyanage.png",
  "JANITH LIYANAGE": "/assets/players/cutout/janith_liyanage.png",
  "L SAMARAKOON": "/assets/players/cutout/lahiru_samarakoon.png",
  "LAHIRU SAMARAKOON": "/assets/players/cutout/lahiru_samarakoon.png",
  "L CROOSPULLE": "/assets/players/cutout/lasith_croospulle.png",
  "LASITH CROOSPULLE": "/assets/players/cutout/lasith_croospulle.png",
  "P RATHNAYAKE": "/assets/players/cutout/pavan_rathnayake.png",
  "PAVAN RATHNAYAKE": "/assets/players/cutout/pavan_rathnayake.png",
  "TOM LATHAM": "/assets/players/cutout/tom_latham.png",
  "T LATHAM": "/assets/players/cutout/tom_latham.png",
  "DEVON CONWAY": "/assets/players/cutout/devon_conway.png",
  "D CONWAY": "/assets/players/cutout/devon_conway.png",
  "HENRY NICHOLLS": "/assets/players/cutout/henry_nicholls.png",
  "H NICHOLLS": "/assets/players/cutout/henry_nicholls.png",
  "RACHIN RAVINDRA": "/assets/players/cutout/rachin_ravindra.png",
  "R RAVINDRA": "/assets/players/cutout/rachin_ravindra.png",
  "DARYL MITCHELL": "/assets/players/cutout/daryl_mitchell.png",
  "D MITCHELL": "/assets/players/cutout/daryl_mitchell.png",
  "TOM BLUNDELL": "/assets/players/cutout/tom_blundell.png",
  "T BLUNDELL": "/assets/players/cutout/tom_blundell.png",
  "GLENN PHILLIPS": "/assets/players/cutout/glenn_phillips.png",
  "G PHILLIPS": "/assets/players/cutout/glenn_phillips.png",
  "NATHAN SMITH": "/assets/players/cutout/nathan_smith.png",
  "N SMITH": "/assets/players/cutout/nathan_smith.png",
  "KYLE JAMIESON": "/assets/players/cutout/kyle_jamieson.png",
  "K JAMIESON": "/assets/players/cutout/kyle_jamieson.png",
  "MATT HENRY": "/assets/players/cutout/matt_henry.png",
  "M HENRY": "/assets/players/cutout/matt_henry.png",
  "JACOB DUFFY": "/assets/players/cutout/jacob_duffy.png",
  "J DUFFY": "/assets/players/cutout/jacob_duffy.png",
  "YASHASVI JAISWAL": "/assets/players/cutout/yashasvi_jaiswal.png",
  "Y JAISWAL": "/assets/players/cutout/yashasvi_jaiswal.png",
  "KL RAHUL": "/assets/players/cutout/kl_rahul.png",
  "K RAHUL": "/assets/players/cutout/kl_rahul.png",
  "DEVDUTT PADIKKAL": "/assets/players/cutout/devdutt_padikkal.png",
  "D PADIKKAL": "/assets/players/cutout/devdutt_padikkal.png",
  "SHUBMAN GILL": "/assets/players/cutout/shubman_gill.png",
  "S GILL": "/assets/players/cutout/shubman_gill.png",
  "RISHABH PANT": "/assets/players/cutout/rishabh_pant.png",
  "R PANT": "/assets/players/cutout/rishabh_pant.png",
  "DHRUV JUREL": "/assets/players/cutout/dhruv_jurel.png",
  "D JUREL": "/assets/players/cutout/dhruv_jurel.png",
  "WASHINGTON SUNDAR": "/assets/players/cutout/washington_sundar.png",
  "W SUNDAR": "/assets/players/cutout/washington_sundar.png",
  "ANSHUL KAMBOJ": "/assets/players/cutout/anshul_kamboj.png",
  "A KAMBOJ": "/assets/players/cutout/anshul_kamboj.png",
  "JASPRIT BUMRAH": "/assets/players/cutout/jasprit_bumrah.png",
  "J BUMRAH": "/assets/players/cutout/jasprit_bumrah.png",
  "AKASH DEEP": "/assets/players/cutout/akash_deep.png",
  "A DEEP": "/assets/players/cutout/akash_deep.png",
  "GURNOOR BRAR": "/assets/players/cutout/gurnoor_brar.png",
  "G BRAR": "/assets/players/cutout/gurnoor_brar.png",
  "AFIF HOSSAIN": "/assets/players/cutout/afif_hossain.png",
  "A HOSSAIN": "/assets/players/cutout/afif_hossain.png",
  "MAHMUDUL HASAN JOY": "/assets/players/cutout/mahmudul_hasan_joy.png",
  "M H JOY": "/assets/players/cutout/mahmudul_hasan_joy.png",
  "SABBIR RAHMAN": "/assets/players/cutout/sabbir_rahman.png",
  "S RAHMAN": "/assets/players/cutout/sabbir_rahman.png",
  "MAHIDUL ISLAM ANKON": "/assets/players/cutout/mahidul_islam_ankon.png",
  "M I ANKON": "/assets/players/cutout/mahidul_islam_ankon.png",
  "RAKIBUL HASAN": "/assets/players/cutout/rakibul_hasan.png",
  "R HASAN": "/assets/players/cutout/rakibul_hasan.png",
  "IQBAL HOSSAIN EMON": "/assets/players/cutout/iqbal_hossain_emon.png",
  "I H EMMON": "/assets/players/cutout/iqbal_hossain_emon.png",
  "ROHAIL NAZIR": "/assets/players/cutout/rohail_nazir.png",
  "R NAZIR": "/assets/players/cutout/rohail_nazir.png",
  "FARHAN YOUSAF": "/assets/players/cutout/farhan_yousaf.png",
  "F YOUSAF": "/assets/players/cutout/farhan_yousaf.png",
  "ALI RAZA": "/assets/players/cutout/ali_raza.png",
  "A RAZA": "/assets/players/cutout/ali_raza.png",
  "SAIF HASSAN": "/assets/players/saif_hassan__13U.png",
  "S HASSAN": "/assets/players/saif_hassan__13U.png",
  "ABDUL SAMAD": "/assets/players/abdul_samad__CMY.png",
  "A SAMAD": "/assets/players/abdul_samad__CMY.png",
};

function resolveCaptainCutout(name) {
  const clean = String(name || "")
    .replace(/\((?:c|wk|vc)\)/gi, "")
    .replace(/[^a-z0-9\s]/gi, " ")
    .trim()
    .toUpperCase()
    .replace(/\s+/g, " ");
  if (!clean) return "";
  if (CAPTAIN_CUTOUT_IMAGES[clean]) return `${CAPTAIN_CUTOUT_IMAGES[clean]}?v=58`;
  const parts = clean.split(" ");
  if (parts.length >= 2) {
    const alias = `${parts[0][0]} ${parts[parts.length - 1]}`;
    if (CAPTAIN_CUTOUT_IMAGES[alias]) return `${CAPTAIN_CUTOUT_IMAGES[alias]}?v=58`;
  }
  return "";
}

function updatePrematchOverlay() {
  const data = currentState || REFERENCE_PREVIEW_STATE;
  const leftTeam = data.batting_team || "NZ";
  const rightTeam = data.bowling_team || "IND";

  document.getElementById("pmWaveFlagLeft").innerHTML = getFlagSvg(leftTeam);
  document.getElementById("pmWaveFlagRight").innerHTML = getFlagSvg(rightTeam);
  document.getElementById("pmTeamLeft").textContent = leftTeam;
  document.getElementById("pmTeamRight").textContent = rightTeam;

  const FULL_PLAYER_NAMES = {
    "S HASSAN": "SAIF HASSAN",
    "A HOSSAIN": "AFIF HOSSAIN",
    "S H DIPU": "SHAHADAT HOSSAIN DIPU",
    "M H JOY": "MAHMUDUL HASAN JOY",
    "S RAHMAN": "SABBIR RAHMAN",
    "M I ANKON": "MAHIDUL ISLAM ANKON",
    "R HASAN": "RAKIBUL HASAN",
    "S M M HASAN": "SM MEHEROB HASAN",
    "M RUBEL": "MD RUBEL",
    "R MONDOL": "RIPON MONDOL",
    "I H EMMON": "IQBAL HOSSAIN EMON",
    "S HUSSAIN": "SHAMYL HUSSAIN",
    "M SADAQAT": "MAAZ SADAQAT",
    "S KHAN": "SHAHZAIB KHAN",
    "R NAZIR": "ROHAIL NAZIR",
    "H NAWAZ": "HASAN NAWAZ",
    "A SAMAD": "ABDUL SAMAD",
    "F YOUSAF": "FARHAN YOUSAF",
    "M I RANDHAWA": "MUHAMMAD IMRAN RANDHAWA",
    "A DANIYAL": "AHMED DANIYAL",
    "S MOQIM": "SUFYAN MOQIM",
    "A RAZA": "ALI RAZA",
    "T LATHAM": "TOM LATHAM",
    "D CONWAY": "DEVON CONWAY",
    "H NICHOLLS": "HENRY NICHOLLS",
    "R RAVINDRA": "RACHIN RAVINDRA",
    "D MITCHELL": "DARYL MITCHELL",
    "T BLUNDELL": "TOM BLUNDELL",
    "G PHILLIPS": "GLENN PHILLIPS",
    "N SMITH": "NATHAN SMITH",
    "K JAMIESON": "KYLE JAMIESON",
    "M HENRY": "MATT HENRY",
    "J DUFFY": "JACOB DUFFY",
    "Y JAISWAL": "YASHASVI JAISWAL",
    "K RAHUL": "KL RAHUL",
    "D PADIKKAL": "DEVDUTT PADIKKAL",
    "S GILL": "SHUBMAN GILL",
    "R PANT": "RISHABH PANT",
    "D JUREL": "DHRUV JUREL",
    "W SUNDAR": "WASHINGTON SUNDAR",
    "A KAMBOJ": "ANSHUL KAMBOJ",
    "J BUMRAH": "JASPRIT BUMRAH",
    "A DEEP": "AKASH DEEP",
    "G BRAR": "GURNOOR BRAR",
  };
  const findCaptain = (xi, fallback) => {
    if (!Array.isArray(xi) || !xi.length) return fallback;
    const cap = xi.find((n) => /\(C\)/i.test(n));
    const raw = (cap || xi[0]).replace(/\((?:c|wk|vc)\)/gi, "").trim();
    return FULL_PLAYER_NAMES[raw.toUpperCase()] || raw;
  };
  const capLeft = findCaptain(data.batting_xi, data.striker?.name || "CAPTAIN");
  const capRight = findCaptain(data.bowling_xi, data.bowler?.name || "CAPTAIN");
  document.getElementById("pmCaptainLeft").textContent = capLeft;
  document.getElementById("pmCaptainRight").textContent = capRight;

  const imgLeft = document.getElementById("pmCaptainImgLeft");
  const imgRight = document.getElementById("pmCaptainImgRight");
  const srcLeft = resolveCaptainCutout(capLeft) || resolvePlayerPhoto(capLeft);
  const srcRight = resolveCaptainCutout(capRight) || resolvePlayerPhoto(capRight);
  if (imgLeft) {
    imgLeft.src = srcLeft || "";
    imgLeft.style.display = srcLeft ? "block" : "none";
  }
  if (imgRight) {
    imgRight.src = srcRight || "";
    imgRight.style.display = srcRight ? "block" : "none";
  }

  if (data.match_title) {
    document.getElementById("pmMatchTitle").textContent = String(data.match_title).toUpperCase();
  }
  if (data.venue) {
    document.getElementById("pmVenueName").textContent = String(data.venue).toUpperCase();
  }
  if (data.match_date) {
    const dtEl = document.getElementById("pmDateTime");
    if (dtEl) dtEl.textContent = String(data.match_date).toUpperCase();
  }

  const formatted = formatCountdown(prematchSecondsLeft);
  const topCd = document.getElementById("pmCountdownTop");
  const botCd = document.getElementById("pmCountdownBottom");
  if (topCd) topCd.textContent = formatted;
  if (botCd) botCd.textContent = formatted;
}

function setPrematchMode(enabled) {
  prematchMode = Boolean(enabled);
  document.body.classList.toggle("prematch-mode", prematchMode);

  const overlay = document.getElementById("prematchOverlay");
  const btn = document.getElementById("btnTogglePrematch");
  if (btn) btn.textContent = `Pre-Match: ${prematchMode ? "ON" : "OFF"}`;

  if (prematchMode) {
    closeAllModals();
    updatePrematchOverlay();
    if (overlay) overlay.hidden = false;
    if (!prematchTimer) {
      prematchTimer = setInterval(() => {
        if (prematchSecondsLeft > 0) prematchSecondsLeft -= 1;
        const formatted = formatCountdown(prematchSecondsLeft);
        const topCd = document.getElementById("pmCountdownTop");
        const botCd = document.getElementById("pmCountdownBottom");
        if (topCd) topCd.textContent = formatted;
        if (botCd) botCd.textContent = formatted;
      }, 1000);
    }
  } else {
    if (overlay) overlay.hidden = true;
    if (prematchTimer) {
      clearInterval(prematchTimer);
      prematchTimer = null;
    }
  }
}

const VENUE_PITCH_PROFILES = [
  {
    match: /HAGLEY|CHRISTCHURCH|BASIN RESERVE|WELLINGTON|EDEN PARK|AUCKLAND|HAMILTON|MOUNT MAUNGANUI/i,
    type: "SEAM & BOUNCE",
    desc: "GREEN DECK • PACE DOMINATES WITH CARRY & LATERAL MOVEMENT",
    test: { expected: "269 / 280", highest: "659 / 6", lowest: "95 ALL OUT" },
    odi: { expected: "265 - 290", highest: "341 / 7", lowest: "138 ALL OUT" },
    t20: { expected: "168 - 184", highest: "208 / 5", lowest: "102 ALL OUT" },
    pacerPct: 88,
    spinnerPct: 12,
    pacerNote: "88% WICKETS BY PACE • SEAM & BOUNCE ALL DAY",
    spinnerNote: "12% SPIN SHARE • DRIFT & BOUNCE LATER IN TEST",
    boundary: "68-76m",
    boundaryPct: 82,
  },
  {
    match: /DOHA|WEST END PARK/i,
    type: "SEAM-FRIENDLY",
    desc: "GOOD BOUNCE & CARRY \u2022 EARLY MOVEMENT FOR QUICKS",
    odi: { expected: "255 - 275", highest: "318 / 6", lowest: "142 ALL OUT" },
    t20: { expected: "164 - 178", highest: "208 / 4", lowest: "112 ALL OUT" },
    pacerPct: 54,
    spinnerPct: 46,
    pacerNote: "EARLY SEAM & EXTRA BOUNCE WITH NEW BALL",
    spinnerNote: "GRIP & TURN IN MIDDLE OVERS",
    boundary: "65-70m",
    boundaryPct: 72,
  },
  {
    match: /DUBAI|SHARJAH|ABU DHABI/i,
    type: "BALANCED / SLOW",
    desc: "EVEN PACE EARLY \u2022 GRIPS FOR SPINNERS UNDER LIGHTS",
    odi: { expected: "245 - 265", highest: "309 / 7", lowest: "128 ALL OUT" },
    t20: { expected: "158 - 172", highest: "212 / 2", lowest: "105 ALL OUT" },
    pacerPct: 47,
    spinnerPct: 53,
    pacerNote: "CUTTERS & CHANGE OF PACE EFFECTIVE",
    spinnerNote: "SLOW TURN & VARIATIONS DOMINATE MIDDLE OVERS",
    boundary: "68-74m",
    boundaryPct: 78,
  },
  {
    match: /WANKHEDE|MUMBAI|CHINNASWAMY|BENGALURU|HYDERABAD/i,
    type: "BATTING PARADISE",
    desc: "TRUE BOUNCE & FAST OUTFIELD \u2022 HIGH-SCORING DECK",
    odi: { expected: "305 - 335", highest: "438 / 4", lowest: "176 ALL OUT" },
    t20: { expected: "192 - 210", highest: "262 / 3", lowest: "129 ALL OUT" },
    pacerPct: 58,
    spinnerPct: 42,
    pacerNote: "SWING IN POWERPLAY \u2022 HARD LENGTHS AT DEATH",
    spinnerNote: "WRIST SPINNERS KEY FOR BREAKTHROUGHS",
    boundary: "62-66m",
    boundaryPct: 64,
  },
  {
    match: /CHENNAI|CHEPAUK|GALLE|PREMADASA|COLOMBO|PALLEKELE/i,
    type: "SPIN-FRIENDLY",
    desc: "DRY SURFACE \u2022 SHARP TURN & VARIABLE BOUNCE",
    odi: { expected: "230 - 255", highest: "298 / 6", lowest: "118 ALL OUT" },
    t20: { expected: "148 - 164", highest: "196 / 5", lowest: "96 ALL OUT" },
    pacerPct: 36,
    spinnerPct: 64,
    pacerNote: "OFF-CUTTERS & SLOWER BOUNCERS WORK BEST",
    spinnerNote: "HIGH TURN & DRIFT THROUGHOUT THE INNINGS",
    boundary: "66-72m",
    boundaryPct: 74,
  },
  {
    match: /MELBOURNE|MCG|SYDNEY|SCG|PERTH|ADELAIDE|BRISBANE/i,
    type: "PACE & BOUNCE",
    desc: "SPONGY TENNIS-BALL BOUNCE \u2022 CARRIES THROUGH TO KEEPER",
    odi: { expected: "275 - 295", highest: "369 / 7", lowest: "136 ALL OUT" },
    t20: { expected: "168 - 182", highest: "221 / 5", lowest: "110 ALL OUT" },
    pacerPct: 65,
    spinnerPct: 35,
    pacerNote: "STEEP BOUNCE & SEAM MOVEMENT ALL DAY",
    spinnerNote: "OVER-SPIN NEEDED ON BIG SQUARE BOUNDARIES",
    boundary: "74-82m",
    boundaryPct: 88,
  },
  {
    match: /LORD|OVAL|EDGBASTON|TRENT BRIDGE|HEADINGLEY|OLD TRAFFORD/i,
    type: "SEAM & SWING",
    desc: "OVERCAST SWING CONDITIONS \u2022 GREEN TINGE HELPS QUICKS",
    odi: { expected: "265 - 288", highest: "351 / 5", lowest: "131 ALL OUT" },
    t20: { expected: "166 - 180", highest: "218 / 6", lowest: "108 ALL OUT" },
    pacerPct: 67,
    spinnerPct: 33,
    pacerNote: "LATERAL SWING & SEAM MOVEMENT OFF THE DECK",
    spinnerNote: "CONTAINMENT ROLE UNLESS SURFACE DRIES OUT",
    boundary: "64-70m",
    boundaryPct: 70,
  },
];

function resolvePitchProfile(data) {
  const venue = String(data.venue || "HAGLEY OVAL, CHRISTCHURCH");
  const title = String(data.match_title || "2ND TEST").toUpperCase();
  const isT20 = /\bT20\b|TWENTY20|IPL|BBL|PSL|T10/i.test(title);
  const isTest = /\bTEST\b/i.test(title);

  let base = VENUE_PITCH_PROFILES.find((p) => p.match.test(venue));
  if (!base) {
    const pt = `${data.pitch_type || ""} ${data.pitch_report || ""}`.toUpperCase();
    if (/SPIN|TURN|DRY|DUST/.test(pt)) {
      base = {
        type: "SPIN-FRIENDLY",
        desc: "DRY SURFACE \u2022 ASSISTING SPINNERS THROUGH MIDDLE OVERS",
        test: { expected: "275 - 320", highest: "524 / 8", lowest: "112 ALL OUT" },
        odi: { expected: "235 - 258", highest: "302 / 6", lowest: "121 ALL OUT" },
        t20: { expected: "150 - 166", highest: "198 / 5", lowest: "99 ALL OUT" },
        pacerPct: 38,
        spinnerPct: 62,
        pacerNote: "CUTTERS & CHANGE OF PACE KEY",
        spinnerNote: "SHARP TURN & GRIP ON OFFER",
        boundary: "66-71m",
        boundaryPct: 73,
      };
    } else if (/BAT|FLAT|BELTER|HIGH/.test(pt)) {
      base = {
        type: "BATTING-FRIENDLY",
        desc: "TRUE PACE & EVEN BOUNCE \u2022 VALUE FOR SHOTS",
        test: { expected: "340 - 410", highest: "620 / 6", lowest: "158 ALL OUT" },
        odi: { expected: "295 - 325", highest: "398 / 5", lowest: "165 ALL OUT" },
        t20: { expected: "185 - 204", highest: "246 / 4", lowest: "124 ALL OUT" },
        pacerPct: 56,
        spinnerPct: 44,
        pacerNote: "HARD LENGTHS & YORKERS AT DEATH",
        spinnerNote: "VARIATION IN PACE CRUCIAL",
        boundary: "63-67m",
        boundaryPct: 66,
      };
    } else {
      base = VENUE_PITCH_PROFILES[0];
    }
  }

  const vs = data.venue_stats || {};
  const scores = isTest ? (base.test || base.odi) : (isT20 ? base.t20 : base.odi);
  const pacerPct = Number.isFinite(Number(data.pacer_pct))
    ? Number(data.pacer_pct)
    : (Number.isFinite(Number(vs.pace_pct)) ? Number(vs.pace_pct) : base.pacerPct);
  const spinnerPct = Number.isFinite(Number(data.spinner_pct))
    ? Number(data.spinner_pct)
    : (Number.isFinite(Number(vs.spin_pct)) ? Number(vs.spin_pct) : base.spinnerPct);

  const avgExpected = vs.avg_1st && vs.avg_2nd ? `${vs.avg_1st} / ${vs.avg_2nd}` : scores.expected;
  const highestVal = vs.highest_total ? String(vs.highest_total).replace("-", " / ") : scores.highest;
  const lowestVal = vs.lowest_total ? String(vs.lowest_total).replace("-", " / ") : scores.lowest;

  return {
    venue: venue.toUpperCase(),
    format: title,
    type: String(data.pitch_type || base.type).toUpperCase(),
    desc: String(data.pitch_report || base.desc).toUpperCase(),
    expected: String(data.expected_score || avgExpected).toUpperCase(),
    highest: String(data.highest_score || highestVal).toUpperCase(),
    lowest: String(data.lowest_score || lowestVal).toUpperCase(),
    pacerPct,
    spinnerPct,
    pacerNote: String(data.pacer_note || base.pacerNote).toUpperCase(),
    spinnerNote: String(data.spinner_note || base.spinnerNote).toUpperCase(),
    boundary: String(data.boundary_size || base.boundary),
    boundaryPct: Number.isFinite(Number(data.boundary_pct)) ? Number(data.boundary_pct) : base.boundaryPct,
  };
}

function openPitchModal() {
  const data = currentState || REFERENCE_PREVIEW_STATE;
  closeAllModals();
  const modal = document.getElementById("pitchModal");
  if (!modal) return;

  const p = resolvePitchProfile(data);
  document.getElementById("pitchVenuePill").textContent = `${p.venue} \u2022 ${p.format}`;
  document.getElementById("pitchTypeBadge").textContent = p.type;
  document.getElementById("pitchTypeDesc").textContent = p.desc;
  document.getElementById("pitchExpectedScore").textContent = p.expected;
  document.getElementById("pitchHighestScore").textContent = p.highest;
  document.getElementById("pitchLowestScore").textContent = p.lowest;
  document.getElementById("pitchPacerPct").textContent = `${p.pacerPct}%`;
  document.getElementById("pitchSpinnerPct").textContent = `${p.spinnerPct}%`;
  document.getElementById("pitchPacerNote").textContent = p.pacerNote;
  document.getElementById("pitchSpinnerNote").textContent = p.spinnerNote;
  document.getElementById("pitchBoundarySize").textContent = p.boundary;

  const barTargets = [`${p.pacerPct}%`, `${p.spinnerPct}%`, `${p.boundaryPct}%`];
  const bars = modal.querySelectorAll(".ps-bar span");
  bars.forEach((bar, idx) => {
    bar.setAttribute("data-target", barTargets[idx] || "0%");
    bar.style.width = "0%";
  });

  modal.hidden = false;
  void modal.offsetWidth;

  requestAnimationFrame(() => {
    bars.forEach((bar) => {
      bar.style.width = bar.getAttribute("data-target") || "0%";
    });
  });
}

document.getElementById("btnPitchReport")?.addEventListener("click", () => openPitchModal());

const VENUE_WEATHER_PROFILES = [
  { match: /HAGLEY|CHRISTCHURCH|WELLINGTON|AUCKLAND|HAMILTON|MOUNT MAUNGANUI/i, temp: 12.2, feels: 11, cond: "MOSTLY CLEAR", hum: 62, wind: 18, windDir: "NE SEA BREEZE", rain: 16, dew: "COOL CANTERBURY CONDITIONS • SEAM HELP" },
  { match: /DOHA|WEST END PARK/i, temp: 27, feels: 28, cond: "CLEAR & BREEZY", hum: 56, wind: 14, windDir: "NW BREEZE", rain: 5, dew: "LOW TO MODERATE DEW LATER" },
  { match: /DUBAI|SHARJAH|ABU DHABI/i, temp: 29, feels: 31, cond: "WARM EVENING", hum: 62, wind: 11, windDir: "W BREEZE", rain: 2, dew: "HEAVY DEW EXPECTED IN 2ND INNINGS" },
  { match: /MUMBAI|WANKHEDE|CHENNAI|COLOMBO|GALLE/i, temp: 30, feels: 34, cond: "HUMID & CLEAR", hum: 74, wind: 16, windDir: "SW SEA BREEZE", rain: 12, dew: "MODERATE TO HIGH DEW FACTOR" },
  { match: /MELBOURNE|MCG|SYDNEY|PERTH|ADELAIDE/i, temp: 21, feels: 20, cond: "PARTLY CLOUDY", hum: 48, wind: 19, windDir: "S BREEZE", rain: 10, dew: "MINIMAL DEW \u2022 CRISP AIR" },
  { match: /LORD|OVAL|EDGBASTON|MANCHESTER|LEEDS/i, temp: 18, feels: 17, cond: "COOL & OVERCAST", hum: 68, wind: 18, windDir: "SW GUSTS", rain: 20, dew: "OVERCAST \u2022 SWING CONDITIONS" },
];

function openWeatherModal() {
  const data = currentState || REFERENCE_PREVIEW_STATE;
  closeAllModals();
  const modal = document.getElementById("weatherModal");
  if (!modal) return;

  const venue = String(data.venue || "HAGLEY OVAL, CHRISTCHURCH");
  const format = String(data.match_title || "2ND TEST").toUpperCase();
  const prof = VENUE_WEATHER_PROFILES.find((w) => w.match.test(venue)) || VENUE_WEATHER_PROFILES[0];
  const wObj = data.weather && typeof data.weather === "object" ? data.weather : {};
  const parseMetric = (val, fb) => {
    const n = parseFloat(String(val ?? "").replace(/[^0-9.\-]/g, ""));
    return Number.isFinite(n) ? n : fb;
  };

  const temp = Number.isFinite(Number(data.temperature)) ? Number(data.temperature) : parseMetric(wObj.temp, prof.temp);
  const hum = Number.isFinite(Number(data.humidity)) ? Number(data.humidity) : parseMetric(wObj.humidity, prof.hum);
  const rain = Number.isFinite(Number(data.rain_chance)) ? Number(data.rain_chance) : parseMetric(wObj.rain_chance, prof.rain);
  const wind = Number.isFinite(Number(data.wind_speed)) ? Number(data.wind_speed) : prof.wind;
  const condText = wObj.condition || (typeof data.weather === "string" ? data.weather : "") || prof.cond;

  document.getElementById("weatherVenuePill").textContent = `${venue.toUpperCase()} \u2022 ${format}`;
  document.getElementById("weatherTemp").textContent = `${temp}\u00B0C`;
  document.getElementById("weatherFeels").textContent = `FEELS LIKE ${Math.round(temp - 1)}\u00B0C`;
  document.getElementById("weatherCondBadge").textContent = String(condText).toUpperCase();
  document.getElementById("weatherStatusNote").textContent =
    rain <= 20 ? "LOW RAIN THREAT \u2022 UNINTERRUPTED PLAY EXPECTED" : "PASSING CLOUDS \u2022 SLIGHT CHANCE OF BRIEF SHOWER";
  document.getElementById("weatherDewPill").textContent = `${prof.dew}`;

  document.getElementById("weatherHumidityPct").textContent = `${hum}%`;
  document.getElementById("weatherWindVal").textContent = `${wind} KM/H`;
  document.getElementById("weatherWindDir").textContent = prof.windDir;
  document.getElementById("weatherRainPct").textContent = `${rain}%`;

  const hoursGrid = document.getElementById("weatherHoursGrid");
  if (hoursGrid) {
    hoursGrid.innerHTML = `
      <div class="wh-slot"><span class="wh-time">NOW</span><span class="wh-icon">&#9728;</span><span class="wh-temp">${temp}\u00B0C</span></div>
      <div class="wh-slot"><span class="wh-time">+2 HRS</span><span class="wh-icon">&#9925;</span><span class="wh-temp">${(temp + 2).toFixed(1)}\u00B0C</span></div>
      <div class="wh-slot"><span class="wh-time">+4 HRS</span><span class="wh-icon">&#9790;</span><span class="wh-temp">${(temp + 1).toFixed(1)}\u00B0C</span></div>
    `;
  }

  const windPct = Math.min(95, Math.max(18, Math.round((wind / 35) * 100)));
  const targets = [`${hum}%`, `${windPct}%`, `${Math.max(4, rain)}%`];
  const bars = modal.querySelectorAll(".ps-bar span");
  bars.forEach((bar, idx) => {
    bar.setAttribute("data-target", targets[idx] || "0%");
    bar.style.width = "0%";
  });

  modal.hidden = false;
  void modal.offsetWidth;
  requestAnimationFrame(() => {
    bars.forEach((bar) => {
      bar.style.width = bar.getAttribute("data-target") || "0%";
    });
  });
}

document.getElementById("btnWeatherReport")?.addEventListener("click", () => openWeatherModal());

document.getElementById("btnTogglePrematch")?.addEventListener("click", () => {
  setPrematchMode(!prematchMode);
});

document.getElementById("btnPlayToss")?.addEventListener("click", () => openTossModal());
document.getElementById("centerEmblem")?.addEventListener("click", () => openTossModal());
document.getElementById("centerEmblem")?.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    openTossModal();
  }
});
document.getElementById("btnReplayToss")?.addEventListener("click", () => openTossModal());
document.getElementById("btnSwapTossWinner")?.addEventListener("click", () => {
  tossConfig.winnerSide = tossConfig.winnerSide === "left" ? "right" : "left";
  tossConfig.face = tossConfig.face === "HEADS" ? "TAILS" : "HEADS";
  openTossModal();
});
document.getElementById("btnToggleTossChoice")?.addEventListener("click", () => {
  tossConfig.choice = tossConfig.choice === "BAT" ? "BOWL" : "BAT";
  updateTossDecisionText();
});

document.querySelectorAll("[data-close]").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.getElementById(btn.getAttribute("data-close")).hidden = true;
  });
});

document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) backdrop.hidden = true;
  });
});

// Initial render: preview state if ?preview=1, else live API + WebSocket
if (previewMode) {
  applyState(REFERENCE_PREVIEW_STATE);
}

fetch("/api/player-images")
  .then((r) => (r.ok ? r.json() : null))
  .then((d) => {
    if (d && d.images) {
      playerImageDb = { ...BUILTIN_PLAYER_IMAGES, ...d.images };
      if (currentState) applyState(currentState);
    }
  })
  .catch(() => {});

fetch("/api/state")
  .then((r) => (r.ok ? r.json() : null))
  .then((d) => {
    if (d) {
      liveStateCache = d;
      if (!previewMode) applyState(d);
    }
  })
  .catch(() => {});

function triggerTossFromPayload(payload) {
  const { left, right } = getTossTeams();
  const tossText = String(payload?.toss || "").toUpperCase();
  const winnerHint = String(payload?.winner || "").toUpperCase();
  const decisionHint = String(payload?.decision || "").toUpperCase();

  const matchesTeam = (text, team) => {
    const t = String(team || "").trim().toUpperCase();
    if (!t || !text) return false;
    if (text.includes(t)) return true;
    const firstWord = t.split(/\s+/)[0];
    return firstWord.length >= 2 && text.includes(firstWord);
  };

  if (matchesTeam(winnerHint, right) || (!matchesTeam(winnerHint, left) && matchesTeam(tossText, right) && !matchesTeam(tossText, left))) {
    tossConfig.winnerSide = "right";
  } else if (matchesTeam(winnerHint, left) || matchesTeam(tossText, left)) {
    tossConfig.winnerSide = "left";
  }

  if (decisionHint === "BOWL" || decisionHint === "FIELD" || /\b(BOWL|FIELD)\b/.test(tossText)) {
    tossConfig.choice = "BOWL";
  } else if (decisionHint === "BAT" || /\bBAT\b/.test(tossText)) {
    tossConfig.choice = "BAT";
  }

  openTossModal();
}

const isTopLevelWindow = window.self === window.top;
const CROWD_BASE_VOLUME = 0.5;
const CROWD_DUCK_VOLUME = 0.3;
let crowdEnabled = true;
const commentaryAudioQueue = [];
let isPlayingCommentary = false;

const crowdBgAudio = isTopLevelWindow ? new Audio("/assets/crowd_bg.mp3") : null;
if (crowdBgAudio) {
  crowdBgAudio.loop = true;
  crowdBgAudio.volume = CROWD_BASE_VOLUME;
  crowdBgAudio.play().catch(() => {});
  const unlockAudio = () => {
    if (crowdEnabled && crowdBgAudio.paused) {
      crowdBgAudio.play().catch(() => {});
    }
    if (!isPlayingCommentary && commentaryAudioQueue.length > 0) {
      playNextCommentaryAudio();
    }
  };
  window.addEventListener("pointerdown", unlockAudio, { once: true });
  window.addEventListener("keydown", unlockAudio, { once: true });
}

function toggleCrowdAudio() {
  if (!crowdBgAudio) return;
  crowdEnabled = !crowdEnabled;
  if (crowdEnabled) {
    crowdBgAudio.volume = isPlayingCommentary ? CROWD_DUCK_VOLUME : CROWD_BASE_VOLUME;
    crowdBgAudio.play().catch(() => {});
  } else {
    crowdBgAudio.pause();
  }
}

let commentaryNextTimer = null;
let lastEnqueuedAudioUrl = "";
let lastCommentaryReceivedAt = 0;

function stopAllCommentaryAudio() {
  if (commentaryNextTimer) {
    clearTimeout(commentaryNextTimer);
    commentaryNextTimer = null;
  }
  commentaryAudioQueue.length = 0;
  const active = window._activeCommentaryAudio;
  if (active) {
    try {
      active.pause();
      active.removeAttribute("src");
      active.load();
    } catch (_) {}
    window._activeCommentaryAudio = null;
  }
  isPlayingCommentary = false;
  if (crowdBgAudio && crowdEnabled) {
    crowdBgAudio.volume = CROWD_BASE_VOLUME;
  }
}

function playNextCommentaryAudio() {
  if (!isTopLevelWindow) return;
  if (isPlayingCommentary || commentaryAudioQueue.length === 0) {
    if (crowdBgAudio && crowdEnabled && !isPlayingCommentary && commentaryAudioQueue.length === 0) {
      crowdBgAudio.volume = CROWD_BASE_VOLUME;
    }
    return;
  }
  if (window._activeCommentaryAudio) {
    try {
      window._activeCommentaryAudio.pause();
      window._activeCommentaryAudio.removeAttribute("src");
      window._activeCommentaryAudio.load();
    } catch (_) {}
    window._activeCommentaryAudio = null;
  }
  const entry = commentaryAudioQueue.shift();
  const url = typeof entry === "string" ? entry : entry?.url;
  const syncedState = typeof entry === "object" ? entry?.state : null;
  if (!url) {
    playNextCommentaryAudio();
    return;
  }
  isPlayingCommentary = true;
  if (crowdBgAudio && crowdEnabled) crowdBgAudio.volume = CROWD_DUCK_VOLUME;
  const audio = new Audio(url);
  window._activeCommentaryAudio = audio;
  let finished = false;
  let safetyTimer = null;
  const finish = () => {
    if (finished) return;
    finished = true;
    if (safetyTimer) clearTimeout(safetyTimer);
    try {
      audio.pause();
      audio.removeAttribute("src");
    } catch (_) {}
    if (window._activeCommentaryAudio === audio) window._activeCommentaryAudio = null;
    isPlayingCommentary = false;
    playNextCommentaryAudio();
  };
  safetyTimer = setTimeout(finish, 30000);
  audio.addEventListener("ended", finish);
  audio.addEventListener("error", finish);
  audio.play().then(() => {
    if (syncedState && !previewMode) {
      liveStateCache = syncedState;
      applyState(syncedState);
    }
  }).catch((err) => {
    if (err && err.name === "NotAllowedError") {
      // Re-queue once so user click unlocks playback instead of silently dropping
      commentaryAudioQueue.unshift(entry);
      finished = true;
      clearTimeout(safetyTimer);
      if (window._activeCommentaryAudio === audio) window._activeCommentaryAudio = null;
      isPlayingCommentary = false;
      if (syncedState && !previewMode) {
        liveStateCache = syncedState;
        applyState(syncedState);
      }
      return;
    }
    finish();
  });
}

function enqueueCommentaryAudio(url, syncedState = null) {
  if (!isTopLevelWindow || !url) return;
  if (url === lastEnqueuedAudioUrl) return;
  lastEnqueuedAudioUrl = url;
  lastCommentaryReceivedAt = Date.now();
  if (commentaryAudioQueue.length >= 2) commentaryAudioQueue.shift();
  commentaryAudioQueue.push({ url, state: syncedState });
  playNextCommentaryAudio();
}

function connectWebSocket() {
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${proto}//${location.host}/ws`);
  ws.addEventListener("message", (evt) => {
    try {
      const payload = JSON.parse(evt.data);
      if (!payload) return;
      if (payload.type === "commentary_interrupt") {
        lastCommentaryReceivedAt = 0;
        stopAllCommentaryAudio();
        return;
      }
      if (payload.type === "commentary") {
        if (payload.audio_url) enqueueCommentaryAudio(payload.audio_url, payload.state || null);
        return;
      }
      if (payload.type === "event_fx" || payload.type === "fx") {
        if (window.triggerEventFx && payload.event) {
          window.triggerEventFx(payload.event, payload.subtitle || payload.detail || "");
        }
        return;
      }
      if (payload.type === "milestone") {
        if (window.triggerMilestoneFx) {
          window.triggerMilestoneFx(payload);
        }
        return;
      }
      if (payload.type === "control" && payload.action === "crowd_toggle") {
        toggleCrowdAudio();
        return;
      }
      if (payload.type === "toss_trigger") {
        triggerTossFromPayload(payload);
        return;
      }
      if (payload.type === "toss_close" || payload.type === "v2_modal_close") {
        closeAllModals();
        setPrematchMode(false);
        return;
      }
      if (payload.type === "v2_prematch") {
        setPrematchMode(payload.enabled !== undefined ? Boolean(payload.enabled) : !prematchMode);
        return;
      }
      if (payload.type === "v2_pitch") {
        openPitchModal();
        return;
      }
      if (payload.type === "v2_weather") {
        openWeatherModal();
        return;
      }
      if (payload.type === "v2_scorecard") {
        openScorecardModal();
        return;
      }
      if (payload.type !== "commentary" && payload.batting_team) {
        liveStateCache = payload;
        if (!previewMode) applyState(payload);
      }
    } catch {}
  });
  ws.addEventListener("close", () => setTimeout(connectWebSocket, 3000));
  ws.addEventListener("error", () => {
    try { ws.close(); } catch {}
  });
}

function initChromaKeyBall() {
  const video = document.getElementById("ballSourceVideo");
  const canvas = document.getElementById("ballKeyedCanvas");
  if (!video || !canvas) return;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return;

  const size = canvas.width;
  const tryPlay = () => {
    video.play().catch(() => {});
  };
  video.addEventListener("canplay", tryPlay);
  tryPlay();

  function renderFrame() {
    if (video.readyState >= 2 && video.videoWidth > 0 && video.videoHeight > 0) {
      const vw = video.videoWidth;
      const vh = video.videoHeight;
      const side = Math.min(vw, vh);
      const sx = (vw - side) / 2;
      const sy = (vh - side) / 2;

      ctx.clearRect(0, 0, size, size);
      ctx.drawImage(video, sx, sy, side, side, 0, 0, size, size);

      const frame = ctx.getImageData(0, 0, size, size);
      const data = frame.data;
      for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        const maxRB = r > b ? r : b;
        const greenDiff = g - maxRB;

        if (greenDiff > 32 && g > 65) {
          data[i + 3] = 0;
        } else if (greenDiff > 10 && g > 50) {
          const alpha = 1 - (greenDiff - 10) / 22;
          data[i + 3] = Math.max(0, Math.min(255, Math.round(data[i + 3] * alpha)));
          data[i + 1] = maxRB; // suppress green spill on edges
        }
      }
      ctx.putImageData(frame, 0, 0);
    }
    requestAnimationFrame(renderFrame);
  }

  requestAnimationFrame(renderFrame);
}

let overBreakTimer1 = null;
let overBreakTimer2 = null;
let lastOverBreakShown = -1;
const OVER_SUMMARY_HOLD_MS = 3500;
const OVER_BOWLER_HOLD_MS = 3000;

function clearOverBreakTimers() {
  if (overBreakTimer1) {
    clearTimeout(overBreakTimer1);
    overBreakTimer1 = null;
  }
  if (overBreakTimer2) {
    clearTimeout(overBreakTimer2);
    overBreakTimer2 = null;
  }
}

function parseOversParts(oversStr) {
  const m = String(oversStr || "0.0").trim().match(/^(\d+)(?:\.(\d+))?$/);
  if (!m) return { completed: 0, balls: 0 };
  return { completed: parseInt(m[1], 10) || 0, balls: parseInt(m[2] || "0", 10) || 0 };
}

function maybeTriggerOverBreakShowcase(prevOversRaw, data) {
  if (prevOversRaw === null) return; // Never trigger on initial page load
  if (prematchMode || !data || data.match_status === "prematch") return;
  const qs = new URLSearchParams(location.search);
  if (qs.get("auto") === "0") return;

  const prev = parseOversParts(prevOversRaw);
  const curr = parseOversParts(data.overs);
  const completedOver =
    (curr.balls === 0 && curr.completed > 0 && (prev.completed < curr.completed || prev.balls > 0)) ||
    (curr.completed > prev.completed && prev.completed >= 0);

  if (!completedOver || curr.completed <= 0 || curr.completed === lastOverBreakShown) return;
  lastOverBreakShown = curr.completed;

  const bowlerSnap = data.bowler ? { ...data.bowler } : null;
  const bowlingTeamSnap = data.bowling_team || "";

  openScorecardModal();
  overBreakTimer1 = setTimeout(() => {
    overBreakTimer1 = null;
    if (bowlerSnap && bowlerSnap.name) {
      openPlayerCard({
        name: bowlerSnap.name,
        team: bowlingTeamSnap,
        role: "BOWLER",
        bowler: bowlerSnap,
      });
      overBreakTimer2 = setTimeout(() => {
        overBreakTimer2 = null;
        closeAllModals();
      }, OVER_BOWLER_HOLD_MS);
    } else {
      closeAllModals();
    }
  }, OVER_SUMMARY_HOLD_MS);
}

initChromaKeyBall();
if (new URLSearchParams(location.search).get("preview") === "1") {
  applyState(REFERENCE_PREVIEW_STATE);
  if (new URLSearchParams(location.search).get("wicket") === "1") {
    setTimeout(() => {
      applyState({
        ...REFERENCE_PREVIEW_STATE,
        batting_team: "IND",
        bowling_team: "NZ",
        runs: 72,
        wickets: (REFERENCE_PREVIEW_STATE.wickets || 0) + 1,
        overs: "22.4",
        striker: {
          name: "SHUBMAN GILL",
          runs: 17,
          balls: 29,
          fours: 3,
          sixes: 0,
          strike_rate: 58.62,
          on_strike: true,
          dismissal: "c Latham b Jamieson",
        },
        non_striker: {
          name: "KL RAHUL",
          runs: 25,
          balls: 80,
          fours: 3,
          sixes: 0,
          strike_rate: 31.25,
          on_strike: false,
          dismissal: "",
        },
        bowler: {
          name: "KYLE JAMIESON",
          wickets: 2,
          runs_conceded: 33,
          overs: "13.0",
          maidens: 4,
          economy: 2.54,
        },
      });
    }, 350);
  }
  window.addEventListener("message", (ev) => {
    if (ev.data?.type === "preview_state" && ev.data.state) {
      applyState(ev.data.state);
    }
  });
} else {
  connectWebSocket();
  let lastPolledStateSig = "";
  setInterval(async () => {
    if (Date.now() - lastCommentaryReceivedAt < 12000) return;
    try {
      const resp = await fetch("/api/state", { cache: "no-store" });
      if (!resp.ok) return;
      const d = await resp.json();
      if (!d || !d.batting_team) return;
      const sig = [
        d.batting_team,
        d.runs,
        d.wickets,
        d.overs,
        d.striker?.name,
        d.striker?.runs,
        d.striker?.balls,
        d.non_striker?.name,
        d.non_striker?.runs,
        d.non_striker?.balls,
        d.bowler?.name,
        d.bowler?.overs,
        d.bowler?.runs_conceded,
        d.bowler?.wickets,
        (d.curr_over?.balls || []).join(","),
        d.batters_list?.length || 0,
      ].join("|");
      if (sig !== lastPolledStateSig) {
        lastPolledStateSig = sig;
        applyState(d);
      }
    } catch (_) {}
  }, 1000);
}
if (prematchMode) {
  setPrematchMode(true);
}
if (autoPlayToss) {
  openTossModal();
}
if (autoPlayPitch) {
  openPitchModal();
}
if (autoPlayWeather) {
  openWeatherModal();
}
