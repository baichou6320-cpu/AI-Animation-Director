# Style Reference

Use this file to translate a user's style request into practical animation direction. Avoid direct copying of protected franchises, living artists, or proprietary characters. Convert references into neutral traits: palette, light, texture, camera, motion, rhythm, emotion, and production constraints.

## Style Translation Pattern

For each style, define:

- Visual language: shape, texture, palette, detail level, lighting.
- Camera language: shot sizes, movement, lens feeling, framing.
- Animation language: motion timing, acting style, physics, transitions.
- Prompt anchors: reusable phrases for image/video prompts.
- Avoid: failure modes or overused terms.

## Warm Hand-Drawn Fantasy

- Visual language: soft hand-painted backgrounds, warm daylight, gentle haze, natural textures, expressive but simple character shapes.
- Camera language: slow push-ins, drifting pans, wide establishing shots, intimate medium shots.
- Animation language: small gestures, wind, fabric, clouds, water, emotional pauses.
- Prompt anchors: `warm hand-drawn animated short film look`, `painted background`, `soft natural light`, `gentle expressive character acting`, `storybook atmosphere`.
- Avoid: naming a specific studio as a replication target; overly glossy 3D surfaces.

## Famous Animation Reference Translation

When a user asks for a style similar to a living director, a specific studio, or a protected film world, do not put the name into copy-ready prompts as the main style instruction. Translate it into neutral visible traits, then continue.

Use this pattern:

- User reference: `[director/studio/work] 类似的温馨幻想动画`
- Safe style translation: `warm hand-painted fantasy animation, soft watercolor-like backgrounds, natural morning light, cozy everyday props, simple expressive faces, low-contrast shadows, slow slice-of-life camera rhythm`
- Explain briefly when useful: `风格已转译为温暖手绘幻想动画，不直接复刻具体作品、角色或专有画面。`

Do not over-police the user. A short translation note is enough; the useful part is the copy-ready prompt.

## Warm Isekai Morning

- Visual language: cozy hill cottage or small room, round windows, handmade wood and linen materials, cream walls, moss green plants, golden morning light, light fantasy objects that feel domestic rather than spectacular.
- Camera language: stable medium shots, slow push-ins, gentle window reveals, tabletop closeups, quiet establishing shots.
- Animation language: waking up, opening curtains, steam rising, fabric moving in a breeze, plants glowing softly, clouds drifting, small satisfied expressions.
- Prompt anchors: `warm hand-painted fantasy morning`, `cozy otherworld cottage`, `golden morning light`, `watercolor texture`, `gentle slice-of-life animation`, `soft natural shadows`.
- Avoid: overpowered magic effects, crowded fantasy creatures, modern city props, neon cyberpunk lighting, direct studio or director imitation.

## Aesthetic Scene Presets

Use these when the user has a mood but no concrete scene. Offer them as optional defaults or choose one when `direct_assumption_mode=true`.

- `forest_cottage`: green forest cottage, flowers, moss roof, clean summer sky, warm fairy-tale calm.
- `sunset_wheat_field`: golden wheat, long shadows, low wind, simple path, quiet emotional closure.
- `sky_island_morning`: small cottage above clouds, floating garden, bright sky, airy peaceful morning.
- `seaside_town_breakfast`: white walls, blue morning sea, linen curtains, breakfast table, gentle coastal wind.
- `cozy_kitchen_magic`: wooden kitchen, kettle steam, small glowing herbs, handmade ceramics, morning light through round window.

## Cyberpunk Neon

- Visual language: high contrast, wet streets, saturated neon, holographic signage, dense urban layers, reflective materials.
- Camera language: low angles, tracking shots, handheld urgency, long-lens compression for crowded streets.
- Animation language: rain, steam, flickering screens, crowds, fast vehicle/light movement.
- Prompt anchors: `neon cyberpunk city`, `rain-soaked reflective street`, `magenta cyan lighting`, `dense futuristic urban detail`, `cinematic contrast`.
- Avoid: too many moving objects in one video shot; unreadable signage; pure purple-blue monotony.

## Noir Animation

- Visual language: black-and-white or limited color, hard shadows, smoke, blinds, silhouettes, wet pavement.
- Camera language: low-key closeups, Dutch angles, slow dolly, motivated shadows.
- Animation language: restrained acting, cigarette smoke, rain, door light, shadow movement.
- Prompt anchors: `animated noir`, `high contrast chiaroscuro lighting`, `dramatic silhouettes`, `moody detective atmosphere`.
- Avoid: flat grayscale without contrast; modern comedy acting unless requested.

## Family-Friendly 3D Animation

- Visual language: appealing shapes, readable silhouettes, tactile materials, bright but balanced palette, expressive faces.
- Camera language: stable framing, playful pushes, clean eyelines, clear geography.
- Animation language: elastic timing, readable poses, warm comedic beats, emotionally legible acting.
- Prompt anchors: `polished family-friendly 3D animated film look`, `appealing character design`, `expressive face`, `soft studio-quality lighting`.
- Avoid: uncanny skin, over-detailed pores, adult thriller lighting.

## Chinese Ink-Wash Animation

- Visual language: ink diffusion, rice paper texture, negative space, restrained palette, brush strokes, misty mountains or water.
- Camera language: lateral scrolls, quiet wide shots, slow reveals, minimal cuts.
- Animation language: flowing cloth, drifting ink, water ripples, birds, mist, brush-like transitions.
- Prompt anchors: `Chinese ink-wash animation`, `rice paper texture`, `flowing black ink`, `minimal elegant composition`, `mist and negative space`.
- Avoid: over-saturated colors; heavy 3D realism; crowded compositions.

## Stop-Motion Handmade

- Visual language: miniature sets, tactile fabrics, clay, paper, visible craft texture, shallow depth of field.
- Camera language: locked-off frames, subtle dollies, macro details, table-top staging.
- Animation language: slightly stepped motion, hand-crafted imperfections, prop-based acting.
- Prompt anchors: `handmade stop-motion animation`, `miniature practical set`, `tactile clay and fabric texture`, `subtle frame-by-frame motion`.
- Avoid: perfectly smooth CGI unless the user wants hybrid style.

## Documentary Realism

- Visual language: natural light, grounded environments, imperfect details, observational framing.
- Camera language: handheld or shoulder-like movement, natural zooms, medium-long observational shots.
- Animation language: restrained, believable movement; environmental action over spectacle.
- Prompt anchors: `animated documentary realism`, `natural available light`, `observational camera`, `grounded everyday detail`.
- Avoid: excessive stylization, dramatic fantasy lighting, impossible camera paths.

## Ad / Product Film

- Visual language: clean product readability, controlled highlights, brand palette, polished surfaces.
- Camera language: hero closeups, macro details, smooth reveals, kinetic transitions.
- Animation language: product-first motion, clear benefit demonstration, rhythmic cuts.
- Prompt anchors: `premium animated product film`, `clean hero lighting`, `precise product detail`, `smooth cinematic reveal`.
- Avoid: story beats that hide the product; visual clutter around key brand moments.
