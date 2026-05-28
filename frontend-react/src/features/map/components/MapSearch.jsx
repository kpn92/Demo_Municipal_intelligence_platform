import { useRef, useEffect } from "react";
import { useMapSearch } from "../hooks/useMapSearch.js";

function MapSearch({ whenReady }) {
  const { query, results, search, flyTo, clear } = useMapSearch(whenReady);
  const inputRef = useRef(null);

  useEffect(() => {
    if (results.length === 0) return;
    const handler = (e) => {
      if (inputRef.current && !inputRef.current.closest(".map-search-wrap")?.contains(e.target)) {
        clear();
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [results.length, clear]);

  return (
    <div className="map-search-wrap">
      <div className="map-search-row">
        <input
          ref={inputRef}
          type="search"
          className="map-search-input"
          placeholder="Αναζήτηση δρόμου…"
          value={query}
          onChange={(e) => search(e.target.value)}
          autoComplete="off"
        />
        {query && (
          <button type="button" className="map-search-clear" onClick={clear} aria-label="Καθαρισμός">
            ×
          </button>
        )}
      </div>
      {results.length > 0 && (
        <ul className="map-search-results" role="listbox">
          {results.map((r) => (
            <li
              key={r.id}
              role="option"
              className="map-search-result-item"
              onMouseDown={() => flyTo(r)}
            >
              {r.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MapSearch;
