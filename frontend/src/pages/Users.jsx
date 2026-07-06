import { useEffect, useState } from "react";
import { api } from "../api/client";

const ROLE_LABELS = { owner: "Propietario", admin: "Administrador", viewer: "Solo lectura" };

export default function Users({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("viewer");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  function loadUsers() {
    setLoading(true);
    api
      .listUsers()
      .then(setUsers)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadUsers();
    api.getUserAuditLog().then(setAuditLog).catch(() => {});
  }, []);

  function refreshAll() {
    loadUsers();
    api.getUserAuditLog().then(setAuditLog).catch(() => {});
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      await api.register({ email, full_name: fullName, password, role });
      setEmail("");
      setFullName("");
      setPassword("");
      setRole("viewer");
      refreshAll();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(user) {
    const confirmed = window.confirm(
      `¿Seguro que quieres eliminar a ${user.full_name} (${ROLE_LABELS[user.role]})? Esta acción es irreversible.`
    );
    if (!confirmed) return;
    try {
      await api.deleteUser(user.id);
      refreshAll();
    } catch (err) {
      alert(err.message);
    }
  }

  function canDelete(user) {
    if (user.id === currentUser?.id) return false;
    if (user.role === "owner") return false;
    if (currentUser?.role === "admin" && user.role !== "viewer") return false;
    return true;
  }

  if (loading) return <p>Cargando usuarios...</p>;
  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <h2>Usuarios</h2>
      <p className="subtitle">
        Quienes pueden entrar a esta herramienta. "Administrador" puede crear
        personas, asignar accesos y disparar offboardings; "Solo lectura"
        únicamente puede consultar.
      </p>

      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.full_name}</td>
              <td>{u.email}</td>
              <td>
                <span className={`status ${u.role === "viewer" ? "status-offboarded" : "status-active"}`}>
                  {ROLE_LABELS[u.role] || u.role}
                </span>
              </td>
              <td>
                {canDelete(u) && (
                  <button className="danger" onClick={() => handleDelete(u)}>
                    Eliminar
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="offboard-panel">
        <h3>Crear usuario nuevo</h3>
        <form onSubmit={handleSubmit}>
          <label>
            Nombre completo
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </label>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label>
            Contraseña temporal
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
          </label>
          <label>
            Rol
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="viewer">Solo lectura</option>
              {currentUser?.role === "owner" && <option value="admin">Administrador</option>}
            </select>
          </label>

          {formError && <p className="error">{formError}</p>}

          <button type="submit" className="primary" disabled={submitting}>
            {submitting ? "Creando..." : "Crear usuario"}
          </button>
        </form>
      </div>

      <h3>Historial de gestión de usuarios</h3>
      {auditLog.length === 0 ? (
        <p className="subtitle">Todavía no hay acciones registradas.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Quién</th>
              <th>Acción</th>
              <th>Sobre quién</th>
              <th>Fecha</th>
            </tr>
          </thead>
          <tbody>
            {auditLog.map((entry) => (
              <tr key={entry.id}>
                <td>{entry.actor_email}</td>
                <td>{entry.action === "create_user" ? "Creó a" : "Eliminó a"}</td>
                <td>
                  {entry.target_email} ({ROLE_LABELS[entry.target_role] || entry.target_role})
                </td>
                <td>{new Date(entry.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}