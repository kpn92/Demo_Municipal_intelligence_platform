import { useState, useEffect } from "react";

export function useClock() {
  const [time, setTime] = useState(() =>
    new Date().toLocaleTimeString("el-GR", { hour: "2-digit", minute: "2-digit" }),
  );

  useEffect(() => {
    const tick = () =>
      setTime(new Date().toLocaleTimeString("el-GR", { hour: "2-digit", minute: "2-digit" }));
    const id = setInterval(tick, 10000);
    return () => clearInterval(id);
  }, []);

  return time;
}
