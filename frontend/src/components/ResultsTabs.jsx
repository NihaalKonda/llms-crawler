import React, { useState } from "react";
import TextBlock from "./TextBlock";

export default function ResultsTabs({ llmsTxt, llmsFullTxt }) {
  const [activeTab, setActiveTab] = useState("llms");

  const tabs = [
    { id: "llms", label: "llms.txt", filename: "llms.txt", value: llmsTxt },
    {
      id: "llms-full",
      label: "llms-full.txt",
      filename: "llms-full.txt",
      value: llmsFullTxt,
    },
  ];

  const active = tabs.find((t) => t.id === activeTab) || tabs[0];

  return (
    <div>
      <div
        style={{
          display: "flex",
          borderBottom: "1px solid #ddd",
          marginBottom: "0.75rem",
          gap: "0.5rem",
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: "0.4rem 0.8rem",
              border: "none",
              borderBottom:
                activeTab === tab.id ? "2px solid #2563eb" : "2px solid transparent",
              backgroundColor: "transparent",
              cursor: "pointer",
              fontSize: "0.9rem",
              color: activeTab === tab.id ? "#111" : "#666",
              fontWeight: activeTab === tab.id ? 600 : 400,
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <TextBlock
        label={active.label}
        filename={active.filename}
        value={active.value}
      />
    </div>
  );
}