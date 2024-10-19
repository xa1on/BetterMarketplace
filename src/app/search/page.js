import SearchForm from "./SearchForm.js";
import Results from "./Results.js";

export default function SearchPage(searchParams) {

    const product = searchParams.searchParams.product || "";

    return (
        <div>
            <p>Search for a product!</p>
            <SearchForm />
            <Results product={product}/>
        </div>
    );
}