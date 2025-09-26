"use client";

import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import api from "@/lib/api";
import { useState } from "react";

const pointSchema = z.object({ flow: z.number().nonnegative(), head: z.number().nonnegative() });

const schema = z.object({
  name: z.string().min(1),
  static_head: z.number().nonnegative(),
  static_head_unit: z.string().min(1),
  resistance_coefficient: z.number().nonnegative(),
  flow_unit: z.string().min(1),
  head_unit: z.string().min(1),
  unit_system: z.enum(["us", "si"]),
  csv_points: z.array(pointSchema).optional()
});

type FormValues = z.infer<typeof schema>;

export function SystemCurveForm() {
  const [message, setMessage] = useState<string | null>(null);
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "System Curve",
      static_head: 50,
      static_head_unit: "ft",
      resistance_coefficient: 1e-4,
      flow_unit: "gpm",
      head_unit: "ft",
      unit_system: "us",
      csv_points: []
    }
  });

  const { fields, append, remove } = useFieldArray({ control: form.control, name: "csv_points" });

  const mutation = useMutation({
    mutationFn: (values: FormValues) => api.post("/api/system-curves", values).then((res) => res.data),
    onSuccess: () => setMessage("System curve saved"),
    onError: (error) => setMessage(`Error: ${(error as Error).message}`)
  });

  return (
    <form onSubmit={form.handleSubmit((values) => mutation.mutate(values))} className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-1">
          <span>Name</span>
          <input className="rounded border border-slate-300 p-2" {...form.register("name")} />
        </label>
        <label className="flex flex-col gap-1">
          <span>Static head</span>
          <input
            type="number"
            className="rounded border border-slate-300 p-2"
            {...form.register("static_head", { valueAsNumber: true })}
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>Static head unit</span>
          <input className="rounded border border-slate-300 p-2" {...form.register("static_head_unit")} />
        </label>
        <label className="flex flex-col gap-1">
          <span>Resistance coefficient (K)</span>
          <input
            type="number"
            step="any"
            className="rounded border border-slate-300 p-2"
            {...form.register("resistance_coefficient", { valueAsNumber: true })}
          />
        </label>
      </div>
      <div>
        <h3 className="text-lg font-semibold">CSV Points (optional)</h3>
        <table className="mt-2 min-w-full border border-slate-200 text-sm">
          <thead>
            <tr className="bg-slate-100">
              <th className="p-2 text-left">Flow</th>
              <th className="p-2 text-left">Head</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {fields.map((field, index) => (
              <tr key={field.id} className="border-t">
                <td className="p-2">
                  <input
                    type="number"
                    step="any"
                    className="w-full rounded border border-slate-300 p-1"
                    {...form.register(`csv_points.${index}.flow` as const, { valueAsNumber: true })}
                  />
                </td>
                <td className="p-2">
                  <input
                    type="number"
                    step="any"
                    className="w-full rounded border border-slate-300 p-1"
                    {...form.register(`csv_points.${index}.head` as const, { valueAsNumber: true })}
                  />
                </td>
                <td className="p-2 text-right">
                  <button type="button" className="text-sm text-red-500" onClick={() => remove(index)}>
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button
          type="button"
          onClick={() => append({ flow: 0, head: 0 })}
          className="mt-2 rounded bg-brand px-3 py-1 text-sm text-white"
        >
          Add row
        </button>
      </div>
      <button
        type="submit"
        className="rounded bg-brand px-4 py-2 font-semibold text-white disabled:opacity-50"
        disabled={mutation.isLoading}
      >
        Save system curve
      </button>
      {message && <p className="text-sm text-slate-600">{message}</p>}
    </form>
  );
}
