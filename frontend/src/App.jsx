import { useState } from "react";
import PersonsList from "./pages/PersonsList";
import PersonDetail from "./pages/PersonDetail";
import OrphanedAccessPanel from "./pages/OrphanedAccessPanel";

export default function App() {
  const [activeTab, setActiveTab] = useState("persons"); // "persons" | "orphaned"
  const [selectedPersonId, setSelectedPersonId] = useState(null);

  function goToTab(tab) {
    setSelectedPersonId(null);
    setActiveTab(tab);
  }

  return (
    <div className="app">
      <header>
        <h1>Offboarding Security Agent</h1>
        <nav>
          <button
            className={activeTab === "persons" ? "tab active" : "tab"}
            onClick={() => goToTab("persons")}
          >
            Personas
          </button>
          <button
            className={activeTab === "orphaned" ? "tab active" : "tab"}
            onClick={() => goToTab("orphaned")}
          >
            Accesos huérfanos
          </button>
        </nav>
      </header>
      <main>
        {activeTab === "orphaned" ? (
          <OrphanedAccessPanel />
        ) : selectedPersonId ? (
          <PersonDetail
            personId={selectedPersonId}
            onBack={() => setSelectedPersonId(null)}
          />
        ) : (
          <PersonsList onSelectPerson={setSelectedPersonId} />
        )}
      </main>
    </div>
  );
}