import Link from "next/link";

const links = [
  { href: "/pumps", label: "Pumps" },
  { href: "/system-curves", label: "System Curves" },
  { href: "/scenarios", label: "Scenarios" }
];

export default function HomePage() {
  return (
    <main className="mx-auto max-w-4xl space-y-6 py-10">
      <header>
        <h1 className="text-3xl font-semibold text-brand">Hydraulic Toolbox</h1>
        <p className="text-slate-600">Manage pumps, system curves, and compute operating points.</p>
      </header>
      <nav className="grid gap-4 md:grid-cols-3">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className="rounded-lg border border-slate-200 bg-white p-4 text-center shadow-sm transition hover:border-brand hover:text-brand"
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </main>
  );
}
