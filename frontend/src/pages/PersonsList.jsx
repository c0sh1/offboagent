import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function PersonsList({ onSelectPerson }) {
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .listPersons()
      .then(setPersons)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Cargando personas...</p>;
  if (error) return <p className="error">Error: {error}</p>;

  return (
    <div>
      <h2>Personas</h2>
      <table>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Email</th>
            <th>Tipo</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {persons.map((person) => (
            <tr key={person.id} onClick={() => onSelectPerson(person.id)}>
              <td>{person.full_name}</td>
              <td>{person.email}</td>
              <td>{person.person_type}</td>
              <td>
                <span className={`status status-${person.status}`}>
                  {person.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}