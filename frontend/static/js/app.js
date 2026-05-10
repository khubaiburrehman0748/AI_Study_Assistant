

"use strict";


const API_BASE = "http://localhost:5000/api";


let allTasks        = [];
let currentFilter   = "all";
let isWaiting       = false;   


document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  loadTaskBadge();
});


async function checkHealth() {
  const dot  = document.getElementById("status-dot");
  const text = document.getElementById("status-text");
  try {
    const res = await fetch(`${API_BASE}/health`, { method: "GET" });
    if (res.ok) {
      dot.className  = "status-dot online";
      text.textContent = "Backend online";
    } else {
      throw new Error("not ok");
    }
  } catch {
    dot.className  = "status-dot offline";
    text.textContent = "Backend offline";
    showToast("⚠️ Backend not reachable. Run: python app.py", "error");
  }
}


function switchPanel(name) {
  
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));

  
  document.getElementById(`panel-${name}`).classList.add("active");
  document.querySelector(`[data-panel="${name}"]`).classList.add("active");

  
  if (name === "tasks")    loadTasks();
  if (name === "progress") loadProgress();
}


function handleKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function autoResize(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

async function sendMessage() {
  if (isWaiting) return;

  const input = document.getElementById("chat-input");
  const text  = input.value.trim();
  if (!text) return;

  
  appendMessage("user", text);
  input.value = "";
  input.style.height = "auto";

  
  const typingId = showTyping();
  isWaiting = true;
  document.getElementById("send-btn").disabled = true;

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });

    removeTyping(typingId);

    if (!response.ok) {
      const err = await response.json();
      appendMessage("bot", `❌ Error: ${err.error || "Unknown error"}`);
      return;
    }

    const data = await response.json();

    
    appendBotResponse(data);

    
    loadTaskBadge();

  } catch (err) {
    removeTyping(typingId);
    appendMessage("bot", "❌ Could not reach the backend. Is the server running?");
  } finally {
    isWaiting = false;
    document.getElementById("send-btn").disabled = false;
    document.getElementById("chat-input").focus();
  }
}

function sendQuick(text) {
  const input = document.getElementById("chat-input");
  input.value = text;
  switchPanel("chat");
  sendMessage();
}

function appendMessage(role, text) {
  const window = document.getElementById("chat-window");
  const div    = document.createElement("div");
  div.className = `message ${role}`;

  const avatar = role === "bot" ? "⬡" : "👤";
  div.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-bubble">${formatText(text)}</div>
  `;

  window.appendChild(div);
  window.scrollTop = window.scrollHeight;
}

function appendBotResponse(data) {
  const window = document.getElementById("chat-window");
  const div    = document.createElement("div");
  div.className = "message bot";

  let planHTML = "";
  if (data.intent === "planning" && data.data?.plan?.schedule) {
    planHTML = buildPlanCard(data.data.plan);
  }

  div.innerHTML = `
    <div class="msg-avatar">⬡</div>
    <div class="msg-bubble">
      ${formatText(data.reply)}
      ${planHTML}
    </div>
  `;

  window.appendChild(div);
  window.scrollTop = window.scrollHeight;
}

function buildPlanCard(plan) {
  const rows = plan.schedule.map(day => {
    const topics = day.sessions.map(s => s.topic).join(", ");
    return `
      <div class="plan-day">
        <div class="plan-day-label">${day.label}</div>
        <div class="plan-day-topics">${topics}</div>
      </div>
    `;
  }).join("");

  return `<div class="msg-plan-card">${rows}</div>`;
}

function showTyping() {
  const id     = "typing-" + Date.now();
  const window = document.getElementById("chat-window");
  const div    = document.createElement("div");
  div.className = "message bot typing-indicator";
  div.id        = id;
  div.innerHTML = `
    <div class="msg-avatar">⬡</div>
    <div class="msg-bubble">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>
  `;
  window.appendChild(div);
  window.scrollTop = window.scrollHeight;
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}


function formatText(text) {
  if (!text) return "";

  let html = text
    
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    
    .replace(/`(.+?)`/g, "<code>$1</code>")
    
    .replace(/^•\s(.+)$/gm, "<li>$1</li>")
    
    .replace(/^[-]\s(.+)$/gm, "<li>$1</li>")
    
    .replace(/^\d+\.\s(.+)$/gm, "<li>$1</li>");

  
  html = html.replace(/(<li>.*<\/li>\n?)+/gs, match => `<ul>${match}</ul>`);

  
  html = html.replace(/\n\n/g, "</p><p>");
  html = html.replace(/\n/g, "<br/>");

  return `<p>${html}</p>`;
}


async function loadTasks() {
  try {
    const res  = await fetch(`${API_BASE}/tasks`);
    const data = await res.json();
    allTasks = data.tasks || [];
    renderTasks(currentFilter);
    updateBadge(allTasks.filter(t => t.status === "pending").length);
  } catch {
    showToast("Failed to load tasks", "error");
  }
}

async function loadTaskBadge() {
  try {
    const res  = await fetch(`${API_BASE}/tasks?status=pending`);
    const data = await res.json();
    updateBadge(data.count || 0);
  } catch {  }
}

function updateBadge(count) {
  const badge = document.getElementById("pending-badge");
  badge.textContent = count;
  badge.classList.toggle("visible", count > 0);
}

function filterTasks(filter, btn) {
  currentFilter = filter;
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderTasks(filter);
}

function renderTasks(filter) {
  const list = document.getElementById("tasks-list");
  let tasks  = [...allTasks];

  if (filter === "pending") tasks = tasks.filter(t => t.status === "pending");
  if (filter === "done")    tasks = tasks.filter(t => t.status === "done");

  if (tasks.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <p class="empty-icon">📋</p>
        <p>${filter === "all" ? "No tasks yet. Create a study plan in the Chat!" : `No ${filter} tasks.`}</p>
      </div>`;
    return;
  }

  
  const groups = {};
  tasks.forEach(t => {
    const key = t.day_label || `Day ${t.day}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(t);
  });

  list.innerHTML = Object.entries(groups).map(([label, dayTasks]) => `
    <div class="day-group-header">${label}</div>
    ${dayTasks.map(task => renderTaskItem(task)).join("")}
  `).join("");
}

function renderTaskItem(task) {
  const isDone = task.status === "done";
  return `
    <div class="task-item ${isDone ? "done" : ""}" id="task-${task.id}">
      <div class="task-checkbox" onclick="toggleTask('${task.id}', '${task.status}')">
        ${isDone ? "✓" : ""}
      </div>
      <div class="task-info">
        <div class="task-topic">${task.topic}</div>
        <div class="task-meta">
          <span>${task.subject || ""}</span>
          <span>${task.duration_hours}h</span>
        </div>
      </div>
      <span class="task-type-badge ${task.type}">${task.type}</span>
    </div>`;
}

async function toggleTask(taskId, currentStatus) {
  const newStatus = currentStatus === "done" ? "pending" : "done";

  try {
    const res = await fetch(`${API_BASE}/tasks/${taskId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });

    if (!res.ok) throw new Error();

    
    const task = allTasks.find(t => t.id === taskId);
    if (task) task.status = newStatus;

    renderTasks(currentFilter);
    updateBadge(allTasks.filter(t => t.status === "pending").length);

    showToast(
      newStatus === "done" ? `✅ "${task?.topic}" marked done!` : `↩️ Task unmarked`,
      "success"
    );
  } catch {
    showToast("Failed to update task", "error");
  }
}


async function loadProgress() {
  try {
    const [statsRes, suggestRes] = await Promise.all([
      fetch(`${API_BASE}/progress`),
      fetch(`${API_BASE}/suggest`)
    ]);

    const statsData   = await statsRes.json();
    const suggestData = await suggestRes.json();

    renderStats(statsData.stats);
    renderSuggestion(suggestData.suggestion);

  } catch {
    showToast("Failed to load progress", "error");
  }
}

function renderStats(stats) {
  const grid = document.getElementById("stats-grid");
  grid.innerHTML = `
    <div class="stat-card accent">
      <div class="stat-number">${stats.percentage}%</div>
      <div class="stat-label">Completion</div>
    </div>
    <div class="stat-card green">
      <div class="stat-number">${stats.done}</div>
      <div class="stat-label">Tasks Done</div>
    </div>
    <div class="stat-card">
      <div class="stat-number">${stats.pending}</div>
      <div class="stat-label">Remaining</div>
    </div>
    <div class="stat-card amber">
      <div class="stat-number">${stats.done_hours}h</div>
      <div class="stat-label">Hours Studied</div>
    </div>
  `;

  const barSection = document.getElementById("progress-bar-section");
  barSection.innerHTML = `
    <div class="progress-track">
      <div class="progress-fill" style="width: ${stats.percentage}%"></div>
    </div>
    <div class="progress-pct-label">${stats.done} / ${stats.total} tasks completed · ${stats.remaining_hours}h remaining</div>
  `;
}

function renderSuggestion(suggestion) {
  const card = document.getElementById("suggestion-card");
  if (!suggestion?.message) return;
  card.innerHTML    = formatText(suggestion.message);
  card.classList.add("visible");
}


async function submitPlan(e) {
  e.preventDefault();

  const subject = document.getElementById("plan-subject").value.trim();
  const days    = parseInt(document.getElementById("plan-days").value);
  const hours   = parseFloat(document.getElementById("plan-hours").value);
  const goal    = document.getElementById("plan-goal").value.trim() || "Exam Preparation";
  const topicsRaw = document.getElementById("plan-topics").value.trim();
  const topics  = topicsRaw ? topicsRaw.split(",").map(t => t.trim()).filter(Boolean) : null;

  const btn = document.getElementById("plan-submit-btn");
  btn.disabled    = true;
  btn.textContent = "Generating…";

  try {
    const res = await fetch(`${API_BASE}/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject, days, hours_per_day: hours, goal, topics })
    });

    const data = await res.json();

    if (!res.ok) {
      showToast(`Error: ${data.error}`, "error");
      return;
    }

    showToast(`✅ Plan created! ${data.tasks_created} tasks saved.`, "success");
    renderPlanPreview(data.plan);
    loadTaskBadge();

  } catch {
    showToast("Failed to create plan", "error");
  } finally {
    btn.disabled    = false;
    btn.textContent = "Generate Study Plan →";
  }
}

function renderPlanPreview(plan) {
  const preview = document.getElementById("plan-preview");
  const rows    = plan.schedule.map(day => {
    const sessions = day.sessions.map(s =>
      `<div class="preview-session">• ${s.topic} (${s.duration_hours}h)</div>`
    ).join("");
    return `
      <div class="preview-day">
        <div class="preview-day-num">${day.label.split("—")[0].trim()}</div>
        <div class="preview-sessions">${sessions}</div>
        <div class="preview-hours">${day.total_hours}h total</div>
      </div>`;
  }).join("");

  preview.innerHTML = `
    <div class="plan-preview-header">
      📅 ${plan.subject} · ${plan.days} days · ${plan.total_topics} topics
    </div>
    ${rows}
  `;
  preview.classList.add("visible");
  preview.scrollIntoView({ behavior: "smooth", block: "start" });
}


function showToast(message, type = "success") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => toast.remove(), 3200);
}
