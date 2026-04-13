# frontend-design Examples

## Example 1: Initial App Shell

**Prompt:**
Build the Shiver Shack chat interface. Use the sample background image and the SAMN employee image. The layout should have the restaurant background filling the screen, SAMN standing behind the counter on the left, and a chat panel on the right.

**Expected Output:**
- A React component (`App.jsx`) that renders a full-viewport layout
- Background styled to resemble a painted-plank shack interior with a chalkboard menu visible at the top
- "Shiver Shack / a calorie-neutral cafe" sign prominently displayed
- Hand-lettered-style taped sign reading "Patio Open Dec. - Feb." on the wall
- SAMN image (`/docs/Samn_in_parka_1.png`) positioned left-center behind a counter element
- A cash register rendered on the counter (CSS/SVG or image)
- Chat panel on the right: greeting message from SAMN, a user input field at the bottom, scrollable message history above
- CSS variables used for all colors and fonts; no Inter/Roboto/Arial

---

## Example 2: Chat Message Exchange

**Prompt:**
Add a chat message to the interface where SAMN responds to a user's order entry. The bot response includes an alternate employee image.

**Expected Output:**
- User message bubble appears right-aligned with a distinct style
- SAMN response bubble appears left-aligned
- SAMN image updates to the alternate image supplied in the `chat_response` model
- Smooth scroll to the latest message
- Optional: subtle entrance animation on new message bubbles (CSS keyframes)

---

## Example 3: Order Summary Display

**Prompt:**
Display a completed order summary at the end of the chat. The summary should list each ordered item with quantity and price, plus a total.

**Expected Output:**
- A summary card rendered inside or below the chat panel
- Lists each `order_entry` item: name, quantity, unit price
- Displays total price and "minutes to shiver" from the `complete_order` model
- Styled consistently with the chalkboard/shack aesthetic (chalk-style font, dark background card)
- A closing message from SAMN using the `ending-comment` non-error response type
