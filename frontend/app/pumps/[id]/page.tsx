import api from "@/lib/api";
import { CurveChart } from "@/components/curve-chart";

async function fetchPump(id: string) {
  const response = await api.get(`/api/pumps/${id}`);
  return response.data;
}

export default async function PumpDetailPage({ params }: { params: { id: string } }) {
  const pump = await fetchPump(params.id);
  const trace = {
    name: pump.name,
    x: pump.curve_points.map((p: any) => p.flow),
    y: pump.curve_points.map((p: any) => p.head),
    mode: "lines"
  };
  return (
    <main className="mx-auto max-w-5xl space-y-6 py-10">
      <header>
        <h1 className="text-3xl font-semibold text-brand">{pump.name}</h1>
        <p className="text-slate-600">Rated speed {pump.rated_speed_rpm} RPM</p>
      </header>
      <CurveChart traces={[trace]} />
      <section className="rounded border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="text-xl font-semibold">Curve Points</h2>
        <table className="mt-2 min-w-full text-sm">
          <thead>
            <tr className="bg-slate-100">
              <th className="p-2 text-left">Flow ({pump.flow_unit})</th>
              <th className="p-2 text-left">Head ({pump.head_unit})</th>
              <th className="p-2 text-left">Efficiency</th>
            </tr>
          </thead>
          <tbody>
            {pump.curve_points.map((point: any, idx: number) => (
              <tr key={idx} className="border-t">
                <td className="p-2">{point.flow.toFixed(2)}</td>
                <td className="p-2">{point.head.toFixed(2)}</td>
                <td className="p-2">{point.efficiency ? `${(point.efficiency * 100).toFixed(1)}%` : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
