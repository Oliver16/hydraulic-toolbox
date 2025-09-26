"use client";

import { useFieldArray, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { createPump } from "@/lib/api";
import { useState } from "react";

const pointSchema = z.object({
  flow: z.number().nonnegative(),
  head: z.number().nonnegative(),
  efficiency: z.number().nonnegative().optional(),
  power: z.number().nonnegative().optional(),
  npshr: z.number().nonnegative().optional()
});

const formSchema = z.object({
  name: z.string().min(1),
  rated_speed_rpm: z.number().positive(),
  unit_system: z.enum(["us", "si"]),
  flow_unit: z.string().min(1),
  head_unit: z.string().min(1),
  efficiency_unit: z.string().optional(),
  power_unit: z.string().optional(),
  npshr_unit: z.string().optional(),
  curve_points: z.array(pointSchema).min(3)
});

export type PumpFormValues = z.infer<typeof formSchema>;

export function PumpForm() {
  const [message, setMessage] = useState<string | null>(null);
  const form = useForm<PumpFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      unit_system: "us",
      flow_unit: "gpm",
      head_unit: "ft",
      rated_speed_rpm: 1780,
      curve_points: [
        { flow: 0, head: 150, efficiency: 55, power: 100 },
        { flow: 500, head: 140, efficiency: 70, power: 120 },
        { flow: 1000, head: 120, efficiency: 75, power: 160 }
      ]
    }
  });

  const { fields, append, remove } = useFieldArray({ control: form.control, name: "curve_points" });

  const mutation = useMutation({
    mutationFn: createPump,
    onSuccess: () => {
      setMessage("Pump saved successfully");
    },
    onError: (error) => {
      setMessage(`Error: ${(error as Error).message}`);
    }
  });

  const onSubmit = (values: PumpFormValues) => {
    mutation.mutate(values);
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-1">
          <span>Name</span>
          <input className="rounded border border-slate-300 p-2" {...form.register("name")} />
        </label>
        <label className="flex flex-col gap-1">
          <span>Rated speed (RPM)</span>
          <input
            type="number"
            className="rounded border border-slate-300 p-2"
            {...form.register("rated_speed_rpm", { valueAsNumber: true })}
          />
        </label>
        <label className="flex flex-col gap-1">
          <span>Flow unit</span>
          <input className="rounded border border-slate-300 p-2" {...form.register("flow_unit")} />
        </label>
        <label className="flex flex-col gap-1">
          <span>Head unit</span>
          <input className="rounded border border-slate-300 p-2" {...form.register("head_unit")} />
        </label>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border border-slate-200 bg-white text-sm">
          <thead>
            <tr className="bg-slate-100">
              <th className="p-2 text-left">Flow</th>
              <th className="p-2 text-left">Head</th>
              <th className="p-2 text-left">Efficiency</th>
              <th className="p-2 text-left">Power</th>
              <th className="p-2 text-left">NPSHr</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {fields.map((field, index) => (
              <tr key={field.id} className="border-t">
                {["flow", "head", "efficiency", "power", "npshr"].map((key) => (
                  <td key={key} className="p-2">
                    <input
                      type="number"
                      step="any"
                      className="w-full rounded border border-slate-300 p-1"
                      {...form.register(`curve_points.${index}.${key as keyof typeof field}` as const, {
                        valueAsNumber: true
                      })}
                    />
                  </td>
                ))}
                <td className="p-2 text-right">
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className="text-sm text-red-500"
                    disabled={fields.length <= 3}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button
          type="button"
          onClick={() => append({ flow: 0, head: 0, efficiency: undefined })}
          className="mt-2 rounded bg-brand px-3 py-1 text-sm text-white"
        >
          Add point
        </button>
      </div>
      <button
        type="submit"
        className="rounded bg-brand px-4 py-2 font-semibold text-white disabled:opacity-50"
        disabled={mutation.isLoading}
      >
        Save pump
      </button>
      {message && <p className="text-sm text-slate-600">{message}</p>}
    </form>
  );
}
