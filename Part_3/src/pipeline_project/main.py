from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from pipeline_project.schemas import PredictionRequest, PredictionResponse
from pipeline_project.service import predict_from_request


app = FastAPI(title="Pipeline Project API", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pipeline Project API</title>
    <style>
        :root {
            color-scheme: light;
            --bg: #f3f7ff;
            --panel: #ffffff;
            --text: #162033;
            --muted: #5f6b7a;
            --accent: #2563eb;
            --accent-dark: #1d4ed8;
            --success: #0f766e;
            --danger: #b91c1c;
            --border: #d9e2ef;
            --shadow: 0 18px 45px rgba(22, 32, 51, 0.08);
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #eaf1ff 0%, var(--bg) 55%, #eef6ff 100%);
            color: var(--text);
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 24px;
        }
        .card {
            width: min(100%, 980px);
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: var(--shadow);
            overflow: hidden;
        }
        header {
            padding: 32px 32px 20px;
            border-bottom: 1px solid var(--border);
        }
        h1 { margin: 0 0 8px; font-size: 2rem; }
        p { margin: 0; color: var(--muted); line-height: 1.5; }
        .content { padding: 32px; display: grid; gap: 24px; grid-template-columns: 1.2fr 0.8fr; }
        form {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
        }
        label { display: grid; gap: 6px; font-size: 0.92rem; color: var(--text); }
        input, select {
            width: 100%;
            padding: 12px 14px;
            border-radius: 12px;
            border: 1px solid var(--border);
            font: inherit;
            background: #fbfdff;
        }
        input:focus, select:focus { outline: 2px solid rgba(37, 99, 235, 0.2); border-color: var(--accent); }
        .actions { grid-column: 1 / -1; display: flex; gap: 12px; align-items: center; margin-top: 8px; }
        button {
            border: 0;
            border-radius: 12px;
            padding: 12px 18px;
            background: var(--accent);
            color: white;
            font-weight: 700;
            cursor: pointer;
        }
        button:hover { background: var(--accent-dark); }
        .hint { color: var(--muted); font-size: 0.92rem; }
        .panel {
            background: #f8fbff;
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 20px;
            min-height: 100%;
        }
        .result-box {
            display: grid;
            gap: 14px;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            padding: 7px 12px;
            border-radius: 999px;
            font-size: 0.88rem;
            font-weight: 600;
        }
        .badge.ok { background: rgba(15, 118, 110, 0.12); color: var(--success); }
        .badge.bad { background: rgba(185, 28, 28, 0.12); color: var(--danger); }
        .result-main {
            display: grid;
            gap: 8px;
            padding: 16px;
            border-radius: 16px;
            background: white;
            border: 1px solid var(--border);
        }
        .result-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0;
        }
        .result-value {
            margin: 0;
            font-size: 1.4rem;
            font-weight: 800;
        }
        .result-note {
            margin: 0;
            color: var(--muted);
        }
        .error-list {
            margin: 0;
            padding-left: 18px;
            color: var(--danger);
        }
        .small {
            color: var(--muted);
            font-size: 0.9rem;
        }
        @media (max-width: 840px) {
            .content { grid-template-columns: 1fr; }
            form { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <main class="card">
        <header>
            <h1>Pipeline Project API</h1>
            <p>Enter the census record details below and get a prediction result from the trained pipeline.</p>
        </header>
        <section class="content">
            <form id="prediction-form">
                <label>Age (years) <input name="age" type="number" min="1" max="120" value="39" required></label>
                <label>Work class <select name="workclass" required><option value="">-- Select --</option><option value="Federal-gov">Federal-gov</option><option value="Local-gov">Local-gov</option><option value="Private" selected>Private</option><option value="Self-emp-inc">Self-emp-inc</option><option value="Self-emp-not-inc">Self-emp-not-inc</option><option value="State-gov">State-gov</option></select></label>
                <label>Final weight (fnlwgt) <input name="fnlwgt" type="number" min="1" value="77516" required></label>
                <label>Education level <select name="education" required><option value="">-- Select --</option><option value="1st-4th">1st-4th</option><option value="5th-6th">5th-6th</option><option value="7th-8th">7th-8th</option><option value="9th">9th</option><option value="10th">10th</option><option value="11th">11th</option><option value="12th">12th</option><option value="Assoc-acdm">Assoc-acdm</option><option value="Assoc-voc">Assoc-voc</option><option value="Bachelors" selected>Bachelors</option><option value="Doctorate">Doctorate</option><option value="HS-grad">HS-grad</option><option value="Masters">Masters</option><option value="Prof-school">Prof-school</option><option value="Some-college">Some-college</option></select></label>
                <label>Education number <select name="education.num" required><option value="">-- Select --</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option><option value="7">7</option><option value="8">8</option><option value="9">9</option><option value="10">10</option><option value="11">11</option><option value="12">12</option><option value="13" selected>13</option><option value="14">14</option><option value="15">15</option><option value="16">16</option></select></label>
                <label>Marital status <select name="marital.status" required><option value="">-- Select --</option><option value="Divorced">Divorced</option><option value="Married-civ-spouse">Married-civ-spouse</option><option value="Married-spouse-absent">Married-spouse-absent</option><option value="Never-married" selected>Never-married</option><option value="Separated">Separated</option><option value="Widowed">Widowed</option></select></label>
                <label>Occupation <select name="occupation" required><option value="">-- Select --</option><option value="Adm-clerical" selected>Adm-clerical</option><option value="Armed-Forces">Armed-Forces</option><option value="Craft-repair">Craft-repair</option><option value="Exec-managerial">Exec-managerial</option><option value="Farming-fishing">Farming-fishing</option><option value="Handlers-cleaners">Handlers-cleaners</option><option value="Machine-op-inspct">Machine-op-inspct</option><option value="Other-service">Other-service</option><option value="Priv-house-serv">Priv-house-serv</option><option value="Prof-specialty">Prof-specialty</option><option value="Protective-serv">Protective-serv</option><option value="Sales">Sales</option><option value="Tech-support">Tech-support</option><option value="Transport-moving">Transport-moving</option></select></label>
                <label>Relationship <select name="relationship" required><option value="">-- Select --</option><option value="Husband">Husband</option><option value="Not-in-family" selected>Not-in-family</option><option value="Other-relative">Other-relative</option><option value="Own-child">Own-child</option><option value="Unmarried">Unmarried</option><option value="Wife">Wife</option></select></label>
                <label>Race <select name="race" required><option value="">-- Select --</option><option value="Asian-Pac-Islander">Asian-Pac-Islander</option><option value="Black">Black</option><option value="Other">Other</option><option value="White" selected>White</option></select></label>
                <label>Sex <select name="sex" required><option value="">-- Select --</option><option value="Female">Female</option><option value="Male" selected>Male</option></select></label>
                <label>Capital gain <input name="capital.gain" type="number" min="0" value="2174" required></label>
                <label>Capital loss <input name="capital.loss" type="number" min="0" value="0" required></label>
                <label>Hours per week <input name="hours.per.week" type="number" min="1" max="168" value="40" required></label>
                <label>Native country <select name="native.country" required><option value="">-- Select --</option><option value="Cambodia">Cambodia</option><option value="Canada">Canada</option><option value="China">China</option><option value="Columbia">Columbia</option><option value="Cuba">Cuba</option><option value="Dominican-Republic">Dominican-Republic</option><option value="Ecuador">Ecuador</option><option value="El-Salvador">El-Salvador</option><option value="England">England</option><option value="France">France</option><option value="Germany">Germany</option><option value="Greece">Greece</option><option value="Guam">Guam</option><option value="Haiti">Haiti</option><option value="Hong">Hong</option><option value="Hungary">Hungary</option><option value="India">India</option><option value="Iran">Iran</option><option value="Ireland">Ireland</option><option value="Italy">Italy</option><option value="Jamaica">Jamaica</option><option value="Japan">Japan</option><option value="Laos">Laos</option><option value="Mexico">Mexico</option><option value="Nicaragua">Nicaragua</option><option value="Outlying-US(Guam-USVI-etc)">Outlying-US(Guam-USVI-etc)</option><option value="Peru">Peru</option><option value="Philippines">Philippines</option><option value="Poland">Poland</option><option value="Portugal">Portugal</option><option value="Puerto-Rico">Puerto-Rico</option><option value="Scotland">Scotland</option><option value="South">South</option><option value="Taiwan">Taiwan</option><option value="Thailand">Thailand</option><option value="Trinadad&Tobago">Trinadad&Tobago</option><option value="United-States" selected>United-States</option><option value="Vietnam">Vietnam</option><option value="Yugoslavia">Yugoslavia</option></select></label>
                <div class="actions">
                    <button type="submit">Predict</button>
                    <span class="hint">Swagger is still available at <a href="/docs">/docs</a>.</span>
                </div>
            </form>
            <aside class="panel">
                <h2 style="margin-top: 0;">Prediction result</h2>
                <div class="result-box" id="result">
                    <div class="small">Fill the form and press Predict.</div>
                </div>
            </aside>
        </section>
    </main>
    <script>
        const form = document.getElementById('prediction-form');
        const result = document.getElementById('result');

        function renderPrediction(data) {
            const label = data.prediction ? 'Income above 50K' : 'Income at or below 50K';
            const badgeClass = data.prediction ? 'ok' : 'bad';
            const probability = (data.probability * 100).toFixed(1);

            result.innerHTML = `
                <div class="badge ${badgeClass}">${data.prediction ? 'Positive prediction' : 'Negative prediction'}</div>
                <div class="result-main">
                    <p class="result-title">Model result</p>
                    <p class="result-value">${label}</p>
                    <p class="result-note">Estimated probability: ${probability}%</p>
                </div>
            `;
        }

        function renderErrors(data) {
            const details = Array.isArray(data.detail) ? data.detail : [{ msg: data.detail || 'Request failed' }];
            const items = details.map(item => `<li>${item.loc ? item.loc.join(' / ') + ': ' : ''}${item.msg || item}</li>`).join('');

            result.innerHTML = `
                <div class="badge bad">Validation error</div>
                <div class="result-main">
                    <p class="result-title">Please correct the highlighted input values.</p>
                    <ul class="error-list">${items}</ul>
                </div>
            `;
        }

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            result.innerHTML = '<div class="small">Predicting...</div>';

            const payload = Object.fromEntries(new FormData(form).entries());
            for (const key of Object.keys(payload)) {
                if (!Number.isNaN(Number(payload[key])) && payload[key].trim?.() !== '') {
                    payload[key] = Number(payload[key]);
                }
            }

            const response = await fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            if (!response.ok) {
                renderErrors(data);
                return;
            }

            renderPrediction(data);
        });
    </script>
</body>
</html>
"""


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    try:
        return predict_from_request(payload)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
