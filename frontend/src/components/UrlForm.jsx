import { useState } from "react";

export default function UrlForm({ onSubmit, disabled }) {
  const [url, setUrl] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) return;
    try {
      await onSubmit(trimmed);
    } catch (err) {
      console.error('Form submission error:', err);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: "flex",
        gap: "0.5rem",
        alignItems: "center",
        marginBottom: "1rem",
      }}
    >
      <input
        type="url"
        placeholder="https://example.com"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        disabled={disabled}
        style={{
          flex: 1,
          padding: "0.5rem 0.75rem",
          borderRadius: "6px",
          border: "1px solid #ccc",
          fontSize: "0.95rem",
        }}
      />
      <button
        type="submit"
        disabled={disabled}
        style={{
          padding: "0.55rem 1.1rem",
          borderRadius: "6px",
          border: "none",
          backgroundColor: disabled ? "#999" : "#2563eb",
          color: "white",
          fontSize: "0.95rem",
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      >
        Generate
      </button>
    </form>
  );
}