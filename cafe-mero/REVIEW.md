# Cafe Mero reel — review

- 24.5 s, 1080x1920, 30 fps, H.264 + AAC, -14 LUFS.
- Story: latte pour hook (slow) → grind → dose → tamp (ramps to slow) → lock-in → espresso extraction (ramp to 0.4x) → milk → steam purge dissolving into frothing → swirl → latte art (ramp to 0.5x) → heart hero with push-in → logo on matching white + "Good Coffee. Great Company."
- Slow motion: sources are all 30 fps, so slow sections use motion-compensated interpolation to 120 fps, sampled along smooth speed curves (tools/shot.py). Frames inspected for ghosting on the milk stream, espresso streams and hands: none found in the samples checked.
- Grade: Product Polish base with slight warmth (temperature 0.04), applied per shot via media-treatment.
- Music: original track composed in tools/music.py (owned outright). Natural sound from each clip at real speed; whoosh on the lock-in, chime on the logo (bundled SFX). Mix in tools/mix.py. The sound was measured, not heard.
- Logo: the supplied file, unaltered, on #FEFEFE (its own background), opacity + short rise only.
- Limits: source is 478x850 (WhatsApp-compressed), upscaled 2.26x, so detail is soft. No beans-falling or finished-cup-steam footage exists, so those moments are not in the edit.
