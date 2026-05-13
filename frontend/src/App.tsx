const layerItems = [
  "Local FastAPI backend",
  "React + Vite TypeScript frontend",
  "Health check and build validation",
  "Reserved modular areas for future growth",
];

const outOfScopeItems = [
  "Authentication",
  "Tenants and workspaces",
  "Billing",
  "Cloud deployment",
  "Automated application submission",
];

function App() {
  return (
    <main className="app-shell">
      <section className="intro">
        <p className="eyebrow">Local-first Layer 1 foundation</p>
        <h1>Careero</h1>
        <p className="summary">
          A STRIDE-powered career operations application for organizing a
          personal job search and preparing stronger applications.
        </p>
      </section>

      <section className="foundation-grid" aria-label="Layer 1 foundation">
        <div className="panel">
          <h2>Layer 1 includes</h2>
          <ul>
            {layerItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="panel">
          <h2>Out of scope</h2>
          <ul>
            {outOfScopeItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}

export default App;
