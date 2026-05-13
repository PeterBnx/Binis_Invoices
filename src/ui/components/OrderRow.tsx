import { FaChevronCircleRight } from "react-icons/fa";

interface Props {
  order_id: string;
  client: string;
  date: string;
  price: string;
  onClick: () => void;
}

function OrderRow({ order_id, client, date, price, onClick }: Props) {
  return (
    <tr 
      onClick={onClick}
      className="cursor-pointer transition-colors duration-150 border-b border-[var(--border-muted)] bg-[var(--bg)] hover:bg-[var(--bg-light)] group"
    >
      <td className="px-6 py-4 text-sm font-mono text-[var(--text-muted)]">
        {order_id}
      </td>
      <td className="px-6 py-4 text-sm font-medium text-[var(--text)]">
        {client}
      </td>
      <td className="px-6 py-4 text-sm text-[var(--text-muted)]">
        {date}
      </td>
      <td className="px-6 py-4 text-sm text-[var(--text-muted)]">
        {price}
      </td>
      <td className="px-6 py-4 text-right text-[var(--primary)] text-xl">
        {/* Added group-hover to make the icon pop when the row is hovered */}
        <FaChevronCircleRight className="inline-block transition-transform duration-200 group-hover:translate-x-1" />
      </td>
    </tr>
  );
}

export default OrderRow;