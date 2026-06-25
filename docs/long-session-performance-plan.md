# Long Study Session Performance Plan

This plan identifies performance risks and review metrics for Study Copilot sessions with many generated cards. It focuses on the current single-file frontend in `study-copilot-full.html`.

## Current Rendering Model

The lesson view currently:

- Builds all generated cards before rendering the study session.
- Appends one `.card-slide` element per card.
- Creates progress dots for every card.
- Uses an `IntersectionObserver` for every rendered slide.
- Keeps the full `studyCardsList` array in memory.
- Stores sessions, progress, and bookmarks in backend memory when the backend is online.

This works well for short sessions, but long sessions can increase DOM size, memory usage, scroll work, and mobile rendering cost.

## Performance Risks

### Large DOM Trees

Each card can include body text, code blocks, quiz options, explanation panels, and metadata. Rendering many cards at once can increase:

- Initial render time.
- Style and layout work.
- Memory usage.
- Cost of DOM queries such as `document.querySelectorAll('.card-slide')`.

### Scroll Smoothness

The app uses vertical scroll snap and smooth scrolling. Long sessions may expose:

- Stutter when swiping quickly through many cards.
- Delayed snap behavior on mobile browsers.
- Extra layout work when cards contain large code examples or explanations.
- More expensive active-card tracking with many observed slides.

### Mobile Memory Pressure

Mobile browsers may struggle when many cards include:

- Long pasted notes output.
- Code snippets.
- Quiz explanation overlays.
- Scrollable card bodies inside a scroll-snapping viewport.

Symptoms can include tab reloads, delayed taps, blank frames, or dropped frames.

### Repeated View Logging

`IntersectionObserver` can call `logCardViewed()` whenever a card becomes active. In long sessions, fast scrolling may produce many view calls when the backend is online.

### Quiz Auto-Advance

Correct quiz answers trigger delayed auto-scroll. In longer sessions, this should remain smooth and should not skip cards, queue multiple scrolls, or conflict with manual scrolling.

## Metrics to Watch

Use browser devtools and manual observation to track:

| Metric | Why it matters |
| --- | --- |
| Initial lesson render time | Shows how expensive full-session rendering is. |
| DOM node count | Indicates how much work the browser must track. |
| JS heap size | Helps identify memory growth across long sessions. |
| Scroll frame rate | Measures whether swiping remains smooth. |
| Long tasks over 50ms | Highlights blocking JavaScript or layout work. |
| Time to first interactive card | Measures how quickly learners can start. |
| View logging request count | Detects noisy backend calls while scrolling. |
| Mobile tab stability | Catches memory pressure and reload behavior. |

Suggested test sizes:

- 5 cards: baseline current default.
- 10 cards: current frontend maximum for topic generation.
- 25 cards: stress case for future backend or imported decks.
- 50 cards: virtualization research case.

## Manual Review Steps

1. Generate a 5-card session and capture baseline behavior.
2. Generate or mock a 10-card session and compare render time and scroll smoothness.
3. Temporarily seed a larger local `studyCardsList` in development to test 25-card and 50-card sessions.
4. Test on a small mobile viewport.
5. Test a session with several code and quiz cards.
6. Scroll from first card to last card quickly, then slowly.
7. Open and close the stats drawer during a long session.
8. Bookmark cards near the beginning, middle, and end of the deck.
9. Answer quiz cards and verify auto-scroll remains stable.

## Lazy Rendering and Virtualization Research

Future optimization work should explore rendering only the active card and a small buffer around it.

Possible approaches:

- Keep all card data in `studyCardsList`, but render only current, previous, and next cards.
- Virtualize `.card-slide` elements while preserving scroll position.
- Defer rendering quiz explanation overlays until the quiz card is active.
- Defer code block rendering for offscreen cards.
- Batch progress dot updates for very large decks.
- Avoid repeated `querySelectorAll('.card-slide')` calls in hot paths.

Questions to answer before implementation:

- Can scroll snap still feel natural if offscreen slides are virtualized?
- How should progress dots work when not every slide exists in the DOM?
- Should long sessions use grouped sections instead of one slide per card?
- How should view logging avoid duplicate calls during fast scroll?
- What is the maximum intended deck size for production?

## Future Optimization Issues

Potential follow-up issues:

- Add a long-session mock generator for frontend performance testing.
- Add a render timing measurement around `renderStudySession()`.
- Track viewed card ids locally to avoid duplicate `/api/view/{card_id}` calls.
- Add reduced-motion handling for card entrance and auto-scroll behavior.
- Research card virtualization for decks larger than 10 cards.
- Add a performance checklist to frontend PR reviews.
- Add mobile browser performance notes for Safari and Chrome.

## Pre-PR Performance Checklist

Before merging changes that affect card rendering, scrolling, quiz feedback, or session state:

- [ ] Test a 5-card baseline session.
- [ ] Test the largest session size supported by the changed flow.
- [ ] Check that scrolling remains smooth on a mobile viewport.
- [ ] Check that progress dots update without visible lag.
- [ ] Check that quiz auto-scroll does not queue duplicate scrolls.
- [ ] Check that opening drawers or overlays does not noticeably slow the session.
- [ ] Note any expected performance tradeoffs in the pull request.

