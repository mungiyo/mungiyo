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
    "flink": "apacheflink.svg", "airflow": "apacheairflow.svg", "databricks": "databricks.svg",
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

    def edge(self, s, t, label="", dashed=False, ex=None, en=None, pts=None):
        i = self._id()
        st = (f"edgeStyle=orthogonalEdgeStyle;rounded=1;{FONT}endArrow=block;endFill=1;strokeColor=#555555;"
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
for x, t in zip(X, ["Sources", "Capture", "Stream", "Process", "Lakehouse", "Serve"]):
    d.text(x, 62, W, 20, t.upper(), 10, "#888888", True)
db = d.node(X[0], 100, "Service DBs", "Postgres · MySQL · DocDB", "src", icon="postgres")
ev = d.node(X[0], 340, "App events", "event logs", "src")
dbz = d.node(X[1], 100, "Debezium", "Kafka Connect · custom SMT", "ingest", icon="debezium")
kafka = d.node(X[2], 100, "Kafka", "", "ingest", h=296)
d.icon(X[2] + H - 18, 198, "kafka", 36)
spark = d.node(X[3], 100, "Spark on Kubernetes", "CDC MERGE every 10 min", "proc", icon="spark")
flink = d.node(X[3], 340, "Flink", "real-time feature jobs", "proc", icon="flink")
raw = d.node(X[4], 100, "Raw replicas", "Delta · Unity Catalog", "lake", icon="databricks")
dw = d.node(X[4], 220, "dbt warehouse", "staging → core → mart", "lake", icon="dbt")
svc = d.node(X[5], 100, "Product services", "CRM · apps", "src")
feach = d.node(X[5], 220, "feach", "feature lookup API", "serve")
pg = d.node(X[5], 340, "Online store", "PostgreSQL", "serve", icon="postgres")
d.edge(db, dbz, ex=R, en=L)
d.edge(dbz, kafka, ex=R, en=(0, 0.095))
d.edge(ev, kafka, ex=R, en=(0, 0.905))
d.edge(kafka, spark, ex=(1, 0.095), en=L)
d.edge(kafka, flink, ex=(1, 0.905), en=L)
d.edge(spark, raw, ex=R, en=L)
d.edge(raw, dw, ex=B, en=T)
d.edge(dw, pg, ex=B, en=(0, 0.25), pts=[(X[4] + H, 354)])
d.edge(flink, pg, ex=(1, 0.75), en=(0, 0.75))
d.text(X[4] + H + 8, 288, 110, 30, "batch sync\nchanged rows only", 10, "#333333", False, "left")
d.text(X[3] + W + 30, 386, 110, 16, "real-time upsert", 10, "#333333", False, "left")
d.edge(pg, feach, ex=T, en=B)
d.edge(feach, svc, ex=T, en=B)
band = X[5] + W - X[1]
d.node(X[1], 440, "Airflow 3 on Kubernetes", "schedules CDC merge · dbt runs · feature sync", "orch", w=band, h=52)
d.icon(X[1] + 44, 453, "airflow")
d.icon(X[1] + 78, 453, "k8s")
d.node(X[1], 506, "CI/CD", "GitHub Actions → ECR · S3 → ArgoCD · git-sync", "ci", w=band, h=52)
d.icon(X[1] + 44, 519, "gha")
d.icon(X[1] + 78, 519, "argo")
d.badge(X[3] - 10, 90, 1)
d.badge(X[5] - 10, 210, 2)
d.badge(X[4] - 10, 210, 3)
d.badge(X[1] - 10, 430, 4)
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

# ---------------------------------------------------------------- 2. feach
d = D("feach feature store")
d.text(30, 20, 800, 30, "2 · feach — feature store: pipelines write, one API reads", 18, "#111111", True, "left")
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
d.text(30, 20, 900, 30, "3 · dbt CI/CD — one commit SHA names both the image and the DAG graph", 18, "#111111", True, "left")
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

# ---------------------------------------------------------------- 4. Airflow CI/CD
d = D("Airflow CI/CD")
d.text(30, 20, 900, 30, "4 · Airflow CI/CD — the image is promoted, DAGs are pulled", 18, "#111111", True, "left")
XA = [50 + STEP * i for i in range(4)]
GW = XA[3] + W + 20 - 30
CX = 30 + GW + 20
d.group(30, 70, GW, 250, "Platform image · Airflow + shared operator package", "orch")
d.group(30, 340, GW, 130, "DAGs", "proc")
d.group(CX, 70, W + 30, 400, "Airflow on Kubernetes\ndev · stg · prod", "lake")
ipr = d.node(XA[0], 110, "Pull request", "", "plain", icon="github")
ici = d.node(XA[1], 110, "CI", "lint · lock check\nbuild image, pytest inside", "ci", h=70, icon="gha")
irel = d.node(XA[2], 110, "release-please", "release PR → version tag", "orch", icon="github")
iecr = d.node(XA[3], 110, "ECR image", "vX.Y.Z-sha · immutable", "plain", icon="aws")
dep = d.node(XA[1], 235, "Deploy workflow", "manual · per-env approval", "ci", icon="gha")
gop = d.node(XA[2], 235, "GitOps repo", "image tag in Helm values", "plain", icon="helm")
argo = d.node(XA[3], 235, "ArgoCD", "sync", "orch", icon="argo")
dpr = d.node(XA[0], 385, "Pull request", "", "plain", icon="github")
dci = d.node(XA[1], 385, "CI", "lint · DAG import tests\ninside the runtime image", "ci", h=70, icon="gha")
dmain = d.node(XA[2], 385, "main branch", "single branch, all envs", "plain", icon="git")
gs = d.node(XA[3], 385, "git-sync sidecar", "in every pod · 60 s", "proc", icon="git")
sched = d.node(CX + 15, 150, "Scheduler", "Kubernetes executor", "plain", icon="k8s")
dagp = d.node(CX + 15, 385, "DAG processor", "task pods", "plain", icon="airflow")
d.edge(ipr, ici, ex=R, en=L)
d.edge(ici, irel, "merge", ex=R, en=L)
d.edge(irel, iecr, "push", ex=R, en=L)
d.edge(iecr, dep, "pick a version", dashed=True, ex=B, en=T, pts=[(XA[3] + H, 205), (XA[1] + H, 205)])
d.edge(dep, gop, "bump", ex=R, en=L)
d.edge(gop, argo, ex=R, en=L)
d.edge(argo, sched, "roll out", ex=R, en=B, pts=[(CX + 15 + H, 263)])
d.edge(dpr, dci, ex=R, en=L)
d.edge(dci, dmain, "merge", ex=R, en=L)
d.edge(dmain, gs, "pull", ex=R, en=L)
d.edge(gs, dagp, ex=R, en=L)
d.save("airflow-cicd.drawio")
