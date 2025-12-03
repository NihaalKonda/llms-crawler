import { useState } from "react";
import { crawlSite } from "./api";
import UrlForm from "./components/UrlForm";
import ResultsTabs from "./components/ResultsTabs";
import Loader from "./components/Loader";

export default function App() {
  const [llmsTxt, setLlmsTxt] = useState("");
  const [llmsFullTxt, setLlmsFullTxt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(url) {
    setError("");
    setLoading(true);
    setLlmsTxt("");
    setLlmsFullTxt("");

    try {
      const { llms_txt, llms_full_txt } = await crawlSite(url);
      setLlmsTxt(llms_txt || "");
      setLlmsFullTxt(llms_full_txt || "");
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "2rem 1rem",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <h1 style={{ fontSize: "1.8rem", marginBottom: "0.75rem" }}>
        llms.txt Generator
      </h1>
      <p style={{ marginBottom: "1.5rem", color: "#555" }}>
        Enter a website URL to crawl and generate{" "}
        <code>llms.txt</code> and <code>llms-full.txt</code>.
      </p>

      <UrlForm onSubmit={handleSubmit} disabled={loading} />

      {loading && <Loader />}

      {error && (
        <div
          style={{
            marginTop: "1rem",
            padding: "0.75rem 1rem",
            borderRadius: "6px",
            backgroundColor: "#ffe6e6",
            color: "#a00",
            fontSize: "0.9rem",
          }}
        >
          {error}
        </div>
      )}

      {(llmsTxt || llmsFullTxt) && (
        <div style={{ marginTop: "2rem" }}>
          <ResultsTabs llmsTxt={llmsTxt} llmsFullTxt={llmsFullTxt} />
        </div>
      )}
    </div>
  );
}
