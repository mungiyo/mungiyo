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
d.text(30, 20, 700, 30, "데이터 플랫폼 — 서비스 DB 에서 서빙까지", 18, "#111111", True, "left")
for x, t in zip(X, ["원천", "수집", "스트림", "처리", "레이크하우스", "서빙"]):
    d.text(x, 62, W, 20, t.upper(), 10, "#888888", True)
db = d.node(X[0], 100, "서비스 DB", "Postgres · MySQL · DocDB", "src", icon="postgres")
ev = d.node(X[0], 340, "앱 이벤트", "이벤트 로그", "src")
dbz = d.node(X[1], 100, "Debezium", "Kafka Connect · 자체 SMT", "ingest", icon="debezium")
kafka = d.node(X[2], 100, "Kafka", "", "ingest", h=296)
d.icon(X[2] + H - 18, 198, "kafka", 36)
spark = d.node(X[3], 100, "Spark on Kubernetes", "10분마다 CDC MERGE", "proc", icon="spark")
flink = d.node(X[3], 340, "Flink", "실시간 피처 잡", "proc", icon="flink")
raw = d.node(X[4], 100, "원천 복제본", "Delta · Unity Catalog", "lake", icon="databricks")
dw = d.node(X[4], 220, "dbt 웨어하우스", "staging → core → mart", "lake", icon="dbt")
svc = d.node(X[5], 100, "제품 서비스", "CRM · 앱", "src")
feach = d.node(X[5], 220, "feach", "피처 조회 API", "serve")
pg = d.node(X[5], 340, "온라인 스토어", "PostgreSQL", "serve", icon="postgres")
d.edge(db, dbz, ex=R, en=L)
d.edge(dbz, kafka, ex=R, en=(0, 0.095))
d.edge(ev, kafka, ex=R, en=(0, 0.905))
d.edge(kafka, spark, ex=(1, 0.095), en=L)
d.edge(kafka, flink, ex=(1, 0.905), en=L)
d.edge(spark, raw, ex=R, en=L)
d.edge(raw, dw, ex=B, en=T)
d.edge(dw, pg, ex=B, en=(0, 0.25), pts=[(X[4] + H, 354)])
d.edge(flink, pg, ex=(1, 0.75), en=(0, 0.75))
d.text(X[4] + H + 8, 288, 110, 30, "배치 동기화\n바뀐 행만", 10, "#333333", False, "left")
d.text(X[3] + W + 30, 386, 110, 16, "실시간 upsert", 10, "#333333", False, "left")
d.edge(pg, feach, ex=T, en=B)
d.edge(feach, svc, ex=T, en=B)
band = X[5] + W - X[1]
d.node(X[1], 440, "Airflow 3 on Kubernetes", "CDC 머지 · dbt 실행 · 피처 동기화를 스케줄", "orch", w=band, h=52)
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
d.text(30, 20, 800, 30, "1 · CDC 파이프라인 — 랜딩 없이 Kafka 에서 레이크하우스로 바로", 18, "#111111", True, "left")
portal = d.node(X[1], 80, "셀프서비스 포털", "재스냅샷 실행", "plain")
dag = d.node(X[3], 80, "Airflow DAG", "10분마다", "orch", icon="airflow")
db = d.node(X[0], 220, "원천 DB", "Postgres · MySQL · DocDB\nWAL / binlog", "src", h=70, icon="postgres")
dbz = d.node(X[1], 220, "Debezium", "K8s 위 Kafka Connect\n자체 SMT 로 타입 정규화", "ingest", h=70, icon="debezium")
kafka = d.node(X[2], 220, "Kafka", "테이블마다 토픽 하나", "ingest", icon="kafka")
job = d.node(X[3], 220, "Spark CDC 잡", "Structured Streaming\nforeachBatch MERGE", "proc", h=70, icon="spark")
raw = d.node(X[4], 220, "원천 복제본", "Delta · Unity Catalog\ncatalog-managed", "lake", h=70, icon="databricks")
dw = d.node(X[5], 220, "dbt 웨어하우스", "staging → core → mart", "lake", icon="dbt")
topic = d.node(X[3], 380, "스키마 변경 토픽", "새 테이블 · 컬럼 · 타입", "ingest", icon="kafka")
alert = d.node(X[4], 380, "알림 DAG", "", "orch", icon="airflow")
slack = d.node(X[5], 380, "Slack", "", "plain", icon="slack")
d.edge(db, dbz, ex=R, en=L)
d.edge(dbz, kafka, ex=R, en=L)
d.edge(kafka, job, ex=R, en=L)
d.edge(job, raw, ex=R, en=L)
d.edge(raw, dw, ex=R, en=L)
d.edge(portal, dbz, "시그널 토픽 →\n증분 스냅샷", ex=B, en=T)
d.edge(dag, job, "SparkApplication 제출", ex=B, en=T)
d.edge(job, topic, "스키마 진화\n타입 넓히기", ex=B, en=T)
d.edge(topic, alert, ex=R, en=L)
d.edge(alert, slack, ex=R, en=L)
d.save("cdc-pipeline.drawio")

# ---------------------------------------------------------------- 2. feach
d = D("feach feature store")
d.text(30, 20, 800, 30, "2 · feach — 피처 스토어: 쓰기는 파이프라인, 읽기는 API 하나", 18, "#111111", True, "left")
XF = [30, 262, 510, 776, 1008]
mart = d.node(XF[0], 100, "dbt 피처 마트", "Databricks · 매시간", "lake", icon="dbt")
sync = d.node(XF[1], 100, "Airflow 배치 동기화", "Delta 두 버전을 비교해\n바뀐 행만 upsert", "orch", h=70, icon="airflow")
kafka = d.node(XF[0], 240, "Kafka", "CDC 토픽 · 앱 이벤트", "ingest", h=170)
d.icon(XF[0] + H - 16, 268, "kafka", 32)
fl = d.node(XF[1], 240, "Flink 잡", "세션 클러스터\n잡마다 jar 하나 · upsert", "proc", h=70, icon="flink")
jdbc = d.node(XF[1], 354, "JDBC sink", "Kafka Connect\n테이블 그대로 복사", "ingest", h=70, icon="kafka")
d.group(XF[2] - 15, 70, W + 30, 364, "온라인 스토어 · PostgreSQL", "serve")
d.icon(XF[2] + W - 14, 76, "postgres", 22)
tb = d.node(XF[2], 100, "배치 피처", "", "plain")
tr = d.node(XF[2], 240, "실시간 피처", "", "plain")
tc = d.node(XF[2], 354, "원본 사본", "view 로 조인", "plain")
serving = d.node(XF[3], 240, "feach 서빙 API", "POST /get-features\n스토어 왕복 한 번", "serve", h=70)
cons = d.node(XF[4], 240, "제품 서비스", "CRM · SDK get_features()", "src")
ui = d.node(XF[1], 490, "feach 카탈로그 UI", "피처 계약 작성", "serve")
meta = d.node(XF[2], 490, "feach meta API", "", "serve")
mdb = d.node(XF[3], 490, "메타 DB", "환경마다 하나", "plain", icon="postgres")
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
d.edge(mdb, serving, "계약", dashed=True, ex=T, en=(0.6, 1))
d.save("feach.drawio")

# ---------------------------------------------------------------- 3. dbt CI/CD
d = D("dbt CI/CD")
d.text(30, 20, 900, 30, "3 · dbt CI/CD — 커밋 SHA 하나가 이미지와 DAG 그래프를 함께 가리킨다", 18, "#111111", True, "left")
XC = [50 + STEP * i for i in range(5)]
GW = XC[4] + W + 20 - 30
d.group(30, 70, GW, 130, "Pull request", "ci")
d.group(30, 220, GW, 130, "main 머지 · 올리는 순서: 이미지 → manifest → 포인터", "orch")
d.group(30, 370, GW, 130, "실행 · Airflow", "proc")
pr = d.node(XC[0], 110, "Pull request", "dbt 모델", "plain", icon="github")
conv = d.node(XC[1], 110, "규칙 검사", "이름 · 오너", "ci", icon="gha")
slim = d.node(XC[2], 110, "Slim CI 빌드", "state:modified+ · --defer", "ci", icon="dbt")
sch = d.node(XC[3], 110, "PR 별 스키마", "PR 닫히면 삭제", "lake", icon="databricks")
gate = d.node(XC[4], 110, "이미지 빌드 게이트", "환경마다 dbt parse", "ci", icon="docker")
mg = d.node(XC[0], 260, "머지", "", "plain", icon="github")
img = d.node(XC[1], 260, "dbt 이미지 빌드", "프로젝트 + manifest", "orch", icon="docker")
ecr = d.node(XC[2], 260, "ECR 이미지", "태그 = 커밋 SHA", "plain", icon="aws")
s3 = d.node(XC[3], 260, "S3 manifest", "경로 = 커밋 SHA", "plain", icon="aws")
ptr = d.node(XC[4], 260, "포인터 파일", "current = SHA", "plain", icon="aws")
dp = d.node(XC[0], 410, "DAG processor", "파싱 때 포인터를 읽음", "orch", icon="airflow")
cos = d.node(XC[1], 410, "Cosmos DAG", "manifest 로 렌더링", "orch", icon="cosmos")
pod = d.node(XC[2], 410, "dbt pod", "같은 SHA 이미지로 실행", "proc", icon="k8s")
dbx = d.node(XC[3], 410, "Databricks", "웨어하우스 테이블", "lake", icon="databricks")
om = d.node(XC[4], 410, "OpenMetadata", "같은 manifest 수집", "plain", icon="om")
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
d.text(30, 20, 900, 30, "4 · Airflow CI/CD — 이미지는 승격하고, DAG 은 당겨 온다", 18, "#111111", True, "left")
XA = [50 + STEP * i for i in range(4)]
GW = XA[3] + W + 20 - 30
CX = 30 + GW + 20
d.group(30, 70, GW, 250, "플랫폼 이미지 · Airflow + 공용 오퍼레이터 패키지", "orch")
d.group(30, 340, GW, 130, "DAGs", "proc")
d.group(CX, 70, W + 30, 400, "Airflow on Kubernetes\ndev · stg · prod", "lake")
ipr = d.node(XA[0], 110, "Pull request", "", "plain", icon="github")
ici = d.node(XA[1], 110, "CI", "lint · lock 검사\n이미지 안에서 pytest", "ci", h=70, icon="gha")
irel = d.node(XA[2], 110, "release-please", "릴리스 PR → 버전 태그", "orch", icon="github")
iecr = d.node(XA[3], 110, "ECR 이미지", "vX.Y.Z-sha · 불변 태그", "plain", icon="aws")
dep = d.node(XA[1], 235, "배포 워크플로", "수동 · 환경별 승인", "ci", icon="gha")
gop = d.node(XA[2], 235, "GitOps 레포", "Helm values 이미지 태그", "plain", icon="helm")
argo = d.node(XA[3], 235, "ArgoCD", "sync", "orch", icon="argo")
dpr = d.node(XA[0], 385, "Pull request", "", "plain", icon="github")
dci = d.node(XA[1], 385, "CI", "lint · DAG import 테스트\n실행 이미지 안에서", "ci", h=70, icon="gha")
dmain = d.node(XA[2], 385, "main 브랜치", "브랜치 하나로 전 환경", "plain", icon="git")
gs = d.node(XA[3], 385, "git-sync sidecar", "모든 파드 · 60초", "proc", icon="git")
sched = d.node(CX + 15, 150, "스케줄러", "Kubernetes executor", "plain", icon="k8s")
dagp = d.node(CX + 15, 385, "DAG processor", "태스크 파드", "plain", icon="airflow")
d.edge(ipr, ici, ex=R, en=L)
d.edge(ici, irel, "머지", ex=R, en=L)
d.edge(irel, iecr, "push", ex=R, en=L)
d.edge(iecr, dep, "버전 선택", dashed=True, ex=B, en=T, pts=[(XA[3] + H, 205), (XA[1] + H, 205)])
d.edge(dep, gop, "태그", ex=R, en=L)
d.edge(gop, argo, ex=R, en=L)
d.edge(argo, sched, "배포", ex=R, en=B, pts=[(CX + 15 + H, 263)])
d.edge(dpr, dci, ex=R, en=L)
d.edge(dci, dmain, "머지", ex=R, en=L)
d.edge(dmain, gs, "pull", ex=R, en=L)
d.edge(gs, dagp, ex=R, en=L)
d.save("airflow-cicd.drawio")
