import samn from '../../assets/samn.png'
import './Employee.css'

function Employee({ isLoading }) {
  return (
    <div className={`employee-wrap ${isLoading ? 'employee--thinking' : ''}`}>
      <img
        src={samn}
        alt="SAMN, your order-taker"
        className="employee-img"
      />
    </div>
  )
}

export default Employee
