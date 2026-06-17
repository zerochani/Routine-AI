"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";

interface Routine {
  id: number;
  name: string;
  description: string;
  time: string;
  repeat_type: string;
  completion_status: string | null;
}

interface StreakMap {
  [routineId: number]: number;
}

export default function DashboardPage() {
  const [routines, setRoutines] = useState<Routine[]>([]);
  const [streaks, setStreaks] = useState<StreakMap>({});
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const data = await api.get("/routines?today=true");
    setRoutines(data);

    const streakResults = await Promise.all(
      data.map((r: Routine) =>
        api.get(`/routines/${r.id}/streak`).then((s: { streak: number }) => [r.id, s.streak])
      )
    );
    setStreaks(Object.fromEntries(streakResults));
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const complete = async (routineId: number, status: "done" | "skip") => {
    await api.post("/completions", { routine_id: routineId, status });
    setRoutines((prev) =>
      prev.map((r) => r.id === routineId ? { ...r, completion_status: status } : r)
    );
    if (status === "done") {
      setStreaks((prev) => ({ ...prev, [routineId]: (prev[routineId] ?? 0) + 1 }));
    }
  };

  if (loading) {
    return <p className="text-gray-500 text-center mt-16">로딩 중...</p>;
  }

  const totalStreak = Object.values(streaks).reduce((a, b) => a + b, 0);
  const doneCount = routines.filter((r) => r.completion_status === "done").length;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">오늘 루틴</h1>
          <p className="text-gray-500 text-sm mt-1">
            {new Date().toLocaleDateString("ko-KR", { weekday: "long", month: "long", day: "numeric" })}
          </p>
        </div>
        {totalStreak > 0 && (
          <div className="text-right">
            <p className="text-2xl">🔥</p>
            <p className="text-sm text-orange-400 font-semibold">{totalStreak}일 연속</p>
          </div>
        )}
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
          {routines.map((routine) => {
            const isDone = routine.completion_status === "done";
            const isSkip = routine.completion_status === "skip";
            const completed = isDone || isSkip;

            return (
              <div
                key={routine.id}
                className={`flex items-center justify-between rounded-xl p-4 border transition-all ${
                  completed
                    ? "border-gray-800 bg-gray-900 opacity-60"
                    : "border-gray-700 bg-gray-900"
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`font-semibold ${isDone ? "line-through text-gray-500" : ""}`}>
                      {routine.name}
                    </span>
                    {streaks[routine.id] > 0 && (
                      <span className="text-xs text-orange-400">🔥{streaks[routine.id]}</span>
                    )}
                  </div>
                  {routine.description && (
                    <p className="text-xs text-gray-500 mt-0.5">{routine.description}</p>
                  )}
                  <p className="text-xs text-gray-600 mt-1">{routine.time}</p>
                </div>

                {!completed ? (
                  <div className="flex gap-2 ml-4 shrink-0">
                    <button
                      onClick={() => complete(routine.id, "done")}
                      className="px-3 py-1.5 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm font-medium transition-colors"
                    >
                      완료
                    </button>
                    <button
                      onClick={() => complete(routine.id, "skip")}
                      className="px-3 py-1.5 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm transition-colors"
                    >
                      건너뜀
                    </button>
                  </div>
                ) : (
                  <span className={`ml-4 text-sm font-medium shrink-0 ${isDone ? "text-green-500" : "text-gray-500"}`}>
                    {isDone ? "✓ 완료" : "— 건너뜀"}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}

      {routines.length > 0 && (
        <p className="text-center text-sm text-gray-600 mt-8">
          {doneCount}/{routines.length} 완료
        </p>
      )}
    </div>
  );
}
