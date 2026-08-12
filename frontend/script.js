/* script.js - TaskFlow dashboard logic
 * Talks to the real FastAPI backend at relative paths (same origin).
 * No innerHTML for user data: uses createElement/textContent throughout.
 */

const API = {
  users: "/users",
  projects: "/projects",
  tasks: "/tasks",
};

const CACHE_KEY = "taskflow:tasks:cache";

const state = {
  projects: [],
  currentProjectId: null,
  tasks: [],
};

// ------------------------------------------------------------- DOM refs --
const projectSelect = document.getElementById("project-select");
const newProjectBtn = document.getElementById("new-project-btn");
const statsContent = document.getElementById("stats-content");

const quickAddForm = document.getElementById("quickadd-form");
const quickAddInput = document.getElementById("quickadd-input");
const quickAddError = document.getElementById("quickadd-error");

const taskForm = document.getElementById("task-form");
const taskTitleInput = document.getElementById("task-title");
const taskTitleError = document.getElementById("task-title-error");
const taskPriorityInput = document.getElementById("task-priority");
const taskDueInput = document.getElementById("task-due");

const sortBtn = document.getElementById("sort-btn");
const refreshBtn = document.getElementById("refresh-btn");
const searchInput = document.getElementById("search-input");
const searchAlgo = document.getElementById("search-algo");
const searchBtn = document.getElementById("search-btn");

const taskListEl = document.getElementById("task-list");
const taskListStatus = document.getElementById("task-list-status");
const toastEl = document.getElementById("toast");

// ------------------------------------------------------------------ Util --
function showToast(message, isError = false) {
  toastEl.textContent = message;
  toastEl.classList.toggle("toast--error", isError);
  toastEl.hidden = false;
  setTimeout(() => { toastEl.hidden = true; }, 3000);
}

function setListStatus(text) {
  if (!text) {
    taskListStatus.hidden = true;
    taskListStatus.textContent = "";
  } else {
    taskListStatus.hidden = false;
    taskListStatus.textContent = text;
  }
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let body = null;
  try { body = await response.json(); } catch (_) { /* no body */ }

  if (!response.ok) {
    const detail = body && body.detail ? body.detail : `Request failed (${response.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

// -------------------------------------------------------------- Caching --
function saveTasksToCache(tasks) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(tasks));
  } catch (_) { /* storage unavailable - ignore */ }
}

function loadTasksFromCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (_) {
    return [];
  }
}

// --------------------------------------------------------------- Render --
function renderTasks(tasks) {
  taskListEl.innerHTML = ""; // clearing our own rendered markup, not user input

  if (tasks.length === 0) {
    setListStatus("No tasks yet. Add one above to get started.");
    return;
  }
  setListStatus("");

  for (const task of tasks) {
    taskListEl.appendChild(buildTaskCard(task));
  }
}

function buildTaskCard(task) {
  const li = document.createElement("li");
  li.className = "task-card";

  const main = document.createElement("div");
  main.className = "task-card__main";

  const title = document.createElement("div");
  title.className = "task-card__title";
  title.textContent = task.title;

  const meta = document.createElement("div");
  meta.className = "task-card__meta";

  const pill = document.createElement("span");
  pill.className = `priority-pill priority-pill--${task.priority}`;
  pill.textContent = task.priority;
  meta.appendChild(pill);

  if (task.due_date) {
    const due = document.createElement("span");
    due.textContent = `Due: ${task.due_date}`;
    meta.appendChild(due);
  }

  main.appendChild(title);
  main.appendChild(meta);

  const actions = document.createElement("div");
  actions.className = "task-card__actions";

  const editBtn = document.createElement("button");
  editBtn.className = "icon-btn";
  editBtn.type = "button";
  editBtn.textContent = "Edit";
  editBtn.addEventListener("click", () => editTaskPrompt(task));

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "icon-btn icon-btn--danger";
  deleteBtn.type = "button";
  deleteBtn.textContent = "Delete";
  deleteBtn.addEventListener("click", () => deleteTask(task.id));

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);

  li.appendChild(main);
  li.appendChild(actions);
  return li;
}

function renderStats(rows) {
  statsContent.innerHTML = "";

  if (!rows || rows.length === 0) {
    const p = document.createElement("p");
    p.className = "muted";
    p.textContent = "No statistics available yet.";
    statsContent.appendChild(p);
    return;
  }

  const row = rows.find((r) => r.project_id === state.currentProjectId) || rows[0];

  const cards = [
    ["Total tasks", row.task_count],
    ["High priority", row.high_count],
    ["Medium priority", row.medium_count],
    ["Low priority", row.low_count],
  ];

  for (const [label, value] of cards) {
    const card = document.createElement("div");
    card.className = "stat-card";
    const l = document.createElement("div");
    l.className = "stat-card__label";
    l.textContent = label;
    const v = document.createElement("div");
    v.className = "stat-card__value";
    v.textContent = String(value);
    card.appendChild(l);
    card.appendChild(v);
    statsContent.appendChild(card);
  }
}

function renderProjectOptions() {
  projectSelect.innerHTML = "";
  if (state.projects.length === 0) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No projects yet";
    projectSelect.appendChild(opt);
    return;
  }
  for (const project of state.projects) {
    const opt = document.createElement("option");
    opt.value = String(project.id);
    opt.textContent = project.name;
    projectSelect.appendChild(opt);
  }
}

// ---------------------------------------------------------------- Loads --
async function loadProjects() {
  state.projects = await apiRequest(API.projects);
  renderProjectOptions();
  if (state.projects.length > 0) {
    state.currentProjectId = state.projects[0].id;
    projectSelect.value = String(state.currentProjectId);
  }
}

async function loadStats() {
  try {
    const rows = await apiRequest(`${API.projects}/statistics`);
    renderStats(rows);
  } catch (err) {
    showToast(`Could not load statistics: ${err.message}`, true);
  }
}

async function loadTasks() {
  if (!state.currentProjectId) {
    renderTasks([]);
    return;
  }

  // 1. Render cached tasks immediately so the page is never blank.
  const cached = loadTasksFromCache();
  if (cached.length) renderTasks(cached);
  setListStatus("Loading tasks\u2026");

  try {
    const fresh = await apiRequest(`${API.tasks}?project_id=${state.currentProjectId}`);
    state.tasks = fresh;
    saveTasksToCache(fresh);
    renderTasks(fresh);
  } catch (err) {
    setListStatus("");
    showToast(`Could not load tasks: ${err.message}`, true);
  }
}

// -------------------------------------------------------------- Actions --
async function createTask(payload) {
  const created = await apiRequest(API.tasks, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  showToast("Task added.");
  await loadTasks();
  await loadStats();
  return created;
}

async function deleteTask(taskId) {
  try {
    await apiRequest(`${API.tasks}/${taskId}`, { method: "DELETE" });
    showToast("Task deleted.");
    await loadTasks();
    await loadStats();
  } catch (err) {
    showToast(`Delete failed: ${err.message}`, true);
  }
}

async function editTaskPrompt(task) {
  const newTitle = window.prompt("Edit task title:", task.title);
  if (newTitle === null) return;
  const trimmed = newTitle.trim();
  if (!trimmed) {
    showToast("Title cannot be empty.", true);
    return;
  }
  try {
    await apiRequest(`${API.tasks}/${task.id}`, {
      method: "PUT",
      body: JSON.stringify({ title: trimmed }),
    });
    showToast("Task updated.");
    await loadTasks();
  } catch (err) {
    showToast(`Update failed: ${err.message}`, true);
  }
}

async function createProjectPrompt() {
  const name = window.prompt("New project name:");
  if (!name || !name.trim()) return;
  if (state.projects.length === 0) {
    showToast("Create a user first via the API to own this project.", true);
    return;
  }
  const ownerId = state.projects[0].owner_id;
  try {
    await apiRequest(API.projects, {
      method: "POST",
      body: JSON.stringify({ name: name.trim(), owner_id: ownerId }),
    });
    showToast("Project created.");
    await loadProjects();
    await loadTasks();
    await loadStats();
  } catch (err) {
    showToast(`Could not create project: ${err.message}`, true);
  }
}

// --------------------------------------------------------------- Events --
projectSelect.addEventListener("change", async () => {
  state.currentProjectId = Number(projectSelect.value);
  await loadTasks();
  await loadStats();
});

newProjectBtn.addEventListener("click", createProjectPrompt);

taskTitleInput.addEventListener("input", () => {
  if (taskTitleInput.value.trim()) {
    taskTitleError.hidden = true;
  }
});

taskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = taskTitleInput.value.trim();
  if (!title) {
    taskTitleError.hidden = false;
    return;
  }
  taskTitleError.hidden = true;

  if (!state.currentProjectId) {
    showToast("Select or create a project first.", true);
    return;
  }

  try {
    await createTask({
      title,
      priority: taskPriorityInput.value,
      due_date: taskDueInput.value.trim() || null,
      project_id: state.currentProjectId,
    });
    taskForm.reset();
    taskPriorityInput.value = "medium";
  } catch (err) {
    showToast(`Could not add task: ${err.message}`, true);
  }
});

quickAddForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const description = quickAddInput.value.trim();
  if (!description) {
    quickAddError.hidden = false;
    quickAddError.textContent = "Please describe the task.";
    return;
  }
  if (!state.currentProjectId) {
    quickAddError.hidden = false;
    quickAddError.textContent = "Select or create a project first.";
    return;
  }
  quickAddError.hidden = true;

  try {
    await apiRequest(`${API.tasks}/quick-add`, {
      method: "POST",
      body: JSON.stringify({ description, project_id: state.currentProjectId }),
    });
    showToast("AI parsed and added the task.");
    quickAddInput.value = "";
    await loadTasks();
    await loadStats();
  } catch (err) {
    quickAddError.hidden = false;
    quickAddError.textContent = err.message;
  }
});

sortBtn.addEventListener("click", async () => {
  if (!state.currentProjectId) return;
  try {
    const sorted = await apiRequest(
      `${API.tasks}?project_id=${state.currentProjectId}&sort=priority`
    );
    renderTasks(sorted);
    showToast("Sorted by priority.");
  } catch (err) {
    showToast(`Sort failed: ${err.message}`, true);
  }
});

refreshBtn.addEventListener("click", async () => {
  await loadTasks();
  await loadStats();
});

searchBtn.addEventListener("click", async () => {
  const title = searchInput.value.trim();
  if (!title) {
    showToast("Enter an exact title to search for.", true);
    return;
  }
  try {
    const result = await apiRequest(
      `${API.tasks}/search?title=${encodeURIComponent(title)}&algo=${searchAlgo.value}`
    );
    renderTasks([result]);
    showToast("Task found.");
  } catch (err) {
    showToast(`Not found: ${err.message}`, true);
  }
});

// ----------------------------------------------------------------- Init --
async function init() {
  // Show cached tasks immediately, before any network call resolves.
  const cached = loadTasksFromCache();
  if (cached.length) renderTasks(cached);

  try {
    await loadProjects();
    await loadTasks();
    await loadStats();
  } catch (err) {
    showToast(`Startup error: ${err.message}`, true);
  }
}

init();
