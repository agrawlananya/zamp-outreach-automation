import { createProspect } from "./api.js";

const form = document.getElementById("intake-form");
const submitButton = document.getElementById("submit-button");
const errorBox = document.getElementById("error-box");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.hidden = true;
  errorBox.textContent = "";
  submitButton.disabled = true;
  submitButton.textContent = "Starting research…";

  const data = {
    name: form.name.value.trim(),
    title: form.title.value.trim(),
    company_name: form.company_name.value.trim(),
  };

  try {
    const result = await createProspect(data);
    window.location.href = `run.html?id=${result.run_id}`;
  } catch (error) {
    errorBox.textContent = `Could not start research: ${error.message}`;
    errorBox.hidden = false;
    submitButton.disabled = false;
    submitButton.textContent = "Start Research";
  }
});
