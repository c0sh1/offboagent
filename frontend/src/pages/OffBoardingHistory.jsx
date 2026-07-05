import { useEffect, useState } from "react";
import { api } from "../api/client";

const STATUS_LABELS = {
  initiated: "Iniciado",
  in_progress: "En curso",
  completed: "Completado",
  completed_with_errors: "Completado con errores",
};

export default function OffboardingHistory() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    api
      .listOffboardingEvents()
      .then(setEvents)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Cargando historial...</p>;
  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <h2>Historial de offboardings</h2>

      {events.length === 0 ? (
        <p className="subtitle">Todavía no se ha ejecutado ningún offboarding.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Persona</th>
              <th>Estado</th>
              <th>Iniciado</th>
              <th>Completado</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <>
                <tr
                  key={event.id}
                  onClick={() =>
                    setExpandedId(expandedId === event.id ? null : event.id)
                  }
                >
                  <td>{event.person_full_name || event.person_id}</td>
                  <td>
                    <span className={`status status-${event.status}`}>
                      {STATUS_LABELS[event.status] || event.status}
                    </span>
                  </td>
                  <td>{new Date(event.started_at).toLocaleString()}</td>
                  <td>
                    {event.completed_at
                      ? new Date(event.completed_at).toLocaleString()
                      : "—"}
                  </td>
                </tr>
                {expandedId === event.id && (
                  <tr className="expanded-row">
                    <td colSpan={4}>
                      <ul className="log-list">
                        {event.log_entries.map((log, i) => (
                          <li
                            key={i}
                            className={log.result === "success" ? "ok" : "fail"}
                          >
                            {log.system_name}: {log.result} — {log.detail}
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}