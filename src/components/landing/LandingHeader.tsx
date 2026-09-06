import { Link } from "@tanstack/react-router";
import { Menu, Search, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";

export function LandingHeader() {
  return (
    <header className="absolute inset-x-0 top-0 z-50 flex items-center gap-4 px-5 py-4 lg:px-8">
      <Link to="/" className="flex items-center gap-2.5 text-white">
        <span className="grid size-8 place-items-center rounded-sm border border-white/25 bg-white/5">
          <ShieldAlert className="size-4" aria-hidden />
        </span>
        <span className="text-sm font-semibold tracking-[0.2em] uppercase">Sentinel</span>
      </Link>

      <nav className="ml-auto flex items-center gap-2">
        <Button
          asChild
          variant="outline"
          size="sm"
          className="hidden border-white/30 bg-transparent text-white hover:bg-white/10 hover:text-white sm:inline-flex"
        >
          <Link to="/auth">Sign in</Link>
        </Button>
        <Button
          asChild
          size="sm"
          className="border border-white/20 bg-white text-black hover:bg-white/90"
        >
          <Link to="/auth">Get Started</Link>
        </Button>
        <button
          type="button"
          aria-label="Search"
          className="grid size-9 place-items-center text-white/70 transition-colors hover:text-white"
        >
          <Search className="size-4" />
        </button>
        <button
          type="button"
          aria-label="Menu"
          className="grid size-9 place-items-center text-white/70 transition-colors hover:text-white"
        >
          <Menu className="size-4" />
        </button>
      </nav>
    </header>
  );
}
