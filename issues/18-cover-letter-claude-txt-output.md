# 18 — Cover Letter: Claude Call + .txt Output

## What to build

When `generate_cover_letter=true` in the `/generate` request, make a second Claude call using the JD, company, job title, accepted summary, and accepted experience bullets as context. Write the output as a plain-text `.txt` file to the project root alongside the `.docx`.

Filename convention: `CoverLetter_{Company}_{JobTitle}_{YYYY-MM-DD}.txt`

The cover letter should be returned as a second file download (or the frontend can trigger two sequential downloads). Keep the Claude prompt focused: professional tone, three paragraphs, no hallucinated facts beyond what's in the resume content provided.

## Acceptance criteria

- [ ] When flag=true, a second Claude call is made after the resume is generated
- [ ] `.txt` file is written to project root with the correct filename convention
- [ ] File download is triggered in the browser (alongside or after the `.docx` download)
- [ ] When flag=false, no extra Claude call is made and no `.txt` is written
- [ ] Cover letter content references only information present in the provided resume context

## Blocked by

- #17 — Cover Letter: Checkbox + Flag Plumbing
