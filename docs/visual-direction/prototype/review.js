const screens = {
  "dashboard-desktop": ["Dashboard · Desktop", 1440, 900],
  "dashboard-tablet": ["Dashboard · Tablet portrait", 768, 1024],
  "dashboard-mobile": ["Dashboard · Mobile", 390, 844],
  "focus-desktop": ["Focus · Desktop", 1440, 900],
  "focus-mobile": ["Focus · Mobile", 390, 844],
  "analytics-desktop": ["Analytics · Desktop", 1440, 900],
  "subject-desktop": ["Subject workspace · Desktop", 1440, 900],
  "design-system": ["Design System", 1440, 900],
};

const frame = document.querySelector("#prototype-frame");
const name = document.querySelector("#screen-name");
const size = document.querySelector("#screen-size");
const open = document.querySelector("#open-screen");
const viewport = document.querySelector("#viewport-size");
const scrollPosition = document.querySelector("#scroll-position");
let selectedScreen = "dashboard-desktop";

function applyViewport() {
  const [width, height] = viewport.value.split("x").map(Number);
  const query = `view=${selectedScreen}&width=${width}&height=${height}&scroll=${scrollPosition.value}`;
  frame.src = `screen.html?${query}`;
  frame.style.width = `${width}px`;
  frame.style.height = `${height}px`;
  size.textContent = `${width} × ${height}`;
  open.href = `screen.html?${query}`;
}

function selectScreen(id) {
  const [label] = screens[id];
  selectedScreen = id;
  const options = id === "design-system" ? [[1440,900],[1024,768],[768,1024],[390,844]] : id.includes("mobile") ? [[390,844],[430,932]] : id.includes("tablet") ? [[768,1024],[820,1180],[1024,768]] : [[1440,900],[1366,768],[1024,768]];
  viewport.replaceChildren(...options.map(([w,h]) => new Option(`${w} × ${h}`, `${w}x${h}`)));
  name.textContent = label;
  applyViewport();
  document.querySelectorAll("[data-screen]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.screen === id);
  });
}

document.querySelectorAll("[data-screen]").forEach((button) => {
  button.addEventListener("click", () => selectScreen(button.dataset.screen));
});

selectScreen("dashboard-desktop");
viewport.addEventListener("change", applyViewport);
scrollPosition.addEventListener("change", applyViewport);
