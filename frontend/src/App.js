import { useEffect, useState } from "react";
import "./App.css";

const COLORS = [
  "#FF0000",
  "#00FF00",
  "#0000FF",
  "#FFFF00",
  "#FF00FF",
  "#00FFFF",
  "#000000",
  "#FFFFFF"
];

const GRID_SIZE = 50;

// Base API: always go through nginx /api (ingress/frontend proxy)
const API_BASE = "/api";

function App() {
  const [grid, setGrid] = useState([]);
  const [selectedColor, setSelectedColor] = useState("#FF0000");

  const fetchGrid = async () => {
    try {
      const res = await fetch(`${API_BASE}/grid`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGrid(data.grid);
    } catch (err) {
      console.error("fetchGrid error:", err);
    }
  };

  const updatePixel = async (x, y) => {
    const colorIndex = COLORS.indexOf(selectedColor);
    try {
      await fetch(`${API_BASE}/pixel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          x,
          y,
          color: colorIndex + 1
        })
      });
      // Optionnel: rafraîchir localement pour réactivité
      // fetchGrid();
    } catch (err) {
      console.error("updatePixel error:", err);
    }
  };

  useEffect(() => {
    fetchGrid();
    const interval = setInterval(fetchGrid, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      {/* Simple status when grid not yet loaded */}
      {grid.length === 0 && (
        <div style={{ position: "absolute", top: 10, left: 10, fontSize: 14, color: "#555" }}>
          Chargement de la grille...
        </div>
      )}
      {/* Palette */}
      <div className="color-palette">
        {COLORS.map((color) => (
          <div
            key={color}
            onClick={() => setSelectedColor(color)}
            className={`color-swatch ${selectedColor === color ? "color-selected" : ""}`}
            style={{ backgroundColor: color }}
          />
        ))}
      </div>

      {/* Grille */}
      <div
        className="grid"
        style={{
          gridTemplateColumns: `repeat(${GRID_SIZE}, var(--pixel-size))`
        }}
      >
        {grid.flatMap((row, y) =>
          row.map((color, x) => (
            <div
              key={`${x}-${y}`}
              onClick={() => updatePixel(x, y)}
              className="pixel"
              style={{
                    // Use a light gray for empty cells so the grid is visible immediately
                    backgroundColor: color === 0 ? "#e6e6e6" : COLORS[color - 1]
              }}
            />
          ))
        )}
      </div>
    </div>
  );
}

export default App;