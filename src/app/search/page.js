import SearchForm from "./SearchForm.js";
import Results from "./Results.js";
import { revalidatePath } from "next/cache.js";

export default function SearchPage(searchParams) {

    const product = searchParams.searchParams.product || "";

    setInterval(function() {
        revalidatePath("/search");
    }, 1 * 1000); // 60 * 1000 milsec

    return (
        <div className="flex flex-col min-h-screen justify-center items-center">
            <p>Search for a product!</p>
            <SearchForm />
            <Results product={product}/>
        </div>
    );
}