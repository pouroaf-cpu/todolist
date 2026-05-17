// Data layer — shapes mirror logic/task_utils.normalize_task() in the Python repo.
// In production these come from the Google Apps Script endpoint at BASE_URL.
// Fields: id, name, project, priority, nextDue (YYYY-MM-DD), notes, url,
//         duration (mins), preferredWindow ("HH:MM-HH:MM"), recurring, intervalDays.

(function () {
  const TODAY = new Date();
  TODAY.setHours(0, 0, 0, 0);
  const day = (offset) => {
    const d = new Date(TODAY);
    d.setDate(d.getDate() + offset);
    return d.toISOString().slice(0, 10);
  };

  window.SAMPLE_TASKS = [
    // ── Overdue ─────────────────────────────────────────────────────────────
    { id: "t1", name: "Setup pocket flow", project: "Personal", priority: 5,
      nextDue: day(-3), notes: "Outline the v1 flow; share with K for review.",
      url: "", duration: 45, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
    { id: "t2", name: "Call Rebecca — IF 0800 760 00", project: "Personal", priority: 5,
      nextDue: day(-2), notes: "Insurance renewal — needs car & contents review.",
      url: "", duration: 20, preferredWindow: "09:00-12:00", recurring: false, intervalDays: 0, done: false },

    // ── Today ───────────────────────────────────────────────────────────────
    { id: "t3", name: "Supabase — webhook to mark invoices Paid", project: "Tradesflow", priority: 8,
      nextDue: day(0), notes: "Triggered by Stripe payment_intent.succeeded. Update invoices.status='paid'.",
      url: "https://supabase.com/dashboard/project/_/functions", duration: 60, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
    { id: "t4", name: "Supabase — Ara CRM call outcomes write-back", project: "Tradesflow", priority: 8,
      nextDue: day(0), notes: "Map dispositions: connected / voicemail / no_answer. Backfill last 7d.",
      url: "", duration: 90, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
    { id: "t5", name: "Call Paper Plus — order print stock", project: "Personal", priority: 5,
      nextDue: day(0), notes: "Order print stock for next week's run.",
      url: "", duration: 10, preferredWindow: "09:00-17:00", recurring: false, intervalDays: 0, done: false },
    { id: "t6", name: "Sheet as read-only client view (Apps Script poll 5m)", project: "Tradesflow", priority: 6,
      nextDue: day(0), notes: "Sheet should reflect Supabase view via Apps Script polling every 5m.",
      url: "", duration: 45, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
    { id: "t7", name: "Standup — review last sprint", project: "Work", priority: 4,
      nextDue: day(0), notes: "", url: "", duration: 30, preferredWindow: "09:00-09:30", recurring: true, intervalDays: 7, done: false },
    { id: "t8", name: "Water the indoor plants", project: "Home", priority: 2,
      nextDue: day(0), notes: "Don't forget the monstera in the bedroom.",
      url: "", duration: 15, preferredWindow: "", recurring: true, intervalDays: 3, done: true },

    // ── Tomorrow ────────────────────────────────────────────────────────────
    { id: "t9", name: "Handle line numbers 10→12 in import script", project: "Tradesflow", priority: 10,
      nextDue: day(1), notes: "Edge case from yesterday's import. Reproduce with sample-csv-04.",
      url: "", duration: 60, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
    { id: "t10", name: "Submit timesheet", project: "Work", priority: 7,
      nextDue: day(1), notes: "", url: "", duration: 10, preferredWindow: "", recurring: true, intervalDays: 7, done: false },
    { id: "t11", name: "Pick up dry cleaning", project: "Errands", priority: 3,
      nextDue: day(1), notes: "Open till 5:30pm.", url: "", duration: 20, preferredWindow: "12:00-17:30", recurring: false, intervalDays: 0, done: false },

    // ── This week ───────────────────────────────────────────────────────────
    { id: "t12", name: "Q3 planning doc — first draft", project: "Work", priority: 6,
      nextDue: day(3), notes: "Cover three workstreams + headcount asks.",
      url: "", duration: 120, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
    { id: "t13", name: "Renew tradesflow.app domain", project: "Tradesflow", priority: 9,
      nextDue: day(4), notes: "Auto-renew failed last cycle; pay manually.",
      url: "https://dash.cloudflare.com", duration: 15, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
    { id: "t14", name: "Dentist 9:30am", project: "Personal", priority: 5,
      nextDue: day(5), notes: "", url: "", duration: 45, preferredWindow: "09:00-10:30", recurring: false, intervalDays: 0, done: false },
    { id: "t15", name: "Send invoice — Mar/Apr retainer", project: "Tradesflow", priority: 7,
      nextDue: day(6), notes: "Include the additional CRM hours.",
      url: "", duration: 20, preferredWindow: "", recurring: false, intervalDays: 0, done: false },
  ];

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
