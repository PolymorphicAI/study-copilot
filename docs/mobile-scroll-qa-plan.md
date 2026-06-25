# Mobile Scroll QA Plan

This QA plan covers the vertical, TikTok-style study card experience in `study-copilot-full.html`. It focuses on mobile scrolling, scroll snap behavior, touch gestures, keyboard fallback behavior, and known risks in the lesson viewport.

## Scope

Test the lesson view after cards are generated from:

- Topic generation
- PDF upload
- Pasted notes
- Offline sandbox fallback
- Backend fallback mode

The primary elements under test are:

- `#cards-viewport`
- `.card-slide`
- `.learning-card`
- Left progress dots
- Right-side controls
- Quiz option buttons
- Correct-answer auto-scroll behavior

## Device and Screen Size Matrix

Use real devices when possible. Browser responsive mode is acceptable for a first pass.

| Device class | Example width | What to check |
| --- | --- | --- |
| Small phone | 320px to 360px | Card padding, title wrapping, control overlap. |
| Common phone | 375px to 430px | One-card-per-screen scroll rhythm. |
| Large phone | 480px to 540px | Right controls and left dots remain reachable. |
| Small tablet | 768px | Mobile breakpoint behavior at the current CSS cutoff. |
| Desktop narrow | 900px to 1024px | Transition from mobile spacing to desktop spacing. |

Also test both portrait and landscape orientation for at least one phone-sized viewport.

## Baseline Setup

1. Open `study-copilot-full.html`.
2. Generate at least 5 cards.
3. Confirm the lesson view opens and `#cards-viewport` starts at the first card.
4. Confirm the first progress dot is active.
5. Confirm right-side controls are visible and do not cover card text.

Repeat the plan with backend online and backend offline when possible.

## Scroll Snap Behavior

Expected behavior:

- Each `.card-slide` occupies a full viewport-height slot.
- Vertical scrolling snaps to one card at a time.
- The active card updates when at least most of the next card is visible.
- Scroll position resets to the first card when a new lesson is generated.

Checks:

- Swipe slowly from card 1 to card 2.
- Swipe quickly through multiple cards.
- Stop between cards and verify snap lands on one card.
- Scroll to the final card and verify it does not overscroll into blank space.
- Generate a new lesson and verify the viewport returns to card 1.

## Touch Behavior

Expected behavior:

- Vertical swipes move through the card stack.
- Tapping quiz options does not accidentally scroll.
- Tapping right-side controls does not trigger an unintended card change.
- Inner card overflow remains usable when card content is taller than the card.

Checks:

- Swipe on the card body.
- Swipe near the left progress dots.
- Swipe near the right action controls.
- Tap the bookmark control on several cards.
- Open the stats drawer and close it without changing the active card unexpectedly.
- On a long card, scroll inside `.learning-card` and verify the page does not feel trapped.

## Keyboard Behavior on Mobile and Desktop

Expected behavior:

- `ArrowDown` and `PageDown` move to the next card.
- `ArrowUp` and `PageUp` move to the previous card.
- Number keys `1` to `4` answer only the active quiz card.
- Keyboard shortcuts do not trigger while typing in inputs or textareas.

Checks:

- Use keyboard navigation in desktop responsive mode.
- Connect a hardware keyboard to a mobile device or tablet if available.
- Verify navigation stops at the first and final card.
- Verify quiz shortcuts still work after touch scrolling.

## Progress Dots and Active Card Tracking

The app uses an `IntersectionObserver` rooted at `#cards-viewport` with a `0.55` threshold to update `currentCardIndex` and progress dots.

Checks:

- Active dot updates when swiping to each card.
- Active dot updates when using keyboard navigation.
- Active dot updates after correct-answer auto-scroll.
- Clicking a progress dot scrolls to the expected card.
- Bookmark button active state follows the currently visible card.

## Quiz Auto-Scroll

Expected behavior:

- Correct quiz answers show feedback.
- The countdown bar appears after a correct answer.
- The app scrolls to the next card after the short delay.
- Incorrect answers show the explanation and do not auto-scroll.

Checks:

- Answer a quiz correctly with touch.
- Answer a quiz correctly with number keys.
- Answer a quiz incorrectly and verify the card remains visible.
- Verify auto-scroll does not skip more than one card.

## Known Risks

- `100vh` can behave differently on mobile browsers with dynamic address bars.
- Right-side controls can crowd small screens.
- Left progress dots can be hard to tap on narrow devices.
- Smooth scrolling plus scroll snap can feel inconsistent across browsers.
- Cards with long content may require inner scrolling and can compete with page scrolling.
- Auto-scroll after quiz feedback may surprise users if they want more time to read.
- The `0.55` observer threshold may mark the next card active before the user expects it.
- Reduced-motion preferences are not currently documented in the UI behavior.

## Regression Checklist

Before merging changes that affect scrolling, cards, quiz feedback, or layout:

- [ ] Tested at 320px width.
- [ ] Tested at 375px to 430px width.
- [ ] Tested at 768px width.
- [ ] Tested portrait and landscape where practical.
- [ ] Verified scroll snap from first card to final card.
- [ ] Verified progress dots update while swiping.
- [ ] Verified keyboard navigation still works.
- [ ] Verified quiz auto-scroll works only after correct answers.
- [ ] Verified right controls do not cover card content.
- [ ] Verified long card content remains readable.
- [ ] Captured screenshots or notes for any visual layout change.

