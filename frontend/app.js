const scenarioId = "port-closure-001";
const recoverButton = document.querySelector("#recover");
const resetButton = document.querySelector("#reset");
const traceBox = document.querySelector("#trace");
const runState = document.querySelector("#run-state");
const networkStatus = document.querySelector("#network-status");
const outcome = document.querySelector("#outcome");

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function showTrace(trace) {
  const item = document.createElement("div");
  item.className = "trace-item";
  item.innerHTML = `<b>${trace.agent}</b><span>${trace.action.replaceAll("_", " ")}</span><p>${trace.summary}</p>`;
  traceBox.appendChild(item);
  traceBox.scrollTop = traceBox.scrollHeight;
}

async function resetScenario() {
  await fetch(`/api/scenarios/${scenarioId}/reset`, { method: "POST" });
  traceBox.innerHTML = '<div class="empty">Scenario reset. Start a recovery run.</div>';
  runState.textContent = "Waiting";
  networkStatus.textContent = "Disrupted";
  networkStatus.style.color = "#ff9aa3";
  outcome.classList.add("hidden");
}

async function runRecovery() {
  recoverButton.disabled = true;
  resetButton.disabled = true;
  runState.textContent = "Agents running";
  traceBox.innerHTML = "";
  outcome.classList.add("hidden");

  try {
    const response = await fetch(`/api/scenarios/${scenarioId}/recover`, { method: "POST" });
    const result = await response.json();
    for (const trace of result.traces) {
      showTrace(trace);
      await delay(300);
    }
    runState.textContent = result.status;
    if (result.status === "resolved") {
      networkStatus.textContent = "Recovered";
      networkStatus.style.color = "#6fffc1";
      document.querySelector("#route").textContent = result.final_plan.route_id;
      document.querySelector("#cost").textContent = `₹${result.final_plan.expected_cost}`;
      document.querySelector("#time").textContent = `${result.final_plan.expected_delivery_hours} hours`;
      document.querySelector("#carbon").textContent = `${result.final_plan.expected_carbon_kg} kg`;
      document.querySelector("#attempts").textContent = result.attempts;
      outcome.classList.remove("hidden");
    }
  } catch (error) {
    runState.textContent = "Error";
    traceBox.innerHTML = `<div class="empty">${error.message}</div>`;
  } finally {
    recoverButton.disabled = false;
    resetButton.disabled = false;
  }
}

recoverButton.addEventListener("click", runRecovery);
resetButton.addEventListener("click", resetScenario);
resetScenario();

