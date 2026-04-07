interface Props {
    order_id: string;
    client: string;
    date: string;
    status: string;
}

function OrderRow(props: Props) {
    return (
        <tr className="cursor-pointer hover:bg-[#3D3D3D]/10 transition-colors group">
            <td className="px-8 py-6">
                <span className="font-mono text-sm">
                    {props.order_id}
                </span>
            </td>
            <td className="px-8 py-6">
                <div className="text-sm font-semibold text-on-surface">
                    {props.client}
                </div>
            </td>
            <td className="px-8 py-6">
                <span className="text-sm">
                    {props.date}
                </span>
            </td>
            <td className="px-8 py-6">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-green-500/10 text-green-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                    {props.status}
                </span>
            </td>
            <td className="px-8 py-6 text-right w-10">
                <span className="material-symbols-outlined opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300">
                    chevron_right
                </span>
            </td>
        </tr>
    );
}

export default OrderRow;