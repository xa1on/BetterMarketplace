import Card from "@/components/Card";

export default function Results(props) {
    const product = props.product;

    const db = [
        {
            header: "2017 Subaru BRZ",
            price: 12500,
            source: "marketplace",
            location: "Hayward, CA",
            link: "http://google.com",
            id: 0,
        },
        {
            header: "2018 Subaru BRZ",
            price: 1500,
            source: "reddit",
            location: "San Jose, CA",
            link: "http://instagram.com",
            id: 0,
        }
    ]


    return (
        <div className="gap-4">
            {db.map(
                (item) => 
                    <Card key={item.id} header={item.header} price={item.price} source={item.source} location={item.location} link={item.link}/>

            )}
            <Card header={product} price={10} source="craigslist" location="San Jose" link="http://google.com"/>
        </div>
    );
}