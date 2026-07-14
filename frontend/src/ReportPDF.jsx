import {
    Document, Page, Text, View, StyleSheet, Image,
    Svg, Polygon, Line, Circle
} from "@react-pdf/renderer";

const DARK = "#1e3a5f";
const TEAL = "#0d9488";
const BLUE = "#2563eb";
const GREEN = "#16a34a";
const RED = "#dc2626";
const AMBER = "#d97706";
const PURPLE = "#7c3aed";
const GRAY = "#6b7280";
const LGRAY = "#f3f4f6";
const WHITE = "#ffffff";
const LOGO = "http://localhost:5173/logo.png";

const F = {
    xs: 8, sm: 9.5, md: 11, lg: 14, xl: 18, xxl: 24, hero: 30,
};

const s = StyleSheet.create({
    page: {
        fontFamily: "Helvetica", fontSize: F.sm, color: "#1e293b",
        paddingBottom: 44, backgroundColor: WHITE,
    },
    pageHeader: {
        flexDirection: "row", justifyContent: "space-between", alignItems: "center",
        borderBottom: "1.5px solid #e5e7eb",
        marginHorizontal: 24, marginTop: 18, marginBottom: 14, paddingBottom: 10,
    },
    phLogo: { flexDirection: "row", alignItems: "center", gap: 7 },
    phLogoImg: { width: 26, height: 26 },
    phLogoTxt: { fontSize: F.sm, fontFamily: "Helvetica-Bold", color: DARK },
    phRight: { fontSize: F.xs, color: GRAY },
    body: { paddingHorizontal: 24 },

    zone: { marginBottom: 14 },
    zoneBar: {
        backgroundColor: DARK, paddingVertical: 8, paddingHorizontal: 14,
        flexDirection: "row", justifyContent: "space-between", alignItems: "center",
    },
    zoneTtl: { color: WHITE, fontSize: F.sm, fontFamily: "Helvetica-Bold", letterSpacing: 0.5 },
    zonePri: { fontSize: F.xs, color: "#93c5fd" },
    zoneBody: { border: "1px solid #d1d5db", borderTop: 0, padding: "14 14" },

    bul: { flexDirection: "row", marginBottom: 6, alignItems: "flex-start" },
    bulDot: { width: 7, height: 7, backgroundColor: TEAL, borderRadius: 1, marginTop: 3, marginRight: 8, flexShrink: 0 },
    bulTxt: { flex: 1, fontSize: F.sm, lineHeight: 1.65, color: "#374151" },

    statBox: { flex: 1, alignItems: "center", padding: "6 4" },
    statVal: { fontSize: F.xxl, fontFamily: "Helvetica-Bold", color: DARK },
    statLbl: { fontSize: F.xs, color: GRAY, marginTop: 3 },
    statSub: { fontSize: F.xs, color: TEAL, marginTop: 2 },

    rankRow: { flexDirection: "row", gap: 10, marginBottom: 12 },
    rankBox: { flex: 1, backgroundColor: LGRAY, borderRadius: 5, padding: "14 10", alignItems: "center" },
    rankNum: { fontSize: F.hero, fontFamily: "Helvetica-Bold", color: TEAL },
    rankLbl: { fontSize: F.xs, color: GRAY, marginTop: 4 },
    rankPct: { fontSize: F.md, fontFamily: "Helvetica-Bold", color: BLUE, marginTop: 5 },
    rankChg: { fontSize: F.xs, color: GRAY, marginTop: 3 },

    quadGrid: { flexDirection: "row", flexWrap: "wrap", gap: 6, width: 220 },
    quadBox: { width: 105, padding: "10 11", borderRadius: 4 },
    quadTtl: { fontSize: F.sm, fontFamily: "Helvetica-Bold", marginBottom: 5 },
    quadNum: { fontSize: 26, fontFamily: "Helvetica-Bold" },
    quadSub: { fontSize: F.xs, color: GRAY, marginTop: 3 },

    mRow: { flexDirection: "row", alignItems: "center", marginBottom: 7 },
    mLbl: { width: 120, fontSize: F.sm, textAlign: "right", paddingRight: 9, color: "#374151" },
    mTrack: { flex: 1, height: 14, backgroundColor: "#e5e7eb", borderRadius: 3 },
    mFill: { height: 14, borderRadius: 3 },
    mPct: { width: 36, fontSize: F.sm, fontFamily: "Helvetica-Bold", paddingLeft: 7 },

    tblHead: { flexDirection: "row", backgroundColor: DARK, padding: "6 10" },
    tblHC: { fontSize: F.sm, fontFamily: "Helvetica-Bold", color: WHITE },
    tblRow: { flexDirection: "row", borderBottom: "1px solid #f3f4f6", padding: "7 10" },
    tblC: { fontSize: F.sm, color: "#374151", lineHeight: 1.5 },

    rtGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
    rtTile: { width: "48%", borderRadius: 4, padding: "10 11" },
    rtSubj: { fontSize: F.md, fontFamily: "Helvetica-Bold", marginBottom: 3 },
    rtLbl: { fontSize: F.xs, marginBottom: 5 },
    rtAct: { fontSize: F.xs, color: "#374151" },

    recCard: { borderRadius: 4, padding: "10 12", marginBottom: 8 },
    recTtl: { fontSize: F.md, fontFamily: "Helvetica-Bold", marginBottom: 4 },
    recBdy: { fontSize: F.sm, color: "#374151", lineHeight: 1.55 },

    z8Row: { flexDirection: "row", gap: 8, marginBottom: 14 },
    z8Box: { flex: 1, backgroundColor: LGRAY, borderRadius: 4, padding: "12 8", alignItems: "center" },
    z8Val: { fontSize: F.xl, fontFamily: "Helvetica-Bold" },
    z8Lbl: { fontSize: F.xs, color: "#374151", textAlign: "center", marginTop: 5 },
    z8Sub: { fontSize: F.xs, color: GRAY, textAlign: "center", marginTop: 3 },

    sumSec: { borderLeft: "4px solid #0d9488", paddingLeft: 14, marginBottom: 18 },
    sumTtl: { fontSize: F.lg, fontFamily: "Helvetica-Bold", marginBottom: 10, color: DARK },

    footer: {
        position: "absolute", bottom: 16, left: 24, right: 24,
        flexDirection: "row", justifyContent: "space-between",
        borderTop: "1px solid #e5e7eb", paddingTop: 6,
    },
    ftxt: { fontSize: F.xs, color: GRAY },
});

// ── helpers ────────────────────────────────────────────────────────────────
const suffix = n => n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th";
const topPct = pct => `Top ${Math.max(1, Math.round(100 - pct))}%`;
const mColor = pct => pct < 35 ? RED : pct < 60 ? AMBER : GREEN;
const rtColors = l => l === "Good to Go" ? { bg: "#f0fdf4", text: GREEN }
    : l === "Need Practice" ? { bg: "#fffbeb", text: AMBER }
        : { bg: "#fff1f2", text: RED };
const rcColors = c => c === "CRITICAL" ? { bg: "#fff1f2", border: RED }
    : c === "IMPROVE" ? { bg: "#fffbeb", border: AMBER }
        : { bg: "#f0fdf4", border: GREEN };

// ── reusable components ────────────────────────────────────────────────────
function B({ text }) {
    return (
        <View style={s.bul}>
            <View style={s.bulDot} />
            <Text style={s.bulTxt}>{String(text || "")}</Text>
        </View>
    );
}

// Fixed Header and Footer are inlined directly below

function Zone({ title, priority, children }) {
    return (
        <View style={s.zone}>
            <View style={s.zoneBar}>
                <Text style={s.zoneTtl}>{title}</Text>
                {priority && <Text style={s.zonePri}>{priority}</Text>}
            </View>
            <View style={s.zoneBody}>{children}</View>
        </View>
    );
}

// ── SVG Radar Chart ────────────────────────────────────────────────────────
function RadarChart({ data, size = 220 }) {
    if (!data || data.length === 0) return null;

    const cx = size / 2;
    const cy = size / 2;
    const r = size * 0.36;
    const n = data.length;

    const angle = i => (i * 2 * Math.PI / n) - Math.PI / 2;
    const pt = (val, i) => {
        const a = angle(i);
        const dist = (val / 100) * r;
        return { x: cx + dist * Math.cos(a), y: cy + dist * Math.sin(a) };
    };
    const polyPts = key =>
        data.map((d, i) => { const p = pt(d[key], i); return `${p.x},${p.y}`; }).join(" ");
    const labelPt = i => {
        const a = angle(i);
        return { x: cx + (r + 18) * Math.cos(a), y: cy + (r + 18) * Math.sin(a) };
    };

    return (
        <Svg width={size} height={size}>
            {/* Grid rings */}
            {[0.25, 0.5, 0.75, 1].map((frac, li) => (
                <Polygon
                    key={li}
                    points={data.map((_, i) => { const p = pt(frac * 100, i); return `${p.x},${p.y}`; }).join(" ")}
                    fill="none" stroke="#e5e7eb" strokeWidth="0.8"
                />
            ))}
            {/* Axis lines */}
            {data.map((_, i) => {
                const p = pt(100, i);
                return <Line key={i} x1={cx} y1={cy} x2={p.x} y2={p.y} stroke="#d1d5db" strokeWidth="0.8" />;
            })}
            {/* Topper */}
            <Polygon points={polyPts("topper")} fill={PURPLE} fillOpacity="0.08" stroke={PURPLE} strokeWidth="1.2" />
            {/* Class avg */}
            <Polygon points={polyPts("class_avg")} fill={GREEN} fillOpacity="0.12" stroke={GREEN} strokeWidth="1.5" />
            {/* You */}
            <Polygon points={polyPts("you")} fill={BLUE} fillOpacity="0.25" stroke={BLUE} strokeWidth="2" />
            {/* Dots — You */}
            {data.map((d, i) => {
                const p = pt(d.you, i);
                return <Circle key={i} cx={p.x} cy={p.y} r="3.5" fill={BLUE} />;
            })}
            {/* Labels */}
            {data.map((d, i) => {
                const lp = labelPt(i);
                const a = angle(i);
                const anchor = Math.cos(a) > 0.1 ? "start" : Math.cos(a) < -0.1 ? "end" : "middle";
                return (
                    <Text key={i} x={lp.x} y={lp.y} fontSize="9"
                        fontFamily="Helvetica-Bold" fill={DARK} textAnchor={anchor}>
                        {d.subject}
                    </Text>
                );
            })}
        </Svg>
    );
}

// ── main export ────────────────────────────────────────────────────────────
export function ReportPDF({ data }) {
    const {
        overview: ov, rank: rk, quadrant: qd, by_subject,
        mastery, radar, subject_ratings, recommendations,
        narrative: nr,
    } = data;

    // zone4_table comes from Groq (AI-generated per-topic status/focus),
    // zone4 is the rule-based fallback — use whichever is available.
    const topicTableRows = nr.zone4_table || nr.zone4 || [];

    const date = new Date().toLocaleDateString("en-IN", { month: "short", year: "numeric" });

    return (
        <Document>

            {/* ══════════════════════════════════════════════════════════
                COVER PAGE
            ══════════════════════════════════════════════════════════ */}
            <Page size="A4" style={s.page}>
                <View style={{ backgroundColor: DARK, height: 16 }} />

                <View style={{ alignItems: "center", marginTop: 64, marginBottom: 28 }}>
                    <Image src={LOGO} style={{ width: 120, height: 120, marginBottom: 18 }} />
                    <Text style={{ fontSize: 18, fontFamily: "Helvetica-Bold", color: DARK }}>
                        IntellectaFlow LLP
                    </Text>
                </View>

                <View style={{
                    backgroundColor: DARK, marginHorizontal: 32, padding: "36 40",
                    borderRadius: 6, marginBottom: 44, alignItems: "center",
                }}>
                    <Text style={{ color: WHITE, fontSize: 28, fontFamily: "Helvetica-Bold", marginBottom: 10 }}>
                        Student Analytics Report
                    </Text>
                    <Text style={{ color: "#93c5fd", fontSize: 15 }}>Enhanced Metrics Dashboard</Text>
                </View>

                <View style={{ marginHorizontal: 60, backgroundColor: LGRAY, padding: "22 28", borderRadius: 6 }}>
                    {[
                        ["Student", ov.student_name],
                        //["Subject", `${ov.course_code} · ${ov.course_name}`],
                        ["Batch", `B.Tech ${ov.branch} · ${ov.section} · ${new Date().getFullYear()}`],
                        ["Report Generated", date],
                    ].map(([l, v]) => (
                        <View key={l} style={{ flexDirection: "row", marginBottom: 16 }}>
                            <Text style={{ width: 140, fontSize: F.sm, color: GRAY }}>{l}</Text>
                            <Text style={{ fontSize: F.md, fontFamily: "Helvetica-Bold" }}>{v}</Text>
                        </View>
                    ))}
                </View>

                <View style={{ alignItems: "center", marginTop: 50 }}>
                    <Text style={{ fontSize: F.sm, fontFamily: "Helvetica-Bold", letterSpacing: 1, marginBottom: 6 }}>
                        CONFIDENTIAL DOCUMENT
                    </Text>
                    <Text style={{ fontSize: F.xs, color: GRAY, fontStyle: "italic" }}>
                        This report is intended for the named faculty and authorized personnel only.
                    </Text>
                </View>

                <View style={{ backgroundColor: DARK, height: 16, position: "absolute", bottom: 0, left: 0, right: 0 }} />
            </Page>

            {/* ══════════════════════════════════════════════════════════
                CONTENT PAGES (Dynamic Flow)
            ══════════════════════════════════════════════════════════ */}
            <Page size="A4" style={s.page} wrap>
                {/* Fixed Header */}
                <View style={s.pageHeader} fixed>
                    <View style={s.phLogo}>
                        <Image src={LOGO} style={s.phLogoImg} />
                        <Text style={s.phLogoTxt}>IntellectaFlow LLP</Text>
                    </View>
                    <Text style={s.phRight}>{ov.student_name}  ·  {ov.course_code} · {ov.course_name}</Text>
                </View>

                {/* Fixed Footer */}
                <View style={s.footer} fixed>
                    <Text style={s.ftxt}>TestArena Student Report - [Date]</Text>
                    <Text style={s.ftxt} render={({ pageNumber }) => `Page ${pageNumber}`} />
                </View>

                <View style={s.body}>

                    <Text style={{ fontSize: 20, fontFamily: "Helvetica-Bold", color: BLUE, textAlign: "center", marginBottom: 6 }}>
                        Overall Summary
                    </Text>
                    <Text style={{ fontSize: F.sm, color: GRAY, textAlign: "center", marginBottom: 20, fontStyle: "italic" }}>
                        {Array.isArray(nr.summary) ? nr.summary[0] : (nr.summary || "")}
                    </Text>

                    {/* Overall Performance */}
                    <View style={s.sumSec}>
                        <Text style={s.sumTtl}>Overall Performance</Text>
                        <View style={{ border: "1px solid #e5e7eb", borderRadius: 4, padding: "14 12" }}>
                            <View style={{ flexDirection: "row", borderBottom: "1px solid #e5e7eb", paddingBottom: 12, marginBottom: 10 }}>
                                {[
                                    { l: "Composite Score", v: `${ov.composite_score.toFixed(0)}/100`, s: "+8 from last test", c: DARK },
                                    { l: "Tests Taken", v: ov.tests_taken, s: `Attempt rate ${ov.attempt_rate}%`, c: DARK },
                                    { l: "Avg Score", v: `${ov.avg_score_pct}%`, s: `Class avg: ${ov.class_avg.toFixed(0)}%`, c: TEAL },
                                    { l: "Best Score", v: `${ov.best_score_pct}%`, s: ov.course_code, c: GREEN },
                                ].map(({ l, v, s: sub, c }) => (
                                    <View key={l} style={s.statBox}>
                                        <Text style={[s.statVal, { color: c }]}>{v}</Text>
                                        <Text style={s.statLbl}>{l}</Text>
                                        <Text style={s.statSub}>{sub}</Text>
                                    </View>
                                ))}
                            </View>
                            <View style={{ backgroundColor: LGRAY, borderRadius: 3, padding: "8 12" }}>
                                <Text style={{ fontSize: F.sm }}>
                                    <Text style={{ fontFamily: "Helvetica-Bold" }}>Performance Level: </Text>
                                    <Text style={{ color: AMBER }}>{ov.band_label}</Text>
                                    {"  |  Class avg: "}{ov.class_avg.toFixed(0)}
                                    {"  ·  Branch topper: "}{ov.branch_topper.toFixed(0)}
                                    {"  ·  Top "}{rk ? Math.max(1, Math.round(100 - rk.class_percentile)) : "—"}{"% of class"}
                                </Text>
                            </View>
                        </View>
                    </View>

                    {/* Rank & Percentile */}
                    <View style={s.sumSec}>
                        <Text style={s.sumTtl}>Rank & Percentile</Text>
                        <View style={{ border: "1px solid #e5e7eb", borderRadius: 4, padding: "14 12" }}>
                            {rk && (
                                <View style={s.rankRow}>
                                    {[
                                        { l: "Class Rank", r: rk.class_rank, p: rk.class_percentile, ch: "+ 2 from last test" },
                                        { l: "Branch Rank", r: rk.branch_rank, p: rk.branch_percentile, ch: "+ 4 from last test" },
                                        { l: "Platform Rank", r: rk.platform_rank, p: rk.platform_percentile, ch: "No change" },
                                    ].map(({ l, r, p, ch }) => (
                                        <View key={l} style={s.rankBox}>
                                            <Text style={s.rankNum}>{r}{suffix(r)}</Text>
                                            <Text style={s.rankLbl}>{l}</Text>
                                            <Text style={s.rankPct}>{topPct(p)}</Text>
                                            <Text style={s.rankChg}>{ch}</Text>
                                        </View>
                                    ))}
                                </View>
                            )}
                            {(nr.zone2 || []).slice(0, 2).map((t, i) => <B key={i} text={t} />)}
                        </View>
                    </View>

                    {/* Score Trend & Consistency */}
                    <View style={s.sumSec}>
                        <Text style={s.sumTtl}>Score Trend & Consistency</Text>
                        <View style={{ border: "1px solid #e5e7eb", borderRadius: 4, padding: "14 12" }}>
                            <View style={{ flexDirection: "row", marginBottom: 10 }}>
                                {[
                                    { v: `${ov.consistency_score.toFixed(0)}/100`, l: "Consistency Score", s: `Varies ±${Math.round(ov.consistency_score * 0.15)} pts`, c: AMBER },
                                    { v: `${ov.streak_count}`, l: "Tests in a Row", s: "1 more to hit milestone", c: GREEN },
                                    { v: `-${ov.neg_marks_lost.toFixed(0)}`, l: "Points Lost (Neg. Mark)", s: `Avoid guessing on ${ov.course_code}`, c: RED },
                                    { v: `${ov.avg_time_per_question}s`, l: "Avg Time / Question", s: "Class avg 2.1 min", c: BLUE },
                                ].map(({ v, l, s: sub, c }) => (
                                    <View key={l} style={[s.statBox, { border: "1px solid #e5e7eb", borderRadius: 4, margin: 4, padding: "12 8" }]}>
                                        <Text style={[s.statVal, { color: c, fontSize: F.xl }]}>{v}</Text>
                                        <Text style={s.statLbl}>{l}</Text>
                                        <Text style={[s.statSub, { color: GRAY, fontStyle: "italic" }]}>{sub}</Text>
                                    </View>
                                ))}
                            </View>
                            <Text style={{ fontSize: F.sm }}>
                                <Text style={{ fontFamily: "Helvetica-Bold" }}>Trend Insight: </Text>
                                {(nr.zone8 || [])[0] || ""}
                            </Text>
                        </View>
                    </View>
                </View>

                <View style={s.body}>
                    <Text style={{ fontSize: 20, fontFamily: "Helvetica-Bold", textAlign: "center", marginBottom: 22 }}>
                        Table of Contents
                    </Text>
                    <View style={{ border: "1px solid #374151", borderRadius: 4 }}>
                        <View style={{ flexDirection: "row", backgroundColor: DARK, padding: "10 14" }}>
                            {[["Section", 52], ["Title", 120], ["Description", null], ["Page", 32]].map(([h, w]) => (
                                <Text key={h} style={[
                                    { fontSize: F.sm, fontFamily: "Helvetica-Bold", color: WHITE },
                                    w ? { width: w } : { flex: 1 },
                                    h === "Page" ? { textAlign: "right" } : {},
                                ]}>{h}</Text>
                            ))}
                        </View>
                        {[
                            ["1", "Summary", "Quick overview of performance, strengths, and improvement areas.", "i"],
                            ["2", "Table of Contents", "Easy guide to navigate the report.", "ii"],
                            ["3", "Overall Performance Score", "Snapshot of scores, participation, and overall achievement.", "iii"],
                            ["4", "Speed vs Accuracy Matrix", "Shows how effectively the student balances speed and accuracy.", "iii"],
                            ["5", "Rank & Percentile", "Comparison with classmates, branch peers, and platform learners.", "iii"],
                            ["6", "Topic Mastery Heatmap", "Highlights strong topics and areas needing improvement.", "iv"],
                            ["7", "Peer Comparison Radar", "Visual comparison with class averages and top performers.", "v"],
                            ["8", "Score Trend & Consistency", "Tracks progress, consistency, and score trends over time.", "vi"],
                        ].map(([sec, title, desc, pg], i) => (
                            <View key={sec} style={{
                                flexDirection: "row", padding: "14 14", alignItems: "center",
                                backgroundColor: i % 2 === 0 ? WHITE : LGRAY,
                                borderTop: "1px solid #e5e7eb",
                            }}>
                                <View style={{ width: 52, alignItems: "flex-start" }}>
                                    <View style={{ backgroundColor: DARK, borderRadius: 3, paddingVertical: 4, paddingHorizontal: 9 }}>
                                        <Text style={{ fontSize: F.sm, fontFamily: "Helvetica-Bold", color: WHITE }}>{sec}</Text>
                                    </View>
                                </View>
                                <Text style={{ width: 120, fontSize: F.sm, fontFamily: "Helvetica-Bold" }}>{title}</Text>
                                <Text style={{ flex: 1, fontSize: F.xs, color: GRAY, lineHeight: 1.6 }}>{desc}</Text>
                                <Text style={{ width: 32, fontSize: F.sm, textAlign: "right" }}>{pg}</Text>
                            </View>
                        ))}
                    </View>
                </View>

                <View style={s.body} break>

                    {/* ZONE 1 */}
                    <Zone title="ZONE 1 — OVERALL PERFORMANCE SCORE" priority="MUST HAVE">
                        <View style={{ flexDirection: "row", border: "1px solid #e5e7eb", borderRadius: 4, padding: "10 10", marginBottom: 10 }}>
                            {/* Circular gauge */}
                            <View style={{ alignItems: "center", justifyContent: "center", marginRight: 14, width: 80 }}>
                                <View style={{ width: 68, height: 68, borderRadius: 34, border: `6px solid ${BLUE}`, alignItems: "center", justifyContent: "center" }}>
                                    <Text style={{ fontSize: 15, fontFamily: "Helvetica-Bold", color: DARK }}>
                                        {ov.composite_score.toFixed(0)}%
                                    </Text>
                                </View>
                                <View style={{ backgroundColor: AMBER, borderRadius: 10, paddingVertical: 3, paddingHorizontal: 10, marginTop: 6 }}>
                                    <Text style={{ fontSize: 7, fontFamily: "Helvetica-Bold", color: WHITE }}>{ov.band_label}</Text>
                                </View>
                            </View>
                            <View style={{ flex: 1 }}>
                                <View style={{ flexDirection: "row", borderBottom: "1px solid #e5e7eb", paddingBottom: 8, marginBottom: 8 }}>
                                    {[
                                        { l: "Composite score", v: `${ov.composite_score.toFixed(0)}/100`, s: "+8 from last test", c: DARK },
                                        { l: "Tests taken", v: ov.tests_taken, s: `Attempt rate ${ov.attempt_rate}%`, c: DARK },
                                        { l: "Avg score", v: `${ov.avg_score_pct}%`, s: `Class avg: ${ov.class_avg.toFixed(0)}%`, c: TEAL },
                                        { l: "Best score", v: `${ov.best_score_pct}%`, s: ov.course_code, c: GREEN },
                                    ].map(({ l, v, s: sub, c }) => (
                                        <View key={l} style={{ flex: 1, alignItems: "center" }}>
                                            <Text style={{ fontSize: 7, color: GRAY, marginBottom: 2 }}>{l}</Text>
                                            <Text style={{ fontSize: F.md, fontFamily: "Helvetica-Bold", color: c }}>{v}</Text>
                                            <Text style={{ fontSize: 7, color: TEAL, marginTop: 2 }}>{sub}</Text>
                                        </View>
                                    ))}
                                </View>
                                <Text style={{ fontSize: F.xs, color: GRAY }}>
                                    {"Class avg: "}{ov.class_avg.toFixed(0)}
                                    {"  ·  Branch topper: "}{ov.branch_topper.toFixed(0)}
                                    {"  ·  You are in the top "}{rk ? Math.max(1, Math.round(100 - rk.class_percentile)) : "—"}{"% of your class"}
                                </Text>
                            </View>
                        </View>
                        {(nr.zone1 || []).map((t, i) => <B key={i} text={t} />)}
                    </Zone>

                    {/* ZONE 2 */}
                    <Zone title="ZONE 2 — RANK & PERCENTILE" priority="MUST HAVE">
                        {rk && (
                            <View style={[s.rankRow, { marginBottom: 10 }]}>
                                {[
                                    { l: "Class rank", r: rk.class_rank, p: rk.class_percentile, ch: "+ 2 from last test" },
                                    { l: "Branch rank", r: rk.branch_rank, p: rk.branch_percentile, ch: "+ 4 from last test" },
                                    { l: "Platform rank", r: rk.platform_rank, p: rk.platform_percentile, ch: "No change" },
                                ].map(({ l, r, p, ch }) => (
                                    <View key={l} style={[s.rankBox, { padding: "10 8" }]}>
                                        <Text style={[s.rankNum, { fontSize: F.xxl }]}>{r}{suffix(r)}</Text>
                                        <Text style={s.rankLbl}>{l}</Text>
                                        <Text style={[s.rankPct, { fontSize: F.sm }]}>{topPct(p)}</Text>
                                        <Text style={s.rankChg}>{ch}</Text>
                                    </View>
                                ))}
                            </View>
                        )}
                        {(nr.zone2 || []).map((t, i) => <B key={i} text={t} />)}
                    </Zone>

                    {/* ZONE 3 */}
                    <Zone title="ZONE 3 — SPEED VS ACCURACY MATRIX" priority="MUST HAVE — CORE USP">
                        <View style={{ flexDirection: "row", gap: 14 }}>
                            {/* 2×2 quadrant */}
                            <View>
                                <Text style={{ fontSize: F.xs, fontFamily: "Helvetica-Bold", marginBottom: 8 }}>Per-quiz 2x2 quadrant</Text>
                                <View style={[s.quadGrid, { width: 200 }]}>
                                    {[
                                        { k: "fast_correct", l: "Fast & Correct", s: "questions - ideal", bg: "#dcfce7", c: GREEN },
                                        { k: "fast_wrong", l: "Fast & Wrong", s: "questions - rushing", bg: "#fee2e2", c: RED },
                                        { k: "slow_correct", l: "Slow & Correct", s: "questions - careful", bg: "#dbeafe", c: BLUE },
                                        { k: "slow_wrong", l: "Slow & Wrong", s: "questions - struggling", bg: "#fef3c7", c: AMBER },
                                    ].map(({ k, l, s: sub, bg, c }) => (
                                        <View key={k} style={{ width: 95, padding: "7 9", borderRadius: 4, backgroundColor: bg }}>
                                            <Text style={{ fontSize: 7, fontFamily: "Helvetica-Bold", color: c, marginBottom: 3 }}>{l}</Text>
                                            <Text style={{ fontSize: 20, fontFamily: "Helvetica-Bold", color: c }}>{qd[k]}</Text>
                                            <Text style={{ fontSize: 7, color: GRAY, marginTop: 2 }}>{sub}</Text>
                                        </View>
                                    ))}
                                </View>
                                <View style={{ marginTop: 8, padding: "5 7", backgroundColor: LGRAY, borderRadius: 3 }}>
                                    <Text style={{ fontSize: 7, color: "#374151" }}>
                                        {qd.fast_wrong > qd.fast_correct * 0.2
                                            ? `You rush on ${ov.course_code} — ${qd.fast_wrong} fast+wrong. Slow down.`
                                            : "Good balance of speed and accuracy."}
                                    </Text>
                                </View>
                            </View>
                            {/* Speed by subject */}
                            <View style={{ flex: 1 }}>
                                <Text style={{ fontSize: F.xs, fontFamily: "Helvetica-Bold", marginBottom: 8 }}>Speed-accuracy by subject</Text>
                                <View style={{ border: "1px solid #e5e7eb", borderRadius: 4 }}>
                                    <View style={s.tblHead}>
                                        <Text style={[s.tblHC, { flex: 1 }]}>Subject</Text>
                                        <Text style={[s.tblHC, { width: 72, color: "#86efac" }]}>Fast+Correct</Text>
                                        <Text style={[s.tblHC, { width: 72, color: "#fca5a5" }]}>Fast+Wrong</Text>
                                    </View>
                                    {(by_subject || []).map((r, i) => (
                                        <View key={r.subject} style={[s.tblRow, { backgroundColor: i % 2 === 0 ? WHITE : LGRAY }]}>
                                            <Text style={[s.tblC, { flex: 1, fontFamily: "Helvetica-Bold" }]}>{r.subject}</Text>
                                            <Text style={[s.tblC, { width: 72, color: GREEN }]}>{r.fast_correct}</Text>
                                            <Text style={[s.tblC, { width: 72, color: RED }]}>{r.fast_wrong}</Text>
                                        </View>
                                    ))}
                                </View>
                            </View>
                        </View>
                        <View style={{ marginTop: 10 }}>
                            {(nr.zone3 || []).map((t, i) => <B key={i} text={t} />)}
                        </View>
                    </Zone>

                </View>

                <View style={s.body}>
                    <Zone title="ZONE 4 — TOPIC MASTERY HEATMAP" priority="MUST HAVE">

                        {/* Mastery bars */}
                        <View style={{ border: "1px solid #e5e7eb", borderRadius: 4, padding: "14 12", marginBottom: 16 }}>
                            <Text style={{ fontSize: F.sm, fontFamily: "Helvetica-Bold", marginBottom: 12 }}>
                                Chapter-level mastery bars (worst first)
                            </Text>
                            {(mastery || []).map(t => (
                                <View key={t.topic} style={s.mRow}>
                                    <Text style={s.mLbl}>{t.topic}</Text>
                                    <View style={s.mTrack}>
                                        <View style={[s.mFill, { width: `${t.mastery_pct}%`, backgroundColor: mColor(t.mastery_pct) }]} />
                                    </View>
                                    <Text style={[s.mPct, { color: mColor(t.mastery_pct) }]}>{Math.round(t.mastery_pct)}%</Text>
                                </View>
                            ))}
                        </View>

                        {/* Skill rating tiles */}
                        <View style={[s.rtGrid, { marginBottom: 16 }]}>
                            {(subject_ratings || []).map(s2 => {
                                const { bg, text } = rtColors(s2.label);
                                return (
                                    <View key={s2.subject} style={[s.rtTile, { backgroundColor: bg }]}>
                                        <Text style={[s.rtSubj, { color: text }]}>{s2.subject}</Text>
                                        <Text style={[s.rtLbl, { color: text }]}>{s2.label} · {s2.avg_mastery}%</Text>
                                        <Text style={s.rtAct}>{s2.action}</Text>
                                    </View>
                                );
                            })}
                        </View>

                        {/* Per-topic table — prefers AI-generated rows, falls back to rule-based */}
                        <View>
                            <View style={s.tblHead}>
                                <Text style={[s.tblHC, { width: 22, marginRight: 6 }]}>Sl.</Text>
                                <Text style={[s.tblHC, { width: 95 }]}>Topic</Text>
                                <Text style={[s.tblHC, { flex: 1 }]}>Current Status</Text>
                                <Text style={[s.tblHC, { flex: 1 }]}>Improvement Focus</Text>
                            </View>
                            {topicTableRows.map((row, i) => (
                                <View key={i} style={[s.tblRow, { backgroundColor: i % 2 === 0 ? WHITE : LGRAY }]}>
                                    <Text style={[s.tblC, { width: 22, marginRight: 6, color: GRAY }]}>{i + 1}</Text>
                                    <Text style={[s.tblC, { width: 95, fontFamily: "Helvetica-Bold" }]}>{row.topic}</Text>
                                    <Text style={[s.tblC, { flex: 1 }]}>{row.status}</Text>
                                    <Text style={[s.tblC, { flex: 1 }]}>{row.focus}</Text>
                                </View>
                            ))}
                        </View>

                        {/* Zone 4 summary bullets — Groq-generated or rule-based */}
                        <View style={{ marginTop: 12 }}>
                            {(nr.zone4_summary || []).map((t, i) => <B key={i} text={t} />)}
                        </View>
                    </Zone>
                </View>

                <View style={s.body}>
                    <Zone title="ZONE 5 — PEER COMPARISON RADAR" priority="HIGH PRIORITY">
                        <Text style={{ fontSize: F.sm, fontFamily: "Helvetica-Bold", marginBottom: 8 }}>
                            You vs class avg vs branch topper
                        </Text>

                        {/* Legend */}
                        <View style={{ flexDirection: "row", gap: 16, marginBottom: 14 }}>
                            {[["You", BLUE], ["Class avg", GREEN], ["Branch topper", PURPLE]].map(([l, c]) => (
                                <View key={l} style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                                    <View style={{ width: 14, height: 14, backgroundColor: c, borderRadius: 2 }} />
                                    <Text style={{ fontSize: F.sm, color: GRAY }}>{l}</Text>
                                </View>
                            ))}
                        </View>

                        {/* Radar + data table side by side */}
                        <View style={{ flexDirection: "row", gap: 16, marginBottom: 14 }}>
                            <View style={{ alignItems: "center" }}>
                                <RadarChart data={radar} size={240} />
                            </View>
                            <View style={{ flex: 1 }}>
                                <View style={{ border: "1px solid #e5e7eb", borderRadius: 4 }}>
                                    <View style={s.tblHead}>
                                        <Text style={[s.tblHC, { width: 55 }]}>Subject</Text>
                                        <Text style={[s.tblHC, { width: 35, color: "#93c5fd" }]}>You</Text>
                                        <Text style={[s.tblHC, { width: 50, color: "#86efac" }]}>Avg</Text>
                                        <Text style={[s.tblHC, { width: 50, color: "#d8b4fe" }]}>Topper</Text>
                                    </View>
                                    {(radar || []).map((r, i) => (
                                        <View key={r.subject} style={[s.tblRow, { backgroundColor: i % 2 === 0 ? WHITE : LGRAY }]}>
                                            <Text style={[s.tblC, { width: 55, fontFamily: "Helvetica-Bold" }]}>{r.subject}</Text>
                                            <Text style={[s.tblC, { width: 35, color: BLUE }]}>{r.you.toFixed(0)}</Text>
                                            <Text style={[s.tblC, { width: 50, color: GREEN }]}>{r.class_avg.toFixed(0)}</Text>
                                            <Text style={[s.tblC, { width: 50, color: PURPLE }]}>{r.topper.toFixed(0)}</Text>
                                        </View>
                                    ))}
                                </View>
                            </View>
                        </View>

                        {/* Per-subject narrative — AI-generated via Groq or rule-based */}
                        {(nr.zone5 || []).map((r, i) => (
                            <View key={i} style={{ marginBottom: 10 }}>
                                <Text style={{ fontSize: F.sm, fontFamily: "Helvetica-Bold", marginBottom: 3 }}>{r.subject}</Text>
                                <B text={r.status} />
                                <B text={r.focus} />
                            </View>
                        ))}
                        {(nr.zone5_summary || []).map((t, i) => <B key={i} text={t} />)}
                    </Zone>
                </View>

                <View style={s.body}>

                    <Zone title="ZONE 7 — ADAPTIVE RECOMMENDATIONS" priority="MUST HAVE">
                        {(recommendations || []).map((r, i) => {
                            const { bg, border } = rcColors(r.category);
                            return (
                                <View key={i} style={[s.recCard, { backgroundColor: bg, borderLeft: `4px solid ${border}` }]}>
                                    <Text style={[s.recTtl, { color: border }]}>{r.topic || "Speed & Accuracy"}</Text>
                                    <Text style={s.recBdy}>{r.evidence_text}</Text>
                                    {r.action_text ? <Text style={[s.recBdy, { color: GRAY, marginTop: 3 }]}>{r.action_text}</Text> : null}
                                </View>
                            );
                        })}
                    </Zone>

                    <Zone title="ZONE 8 — SCORE TREND & CONSISTENCY" priority="HIGH PRIORITY">
                        <View style={s.z8Row}>
                            {[
                                { v: `${ov.consistency_score.toFixed(0)}/100`, l: "Consistency", s: `scores vary ±${Math.round(ov.consistency_score * 0.15)} pts`, c: AMBER },
                                { v: `${ov.streak_count}`, l: "Tests in a Row", s: "1 more to hit milestone", c: GREEN },
                                { v: `-${ov.neg_marks_lost.toFixed(0)} pts`, l: "Lost to wrong answers", s: "(negative marking)", c: RED },
                                { v: `${ov.avg_time_per_question}s`, l: "Avg time/question", s: "class avg 2.1 min", c: BLUE },
                            ].map(({ v, l, s: sub, c }) => (
                                <View key={l} style={s.z8Box}>
                                    <Text style={[s.z8Val, { color: c }]}>{v}</Text>
                                    <Text style={s.z8Lbl}>{l}</Text>
                                    <Text style={s.z8Sub}>{sub}</Text>
                                </View>
                            ))}
                        </View>
                        {(nr.zone8 || []).map((t, i) => <B key={i} text={t} />)}
                    </Zone>

                </View>
            </Page>

        </Document>
    );
}