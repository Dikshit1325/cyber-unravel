import { useMemo, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Search } from "lucide-react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { entities, transactions, inr } from "@/lib/mock-data";
import { entityIcon } from "./primitives";

export function GlobalSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const groups = useMemo(() => {
    const byType = (type: string) => entities.filter((e) => e.type === type);
    return [
      { heading: "Entities", items: byType("Person") },
      { heading: "Accounts", items: byType("Bank Account") },
      { heading: "Phones", items: byType("Phone") },
      { heading: "Social Accounts", items: byType("Social Account") },
      { heading: "IP Addresses", items: byType("IP Address") },
      { heading: "Devices", items: byType("Device") },
    ];
  }, []);

  const go = (path: string) => {
    setOpen(false);
    void navigate({ to: path });
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="flex h-9 w-full max-w-md items-center gap-2 rounded-md border border-input bg-secondary/60 px-3 text-left text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
        aria-label="Open investigation search"
      >
        <Search className="size-4" aria-hidden />
        <span className="truncate">Search phone, account, IP, entity, transaction…</span>
        <kbd className="ml-auto hidden rounded border border-border bg-background px-1.5 py-0.5 font-mono text-[10px] md:inline">
          /
        </kbd>
      </button>

      <CommandDialog open={open} onOpenChange={setOpen}>
        <CommandInput
          value={query}
          onValueChange={setQuery}
          placeholder="Search phone, account, IP, entity, transaction..."
        />
        <CommandList>
          <CommandEmpty>
            <div className="px-2 py-6 text-center">
              <p className="text-sm font-medium text-foreground">No matching record found</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Try an identifier such as ENT-1092, AC-48291, PH-1001 or IP-1001, or import the relevant
                dataset from Data Sources.
              </p>
            </div>
          </CommandEmpty>
          {groups.map((group) => (
            <CommandGroup key={group.heading} heading={group.heading}>
              {group.items.map((e) => {
                const Icon = entityIcon[e.type];
                return (
                  <CommandItem
                    key={e.id}
                    value={`${e.id} ${e.label} ${e.type}`}
                    onSelect={() => go(`/entities/${e.id}`)}
                  >
                    <Icon className="size-4 text-primary" aria-hidden />
                    <span className="font-mono text-xs">{e.id}</span>
                    <span className="truncate text-xs text-muted-foreground">{e.label}</span>
                    <span className="ml-auto font-mono text-[10px] text-muted-foreground">
                      score {e.score}
                    </span>
                  </CommandItem>
                );
              })}
            </CommandGroup>
          ))}
          <CommandGroup heading="Transactions">
            {transactions.slice(0, 8).map((t) => (
              <CommandItem
                key={t.id}
                value={`${t.id} ${t.sender} ${t.receiver}`}
                onSelect={() => go("/transactions")}
              >
                <span className="font-mono text-xs">{t.id}</span>
                <span className="truncate text-xs text-muted-foreground">
                  {t.sender} → {t.receiver}
                </span>
                <span className="ml-auto font-mono text-[10px] text-financial">{inr(t.amount)}</span>
              </CommandItem>
            ))}
          </CommandGroup>
        </CommandList>
      </CommandDialog>
    </>
  );
}
