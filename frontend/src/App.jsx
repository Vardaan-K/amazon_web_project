import { useState } from "react";

function App() {
  const [form, setForm] = useState({
    genre: "",
    min_runtime: "",
    max_runtime: "",
    start_year: "",
    end_year: "",
    title_type: "movie",
    limit: 10,
  });

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      alert("Failed to fetch recommendations.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Movie Recommendations</h1>

      <form onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
        <input
          name="genre"
          placeholder="Genre"
          value={form.genre}
          onChange={handleChange}
          style={{ marginRight: "0.5rem" }}
        />
        <input
          name="start_year"
          placeholder="Start Year"
          value={form.start_year}
          onChange={handleChange}
          style={{ marginRight: "0.5rem", width: "100px" }}
        />
        <input
          name="end_year"
          placeholder="End Year"
          value={form.end_year}
          onChange={handleChange}
          style={{ marginRight: "0.5rem", width: "100px" }}
        />
        <input
          name="min_runtime"
          placeholder="Min Runtime"
          value={form.min_runtime}
          onChange={handleChange}
          style={{ marginRight: "0.5rem", width: "120px" }}
        />
        <input
          name="max_runtime"
          placeholder="Max Runtime"
          value={form.max_runtime}
          onChange={handleChange}
          style={{ marginRight: "0.5rem", width: "120px" }}
        />
        <select
          name="title_type"
          value={form.title_type}
          onChange={handleChange}
          style={{ marginRight: "0.5rem" }}
        >
          <option value="movie">Movie</option>
          <option value="tv">TV</option>
          <option value="short">Short</option>
        </select>
        <input
          name="limit"
          placeholder="Limit"
          type="number"
          value={form.limit}
          onChange={handleChange}
          style={{ width: "80px", marginRight: "0.5rem" }}
        />
        <button type="submit">Get Recommendations</button>
      </form>

      {loading && <p>Loading...</p>}

      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
        {results.map((movie, idx) => (
          <div
            key={idx}
            style={{
              border: "1px solid #ccc",
              borderRadius: "8px",
              padding: "1rem",
              width: "300px",
            }}
          >
            <h2>
              {movie.title} ({movie.year})
            </h2>
            <p>
              IMDb: {movie.imdb} | Votes: {movie.num_votes}
            </p>
            <p>
              <strong>Pros:</strong>
            </p>
            <ul>
              {movie.pros.map((pro, i) => (
                <li key={i}>{pro}</li>
              ))}
            </ul>
            <p>
              <strong>Cons:</strong>
            </p>
            <ul>
              {movie.cons.map((con, i) => (
                <li key={i}>{con}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
