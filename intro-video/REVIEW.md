# Review — 15 s intro

- Structure: stadium hook (0–3.4 s) → prediction screen with odds counting up (3.4–10.3 s) → end card (10.3–15 s).
- Placeholders (labelled on screen): prediction screen, logo, app name. Swap them for the real app's screen, logo and name.
- Edit the text, team names, percentages and colours as root variables in `index.html`.
- Checked: `hyperframes check` passes; frames reviewed at 0.3, 1.6, 3.1, 3.6, 5.6, 8.5, 9.7, 10.6–14.55 s.
- No music: a 15 s intro was built silent. Add music via `/media-use` if wanted.
- Weakest shot: the prediction card is a stand-in for the real app UI; it should be replaced with the real screen.
- GSAP is vendored in `assets/vendor/` because the render browser here could not reach the CDN.
