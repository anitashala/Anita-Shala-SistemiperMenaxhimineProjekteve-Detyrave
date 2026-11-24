// dashboard.js – statistikat nga GET /api/dashboard

requireLogin();
document.getElementById("logout-btn").addEventListener("click", logout);

const dashboardState = document.getElementById("dashboard-state");
const dashboardContent = document.getElementById("dashboard-content");
const myTasksList = document.getElementById("my-tasks");
const dueSoonList = document.getElementById("due-soon");

function renderTaskLinks(list, tasks, emptyText, showStatus) {
  list.textContent = "";
  if (tasks.length === 0) {
    list.appendChild(el("li", "muted", emptyText));
    return;
  }
  tasks.forEach((task) => {
    const item = el("li");
    const link = el("a", null, task.title);
    link.href = "tasks.html?project=" + task.project_id;
    item.appendChild(link);

    const parts = [];
    if (showStatus) parts.push(STATUS_LABELS[task.status]);
    if (task.deadline) parts.push("Afati: " + formatDate(task.deadline));
    item.appendChild(el("span", "muted", parts.join(" – ")));
    list.appendChild(item);
  });
}

async function loadDashboard() {
  setState(dashboardState, "loading", "Duke ngarkuar dashboard-in…");
  dashboardContent.hidden = true;

  try {
    const data = (await apiRequest("/dashboard")) || {};
    const byStatus = data.by_status || {};

    ["TODO", "IN_PROGRESS", "DONE"].forEach((status) => {
      document.getElementById("count-" + status).textContent = byStatus[status] || 0;
    });
    renderTaskLinks(myTasksList, data.my_tasks || [], "Nuk ju është caktuar asnjë detyrë.", true);
    renderTaskLinks(dueSoonList, data.due_soon || [], "Nuk ka detyra që skadojnë së shpejti.", false);

    setState(dashboardState, "none");
    dashboardContent.hidden = false;
  } catch (error) {
    setState(dashboardState, "error", error.message, loadDashboard);
  }
}

loadDashboard();
