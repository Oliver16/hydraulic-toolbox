import api from "@/lib/api";
import { CurveChart } from "@/components/curve-chart";

async function fetchResult(id: string) {
  const response = await api.get(`/api/results/${id}`);
  return response.data;
}

export default async function ResultPage({ params }: { params: { id: string } }) {
  const result = await fetchResult(params.id);
  const traces = result.operating_points.map((point: any) => ({
    name: `${point.configuration} @${point.speed_ratio.toFixed(2)}`,
    x: [point.flow],
    y: [point.head],
    mode: "markers",
    marker: { size: 12 }
  }));
  return (
    <main className="mx-auto max-w-5xl space-y-6 py-10">
      <header>
        <h1 className="text-3xl font-semibold text-brand">Scenario Result #{result.scenario_id}</h1>
        <p className="text-slate-600">Generated {new Date(result.created_at).toLocaleString()}</p>
      </header>
      <CurveChart traces={traces} />
      <section className="rounded border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="text-xl font-semibold">Operating Points</h2>
        <table className="mt-2 min-w-full text-sm">
          <thead>
            <tr className="bg-slate-100">
              <th className="p-2 text-left">Configuration</th>
              <th className="p-2 text-left">Speed</th>
              <th className="p-2 text-left">Flow</th>
              <th className="p-2 text-left">Head</th>
              <th className="p-2 text-left">Efficiency</th>
              <th className="p-2 text-left">Power</th>
            </tr>
          </thead>
          <tbody>
            {result.operating_points.map((point: any, idx: number) => (
              <tr key={idx} className="border-t">
                <td className="p-2">{point.configuration}</td>
                <td className="p-2">{point.speed_ratio.toFixed(2)}</td>
                <td className="p-2">{point.flow.toFixed(3)}</td>
                <td className="p-2">{point.head.toFixed(2)}</td>
                <td className="p-2">{point.efficiency ? `${(point.efficiency * 100).toFixed(1)}%` : "-"}</td>
                <td className="p-2">{point.power ? point.power.toFixed(0) : "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-4 flex gap-4">
          <a className="rounded bg-brand px-3 py-2 text-sm text-white" href={`/${result.csv_path}`}>
            Download data (JSON)
          </a>
          <a className="rounded bg-brand px-3 py-2 text-sm text-white" href={`/${result.pdf_path}`}>
            Download PDF
          </a>
        </div>
      </section>
    </main>
  );
}
