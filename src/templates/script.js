"use strict";

const API_URL = "http://127.0.0.1:8000/predict";
const RING_LENGTH = 2 * Math.PI * 52; // matches r="52" in index.html

const $ = (id) => document.getElementById(id);
const form = $("predict-form");
const submitBtn = $("submit-btn");
const states = ["idle", "loading", "result", "error"].reduce((acc, name) => {
  acc[name] = $(`state-${name}`);
  return acc;
}, {});

const CATEGORICAL = {
  gender: ["female", "male"],
  race_ethnicity: ["group A", "group B", "group C", "group D", "group E"],
  parental_level_of_education: ["bachelor's degree", "some college", "master's degree", "associate's degree", "high school", "some high school"],
  lunch: ["standard", "free/reduced"],
  test_preparation_course: ["none", "completed"],
};
const SCORES = ["reading_score", "writing_score"];
const LABELS = {
  gender: "gender",
  race_ethnicity: "a race/ethnicity group",
  parental_level_of_education: "parental level of education",
  lunch: "a lunch type",
  test_preparation_course: "test preparation status",
  reading_score: "Reading score",
  writing_score: "Writing score",
};

/* ---------- UI helpers ---------- */

function showState(name) {
  Object.entries(states).forEach(([key, el]) => { el.hidden = key !== name; });
}

function setFieldError(name, message) {
  const input = $(name);
  const msg = document.querySelector(`.msg[data-for="${name}"]`);
  input.classList.toggle("invalid", Boolean(message));
  input.setAttribute("aria-invalid", message ? "true" : "false");
  if (message) input.setAttribute("aria-describedby", `err-${name}`);
  else input.removeAttribute("aria-describedby");
  msg.id = `err-${name}`;
  msg.textContent = message || "";
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.querySelector(".btn-label").textContent = isLoading ? "Predicting…" : "Predict math score";
}

function showError(title, text) {
  $("error-title").textContent = title;
  $("error-text").textContent = text;
  showState("error");
}

/* ---------- Slider <-> number sync ---------- */

function updateSliderFill(slider) {
  slider.style.setProperty("--fill", `${slider.value}%`);
}

document.querySelectorAll("input[type='range'][data-sync]").forEach((slider) => {
  const number = $(slider.dataset.sync);
  updateSliderFill(slider);

  slider.addEventListener("input", () => {
    number.value = slider.value;
    updateSliderFill(slider);
    setFieldError(number.id, "");
  });

  number.addEventListener("input", () => {
    const value = Number(number.value);
    if (number.value !== "" && Number.isFinite(value)) {
      slider.value = Math.min(100, Math.max(0, value));
      updateSliderFill(slider);
    }
    setFieldError(number.id, "");
  });
});

Object.keys(CATEGORICAL).forEach((name) => {
  $(name).addEventListener("change", () => setFieldError(name, ""));
});

/* ---------- Validation ---------- */

function validate() {
  const payload = {};
  let firstInvalid = null;

  const fail = (name, message) => {
    setFieldError(name, message);
    if (!firstInvalid) firstInvalid = $(name);
  };

  for (const [name, allowed] of Object.entries(CATEGORICAL)) {
    const value = $(name).value;
    if (!allowed.includes(value)) fail(name, `Select ${LABELS[name]}.`);
    else { setFieldError(name, ""); payload[name] = value; }
  }

  for (const name of SCORES) {
    const raw = $(name).value.trim();
    const value = Number(raw);
    if (raw === "") fail(name, `${LABELS[name]} is required.`);
    else if (!Number.isInteger(value)) fail(name, `${LABELS[name]} must be a whole number.`);
    else if (value < 0 || value > 100) fail(name, `${LABELS[name]} must be between 0 and 100.`);
    else { setFieldError(name, ""); payload[name] = value; }
  }

  if (firstInvalid) { firstInvalid.focus(); return null; }
  return payload;
}

/* ---------- API ---------- */

function describeHttpError(status, body) {
  // FastAPI validation errors (422) return { detail: [{ loc, msg }, ...] }
  if (body && Array.isArray(body.detail)) {
    const items = body.detail.map((d) => `${(d.loc || []).slice(1).join(".") || "input"}: ${d.msg}`);
    return `The server rejected the input (HTTP ${status}). ${items.join("; ")}`;
  }
  if (body && typeof body.detail === "string") return `${body.detail} (HTTP ${status})`;
  return `The server returned an error (HTTP ${status}).`;
}

async function requestPrediction(payload) {
  let response;
  try {
    response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    const error = new Error("Could not reach the prediction server. Check that FastAPI is running at http://127.0.0.1:8000 and try again.");
    error.title = "Server unavailable";
    throw error;
  }

  let body = null;
  try { body = await response.json(); } catch (_) { /* body stays null */ }

  if (!response.ok) {
    const error = new Error(describeHttpError(response.status, body));
    error.title = "Prediction failed";
    throw error;
  }

  const score = body && body.math_score;
  if (typeof score !== "number" || !Number.isFinite(score)) {
    const error = new Error("The server replied, but the response did not include a valid math_score number.");
    error.title = "Unexpected response";
    throw error;
  }
  return score;
}

/* ---------- Result display ---------- */

function scoreNote(score) {
  if (score >= 80) return "Strong predicted performance.";
  if (score >= 60) return "Solid predicted performance.";
  if (score >= 40) return "Moderate predicted performance.";
  return "Lower predicted performance.";
}

function showResult(score) {
  const shown = Math.round(score * 10) / 10;
  const pct = Math.min(100, Math.max(0, score));
  const bar = $("ring-bar");
  const valueEl = $("score-value");

  bar.style.strokeDashoffset = RING_LENGTH;
  $("progress-fill").style.width = "0%";
  valueEl.textContent = "0";
  $("score-note").textContent = scoreNote(score);
  showState("result");

  requestAnimationFrame(() => requestAnimationFrame(() => {
    bar.style.strokeDashoffset = RING_LENGTH * (1 - pct / 100);
    $("progress-fill").style.width = `${pct}%`;
  }));

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) { valueEl.textContent = shown; return; }

  const start = performance.now();
  const duration = 1200;
  const tick = (now) => {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    valueEl.textContent = (shown * eased).toFixed(1).replace(/\.0$/, "");
    if (t < 1) requestAnimationFrame(tick);
    else valueEl.textContent = shown;
  };
  requestAnimationFrame(tick);
}

/* ---------- Events ---------- */

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = validate();
  if (!payload) return;

  setLoading(true);
  showState("loading");
  try {
    const score = await requestPrediction(payload);
    showResult(score);
  } catch (err) {
    showError(err.title || "Something went wrong", err.message);
  } finally {
    setLoading(false);
  }
});

function resetForm() {
  form.reset();
  document.querySelectorAll("input[type='range']").forEach((s) => { s.value = 50; updateSliderFill(s); });
  [...Object.keys(CATEGORICAL), ...SCORES].forEach((name) => setFieldError(name, ""));
  showState("idle");
}

$("reset-btn").addEventListener("click", resetForm);
$("again-btn").addEventListener("click", () => { resetForm(); $("gender").focus(); });
$("retry-btn").addEventListener("click", () => { showState("idle"); submitBtn.focus(); });
