"use client";

import { useForm, useFieldArray } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import api, { createScenario } from "@/lib/api";
import { useState } from "react";

const pumpConfigSchema = z.object({
  pump_id: z.number().int().positive(),
  arrangement: z.enum(["parallel", "series"]),
  count: z.number().int().positive(),
  vfd_speeds: z.array(z.number().positive()).min(1)
});

const schema = z.object({
  name: z.string().min(1),
  system_curve_id: z.number().int().positive(),
  unit_system: z.enum(["us", "si"]),
  pumps: z.array(pumpConfigSchema).min(1)
});

type FormValues = z.infer<typeof schema>;

export function ScenarioForm() {
  const [message, setMessage] = useState<string | null>(null);
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "Scenario",
      unit_system: "us",
      system_curve_id: 1,
      pumps: [{ pump_id: 1, arrangement: "parallel", count: 1, vfd_speeds: [1.0] }]
    }
  });

  const { fields, append, remove } = useFieldArray({ control: form.control, name: "pumps" });

  const mutation = useMutation({
    mutationFn: createScenario,
    onSuccess: (data) => setMessage(`Scenario ${data.name} created`),
    onError: (error) => setMessage(`Error: ${(error as Error).message}`)
  });

  const { data: pumps } = useQuery({ queryKey: ["pumps"], queryFn: () => api.get("/api/pumps").then((res) => res.data) });
  const { data: systemCurves } = useQuery({
    queryKey: ["system-curves"],
    queryFn: () => api.get("/api/system-curves").then((res) => res.data)
  });

  return (
    <form onSubmit={form.handleSubmit((values) => mutation.mutate(values))} className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-1">
          <span>Name</span>
          <input className="rounded border border-slate-300 p-2" {...form.register("name")} />
        </label>
        <label className="flex flex-col gap-1">
          <span>System curve</span>
          <select className="rounded border border-slate-300 p-2" {...form.register("system_curve_id", { valueAsNumber: true })}>
            {systemCurves?.map((curve: any) => (
              <option key={curve.id} value={curve.id}>
                {curve.name}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="space-y-4">
        {fields.map((field, index) => (
          <div key={field.id} className="rounded border border-slate-200 bg-white p-4 shadow-sm">
            <div className="grid gap-4 md:grid-cols-4">
              <label className="flex flex-col gap-1">
                <span>Pump</span>
                <select
                  className="rounded border border-slate-300 p-2"
                  {...form.register(`pumps.${index}.pump_id` as const, { valueAsNumber: true })}
                >
                  {pumps?.map((pump: any) => (
                    <option key={pump.id} value={pump.id}>
                      {pump.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="flex flex-col gap-1">
                <span>Arrangement</span>
                <select className="rounded border border-slate-300 p-2" {...form.register(`pumps.${index}.arrangement` as const)}>
                  <option value="parallel">Parallel</option>
                  <option value="series">Series</option>
                </select>
              </label>
              <label className="flex flex-col gap-1">
                <span>Count</span>
                <input
                  type="number"
                  className="rounded border border-slate-300 p-2"
                  {...form.register(`pumps.${index}.count` as const, { valueAsNumber: true })}
                />
              </label>
              <label className="flex flex-col gap-1">
                <span>VFD Speeds</span>
                <input
                  className="rounded border border-slate-300 p-2"
                  {...form.register(`pumps.${index}.vfd_speeds` as const, {
                    setValueAs: (value) =>
                      String(value)
                        .split(",")
                        .map((v) => parseFloat(v.trim()))
                        .filter((v) => !Number.isNaN(v))
                  })}
                  defaultValue={field.vfd_speeds?.join(",") || "1.0"}
                />
              </label>
            </div>
            <div className="mt-2 text-right">
              <button type="button" className="text-sm text-red-500" onClick={() => remove(index)}>
                Remove
              </button>
            </div>
          </div>
        ))}
        <button
          type="button"
          onClick={() => append({ pump_id: pumps?.[0]?.id ?? 1, arrangement: "parallel", count: 1, vfd_speeds: [1] })}
          className="rounded bg-brand px-3 py-1 text-sm text-white"
        >
          Add pump
        </button>
      </div>
      <button
        type="submit"
        className="rounded bg-brand px-4 py-2 font-semibold text-white disabled:opacity-50"
        disabled={mutation.isLoading}
      >
        Save scenario
      </button>
      {message && <p className="text-sm text-slate-600">{message}</p>}
    </form>
  );
}
