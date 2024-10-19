import Image from "next/image";
import redditLogo from "../ui/images/reddit_logo.png";
import ebayLogo from "../ui/images/ebay_logo.png";
import craigslistLogo from "../ui/images/craigslist_logo.png";


export default function Card(props) {

    function getImage(source) {
        switch (source) {
            case "reddit": 
                return redditLogo
            case "ebay": 
                return ebayLogo
            case "craigslist": 
                return craigslistLogo
        }
    }

    return (
    
    <a href={props.link}>
    
        <div className="flex font-sans bg-violet-100 w-80 shadow-lg rounded-lg">
            
            <div>
                <div className="flex-none w-20 relative p-1">
                    <Image src={getImage(props.source)} alt="" className="inset-0 object-cover" width={40}/>
                    <h1 className="flex-auto text-2xl font-semibold text-slate-900">
                        {props.header}
                    </h1>
                    <div className="flex-none w-full text-lg font-semibold text-slate-500">
                        ${props.price}
                    </div>
                    <div className="text-base font-semibold text-slate-500">
                        {props.location}
                    </div>
                </div>
                
            </div>
            
            <Image src={getImage(props.source)} alt="" className="inset-0 object-cover" width={200}/>
            
        </div>
    </a>

    );
}
