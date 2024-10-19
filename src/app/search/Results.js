import Card from "@/components/Card";

export default function Results(props) {
    const product = props.product;

    return (
        <div>
            Hello {product}
            <Card header={product} price={10} source="reddit"/>
        </div>
    );
}