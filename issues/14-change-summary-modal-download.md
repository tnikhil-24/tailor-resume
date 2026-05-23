# 14 — Change Summary Modal: Download Integration

## What to build

Add a "Download Resume" button inside the change summary modal (from #13). Clicking it fires the existing `/generate` POST request, triggers the `.docx` file download, and closes the modal on success. If the cover letter checkbox is checked (issue #17), the modal should note "Cover letter will also be generated" and both files download.

## Acceptance criteria

- [ ] "Download Resume" button is visible inside the modal
- [ ] Clicking it fires `/generate` with the current decisions payload
- [ ] `.docx` file downloads successfully
- [ ] Modal closes automatically on successful download
- [ ] Button shows a loading state while `/generate` is in progress
- [ ] On error, modal stays open and shows an error message

## Blocked by

- #13 — Change Summary Modal: Structure
