import { useState } from "react";
import { api } from "../api/client";

const ROLE_LABELS = { owner: "Propietario", admin: "Administrador", viewer: "Solo lectura" };

export default function Account({ currentUser }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

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
    </div>
  );
}