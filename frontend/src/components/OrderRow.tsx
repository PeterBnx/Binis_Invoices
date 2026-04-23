interface Props {
    order_id: string;
    client: string;
    date: string;
    price: string;
    onClick: () => void;
}

function OrderRow(props: Props) {
    return (
        <tr 
            onClick={props.onClick}
            className="cursor-pointer transition-colors group relative"
        >

            <td className="px-8 py-6 w-1/5 border-y border-transparent group-hover:border-white group-hover:bg-white/5 transition-all">
                <span className="font-mono text-sm">{props.order_id}</span>
            </td>
            <td className="px-8 py-6 w-1/4 border-y border-transparent group-hover:border-white group-hover:bg-white/5 transition-all">
                <div className="text-sm font-semibold">{props.client}</div>
            </td>
            <td className="px-8 py-6 w-1/4 border-y border-transparent group-hover:border-white group-hover:bg-white/5 transition-all">
                <span className="text-sm">{props.date}</span>
            </td>
            <td className="px-8 py-6 w-1/4 border-y border-transparent group-hover:border-white group-hover:bg-white/5 transition-all">
                <span className="text-sm">{props.price}</span>
            </td>
            {/* Last cell handles the right border corner */}
            <td className="px-8 py-6 text-right w-10 border-y border-transparent group-hover:border-white group-hover:bg-white/5 transition-all">
                <span className="material-symbols-outlined opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
                    chevron_right
                </span>
            </td>
        </tr>
    );
}
export default OrderRow;