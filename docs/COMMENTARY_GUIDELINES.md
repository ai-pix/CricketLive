# Cricket Live Broadcast — Commentary Rules & Workflow Guidelines

Grounded in BBC *Test Match Special* (radio continuity & storytelling) and *Star Sports Hindi* (high-energy TV/digital rhythm, tactical graphics tie-in, and emotional connect).

---

## 1. Studio Box Roles
- **Caller / Host (`host`)**:
  - Owns live ball-by-ball urgency, scoreboard accuracy (runs, wickets, overs, CRR/RRR, target), match transitions, over recaps, news bulletins, and prompts to the viewer.
  - Voice timbre: Grounded, authoritative studio anchor.
- **Color Analyst / Expert (`expert`)**:
  - Owns *why* things happen: pitch chemistry (pace vs spin, dew), bowler plans (cutters, wrong-uns, yorker execution), batting technique/matchups, rule nuances (Powerplay, Impact Player, DLS, Free Hit), and dressing-room stories.
  - Voice timbre: Higher-energy analytical partner.

---

## 2. Conversational Structure Rules ("Anti-Ping-Pong Rule")
1. **No Rigid 1-Line Alternating**: Real broadcasters do not mechanically trade single sentences forever. Turn shapes must vary naturally across:
   - **Extended Expert Deep-Dive** (`H` sets up briefly → `E` delivers a 2–4 sentence tactical or story explanation → `H` reacts).
   - **Extended Host Live Sequence** (`H` delivers a 2–3 sentence setup + live delivery call + situation update → `E` adds a punchy reaction).
   - **Rapid Tactical Exchange** (`H` → `E` → `H` → `E`, 4–5 connected turns on one cohesive topic).
   - **Dual-Voice Story Arc** (`H` introduces context → `E` tells story part 1 → `H` asks follow-up → `E` lands insight → `H` bridges back to crease).
2. **Cohesion Within Topics**: All turns in an arc stay on one clear thread (e.g., Pace vs Spin + Dubai Dew, or Points Table NRR impact, or CREX News item + match parallel) instead of jumping randomly between topics mid-arc.

---

## 3. Cadence & "Accordion Effect"
- **Live Ball Delivery (Highest Priority — Instant)**:
  - Preempts background studio chatter immediately (`commentary_interrupt`) when runs, wickets, overs, or CREX live ball commentary change.
  - **Dot / Routine Single**: Calm, concise update (using CREX live Hindi ball text when available) — only 1–2 turns so the flow smoothly transitions into tactics/stories.
  - **Four / Six / Wicket / Milestone**: Instant vocal escalation (`H` calls the shot/dismissal dynamically → `E` dissects shot/delivery mechanics in 1–2 longer analytical sentences).
  - **No Robotic Resumes**: Never say *"please continue the story you were saying"* after an interruption. Real commentators stay with live cricket momentum and naturally open a fresh thread later.
- **Over Break (`X.0` after `Y.5`/`Y.6`)**:
  - Mandatory Over Summary (runs conceded in over, bowler figures, scoring trend, and tactical outlook for the next over).
- **Continuous Between-Ball Flow**:
  - Maintain a lookahead pre-synthesis buffer (`Turn N+1` synthesized while `Turn N` plays) so transitions have `< 0.3s` gap and **zero dead air**.

---

## 4. Phase-Aware Context Rules
Dialogue automatically adapts to live match phase:
- **`POWERPLAY` (Overs 0.0 – 5.6)**: Circle fielding restrictions, new-ball swing/seam, aggressive intent vs early wickets.
- **`MIDDLE` (Overs 6.0 – 14.6)**: Spin choke, strike rotation, partnership building, venue pace-vs-spin data, dew onset, points table & CREX news stories.
- **`DEATH` (Overs 15.0+)**: Yorker vs slower-ball variations, RRR squeeze, boundary matchups, projected score scenarios.
- **`CHASE_CRUNCH`**: When `target > 0` and balls remaining ≤ 36 or `RRR > CRR + 2.0`, prioritize chase pressure over unrelated trivia.

---

## 5. Data-Driven Personalization & Anti-Repetition
Every broadcast draws live from CREX & SQLite (`cricket_live.db`):
- Live scorecard (`striker`, `non_striker`, `bowler`, `partnership`, `batters_list`, `bowlers_list`, `fall_of_wickets`).
- CREX extended categories (`venue_stats`, `weather`, `fan_poll`, `team_form`, `recent_h2h`, `points_table`, `series_leaders`, `icc_rankings`).
- Live CREX news (`news_items`) & pre-seeded story bank (`commentary_stories`).
- **No-Repeat Deck**: Every topic, opening frame, news headline, and DB story goes into a shuffled cooldown deck persisted across runs — no item repeats until the deck cycles cleanly.
