// api.js – i vetmi vend ku bëhen thirrjet fetch() drejt backend-it,
// plus disa funksione ndihmëse të përbashkëta për të gjitha faqet.

const API_URL = "http://localhost:8000/api";

const STATUS_LABELS = {
  TODO: "Për t’u bërë",
  IN_PROGRESS: "Në progres",
  DONE: "Përfunduar",
};

const PRIORITY_LABELS = {
  LOW: "E ulët",
  MEDIUM: "Mesatare",
  HIGH: "E lartë",
};

// ---------- Thirrja kryesore drejt API-së ----------
async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = "Bearer " + token;

  let response;
  try {
    response = await fetch(API_URL + path, { ...options, headers });
  } catch (error) {
    throw new Error("Nuk u lidh me serverin. Kontrollo që backend-i është i ndezur.");
  }

  // Token i skaduar ose i pavlefshëm: kthehu te login (jo për /auth/, që mesazhi të shfaqet te forma)
  if (response.status === 401 && !path.startsWith("/auth/")) {
    localStorage.removeItem("token");
    window.location.href = "login.html";
    return;
  }

  if (response.status === 204) return null;

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || "Gabim i panjohur");
  return data;
}

// ---------- Sesioni ----------
function requireLogin() {
  if (!localStorage.getItem("token")) window.location.href = "login.html";
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}

// ---------- Ndihmëse për UI ----------
// Krijon element me tekst të sigurt (textContent, jo innerHTML)
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

// Gjendjet e listave: "loading", "empty", "error" ose "none" (e fshehur)
function setState(box, type, message, onRetry) {
  box.textContent = "";
  if (type === "none") {
    box.hidden = true;
    return;
  }
  box.hidden = false;
  box.className = "state state-" + type;
  box.appendChild(el("p", null, message));
  if (type === "error" && onRetry) {
    const retry = el("button", "btn btn-light btn-small", "Provo përsëri");
    retry.type = "button";
    retry.addEventListener("click", onRetry);
    box.appendChild(retry);
  }
}

// Mesazh mbi forma: kind = "error" ose "success"
function showMessage(box, text, kind) {
  if (!text) {
    box.hidden = true;
    box.textContent = "";
    return;
  }
  box.textContent = text;
  box.className = "message message-" + kind;
  box.hidden = false;
}

function formatDate(value) {
  if (!value) return "";
  const [year, month, day] = String(value).slice(0, 10).split("-");
  return `${day}.${month}.${year}`;
}
