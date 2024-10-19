import "@/ui/navbar.css"
import Link from "next/link";


export default function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-left ">
                <Link href="..">Home</Link>
            </div>

            <div className="navbar-center">
                <Link href="../search" className="item">Search</Link>
                {/* <Link href="../get_link">Get Link</Link> */}
            </div>

            <div className="navbar-right">
                {/* profile / sign in */}
            </div>
        </nav>
    );
};