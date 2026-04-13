---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: chat interface that walks users through a fast-food meal order (for example, cheese burger, fries, and a shake).
- **Tone**: fast-food restaurant that is NOT a chain restaurant, but a local version of one. The background should look like painted planks of a shack and the menu is in chalk. There is a sign that reads "Patio Open Dec. - Feb." that appears hand written and is taped to the wall.
- **Differentiation**: There is an employee named SAMN that represents the "bot" in the chat interface.

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working React code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Backgrounds & Visual Details**: Making the background look like you are facing the counter of a locally-owned fast-food restaurant is key. There needs to be a cash register on the counter and an employee standing behind it. Add contextual effects and textures that match the overall aesthetic.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. This is a simple interface with just a background, bot, and chat interface, however it should have small details that would be typical of the restaurant setting.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

## Main Components
1. Background that has the appearance of a locally-owned fast-food restaurant
  - Needs a sign with "Shiver Shack" as the name of the restaurant and below this "a calorie-neutral cafe"
  - Chalkboard Menu
  - Taped-up hand-written sign that reads "Patio Open Dec. - Feb."
2. Chat interface (bot displays a greeting, then the user can provide input, then the bot response, and so on)
3. Employee behind the cash register - this is the supplied image of SAMN
  - if animation is going to be added, this is where to do it

### Use React as the framework

## UI Design Resources
[Sample Background image](/docs/shiver_shack_background.png)
[Employee SAMN that represent the bot](/docs/Samn_in_parka_1.png)
[React Quick Start documentation](https://react.dev/learn)
[React adding interactivity](https://react.dev/learn/adding-interactivity)
[Skill examples](../frontend-design/examples.md)