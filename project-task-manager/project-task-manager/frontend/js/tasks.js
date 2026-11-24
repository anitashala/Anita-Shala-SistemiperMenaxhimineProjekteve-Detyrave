// tasks.js – faqja e një projekti: anëtarët, detyrat dhe komentet

requireLogin();
document.getElementById("logout-btn").addEventListener("click", logout);

const projectId = new URLSearchParams(window.location.search).get("project");
if (!projectId) {
  window.location.href = "projects.html";
}

const projectTitle = document.getElementById("project-title");
const projectDescription = document.getElementById("project-description");
const membersState = document.getElementById("members-state");
const membersList = document.getElementById("members-list");
const memberForm = document.getElementById("member-form");
const memberMessage = document.getElementById("member-message");
const taskForm = document.getElementById("task-form");
const taskMessage = document.getElementById("task-message");
const assigneeSelect = document.getElementById("task-assignee");
const tasksState = document.getElementById("tasks-state");
const tasksList = document.getElementById("tasks-list");

let myRole = null;

// ---------- Projekti ----------
async function loadProject() {
  const projects = (await apiRequest("/projects")) || [];
  const project = projects.find((p) => String(p.id) === projectId);
  if (!project) {
    setState(tasksState, "error", "Projekti nuk u gjet ose nuk keni qasje në të.");
    projectTitle.textContent = "Projekti nuk u gjet";
    return false;
  }
  myRole = project.my_role;
  projectTitle.textContent = project.name;
  projectDescription.textContent = project.description || "";
  memberForm.hidden = myRole !== "OWNER";
  return true;
}

// ---------- Anëtarët ----------
async function loadMembers() {
  setState(membersState, "loading", "Duke ngarkuar anëtarët…");
  membersList.textContent = "";

  try {
    const members = (await apiRequest(`/projects/${projectId}/members`)) || [];
    setState(membersState, "none");

    assigneeSelect.textContent = "";
    const none = el("option", null, "Pa caktuar");
    none.value = "";
    assigneeSelect.appendChild(none);

    members.forEach((member) => {
      const item = el("li");
      const info = el("span");
      info.appendChild(el("strong", null, member.full_name));
      info.appendChild(el("span", "muted", "  " + member.email + "  "));
      info.appendChild(el("span", "badge badge-" + member.member_role, member.member_role === "OWNER" ? "Pronar" : "Anëtar"));
      item.appendChild(info);

      if (myRole === "OWNER" && member.member_role !== "OWNER") {
        const remove = el("button", "btn btn-danger btn-small", "Hiq");
        remove.type = "button";
        remove.addEventListener("click", () => removeMember(member));
        item.appendChild(remove);
      }
      membersList.appendChild(item);

      const option = el("option", null, member.full_name);
      option.value = member.user_id;
      assigneeSelect.appendChild(option);
    });
  } catch (error) {
    setState(membersState, "error", error.message, loadMembers);
  }
}

async function removeMember(member) {
  if (!confirm(`Të hiqet ${member.full_name} nga projekti?`)) return;
  try {
    await apiRequest(`/projects/${projectId}/members/${member.user_id}`, { method: "DELETE" });
    showMessage(memberMessage, "Anëtari u hoq.", "success");
    await loadMembers();
    await loadTasks();
  } catch (error) {
    showMessage(memberMessage, error.message, "error");
  }
}

memberForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage(memberMessage, "");
  const email = document.getElementById("member-email").value.trim();

  if (!email.includes("@")) {
    showMessage(memberMessage, "Shkruaj një email të vlefshëm.", "error");
    return;
  }

  try {
    await apiRequest(`/projects/${projectId}/members`, {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    memberForm.reset();
    showMessage(memberMessage, "Anëtari u shtua.", "success");
    loadMembers();
  } catch (error) {
    showMessage(memberMessage, error.message, "error");
  }
});

// ---------- Detyrat ----------
async function loadTasks() {
  setState(tasksState, "loading", "Duke ngarkuar detyrat…");
  tasksList.textContent = "";

  try {
    const tasks = (await apiRequest(`/projects/${projectId}/tasks`)) || [];
    if (tasks.length === 0) {
      setState(tasksState, "empty", "Ky projekt nuk ka ende detyra. Krijo të parën më sipër.");
      return;
    }
    setState(tasksState, "none");
    tasks.forEach((task) => tasksList.appendChild(renderTask(task)));
  } catch (error) {
    setState(tasksState, "error", error.message, loadTasks);
  }
}

function renderTask(task) {
  const card = el("article", "task");
  card.dataset.status = task.status;

  const head = el("div", "task-head");
  head.appendChild(el("h3", null, task.title));
  head.appendChild(el("span", "badge badge-" + task.priority, "Prioriteti: " + PRIORITY_LABELS[task.priority]));
  card.appendChild(head);

  const meta = [task.assigned_to_name ? "Përgjegjës: " + task.assigned_to_name : "Pa caktuar"];
  if (task.deadline) meta.push("Afati: " + formatDate(task.deadline));
  card.appendChild(el("p", "task-meta", meta.join(" – ")));
  if (task.description) card.appendChild(el("p", null, task.description));

  const controls = el("div", "task-controls");

  if (task.can_edit) {
    const select = el("select");
    select.setAttribute("aria-label", "Statusi i detyrës");
    Object.keys(STATUS_LABELS).forEach((status) => {
      const option = el("option", null, STATUS_LABELS[status]);
      option.value = status;
      option.selected = status === task.status;
      select.appendChild(option);
    });
    select.addEventListener("change", () => changeStatus(task, select.value));
    controls.appendChild(select);

    const remove = el("button", "btn btn-danger btn-small", "Fshij");
    remove.type = "button";
    remove.addEventListener("click", () => deleteTask(task));
    controls.appendChild(remove);
  } else {
    controls.appendChild(el("span", "status-text", STATUS_LABELS[task.status]));
  }

  const commentsPanel = el("div", "comments");
  commentsPanel.hidden = true;
  const toggle = el("button", "btn btn-light btn-small", "Komente");
  toggle.type = "button";
  toggle.addEventListener("click", () => {
    commentsPanel.hidden = !commentsPanel.hidden;
    if (!commentsPanel.hidden && commentsPanel.childElementCount === 0) {
      buildCommentsPanel(task.id, commentsPanel);
    }
  });
  controls.appendChild(toggle);

  card.appendChild(controls);
  card.appendChild(commentsPanel);
  return card;
}

async function changeStatus(task, status) {
  try {
    await apiRequest("/tasks/" + task.id, { method: "PATCH", body: JSON.stringify({ status }) });
    showMessage(taskMessage, "Statusi u ndryshua.", "success");
  } catch (error) {
    showMessage(taskMessage, error.message, "error");
  }
  loadTasks();
}

async function deleteTask(task) {
  if (!confirm(`Të fshihet detyra "${task.title}"?`)) return;
  try {
    await apiRequest("/tasks/" + task.id, { method: "DELETE" });
    showMessage(taskMessage, "Detyra u fshi.", "success");
  } catch (error) {
    showMessage(taskMessage, error.message, "error");
  }
  loadTasks();
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage(taskMessage, "");

  const title = document.getElementById("task-title").value.trim();
  const description = document.getElementById("task-description").value.trim();
  const priority = document.getElementById("task-priority").value;
  const deadline = document.getElementById("task-deadline").value;
  const assignee = assigneeSelect.value;

  // Validimi në frontend është vetëm për përdorshmëri; vendimi final merret në backend
  if (!title) {
    showMessage(taskMessage, "Titulli është i detyrueshëm.", "error");
    return;
  }
  if (title.length > 150) {
    showMessage(taskMessage, "Titulli mund të ketë më së shumti 150 karaktere.", "error");
    return;
  }

  const button = taskForm.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await apiRequest("/tasks", {
      method: "POST",
      body: JSON.stringify({
        project_id: Number(projectId),
        title,
        description: description || null,
        priority,
        deadline: deadline || null,
        assigned_to: assignee ? Number(assignee) : null,
      }),
    });
    taskForm.reset();
    showMessage(taskMessage, "Detyra u krijua.", "success");
    loadTasks();
  } catch (error) {
    showMessage(taskMessage, error.message, "error");
  } finally {
    button.disabled = false;
  }
});

// ---------- Komentet ----------
function buildCommentsPanel(taskId, panel) {
  const state = el("div", "state");
  state.hidden = true;
  const list = el("div");
  const message = el("div", "message");
  message.hidden = true;

  const form = el("form", "comment-form");
  const input = el("input");
  input.type = "text";
  input.placeholder = "Shkruaj një koment…";
  input.setAttribute("aria-label", "Koment i ri");
  const send = el("button", "btn btn-small", "Posto");
  send.type = "submit";
  form.appendChild(input);
  form.appendChild(send);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showMessage(message, "");
    const content = input.value.trim();
    if (!content) {
      showMessage(message, "Komenti nuk mund të jetë bosh.", "error");
      return;
    }
    send.disabled = true;
    try {
      await apiRequest(`/tasks/${taskId}/comments`, {
        method: "POST",
        body: JSON.stringify({ content }),
      });
      input.value = "";
      loadComments(taskId, list, state);
    } catch (error) {
      showMessage(message, error.message, "error");
    } finally {
      send.disabled = false;
    }
  });

  panel.appendChild(state);
  panel.appendChild(list);
  panel.appendChild(message);
  panel.appendChild(form);
  loadComments(taskId, list, state);
}

async function loadComments(taskId, list, state) {
  setState(state, "loading", "Duke ngarkuar komentet…");
  list.textContent = "";

  try {
    const comments = (await apiRequest(`/tasks/${taskId}/comments`)) || [];
    if (comments.length === 0) {
      setState(state, "empty", "Nuk ka komente ende.");
      return;
    }
    setState(state, "none");
    comments.forEach((comment) => {
      const item = el("div", "comment");
      const head = el("p");
      head.appendChild(el("strong", null, comment.author_name));
      head.appendChild(el("span", "muted", "  " + formatDate(comment.created_at)));
      item.appendChild(head);
      item.appendChild(el("p", null, comment.content));
      list.appendChild(item);
    });
  } catch (error) {
    setState(state, "error", error.message, () => loadComments(taskId, list, state));
  }
}

// ---------- Nisja ----------
async function init() {
  try {
    const found = await loadProject();
    if (!found) return;
  } catch (error) {
    setState(tasksState, "error", error.message, init);
    return;
  }
  await loadMembers();
  await loadTasks();
}

init();
