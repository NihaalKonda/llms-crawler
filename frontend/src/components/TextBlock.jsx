export default function TextBlock({ label, filename, value }) {
  const canDownload = typeof window !== "undefined" && !!value;

  function handleCopy() {
    if (!value) return;
    navigator.clipboard.writeText(value).catch((err) => {
      console.error("Failed to copy text:", err);
    });
  }

  function handleDownload() {
    if (!value) return;
    const blob = new Blob([value], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div>
      <div
        style={{
          marginBottom: "0.4rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "0.5rem",
        }}
      >
        <span style={{ fontWeight: 500 }}>{label}</span>
        <div style={{ display: "flex", gap: "0.4rem" }}>
          <button
            type="button"
            onClick={handleCopy}
            disabled={!value}
            style={{
              padding: "0.3rem 0.7rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              backgroundColor: "#f9f9f9",
              cursor: value ? "pointer" : "not-allowed",
              fontSize: "0.8rem",
            }}
          >
            Copy
          </button>
          <button
            type="button"
            onClick={handleDownload}
            disabled={!value || !canDownload}
            style={{
              padding: "0.3rem 0.7rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              backgroundColor: "#f9f9f9",
              cursor: value ? "pointer" : "not-allowed",
              fontSize: "0.8rem",
            }}
          >
            Download
          </button>
        </div>
      </div>
      <textarea
        readOnly
        value={value}
        spellCheck={false}
        style={{
          width: "100%",
          minHeight: "260px",
          resize: "vertical",
          padding: "0.5rem 0.7rem",
          borderRadius: "6px",
          border: "1px solid #ddd",
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
          fontSize: "0.8rem",
          lineHeight: 1.4,
          backgroundColor: "#fafafa",
          whiteSpace: "pre",
        }}
      />
    </div>
  );
}