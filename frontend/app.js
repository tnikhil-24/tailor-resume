async function tailor() {
  const jd = document.getElementById("jd").value.trim();
  const job_title = document.getElementById("job_title").value.trim();
  const company = document.getElementById("company").value.trim();

  if (!jd || !job_title || !company) {
    alert("Please fill in Job Title, Company, and Job Description.");
    return;
  }

  const btn = document.getElementById("tailor-btn");
  btn.disabled = true;
  btn.textContent = "Tailoring...";

  try {
    const res = await fetch("/tailor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd, job_title, company }),
    });

    const data = await res.json();
    console.log("Response:", data);

    const output = document.getElementById("output");
    output.classList.remove("hidden");
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    console.error("Error:", err);
    alert("Something went wrong. Check the console.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Tailor Resume";
  }
}
