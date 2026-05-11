export default function Loading() {
  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "16px",
        background: "var(--background)",
      }}
    >
      <div
        className="logo-glow"
        style={{ fontSize: "32px", fontWeight: "900" }}
      >
        App
      </div>
      <div
        style={{
          width: "200px",
          height: "2px",
          background: "rgba(255, 255, 255, 0.1)",
          borderRadius: "99px",
          overflow: "hidden",
          position: "relative",
        }}
      >
        <div
          className="shimmer"
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "50%",
            height: "100%",
            background: "var(--primary)",
            boxShadow: "0 0 15px var(--primary)",
          }}
        />
      </div>
      <div
        style={{
          fontSize: "12px",
          color: "var(--text-secondary)",
          fontFamily: "monospace",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
        }}
      >
        Synchronizing Neural Link...
      </div>
    </div>
  );
}
