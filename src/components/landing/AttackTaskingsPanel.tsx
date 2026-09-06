import { Crosshair, Radar, ShieldAlert, Zap } from "lucide-react";

const TASKINGS = [
  {
    id: "OP-RADIANT-FALCON",
    title: "OP RADIANT FALCON",
    priority: "P1",
    meta: "CDR/IPDR · FIN/SOC · TK/OC/NF",
    status: "engage",
    icon: Crosshair,
  },
  {
    id: "VESSEL-7742",
    title: "VESSEL",
    priority: "P1",
    meta: "SIM-BOX · 214 BURST · MUM/DXB",
    status: "track",
    icon: Radar,
  },
  {
    id: "SA-5-NODE",
    title: "SA-5",
    priority: "P2",
    meta: "LAYERED TRANSFER · 7 ACCTS",
    status: "engage",
    icon: Zap,
  },
  {
    id: "HQ-2-CLUSTER",
    title: "HQ-2",
    priority: "P2",
    meta: "SOCIAL CLUSTER · 12 IDENTITIES",
    status: "find",
    icon: ShieldAlert,
  },
  {
    id: "BRIDGE-C04",
    title: "BRIDGE C-04",
    priority: "P1",
    meta: "CROSS-DOMAIN · NAT POOL",
    status: "engage",
    icon: Crosshair,
  },
  {
    id: "MULE-SPIKE",
    title: "MULE SPIKE",
    priority: "P1",
    meta: "CASH-OUT · 6 MIN WINDOW",
    status: "track",
    icon: Radar,
  },
];

export function AttackTaskingsPanel() {
  return (
    <aside className="pointer-events-auto flex w-full max-w-xs flex-col border border-white/10 bg-black/55 backdrop-blur-md lg:max-w-sm">
      <div className="flex border-b border-white/10">
        {["Stage", "Target Status", "Battlespace"].map((tab, i) => (
          <button
            key={tab}
            type="button"
            className={`flex-1 px-2 py-2.5 font-mono text-[9px] tracking-widest uppercase transition-colors ${
              i === 0 ? "border-b border-white/80 text-white" : "text-white/40 hover:text-white/70"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="border-b border-white/10 px-3 py-2">
        <p className="font-mono text-[10px] tracking-widest text-white/50 uppercase">
          Recommend Taskings
        </p>
      </div>

      <ul className="max-h-[340px] flex-1 overflow-y-auto">
        {TASKINGS.map((t) => (
          <li
            key={t.id}
            className="group border-b border-white/6 px-3 py-3 transition-colors hover:bg-white/4"
          >
            <div className="flex items-start gap-2.5">
              <span className="mt-0.5 grid size-6 shrink-0 place-items-center rounded-sm border border-white/15 text-white/70">
                <t.icon className="size-3" aria-hidden />
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="truncate text-xs font-medium text-white">{t.title}</span>
                  <span
                    className={`shrink-0 rounded-sm border px-1 font-mono text-[9px] ${
                      t.priority === "P1"
                        ? "border-red-400/40 bg-red-400/10 text-red-300"
                        : "border-yellow-400/40 bg-yellow-400/10 text-yellow-300"
                    }`}
                  >
                    {t.priority}
                  </span>
                </div>
                <p className="mt-1 font-mono text-[9px] leading-relaxed text-white/45">{t.meta}</p>
                <div className="mt-2 flex gap-1.5">
                  <span className="rounded-sm border border-white/20 px-2 py-0.5 font-mono text-[9px] tracking-wide text-white/70 uppercase">
                    {t.status}
                  </span>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>

      <div className="border-t border-white/10 px-3 py-2 font-mono text-[9px] text-white/35">
        <span className="inline-flex items-center gap-1.5">
          <span className="size-1.5 animate-pulse rounded-full bg-red-400" />
          {TASKINGS.filter((t) => t.priority === "P1").length} active P1 threats
        </span>
      </div>
    </aside>
  );
}
