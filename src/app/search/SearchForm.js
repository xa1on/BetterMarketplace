export default function SearchForm() {
    
    return (
        <form>
            <input type="text" name="product" className="border-2 rounded-md border-black p-2" />
            <button type="submit" className="border-2 border-black rounded-md p-2">Search</button>
        </form>
    );
}