import { useState } from "react";
import { api } from "../api/client";
import { setToken } from "../api/authToken";

export default function Login({ onLoggedIn }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (mode === "register") {
        await api.register({ email, full_name: fullName, password });
      }
      const { access_token } = await api.login({ email, password });
      setToken(access_token);
      onLoggedIn();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-screen">
      <form className="panel-form login-form" onSubmit={handleSubmit}>
        <div className="brand" style={{ marginBottom: "0.5rem" }}>
          <span className="brand-mark" aria-hidden="true">◆</span>
          <span className="brand-name">Offboarding Agent</span>
        </div>
        <h2>{mode === "login" ? "Iniciar sesión" : "Crear cuenta de administrador"}</h2>

        {mode === "register" && (
          <label>
            Nombre completo
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </label>
        )}
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
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit" className="primary" disabled={submitting}>
          {submitting ? "Procesando..." : mode === "login" ? "Entrar" : "Crear cuenta y entrar"}
        </button>

        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          style={{ background: "transparent", border: "none" }}
        >
          {mode === "login"
            ? "¿Primera vez? Crear cuenta de administrador"
            : "¿Ya tienes cuenta? Iniciar sesión"}
        </button>
      </form>
    </div>
  );
}