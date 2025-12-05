import { useState, useEffect, useRef } from "react";
import { crawlSite, checkForUpdates } from "./api";
import UrlForm from "./components/UrlForm";
import ResultsTabs from "./components/ResultsTabs";
import Loader from "./components/Loader";

export default function App() {
  const [llmsTxt, setLlmsTxt] = useState("");
  const [llmsFullTxt, setLlmsFullTxt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentUrl, setCurrentUrl] = useState("");
  const [version, setVersion] = useState(0);
  const [autoUpdateEnabled, setAutoUpdateEnabled] = useState(false);
  const [updateNotification, setUpdateNotification] = useState("");
  const pollIntervalRef = useRef(null);
  const notificationTimeoutRef = useRef(null);

  useEffect(() => {
    if (!currentUrl || !autoUpdateEnabled) {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      return;
    }

    const pollForUpdates = async () => {
      try {
        const data = await checkForUpdates(currentUrl);
        if (data.has_update && data.version > version) {
          console.log(`[Auto-Update] New version ${data.version} available for ${currentUrl}`);
          setLlmsTxt(data.llms_txt || "");
          setLlmsFullTxt(data.llms_full_txt || "");
          setVersion(data.version);
          setUpdateNotification("Content has been updated automatically!");

          if (notificationTimeoutRef.current) {
            clearTimeout(notificationTimeoutRef.current);
          }
          notificationTimeoutRef.current = setTimeout(() => {
            setUpdateNotification("");
          }, 5000);
        }
      } catch (err) {
        console.error("[Auto-Update] Poll error:", err);
      }
    };

    pollIntervalRef.current = setInterval(pollForUpdates, 30000);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [currentUrl, version, autoUpdateEnabled]);

  async function handleSubmit(url) {
    setError("");
    setLoading(true);
    setLlmsTxt("");
    setLlmsFullTxt("");

    try {
      const data = await crawlSite(url);
      setLlmsTxt(data.llms_txt || "");
      setLlmsFullTxt(data.llms_full_txt || "");
      setCurrentUrl(url);
      setVersion(data.version || 1);
      setAutoUpdateEnabled(true);
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

      {updateNotification && (
        <div
          style={{
            marginTop: "1rem",
            padding: "0.75rem 1rem",
            borderRadius: "6px",
            backgroundColor: "#e6f7ff",
            color: "#0066cc",
            fontSize: "0.9rem",
            border: "1px solid #91d5ff",
          }}
        >
          {updateNotification}
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
