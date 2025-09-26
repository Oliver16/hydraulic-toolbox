"use client";

import { useForm } from "react-hook-form";
import { useState } from "react";
import api from "@/lib/api";

interface LoginValues {
  email: string;
  password: string;
}

export default function LoginPage() {
  const form = useForm<LoginValues>({ defaultValues: { email: "user@example.com", password: "password" } });
  const [message, setMessage] = useState<string | null>(null);

  const onSubmit = async (values: LoginValues) => {
    try {
      const data = new URLSearchParams();
      data.append("username", values.email);
      data.append("password", values.password);
      const response = await api.post("/auth/login", data, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });
      setMessage(`Logged in. Access token: ${response.data.access_token.slice(0, 16)}...`);
    } catch (error) {
      setMessage(`Error: ${(error as Error).message}`);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center gap-6 p-8">
      <h1 className="text-3xl font-semibold text-brand">Sign in</h1>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <label className="flex flex-col gap-1">
          <span>Email</span>
          <input className="rounded border border-slate-300 p-2" {...form.register("email")} />
        </label>
        <label className="flex flex-col gap-1">
          <span>Password</span>
          <input type="password" className="rounded border border-slate-300 p-2" {...form.register("password")} />
        </label>
        <button type="submit" className="w-full rounded bg-brand px-4 py-2 font-semibold text-white">
          Log in
        </button>
      </form>
      {message && <p className="text-sm text-slate-600">{message}</p>}
    </main>
  );
}
