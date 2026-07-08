import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Systems({ currentUser }) {
  const [systems, setSystems] = useState([]);
  const [connectorTypes, setConnectorTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedType, setSelectedType] = useState("");
  const [useRealCredentials, setUseRealCredentials] = useState(false);
  const [credentialValues, setCredentialValues] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);

  function loadAll() {
    setLoading(true);
    Promise.all([api.listSystems(), api.listConnectorTypes()])
      .then(([systemsData, typesData]) => {
        setSystems(systemsData);
        setConnectorTypes(typesData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(loadAll, []);

  const canWrite = currentUser?.role === "admin" || currentUser?.role === "owner";
  const connectedKeys = new Set(systems.map((s) => s.connector_key));
  const availableTypes = connectorTypes.filter((t) => !connectedKeys.has(t.connector_key));
  const selectedTypeMeta = connectorTypes.find((t) => t.connector_key === selectedType);

  function handleSelectType(key) {
    setSelectedType(key);
    setUseRealCredentials(false);
    setCredentialValues({});
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      await api.createSystem({
        connector_key: selectedType,
        credentials: useRealCredentials ? credentialValues : null,
      });
      setSelectedType("");
      setUseRealCredentials(false);
      setCredentialValues({});
      loadAll();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p>Cargando sistemas...</p>;
  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <h2>Sistemas conectados</h2>
      <p className="subtitle">
        Cada empresa conecta y configura sus propios sistemas. Sin
        credenciales, un sistema queda en modo simulado (útil para
        probar); con credenciales reales, las acciones son de verdad.
      </p>

      {systems.length === 0 ? (
        <p className="subtitle">Todavía no has conectado ningún sistema.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Sistema</th>
              <th>Categoría</th>
              <th>Modo</th>
            </tr>
          </thead>
          <tbody>
            {systems.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{s.category}</td>
                <td>
                  <span className={`status ${s.has_real_credentials ? "status-active" : "status-offboarded"}`}>
                    {s.has_real_credentials ? "real" : "simulado"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {canWrite && availableTypes.length > 0 && (
        <div className="offboard-panel">
          <h3>Conectar un sistema nuevo</h3>
          <form onSubmit={handleSubmit}>
            <label>
              Tipo de sistema
              <select value={selectedType} onChange={(e) => handleSelectType(e.target.value)} required>
                <option value="">Selecciona un tipo...</option>
                {availableTypes.map((t) => (
                  <option key={t.connector_key} value={t.connector_key}>
                    {t.label}
                  </option>
                ))}
              </select>
            </label>

            {selectedTypeMeta && !selectedTypeMeta.has_real_integration && (
              <p className="subtitle">
                Este tipo todavía no tiene integración real disponible - se conectará
                en modo simulado.
              </p>
            )}

            {selectedTypeMeta && selectedTypeMeta.has_real_integration && (
              <>
                <label style={{ flexDirection: "row", alignItems: "center", gap: "0.5rem" }}>
                  <input
                    type="checkbox"
                    checked={useRealCredentials}
                    onChange={(e) => setUseRealCredentials(e.target.checked)}
                    style={{ width: "auto" }}
                  />
                  Usar credenciales reales (si no, queda simulado)
                </label>

                {useRealCredentials &&
                  selectedTypeMeta.credential_fields.map((field) => (
                    <label key={field.key}>
                      {field.label}
                      <input
                        type={field.secret ? "password" : "text"}
                        value={credentialValues[field.key] || ""}
                        onChange={(e) =>
                          setCredentialValues({ ...credentialValues, [field.key]: e.target.value })
                        }
                        required
                      />
                    </label>
                  ))}
              </>
            )}

            {formError && <p className="error">{formError}</p>}

            <button type="submit" className="primary" disabled={submitting || !selectedType}>
              {submitting ? "Conectando..." : "Conectar sistema"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}