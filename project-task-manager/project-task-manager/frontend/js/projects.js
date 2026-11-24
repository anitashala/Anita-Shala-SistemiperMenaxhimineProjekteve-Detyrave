// projects.js – lista e projekteve, krijimi dhe fshirja

requireLogin();
document.getElementById("logout-btn").addEventListener("click", logout);

const projectForm = document.getElementById("project-form");
const projectMessage = document.getElementById("project-message");
const projectsState = document.getElementById("projects-state");
const projectsList = document.getElementById("projects-list");

async function loadProjects() {
  setState(projectsState, "loading", "Duke ngarkuar projektet…");
  projectsList.textContent = "";

  try {
    const projects = (await apiRequest("/projects")) || [];
    if (projects.length === 0) {
      setState(projectsState, "empty", "Nuk keni asnjë projekt. Krijoni të parin më sipër.");
      return;
    }
    setState(projectsState, "none");
    projects.forEach((project) => projectsList.appendChild(renderProject(project)));
  } catch (error) {
    setState(projectsState, "error", error.message, loadProjects);
  }
}

function renderProject(project) {
  const card = el("article", "card");

  card.appendChild(el("h3", null, project.name));
  card.appendChild(el("span", "badge badge-" + project.my_role, project.my_role === "OWNER" ? "Pronar" : "Anëtar"));
  if (project.description) card.appendChild(el("p", null, project.description));
  if (project.deadline) card.appendChild(el("p", "muted", "Afati: " + formatDate(project.deadline)));

  const actions = el("div", "card-actions");
  const open = el("a", "btn btn-small", "Hap projektin");
  open.href = "tasks.html?project=" + project.id;
  actions.appendChild(open);

  if (project.my_role === "OWNER") {
    const remove = el("button", "btn btn-danger btn-small", "Fshij");
    remove.type = "button";
    remove.addEventListener("click", () => deleteProject(project));
    actions.appendChild(remove);
  }
  card.appendChild(actions);
  return card;
}

async function deleteProject(project) {
  if (!confirm(`Të fshihet projekti "${project.name}" me të gjitha detyrat e tij?`)) return;
  try {
    await apiRequest("/projects/" + project.id, { method: "DELETE" });
    showMessage(projectMessage, "Projekti u fshi.", "success");
    loadProjects();
  } catch (error) {
    showMessage(projectMessage, error.message, "error");
  }
}

projectForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage(projectMessage, "");

  const name = document.getElementById("project-name").value.trim();
  const description = document.getElementById("project-description").value.trim();
  const deadline = document.getElementById("project-deadline").value;

  if (!name) {
    showMessage(projectMessage, "Emri i projektit është i detyrueshëm.", "error");
    return;
  }

  const button = projectForm.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    await apiRequest("/projects", {
      method: "POST",
      body: JSON.stringify({ name, description: description || null, deadline: deadline || null }),
    });
    projectForm.reset();
    showMessage(projectMessage, "Projekti u krijua.", "success");
    loadProjects();
  } catch (error) {
    showMessage(projectMessage, error.message, "error");
  } finally {
    button.disabled = false;
  }
});

loadProjects();
