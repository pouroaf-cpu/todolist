/* global React, ReactDOM, useTweaks, TweaksPanel, TweakSection, TweakRadio, TweakColor, TweakToggle, TweakSlider, SAMPLE_TASKS, SAMPLE_WEATHER, projectColors, PROJECTS, METRICS */

const { useState, useEffect, useRef, useMemo, useCallback, memo } = React;

const TWEAK_DEFAULTS = {
  "theme": "light",
  "accent": "#22c55e",
  "density": "compact",
  "rowstyle": "rail",
  "showWeather": true,
  "weatherExpanded": false,
  "showAnytime": true
};

// ── Time windows ───────────────────────────────────────────────────────────
const WINDOWS = [
  { id: "early",    name: "Early",     range: "06:00–09:00", startMin:  6*60, endMin:  9*60 },
  { id: "morning",  name: "Morning",   range: "09:00–12:00", startMin:  9*60, endMin: 12*60 },
  { id: "midday",   name: "Midday",    range: "12:00–14:00", startMin: 12*60, endMin: 14*60 },
  { id: "afternoon",name: "Afternoon", range: "14:00–17:00", startMin: 14*60, endMin: 17*60 },
  { id: "evening",  name: "Evening",   range: "17:00–21:00", startMin: 17*60, endMin: 21*60 },
  { id: "anytime",  name: "Anytime",   range: "no time set", startMin: null,  endMin: null },
];

const windowForMin = (m) => {
  if (m == null) return "anytime";
  for (const w of WINDOWS) {
    if (w.startMin != null && m >= w.startMin && m < w.endMin) return w.id;
  }
  if (m < 6 * 60) return "early";
  return "evening";
};

const parseTime = (s) => {
  if (!s) return null;
  const m = /^(\d{1,2}):(\d{2})$/.exec(s.trim());
  if (!m) return null;
  const h = +m[1], mm = +m[2];
  if (h < 0 || h > 23 || mm < 0 || mm > 59) return null;
  return h * 60 + mm;
};
const fmtTime = (m) => m == null ? "" : `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;

const taskEffectiveTime = (task) => {
  if (task.scheduledTime != null) return task.scheduledTime;
  if (task.preferredWindow) {
    const m = /^(\d{1,2}):(\d{2})/.exec(task.preferredWindow);
    if (m) return +m[1] * 60 + +m[2];
  }
  return null;
};
const taskIsAutoSlotted = (task) =>
  task.scheduledTime == null && !!task.preferredWindow;

// ── helpers ────────────────────────────────────────────────────────────────
const startOfDay = (d) => { const x = new Date(d); x.setHours(0,0,0,0); return x; };
const diffDays = (a, b) => Math.round((startOfDay(a) - startOfDay(b)) / 86400000);
const parseDate = (iso) => new Date(iso + "T00:00:00");

function formatDue(iso, today) {
  if (!iso) return "—";
  const d = parseDate(iso);
  const delta = diffDays(d, today);
  if (delta === 0) return "Today";
  if (delta === -1) return "Yesterday";
  if (delta === 1) return "Tomorrow";
  if (delta < 0 && delta >= -6) return `${-delta}d ago`;
  if (delta > 0 && delta <= 6) return d.toLocaleDateString(undefined, { weekday: "short" });
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

const PRIO_TIER = (p) => (p >= 8 ? "hi" : p >= 5 ? "mid" : "lo");

// ── Icons ──────────────────────────────────────────────────────────────────
const I = {
  search: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="7" cy="7" r="4.5"/><path d="m10.5 10.5 3 3" strokeLinecap="round"/></svg>,
  plus: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 3v10M3 8h10" strokeLinecap="round"/></svg>,
  chev: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="m4 6 4 4 4-4" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  check: <svg viewBox="0 0 16 16"><path d="m3.5 8.2 3.1 3.1 6-6"/></svg>,
  drag: <svg viewBox="0 0 16 16" fill="currentColor"><circle cx="6" cy="4" r="1"/><circle cx="10" cy="4" r="1"/><circle cx="6" cy="8" r="1"/><circle cx="10" cy="8" r="1"/><circle cx="6" cy="12" r="1"/><circle cx="10" cy="12" r="1"/></svg>,
  note: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M3 4h7M3 7h10M3 10h6M3 13h8" strokeLinecap="round"/></svg>,
  link: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M6.5 9.5a2.5 2.5 0 0 0 3.5 0L12 7.5a2.5 2.5 0 0 0-3.5-3.5L7 5.5M9.5 6.5a2.5 2.5 0 0 0-3.5 0L4 8.5a2.5 2.5 0 0 0 3.5 3.5L9 10.5" strokeLinecap="round"/></svg>,
  recur: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M3.5 8a4.5 4.5 0 0 1 7.4-3.4M12.5 8a4.5 4.5 0 0 1-7.4 3.4" strokeLinecap="round"/><path d="M10 2.5v3h-3M6 13.5v-3h3" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  trash: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M3.5 4.5h9M6 4.5V3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v1.5M5 4.5l.5 8a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1l.5-8" strokeLinecap="round" strokeLinejoin="round"/></svg>,
  sun: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.3 3.3l1 1M11.7 11.7l1 1M3.3 12.7l1-1M11.7 4.3l1-1" strokeLinecap="round"/></svg>,
  moon: <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"><path d="M13.5 9.5A5.5 5.5 0 1 1 6.5 2.5a4.5 4.5 0 0 0 7 7Z" strokeLinejoin="round"/></svg>,
};

// ── Clock ──────────────────────────────────────────────────────────────────
function Clock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 30000);
    return () => clearInterval(id);
  }, []);
  return (
    <span className="clock">
      {now.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}
      {" · "}
      {now.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}
    </span>
  );
}

// ── Weather strip ──────────────────────────────────────────────────────────
function WeatherStrip({ slots, expanded, onToggle }) {
  if (!slots || !slots.length) return null;
  const now = slots[0];
  return (
    <div className={"weather-strip" + (expanded ? " expanded" : "")}>
      <button className="weather-summary" onClick={onToggle} aria-expanded={expanded}>
        <span className="ic">{now.icon}</span>
        <span className="t">{now.temp}°</span>
        <span className="loc">Otorohanga</span>
        <span className="trend">
          {slots.slice(1, 7).map((s, i) => (
            <span key={i} className="trend-dot" title={`${s.label} ${s.temp}° · ${s.rain}% rain`}>
              <span className="d-ic">{s.icon}</span>
              <span className="d-t">{s.temp}°</span>
            </span>
          ))}
        </span>
        <span className={"chev" + (expanded ? " open" : "")}>{I.chev}</span>
      </button>
      {expanded && (
        <div className="weather-cards">
          {slots.map((s, i) => (
            <div key={i} className="wcard">
              <div className="wlbl">{s.label}</div>
              <div className="wic">{s.icon}</div>
              <div className="wt">{s.temp}°</div>
              <div className="wr">{s.rain}%</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Progress chip ──────────────────────────────────────────────────────────
function ProgressChip({ done, total }) {
  const pct = total ? Math.round((done / total) * 100) : 0;
  return (
    <span className="progress-chip" title={`${done}/${total} done today`}>
      <span className="ring-mini" style={{ "--pct": pct }} />
      <span><span className="pcount">{done}</span><span className="ptotal">/{total}</span></span>
    </span>
  );
}

// ── Time chip (inline editable) ────────────────────────────────────────────
function TimeChip({ task, onChange }) {
  const time = taskEffectiveTime(task);
  const isAuto = taskIsAutoSlotted(task);
  const [editing, setEditing] = useState(false);
  const [val, setVal] = useState(fmtTime(time));
  const inputRef = useRef(null);

  useEffect(() => { setVal(fmtTime(time)); }, [time]);
  useEffect(() => { if (editing) inputRef.current?.select(); }, [editing]);

  const commit = () => {
    const parsed = parseTime(val);
    if (val.trim() === "") onChange(null);
    else if (parsed != null) onChange(parsed);
    else setVal(fmtTime(time));
    setEditing(false);
  };

  if (editing) {
    return (
      <input
        ref={inputRef}
        className="time-chip"
        type="text"
        value={val}
        placeholder="HH:MM"
        onChange={(e) => setVal(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
          if (e.key === "Escape") { setVal(fmtTime(time)); setEditing(false); }
        }}
      />
    );
  }
  return (
    <button
      className={"time-chip" + (time == null ? " unset" : "") + (isAuto ? " auto" : "")}
      onClick={(e) => { e.stopPropagation(); setEditing(true); }}
      title={isAuto ? `Auto-slotted from preferred window ${task.preferredWindow}` : "Click to edit time"}
    >
      {time == null ? "—:—" : fmtTime(time)}
    </button>
  );
}

// ── Task row ───────────────────────────────────────────────────────────────
const TaskRow = memo(function TaskRow({
  task, today, expanded,
  onToggleExpand, onToggleDone, onDelete, onSetTime,
  onDragStart, onDragOver, onDrop, onDragEnd, dropHint,
}) {
  const pc = projectColors(task.project);
  const rel = formatDue(task.nextDue, today);
  const dueDelta = task.nextDue ? diffDays(parseDate(task.nextDue), today) : 0;
  const dateClass = dueDelta < 0 ? "overdue" : dueDelta === 0 ? "today" : "";

  return (
    <div className={"task-row-wrap" + (expanded ? " expanded" : "")}>
      <div
        className={
          "task" + (task.done ? " done" : "") +
          (task.pending ? " pending" : "") +
          (task.justDone ? " just-done" : "") +
          (task.isNew ? " new" : "") +
          (dropHint === "before" ? " drop-before" : dropHint === "after" ? " drop-after" : "")
        }
        style={{ "--rail": pc.accent }}
        draggable
        onDragStart={(e) => onDragStart(e, task.id)}
        onDragOver={(e) => onDragOver(e, task.id)}
        onDrop={(e) => onDrop(e, task.id)}
        onDragEnd={onDragEnd}
      >
        <span className="drag" aria-hidden>{I.drag}</span>
        <button
          className="check"
          aria-label={task.done ? "Mark not done" : "Mark done"}
          aria-checked={task.done}
          role="checkbox"
          disabled={task.pending}
          onClick={() => onToggleDone(task.id)}
        >
          {I.check}
        </button>
        <span className="dot" aria-hidden />
        <span className="body" onClick={() => onToggleExpand(task.id)}>
          <span className="title">{task.name}</span>
          <span className="project">{task.project}</span>
          {task.recurring && <span className="icon-flag" title={`Every ${task.intervalDays}d`}>{I.recur}</span>}
          {task.notes && <span className="icon-flag" title="Has notes">{I.note}</span>}
          {task.url && <span className="icon-flag" title="Has link">{I.link}</span>}
        </span>
        <span className="meta">
          <TimeChip task={task} onChange={(m) => onSetTime(task.id, m)} />
          {task.duration > 0 && <span className="dur">{task.duration}m</span>}
          <span className={`date ${dateClass}`}>{rel}</span>
          <span className="prio" data-tier={PRIO_TIER(task.priority)}>P{task.priority}</span>
        </span>
        <span className="actions">
          <button className="expand" onClick={() => onToggleExpand(task.id)} aria-label="Expand details">
            {I.chev}
          </button>
        </span>
      </div>
      <div className="task-details" aria-hidden={!expanded}>
        {task.notes && (
          <div className="row">
            <span className="k">Notes</span>
            <span className="note">{task.notes}</span>
          </div>
        )}
        {task.url && (
          <div className="row">
            <span className="k">Link</span>
            <a className="note link" href={task.url} target="_blank" rel="noopener noreferrer">{task.url}</a>
          </div>
        )}
        <div className="row">
          <span className="k">Meta</span>
          <span className="note">
            {task.duration}m
            {task.preferredWindow ? ` · prefers ${task.preferredWindow}` : ""}
            {task.recurring ? ` · every ${task.intervalDays}d` : ""}
            {` · row #${task.id.replace("t", "")}`}
          </span>
        </div>
        <div className="row">
          <span className="k">Actions</span>
          <span className="chip-row">
            <span className="chip" onClick={() => onSetTime(task.id, null)}>Clear time</span>
            <span className="chip">Snooze 1 day</span>
            <span className="chip">Edit</span>
            <span className="chip danger" onClick={() => onDelete(task.id)}>{I.trash} Delete</span>
          </span>
        </div>
      </div>
    </div>
  );
}, (a, b) =>
  a.task === b.task &&
  a.expanded === b.expanded &&
  a.dropHint === b.dropHint &&
  a.today === b.today
);

// ── App ────────────────────────────────────────────────────────────────────
function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  const [today, setToday] = useState(() => startOfDay(new Date()));
  useEffect(() => {
    const onVis = () => setToday(startOfDay(new Date()));
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, []);

  const [tasks, setTasks] = useState(() =>
    SAMPLE_TASKS.map((x) => ({ ...x, scheduledTime: null }))
  );
  const [expandedIds, setExpandedIds] = useState(() => new Set());
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("active");
  const [scopeFilter, setScopeFilter] = useState("today");
  const [hiddenProjects, setHiddenProjects] = useState(() => new Set());
  const [addOpen, setAddOpen] = useState(false);
  const [draft, setDraft] = useState({ name: "", project: "Personal", priority: 5, when: "today", duration: 30, time: "" });
  const [dragId, setDragId] = useState(null);
  const [dropHint, setDropHint] = useState({ id: null, where: null });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", t.theme === "dark" ? "dark" : "light");
  }, [t.theme]);
  useEffect(() => {
    document.documentElement.style.setProperty("--accent", t.accent);
    document.documentElement.style.setProperty("--accent-soft", `${t.accent}1f`);
  }, [t.accent]);
  useEffect(() => {
    document.documentElement.setAttribute("data-density", t.density);
    document.documentElement.setAttribute("data-rowstyle", t.rowstyle);
  }, [t.density, t.rowstyle]);

  const searchRef = useRef(null);
  const addRef = useRef(null);
  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        searchRef.current?.focus();
        searchRef.current?.select();
      } else if ((e.metaKey || e.ctrlKey) && e.key === "n") {
        e.preventDefault();
        setAddOpen(true);
        setTimeout(() => addRef.current?.focus(), 50);
      } else if (e.key === "Escape" && addOpen) setAddOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [addOpen]);

  const todayISO = today.toISOString().slice(0, 10);
  const isOverdue = (task) => task.nextDue && diffDays(parseDate(task.nextDue), today) < 0;
  const isToday   = (task) => task.nextDue === todayISO;

  const allProjects = useMemo(() => {
    const counts = {};
    for (const task of tasks) {
      counts[task.project] = (counts[task.project] || 0) + 1;
    }
    return Object.keys(counts).sort().map((name) => ({ name, count: counts[name] }));
  }, [tasks]);

  const visible = useMemo(() => {
    let v = tasks;
    if (filter === "active") v = v.filter((x) => !x.done);
    else if (filter === "done") v = v.filter((x) => x.done);
    if (hiddenProjects.size > 0) v = v.filter((x) => !hiddenProjects.has(x.project));
    if (scopeFilter === "today") v = v.filter((x) => isToday(x) || isOverdue(x));
    if (query.trim()) {
      const q = query.trim().toLowerCase();
      v = v.filter((x) =>
        x.name.toLowerCase().includes(q) ||
        (x.project || "").toLowerCase().includes(q) ||
        (x.notes || "").toLowerCase().includes(q)
      );
    }
    return v;
  }, [tasks, filter, hiddenProjects, scopeFilter, query, today]);

  const todayTotal = tasks.filter((x) => isToday(x)).length;
  const todayDone = tasks.filter((x) => x.done && isToday(x)).length;

  const counts = useMemo(() => ({
    active: tasks.filter((x) => !x.done).length,
    done: tasks.filter((x) => x.done).length,
    all: tasks.length,
  }), [tasks]);

  // ── Actions ─────────────────────────────────────────────────────────────
  const toggleExpand = useCallback((id) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }, []);

  const toggleDone = useCallback((id) => {
    setTasks((prev) =>
      prev.map((x) => {
        if (x.id !== id) return x;
        const nowDone = !x.done;
        return { ...x, done: nowDone, justDone: nowDone, pending: nowDone };
      })
    );
    setTimeout(() => {
      setTasks((prev) => prev.map((x) => (x.id === id ? { ...x, justDone: false, pending: false } : x)));
    }, 600);
  }, []);

  const setTime = useCallback((id, mins) => {
    setTasks((prev) => prev.map((x) => x.id === id ? { ...x, scheduledTime: mins } : x));
  }, []);

  const deleteTask = useCallback((id) => {
    setTasks((prev) => prev.filter((x) => x.id !== id));
  }, []);

  const toggleProject = (name) => {
    setHiddenProjects((prev) => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  };
  const showAllProjects = () => setHiddenProjects(new Set());
  const soloProject = (name) => {
    setHiddenProjects(new Set(allProjects.filter((p) => p.name !== name).map((p) => p.name)));
  };

  const addTask = useCallback(() => {
    const name = draft.name.trim();
    if (!name) return;
    const offset = draft.when === "today" ? 0 : draft.when === "tomorrow" ? 1 : 7;
    const d = new Date(today);
    d.setDate(d.getDate() + offset);
    const id = "t" + Math.random().toString(36).slice(2, 8);
    const parsedTime = parseTime(draft.time);
    const task = {
      id, name, project: draft.project, priority: draft.priority,
      nextDue: d.toISOString().slice(0, 10), notes: "", url: "",
      duration: draft.duration, preferredWindow: "", recurring: false, intervalDays: 0,
      scheduledTime: parsedTime,
      done: false, isNew: true,
    };
    setTasks((prev) => [task, ...prev]);
    setDraft({ ...draft, name: "", time: "" });
    setTimeout(() => {
      setTasks((prev) => prev.map((x) => (x.id === id ? { ...x, isNew: false } : x)));
    }, 400);
    addRef.current?.focus();
  }, [draft, today]);

  // ── Drag & drop ─────────────────────────────────────────────────────────
  const onDragStart = (e, id) => {
    setDragId(id);
    e.dataTransfer.effectAllowed = "move";
    try { e.dataTransfer.setData("text/plain", id); } catch (_) {}
  };
  const onDragOver = (e, overId) => {
    if (!dragId || dragId === overId) return;
    e.preventDefault();
    const r = e.currentTarget.getBoundingClientRect();
    const where = (e.clientY - r.top) < r.height / 2 ? "before" : "after";
    setDropHint({ id: overId, where });
  };
  const onDrop = (e, overId) => {
    e.preventDefault();
    if (!dragId || dragId === overId) {
      setDragId(null); setDropHint({ id: null, where: null });
      return;
    }
    const where = dropHint.where || "before";
    const overTask = tasks.find((x) => x.id === overId);
    setTasks((prev) => {
      const from = prev.findIndex((x) => x.id === dragId);
      if (from < 0 || !overTask) return prev;
      const next = [...prev];
      const [moved] = next.splice(from, 1);
      const to = next.findIndex((x) => x.id === overId);
      const insertAt = to + (where === "after" ? 1 : 0);
      next.splice(insertAt, 0, moved);
      return next;
    });
    setDragId(null); setDropHint({ id: null, where: null });
  };
  const onDragEnd = () => {
    setDragId(null); setDropHint({ id: null, where: null });
  };

  return (
    <div className="app">
      <div className="win">
        {/* Head — no titlebar, clock + theme toggle live here */}
        <div className="head">
          <h1>Task Focus</h1>
          <Clock />
          <span className="spacer" />
          <ProgressChip done={todayDone} total={todayTotal} />
          <button
            className="theme-toggle"
            onClick={() => setTweak("theme", t.theme === "dark" ? "light" : "dark")}
            title={t.theme === "dark" ? "Switch to light" : "Switch to dark"}
            aria-label="Toggle theme"
          >
            {t.theme === "dark" ? I.sun : I.moon}
          </button>
        </div>

        {/* Weather strip */}
        {t.showWeather && (
          <WeatherStrip
            slots={SAMPLE_WEATHER}
            expanded={t.weatherExpanded}
            onToggle={() => setTweak("weatherExpanded", !t.weatherExpanded)}
          />
        )}

        {/* Toolbar */}
        <div className="toolbar">
          <div className="search">
            {I.search}
            <input
              ref={searchRef}
              placeholder="Search…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <kbd>⌘K</kbd>
          </div>

          <div className="seg" role="tablist" aria-label="Scope">
            {[["today", "Today"], ["all", "All"]].map(([id, label]) => (
              <button key={id} role="tab" aria-pressed={scopeFilter === id} onClick={() => setScopeFilter(id)}>{label}</button>
            ))}
          </div>

          <div className="seg" role="tablist" aria-label="Status">
            {[
              ["active", "Active", counts.active],
              ["done", "Done", counts.done],
              ["all", "All", counts.all],
            ].map(([id, label, n]) => (
              <button key={id} role="tab" aria-pressed={filter === id} onClick={() => setFilter(id)}>
                {label}<span className="count">{n}</span>
              </button>
            ))}
          </div>

          <button className="btn" onClick={() => setAddOpen((v) => !v)} title="Add (⌘N)">{I.plus} New</button>
        </div>

        {/* Project chip filter */}
        <div className="projfilter">
          <span className="pflbl">Projects</span>
          {allProjects.map((p) => {
            const on = !hiddenProjects.has(p.name);
            const pc = projectColors(p.name);
            return (
              <button
                key={p.name}
                className="projchip"
                data-on={on}
                style={{ "--pcolor": pc.accent }}
                onClick={() => toggleProject(p.name)}
                onDoubleClick={() => soloProject(p.name)}
                title={on ? `Hide ${p.name} (double-click to solo)` : `Show ${p.name}`}
              >
                <span className="pcdot" />
                <span>{p.name}</span>
                <span className="pccount">{p.count}</span>
              </button>
            );
          })}
          <span className="pfsep" />
          {hiddenProjects.size > 0 && (
            <button className="pfbtn" onClick={showAllProjects}>Show all</button>
          )}
        </div>

        {/* Inline add bar */}
        <div className={"add-bar" + (addOpen ? "" : " collapsed")}>
          <span
            className="dot-input"
            style={{ background: projectColors(draft.project).accent }}
            title={draft.project}
          />
          <input
            ref={addRef}
            className="title"
            placeholder="What needs doing?"
            value={draft.name}
            onChange={(e) => setDraft({ ...draft, name: e.target.value })}
            onKeyDown={(e) => {
              if (e.key === "Enter") addTask();
              if (e.key === "Escape") setAddOpen(false);
            }}
          />
          <select className="picker" value={draft.project} onChange={(e) => setDraft({ ...draft, project: e.target.value })}>
            {PROJECTS.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select className="picker" value={draft.priority} onChange={(e) => setDraft({ ...draft, priority: Number(e.target.value) })}>
            {[1,2,3,4,5,6,7,8,9,10].map((p) => <option key={p} value={p}>P{p}</option>)}
          </select>
          <select className="picker" value={draft.duration} onChange={(e) => setDraft({ ...draft, duration: Number(e.target.value) })}>
            {[15,30,45,60,90,120].map((d) => <option key={d} value={d}>{d}m</option>)}
          </select>
          <input
            className="time"
            placeholder="HH:MM"
            value={draft.time}
            onChange={(e) => setDraft({ ...draft, time: e.target.value })}
          />
          <select className="picker" value={draft.when} onChange={(e) => setDraft({ ...draft, when: e.target.value })}>
            <option value="today">Today</option>
            <option value="tomorrow">Tomorrow</option>
            <option value="week">+7d</option>
          </select>
          <button className="plus" onClick={addTask} aria-label="Add task">{I.plus}</button>
        </div>

        {/* Flat scrollable task list */}
        <div className="task-scroll">
          {visible.length === 0 ? (
            <div className="empty">
              <div className="big">✓</div>
              <div>
                {query ? "Nothing matches your search." :
                 hiddenProjects.size > 0 ? "All visible projects are caught up." :
                 "Nothing to do."}
              </div>
            </div>
          ) : (
            <div className="tasks flat">
              {visible.map((task) => (
                <TaskRow
                  key={task.id}
                  task={task}
                  today={today}
                  expanded={expandedIds.has(task.id)}
                  onToggleExpand={toggleExpand}
                  onToggleDone={toggleDone}
                  onDelete={deleteTask}
                  onSetTime={setTime}
                  onDragStart={onDragStart}
                  onDragOver={onDragOver}
                  onDrop={onDrop}
                  onDragEnd={onDragEnd}
                  dropHint={dropHint.id === task.id ? dropHint.where : null}
                />
              ))}
            </div>
          )}

          {/* Status bar */}
          <div className="statusbar">
            <span>{visible.length} of {counts.all} tasks · {counts.done} completed today</span>
            <span className="right">
              <span>⌘K search · ⌘N new · drag to reorder</span>
              <span className="sync"><span className="pulse" /> Synced with Google Sheets</span>
            </span>
          </div>
        </div>
      </div>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Theme">
          <TweakRadio
            label="Mode"
            value={t.theme}
            options={["light", "dark"]}
            onChange={(v) => setTweak("theme", v)}
          />
          <TweakColor
            label="Accent"
            value={t.accent}
            options={["#22c55e", "#3b82f6", "#a855f7", "#f59e0b", "#ef4444"]}
            onChange={(v) => setTweak("accent", v)}
          />
        </TweakSection>
        <TweakSection label="Density">
          <TweakRadio
            label="Rows"
            value={t.density}
            options={["compact", "regular", "comfy"]}
            onChange={(v) => setTweak("density", v)}
          />
          <TweakRadio
            label="Style"
            value={t.rowstyle}
            options={["rail", "flat", "card"]}
            onChange={(v) => setTweak("rowstyle", v)}
          />
        </TweakSection>
        <TweakSection label="Chrome">
          <TweakToggle
            label="Weather strip"
            value={t.showWeather}
            onChange={(v) => setTweak("showWeather", v)}
          />
          <TweakToggle
            label="Anytime bucket"
            value={t.showAnytime}
            onChange={(v) => setTweak("showAnytime", v)}
          />
        </TweakSection>
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
