import { useState } from "react";
import { KGResponse } from "../lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function KgPage() {
  const [question, setQuestion] = useState("");
  const [data, setData] = useState<KGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [supportedPatterns, setSupportedPatterns] = useState<string[]>([]);

  async function submit() {
    setError(null);
    setData(null);
    setSupportedPatterns([]);

    try {
      const res = await fetch(`${API_URL}/kg/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (res.status === 422) {
        const errData = await res.json();
        if (errData.detail && errData.detail.supported_patterns) {
          setSupportedPatterns(errData.detail.supported_patterns);
          setError("Unsupported question pattern.");
        } else {
          setError(JSON.stringify(errData.detail));
        }
        return;
      }
      if (res.status === 503) {
        setError("The backend is starting up — please try again in a moment.");
        return;
      }
      if (!res.ok) {
        setError("Could not reach the backend.");
        return;
      }

      const result: KGResponse = await res.json();
      setData(result);
    } catch {
      setError("Could not reach the backend.");
    }
  }

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Knowledge Graph — Recipe Query</h1>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="e.g. Find Sichuan recipes"
        style={{ width: "60%", padding: "0.5rem" }}
      />
      <button onClick={submit} disabled={!question} style={{ padding: "0.5rem 1rem", marginLeft: "1rem" }}>
        Ask
      </button>

      {error && <div style={{ color: "red", marginTop: "1rem" }}>{error}</div>}

      {supportedPatterns.length > 0 && (
        <div style={{ marginTop: "1rem", backgroundColor: "#fff3cd", padding: "1rem", borderRadius: "4px" }}>
          <h4>Supported Patterns:</h4>
          <ul>
            {supportedPatterns.map((pat, idx) => (
              <li key={idx}>{pat}</li>
            ))}
          </ul>
        </div>
      )}

      {data && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Generated Cypher:</h3>
          <pre style={{ background: "#f4f4f4", padding: "1rem", borderRadius: "4px" }}>{data.cypher}</pre>

          <h3>Results ({data.count} rows):</h3>
          <table border={1} cellPadding={8} style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
            <thead>
              <tr>
                <th>Record Data</th>
              </tr>
            </thead>
            <tbody>
              {data.rows.map((row, idx) => (
                <tr key={idx} data-testid="kg-row">
                  <td>
                    <pre style={{ margin: 0 }}>{JSON.stringify(row, null, 2)}</pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}