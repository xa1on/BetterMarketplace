import Card from "@/components/Card";

export default function Results(props) {
    const product = props.product;

    return (
        <div>
            <Card header={product} price={10} source="craigslist" location="San Jose" link="http://google.com"/>
        </div>
    );
}