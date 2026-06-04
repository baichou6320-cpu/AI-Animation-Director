# Production Checklist

Use this file to review an AI animation package before delivery or to diagnose a failed generation.

## Required Deliverables

- Project brief with duration, audience, format, style, and constraints.
- Director treatment with emotion, visual language, camera, color, light, and pacing.
- Script with beginning, turn, ending, action, and optional narration/dialogue.
- Character bible for recurring characters.
- Scene bible for recurring locations.
- Shot list with purpose, duration, image, camera, action, sound, difficulty, and fix notes.
- Image prompts with positive, negative, style, character, scene, and composition anchors.
- Video prompts with subject motion, camera motion, timing, physics, avoid list, and fallback.
- Music/sound direction at low priority.
- Risk list and iteration plan.

## Common Problems and Fixes

| Problem | Symptom | Fix |
| --- | --- | --- |
| Vague concept | Story feels generic or prompt becomes decorative | Add theme, character desire, obstacle, and ending |
| Style drift | Every shot looks like a different film | Create a style anchor and repeat it in every prompt |
| Character drift | Face, age, clothes, or silhouette changes | Add character bible and exact recurring character anchor |
| Scene drift | Location layout changes shot to shot | Add scene bible with spatial layout and fixed props |
| Overloaded shot | Video fails, warps, or ignores action | Split shot or keep only one subject action and one camera move |
| Too many shots | Output is hard to execute | Group by sequence and generate prompts batch by batch |
| Too few shots | Story jumps or lacks emotion | Add reaction shots, inserts, and establishing shots |
| Weak ending | Viewer does not understand the payoff | Add visual callback, object payoff, or emotional close-up |
| Music dominates | Sound direction distracts from production | Reduce to mood, tempo, instruments, ambience, and key effects |

## Feasibility Review

Check each shot:

- Is the shot purpose clear?
- Is there only one primary action?
- Is the camera movement simple enough?
- Are character and scene anchors repeated?
- Is the shot duration realistic for the amount of action?
- Does the prompt avoid precise handoffs, fast transformations, and complex crowd choreography unless necessary?
- Is there a fallback if the video model fails?

## Final QA Questions

- Does the story close emotionally and visually?
- Can the short be understood without extra explanation?
- Are the director treatment, script, shot table, image prompts, and video prompts aligned?
- Are platform-specific assumptions clearly marked?
- Are references translated into generic visual traits instead of direct imitation?
- Are music and sound present but not overdeveloped?
- Is the next production step obvious to the user?
