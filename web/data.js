// Data layer - task shapes mirror logic/task_utils.normalize_task() in the Python repo.
// Tasks load from the Google Apps Script endpoint, then app.jsx reads window.SAMPLE_TASKS.

(function () {
  const TASKS_URL = "https://script.google.com/macros/s/AKfycbzAkoPEaYa5Ys7GTZK8v-60i1x5jgsFLnkkVqfhdl1zGYjIq4SUGTxBUuv7d0LOpb-4pg/exec?action=today";

  window.SAMPLE_TASKS = [];
  window.TASKS_LOAD_STATE = { status: "loading", error: "" };

  const taskString = (value, fallback = "") => String(value ?? fallback);
  const taskNumber = (value, fallback = 0) => {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  };
  const taskBool = (value) => value === true || value === "true" || value === 1 || value === "1";

  function normalizeWebTask(item, index) {
    const raw = item && typeof item === "object" ? item : {};
    return {
      id: taskString(raw.id || raw.taskId || raw.ID || `tmp-${index}`),
      name: taskString(raw.name || raw.task || raw.title || "Untitled Task"),
      project: taskString(raw.project || raw.category || "General"),
      priority: taskNumber(raw.priority, 5),
      nextDue: taskString(raw.nextDue || raw.dueDate || raw.date || ""),
      notes: taskString(raw.notes || raw.description || ""),
      url: taskString(raw.url || raw.link || ""),
      duration: taskNumber(raw.duration, 30) || 30,
      preferredWindow: taskString(raw.preferredWindow || "").trim(),
      recurring: taskBool(raw.recurring),
      intervalDays: taskNumber(raw.intervalDays, 0),
      done: taskBool(raw.done),
      raw,
    };
  }

  function renderLoadState(title, detail, retryable = false) {
    const root = document.getElementById("root");
    if (!root) return;

    root.innerHTML = `
      <div class="app">
        <div class="win">
          <div class="empty" style="margin:auto;max-width:360px;">
            <div class="big">${retryable ? "!" : "..."}</div>
            <div>${title}</div>
            ${detail ? `<div style="margin-top:8px;color:var(--text-4);">${detail}</div>` : ""}
            ${retryable ? `<button class="btn" id="retry-task-load" style="margin-top:14px;">Retry</button>` : ""}
          </div>
        </div>
      </div>
    `;

    if (retryable) {
      document.getElementById("retry-task-load")?.addEventListener("click", () => window.location.reload());
    }
  }

  window.TASKS_READY = fetch(TASKS_URL, { headers: { Accept: "application/json" } })
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((payload) => {
      const data = Array.isArray(payload) ? payload : payload && (payload.data || payload.tasks);
      if (!Array.isArray(data)) throw new Error("Task API response did not include a data array.");

      window.SAMPLE_TASKS = data.map(normalizeWebTask).filter((task) => task.name);
      window.TASKS_LOAD_STATE = { status: "ready", error: "" };
      return { ok: true, error: null };
    })
    .catch((error) => {
      window.SAMPLE_TASKS = [];
      window.TASKS_LOAD_STATE = { status: "error", error: error.message || String(error) };
      return { ok: false, error };
    });

  if (window.ReactDOM && window.ReactDOM.createRoot) {
    const createRoot = window.ReactDOM.createRoot.bind(window.ReactDOM);

    window.ReactDOM.createRoot = function (...args) {
      const root = createRoot(...args);
      const render = root.render.bind(root);

      root.render = function (element) {
        renderLoadState("Loading tasks from Google Sheets", "");
        window.TASKS_READY
          .then((result) => {
            if (result.ok) {
              render(element);
              return;
            }

            const error = result.error;
            renderLoadState(
              "Could not load tasks",
              error?.message || "Check the Apps Script endpoint and try again.",
              true
            );
          });
      };

      return root;
    };
  }

  // Calendar events for today's schedule (would come from iCloud CalDAV in production)
  window.SAMPLE_EVENTS = [
    { id: "e1", title: "Standup", startH: 9, startM: 0, endH: 9, endM: 30 },
    { id: "e2", title: "Coffee w/ Sam", startH: 11, startM: 0, endH: 11, endM: 30 },
    { id: "e3", title: "Lunch", startH: 12, startM: 30, endH: 13, endM: 30 },
    { id: "e4", title: "Client call — Northshore Build", startH: 15, startM: 0, endH: 16, endM: 0 },
  ];

  // Weather — 7 slots matching weather.py shape: { label, temp, rain, icon }
  window.SAMPLE_WEATHER = [
    { label: "Now",       temp: 14, rain: 10, icon: "⛅" },
    { label: "10am",      temp: 16, rain: 5,  icon: "☀" },
    { label: "11am",      temp: 18, rain: 0,  icon: "☀" },
    { label: "12pm",      temp: 19, rain: 5,  icon: "⛅" },
    { label: "1pm",       temp: 19, rain: 15, icon: "⛅" },
    { label: "2pm",       temp: 18, rain: 30, icon: "🌦" },
    { label: "Tomorrow",  temp: 17, rain: 60, icon: "🌧" },
  ];

  // Mirrors logic/task_utils.project_colors() — 10-color palette indexed by
  // sum(ord(c)) of the lowercased project name. Same hashing → same color
  // for every project across the Python widget and this UI.
  const PALETTE = [
    { accent: "#0ea5e9", soft: "#0ea5e933", ink: "#ffffff" },
    { accent: "#84cc16", soft: "#84cc1633", ink: "#1a1a1a" },
    { accent: "#f472b6", soft: "#f472b633", ink: "#3a1028" },
    { accent: "#22c55e", soft: "#22c55e33", ink: "#062b14" },
    { accent: "#a78bfa", soft: "#a78bfa33", ink: "#231942" },
    { accent: "#f59e0b", soft: "#f59e0b33", ink: "#3b2500" },
    { accent: "#14b8a6", soft: "#14b8a633", ink: "#042f2e" },
    { accent: "#ef4444", soft: "#ef444433", ink: "#3f1010" },
    { accent: "#3b82f6", soft: "#3b82f633", ink: "#0b1f3a" },
    { accent: "#f97316", soft: "#f9731633", ink: "#40210a" },
  ];

  window.projectColors = function (project) {
    const name = String(project || "General").trim().toLowerCase() || "general";
    let sum = 0;
    for (let i = 0; i < name.length; i++) sum += name.charCodeAt(i);
    return PALETTE[sum % PALETTE.length];
  };

  window.PROJECTS = ["Personal", "Tradesflow", "Work", "Home", "Errands", "Side", "Admin"];

  window.METRICS = { completedToday: 1, totalToday: 6, remainingToday: 5, percent: 17 };
})();
