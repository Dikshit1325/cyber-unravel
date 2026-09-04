import { useEffect, useRef } from "react";

type Node = { lat: number; lon: number; label: string };

const NODES: Node[] = [
  { lat: 28.61, lon: 77.21, label: "New Delhi" },
  { lat: 19.08, lon: 72.88, label: "Mumbai" },
  { lat: 12.97, lon: 77.59, label: "Bengaluru" },
  { lat: 22.57, lon: 88.36, label: "Kolkata" },
  { lat: 25.27, lon: 55.3, label: "Dubai" },
  { lat: 1.35, lon: 103.82, label: "Singapore" },
  { lat: 51.5, lon: -0.12, label: "London" },
  { lat: 40.71, lon: -74.0, label: "New York" },
  { lat: 55.75, lon: 37.61, label: "Moscow" },
  { lat: 39.9, lon: 116.4, label: "Beijing" },
  { lat: -33.86, lon: 151.2, label: "Sydney" },
  { lat: -23.55, lon: -46.63, label: "Sao Paulo" },
  { lat: 35.68, lon: 139.69, label: "Tokyo" },
  { lat: 6.52, lon: 3.37, label: "Lagos" },
  { lat: 50.11, lon: 8.68, label: "Frankfurt" },
  { lat: 33.68, lon: 73.05, label: "Islamabad" },
];

const ARCS: [number, number][] = [
  [0, 4],
  [1, 5],
  [2, 6],
  [3, 9],
  [0, 15],
  [1, 7],
  [4, 14],
  [5, 12],
  [8, 0],
  [11, 1],
  [10, 2],
  [13, 3],
];

/** Rotating wireframe earth with live cross-border "attack" arcs, drawn on canvas. */
export function CyberGlobe({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let raf = 0;
    let rotation = 0;
    let width = 0;
    let height = 0;
    let radius = 0;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = rect.width;
      height = rect.height;
      canvas.width = Math.max(1, Math.floor(width * dpr));
      canvas.height = Math.max(1, Math.floor(height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      radius = Math.min(width, height) * 0.36;
    };
    resize();
    window.addEventListener("resize", resize);

    const project = (lat: number, lon: number) => {
      const phi = (90 - lat) * (Math.PI / 180);
      const theta = (lon + rotation) * (Math.PI / 180);
      const x = Math.sin(phi) * Math.sin(theta);
      const y = Math.cos(phi);
      const z = Math.sin(phi) * Math.cos(theta);
      return {
        x: width / 2 + x * radius,
        y: height / 2 - y * radius * 0.98,
        z,
      };
    };

    const draw = (t: number) => {
      ctx.clearRect(0, 0, width, height);
      const cx = width / 2;
      const cy = height / 2;

      // atmosphere
      const glow = ctx.createRadialGradient(cx, cy, radius * 0.6, cx, cy, radius * 1.55);
      glow.addColorStop(0, "rgba(56,189,248,0.16)");
      glow.addColorStop(0.55, "rgba(56,189,248,0.05)");
      glow.addColorStop(1, "rgba(56,189,248,0)");
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 1.55, 0, Math.PI * 2);
      ctx.fill();

      // globe body
      const body = ctx.createRadialGradient(
        cx - radius * 0.35,
        cy - radius * 0.4,
        radius * 0.1,
        cx,
        cy,
        radius,
      );
      body.addColorStop(0, "rgba(28,52,74,0.95)");
      body.addColorStop(1, "rgba(10,18,28,0.98)");
      ctx.fillStyle = body;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = "rgba(125,211,252,0.35)";
      ctx.lineWidth = 1;
      ctx.stroke();

      // parallels
      ctx.strokeStyle = "rgba(125,211,252,0.13)";
      for (let lat = -60; lat <= 60; lat += 30) {
        ctx.beginPath();
        for (let lon = -180; lon <= 180; lon += 4) {
          const p = project(lat, lon);
          if (p.z < 0) continue;
          if (lon === -180) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        }
        ctx.stroke();
      }
      // meridians
      for (let lon = -180; lon < 180; lon += 30) {
        ctx.beginPath();
        let started = false;
        for (let lat = -90; lat <= 90; lat += 3) {
          const p = project(lat, lon);
          if (p.z < 0) {
            started = false;
            continue;
          }
          if (!started) {
            ctx.moveTo(p.x, p.y);
            started = true;
          } else ctx.lineTo(p.x, p.y);
        }
        ctx.stroke();
      }

      // arcs
      ARCS.forEach(([a, b], i) => {
        const from = NODES[a]!;
        const to = NODES[b]!;
        const cycle = (t / 2600 + i / ARCS.length) % 1;
        const steps = 48;
        const pts: { x: number; y: number; z: number }[] = [];
        for (let s = 0; s <= steps; s++) {
          const k = s / steps;
          const lat = from.lat + (to.lat - from.lat) * k;
          let dLon = to.lon - from.lon;
          if (dLon > 180) dLon -= 360;
          if (dLon < -180) dLon += 360;
          const lon = from.lon + dLon * k;
          const lift = 1 + Math.sin(Math.PI * k) * 0.28;
          const p = project(lat, lon);
          pts.push({
            x: cx + (p.x - cx) * lift,
            y: cy + (p.y - cy) * lift,
            z: p.z,
          });
        }
        ctx.lineWidth = 1;
        ctx.strokeStyle = "rgba(56,189,248,0.18)";
        ctx.beginPath();
        pts.forEach((p, idx) => {
          if (p.z < -0.15) return;
          if (idx === 0) ctx.moveTo(p.x, p.y);
          else ctx.lineTo(p.x, p.y);
        });
        ctx.stroke();

        // travelling pulse
        const head = Math.floor(cycle * steps);
        const trail = 9;
        for (let s = Math.max(0, head - trail); s <= head; s++) {
          const p = pts[s];
          if (!p || p.z < -0.15) continue;
          const alpha = (1 - (head - s) / trail) * 0.9;
          ctx.fillStyle =
            i % 3 === 0 ? `rgba(248,113,113,${alpha})` : `rgba(125,211,252,${alpha})`;
          ctx.beginPath();
          ctx.arc(p.x, p.y, 1.7, 0, Math.PI * 2);
          ctx.fill();
        }
      });

      // nodes
      NODES.forEach((n, i) => {
        const p = project(n.lat, n.lon);
        if (p.z < 0) return;
        const pulse = 0.5 + 0.5 * Math.sin(t / 620 + i);
        const hot = i % 4 === 0;
        ctx.fillStyle = hot ? "rgba(248,113,113,0.95)" : "rgba(125,211,252,0.9)";
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2.1, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = hot
          ? `rgba(248,113,113,${0.35 * (1 - pulse)})`
          : `rgba(125,211,252,${0.3 * (1 - pulse)})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3 + pulse * 9, 0, Math.PI * 2);
        ctx.stroke();
      });

      rotation += 0.12;
      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} className={className} aria-hidden />;
}
