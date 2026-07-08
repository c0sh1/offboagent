import { useEffect, useState } from "react";
import { api } from "../api/client";

const ROLE_LABELS = { owner: "Propietario", admin: "Administrador", viewer: "Solo lectura" };

export default function Account({ currentUser }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const isOwner = currentUser?.role === "owner";
  const [orgName, setOrgName] = useState("");
  const [orgSubmitting, setOrgSubmitting] = useState(false);
  const [orgError, setOrgError] = useState(null);
  const [orgSuccess, setOrgSuccess] = useState(false);

  useEffect(() => {
    if (isOwner) {
      api.getOrganization().then((org) => setOrgName(org.name)).catch(() => {});
    }
  }, [isOwner]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas nuevas no coinciden.");
      return;
    }

    setSubmitting(true);
    try {
      await api.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleOrgSubmit(e) {
    e.preventDefault();
    setOrgError(null);
    setOrgSuccess(false);
    setOrgSubmitting(true);
    try {
      await api.updateOrganization({ name: orgName });
      setOrgSuccess(true);
    } catch (err) {
      setOrgError(err.message);
    } finally {
      setOrgSubmitting(false);
    }
  }

  return (
    <div>
      <h2>Mi cuenta</h2>
      {currentUser && (
        <p className="subtitle">
          {currentUser.full_name} · {currentUser.email} ·{" "}
          {ROLE_LABELS[currentUser.role] || currentUser.role}
        </p>
      )}

      <div className="offboard-panel">
        <h3>Cambiar contraseña</h3>
        <form onSubmit={handleSubmit}>
          <label>
            Contraseña actual
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
          </label>
          <label>
            Contraseña nueva
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={8}
            />
          </label>
          <label>
            Confirmar contraseña nueva
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
            />
          </label>

          {error && <p className="error">{error}</p>}
          {success && <p className="ok-message">✅ Contraseña actualizada correctamente.</p>}

          <button type="submit" className="primary" disabled={submitting}>
            {submitting ? "Guardando..." : "Cambiar contraseña"}
          </button>
        </form>
      </div>

      {isOwner && (
        <div className="offboard-panel">
          <h3>Configuración de la empresa</h3>
          <form onSubmit={handleOrgSubmit}>
            <label>
              Nombre de la empresa
              <input
                type="text"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                required
              />
            </label>

            {orgError && <p className="error">{orgError}</p>}
            {orgSuccess && <p className="ok-message">✅ Nombre actualizado correctamente.</p>}

            <button type="submit" className="primary" disabled={orgSubmitting}>
              {orgSubmitting ? "Guardando..." : "Guardar cambios"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}