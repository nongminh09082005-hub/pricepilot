from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.secret_key = "pricepilot-secret-key"

MATERIAL_PRICE = {
    "Thép": 29825172,
    "Inox": 84000000,
    "Nhôm": 93255906,
    "Đồng": 358625259
}

BUTTON_CSS = """
button, .btn {
    background: linear-gradient(135deg, #008735, #00b84a);
    color: white;
    border: none;
    padding: 15px 42px;
    font-size: 18px;
    font-weight: 700;
    border-radius: 14px;
    cursor: pointer;
    text-decoration: none;
    box-shadow: 0 8px 20px rgba(0, 204, 102, 0.28);
    transition: all 0.25s ease;
    display: inline-block;
}

button:hover, .btn:hover {
    background: linear-gradient(135deg, #00cc66, #00e676);
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(0, 204, 102, 0.45);
}

button:active, .btn:active {
    transform: translateY(0);
}

.detail {
    box-shadow: none !important;
}

.detail:hover {
    box-shadow: 0 8px 22px rgba(255,255,255,0.18) !important;
}
"""

INTRO_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>PricePilot</title>
<style>
body {
    margin: 0;
    font-family: Poppins, Arial, sans-serif;
    background: linear-gradient(rgba(15,23,42,.78), rgba(15,23,42,.88)),
                url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab');
    background-size: cover;
    background-position: center;
    color: white;
    min-height: 100vh;
}

.header {
    padding: 28px 60px;
    font-size: 28px;
    font-weight: 800;
}

.hero {
    min-height: calc(100vh - 100px);
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    flex-direction: column;
    padding: 40px;
}

.hero h1 {
    font-size: 76px;
    margin-bottom: 18px;
}

.hero p {
    font-size: 21px;
    max-width: 900px;
    line-height: 1.7;
    color: #e5e7eb;
}

.buttons {
    margin-top: 38px;
    display: flex;
    gap: 25px;
}

""" + BUTTON_CSS + """

.detail {
    background: transparent;
    border: 2px solid rgba(255,255,255,.8);
}

.detail:hover {
    background: white;
    color: #008735;
}

.modal {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.75);
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.modal-content {
    background: #111827;
    color: white;
    width: 72%;
    max-height: 80vh;
    overflow-y: auto;
    padding: 38px;
    border-radius: 18px;
    line-height: 1.75;
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 25px 70px rgba(0,0,0,.45);
}

.modal-content h2 {
    margin-top: 0;
    font-size: 32px;
}

.modal-content h3 {
    color: #00cc66;
    margin-top: 26px;
}

.close {
    float: right;
    font-size: 30px;
    cursor: pointer;
    font-weight: bold;
}

@media (max-width: 768px) {
    .hero h1 { font-size: 48px; }
    .buttons { flex-direction: column; }
    .modal-content { width: 86%; }
}
</style>
</head>

<body>
<div class="header">PricePilot</div>

<section class="hero">
    <h1>PricePilot</h1>
    <p>
        PricePilot supports SME mechanical manufacturing businesses in setting product selling prices.
        Here, you will receive detailed analysis, pricing recommendations, profit forecasts,
        risk evaluation, and strategic insights to make smarter pricing decisions.
    </p>

    <div class="buttons">
        <a class="btn" href="/input">Start</a>
        <button class="detail" onclick="openModal()">Detail</button>
    </div>
</section>

<div class="modal" id="detailModal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>

        <h2>How PricePilot Works</h2>

        <p>
        PricePilot combines two important analytical methods: <b>Price Elasticity of Demand</b>
        and <b>Monte Carlo Simulation</b>. These methods help estimate how customers may react
        to price changes and how different pricing decisions may affect order volume, revenue,
        cost pressure, and expected profit.
        </p>

        <h3>1. Price Elasticity of Demand</h3>
        <p>
        Price elasticity of demand measures how sensitive customer demand is when price changes.
        When elasticity is high, customers react strongly to price increases, so even a small
        increase may reduce order volume significantly. When elasticity is low, customers are
        less sensitive to price changes, meaning the business may be able to increase prices
        with lower risk of losing demand.
        </p>

        <p>
        In PricePilot, elasticity is used to estimate the demand impact of each tested price
        increase. This allows the system to compare the benefit of higher margin against the
        potential downside of lower order volume. The goal is not simply to raise prices, but
        to find the point where profit improves without creating unnecessary demand risk.
        </p>

        <h3>2. Monte Carlo Simulation</h3>
        <p>
        Monte Carlo Simulation is a risk-analysis method that explores many possible outcomes
        instead of relying on one fixed forecast. It is commonly used when business results are
        affected by uncertainty, such as demand fluctuation, inflation, market growth, customer
        behavior, and competitive pressure.
        </p>

        <p>
        In this web app, multiple pricing scenarios are simulated to estimate how profit changes
        under different price increases. By comparing those scenarios, PricePilot identifies the
        price increase with the strongest expected profit and provides strategic recommendations:
        aggressive, balanced, or conservative.
        </p>

        <p>
        This gives SME manufacturing businesses a more structured way to make pricing decisions.
        Instead of guessing, the company can use cost data, market assumptions, elasticity, and
        simulation results to choose a price strategy that fits its risk tolerance and business goals.
        </p>
    </div>
</div>

<script>
function openModal() {
    document.getElementById("detailModal").style.display = "flex";
}
function closeModal() {
    document.getElementById("detailModal").style.display = "none";
}
</script>

</body>
</html>
"""

INPUT_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>PricePilot Input</title>
<style>
body {
    font-family: Poppins, Arial, sans-serif;
    margin: 0;
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
    min-height: 100vh;
}

.container {
    max-width: 980px;
    margin: auto;
    padding: 45px 30px;
}

.back {
    color: #00cc66;
    text-decoration: none;
    font-weight: 700;
}

.card {
    background: rgba(255,255,255,0.06);
    padding: 35px;
    border-radius: 22px;
    margin: 30px 0;
    box-shadow: 0 20px 45px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
}

h1 {
    font-size: 42px;
    margin-bottom: 8px;
}

.subtitle {
    color: #cbd5e1;
    margin-bottom: 30px;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 22px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

label {
    font-weight: 600;
    margin-bottom: 8px;
}

input, select {
    padding: 13px 15px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.08);
    color: white;
    font-size: 15px;
}

select option {
    color: black;
}

input[type="range"] {
    accent-color: #00cc66;
    padding: 0;
    cursor: pointer;
}

.range-value {
    color: #00cc66;
    font-weight: 800;
    margin-top: 8px;
}

.button-wrap {
    text-align: center;
    margin-top: 35px;
}

""" + BUTTON_CSS + """

@media (max-width: 768px) {
    .form-grid {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>
<div class="container">

<a class="back" href="/">← Back to intro</a>

<div class="card">
    <h1>Nhập thông tin của bạn</h1>
    <p class="subtitle">
        Điền dữ liệu sản xuất, chi phí và thị trường để PricePilot mô phỏng chiến lược giá tối ưu.
    </p>

    <form method="POST" action="/run">
        <div class="form-grid">

            <div class="form-group">
                <label>Vật liệu</label>
                <select name="material">
                    <option value="Thép">Thép - 29,825,172 VNĐ/tấn</option>
                    <option value="Inox">Inox - 84,000,000 VNĐ/tấn</option>
                    <option value="Nhôm">Nhôm - 93,255,906 VNĐ/tấn</option>
                    <option value="Đồng">Đồng - 358,625,259 VNĐ/tấn</option>
                </select>
            </div>

            <div class="form-group">
                <label>Sản lượng tấn/tháng</label>
                <input type="number" name="tons" value="120">
            </div>

            <div class="form-group">
                <label>Số công nhân</label>
                <input type="number" name="workers" value="25">
            </div>

            <div class="form-group">
                <label>Lương VNĐ/tháng</label>
                <input type="number" name="salary" value="9000000">
            </div>

            <div class="form-group">
                <label>Điện + mặt bằng VNĐ/năm</label>
                <input type="number" name="electricity_year" value="600000000">
            </div>

            <div class="form-group">
                <label>Bảo trì VNĐ/năm</label>
                <input type="number" name="maintenance_year" value="300000000">
            </div>

            <div class="form-group">
                <label>Giá trị máy VNĐ</label>
                <input type="number" name="machine_value" value="3000000000">
            </div>

            <div class="form-group">
                <label>Tuổi thọ máy năm</label>
                <input type="number" name="machine_life" value="8">
            </div>

            <div class="form-group">
                <label>Margin %</label>
                <input type="range" name="margin" min="0" max="60" value="20" oninput="marginVal.innerText=this.value">
                <span class="range-value"><span id="marginVal">20</span>%</span>
            </div>

            <div class="form-group">
                <label>Win rate %</label>
                <input type="range" name="win_rate" min="0" max="100" value="35" oninput="winVal.innerText=this.value">
                <span class="range-value"><span id="winVal">35</span>%</span>
            </div>

            <div class="form-group">
                <label>Số đơn/tháng</label>
                <input type="range" name="orders" min="1" max="200" value="45" oninput="ordersVal.innerText=this.value">
                <span class="range-value"><span id="ordersVal">45</span> đơn</span>
            </div>

            <div class="form-group">
                <label>Elasticity</label>
                <input type="range" name="elasticity" min="0.5" max="2" step="0.1" value="1.2" oninput="elasticityVal.innerText=this.value">
                <span class="range-value"><span id="elasticityVal">1.2</span></span>
            </div>

            <div class="form-group">
                <label>Tăng trưởng ngành %</label>
                <input type="range" name="industry_growth" min="0" max="15" value="7" oninput="industryVal.innerText=this.value">
                <span class="range-value"><span id="industryVal">7</span>%</span>
            </div>

            <div class="form-group">
                <label>Tăng trưởng thu nhập %</label>
                <input type="range" name="income_growth" min="0" max="10" value="5" oninput="incomeVal.innerText=this.value">
                <span class="range-value"><span id="incomeVal">5</span>%</span>
            </div>

            <div class="form-group">
                <label>Lạm phát %</label>
                <input type="range" name="inflation" min="0" max="10" value="4" oninput="inflationVal.innerText=this.value">
                <span class="range-value"><span id="inflationVal">4</span>%</span>
            </div>

        </div>

        <div class="button-wrap">
            <button type="submit">Run Simulation</button>
        </div>
    </form>
</div>

</div>
</body>
</html>
"""

LOADING_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Loading...</title>
<style>
body {
    margin: 0;
    font-family: Poppins, Arial, sans-serif;
    background: #0f172a;
    color: white;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
}

.loader {
    width: 90px;
    height: 90px;
    border: 10px solid rgba(255,255,255,.2);
    border-top: 10px solid #00cc66;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

h1 {
    margin-top: 30px;
}

.progress {
    margin-top: 25px;
    width: 380px;
    height: 12px;
    background: rgba(255,255,255,.2);
    border-radius: 20px;
    overflow: hidden;
}

.bar {
    height: 100%;
    width: 0;
    background: #00cc66;
    animation: loading 3s forwards;
}

@keyframes loading {
    to { width: 100%; }
}
</style>
</head>

<body>

<div class="loader"></div>
<h1>Running simulation...</h1>
<p>Analyzing costs, pricing risk, demand response, and profit potential</p>

<div class="progress">
    <div class="bar"></div>
</div>

<script>
setTimeout(function() {
    window.location.href = "/result";
}, 3000);
</script>

</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>PricePilot Result</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<style>
body {
    font-family: Poppins, Arial, sans-serif;
    margin: 0;
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
    min-height: 100vh;
}

.container {
    max-width: 1100px;
    margin: auto;
    padding: 40px;
}

h1 {
    text-align: center;
    font-size: 42px;
}

.card {
    background: rgba(255,255,255,0.06);
    padding: 25px;
    border-radius: 18px;
    margin: 20px 0;
    box-shadow: 0 20px 45px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.1);
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}

.metric {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 14px;
    text-align: center;
}

.metric p {
    color: #00cc66;
    font-size: 24px;
    font-weight: 800;
}

.insight-box {
    display: none;
    margin-top: 25px;
    line-height: 1.75;
    color: #e5e7eb;
}

.insight-box h2 {
    color: white;
}

.insight-box h3 {
    color: #00cc66;
}

""" + BUTTON_CSS + """

@media (max-width: 768px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>
<div class="container">

<h1>PricePilot Result</h1>

<div class="card">
    <h2>Simulation Result</h2>

    <div class="grid">
        <div class="metric">
            <h3>Current Base Price</h3>
            <p>{{ result.base_price }} VND</p>
        </div>
        <div class="metric">
            <h3>Current Profit</h3>
            <p>{{ result.base_profit }} VND</p>
        </div>
        <div class="metric">
            <h3>Optimal Price Increase</h3>
            <p>{{ result.best_increase }}%</p>
        </div>
    </div>

    <h3>Maximum Expected Profit: {{ result.best_profit }} VND</h3>

    {{ chart | safe }}
</div>

<div class="grid">
    <div class="card">
        <h3>🔴 Aggressive Strategy</h3>
        <p><b>Increase price by {{ result.best_increase }}%</b></p>
        <p>
        This strategy aims to maximize expected profit. It is suitable when demand is strong,
        customers are less price-sensitive, or the business has a strong competitive advantage.
        </p>
    </div>

    <div class="card">
        <h3>🟡 Balanced Strategy</h3>
        <p><b>Increase price by {{ result.balanced_increase }}%</b></p>
        <p>
        This strategy balances profit improvement with customer retention. It is often the most
        practical option for SME manufacturing businesses operating in competitive markets.
        </p>
    </div>

    <div class="card">
        <h3>🟢 Conservative Strategy</h3>
        <p><b>Increase price by 0–5%</b></p>
        <p>
        This strategy protects order volume and cash flow. It is recommended when customers are
        highly price-sensitive or when the company wants to avoid demand volatility.
        </p>
    </div>
</div>

<div class="card">
    <button onclick="toggleInsight()">View detailed insight</button>

    <div id="insightBox" class="insight-box">
        <h2>Detailed Insight</h2>

        <p>
        The simulation indicates that the optimal price increase is
        <b>{{ result.best_increase }}%</b>. At this level, the model estimates the highest expected
        profit among the tested pricing scenarios. This means the additional margin gained from
        the price increase is strong enough to offset the expected decrease in order volume.
        </p>

        <h3>Demand and elasticity interpretation</h3>
        <p>
        Price elasticity plays a key role in this result. A higher elasticity means customers react
        more strongly to price changes, so increasing prices too much can reduce demand quickly.
        A lower elasticity means customers are less sensitive, allowing the business to raise prices
        with lower risk. Therefore, the recommended price increase should always be interpreted
        together with customer behavior and market competition.
        </p>

        <h3>Profit and volume trade-off</h3>
        <p>
        The core trade-off is between margin and volume. A higher selling price improves margin per
        order, but it may reduce the number of accepted orders. A lower price may protect volume,
        but it can limit profit growth. The optimal point is where this trade-off produces the best
        expected profit outcome.
        </p>

        <h3>Strategic recommendation</h3>
        <p>
        The aggressive strategy is appropriate when the company has stable demand, loyal customers,
        specialized production capabilities, or limited direct competition. The balanced strategy is
        recommended when the business wants to improve profitability while still protecting customer
        relationships. The conservative strategy is best when market competition is intense, customers
        are very price-sensitive, or maintaining stable production volume is more important than
        maximizing short-term profit.
        </p>

        <h3>Final business interpretation</h3>
        <p>
        PricePilot should be used as a decision-support tool, not as an automatic pricing rule.
        The final decision should also consider customer contracts, competitor pricing, production
        capacity, material price volatility, cash-flow needs, and the long-term relationship with
        key customers.
        </p>
    </div>
</div>

<a class="btn" href="/input">Try Again</a>

</div>

<script>
function toggleInsight() {
    const box = document.getElementById("insightBox");
    box.style.display = box.style.display === "none" ? "block" : "none";
}
</script>

</body>
</html>
"""


@app.route("/")
def intro():
    return render_template_string(INTRO_HTML)


@app.route("/input")
def input_page():
    return render_template_string(INPUT_HTML)


@app.route("/run", methods=["POST"])
def run_simulation():
    session["form"] = dict(request.form)
    return redirect(url_for("loading"))


@app.route("/loading")
def loading():
    return render_template_string(LOADING_HTML)


@app.route("/result")
def result_page():
    form = session.get("form")

    if not form:
        return redirect(url_for("input_page"))

    material = form["material"]

    tons = float(form["tons"])
    workers = float(form["workers"])
    salary = float(form["salary"])
    electricity_year = float(form["electricity_year"])
    maintenance_year = float(form["maintenance_year"])
    machine_value = float(form["machine_value"])
    machine_life = float(form["machine_life"])
    margin = float(form["margin"])
    win_rate = float(form["win_rate"])
    orders = float(form["orders"])
    elasticity = float(form["elasticity"])
    industry_growth = float(form["industry_growth"])
    income_growth = float(form["income_growth"])
    inflation = float(form["inflation"])

    mat_cost = MATERIAL_PRICE[material] * tons
    labor_cost = workers * salary

    electricity_month = electricity_year / 12
    maintenance_month = maintenance_year / 12
    depreciation = machine_value / (machine_life * 12)

    fixed_cost = electricity_month + maintenance_month + depreciation
    total_cost = mat_cost + labor_cost + fixed_cost

    real_orders = orders * (win_rate / 100)
    cost_per_order = total_cost / max(real_orders, 1)

    base_price = cost_per_order / (1 - margin / 100)
    base_profit = (base_price - cost_per_order) * real_orders

    rows = []

    for inc in range(0, 21, 2):
        demand_change = (
            industry_growth / 100
            + income_growth / 100
            - elasticity * (inc / 100)
        )

        new_orders = real_orders * (1 + demand_change)
        new_cost = cost_per_order * (1 + inflation / 100)
        new_price = base_price * (1 + inc / 100)
        new_profit = (new_price - new_cost) * max(new_orders, 0)

        rows.append({
            "Increase %": inc,
            "Orders": new_orders,
            "Profit": new_profit
        })

    df = pd.DataFrame(rows)

    best = df.loc[df["Profit"].idxmax()]
    balanced_df = df[df["Increase %"] <= 12]
    balanced = balanced_df.loc[balanced_df["Profit"].idxmax()]

    fig = px.line(df, x="Increase %", y="Profit", markers=True)
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="white"
    )
    chart = pio.to_html(fig, full_html=False)

    result = {
        "base_price": f"{base_price:,.0f}",
        "base_profit": f"{base_profit:,.0f}",
        "best_profit": f"{best['Profit']:,.0f}",
        "best_increase": int(best["Increase %"]),
        "balanced_increase": int(balanced["Increase %"])
    }

    return render_template_string(RESULT_HTML, result=result, chart=chart)


if __name__ == "__main__":
    app.run(debug=True)