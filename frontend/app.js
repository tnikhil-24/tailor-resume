const state = {
  job_title: "",
  company: "",
  suggestions: null,
  decisions: {},
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

function checkGenerateReady() {
  const ready = state.decisions.summary !== undefined;
  const btn = document.getElementById("generate-btn");
  btn.disabled = !ready;
  document.getElementById("generate-hint").classList.toggle("hidden", ready);
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
  state.decisions = {};

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

    const { original, suggested } = state.suggestions.summary;
    document.getElementById("summary-diff").innerHTML = renderDiff(original, suggested);

    document.getElementById("results").classList.remove("hidden");
    document.getElementById("summary-accept").classList.remove("active");
    document.getElementById("summary-reject").classList.remove("active");
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
    const filename = res.headers.get("content-disposition")?.match(/filename="?([^"]+)"?/)?.[1]
      || `Resume_${state.company}_${state.job_title}.docx`;

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
