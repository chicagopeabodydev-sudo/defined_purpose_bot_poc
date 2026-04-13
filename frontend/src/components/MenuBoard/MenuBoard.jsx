import menuData from '../../assets/menu.json'
import './MenuBoard.css'

const SECTION_ORDER = ['Main', 'Side', 'Drink']

function groupByType(items) {
  return items.reduce((acc, item) => {
    const key = item.itemType
    if (!acc[key]) acc[key] = []
    acc[key].push(item)
    return acc
  }, {})
}

function MenuBoard() {
  const groups = groupByType(menuData)

  return (
    <aside className="menu-board">
      <h2 className="menu-board-title">— Menu —</h2>

      {SECTION_ORDER.filter(t => groups[t]).map(type => (
        <section key={type} className="menu-section">
          <h3 className="menu-section-heading">{type}s</h3>

          {groups[type].map(item => (
            <div key={item.menuItem} className="menu-item">
              <div className="menu-item-row">
                <span className="menu-item-name">{item.menuItem}</span>
                <span className="menu-item-dots" aria-hidden="true" />
                <span className="menu-item-price">${item.price.toFixed(2)}</span>
              </div>
              <p className="menu-item-desc">{item.description}</p>
              <span className="menu-item-shiver">
                ❄ {item.minutesToShiver} min to shiver it off
              </span>
            </div>
          ))}
        </section>
      ))}

      <div className="menu-board-footer">
        * prices subject to change without apology
      </div>
    </aside>
  )
}

export default MenuBoard
