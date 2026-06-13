# Advisor Avatars

Advisor portraits are optional local assets.

Use paths like this in `data/advisors.json`:

```json
"avatar": "assets/avatars/marcus_aurelius.webp",
"avatar_alt": "MA"
```

Recommended convention:

- Store images in `assets/avatars/`.
- Name files with the advisor id, for example `marcus_aurelius.webp`.
- Prefer square WebP files around 512 x 512 pixels.
- Do not use external image URLs.

If an avatar path is missing or the file does not exist, the app renders a polished fallback avatar using initials, category color, and archetype styling.

