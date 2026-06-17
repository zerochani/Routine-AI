"use client";

import { useEffect } from "react";
import { registerPush } from "@/lib/api";

export default function PushInit() {
  useEffect(() => {
    registerPush().catch(console.error);
  }, []);
  return null;
}
