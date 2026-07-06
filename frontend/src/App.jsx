import { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard";
import PersonsList from "./pages/PersonsList";
import PersonDetail from "./pages/PersonDetail";
import PersonCreate from "./pages/PersonCreate";
import OffboardingHistory from "./pages/OffboardingHistory";
import OrphanedAccessPanel from "./pages/OrphanedAccessPanel";
import Users from "./pages/Users";
import Login from "./pages/Login";
import { getToken, clearToken } from "./api/authToken";
import { api, setUnauthorizedHandler } from "./api/client";

const BASE_NAV_ITEMS = [
  { id: "dashboard", label: "Resumen" },
  { id: "persons", label: "Personas" },
  { id: "history", label: "Historial" },
  { id: "orphaned", label: "Accesos huérfanos" },
];

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!getToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [activeView, setActiveView] = useState("dashboard");
  const [personsSubView, setPersonsSubView] = useState(null);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setIsLoggedIn(false);
      setCurrentUser(null);
    });
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      api.getMe().then(setCurrentUser).catch(() => {});
    }
  }, [isLoggedIn]);

  function handleLogout() {
    clearToken();
    setIsLoggedIn(false);
    setCurrentUser(null);
  }

  function goToView(view) {
    setPersonsSubView(null);
    setActiveView(view);
  }

  const navItems =
    currentUser?.role === "admin" || currentUser?.role === "owner"
      ? [...BASE_NAV_ITEMS, { id: "users", label: "Usuarios" }]
      : BASE_NAV_ITEMS;

  function renderMain() {
    if (activeView === "dashboard") return <Dashboard onNavigate={goToView} />;
    if (activeView === "history") return <OffboardingHistory />;
    if (activeView === "orphaned") return <OrphanedAccessPanel />;
    if (activeView === "users") return <Users currentUser={currentUser} />;

    if (personsSubView?.type === "detail") {
      return (
        <PersonDetail
          personId={personsSubView.id}
          onBack={() => setPersonsSubView(null)}
          currentUser={currentUser}
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
        currentUser={currentUser}
      />
    );
  }

  if (!isLoggedIn) {
    return <Login onLoggedIn={() => setIsLoggedIn(true)} />;
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">◆</span>
          <span className="brand-name">Offboarding Agent</span>
        </div>
        <nav>
          {navItems.map((item) => (
            <button
              key={item.id}
              className={activeView === item.id ? "nav-item active" : "nav-item"}
              onClick={() => goToView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        {currentUser && (
          <p className="current-user-tag">
            {currentUser.full_name} · {currentUser.role}
          </p>
        )}
        <button className="nav-item logout-button" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </aside>
      <main className="content">{renderMain()}</main>
    </div>
  );
}