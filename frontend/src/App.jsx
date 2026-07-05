import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import PersonsList from "./pages/PersonsList";
import PersonDetail from "./pages/PersonDetail";
import PersonCreate from "./pages/PersonCreate";
import OffboardingHistory from "./pages/OffboardingHistory";
import OrphanedAccessPanel from "./pages/OrphanedAccessPanel";

const NAV_ITEMS = [
  { id: "dashboard", label: "Resumen" },
  { id: "persons", label: "Personas" },
  { id: "history", label: "Historial" },
  { id: "orphaned", label: "Accesos huérfanos" },
];

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [personsSubView, setPersonsSubView] = useState(null);

  function goToView(view) {
    setPersonsSubView(null);
    setActiveView(view);
  }

  function renderMain() {
    if (activeView === "dashboard") {
      return <Dashboard onNavigate={goToView} />;
    }
    if (activeView === "history") {
      return <OffboardingHistory />;
    }
    if (activeView === "orphaned") {
      return <OrphanedAccessPanel />;
    }
    if (personsSubView?.type === "detail") {
      return (
        <PersonDetail
          personId={personsSubView.id}
          onBack={() => setPersonsSubView(null)}
        />
      );
    }
    if (personsSubView?.type === "create") {
      return (
        <PersonCreate
          onCreated={(person) =>
            setPersonsSubView({ type: "detail", id: person.id })
          }
        />
      );
    }
    return (
      <PersonsList
        onSelectPerson={(id) => setPersonsSubView({ type: "detail", id })}
        onCreateNew={() => setPersonsSubView({ type: "create" })}
      />
    );
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">◆</span>
          <span className="brand-name">Offboarding Agent</span>
        </div>
        <nav>
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={activeView === item.id ? "nav-item active" : "nav-item"}
              onClick={() => goToView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">{renderMain()}</main>
    </div>
  );
}