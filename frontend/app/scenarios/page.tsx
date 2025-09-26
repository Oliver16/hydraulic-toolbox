import { ScenarioForm } from "@/components/scenario-form";

export default function ScenariosPage() {
  return (
    <main className="mx-auto max-w-5xl space-y-6 py-10">
      <header>
        <h1 className="text-3xl font-semibold text-brand">Scenarios</h1>
        <p className="text-slate-600">Combine pumps with system curves and evaluate operating points.</p>
      </header>
      <ScenarioForm />
    </main>
  );
}
