// login.js – kyçja dhe regjistrimi

if (localStorage.getItem("token")) {
  window.location.href = "projects.html";
}

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginMessage = document.getElementById("login-message");
const registerMessage = document.getElementById("register-message");
const tabLogin = document.getElementById("tab-login");
const tabRegister = document.getElementById("tab-register");

function showTab(which) {
  const isLogin = which === "login";
  loginForm.hidden = !isLogin;
  registerForm.hidden = isLogin;
  tabLogin.classList.toggle("active", isLogin);
  tabRegister.classList.toggle("active", !isLogin);
  tabLogin.setAttribute("aria-selected", String(isLogin));
  tabRegister.setAttribute("aria-selected", String(!isLogin));
}

tabLogin.addEventListener("click", () => showTab("login"));
tabRegister.addEventListener("click", () => showTab("register"));

async function loginAndRedirect(email, password) {
  const data = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  localStorage.setItem("token", data.access_token);
  window.location.href = "projects.html";
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage(loginMessage, "");

  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  if (!email || !password) {
    showMessage(loginMessage, "Shkruaj email-in dhe fjalëkalimin.", "error");
    return;
  }

  const button = loginForm.querySelector("button[type=submit]");
  button.disabled = true;
  button.textContent = "Duke u kyçur…";
  try {
    await loginAndRedirect(email, password);
  } catch (error) {
    showMessage(loginMessage, error.message, "error");
    button.disabled = false;
    button.textContent = "Kyçu";
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage(registerMessage, "");

  const fullName = document.getElementById("register-name").value.trim();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;

  if (!fullName) {
    showMessage(registerMessage, "Emri është i detyrueshëm.", "error");
    return;
  }
  if (!email.includes("@")) {
    showMessage(registerMessage, "Shkruaj një email të vlefshëm.", "error");
    return;
  }
  if (password.length < 8) {
    showMessage(registerMessage, "Fjalëkalimi duhet të ketë të paktën 8 karaktere.", "error");
    return;
  }

  const button = registerForm.querySelector("button[type=submit]");
  button.disabled = true;
  button.textContent = "Duke krijuar llogarinë…";
  try {
    await apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, email, password }),
    });
    await loginAndRedirect(email, password);
  } catch (error) {
    showMessage(registerMessage, error.message, "error");
    button.disabled = false;
    button.textContent = "Krijo llogari";
  }
});
