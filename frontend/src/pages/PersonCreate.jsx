import { useState } from "react";
import { api } from "../api/client";

export default function PersonCreate({ onCreated }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [personType, setPersonType] = useState("employee");
  const [department, setDepartment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const person = await api.createPerson({
        full_name: fullName,
        email,
        person_type: personType,
        department: department || null,
      });
      onCreated(person);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h2>Nueva persona</h2>
      <p className="subtitle">
        Registra a un empleado o contratista en el grafo de identidad.
        Sus accesos a sistemas se añaden después, a medida que se conectan.
      </p>

      <form className="panel-form" onSubmit={handleSubmit}>
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
          Tipo
          <select value={personType} onChange={(e) => setPersonType(e.target.value)}>
            <option value="employee">Empleado</option>
            <option value="contractor">Contratista</option>
          </select>
        </label>
        <label>
          Departamento (opcional)
          <input
            type="text"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            placeholder="ej. Engineering"
          />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit" className="primary" disabled={submitting}>
          {submitting ? "Creando..." : "Crear persona"}
        </button>
      </form>
    </div>
  );
}