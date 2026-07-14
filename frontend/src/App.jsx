import { useEffect, useState } from "react";
import {
  BarChart, Bar, LineChart, Line, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from "recharts";

import { pdf } from "@react-pdf/renderer";
import { ReportPDF } from "./ReportPDF";
import "./App.css"; // Ensure styles are imported

const API = "http://127.0.0.1:8000/api/v1/students";
const STUDENT_ID = "6c4bfdca-cf05-4a81-ba1e-f4ce6f10d271";
const COURSE_ID = "7577eb44-d6dd-44ad-bf89-dfabe5e6c40c";

// ── Custom Tooltip for Recharts ────────────────────────────────────────────
function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <div className="custom-tooltip-label">{label}</div>
        {payload.map((entry, index) => (
          <div key={index} className="custom-tooltip-item" style={{ color: entry.color || entry.fill }}>
            {entry.name}: {entry.value}
          </div>
        ))}
      </div>
    );
  }
  return null;
}

function useFetch(url) {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch(url).then(r => r.json()).then(setData).catch(() => setData(null));
  }, [url]);
  return data;
}

// ── reusable components ────────────────────────────────────────────────────
function ZoneCard({ title, priority, children }) {
  return (
    <div className="zone-card fade-in">
      <div className="zone-header">
        <span className="zone-title">{title}</span>
        {priority && (
          <span className="zone-priority" style={{
            background: priority === "MUST HAVE" ? "var(--accent-teal)" : "var(--accent-purple)",
            color: "#fff"
          }}>{priority}</span>
        )}
      </div>
      <div className="zone-content">{children}</div>
    </div>
  );
}

function StatBox({ label, value, sub, color }) {
  return (
    <div className="stat-box">
      <div className="stat-value" style={{ color: color || "var(--accent-blue)" }}>{value}</div>
      <div className="stat-label">{label}</div>
      {sub && <div className="stat-sub" style={{ color: "var(--accent-teal)" }}>{sub}</div>}
    </div>
  );
}

function BandPill({ label }) {
  const colors = {
    "Excellent": "var(--accent-blue)", "Strong": "var(--accent-green)", "Proficient": "var(--accent-teal)",
    "Developing": "var(--accent-amber)", "Needs Improvement": "var(--accent-red)",
  };
  const color = colors[label] || "var(--text-muted)";
  return (
    <span style={{
      background: color, color: "#fff",
      padding: "4px 14px", borderRadius: 20, fontWeight: 700, fontSize: 14,
      boxShadow: `0 0 12px ${color}`
    }}>{label}</span>
  );
}

function CircularGauge({ value, max = 100 }) {
  const r = 52, cx = 64, cy = 64;
  const pct = Math.max(0, Math.min(value / max, 1));
  const startAngle = 135, sweepAngle = 270;
  const toRad = d => (d * Math.PI) / 180;
  const arcPath = (angle) => {
    const x = cx + r * Math.cos(toRad(angle));
    const y = cy + r * Math.sin(toRad(angle));
    return { x, y };
  };
  const start = arcPath(startAngle);
  const end = arcPath(startAngle + sweepAngle);
  const filled = arcPath(startAngle + sweepAngle * pct);
  const largeArc = sweepAngle * pct > 180 ? 1 : 0;
  const largeArcBg = sweepAngle > 180 ? 1 : 0;

  return (
    <svg width="128" height="128" viewBox="0 0 128 128" style={{ filter: "drop-shadow(0 0 8px rgba(59, 130, 246, 0.4))" }}>
      <path
        d={`M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcBg} 1 ${end.x} ${end.y}`}
        fill="none" stroke="var(--border-subtle)" strokeWidth="10" strokeLinecap="round"
      />
      <path
        d={`M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${filled.x} ${filled.y}`}
        fill="none" stroke="var(--accent-blue)" strokeWidth="10" strokeLinecap="round"
      />
      <text x={cx} y={cy - 6} textAnchor="middle" fontSize="20" fontWeight="800" fill="var(--text-main)">
        {value}
      </text>
      <text x={cx} y={cx + 12} textAnchor="middle" fontSize="11" fill="var(--text-muted)">/100</text>
    </svg>
  );
}

function masteryColor(pct) {
  if (pct < 35) return "var(--accent-red)";
  if (pct < 60) return "var(--accent-amber)";
  return "var(--accent-green)";
}

function subjectColor(code) {
  const map = { DAA: "var(--accent-blue)", DBMS: "var(--accent-green)", ML: "var(--accent-red)", OS: "var(--accent-amber)", CN: "var(--accent-purple)" };
  return map[code] || "var(--text-muted)";
}

// ── main component ─────────────────────────────────────────────────────────
export default function App() {
  const [isDownloading, setIsDownloading] = useState(false);
  const overview = useFetch(`${API}/${STUDENT_ID}/courses/${COURSE_ID}/overview`);
  const rank = useFetch(`${API}/${STUDENT_ID}/courses/${COURSE_ID}/rank`);
  const quadrant = useFetch(`${API}/${STUDENT_ID}/courses/${COURSE_ID}/speed-accuracy`);
  const bySubject = useFetch(`${API}/${STUDENT_ID}/speed-accuracy-by-subject`);
  const mastery = useFetch(`${API}/${STUDENT_ID}/courses/${COURSE_ID}/topic-mastery`);
  const radar = useFetch(`${API}/${STUDENT_ID}/peer-radar`);
  const subjectRatings = useFetch(`${API}/${STUDENT_ID}/subject-ratings`);
  const recommendations = useFetch(`${API}/${STUDENT_ID}/courses/${COURSE_ID}/recommendations`);
  const allTrends = useFetch(`${API}/${STUDENT_ID}/all-trends`);

  if (!overview) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100vh" }}>
      <div style={{ color: "var(--text-muted)", fontSize: 16, animation: "fadeIn 1s infinite alternate" }}>Loading analytics...</div>
    </div>
  );

  const topPct = (pct) => `Top ${Math.max(1, Math.round(100 - pct))}%`;

  const downloadReport = async () => {
    try {
      setIsDownloading(true);
      const res = await fetch(`${API}/${STUDENT_ID}/courses/${COURSE_ID}/full-report`);
      const data = await res.json();
      const blob = await pdf(<ReportPDF data={data} />).toBlob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${data.overview.student_name.replace(" ", "_")}_Analytics_Report.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to generate PDF:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh" }}>

      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div style={{ 
        background: "var(--bg-header)", 
        backdropFilter: "blur(12px)", 
        WebkitBackdropFilter: "blur(12px)",
        padding: "20px 32px", 
        display: "flex", 
        justifyContent: "space-between", 
        alignItems: "center",
        borderBottom: "1px solid var(--border-subtle)",
        position: "sticky",
        top: 0,
        zIndex: 50
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{
            width: 48, height: 48, background: "linear-gradient(135deg, var(--accent-blue), var(--accent-purple))", 
            borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
            color: "#fff", fontWeight: 800, fontSize: 18,
            boxShadow: "0 0 15px rgba(59,130,246,0.5)"
          }}>
            {overview.student_name.split(" ").map(w => w[0]).join("").slice(0, 2)}
          </div>
          <div>
            <div style={{ color: "var(--text-main)", fontWeight: 800, fontSize: 22, letterSpacing: "0.5px" }}>{overview.student_name}</div>
            <div style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 2 }}>
              {overview.branch} · {overview.section} Section · TestArena Analytics
            </div>
          </div>
        </div>
        <div style={{ textAlign: "right", display: "flex", alignItems: "center", gap: 20 }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "var(--text-muted)", fontSize: 12 }}>Report generated</div>
            <div style={{ color: "var(--text-main)", fontWeight: 700 }}>{new Date().toLocaleDateString("en-IN", { month: "short", year: "numeric" })}</div>
          </div>
          <button onClick={downloadReport} className="btn-download" disabled={isDownloading} style={{ opacity: isDownloading ? 0.8 : 1, cursor: isDownloading ? "wait" : "pointer" }}>
            {isDownloading ? (
              <>
                <svg className="spin-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="2" x2="12" y2="6"></line>
                  <line x1="12" y1="18" x2="12" y2="22"></line>
                  <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                  <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                  <line x1="2" y1="12" x2="6" y2="12"></line>
                  <line x1="18" y1="12" x2="22" y2="12"></line>
                  <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                  <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download Report
              </>
            )}
          </button>
        </div>
      </div>

      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "32px 16px" }}>

        {/* ── Zone 1: Overall Performance ───────────────────────────────── */}
        <ZoneCard title="OVERALL PERFORMANCE SCORE">
          <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
              <CircularGauge value={Math.round(overview.composite_score)} />
              <BandPill label={overview.band_label} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", borderBottom: "1px solid var(--border-subtle)", paddingBottom: 16, marginBottom: 12 }}>
                <StatBox label="Composite score" value={`${overview.composite_score.toFixed(0)}/100`} color="var(--accent-blue)" />
                <StatBox label="Tests taken" value={overview.tests_taken} sub={`Attempt rate ${overview.attempt_rate}%`} color="var(--text-main)" />
                <StatBox label="Avg score" value={`${overview.avg_score_pct}%`} sub={`Class avg: ${overview.class_avg.toFixed(0)}%`} color="var(--accent-teal)" />
                <StatBox label="Best score" value={`${overview.best_score_pct}%`} sub={overview.course_code} color="var(--accent-green)" />
              </div>
              <div style={{ fontSize: 13, color: "var(--text-muted)", paddingTop: 4, display: "flex", gap: 16, justifyContent: "center" }}>
                <span>Class avg: <strong style={{ color: "var(--text-main)" }}>{overview.class_avg.toFixed(0)}</strong></span>
                <span>Branch topper: <strong style={{ color: "var(--text-main)" }}>{overview.branch_topper.toFixed(0)}</strong></span>
                <span>You are in the <strong style={{ color: "var(--accent-teal)" }}>top {rank ? Math.max(1, Math.round(100 - rank.class_percentile)) : "—"}%</strong> of your class</span>
              </div>
            </div>
          </div>
        </ZoneCard>

        {/* ── Zone 3: Rank & Percentile ─────────────────────────────────── */}
        {rank && (
          <ZoneCard title="RANK & PERCENTILE">
            <div style={{ display: "flex", gap: 16 }}>
              {[
                { label: "Class rank", rank: rank.class_rank, pct: rank.class_percentile },
                { label: "Branch rank", rank: rank.branch_rank, pct: rank.branch_percentile },
                { label: "Platform rank", rank: rank.platform_rank, pct: rank.platform_percentile },
              ].map(({ label, rank: r, pct }) => (
                <div key={label} className="stat-box" style={{ background: "rgba(255,255,255,0.03)" }}>
                  <div style={{ fontSize: 42, fontWeight: 900, color: "var(--accent-teal)", textShadow: "0 0 15px rgba(20,184,166,0.3)" }}>
                    {r}{r === 1 ? "st" : r === 2 ? "nd" : r === 3 ? "rd" : "th"}
                  </div>
                  <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 6 }}>{label}</div>
                  <div style={{ fontWeight: 700, color: "var(--accent-blue)" }}>{topPct(pct)}</div>
                </div>
              ))}
            </div>
          </ZoneCard>
        )}

        {/* ── Zone 2: Speed vs Accuracy ─────────────────────────────────── */}
        {quadrant && (
          <ZoneCard title="SPEED VS ACCURACY MATRIX">
            <div style={{ display: "flex", gap: 32 }}>
              {/* 2×2 quadrant */}
              <div style={{ flex: "0 0 auto" }}>
                <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 14, color: "var(--text-main)" }}>Per-quiz 2×2 quadrant</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, width: 300 }}>
                  {[
                    { key: "fast_correct", label: "Fast & Correct", sub: "ideal", border: "var(--accent-green)", color: "var(--accent-green)" },
                    { key: "fast_wrong", label: "Fast & Wrong", sub: "rushing", border: "var(--accent-red)", color: "var(--accent-red)" },
                    { key: "slow_correct", label: "Slow & Correct", sub: "careful", border: "var(--accent-blue)", color: "var(--accent-blue)" },
                    { key: "slow_wrong", label: "Slow & Wrong", sub: "struggling", border: "var(--accent-amber)", color: "var(--accent-amber)" },
                  ].map(({ key, label, sub, border, color }) => (
                    <div key={key} style={{ 
                      background: "rgba(255,255,255,0.02)", borderRadius: 12, padding: "16px",
                      borderTop: `3px solid ${border}`, transition: "transform 0.3s ease" 
                    }} className="stat-box">
                      <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", marginBottom: 8, textTransform: "uppercase" }}>{label}</div>
                      <div style={{ fontSize: 32, fontWeight: 800, color, textShadow: `0 0 10px ${color}` }}>{quadrant[key]}</div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>questions — {sub}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Speed by subject bar chart */}
              {bySubject && (
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 14, color: "var(--text-main)" }}>Speed-accuracy by subject</div>
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart data={bySubject} layout="vertical" barSize={12} margin={{ left: -20 }}>
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border-subtle)" />
                      <XAxis type="number" tick={{ fontSize: 11, fill: "var(--text-muted)" }} stroke="var(--border-subtle)" />
                      <YAxis type="category" dataKey="subject" tick={{ fontSize: 12, fill: "var(--text-main)", fontWeight: 600 }} width={60} stroke="none" />
                      <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(255,255,255,0.05)" }} />
                      <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                      <Bar dataKey="fast_correct" name="Fast+Correct" fill="var(--accent-green)" radius={[0, 4, 4, 0]} />
                      <Bar dataKey="fast_wrong" name="Fast+Wrong" fill="var(--accent-red)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </ZoneCard>
        )}

        {/* ── Zone 4: Topic Mastery Heatmap ─────────────────────────────── */}
        {mastery && (
          <ZoneCard title="TOPIC MASTERY HEATMAP">
            <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 14, color: "var(--text-main)" }}>
              Chapter-level mastery bars (worst first)
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {mastery.map(t => (
                <div key={t.topic} style={{ display: "flex", alignItems: "center", gap: 16, padding: "8px 12px", background: "rgba(255,255,255,0.02)", borderRadius: 8 }}>
                  <div style={{ width: 160, fontSize: 13, textAlign: "right", color: "var(--text-main)", fontWeight: 500 }}>
                    {t.topic}
                  </div>
                  <div style={{ flex: 1, background: "rgba(255,255,255,0.05)", borderRadius: 6, height: 16, position: "relative", overflow: "hidden" }}>
                    <div style={{
                      width: `${t.mastery_pct}%`, height: "100%",
                      background: masteryColor(t.mastery_pct),
                      borderRadius: 6, transition: "width 1s cubic-bezier(0.4, 0, 0.2, 1)",
                      boxShadow: `0 0 10px ${masteryColor(t.mastery_pct)}`
                    }} />
                  </div>
                  <div style={{ width: 40, fontSize: 14, fontWeight: 800, color: masteryColor(t.mastery_pct) }}>
                    {Math.round(t.mastery_pct)}%
                  </div>
                </div>
              ))}
            </div>
          </ZoneCard>
        )}

        {/* ── Zone 5: Peer Comparison Radar ─────────────────────────────── */}
        {radar && radar.length > 0 && (
          <ZoneCard title="PEER COMPARISON RADAR">
            <div style={{ fontWeight: 600, marginBottom: 8, fontSize: 14, color: "var(--text-main)", textAlign: "center" }}>
              You vs class avg vs branch topper
            </div>
            <ResponsiveContainer width="100%" height={380}>
              <RadarChart data={radar} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
                <PolarGrid stroke="var(--border-subtle)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: "var(--text-main)", fontSize: 14, fontWeight: 700 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 11 }} axisLine={false} />
                <Radar name="You" dataKey="you" stroke="var(--accent-blue)" strokeWidth={3} fill="var(--accent-blue)" fillOpacity={0.35} />
                <Radar name="Class avg" dataKey="class_avg" stroke="var(--accent-green)" strokeWidth={2} fill="var(--accent-green)" fillOpacity={0.15} />
                <Radar name="Branch topper" dataKey="topper" stroke="var(--accent-purple)" strokeWidth={2} strokeDasharray="4 4" fill="transparent" />
                <Legend wrapperStyle={{ fontSize: 13 }} />
                <Tooltip content={<CustomTooltip />} />
              </RadarChart>
            </ResponsiveContainer>
          </ZoneCard>
        )}

        {/* ── Zone 6: Skill-wise Performance Rating ─────────────────────── */}
        {subjectRatings && (
          <ZoneCard title="SKILL-WISE PERFORMANCE RATING">
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {subjectRatings.map(s => {
                const isGood = s.label === "Good to Go";
                const isWarn = s.label === "Need Practice";
                const headerColor = isGood ? "var(--accent-green)" : isWarn ? "var(--accent-amber)" : "var(--accent-red)";
                const bg = isGood ? "rgba(16, 185, 129, 0.05)" : isWarn ? "rgba(245, 158, 11, 0.05)" : "rgba(239, 68, 68, 0.05)";
                
                return (
                  <div key={s.subject} style={{ 
                    background: bg, borderRadius: 12, padding: 20, 
                    border: `1px solid ${headerColor}`,
                    boxShadow: `inset 0 0 20px ${bg}`
                  }}>
                    <div style={{ fontWeight: 800, color: headerColor, fontSize: 18, marginBottom: 4 }}>
                      {s.subject}
                    </div>
                    <div style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12, display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ padding: "2px 8px", background: headerColor, color: "#fff", borderRadius: 12, fontSize: 11, fontWeight: 700 }}>
                        {s.label}
                      </span>
                      <span>{s.avg_mastery}% mastery</span>
                    </div>
                    <div style={{ fontSize: 13, color: "var(--text-main)", lineHeight: 1.5 }}>{s.action}</div>
                  </div>
                );
              })}
            </div>
          </ZoneCard>
        )}

        {/* ── Zone 7: Adaptive Recommendations ─────────────────────────── */}
        {recommendations && recommendations.length > 0 && (
          <ZoneCard title="ADAPTIVE RECOMMENDATIONS">
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {recommendations.map((r, i) => {
                const isCritical = r.category === "CRITICAL";
                const isImprove = r.category === "IMPROVE";
                const color = isCritical ? "var(--accent-red)" : isImprove ? "var(--accent-amber)" : "var(--accent-green)";
                const bg = isCritical ? "rgba(239, 68, 68, 0.08)" : isImprove ? "rgba(245, 158, 11, 0.08)" : "rgba(16, 185, 129, 0.08)";
                
                return (
                  <div key={i} style={{
                    background: bg, borderLeft: `6px solid ${color}`,
                    borderRadius: "0 12px 12px 0", padding: "16px 20px",
                    display: "flex", flexDirection: "column", gap: 6,
                    boxShadow: `0 4px 15px rgba(0,0,0,0.1)`
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div style={{ fontWeight: 800, color, fontSize: 16, textShadow: `0 0 8px ${color}` }}>
                        {r.topic ? `${r.topic}` : "Speed & Accuracy"}
                      </div>
                      <span style={{ fontSize: 10, fontWeight: 700, color: "#fff", background: color, padding: "2px 8px", borderRadius: 12 }}>
                        {r.category}
                      </span>
                    </div>
                    <div style={{ fontSize: 14, color: "var(--text-main)", fontWeight: 500 }}>{r.evidence_text}</div>
                    {r.action_text ? (
                      <div style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
                        <strong style={{ color: "var(--text-main)" }}>Action:</strong> {r.action_text}
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </ZoneCard>
        )}

        {/* ── Zone 8: Score Trend & Consistency ────────────────────────── */}
        <ZoneCard title="SCORE TREND & CONSISTENCY">
          {allTrends && allTrends.data && allTrends.data.length > 0 && (
            <>
              <div style={{ fontWeight: 600, marginBottom: 16, fontSize: 14, color: "var(--text-main)" }}>Per-subject score trend</div>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={allTrends.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                  <XAxis dataKey="quiz" tick={{ fontSize: 11, fill: "var(--text-muted)" }} stroke="var(--border-subtle)" />
                  <YAxis domain={[0, 50]} tick={{ fontSize: 11, fill: "var(--text-muted)" }} stroke="none" />
                  <Tooltip content={<CustomTooltip />} cursor={{ stroke: "var(--border-subtle)", strokeWidth: 2 }} />
                  <Legend wrapperStyle={{ fontSize: 13, paddingTop: 10 }} />
                  {(allTrends.subjects || []).map(code => (
                    <Line key={code} type="monotone" dataKey={code}
                      stroke={subjectColor(code)} strokeWidth={3}
                      dot={{ r: 4, strokeWidth: 2, fill: "var(--bg-main)" }} 
                      activeDot={{ r: 6, fill: subjectColor(code), stroke: "#fff" }}
                      connectNulls />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </>
          )}

          {/* Zone 8 stat cards */}
          <div style={{ display: "flex", gap: 16, marginTop: 24 }}>
            {[
              {
                value: `${overview.consistency_score.toFixed(0)}/100`,
                label: "Consistency",
                sub: "scores vary across tests", color: "var(--accent-teal)",
              },
              {
                value: overview.streak_count,
                label: "Tests in a row",
                sub: "consecutive attempts", color: "var(--accent-blue)",
              },
              {
                value: `−${overview.neg_marks_lost.toFixed(0)} pts`,
                label: "Lost to wrong answers",
                sub: "negative marking", color: "var(--accent-red)",
              },
              {
                value: `${overview.avg_time_per_question}s`,
                label: "Avg time / question",
                sub: "all subjects", color: "var(--accent-green)",
              },
            ].map(({ value, label, sub, color }) => (
              <div key={label} className="stat-box" style={{ background: "rgba(255,255,255,0.02)" }}>
                <div style={{ fontSize: 32, fontWeight: 900, color, textShadow: `0 0 15px ${color}` }}>{value}</div>
                <div style={{ fontSize: 13, color: "var(--text-main)", marginTop: 6, fontWeight: 700, textTransform: "uppercase" }}>{label}</div>
                <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{sub}</div>
              </div>
            ))}
          </div>
        </ZoneCard>

        <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: 13, paddingBottom: 32, fontWeight: 500 }}>
          TestArena Student Analytics · Designed with IntellectaFlow
        </div>

      </div>
    </div>
  );
}