import { useRef, useState, useEffect, useCallback } from "react";
import useOperationsStore from "../../../store/useOperationsStore.js";
import { formatMinutes } from "../../../shared/lib/formatters.js";
import {
  getInterpolatedPosition,
} from "../lib/collectionRouting.js";
import {
  updateCollectionMarkerPosition,
  removeCollectionMarker,
} from "../../map/hooks/useCollectionRouteMap.js";

const ANIM_DURATION = 30000;

function CollectionTimeline() {
  const route = useOperationsStore((s) => s.collectionWizard.route);

  const [isAnimating, setIsAnimating] = useState(false);

  // Refs for animation state (avoid re-renders in rAF loop)
  const animatingRef = useRef(false);
  const progressRef = useRef(0);
  const startTimeRef = useRef(null);
  const frameIdRef = useRef(null);

  // Refs for DOM elements updated directly in rAF
  const fillRef = useRef(null);
  const thumbRef = useRef(null);
  const binCountRef = useRef(null);
  const timeRef = useRef(null);

  const updateDom = useCallback((progress) => {
    const pct = progress * 100;
    if (fillRef.current) fillRef.current.style.width = `${pct}%`;
    if (thumbRef.current) thumbRef.current.style.left = `${pct}%`;
    if (route) {
      if (binCountRef.current) {
        binCountRef.current.textContent =
          `${Math.round(progress * route.totalBins)} / ${route.totalBins} κάδοι`;
      }
      if (timeRef.current) {
        timeRef.current.textContent =
          formatMinutes(Math.round(progress * route.estimatedMinutes));
      }
      updateCollectionMarkerPosition(getInterpolatedPosition(route.allBins, progress));
    }
  }, [route]);

  const tick = useCallback((timestamp) => {
    if (!animatingRef.current) return;

    if (!startTimeRef.current) {
      startTimeRef.current = timestamp - progressRef.current * ANIM_DURATION;
    }

    const elapsed = timestamp - startTimeRef.current;
    const newProgress = Math.min(elapsed / ANIM_DURATION, 1);
    progressRef.current = newProgress;

    updateDom(newProgress);

    if (newProgress >= 1) {
      animatingRef.current = false;
      setIsAnimating(false);
      return;
    }
    frameIdRef.current = requestAnimationFrame(tick);
  }, [updateDom]);

  const start = useCallback(() => {
    if (progressRef.current >= 1) {
      progressRef.current = 0;
      startTimeRef.current = null;
      updateDom(0);
    }
    animatingRef.current = true;
    setIsAnimating(true);
    frameIdRef.current = requestAnimationFrame(tick);
  }, [tick, updateDom]);

  const pause = useCallback(() => {
    animatingRef.current = false;
    if (frameIdRef.current) cancelAnimationFrame(frameIdRef.current);
    setIsAnimating(false);
  }, []);

  const reset = useCallback(() => {
    pause();
    progressRef.current = 0;
    startTimeRef.current = null;
    updateDom(0);
    removeCollectionMarker();
  }, [pause, updateDom]);

  // Cancel animation when route changes or component unmounts
  useEffect(() => {
    return () => {
      if (frameIdRef.current) cancelAnimationFrame(frameIdRef.current);
      animatingRef.current = false;
    };
  }, [route]);

  const handleTogglePlay = () => {
    if (isAnimating) pause();
    else start();
  };

  if (!route) return null;

  return (
    <section className="fleet-timeline-bar is-visible">
      <div className="fleet-timeline-inner">
        <span className="fleet-timeline-label">
          {route.vehicle.vehicle_code ?? route.vehicle.id}
        </span>

        <div className="fleet-timeline-track-wrap">
          <div className="fleet-timeline-track-bg">
            <div
              ref={fillRef}
              className="fleet-timeline-track-fill"
              style={{ width: "0%" }}
            />
          </div>
          <div
            ref={thumbRef}
            className="fleet-timeline-track-thumb"
            style={{ left: "0%" }}
          />
        </div>

        <div className="fleet-timeline-meta">
          <span ref={binCountRef} className="fleet-timeline-bin-count">
            0 / {route.totalBins} κάδοι
          </span>
          <span ref={timeRef} className="fleet-timeline-time">
            0λ
          </span>
        </div>

        <div className="fleet-timeline-controls">
          <button
            type="button"
            className={`fleet-timeline-play-btn${isAnimating ? " is-playing" : ""}`}
            onClick={handleTogglePlay}
          >
            {isAnimating ? (
              <>
                <svg viewBox="0 0 24 24" width="14" height="14">
                  <rect x="6" y="4" width="4" height="16" fill="currentColor" />
                  <rect x="14" y="4" width="4" height="16" fill="currentColor" />
                </svg>
                Παύση
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" width="14" height="14">
                  <path fill="currentColor" d="M8 5v14l11-7z" />
                </svg>
                Εκτέλεση
              </>
            )}
          </button>
          <button type="button" className="fleet-timeline-stop-btn" onClick={reset}>
            <svg viewBox="0 0 24 24" width="10" height="10">
              <rect x="4" y="4" width="16" height="16" fill="currentColor" />
            </svg>
            Reset
          </button>
        </div>
      </div>
    </section>
  );
}

export default CollectionTimeline;
