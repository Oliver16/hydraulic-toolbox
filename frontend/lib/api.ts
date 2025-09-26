import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
});

export interface PumpInput {
  name: string;
  rated_speed_rpm: number;
  flow_unit: string;
  head_unit: string;
  efficiency_unit?: string;
  power_unit?: string;
  npshr_unit?: string;
  unit_system: "us" | "si";
  curve_points: Array<{ flow: number; head: number; efficiency?: number; power?: number; npshr?: number }>;
}

export interface ScenarioInput {
  name: string;
  system_curve_id: number;
  pumps: Array<{ pump_id: number; arrangement: "parallel" | "series"; count: number; vfd_speeds: number[] }>;
  unit_system: "us" | "si";
}

export async function createPump(payload: PumpInput) {
  return api.post("/api/pumps", payload).then((res) => res.data);
}

export async function listPumps() {
  return api.get("/api/pumps").then((res) => res.data);
}

export async function createScenario(payload: ScenarioInput) {
  return api.post("/api/scenarios", payload).then((res) => res.data);
}

export async function computeScenario(id: number) {
  return api.post(`/api/scenarios/${id}/compute`).then((res) => res.data);
}

export async function getResult(id: number) {
  return api.get(`/api/results/${id}`).then((res) => res.data);
}

export default api;
