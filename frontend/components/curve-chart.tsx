"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export interface CurveTrace {
  name: string;
  x: number[];
  y: number[];
  mode?: "lines" | "markers";
  line?: { dash?: string; color?: string };
}

export function CurveChart({ traces }: { traces: CurveTrace[] }) {
  const data = useMemo(() => traces, [traces]);
  return (
    <div className="rounded border border-slate-200 bg-white p-4 shadow">
      <Plot
        data={data as any}
        layout={{
          autosize: true,
          height: 420,
          legend: { orientation: "h" },
          margin: { l: 60, r: 20, t: 30, b: 50 },
          xaxis: { title: "Flow" },
          yaxis: { title: "Head" }
        }}
        useResizeHandler
        style={{ width: "100%", height: "100%" }}
        config={{ displayModeBar: true, responsive: true }}
      />
    </div>
  );
}
