import { SystemCurveForm } from "@/components/system-curve-form";

export default function SystemCurvesPage() {
  return (
    <main className="mx-auto max-w-5xl space-y-6 py-10">
      <header>
        <h1 className="text-3xl font-semibold text-brand">System Curves</h1>
        <p className="text-slate-600">Define system head curves analytically or from CSV data.</p>
      </header>
      <SystemCurveForm />
    </main>
  );
}
