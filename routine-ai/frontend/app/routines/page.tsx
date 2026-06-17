"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";

interface Routine {
  id: number;
  name: string;
  description: string;
  time: string;
  repeat_type: string;
  active: number;
}

const REPEAT_LABEL: Record<string, string> = {
  daily: "매일",
  weekdays: "평일",
  weekends: "주말",
};

export default function RoutinesPage() {
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const data = await api.get("/routines");
    setRoutines(data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggle = async (routine: Routine) => {
    await api.patch(`/routines/${routine.id}`, { active: !routine.active });
    setRoutines((prev) =>
      prev.map((r) => r.id === routine.id ? { ...r, active: routine.active ? 0 : 1 } : r)
    );
  };

  const remove = async (id: number) => {
    if (!confirm("이 루틴을 삭제할까요?")) return;
    await api.delete(`/routines/${id}`);
    setRoutines((prev) => prev.filter((r) => r.id !== id));
  };

  if (loading) return <p className="text-gray-500 text-center mt-16">로딩 중...</p>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">루틴 관리</h1>
        <a href="/chat" className="text-sm text-blue-400 hover:underline">
          + AI로 추가하기
        </a>
      </div>

      {routines.length === 0 ? (
        <div className="text-center py-16 text-gray-600">
          <p className="text-lg mb-2">등록된 루틴이 없습니다.</p>
          <a href="/chat" className="text-blue-400 hover:underline text-sm">
            AI와 대화해서 루틴을 추가해보세요 →
          </a>
        </div>
      ) : (
        <div className="space-y-3">
          {routines.map((routine) => (
            <div
              key={routine.id}
              className={`flex items-center justify-between rounded-xl p-4 border ${
                routine.active ? "border-gray-700 bg-gray-900" : "border-gray-800 bg-gray-900 opacity-50"
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`font-semibold ${!routine.active ? "text-gray-500" : ""}`}>
                    {routine.name}
                  </span>
                  <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded-full">
                    {REPEAT_LABEL[routine.repeat_type] ?? routine.repeat_type}
                  </span>
                </div>
                {routine.description && (
                  <p className="text-xs text-gray-500 mt-0.5">{routine.description}</p>
                )}
                <p className="text-xs text-gray-600 mt-1">{routine.time}</p>
              </div>

              <div className="flex items-center gap-2 ml-4 shrink-0">
                <button
                  onClick={() => toggle(routine)}
                  className={`text-xs px-3 py-1.5 rounded-lg transition-colors ${
                    routine.active
                      ? "bg-gray-700 hover:bg-gray-600 text-gray-300"
                      : "bg-gray-800 hover:bg-gray-700 text-gray-500"
                  }`}
                >
                  {routine.active ? "비활성화" : "활성화"}
                </button>
                <button
                  onClick={() => remove(routine.id)}
                  className="text-xs px-3 py-1.5 rounded-lg bg-red-900/40 hover:bg-red-900/60 text-red-400 transition-colors"
                >
                  삭제
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
