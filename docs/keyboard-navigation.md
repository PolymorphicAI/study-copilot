# Keyboard Navigation

Study Copilot supports keyboard shortcuts in the lesson view so reviewers and learners can move through generated cards and answer quiz cards without relying only on pointer input.

The shortcuts are implemented in `study-copilot-full.html` through the global `keydown` listener set up by `setupKeyboardListeners()`.

## When Shortcuts Are Active

Keyboard shortcuts are active when:

- A lesson has generated at least one card.
- The user is not typing in an `input` or `textarea`.
- Focus is on the page, a card, or a non-text control.

The listener intentionally ignores key presses inside form fields so learners can type topics, notes, titles, and card counts without triggering navigation.

## Available Shortcuts

| Key | Behavior |
| --- | --- |
| `ArrowDown` | Move to the next study card. |
| `PageDown` | Move to the next study card. |
| `ArrowUp` | Move to the previous study card. |
| `PageUp` | Move to the previous study card. |
| `1` | Select the first quiz option on the active quiz card. |
| `2` | Select the second quiz option on the active quiz card. |
| `3` | Select the third quiz option on the active quiz card. |
| `4` | Select the fourth quiz option on the active quiz card. |

Navigation keys stop at the first and last card. Number keys only answer a quiz when the active card is a quiz card and the matching option button is enabled.

## Expected Navigation Behavior

When a learner presses `ArrowDown` or `PageDown`:

1. The browser's default page movement is prevented.
2. The app checks that the current card is not the final card.
3. The next card is scrolled into view.
4. The active card index updates through the existing card observer behavior.

When a learner presses `ArrowUp` or `PageUp`:

1. The browser's default page movement is prevented.
2. The app checks that the current card is not the first card.
3. The previous card is scrolled into view.
4. The active card index updates through the existing card observer behavior.

## Expected Quiz Behavior

When the active card is a quiz card:

1. Pressing `1`, `2`, `3`, or `4` maps to the matching answer button.
2. The app clicks the matching option button if it exists and is not disabled.
3. Quiz buttons are disabled after an answer to prevent duplicate submissions.
4. The app shows correct or incorrect feedback and an explanation.
5. Correct answers automatically advance to the next card after a short delay.

When the active card is not a quiz card, number keys do not answer anything.

## Offline and Backend Modes

Keyboard behavior works in both review modes:

- Frontend sandbox mode uses locally generated quiz answers and explanations.
- Backend mode posts quiz answers to `/api/check-answer`.
- If backend validation fails after the lesson has loaded, the app falls back to cached quiz answer data when available.

## Contributor Notes

When changing keyboard behavior, verify these flows:

- Typing in the topic input does not move cards.
- Typing in the notes textarea does not move cards.
- Arrow keys move through cards after a lesson is generated.
- Navigation stops at the first and last card.
- Number keys answer only the active quiz card.
- Disabled quiz option buttons cannot be triggered again by number keys.
- Correct quiz answers still auto-advance after feedback is shown.

## Future Discoverability Improvements

The shortcuts currently exist in behavior but are not surfaced prominently in the UI. Future improvements could include:

- A compact keyboard shortcuts help item in the stats or settings drawer.
- Small shortcut hints on quiz option buttons, such as `1`, `2`, `3`, and `4`.
- A first-run tooltip after a lesson is generated.
- Visible focus styles for cards and quiz options.
- An accessibility review for how shortcut hints are announced by screen readers.

