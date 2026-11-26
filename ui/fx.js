/* Shared Polished Event Stinger (FOUR, SIX, WICKET) */
function ensureFxOverlay() {
  let el = document.getElementById("fxOverlay");
  if (!el) {
    el = document.createElement("div");
    el.id = "fxOverlay";
    el.className = "fx-overlay";
    el.innerHTML = `
      <div class="fx-backdrop"></div>
      <div class="fx-shockwave"></div>
      <div class="fx-ribbon-bar fx-ribbon-top"></div>
      <div class="fx-ribbon-bar fx-ribbon-bot"></div>
      <div class="fx-card">
        <div class="fx-kicker" id="fxKicker">BOUNDARY</div>
        <div class="fx-title" id="fxTitle">FOUR!</div>
        <div class="fx-sub" id="fxSub"></div>
      </div>
    `;
    document.body.appendChild(el);
  }
  return el;
}

window.triggerEventFx = function (eventType, subtitle = "") {
  const el = ensureFxOverlay();
  const kickerEl = document.getElementById("fxKicker");
  const titleEl = document.getElementById("fxTitle");
  const subEl = document.getElementById("fxSub");
  const norm = (eventType || "").toUpperCase();

  el.classList.remove("active", "fx-four", "fx-six", "fx-wicket");
  if (norm.includes("WICKET")) {
    el.classList.add("fx-wicket");
    kickerEl.textContent = "BREAKTHROUGH";
    titleEl.textContent = "WICKET!";
  } else if (norm.includes("SIX")) {
    el.classList.add("fx-six");
    kickerEl.textContent = "MAXIMUM";
    titleEl.textContent = "SIX!";
  } else {
    el.classList.add("fx-four");
    kickerEl.textContent = "BOUNDARY";
    titleEl.textContent = "FOUR!";
  }
  subEl.textContent = subtitle || "";

  // Re-trigger animations cleanly
  const clone = el.cloneNode(true);
  el.parentNode.replaceChild(clone, el);
  void clone.offsetWidth;
  clone.classList.add("active");
};

window.triggerMilestoneFx = function (data) {
  let el = document.getElementById("fxMilestoneWrap");
  if (!el) {
    el = document.createElement("div");
    el.id = "fxMilestoneWrap";
    el.className = "fx-milestone-wrap";
    document.body.appendChild(el);
  }
  el.innerHTML = `
    <div class="fx-ms-card">
      <div class="fx-ms-badge">${data.milestone || 50}</div>
      <div>
        <div class="fx-ms-kicker">${data.label || "HALF CENTURY!"} • ${data.team || ""}</div>
        <div class="fx-ms-name">${data.player || "BATTER"}</div>
        <div class="fx-ms-stats">
          <span>RUNS<strong>${data.runs ?? 50}</strong></span>
          <span>BALLS<strong>${data.balls ?? 0}</strong></span>
          <span>4s<strong>${data.fours ?? 0}</strong></span>
          <span>6s<strong>${data.sixes ?? 0}</strong></span>
          <span>SR<strong>${Number(data.strike_rate || 0).toFixed(2)}</strong></span>
        </div>
      </div>
    </div>
  `;
  const clone = el.cloneNode(true);
  el.parentNode.replaceChild(clone, el);
  void clone.offsetWidth;
  clone.classList.add("active");
};
