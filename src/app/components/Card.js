import Image from "next/image";
import redditLogo from "../ui/images/reddit_logo.png";

export default function Card(props) {
    return (
    <div className="flex font-sans bg-violet-100 w-80 shadow-lg rounded-lg">
        <div className="flex-none w-20 relative p-1">
            <Image src={redditLogo} alt="" className="inset-0 object-cover" width={40}/>
            <div className="\text-sm font-medium text-slate-700 mt-2">
                {props.source}
            </div>
        </div>

        <div className="flex flex-wrap">
            <h1 className="flex-auto text-2xl font-semibold text-slate-900">
                {props.header}
            </h1>
            <div className="flex-none w-full text-lg font-semibold text-slate-500">
                ${props.price}
            </div>
        </div>
    </div>

    );
}
