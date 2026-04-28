async function api(url, method = "GET", body = null) {
  const opts = { method, headers: {} };
  if (body instanceof FormData) {
    opts.body = body;
  } else if (body) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(url, opts);
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

function renderTools(mapping) {
  const panel = document.getElementById("toolsPanel");
  panel.innerHTML = "";
  Object.keys(mapping).forEach((area) => {
    const block = document.createElement("div");
    block.className = "tool-block";
    block.innerHTML = `<h3>${area}</h3>${mapping[area]
      .map((tool) => `<span class="chip">${tool}</span>`)
      .join("")}`;
    panel.appendChild(block);
  });
}

async function loadDashboard() {
  const data = await api("/api/dashboard");
  fillRows("taskRows", data.tasks, ["id", "area", "title", "status", "created_at"]);
  fillRows("learnRows", data.learnings, ["id", "area", "topic", "created_at"]);
  fillRows("ideaRows", data.ideas, ["id", "area", "project_type", "title", "created_at"]);
  fillRows("fileRows", data.files, ["id", "area", "project_type", "project_name", "original_filename", "stored_path"]);
  fillRows("chatRows", data.chats, ["id", "role", "message", "created_at"]);
}

async function loadTools() {
  const data = await api("/api/tools");
  renderTools(data);
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

async function saveIdea() {
  const payload = {
    area: document.getElementById("ideaArea").value,
    project_type: document.getElementById("ideaType").value.trim(),
    title: document.getElementById("ideaTitle").value.trim(),
    objective: document.getElementById("ideaObjective").value.trim(),
    stack_hint: document.getElementById("ideaStack").value.trim()
  };
  if (!payload.project_type || !payload.title || !payload.objective) return;
  await api("/api/project-ideas", "POST", payload);
  document.getElementById("ideaType").value = "";
  document.getElementById("ideaTitle").value = "";
  document.getElementById("ideaObjective").value = "";
  document.getElementById("ideaStack").value = "";
  await loadDashboard();
}

async function uploadProjectFile() {
  const file = document.getElementById("projectFile").files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("area", document.getElementById("fileArea").value);
  fd.append("project_type", document.getElementById("fileType").value.trim());
  fd.append("project_name", document.getElementById("fileProjectName").value.trim());
  fd.append("idea_id", document.getElementById("fileIdeaId").value.trim());
  fd.append("file", file);
  const data = await api("/api/project-files", "POST", fd);
  document.getElementById("fileOutput").textContent = data.ok
    ? `Arquivo salvo em: ${data.stored_path}`
    : `Erro: ${data.error || "falha no upload"}`;
  if (data.ok) {
    document.getElementById("projectFile").value = "";
    await loadDashboard();
  }
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

async function sendChat() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message) return;
  const data = await api("/api/chat", "POST", { message });
  document.getElementById("chatOutput").textContent = data.ok ? data.reply : (data.error || "Erro no chat");
  input.value = "";
  await loadDashboard();
}

function handleVoiceCommand(text) {
  const cmd = text.toLowerCase();
  if (cmd.includes("salvar tarefa")) return saveTask();
  if (cmd.includes("salvar aprendizado")) return saveLearning();
  if (cmd.includes("salvar ideia")) return saveIdea();
  if (cmd.includes("executar comando")) return runCommand();
  if (cmd.includes("sincronizar github")) return syncGithub();
  const chatInput = document.getElementById("chatInput");
  chatInput.value = text;
  return sendChat();
}

let recognition = null;
let voiceOn = false;

function toggleVoice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const btn = document.getElementById("voiceBtn");
  if (!SR) {
    document.getElementById("chatOutput").textContent = "Reconhecimento de voz não suportado neste navegador.";
    return;
  }
  if (!recognition) {
    recognition = new SR();
    recognition.lang = "pt-BR";
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const text = event.results[event.results.length - 1][0].transcript.trim();
      document.getElementById("voiceText").value = text;
      handleVoiceCommand(text);
    };
    recognition.onerror = () => {
      document.getElementById("chatOutput").textContent = "Falha no reconhecimento de voz.";
    };
  }
  if (!voiceOn) {
    recognition.start();
    voiceOn = true;
    btn.textContent = "Parar reconhecimento de voz";
  } else {
    recognition.stop();
    voiceOn = false;
    btn.textContent = "Iniciar reconhecimento de voz";
  }
}

loadDashboard();
loadTools();
