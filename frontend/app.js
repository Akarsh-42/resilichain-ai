const scenarioId = "port-closure-001";

const ui = {
  recover: document.querySelector("#recover"),
  reset: document.querySelector("#reset"),
  export: document.querySelector("#export"),
  exportSecondary: document.querySelector("#export-secondary"),
  trace: document.querySelector("#trace"),
  runState: document.querySelector("#run-state"),
  agentsState: document.querySelector("#agents-state"),
  networkStatus: document.querySelector("#network-status"),
  outcome: document.querySelector("#outcome"),
  candidateTable: document.querySelector("#candidate-table"),
  progressBar: document.querySelector("#progress-bar"),
  progressValue: document.querySelector("#progress-value"),
  incidentCount: document.querySelector("#incident-count"),
  revision: document.querySelector("#network-revision"),
  centralStock: document.querySelector("#central-stock"),
  responseMode: document.querySelector("#response-mode"),
  riskScore: document.querySelector("#risk-score"),
  budgetUse: document.querySelector("#budget-use"),
  carbonUse: document.querySelector("#carbon-use"),
  verificationChecks: document.querySelector("#verification-checks"),
  toast: document.querySelector("#toast"),
  clock: document.querySelector("#clock"),
  sla: document.querySelector("#sla"),
};

const routeNames = {
  "east-road": "East road corridor",
  "west-road": "West road carrier",
  "south-express": "South road–rail express",
  "emergency-air": "Emergency air freight",
};

let latestRun = null;
let latestCandidates = [];
let toastTimer = null;
let slaSeconds = 24 * 60 * 60;

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const titleCase = (value) => value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
const money = (value) => `₹${Number(value).toLocaleString("en-IN")}`;

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function toast(message) {
  clearTimeout(toastTimer);
  ui.toast.textContent = message;
  ui.toast.classList.add("show");
  toastTimer = setTimeout(() => ui.toast.classList.remove("show"), 2600);
}

function setPill(element, label, state = "") {
  element.textContent = label;
  element.className = `status-pill ${state}`.trim();
}

function setProgress(value) {
  const safe = Math.max(0, Math.min(100, Math.round(value)));
  ui.progressBar.style.width = `${safe}%`;
  ui.progressValue.textContent = `${safe}%`;
}

function resetAgents() {
  document.querySelectorAll(".agent-card").forEach((card) => {
    card.classList.remove("active", "complete", "failed");
    card.querySelector("b").textContent = "Ready";
  });
}

function setAgentState(agent, state) {
  const card = [...document.querySelectorAll(".agent-card")].find(
    (item) => item.dataset.agent === agent,
  );
  if (!card) return;

  document.querySelectorAll(".agent-card.active").forEach((item) => {
    if (item !== card) {
      item.classList.remove("active");
      item.classList.add("complete");
      item.querySelector("b").textContent = "Complete";
    }
  });

  card.classList.remove("active", "complete", "failed");
  card.classList.add(state);
  card.querySelector("b").textContent =
    state === "active" ? "Working" : state === "failed" ? "Retrying" : "Complete";
}

function routeViolations(route, state) {
  const rules = state.constraints;
  const source = state.nodes.find((node) => node.id === route.source_id);
  const inventory = source?.inventory?.[rules.sku] ?? 0;
  const violations = [];
  if (!route.available) violations.push("route unavailable");
  if (inventory < rules.required_units) violations.push("inventory");
  if (route.capacity_units < rules.required_units) violations.push("capacity");
  if (route.cost > rules.maximum_cost) violations.push("budget");
  if (route.delivery_hours > rules.deadline_hours) violations.push("deadline");
  if (route.carbon_kg > rules.maximum_carbon_kg) violations.push("carbon");
  return violations;
}

function scoreRoute(route, state) {
  const rules = state.constraints;
  return (
    0.45 * (route.cost / rules.maximum_cost) +
    0.35 * (route.delivery_hours / rules.deadline_hours) +
    0.2 * (route.carbon_kg / rules.maximum_carbon_kg)
  ).toFixed(4);
}

function renderCandidateTable(candidates, selectedRoute = null) {
  latestCandidates = candidates;
  if (!candidates?.length) {
    ui.candidateTable.innerHTML = '<tr><td colspan="7" class="table-empty">No recovery alternatives available.</td></tr>';
    return;
  }

  ui.candidateTable.innerHTML = candidates
    .map((candidate) => {
      const violations = candidate.violations || [];
      const feasible = candidate.feasible ?? violations.length === 0;
      const selected = candidate.route_id === selectedRoute;
      return `
        <tr class="${selected ? "selected-row" : ""}">
          <td><strong>${escapeHtml(routeNames[candidate.route_id] || candidate.route_id)}</strong><span class="route-mode">${escapeHtml(candidate.mode || candidate.route_id)}</span></td>
          <td><span class="cell-pill ${candidate.available === false ? "fail" : "pass"}">${candidate.available === false ? "Blocked" : "Available"}</span></td>
          <td>${money(candidate.cost)}</td>
          <td>${candidate.delivery_hours}h</td>
          <td>${candidate.carbon_kg} kg</td>
          <td><span class="cell-pill ${feasible ? "pass" : "fail"}">${feasible ? "Feasible" : escapeHtml(violations.join(", "))}</span></td>
          <td><span class="cell-pill ${selected ? "chosen" : ""}">${selected ? "SELECTED" : feasible ? candidate.score ?? "Eligible" : "Rejected"}</span></td>
        </tr>
      `;
    })
    .join("");
}

function candidatesFromState(state) {
  return state.routes.map((route) => {
    const violations = routeViolations(route, state);
    return {
      ...route,
      feasible: violations.length === 0,
      violations,
      score: violations.length ? null : scoreRoute(route, state),
    };
  });
}

function selectRoute(routeId) {
  document.querySelectorAll(".route").forEach((route) => {
    route.classList.toggle("selected", route.dataset.route === routeId);
  });
  renderCandidateTable(latestCandidates, routeId);
}

function renderScenario(state, selectedRoute = null, updateCandidates = true) {
  const routeById = Object.fromEntries(state.routes.map((route) => [route.id, route]));
  document.querySelectorAll(".route").forEach((element) => {
    const route = routeById[element.dataset.route];
    if (!route) return;
    element.classList.toggle("blocked", !route.available);
    element.classList.toggle("selected", element.dataset.route === selectedRoute);
  });

  const nodes = Object.fromEntries(state.nodes.map((node) => [node.id, node]));
  const west = document.querySelector('[data-node="wh-west"]');
  west.classList.toggle("disrupted", routeById["west-road"]?.available === false);
  west.querySelector("small").textContent = `${nodes["wh-west"]?.inventory?.["SKU-AX9"] ?? 0} units · ${routeById["west-road"]?.available ? "READY" : "CARRIER DOWN"}`;

  const south = document.querySelector('[data-node="wh-south"]');
  south.querySelector("small").textContent = `${nodes["wh-south"]?.inventory?.["SKU-AX9"] ?? 0} units · ${selectedRoute === "south-express" ? "DISPATCHED" : "READY"}`;

  const storeStock = nodes["store-central"]?.inventory?.["SKU-AX9"] ?? 0;
  ui.centralStock.textContent = `${storeStock} units · ${state.status === "recovered" ? "SERVICE RESTORED" : "AT RISK"}`;
  ui.revision.textContent = `STATE REV ${state.revision}`;
  ui.incidentCount.textContent = `${state.disruptions.filter((item) => item.active).length} active disruption${state.disruptions.filter((item) => item.active).length === 1 ? "" : "s"}`;
  if (updateCandidates) renderCandidateTable(candidatesFromState(state), selectedRoute);
}

function traceClass(trace) {
  if (trace.action === "verify_outcome") return "success";
  if (trace.action === "replan" || (trace.action === "execute_action" && trace.summary.includes("failed"))) return "failure";
  return "active";
}

function showTrace(trace, total) {
  const item = document.createElement("div");
  item.className = `trace-item ${traceClass(trace)}`;
  const evidence = Object.keys(trace.evidence || {}).length
    ? `<details><summary>Inspect evidence</summary><pre>${escapeHtml(JSON.stringify(trace.evidence, null, 2))}</pre></details>`
    : "";
  item.innerHTML = `
    <div class="trace-line"><b>${escapeHtml(trace.agent)}</b><span>${String(trace.sequence).padStart(2, "0")} · ${escapeHtml(titleCase(trace.action))}</span></div>
    <p>${escapeHtml(trace.summary)}</p>
    ${evidence}
  `;
  ui.trace.appendChild(item);
  ui.trace.scrollTop = ui.trace.scrollHeight;
  setAgentState(trace.agent, "active");
  setProgress((trace.sequence / total) * 100);

  if (trace.action === "build_candidates" && Array.isArray(trace.evidence.candidates)) {
    latestCandidates = trace.evidence.candidates.map((candidate) => ({
      ...candidate,
      available: !candidate.violations?.includes("route_unavailable"),
    }));
    renderCandidateTable(latestCandidates);
  }

  if (trace.action === "select_plan") {
    latestCandidates = latestCandidates.map((candidate) =>
      candidate.route_id === trace.evidence.route_id
        ? { ...candidate, score: trace.evidence.score }
        : candidate,
    );
    selectRoute(trace.evidence.route_id);
  }

  if (trace.action === "execute_action" && trace.summary.includes("failed")) {
    const failedRoute = document.querySelector(`[data-route="${trace.evidence.route_id}"]`);
    failedRoute?.classList.add("blocked");
    document.querySelector('[data-node="wh-west"]')?.classList.add("disrupted");
    ui.incidentCount.textContent = "2 active disruptions";
    ui.riskScore.textContent = "93";
    setAgentState("Control Tower Orchestrator", "failed");
    toast("Carrier failure observed. The orchestrator is replanning.");
  }
}

function renderOutcome(result) {
  const plan = result.final_plan;
  document.querySelector("#route").textContent = routeNames[plan.route_id] || plan.route_id;
  document.querySelector("#cost").textContent = money(plan.expected_cost);
  document.querySelector("#time").textContent = `${plan.expected_delivery_hours} hours`;
  document.querySelector("#carbon").textContent = `${plan.expected_carbon_kg} kg CO₂e`;
  document.querySelector("#attempts").textContent = result.attempts;
  document.querySelector("#outcome-copy").textContent =
    `The control tower adapted after a live carrier failure and restored ${result.state.constraints.required_units} units of ${result.state.constraints.sku}.`;

  ui.verificationChecks.innerHTML = Object.entries(result.verification.checks)
    .filter(([, passed]) => passed)
    .map(([check]) => `<span class="verification-check">${escapeHtml(titleCase(check))}</span>`)
    .join("");

  ui.budgetUse.textContent = `${Math.round((plan.expected_cost / result.state.constraints.maximum_cost) * 100)}% used · ${money(result.state.constraints.maximum_cost - plan.expected_cost)} buffer`;
  ui.carbonUse.textContent = `${Math.round((plan.expected_carbon_kg / result.state.constraints.maximum_carbon_kg) * 100)}% used · ${result.state.constraints.maximum_carbon_kg - plan.expected_carbon_kg} kg buffer`;
  ui.riskScore.textContent = "18";
  ui.responseMode.textContent = "Autonomous · adapted";
  renderScenario(result.state, plan.route_id, false);
  renderCandidateTable(latestCandidates, plan.route_id);
  setPill(ui.networkStatus, "RECOVERED", "success");
  setPill(ui.runState, "RESOLVED", "success");
  setPill(ui.agentsState, "COMPLETE", "success");
  document.querySelectorAll(".agent-card").forEach((card) => {
    card.classList.remove("active", "failed");
    card.classList.add("complete");
    card.querySelector("b").textContent = "Complete";
  });
  setProgress(100);
  ui.outcome.classList.remove("hidden");
  ui.export.disabled = false;
  ui.outcome.scrollIntoView({ behavior: "smooth", block: "nearest" });
  toast("Recovery verified. All five operational constraints passed.");
}

async function resetScenario({ quiet = false } = {}) {
  ui.recover.disabled = true;
  ui.reset.disabled = true;
  try {
    const response = await fetch(`/api/scenarios/${scenarioId}/reset`, { method: "POST" });
    if (!response.ok) throw new Error(`Reset failed (${response.status})`);
    const state = await response.json();
    latestRun = null;
    slaSeconds = 24 * 60 * 60;
    ui.trace.innerHTML = '<div class="trace-empty"><span>✦</span><strong>System ready</strong><p>Run the recovery scenario to watch five agents collaborate and adapt.</p></div>';
    ui.outcome.classList.add("hidden");
    ui.export.disabled = true;
    ui.riskScore.textContent = "87";
    ui.budgetUse.textContent = "Awaiting selected plan";
    ui.carbonUse.textContent = "Constraint enforced by verifier";
    ui.responseMode.textContent = "Autonomous";
    resetAgents();
    setProgress(0);
    setPill(ui.runState, "WAITING");
    setPill(ui.agentsState, "STANDBY");
    setPill(ui.networkStatus, "DISRUPTED", "danger");
    renderScenario(state);
    if (!quiet) toast("Scenario restored to its initial disruption state.");
  } catch (error) {
    setPill(ui.runState, "ERROR", "danger");
    toast(error.message);
  } finally {
    ui.recover.disabled = false;
    ui.reset.disabled = false;
  }
}

async function runRecovery() {
  ui.recover.disabled = true;
  ui.reset.disabled = true;
  ui.outcome.classList.add("hidden");
  ui.trace.innerHTML = "";
  resetAgents();
  setProgress(2);
  setPill(ui.runState, "RUNNING", "running");
  setPill(ui.agentsState, "ACTIVE", "running");
  toast("Autonomous recovery started.");

  try {
    const response = await fetch(`/api/scenarios/${scenarioId}/recover`, { method: "POST" });
    if (!response.ok) throw new Error(`Recovery failed (${response.status})`);
    const result = await response.json();
    latestRun = result;

    for (const trace of result.traces) {
      showTrace(trace, result.traces.length);
      await delay(390);
    }

    if (result.status === "resolved" && result.verification?.passed) {
      renderOutcome(result);
    } else {
      setPill(ui.runState, "HUMAN REVIEW", "danger");
      setPill(ui.agentsState, "ESCALATED", "danger");
      toast("No safe autonomous plan was found. Human review requested.");
    }
  } catch (error) {
    setPill(ui.runState, "ERROR", "danger");
    setPill(ui.agentsState, "INTERRUPTED", "danger");
    ui.trace.innerHTML = `<div class="trace-empty"><span>!</span><strong>Run interrupted</strong><p>${escapeHtml(error.message)}</p></div>`;
    toast(error.message);
  } finally {
    ui.recover.disabled = false;
    ui.reset.disabled = false;
  }
}

function exportRun() {
  if (!latestRun) return;
  const blob = new Blob([JSON.stringify(latestRun, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `resilichain-run-${latestRun.run_id.slice(0, 8)}.json`;
  link.click();
  URL.revokeObjectURL(url);
  toast("Run report exported.");
}

function updateTime() {
  const now = new Date();
  ui.clock.textContent = `${now.toLocaleTimeString("en-GB", { hour12: false, timeZone: "UTC" })} UTC`;
  slaSeconds = Math.max(0, slaSeconds - 1);
  const hours = Math.floor(slaSeconds / 3600);
  const minutes = Math.floor((slaSeconds % 3600) / 60);
  const seconds = slaSeconds % 60;
  ui.sla.textContent = [hours, minutes, seconds].map((value) => String(value).padStart(2, "0")).join(":");
}

async function boot() {
  updateTime();
  setInterval(updateTime, 1000);
  try {
    const health = await fetch("/api/health");
    if (!health.ok) throw new Error("Backend unavailable");
    await resetScenario({ quiet: true });
  } catch (error) {
    setPill(ui.runState, "OFFLINE", "danger");
    toast("Could not connect to the FastAPI backend.");
  }
}

ui.recover.addEventListener("click", runRecovery);
ui.reset.addEventListener("click", () => resetScenario());
ui.export.addEventListener("click", exportRun);
ui.exportSecondary.addEventListener("click", exportRun);
document.addEventListener("keydown", (event) => {
  if (event.key.toLowerCase() === "r" && !event.metaKey && !event.ctrlKey && !event.altKey) {
    if (!["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) runRecovery();
  }
});

boot();
