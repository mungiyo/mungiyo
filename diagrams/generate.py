"""Generate the draw.io sources for the profile README diagrams.

    python3 generate.py <output-dir>

Icons are read from ./icons next to this file and embedded as data URIs.
"""
import base64
import os
import sys
from xml.sax.saxutils import quoteattr

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
FONT = "fontFamily=Helvetica;html=0;"
W, STEP = 186, 232
PAL = {
    "src": ("#f5f5f5", "#666666"),
    "ingest": ("#ffe6cc", "#d79b00"),
    "proc": ("#dae8fc", "#6c8ebf"),
    "lake": ("#d5e8d4", "#82b366"),
    "serve": ("#e1d5e7", "#9673a6"),
    "orch": ("#fff2cc", "#d6b656"),
    "ci": ("#f8cecc", "#b85450"),
    "plain": ("#ffffff", "#999999"),
}
ICONS = {
    "postgres": "postgresql.svg", "kafka": "apachekafka.svg", "spark": "apachespark.svg",
    "flink": "apacheflink.svg", "airflow": "apacheairflow-color.svg", "databricks": "databricks.svg",
    "delta": "delta.svg", "k8s": "kubernetes.svg", "argo": "argo.svg", "gha": "githubactions.svg",
    "github": "github.svg", "git": "git.svg", "helm": "helm.svg", "docker": "docker.svg",
    "debezium": "debezium.png", "dbt": "dbt-labs.png", "aws": "aws.png", "slack": "slackhq.png",
    "cosmos": "astronomer.png", "om": "open-metadata.png",
}


def icon_uri(name):
    f = ICONS[name]
    mime = "image/svg+xml" if f.endswith(".svg") else "image/png"
    with open(os.path.join(HERE, "icons", f), "rb") as fh:
        return f"data:{mime},{base64.b64encode(fh.read()).decode()}"


class D:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self.n = 1

    def _id(self):
        self.n += 1
        return f"c{self.n}"

    def _v(self, value, style, x, y, w, h):
        i = self._id()
        self.cells.append(
            f'<mxCell id="{i}" value={quoteattr(value).replace(chr(10), "&#xa;")} style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
        )
        return i

    def icon(self, x, y, name, size=26):
        return self._v("", f"shape=image;aspect=fixed;imageAspect=0;image={icon_uri(name)};", x, y, size, size)

    def node(self, x, y, title, sub="", kind="plain", w=W, h=56, icon=None):
        fill, stroke = PAL[kind]
        if 56 < h <= 80:
            y -= (h - 56) // 2
        pad = 36 if icon else 0
        base = (f"rounded=1;arcSize=14;{FONT}fillColor={fill};strokeColor={stroke};fontStyle=1;fontSize=13;"
                f"fontColor=#1a1a1a;spacingLeft={pad};")
        if sub:
            lines = sub.count("\n") + 1
            block = 18 + 13 * lines
            top = (h - block) // 2
            i = self._v(title, base + f"verticalAlign=top;spacingTop={top - 4};", x, y, w, h)
            self._v(sub, f"text;{FONT}fontSize=10;fontColor=#4d4d4d;align=center;verticalAlign=top;strokeColor=none;"
                         f"fillColor=none;spacing=0;", x + pad + 4, y + top + 17, w - pad - 8, 13 * lines + 2)
        else:
            i = self._v(title, base + "verticalAlign=middle;", x, y, w, h)
        if icon:
            self.icon(x + 12, y + (h - 26) // 2, icon)
        return i

    def group(self, x, y, w, h, title, kind="plain"):
        fill, stroke = PAL[kind]
        st = (f"rounded=1;arcSize=4;{FONT}fillColor={fill};strokeColor={stroke};dashed=1;opacity=45;fontStyle=1;"
              f"fontSize=12;fontColor=#333333;verticalAlign=top;align=left;spacingLeft=10;spacingTop=4;")
        return self._v(title, st, x, y, w, h)

    def text(self, x, y, w, h, value, size=11, color="#333333", bold=False, align="center"):
        st = (f"text;{FONT}fontSize={size};fontColor={color};align={align};verticalAlign=middle;strokeColor=none;"
              f"fillColor=none;fontStyle={1 if bold else 0};")
        return self._v(value, st, x, y, w, h)

    def badge(self, x, y, n):
        st = f"ellipse;{FONT}fillColor=#1f2937;strokeColor=#1f2937;fontColor=#ffffff;fontStyle=1;fontSize=12;aspect=fixed;"
        return self._v(str(n), st, x, y, 24, 24)

    def note(self, x, y, w, h, sections):
        """Dashed box holding (heading, [lines]) sections, left-aligned."""
        box = self._v("", "rounded=1;arcSize=4;fillColor=#ffffff;strokeColor=#bbbbbb;dashed=1;", x, y, w, h)
        cy = y + 10
        for head, lines in sections:
            self._v(head, f"text;{FONT}fontSize=11;fontStyle=1;fontColor=#222222;align=left;verticalAlign=top;"
                          f"strokeColor=none;fillColor=none;spacing=0;", x + 12, cy, w - 20, 14)
            cy += 16
            self._v("\n".join(lines), f"text;{FONT}fontSize=10;fontColor=#444444;align=left;verticalAlign=top;"
                                      f"strokeColor=none;fillColor=none;spacing=0;", x + 12, cy, w - 20, 13 * len(lines) + 2)
            cy += 13 * len(lines) + 9
        return box

    def edge(self, s, t, label="", dashed=False, ex=None, en=None, pts=None, color="#555555"):
        i = self._id()
        st = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;{FONT}endArrow=block;endFill=1;strokeColor={color};"
              f"strokeWidth=1.3;fontSize=10;fontColor=#333333;labelBackgroundColor=#ffffff;")
        if dashed:
            st += "dashed=1;"
        if ex:
            st += f"exitX={ex[0]};exitY={ex[1]};exitDx=0;exitDy=0;"
        if en:
            st += f"entryX={en[0]};entryY={en[1]};entryDx=0;entryDy=0;"
        geo = '<mxGeometry relative="1" as="geometry">'
        if pts:
            geo += '<Array as="points">' + "".join(f'<mxPoint x="{a}" y="{b}"/>' for a, b in pts) + "</Array>"
        geo += "</mxGeometry>"
        self.cells.append(
            f'<mxCell id="{i}" value={quoteattr(label).replace(chr(10), "&#xa;")} style="{st}" edge="1" parent="1" '
            f'source="{s}" target="{t}">{geo}</mxCell>'
        )
        return i

    def save(self, fname):
        model = ('<mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
                 'fold="1" page="0" pageScale="1" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
                 + "".join(self.cells) + "</root></mxGraphModel>")
        with open(os.path.join(OUT, fname), "w") as f:
            f.write(f'<mxfile host="app.diagrams.net"><diagram name={quoteattr(self.name)} id="d1">{model}</diagram></mxfile>')


L, R, T, B = (0, 0.5), (1, 0.5), (0.5, 0), (0.5, 1)
X = [30 + STEP * i for i in range(6)]
H = W / 2

# ---------------------------------------------------------------- overview
d = D("Data platform overview")
d.text(30, 20, 700, 30, "Data platform — from service databases to serving", 18, "#111111", True, "left")
for x, t in zip(X, ["Sources", "Capture", "Land · Stream", "Process", "Lakehouse", "Serve"]):
    d.text(x, 62, W, 20, t.upper(), 10, "#888888", True)
# batch ingestion row
files = d.node(X[0], 100, "APIs · files", "3rd-party systems · storage", "src")
land = d.node(X[1], 100, "S3 landing", "original format · immutable", "ingest", icon="aws")
bronze = d.node(X[2], 100, "Bronze", "Auto Loader · append-only", "lake", icon="databricks")
valid = d.node(X[3], 100, "Validate", "stage checks · then publish", "proc", icon="databricks")
# CDC and event rows
db = d.node(X[0], 220, "Service DBs", "Postgres · MySQL · DocDB", "src", icon="postgres")
ev = d.node(X[0], 460, "App events", "event logs", "src")
dbz = d.node(X[1], 220, "Debezium", "Kafka Connect · custom SMT", "ingest", icon="debezium")
kafka = d.node(X[2], 220, "Kafka", "", "ingest", h=296)
d.icon(X[2] + H - 18, 318, "kafka", 36)
spark = d.node(X[3], 220, "Spark on Kubernetes", "CDC MERGE every 10 min", "proc", icon="spark")
flink = d.node(X[3], 460, "Flink", "real-time feature jobs", "proc", icon="flink")
sink = d.node(X[3], 340, "Iceberg sink", "Kafka Connect · append-only", "ingest", icon="kafka")
raw = d.node(X[4], 220, "Raw layer", "CDC · events · ingested Silver", "lake", icon="databricks")
dw = d.node(X[4], 340, "dbt warehouse", "staging → core → mart", "lake", icon="dbt")
svc = d.node(X[5], 220, "Product services", "CRM · apps", "src")
feach = d.node(X[5], 340, "feach", "feature lookup API", "serve")
pg = d.node(X[5], 460, "Online store", "PostgreSQL", "serve", icon="postgres")
d.edge(files, land, ex=R, en=L)
d.edge(land, bronze, ex=R, en=L)
d.edge(bronze, valid, ex=R, en=L)
d.edge(valid, raw, ex=R, en=T, pts=[(X[4] + H, 128)])
d.edge(db, dbz, ex=R, en=L)
d.edge(dbz, kafka, ex=R, en=(0, 0.095))
d.edge(ev, kafka, ex=R, en=(0, 0.905))
d.edge(kafka, spark, ex=(1, 0.095), en=L)
d.edge(kafka, flink, ex=(1, 0.905), en=L)
d.edge(spark, raw, ex=(1, 0.35), en=(0, 0.35))
d.edge(kafka, sink, ex=R, en=L)
d.edge(sink, raw, ex=(1, 0.25), en=(0, 0.75), pts=[(X[3] + W + 23, 354), (X[3] + W + 23, 262)])
d.edge(raw, dw, ex=B, en=T)
d.edge(dw, pg, ex=B, en=(0, 0.25), pts=[(X[4] + H, 474)])
d.edge(flink, pg, ex=(1, 0.75), en=(0, 0.75))
d.text(X[4] + H + 8, 408, 110, 30, "batch sync\nchanged rows only", 10, "#333333", False, "left")
d.text(X[3] + W + 30, 506, 110, 16, "real-time upsert", 10, "#333333", False, "left")
d.edge(pg, feach, ex=T, en=B)
d.edge(feach, svc, ex=T, en=B)
band = X[5] + W - X[1]
d.node(X[1], 560, "Airflow 3 on Kubernetes", "schedules ingestion · CDC merge · dbt runs · feature sync", "orch", w=band, h=52)
d.icon(X[1] + 44, 573, "airflow")
d.icon(X[1] + 78, 573, "k8s")
d.node(X[1], 626, "CI/CD", "GitHub Actions → ECR · S3 → ArgoCD · git-sync", "ci", w=band, h=52)
d.icon(X[1] + 44, 639, "gha")
d.icon(X[1] + 78, 639, "argo")
d.badge(X[3] - 10, 210, 1)
d.badge(X[4] + W - 14, 210, 2)
d.badge(X[5] - 10, 330, 3)
d.badge(X[4] - 10, 330, 4)
d.badge(X[1] - 10, 550, 5)
d.save("overview.drawio")

# ---------------------------------------------------------------- 1. CDC
d = D("CDC pipeline")
d.text(30, 20, 800, 30, "1 · CDC pipeline — Kafka straight into the lakehouse, no landing layer", 18, "#111111", True, "left")
portal = d.node(X[1], 80, "Self-service portal", "trigger a re-snapshot", "plain")
dag = d.node(X[3], 80, "Airflow DAG", "every 10 min", "orch", icon="airflow")
db = d.node(X[0], 220, "Source DBs", "Postgres · MySQL · DocDB\nWAL / binlog", "src", h=70, icon="postgres")
dbz = d.node(X[1], 220, "Debezium", "Kafka Connect on K8s\ncustom SMT fixes types", "ingest", h=70, icon="debezium")
kafka = d.node(X[2], 220, "Kafka", "one topic per table", "ingest", icon="kafka")
job = d.node(X[3], 220, "Spark CDC job", "Structured Streaming\nforeachBatch MERGE", "proc", h=70, icon="spark")
raw = d.node(X[4], 220, "Raw replicas", "Delta · Unity Catalog\ncatalog-managed", "lake", h=70, icon="databricks")
dw = d.node(X[5], 220, "dbt warehouse", "staging → core → mart", "lake", icon="dbt")
topic = d.node(X[3], 380, "Schema changes", "new table · column · type", "ingest", icon="kafka")
alert = d.node(X[4], 380, "Alert DAG", "", "orch", icon="airflow")
slack = d.node(X[5], 380, "Slack", "", "plain", icon="slack")
d.edge(db, dbz, ex=R, en=L)
d.edge(dbz, kafka, ex=R, en=L)
d.edge(kafka, job, ex=R, en=L)
d.edge(job, raw, ex=R, en=L)
d.edge(raw, dw, ex=R, en=L)
d.edge(portal, dbz, "signal topic →\nincremental snapshot", ex=B, en=T)
d.edge(dag, job, "submit SparkApplication", ex=B, en=T)
d.edge(job, topic, "schema evolution\ntype widening", ex=B, en=T)
d.edge(topic, alert, ex=R, en=L)
d.edge(alert, slack, ex=R, en=L)
d.save("cdc-pipeline.drawio")

# ---------------------------------------------------------------- 2. Ingestion pipeline
d = D("Ingestion pipeline")
d.text(30, 20, 900, 30, "2 · Lakehouse ingestion — every batch source lands the same way", 18, "#111111", True, "left")
d.text(30, 50, 1000, 18, "Write-Audit-Publish: only batches that pass validation reach Silver · one source = one pipeline instance",
       11, "#555555", False, "left")
WI, SI = 196, 262
XI = [30 + SI * i for i in range(5)]
stages = [("Source", "src"), ("S3 landing", "ingest"), ("Bronze", "lake"), ("Validate", "proc"), ("Silver", "lake")]
for x, (t, k) in zip(XI, stages):
    d.group(x - 14, 84, WI + 28, 452, t, k)
src = d.node(XI[0], 129, "Source system", "RDBMS · API · file · event\none source = one instance", "src", w=WI, h=70)
s3 = d.node(XI[1], 129, "S3 landing zone", "original format · immutable\ndate partitions", "ingest", w=WI, h=70, icon="aws")
brz = d.node(XI[2], 129, "Bronze", "b_<table> · Delta\nappend-only · all STRING", "lake", w=WI, h=70, icon="databricks")
stg = d.node(XI[3], 129, "Validate", "s_<table>__stage\ntyped · deduped · checked", "proc", w=WI, h=70, icon="databricks")
slv = d.node(XI[4], 129, "Silver", "s_<table> · Delta\nPK = business grain", "lake", w=WI, h=70, icon="databricks")
NY, NH = 212, 214
n_src = d.note(XI[0], NY, WI, NH, [
    ("Extract modes", ["• Full snapshot", "• Incremental (watermark)", "• CDC (Debezium)",
                       "• 3rd-party system API", "• External storage (GCS)"])])
n_s3 = d.note(XI[1], NY, WI, NH, [
    ("Path", ["s3://<bucket>/landing/", "  <source>/<schema>/<table>/", "  dt=YYYY-MM-DD/"]),
    ("Rules", ["• Original format, as received", "• Never overwritten — the", "  source for replays",
               "• Retention by lifecycle rules", "• Read via UC external location"])])
n_brz = d.note(XI[2], NY, WI, NH, [
    ("Load", ["• Auto Loader (cloudFiles)", "• New files only, checkpointed", "• Every column as STRING —",
              "  no type inference"]),
    ("Meta columns", ["• _ingested_at · _source_file", "• _batch_id"])])
n_stg = d.note(XI[3], NY, WI, NH, [
    ("Prepare — this batch only", ["• Cast STRING → target types", "• Standardise column names",
                                    "• Keep latest row per grain"]),
    ("Checks", ["• Schema: casts, expected cols", "• Unique: one row per grain", "• Not null: PK, required cols",
                "• Row count: Bronze vs stage"]),
    ("Defaults", ["• '__unknown__' · -1 · 1900-01-01"])])
n_slv = d.note(XI[4], NY, WI, NH, [
    ("Publish", ["• Range replace (default):", "  REPLACE WHERE … FROM stage", "• Key MERGE: in a transaction,",
                 "  checked before COMMIT"]),
    ("Grain · PK", ["• One row = one business entity", "• PK NOT NULL + UC primary key"]),
    ("Principle", ["• Always rebuildable from Bronze"])])
fail = d.node(XI[3], 461, "Fail", "quarantine · Slack alert\nSilver left untouched", "ci", w=WI, h=70, icon="slack")
down = d.node(XI[4], 461, "Downstream", "dbt warehouse models", "lake", w=WI, h=70, icon="dbt")
d.edge(src, s3, "extract", ex=R, en=L)
d.edge(s3, brz, "Auto Loader", ex=R, en=L)
d.edge(brz, stg, "stage", ex=R, en=L)
d.edge(stg, slv, "publish", ex=R, en=L)
for a, b in [(src, n_src), (s3, n_s3), (brz, n_brz), (stg, n_stg), (slv, n_slv)]:
    d.edge(a, b, dashed=True, ex=B, en=T, color="#999999")
d.edge(n_stg, fail, ex=B, en=T, color="#b85450")
d.edge(n_slv, down, dashed=True, ex=B, en=T, color="#82b366")
GX1 = XI[4] + WI
TW = (GX1 - 30 - 40) / 3
d.group(16, 556, GX1 - 2, 100, "Shared by every pipeline instance", "plain")
orch = d.node(30, 590, "Orchestration — Airflow", "one DAG per source: land → bronze → validate → silver",
              "orch", w=TW, h=52, icon="airflow")
gov = d.node(30 + TW + 20, 590, "Governance — Unity Catalog", "permissions · lineage · raw_<source>__<schema>",
             "lake", w=TW, h=52, icon="databricks")
obs = d.node(30 + 2 * (TW + 20), 590, "Observability", "run log · check results · Slack on failure",
             "plain", w=TW, h=52, icon="slack")
d.save("ingestion.drawio")

# ---------------------------------------------------------------- 3. feach
d = D("feach feature store")
d.text(30, 20, 800, 30, "3 · feach — feature store: pipelines write, one API reads", 18, "#111111", True, "left")
XF = [30, 262, 510, 776, 1008]
mart = d.node(XF[0], 100, "dbt feature mart", "Databricks · hourly", "lake", icon="dbt")
sync = d.node(XF[1], 100, "Airflow batch sync", "diff two Delta versions\n→ upsert changed rows", "orch", h=70, icon="airflow")
kafka = d.node(XF[0], 240, "Kafka", "CDC topics · app events", "ingest", h=170)
d.icon(XF[0] + H - 16, 268, "kafka", 32)
fl = d.node(XF[1], 240, "Flink jobs", "session cluster\none jar per job · upsert", "proc", h=70, icon="flink")
jdbc = d.node(XF[1], 354, "JDBC sink", "Kafka Connect\nplain table copies", "ingest", h=70, icon="kafka")
d.group(XF[2] - 15, 70, W + 30, 364, "Online store · PostgreSQL", "serve")
d.icon(XF[2] + W - 14, 76, "postgres", 22)
tb = d.node(XF[2], 100, "Batch features", "", "plain")
tr = d.node(XF[2], 240, "Real-time features", "", "plain")
tc = d.node(XF[2], 354, "Raw copies", "joined by a view", "plain")
serving = d.node(XF[3], 240, "feach serving API", "POST /get-features\none round trip to the store", "serve", h=70)
cons = d.node(XF[4], 240, "Product services", "CRM · SDK get_features()", "src")
ui = d.node(XF[1], 490, "feach catalog UI", "author feature contracts", "serve")
meta = d.node(XF[2], 490, "feach meta API", "", "serve")
mdb = d.node(XF[3], 490, "Meta DB", "one per environment", "plain", icon="postgres")
d.edge(mart, sync, ex=R, en=L)
d.edge(sync, tb, ex=R, en=L)
d.edge(kafka, fl, ex=(1, 0.165), en=L)
d.edge(kafka, jdbc, ex=(1, 0.835), en=L)
d.edge(fl, tr, ex=R, en=L)
d.edge(jdbc, tc, ex=R, en=L)
d.edge(tb, serving, ex=R, en=(0.25, 0), pts=[(XF[3] + W * 0.25, 128)])
d.edge(tr, serving, ex=R, en=L)
d.edge(tc, serving, ex=R, en=(0.25, 1), pts=[(XF[3] + W * 0.25, 382)])
d.edge(serving, cons, ex=R, en=L)
d.edge(ui, meta, ex=R, en=L)
d.edge(meta, mdb, ex=R, en=L)
d.edge(mdb, serving, "contracts", dashed=True, ex=T, en=(0.6, 1))
d.save("feach.drawio")

# ---------------------------------------------------------------- 3. dbt CI/CD
d = D("dbt CI/CD")
d.text(30, 20, 900, 30, "4 · dbt CI/CD — one commit SHA names both the image and the DAG graph", 18, "#111111", True, "left")
XC = [50 + STEP * i for i in range(5)]
GW = XC[4] + W + 20 - 30
d.group(30, 70, GW, 130, "Pull request", "ci")
d.group(30, 220, GW, 130, "Merge to main · push order: image → manifest → pointer", "orch")
d.group(30, 370, GW, 130, "Runtime · Airflow", "proc")
pr = d.node(XC[0], 110, "Pull request", "dbt models", "plain", icon="github")
conv = d.node(XC[1], 110, "Convention checks", "naming · ownership", "ci", icon="gha")
slim = d.node(XC[2], 110, "Slim CI build", "state:modified+ · --defer", "ci", icon="dbt")
sch = d.node(XC[3], 110, "Per-PR schema", "dropped when PR closes", "lake", icon="databricks")
gate = d.node(XC[4], 110, "Image build gate", "dbt parse for every env", "ci", icon="docker")
mg = d.node(XC[0], 260, "Merge", "", "plain", icon="github")
img = d.node(XC[1], 260, "Build dbt image", "project + parsed manifests", "orch", icon="docker")
ecr = d.node(XC[2], 260, "ECR image", "tag = commit SHA", "plain", icon="aws")
s3 = d.node(XC[3], 260, "S3 manifest", "path = commit SHA", "plain", icon="aws")
ptr = d.node(XC[4], 260, "Pointer file", "current = SHA", "plain", icon="aws")
dp = d.node(XC[0], 410, "DAG processor", "reads pointer at parse", "orch", icon="airflow")
cos = d.node(XC[1], 410, "Cosmos DAG", "rendered from the manifest", "orch", icon="cosmos")
pod = d.node(XC[2], 410, "dbt pod", "same-SHA image · dbt build", "proc", icon="k8s")
dbx = d.node(XC[3], 410, "Databricks", "warehouse tables", "lake", icon="databricks")
om = d.node(XC[4], 410, "OpenMetadata", "ingests the same manifest", "plain", icon="om")
d.edge(pr, conv, ex=R, en=L)
d.edge(conv, slim, ex=R, en=L)
d.edge(slim, sch, ex=R, en=L)
d.edge(sch, gate, ex=R, en=L)
d.edge(mg, img, ex=R, en=L)
d.edge(img, ecr, "1", ex=R, en=L)
d.edge(ecr, s3, "2", ex=R, en=L)
d.edge(s3, ptr, "3", ex=R, en=L)
d.edge(ptr, dp, dashed=True, ex=B, en=(0.85, 0), pts=[(XC[4] + H, 360), (XC[0] + W * 0.85, 360)])
d.edge(dp, cos, ex=R, en=L)
d.edge(cos, pod, ex=R, en=L)
d.edge(pod, dbx, ex=R, en=L)
d.edge(ptr, om, dashed=True, ex=(0.75, 1), en=(0.75, 0))
d.save("dbt-cicd.drawio")

# ---------------------------------------------------------------- 5. Workflow platform
d = D("Airflow-based workflow platform")
d.text(30, 20, 1000, 30, "5 · Airflow-based workflow platform — many ways in, one runtime", 18, "#111111", True, "left")
d.text(30, 50, 1240, 18, "Workflows arrive as code, as specs or from dbt; "
       "the platform layer gives every DAG the same policy, resources, secrets, alerts and lineage", 11, "#555555", False, "left")
WP = 210
AX, BX = 30, 290
C1, C2 = 555, 790
DX = 1060
GT, GH = 84, 506
d.group(AX - 14, GT, WP + 28, GH, "Ways in", "plain")
d.group(BX - 14, GT, WP + 28, GH, "Delivery", "orch")
crt = d.group(C1 - 15, GT, C2 + WP + 15 - (C1 - 15), GH, "Runtime · Airflow 3 on Kubernetes", "lake")
drun = d.group(DX - 14, GT, WP + 28, GH, "Tasks run on", "proc")
rows = [120, 215, 310, 405, 500]
pr = d.node(AX, rows[0] + 7, "DAG pull request", "hand-written DAGs\nreviewed · tested in CI", "plain", w=WP, h=70, icon="github")
portal = d.node(AX, rows[1] + 7, "Spec-driven DAGs", "a UI or service writes a spec\none DAG per spec", "plain", w=WP, h=70)
dbtm = d.node(AX, rows[2] + 7, "dbt project", "one DAG file per unit\ngraph from the manifest", "plain", w=WP, h=70, icon="dbt")
ppr = d.node(AX, rows[3] + 7, "Platform pull request", "image · config · plugins", "plain", w=WP, h=70, icon="github")
gsync = d.node(BX, rows[0] + 7, "git-sync sidecar", "main → every pod\nin about a minute", "proc", w=WP, h=70, icon="git")
s3 = d.node(BX, rows[1] + 7, "Object storage", "specs · dbt manifest\nread at parse time", "plain", w=WP, h=70, icon="aws")
rel = d.node(BX, rows[3] + 7, "Image release", "versioned image → registry\nGitOps tag → ArgoCD", "orch", w=WP, h=70, icon="argo")
ctrl = d.node(C1, 113, "Control plane", "Scheduler · DAG processor\nTriggerer · API server\none per environment",
              "orch", w=WP, h=165, icon="airflow")
kx = d.node(C2, rows[0] + 7, "Kubernetes executor", "one pod per task\nisolation for heavy tasks", "plain", w=WP, h=70, icon="k8s")
cel = d.node(C2, rows[1] + 7, "Celery workers", "always warm · autoscaled\nno pod start for short tasks", "plain", w=WP, h=70)
d.group(C1 - 7, 300, C2 + WP + 7 - (C1 - 7), 280, "Platform layer — every DAG gets it", "plain")
pol = d.node(C1, 340, "Cluster policy", "timeouts · tags · pools\nfailure callbacks", "orch", w=WP, h=70, icon="airflow")
plc = d.node(C2, 340, "Placement policy", "executor · CPU · memory per task\nset from measured usage", "orch", w=WP, h=70, icon="airflow")
sec = d.node(C1, 430, "Secrets", "external secret store\nconnections · variables", "plain", w=WP, h=70, icon="aws")
xcl = d.node(C2, 430, "XCom & task logs", "both on object storage\nstreaming log reader", "plain", w=WP, h=70, icon="aws")
ops = d.node(C1, 520, "Shared operators", "hooks · operators · helpers\nshipped with the DAGs", "plain", w=WP, h=70)
ast = d.node(C2, 520, "Assets", "one per table\ndata-aware schedules", "plain", w=WP, h=70)
run = [
    ("SQL warehouse", "queries · dbt models", "databricks"),
    ("Spark", "shared Spark Connect server", "spark"),
    ("Kubernetes pods", "dbt · containerised jobs", "k8s"),
    ("Databases", "loads · syncs", "postgres"),
    ("External APIs", "3rd-party systems", None),
]
for y, (t, sub, ic) in zip(rows, run):
    d.node(DX, y + 7, t, sub, "plain", w=WP, h=70, icon=ic)
d.edge(pr, gsync, "merge", ex=R, en=L)
d.edge(portal, s3, "spec", ex=R, en=L)
d.edge(dbtm, s3, "manifest", ex=R, en=(0, 0.75))
d.edge(gsync, ctrl, ex=R, en=(0, 42 / 165))
d.edge(s3, ctrl, ex=R, en=(0, 137 / 165))
d.edge(ppr, rel, ex=R, en=L)
d.edge(rel, crt, "roll out", ex=R, en=(0, (440 - GT) / GH))
d.edge(ctrl, kx, ex=(1, 42 / 165), en=L)
d.edge(ctrl, cel, ex=(1, 137 / 165), en=L)
d.edge(crt, drun, "tasks", ex=R, en=L)
d.group(16, 610, DX + WP + 14 - 16, 100, "Observe & govern", "plain")
OW = (DX + WP - 30 - 60) / 4
obs = [
    ("SSO · RBAC", "roles from identity groups", None),
    ("Alerts", "task failures · data test warnings", "slack"),
    ("Task metrics", "memory · CPU · queue wait per task", None),
    ("Lineage", "Assets → metadata catalog", "om"),
]
for i, (t, sub, ic) in enumerate(obs):
    d.node(30 + i * (OW + 20), 644, t, sub, "plain", w=OW, h=52, icon=ic)
d.save("workflow-platform.drawio")

# ---------------------------------------------------------------- 2. Lakehouse
d = D("Lakehouse on Databricks")
d.text(30, 20, 1000, 30, "2 · Lakehouse on Databricks — one copy of the data, several engines", 18, "#111111", True, "left")
d.text(30, 50, 1240, 18, "Open table formats on object storage, governed by Unity Catalog · "
       "each step runs on the engine that fits it", 11, "#555555", False, "left")
GB = 418
d.group(XI[0] - 14, 84, WI + 28, GB - 84, "Ingest", "ingest")
d.group(XI[1] - 14, 84, XI[3] + WI + 28 - XI[1], GB - 84, "Storage — Delta · Iceberg tables in Unity Catalog, files on S3", "lake")
d.group(XI[4] - 14, 84, WI + 28, GB - 84, "Serve", "serve")
RY = [129, 229, 329]
cdc = d.node(XI[0], RY[0], "CDC", "Kafka → Spark MERGE\nservice DB replicas", "ingest", w=WI, h=70, icon="kafka")
evt = d.node(XI[0], RY[1], "Events", "Kafka Connect Iceberg sink\nappend-only", "ingest", w=WI, h=70, icon="kafka")
bat = d.node(XI[0], RY[2], "Batch sources", "APIs · files → S3 landing\n→ Auto Loader", "ingest", w=WI, h=70, icon="aws")
raw = d.node(XI[1], RY[0], "Raw", "source replicas · events\nBronze → Silver", "lake", w=WI, h=70, icon="databricks")
core = d.node(XI[2], RY[0], "Core", "dbt staging → core\nfacts · dimensions", "lake", w=WI, h=70, icon="dbt")
mart = d.node(XI[3], RY[0], "Mart", "dbt marts\nshaped for one use", "lake", w=WI, h=70, icon="dbt")
NY2, NH2 = 212, 190
d.note(XI[1], NY2, WI, NH2, [
    ("How it is written", ["• CDC: MERGE by key every 10 min", "• Events: append-only commits", "• Batch: stage → check → publish",
                           "  (Write-Audit-Publish)"]),
    ("Rules", ["• Bronze stays private —", "  only Silver is granted", "• Schema changes are applied", "  by the job and announced"])])
d.note(XI[2], NY2, WI, NH2, [
    ("Modelling", ["• staging: rename · cast · clean", "• core: Kimball facts and", "  dimensions, shared by all marts"]),
    ("Runs", ["• One image per commit runs dbt", "• Tests and source freshness", "  gate every run",
              "• Slim CI builds only what a", "  pull request changed"])])
d.note(XI[3], NY2, WI, NH2, [
    ("Shape", ["• Wide tables for one consumer:", "  a dashboard, a report, a", "  feature set"]),
    ("Contract", ["• Owner and exposure declared", "  next to the model", "• Consumers read marts,", "  never staging"])])
dash = d.node(XI[4], RY[0], "Dashboards · SQL", "BI dashboards\nad-hoc analysis", "serve", w=WI, h=70, icon="databricks")
feat = d.node(XI[4], RY[1], "Feature store", "changed rows → online store\n→ lookup API", "serve", w=WI, h=70, icon="postgres")
expo = d.node(XI[4], RY[2], "Exports", "scheduled extracts\nto spreadsheets · tools", "serve", w=WI, h=70)
d.edge(cdc, raw, ex=R, en=L)
d.edge(evt, raw, ex=R, en=(0, 0.72), pts=[(XI[1] - 30, RY[1] + 28), (XI[1] - 30, RY[0] + 43)])
d.edge(bat, raw, ex=R, en=(0, 0.92), pts=[(XI[1] - 40, RY[2] + 28), (XI[1] - 40, RY[0] + 57)])
d.edge(raw, core, "dbt", ex=R, en=L)
d.edge(core, mart, "dbt", ex=R, en=L)
d.edge(mart, dash, ex=R, en=L)
d.edge(mart, feat, ex=(1, 0.72), en=L, pts=[(XI[4] - 30, RY[0] + 43), (XI[4] - 30, RY[1] + 28)])
d.edge(mart, expo, ex=(1, 0.92), en=L, pts=[(XI[4] - 40, RY[0] + 57), (XI[4] - 40, RY[2] + 28)])
GX1 = XI[4] + WI
QW = (GX1 - 30 - 60) / 4
d.group(16, 438, GX1 - 2, 100, "Compute engines — the same tables, the engine that fits the step", "proc")
eng = [
    ("Spark on Kubernetes", "CDC merge · snapshots\nopen-source Spark, Spark Connect", "spark"),
    ("Kafka Connect", "event sink\nno cluster to schedule", "kafka"),
    ("Databricks jobs", "Auto Loader · notebooks\nstarted per run", "databricks"),
    ("SQL warehouse", "dbt models · dashboards\nad-hoc SQL", "databricks"),
]
for i, (t, sub, ic) in enumerate(eng):
    d.node(30 + i * (QW + 20), 479, t, sub, "proc", w=QW, h=70, icon=ic)
d.group(16, 558, GX1 - 2, 100, "Around it", "plain")
aro = [
    ("Orchestration — Airflow", "schedules every step", "orch", "airflow"),
    ("Governance — Unity Catalog", "grants by layer · as Terraform", "lake", "databricks"),
    ("Quality", "dbt tests · freshness · WAP checks", "plain", "dbt"),
    ("Catalog — OpenMetadata", "descriptions · lineage", "plain", "om"),
]
for i, (t, sub, k, ic) in enumerate(aro):
    d.node(30 + i * (QW + 20), 592, t, sub, k, w=QW, h=52, icon=ic)
d.save("lakehouse.drawio")
