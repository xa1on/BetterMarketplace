import Image from "next/image";
import redditLogo from "../ui/images/reddit_logo.png";
import ebayLogo from "../ui/images/ebay_logo.png";
import craigslistLogo from "../ui/images/craigslist_logo.png";
import marketplaceLogo from "../ui/images/marketplace_logo.svg";


export default function Card(props) {

    function getImage(source) {
        switch (source) {
            case "reddit": 
                return redditLogo;
            case "ebay": 
                return ebayLogo;
            case "craigslist": 
                return craigslistLogo;
            case "marketplace":
                return marketplaceLogo;
        }
    }

    return (
    
    <a href={props.link}>
    
        <div className="flex flex-row font-sans bg-green-200 w-260 shadow-lg rounded-lg p-5 m-4">
            
            <Image src={getImage(props.source)} alt="" className="" width={200}/>
            
            <div>
                <div className="flex-none relative p-5">
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
            
            
            
        </div>
    </a>

    );
}
