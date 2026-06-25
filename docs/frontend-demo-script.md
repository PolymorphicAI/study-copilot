# Frontend Demo Script

Use this script to review the Study Copilot frontend flows without needing prior product context. The app can be exercised in offline sandbox mode, or against the backend when it is available.

## Setup

1. Open `study-copilot-full.html` in a browser.
2. Optional backend path: from the repository root, run `python backend/main.py`, then refresh the page.
3. Confirm the status badge near the top of the page.

Expected results:

- If the backend is unavailable, the badge eventually shows an offline or sandbox state and the UI still serves local demo cards.
- If the backend is running without a live Gemini key, the UI can still use sandbox responses.
- No API key, wallet, or account is required for the manual checks below.

## Topic Generation

1. Select the `Generate Topic` tab on the start screen.
2. Enter a review topic, for example `Stellar wallets` or `photosynthesis basics`.
3. Keep `Intermediate` difficulty selected.
4. Set the number of cards to `5`.
5. Click `Start Learning`.

Expected results:

- A loading state appears while the app builds the lesson.
- A vertical lesson view opens with multiple cards.
- Cards include learning content and may include quiz cards.
- The left rail shows progress dots for the generated cards.
- The reset or home control returns to the start screen without a page reload.

## PDF Upload

1. Return to the start screen.
2. Select the `Upload PDF` tab.
3. Choose a valid `.pdf` file.
4. Confirm the selected file name appears in the upload area.
5. Click `Start Learning`.

Expected results:

- The app rejects an empty selection or a non-PDF file with a visible validation message.
- With a PDF selected, the app enters the lesson loading state.
- In backend mode, generated cards are based on the uploaded document.
- In offline sandbox mode, local fallback cards are displayed so reviewers can continue the demo.

## Notes Analyzer

1. Return to the start screen.
2. Select the `Paste Notes` tab.
3. Enter a title such as `Review notes`.
4. Paste several sentences of study notes into the notes field.
5. Click `Start Learning`.

Expected results:

- Empty notes are rejected with a visible validation message.
- Valid notes open the same lesson experience as the topic and PDF flows.
- The lesson contains readable study cards and, when available, quiz-style cards.
- The flow works in both backend mode and offline sandbox mode.

## Quiz Answer Flow

1. Navigate to a quiz card in the lesson.
2. Choose an answer by clicking one of the option buttons.
3. Repeat on another quiz card using keyboard shortcuts `1`, `2`, `3`, or `4`.

Expected results:

- The selected option is marked immediately.
- Correct answers are styled as correct and the app can advance after a short delay.
- Incorrect answers show the correct answer and an explanation instead of silently advancing.
- Keyboard shortcuts only answer the active quiz card and do not break navigation.

## Bookmarks

1. On any lesson card, click the bookmark control in the right-side controls.
2. Open the stats or progress drawer.
3. Review the bookmarks section.
4. Click the bookmark control again on the same card.

Expected results:

- The first click saves the current card and shows feedback.
- The saved card appears in the bookmarks list.
- The second click removes the bookmark and updates the saved state.
- In offline mode, bookmark behavior is stored locally for the current browser session.

## In-Lesson Uploads

1. From the lesson view, open the quick notes upload control.
2. Enter a short title and a few notes, then submit.
3. Return to the lesson and open the quick PDF upload control.
4. Select a valid `.pdf` file and submit.

Expected results:

- Both overlays can be opened and closed without losing the current session.
- Invalid or empty submissions show validation feedback.
- Valid submissions start a new lesson generation flow.
- Offline fallback still produces demo cards when the backend cannot generate live content.

## Navigation Checks

1. Use `ArrowDown` or `PageDown` to move to the next card.
2. Use `ArrowUp` or `PageUp` to move to the previous card.
3. Click progress dots on the left rail.

Expected results:

- The active card changes without layout overlap.
- Progress indicators update to match the active card.
- Navigation stays within the first and last card boundaries.