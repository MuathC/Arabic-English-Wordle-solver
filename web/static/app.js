"use strict";

const AGENTS = ["CSP", "Frequency", "Bayesian", "Entropy"];
const ROWS = 6;
const LENGTH = 5;
const KEYBOARDS = {
  en: ["qwertyuiop", "asdfghjkl", "zxcvbnm"],
  // The desktop app's rows plus ذ and إ, which the Arabic word list also uses.
  ar: ["أدجحخهعغفقثصض", "طكمنتالبيسشذ", "ظزوةىآإرؤءئ"],
};
const LETTERS = {
  en: new Set(KEYBOARDS.en.join("")),
  ar: new Set(KEYBOARDS.ar.join("")),
};

const STRINGS = {
  en: {
    page_title: "Wordle AI Solver",
    title: "WORDLE",
    agent_label: "Agent",
    mode_play: "Play vs Agent",
    mode_test: "Test Agent",
    mode_comparison: "Comparison",
    player: "Player",
    agent_CSP: "CSP",
    agent_Frequency: "Frequency",
    agent_Bayesian: "Bayesian",
    agent_Entropy: "Entropy",
    agent_title: "{agent_name} Agent",
    hint: "Hint",
    reset: "New game",
    enter: "Enter",
    delete: "Delete",
    hint_text: "{agent} suggests",
    hint_none: "{agent} has no suggestion",
    agent_waits: "Plays the same word after you finish",
    choose_secret: "Choose the secret word",
    enter_word_prompt: "5 letters",
    enter_word_btn: "Use this word",
    random_word_btn: "Random word",
    word: "Word",
    run_again: "Run again",
    new_word: "New word",
    next_guess: "Next guess",
    solve: "Solve",
    thinking: "Thinking",
    words_left: "Words left: {n}",
    correct: "Correct! {n}/6 in {s}s",
    wrong: "Wrong · {s}s",
    answer: "The word was {word}",
    win_fewer_attempts: "You won! You guessed it in fewer attempts.",
    lose_fewer_attempts: "You lost! The agent guessed it in fewer attempts.",
    draw_same_attempts: "Draw! Both players guessed it in the same number of attempts.",
    lose_only_agent_guessed: "You lost! The word was {word}.",
    win_only_player_guessed: "You won!",
    draw_neither_guessed: "Draw! None of the players guessed it. The word was {word}.",
    not_enough_letters: "Not enough letters",
    not_in_word_list: "Not in word list",
    game_over: "This game is over",
    game_not_found: "This game has expired. Start a new one.",
    network: "Can't reach the server",
    server_error: "Something went wrong. Try again.",
    fb_green: "correct",
    fb_yellow: "in the word, wrong spot",
    fb_grey: "not in the word",
  },
  ar: {
    page_title: "ووردل - حلّال الذكاء الاصطناعي",
    title: "ووردل",
    agent_label: "الوكيل",
    mode_play: "العب ضد الوكيل",
    mode_test: "اختبر الوكيل",
    mode_comparison: "مقارنة",
    player: "اللاعب",
    agent_CSP: "تحقيق القيود",
    agent_Frequency: "التكرار",
    agent_Bayesian: "البايزي",
    agent_Entropy: "الإنتروبي",
    agent_title: "وكيل {agent_name}",
    hint: "تلميح",
    reset: "لعبة جديدة",
    enter: "إدخال",
    delete: "حذف",
    hint_text: "يقترح وكيل {agent}",
    hint_none: "لا يوجد اقتراح من وكيل {agent}",
    agent_waits: "يلعب الكلمة نفسها بعد أن تنتهي",
    choose_secret: "اختر الكلمة السرية",
    enter_word_prompt: "5 حروف",
    enter_word_btn: "استخدم هذه الكلمة",
    random_word_btn: "كلمة عشوائية",
    word: "الكلمة",
    run_again: "إعادة التشغيل",
    new_word: "كلمة جديدة",
    next_guess: "التخمين التالي",
    solve: "حلّ الكلمة",
    thinking: "يفكّر",
    words_left: "الكلمات المتبقية: {n}",
    correct: "إجابة صحيحة! {n}/6 في {s} ث",
    wrong: "إجابة خاطئة · {s} ث",
    answer: "الكلمة كانت {word}",
    win_fewer_attempts: "لقد فزت! لقد خمّنت الكلمة في محاولات أقل.",
    lose_fewer_attempts: "لقد خسرت! الوكيل خمّن الكلمة في محاولات أقل.",
    draw_same_attempts: "تعادل! كلاكما خمّن الكلمة في نفس عدد المحاولات.",
    lose_only_agent_guessed: "لقد خسرت! الكلمة كانت {word}.",
    win_only_player_guessed: "لقد فزت!",
    draw_neither_guessed: "تعادل! لم يخمّن أحد الكلمة. الكلمة كانت {word}.",
    not_enough_letters: "أدخل كلمة مكونة من 5 حروف",
    not_in_word_list: "هذه الكلمة ليست موجودة في القائمة",
    game_over: "انتهت هذه اللعبة",
    game_not_found: "انتهت صلاحية هذه اللعبة. ابدأ لعبة جديدة.",
    network: "تعذّر الاتصال بالخادم",
    server_error: "حدث خطأ ما. حاول مرة أخرى.",
    fb_green: "في المكان الصحيح",
    fb_yellow: "في الكلمة بمكان آخر",
    fb_grey: "ليست في الكلمة",
  },
};

const $ = (id) => document.getElementById(id);

function load(key, fallback, allowed) {
  try {
    const value = localStorage.getItem(key);
    return allowed.includes(value) ? value : fallback;
  } catch {
    return fallback;
  }
}

function save(key, value) {
  try { localStorage.setItem(key, value); } catch { /* storage is optional */ }
}

// Each mode keeps its own state object; async work checks it is still current
// before writing, so answers for an abandoned game are dropped.
const state = {
  lang: load("lang", "en", ["en", "ar"]),
  agent: load("agent", "CSP", AGENTS),
  mode: "play",
  play: null,
  test: null,
  compare: null,
};
let nextKey = 1;
let navigation = 0; // bumped on every mode or language switch

function t(key, vars = {}) {
  const text = STRINGS[state.lang][key] ?? STRINGS.en[key] ?? key;
  return text.replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "");
}

const shown = (word) => word.toUpperCase();
const agentName = (agent) => t("agent_" + agent);
const agentTitle = (agent) => t("agent_title", { agent_name: agentName(agent) });

class ApiError extends Error {
  constructor(code) {
    super(code);
    this.code = code;
  }
}

async function api(path, body) {
  let response;
  try {
    response = await fetch(path, body === undefined ? undefined : {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError("network");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new ApiError(data.error || "server_error");
  return data;
}

function errorText(error) {
  const code = error instanceof ApiError ? error.code : "server_error";
  return STRINGS.en[code] ? t(code) : t("server_error");
}

function createGame(word) {
  const body = word ? { language: state.lang, word } : { language: state.lang };
  const ready = api("/api/games", body).then((game) => game.id);
  ready.catch(() => {}); // callers await it and report the error themselves
  return ready;
}

let toastTimer;
function toast(message) {
  const el = $("toast");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 1800);
}

function setNote(el, text, kind = "") {
  el.textContent = text;
  el.className = "note" + (kind ? " " + kind : "");
}

function runNote(el, run) {
  if (!run) return setNote(el, "");
  if (run.thinking) return setNote(el, t("thinking"), "thinking");
  if (run.error) return setNote(el, run.error, "lost");
  const seconds = run.seconds.toFixed(2);
  if (run.status === "won") return setNote(el, t("correct", { n: run.guesses.length, s: seconds }), "won");
  if (run.status === "lost") return setNote(el, t("wrong", { s: seconds }), "lost");
  setNote(el, t("words_left", { n: run.candidates_left }));
}

// ---------- boards and keyboard ----------

function renderBoard(el, rows, { typed = "", key = "" } = {}) {
  if (el.dataset.key !== String(key)) {
    el.dataset.key = key;
    el.dataset.shown = "0";
  }
  const alreadyShown = Number(el.dataset.shown);
  el.replaceChildren();
  for (let r = 0; r < ROWS; r++) {
    const row = document.createElement("div");
    row.className = "row";
    const guess = rows[r];
    const letters = guess ? [...guess.word] : r === rows.length ? [...typed] : [];
    for (let c = 0; c < LENGTH; c++) {
      const tile = document.createElement("div");
      const letter = letters[c] || "";
      tile.className = "tile";
      tile.textContent = letter;
      if (guess) {
        const color = guess.feedback[c];
        tile.classList.add(color);
        tile.setAttribute("role", "img");
        tile.setAttribute("aria-label", `${shown(letter)}, ${t("fb_" + color)}`);
        if (r < alreadyShown) tile.classList.add("still");
        else tile.style.animationDelay = `${(r - alreadyShown) * 450 + c * 90}ms`;
      } else if (letter) {
        tile.classList.add("typed");
      }
      row.append(tile);
    }
    el.append(row);
  }
  el.dataset.shown = String(rows.length);
}

function shakeRow(el, index) {
  const row = el.children[index];
  if (!row) return;
  row.classList.remove("shake");
  void row.offsetWidth; // restart the animation
  row.classList.add("shake");
}

function buildKeyboard() {
  const keyboard = $("keyboard");
  keyboard.replaceChildren();
  KEYBOARDS[state.lang].forEach((letters, index) => {
    const row = document.createElement("div");
    row.className = "key-row";
    const keys = [...letters];
    if (index === KEYBOARDS[state.lang].length - 1) {
      keys.unshift("Enter");
      keys.push("Backspace");
    }
    for (const key of keys) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "key";
      button.dataset.key = key;
      if (key === "Enter") {
        button.textContent = t("enter");
        button.classList.add("wide");
      } else if (key === "Backspace") {
        button.textContent = "⌫";
        button.setAttribute("aria-label", t("delete"));
        button.classList.add("wide");
      } else {
        button.textContent = key;
      }
      row.append(button);
    }
    keyboard.append(row);
  });
}

function colorKeyboard(rows) {
  const best = {};
  const rank = { grey: 1, yellow: 2, green: 3 };
  for (const { word, feedback } of rows) {
    [...word].forEach((letter, i) => {
      if ((rank[feedback[i]] || 0) > (rank[best[letter]] || 0)) best[letter] = feedback[i];
    });
  }
  for (const button of $("keyboard").querySelectorAll(".key")) {
    button.classList.remove("green", "yellow", "grey");
    if (best[button.dataset.key]) button.classList.add(best[button.dataset.key]);
  }
}

// ---------- play vs agent ----------

function newPlayGame() {
  state.play = {
    key: nextKey++,
    ready: createGame(),
    rows: [],
    typed: "",
    status: "playing",
    answer: null,
    busy: false,
    hint: null,
    agentRun: null,
  };
  renderPlay();
}

function onKey(key) {
  const play = state.play;
  if (!play || play.status !== "playing" || play.busy) return;
  if (key === "Enter") return submitGuess();
  if (key === "Backspace") play.typed = [...play.typed].slice(0, -1).join("");
  else if ([...play.typed].length < LENGTH) play.typed += key;
  renderPlay();
}

async function submitGuess() {
  const play = state.play;
  if ([...play.typed].length < LENGTH) {
    toast(t("not_enough_letters"));
    shakeRow($("player-board"), play.rows.length);
    return;
  }
  play.busy = true;
  let failure = null;
  try {
    const id = await play.ready;
    const result = await api(`/api/games/${id}/guess`, { word: play.typed, row: play.rows.length });
    if (state.play !== play) return;
    Object.assign(play, { rows: result.guesses, status: result.status, answer: result.answer || null, typed: "", hint: null });
    if (play.status !== "playing") playAgent(play, id);
  } catch (error) {
    failure = error;
  }
  play.busy = false;
  if (state.play !== play) return;
  renderPlay();
  if (failure) {
    toast(errorText(failure));
    shakeRow($("player-board"), play.rows.length);
  }
}

async function playAgent(play, id) {
  const agent = state.agent;
  play.agentRun = { agent, thinking: true };
  try {
    const run = await api(`/api/games/${id}/agents/${agent}/solve`, {});
    if (state.play !== play) return;
    play.agentRun = { agent, ...run };
  } catch (error) {
    if (state.play !== play) return;
    play.agentRun = { agent, error: errorText(error) };
  }
  renderPlay();
}

async function getHint() {
  const play = state.play;
  if (!play || play.status !== "playing" || play.hint?.thinking) return;
  const agent = state.agent;
  // A guess or an agent change replaces play.hint, so a late answer to this request is dropped.
  const pending = { agent, thinking: true };
  play.hint = pending;
  renderPlay();
  try {
    const id = await play.ready;
    const result = await api(`/api/games/${id}/hint`, { agent });
    if (state.play !== play || play.hint !== pending) return;
    play.hint = { agent, word: result.word };
  } catch (error) {
    if (state.play !== play || play.hint !== pending) return;
    play.hint = null;
    toast(errorText(error));
  }
  renderPlay();
}

function playResult(play) {
  const run = play.agentRun;
  const word = shown(play.answer);
  const playerWon = play.status === "won";
  const agentWon = run.status === "won";
  if (playerWon && agentWon) {
    if (play.rows.length > run.guesses.length) return t("lose_fewer_attempts");
    if (play.rows.length < run.guesses.length) return t("win_fewer_attempts");
    return t("draw_same_attempts");
  }
  if (agentWon) return t("lose_only_agent_guessed", { word });
  if (playerWon) return t("win_only_player_guessed");
  return t("draw_neither_guessed", { word });
}

function renderHint(play) {
  const line = $("hint-line");
  line.replaceChildren();
  line.className = "hint-line";
  const hint = play.hint;
  if (!hint) return;
  if (hint.thinking) {
    line.textContent = t("thinking");
    line.classList.add("thinking");
  } else if (!hint.word) {
    line.textContent = t("hint_none", { agent: agentName(hint.agent) });
  } else {
    const use = document.createElement("button");
    use.type = "button";
    use.className = "secondary";
    use.textContent = shown(hint.word);
    use.addEventListener("click", () => {
      play.typed = hint.word;
      renderPlay();
    });
    line.append(t("hint_text", { agent: agentName(hint.agent) }), use);
  }
}

function renderPlay() {
  const play = state.play;
  if (!play) return;
  const run = play.agentRun;
  renderBoard($("player-board"), play.rows, { typed: play.status === "playing" ? play.typed : "", key: play.key });
  $("play-agent-title").textContent = agentTitle(run ? run.agent : state.agent);
  renderBoard($("play-agent-board"), run?.guesses || [], { key: play.key });
  if (run) runNote($("play-agent-note"), run);
  else setNote($("play-agent-note"), t("agent_waits"));

  let status = "";
  if (play.status !== "playing") {
    status = run?.guesses ? playResult(play) : t("answer", { word: shown(play.answer) });
  }
  $("play-status").textContent = status;
  $("hint").disabled = play.status !== "playing" || Boolean(play.hint?.thinking);
  renderHint(play);
  colorKeyboard(play.rows);
}

// ---------- test agent and comparison ----------

async function startSecret(word) {
  const { mode, lang } = state;
  // Switching mode or language while this is pending makes the result stale, even after switching back.
  const started = navigation;
  const stale = () => navigation !== started;
  const form = $("secret-form");
  form.querySelectorAll("button").forEach((b) => { b.disabled = true; });
  try {
    if (!word) word = (await api(`/api/random-word?language=${lang}`)).word;
    if (stale()) return;
    const ready = createGame(word);
    await ready; // a typed word may not be in the list
    if (stale()) return;
    if (mode === "test") startTest(word, ready);
    else startCompare(word, ready);
    $("secret-input").value = "";
  } catch (error) {
    if (!stale()) toast(errorText(error));
  } finally {
    form.querySelectorAll("button").forEach((b) => { b.disabled = false; });
  }
}

function startTest(word, ready = createGame(word)) {
  state.test = { key: nextKey++, word, ready, agent: state.agent, run: null, busy: false };
  render();
}

async function stepTest(untilDone) {
  const test = state.test;
  if (!test || test.busy) return;
  test.busy = true;
  renderTest();
  try {
    const id = await test.ready;
    const run = await api(`/api/games/${id}/agents/${test.agent}/${untilDone ? "solve" : "step"}`, {});
    if (state.test !== test) return;
    test.run = run;
  } catch (error) {
    if (state.test !== test) return;
    toast(errorText(error));
  } finally {
    test.busy = false;
  }
  if (state.test === test) renderTest();
}

function startCompare(word, ready = createGame(word)) {
  const compare = { key: nextKey++, word, ready, runs: {} };
  state.compare = compare;
  for (const agent of AGENTS) {
    compare.runs[agent] = { thinking: true };
    ready
      .then((id) => api(`/api/games/${id}/agents/${agent}/solve`, {}))
      .then((run) => { compare.runs[agent] = run; }, (error) => { compare.runs[agent] = { error: errorText(error) }; })
      .then(() => { if (state.compare === compare) renderCompare(); });
  }
  render();
}

function renderSecret() {
  const current = state.mode === "test" ? state.test : state.mode === "compare" ? state.compare : null;
  $("secret-section").hidden = state.mode === "play";
  $("secret-form").hidden = Boolean(current);
  $("secret-bar").hidden = !current;
  if (current) $("secret-label").textContent = `${t("word")}: ${shown(current.word)}`;
}

function renderTest() {
  const test = state.test;
  $("test-view").hidden = state.mode !== "test" || !test;
  if (!test) return;
  const run = test.run;
  $("test-title").textContent = agentTitle(test.agent);
  renderBoard($("test-board"), run?.guesses || [], { key: test.key });
  if (test.busy) setNote($("test-note"), t("thinking"), "thinking");
  else runNote($("test-note"), run);
  const finished = run && run.status !== "playing";
  $("next-guess").disabled = test.busy || finished;
  $("solve").disabled = test.busy || finished;
}

function renderCompare() {
  const compare = state.compare;
  $("compare-view").hidden = state.mode !== "compare" || !compare;
  if (!compare) return;
  const wrap = $("compare-boards");
  if (wrap.dataset.key !== String(compare.key)) {
    wrap.dataset.key = compare.key;
    wrap.replaceChildren(...AGENTS.map((agent) => {
      const card = document.createElement("div");
      card.className = "board-card";
      card.dataset.agent = agent;
      card.innerHTML = '<h2></h2><div class="board"></div><p class="note"></p>';
      return card;
    }));
  }
  for (const card of wrap.children) {
    const agent = card.dataset.agent;
    const run = compare.runs[agent];
    card.querySelector("h2").textContent = agentTitle(agent);
    renderBoard(card.querySelector(".board"), run.guesses || [], { key: `${compare.key}-${agent}` });
    runNote(card.querySelector(".note"), run);
  }
}

// ---------- page ----------

function render() {
  for (const button of document.querySelectorAll(".tabs button")) {
    button.setAttribute("aria-pressed", String(button.dataset.mode === state.mode));
  }
  $("play-view").hidden = state.mode !== "play";
  document.querySelector(".agent-picker").hidden = state.mode === "compare";
  if (state.mode === "play" && !state.play) newPlayGame();
  renderPlay();
  renderSecret();
  renderTest();
  renderCompare();
}

function applyLanguage() {
  const lang = state.lang;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.title = t("page_title");
  for (const el of document.querySelectorAll("[data-i18n]")) el.textContent = t(el.dataset.i18n);
  for (const el of document.querySelectorAll("[data-i18n-placeholder]")) el.placeholder = t(el.dataset.i18nPlaceholder);
  const other = lang === "ar" ? "en" : "ar";
  $("language").textContent = other === "ar" ? "العربية" : "English";
  $("language").lang = other;
  $("agent").replaceChildren(...AGENTS.map((agent) => new Option(agentName(agent), agent, false, agent === state.agent)));
  buildKeyboard();
}

function setMode(mode) {
  if (mode !== state.mode) navigation++;
  state.mode = mode;
  render();
}

function setLanguage(lang) {
  navigation++;
  state.lang = lang;
  save("lang", lang);
  // Word lists differ per language, so every mode starts over.
  state.play = state.test = state.compare = null;
  applyLanguage();
  render();
}

function setAgent(agent) {
  state.agent = agent;
  save("agent", agent);
  if (state.play) state.play.hint = null;
  if (state.test) startTest(state.test.word);
  else render();
}

function readSecretInput() {
  const word = $("secret-input").value.trim().toLowerCase();
  if ([...word].length < LENGTH) return toast(t("not_enough_letters"));
  if (![...word].every((letter) => LETTERS[state.lang].has(letter))) return toast(t("not_in_word_list"));
  startSecret(word);
}

function init() {
  applyLanguage();

  $("language").addEventListener("click", () => setLanguage(state.lang === "ar" ? "en" : "ar"));
  $("agent").addEventListener("change", (e) => setAgent(e.target.value));
  for (const button of document.querySelectorAll(".tabs button")) {
    button.addEventListener("click", () => setMode(button.dataset.mode));
  }

  $("new-game").addEventListener("click", newPlayGame);
  $("hint").addEventListener("click", getHint);
  $("keyboard").addEventListener("click", (e) => {
    const key = e.target.closest(".key");
    if (key) onKey(key.dataset.key);
  });
  // A mouse click shouldn't leave focus on a button, or the next Enter would press it again.
  document.addEventListener("click", (e) => {
    if (e.detail > 0) e.target.closest("button")?.blur();
  });
  document.addEventListener("keydown", (e) => {
    if (state.mode !== "play" || e.ctrlKey || e.metaKey || e.altKey) return;
    if (e.target.closest("input, select, textarea")) return;
    if (e.key === "Enter") {
      if (e.target.closest("button")) return;
      e.preventDefault();
      onKey("Enter");
    } else if (e.key === "Backspace") {
      e.preventDefault();
      onKey("Backspace");
    } else {
      const letters = [...e.key.toLowerCase()];
      // Arabic keyboards send "لا" as one key press; names like "Shift" are longer.
      if (letters.length <= 2 && letters.every((letter) => LETTERS[state.lang].has(letter))) {
        letters.forEach(onKey);
      }
    }
  });

  $("secret-form").addEventListener("submit", (e) => {
    e.preventDefault();
    readSecretInput();
  });
  $("random-word").addEventListener("click", () => startSecret(null));
  $("change-word").addEventListener("click", () => {
    if (state.mode === "test") state.test = null;
    else state.compare = null;
    render();
    $("secret-input").focus();
  });
  $("run-again").addEventListener("click", () => {
    if (state.mode === "test") startTest(state.test.word);
    else startCompare(state.compare.word);
  });
  $("next-guess").addEventListener("click", () => stepTest(false));
  $("solve").addEventListener("click", () => stepTest(true));

  render();
}

init();
