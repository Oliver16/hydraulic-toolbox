import { PumpForm } from "@/components/pump-form";

export default function PumpsPage() {
  return (
    <main className="mx-auto max-w-5xl space-y-6 py-10">
      <header>
        <h1 className="text-3xl font-semibold text-brand">Pumps</h1>
        <p className="text-slate-600">Upload or enter pump curve data and persist it to the library.</p>
      </header>
      <PumpForm />
    </main>
  );
}
