const state = {
  job_title: "",
  company: "",
  suggestions: null,
  decisions: {},
  totalBullets: 0,
  totalAdditions: 0,
  selectedProjects: new Set(),
};

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function renderDiff(original, suggested) {
  const dmp = new diff_match_patch();
  const diffs = dmp.diff_main(original, suggested);
  dmp.diff_cleanupSemantic(diffs);
  return diffs
    .map((d) => {
      const op = d[0], text = d[1];
      if (op === -1) return `<span class="diff-del">${escapeHtml(text)}</span>`;
      if (op === 1) return `<span class="diff-ins">${escapeHtml(text)}</span>`;
      return escapeHtml(text);
    })
    .join("");
}

function decideSummary(accepted) {
  const s = state.suggestions.summary;
  state.decisions.summary = {
    accepted,
    suggested: s.suggested,
    paragraph_index: s.paragraph_index,
  };
  document.getElementById("summary-accept").classList.toggle("active", accepted);
  document.getElementById("summary-reject").classList.toggle("active", !accepted);
  checkGenerateReady();
}

function decideBullet(paragraphIndex, accepted) {
  const allBullets = state.suggestions.experience.flatMap((r) => r.bullets);
  const bullet = allBullets.find((b) => b.paragraph_index === paragraphIndex);

  if (!state.decisions.experience) state.decisions.experience = [];
  const existing = state.decisions.experience.find((d) => d.paragraph_index === paragraphIndex);
  if (existing) {
    existing.accepted = accepted;
  } else {
    state.decisions.experience.push({ accepted, suggested: bullet.suggested, paragraph_index: paragraphIndex });
  }

  document.getElementById(`bullet-accept-${paragraphIndex}`).classList.toggle("active", accepted);
  document.getElementById(`bullet-reject-${paragraphIndex}`).classList.toggle("active", !accepted);
  checkGenerateReady();
}

function decideAddition(index, added) {
  const addition = state.suggestions.skills.suggested_additions[index];
  if (!state.decisions.skills) state.decisions.skills = { reordered_categories: state.suggestions.skills.reordered_categories, additions: [] };

  const existing = state.decisions.skills.additions.find((a) => a.category === addition.category && a.skill === addition.skill);
  if (existing) {
    existing.added = added;
  } else {
    state.decisions.skills.additions.push({ category: addition.category, skill: addition.skill, added });
  }

  document.getElementById(`add-btn-${index}`).classList.toggle("active", added);
  document.getElementById(`skip-btn-${index}`).classList.toggle("active", !added);
  checkGenerateReady();
}

function toggleProject(titleParagraphIndex) {
  if (state.selectedProjects.has(titleParagraphIndex)) {
    state.selectedProjects.delete(titleParagraphIndex);
  } else {
    state.selectedProjects.add(titleParagraphIndex);
  }

  const count = state.selectedProjects.size;
  document.getElementById("projects-counter").textContent =
    count === 0 ? "Select 1–3" : `${count} selected`;

  state.decisions.projects = {
    all_projects: state.suggestions.projects.map((p) => ({
      title_paragraph_index: p.title_paragraph_index,
      all_paragraph_indices: p.all_paragraph_indices,
    })),
    selected_title_paragraph_indices: Array.from(state.selectedProjects),
  };

  checkGenerateReady();
}

function decideOptional(key, keep) {
  if (!state.decisions.optional_sections) state.decisions.optional_sections = {};
  const section = state.suggestions.optional_sections[key];
  state.decisions.optional_sections[key] = {
    keep,
    all_paragraph_indices: section.all_paragraph_indices,
  };

  document.getElementById(`opt-keep-${key}`).classList.toggle("active", keep);
  document.getElementById(`opt-remove-${key}`).classList.toggle("active", !keep);
  checkGenerateReady();
}

function checkGenerateReady() {
  const summaryDone = state.decisions.summary !== undefined;
  const decidedBullets = (state.decisions.experience || []).length;
  const decidedAdditions = (state.decisions.skills?.additions || []).length;
  const projectsOk = state.selectedProjects.size >= 1 && state.selectedProjects.size <= 3;
  const optionalKeys = Object.keys(state.suggestions?.optional_sections || {});
  const decidedOptional = Object.keys(state.decisions.optional_sections || {}).length;
  const optionalDone = decidedOptional === optionalKeys.length;

  const ready = summaryDone && decidedBullets === state.totalBullets &&
    decidedAdditions === state.totalAdditions && projectsOk && optionalDone;

  document.getElementById("generate-btn").disabled = !ready;
  document.getElementById("generate-hint").classList.toggle("hidden", ready);
}

function renderExperience(experience) {
  state.totalBullets = experience.flatMap((r) => r.bullets).length;
  const container = document.getElementById("experience-content");
  container.innerHTML = "";

  experience.forEach((role) => {
    const group = document.createElement("div");
    group.className = "role-group";

    const label = document.createElement("div");
    label.className = "role-label";
    label.textContent = role.company;
    group.appendChild(label);

    role.bullets.forEach((bullet) => {
      const row = document.createElement("div");
      row.className = "bullet-row";

      const diffEl = document.createElement("div");
      diffEl.className = "diff-content";
      diffEl.innerHTML = renderDiff(bullet.original, bullet.suggested);

      const actions = document.createElement("div");
      actions.className = "section-actions";
      actions.innerHTML = `
        <button id="bullet-accept-${bullet.paragraph_index}" class="btn-accept"
          onclick="decideBullet(${bullet.paragraph_index}, true)">Accept</button>
        <button id="bullet-reject-${bullet.paragraph_index}" class="btn-reject"
          onclick="decideBullet(${bullet.paragraph_index}, false)">Reject</button>
      `;

      row.appendChild(diffEl);
      row.appendChild(actions);
      group.appendChild(row);
    });

    container.appendChild(group);
  });

  document.getElementById("experience-section").classList.remove("hidden");
}

function renderSkills(skills) {
  state.totalAdditions = skills.suggested_additions.length;

  // Reordered preview
  const preview = document.getElementById("skills-preview");
  preview.innerHTML = skills.reordered_categories
    .map((cat) => `<div class="skill-row"><span class="skill-category">${escapeHtml(cat.category)}:</span> ${escapeHtml(cat.items.join(", "))}</div>`)
    .join("");

  // Suggested additions
  const additionsEl = document.getElementById("skills-additions");
  if (skills.suggested_additions.length === 0) {
    additionsEl.innerHTML = "";
    state.decisions.skills = { reordered_categories: skills.reordered_categories, additions: [] };
  } else {
    additionsEl.innerHTML = `
      <div class="additions-header">Suggested additions from JD</div>
      ${skills.suggested_additions
        .map((a, i) => `
          <div class="addition-row">
            <div class="addition-info">
              <span class="addition-skill">${escapeHtml(a.skill)}</span>
              <span class="addition-category">→ ${escapeHtml(a.category)}</span>
              <span class="addition-reason">${escapeHtml(a.reason)}</span>
            </div>
            <div class="section-actions">
              <button id="add-btn-${i}" class="btn-accept" onclick="decideAddition(${i}, true)">Add</button>
              <button id="skip-btn-${i}" class="btn-reject" onclick="decideAddition(${i}, false)">Skip</button>
            </div>
          </div>`)
        .join("")}`;
  }

  document.getElementById("skills-section").classList.remove("hidden");
}

function renderProjects(projects) {
  state.selectedProjects = new Set();
  const container = document.getElementById("projects-content");
  container.innerHTML = projects
    .map(
      (p) => `
      <div class="project-row" id="project-row-${p.title_paragraph_index}">
        <label class="project-check">
          <input type="checkbox" onchange="toggleProject(${p.title_paragraph_index})" />
          <div class="project-info">
            <span class="project-title">${escapeHtml(p.title)}</span>
            <span class="project-score">${p.relevance_score}%</span>
          </div>
        </label>
        <div class="project-reason">${escapeHtml(p.reason)}</div>
      </div>`
    )
    .join("");
  document.getElementById("projects-counter").textContent = "Select 1–3";
  document.getElementById("projects-section").classList.remove("hidden");
}

const OPTIONAL_LABELS = {
  research_paper: "Research Paper",
  achievements: "Achievements",
  certifications: "Certifications",
};

function renderOptionalSections(optional_sections) {
  const container = document.getElementById("optional-content");
  container.innerHTML = Object.entries(optional_sections)
    .map(([key, data]) => `
      <div class="section-card">
        <div class="section-header">
          <span class="section-title">${OPTIONAL_LABELS[key] || key}</span>
          <div class="section-actions">
            <button id="opt-keep-${key}" class="btn-accept ${data.keep ? "active" : ""}"
              onclick="decideOptional('${key}', true)">Keep</button>
            <button id="opt-remove-${key}" class="btn-reject ${!data.keep ? "active" : ""}"
              onclick="decideOptional('${key}', false)">Remove</button>
          </div>
        </div>
        <div class="opt-reason">${escapeHtml(data.reason)}</div>
      </div>`)
    .join("");
  document.getElementById("optional-sections").classList.remove("hidden");

  // Pre-populate decisions with Claude's defaults
  if (!state.decisions.optional_sections) state.decisions.optional_sections = {};
  for (const [key, data] of Object.entries(optional_sections)) {
    state.decisions.optional_sections[key] = {
      keep: data.keep,
      all_paragraph_indices: data.all_paragraph_indices,
    };
  }
}

function renderGaps(gaps) {
  if (!gaps || gaps.length === 0) return;
  document.getElementById("gaps-content").innerHTML = gaps
    .map((g) => `<span class="gap-chip">${escapeHtml(g)}</span>`)
    .join("");
  document.getElementById("gaps-section").classList.remove("hidden");
}

async function tailor() {
  const jd = document.getElementById("jd").value.trim();
  const job_title = document.getElementById("job_title").value.trim();
  const company = document.getElementById("company").value.trim();

  if (!jd || !job_title || !company) {
    alert("Please fill in Job Title, Company, and Job Description.");
    return;
  }

  state.job_title = job_title;
  state.company = company;
  state.decisions = { optional_sections: {} };
  state.totalBullets = 0;
  state.totalAdditions = 0;
  state.selectedProjects = new Set();

  const btn = document.getElementById("tailor-btn");
  btn.disabled = true;
  btn.textContent = "Tailoring...";

  try {
    const res = await fetch("/tailor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd, job_title, company }),
    });

    if (!res.ok) throw new Error(await res.text());

    state.suggestions = await res.json();

    // Render summary
    const { original, suggested } = state.suggestions.summary;
    document.getElementById("summary-diff").innerHTML = renderDiff(original, suggested);
    document.getElementById("summary-accept").classList.remove("active");
    document.getElementById("summary-reject").classList.remove("active");

    // Render experience
    renderExperience(state.suggestions.experience);

    // Render skills
    renderSkills(state.suggestions.skills);

    // Render projects
    renderProjects(state.suggestions.projects);

    // Render optional sections and gaps
    renderOptionalSections(state.suggestions.optional_sections);
    renderGaps(state.suggestions.gaps);

    document.getElementById("results").classList.remove("hidden");
    document.getElementById("generate-btn").disabled = true;
    document.getElementById("generate-hint").classList.remove("hidden");

    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    console.error(err);
    alert("Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Tailor Resume";
  }
}

async function generateResume() {
  const btn = document.getElementById("generate-btn");
  btn.disabled = true;
  btn.textContent = "Generating...";

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        decisions: state.decisions,
        job_title: state.job_title,
        company: state.company,
      }),
    });

    if (!res.ok) throw new Error(await res.text());

    const blob = await res.blob();
    const filename =
      res.headers.get("content-disposition")?.match(/filename="?([^"]+)"?/)?.[1] ||
      `Resume_${state.company}_${state.job_title}.docx`;

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error(err);
    alert("Error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate Tailored Resume";
  }
}
