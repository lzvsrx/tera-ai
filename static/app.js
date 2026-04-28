async function api(url, method = "GET", body = null) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : null
  });
  return res.json();
}

function fillRows(id, rows, fields) {
  const t = document.getElementById(id);
  t.innerHTML = "";
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = fields.map((f) => `<td>${row[f] ?? ""}</td>`).join("");
    t.appendChild(tr);
  });
}

async function loadDashboard() {
  const data = await api("/api/dashboard");
  fillRows("taskRows", data.tasks, ["id", "area", "title", "status", "created_at"]);
  fillRows("learnRows", data.learnings, ["id", "area", "topic", "created_at"]);
}

async function saveTask() {
  const payload = {
    area: document.getElementById("taskArea").value,
    title: document.getElementById("taskTitle").value.trim(),
    description: document.getElementById("taskDesc").value.trim(),
    status: document.getElementById("taskStatus").value
  };
  if (!payload.title) return;
  await api("/api/tasks", "POST", payload);
  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDesc").value = "";
  await loadDashboard();
}

async function saveLearning() {
  const payload = {
    area: document.getElementById("learnArea").value,
    topic: document.getElementById("learnTopic").value.trim(),
    note: document.getElementById("learnNote").value.trim()
  };
  if (!payload.topic || !payload.note) return;
  await api("/api/learnings", "POST", payload);
  document.getElementById("learnTopic").value = "";
  document.getElementById("learnNote").value = "";
  await loadDashboard();
}

async function runCommand() {
  const command = document.getElementById("cmdInput").value.trim();
  if (!command) return;
  const data = await api("/api/commands", "POST", { command });
  document.getElementById("cmdOutput").textContent = data.output || "";
}

async function syncGithub() {
  const data = await api("/api/sync-github", "POST", {});
  const out = [];
  out.push(`ok: ${data.ok}`);
  if (data.stdout) out.push(data.stdout);
  if (data.stderr) out.push(data.stderr);
  document.getElementById("gitOutput").textContent = out.join("\n");
}

loadDashboard();
