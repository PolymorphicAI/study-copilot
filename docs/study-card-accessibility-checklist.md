# Study Card Accessibility Checklist

Use this checklist when changing the Study Copilot micro-learning card interface in `study-copilot-full.html`. It focuses on the generated lesson cards, quiz options, progress dots, bookmark controls, copy buttons, and motion behavior reviewers interact with during a study session.

## Keyboard Navigation

- [ ] `ArrowDown` and `PageDown` move to the next card after a lesson is generated.
- [ ] `ArrowUp` and `PageUp` move to the previous card.
- [ ] Navigation stops at the first and last card.
- [ ] Number keys `1`, `2`, `3`, and `4` answer only the active quiz card.
- [ ] Keyboard shortcuts do not trigger while a user is typing in an `input` or `textarea`.
- [ ] Quiz option buttons cannot be activated again after they are disabled.
- [ ] Bookmark, stats, upload, notes, and home controls remain reachable with the keyboard.

## Focus Behavior

- [ ] Focus states are visible on buttons, tabs, quiz options, copy buttons, and drawer controls.
- [ ] Opening a drawer or upload overlay gives users a clear next focus target.
- [ ] Closing a drawer or upload overlay returns users to a predictable place in the lesson.
- [ ] Correct quiz answers can auto-advance without trapping focus.
- [ ] Incorrect quiz answers keep the explanation visible and do not move focus unexpectedly.
- [ ] Progress-dot navigation does not cause keyboard users to lose track of the active card.

## Contrast and Visual States

- [ ] Card text meets readable contrast against the card background.
- [ ] Muted metadata, timestamps, and helper text remain readable.
- [ ] Quiz correct and incorrect states are not communicated by color alone.
- [ ] Disabled quiz options remain legible.
- [ ] Bookmark active and inactive states are visually distinct.
- [ ] Toast messages and status text are readable in both online and offline modes.

## Labels and Semantics

- [ ] Quiz option buttons have clear answer text.
- [ ] Icon-only controls have accessible names or meaningful `title` text.
- [ ] Copy buttons identify the action they perform.
- [ ] API status text communicates `Connecting`, `Gemini Online`, `Sandbox Mode`, or `Backend Offline` clearly.
- [ ] Progress dots expose enough context for the target card when converted to accessible controls.
- [ ] Generated code examples keep code text selectable and copyable.

## Motion and Auto-Advance

- [ ] Smooth scrolling does not hide the active card or important feedback.
- [ ] Card entrance animations do not block reading or keyboard input.
- [ ] The correct-answer countdown bar is paired with visible quiz feedback.
- [ ] Auto-advance only happens after a correct quiz answer.
- [ ] Users can still review incorrect-answer explanations without an automatic scroll.
- [ ] Future animation changes should consider a reduced-motion path.

## Screen-Reader Review Notes

When the card UI gains more semantic markup, contributors should verify:

- The active card can be announced with its title and type.
- Quiz answer feedback is announced after selection.
- Drawer headings and overlay headings are announced when opened.
- Bookmark changes are exposed as status updates.
- Generated card content is read in a logical order: badge, title, body, type-specific controls, then metadata.

## Pre-PR Checklist

Before opening a pull request that changes study cards or lesson controls:

- [ ] I tested card navigation with the keyboard.
- [ ] I tested at least one quiz card with number-key shortcuts.
- [ ] I checked focus visibility on all changed controls.
- [ ] I checked that color is not the only state indicator.
- [ ] I reviewed labels for icon-only or compact controls.
- [ ] I checked motion or auto-scroll changes for readability.
- [ ] I tested the changed flow in backend mode or offline sandbox mode, depending on the touched behavior.
- [ ] I included screenshots, notes, or reproduction steps for reviewers when the change affects visible UI.

