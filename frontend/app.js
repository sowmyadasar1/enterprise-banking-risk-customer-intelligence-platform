/**
 * BankIQ — Frontend Controller
 * Handles navigation, API calls, and result rendering.
 * API key is injected server-side in production; hardcoded here for local dev only.
 */

(() => {
    'use strict';

    // ─── Config (hidden from casual view in production via env injection) ──
    const _cfg = Object.freeze({
        base: 'http://127.0.0.1:8000/api/v1',
        auth: 'enterprise-banking-dev-key-2026',
    });

    // ─── Helpers ───────────────────────────────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    /** Parse a human-formatted number string like "4,500.00" → 4500.00 */
    function num(id) {
        const raw = $(id).value.replace(/,/g, '').trim();
        const n = parseFloat(raw);
        return isNaN(n) ? 0 : n;
    }

    /** Format number as USD */
    function usd(n) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n);
    }

    /** Format number with commas */
    function fmt(n) {
        return new Intl.NumberFormat('en-US').format(Math.round(n));
    }

    function toast(msg, isError = false) {
        const rack = $('#toast-rack');
        const el = document.createElement('div');
        el.className = `toast${isError ? ' error' : ''}`;
        el.textContent = msg;
        rack.appendChild(el);
        setTimeout(() => el.remove(), 3200);
    }

    // ─── API Layer ─────────────────────────────────────────────────────────
    async function api(endpoint, method = 'GET', body = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json', 'X-API-Key': _cfg.auth },
        };
        if (body) opts.body = JSON.stringify(body);

        const t0 = performance.now();
        const res = await fetch(`${_cfg.base}${endpoint}`, opts);
        const ms = (performance.now() - t0).toFixed(1);

        // Update dashboard latency
        const kpi = $('#kpi-latency');
        if (kpi) kpi.textContent = `${ms}ms`;

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        return res.json();
    }

    // ─── Navigation ────────────────────────────────────────────────────────
    function initNav() {
        const titles = {
            home: 'Command Center',
            fraud: 'Fraud Scoring',
            loan: 'Loan Decisioning',
            segment: 'Customer DNA',
            forecast: 'Revenue Forecast',
        };

        $$('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = link.dataset.view;

                $$('.nav-link').forEach(n => n.classList.remove('active'));
                link.classList.add('active');

                $$('.view').forEach(v => v.classList.remove('active'));
                $(`#view-${view}`).classList.add('active');

                $('#page-title').textContent = titles[view] || '';
            });
        });
    }

    // ─── Health Check ──────────────────────────────────────────────────────
    async function checkHealth() {
        const el = $('#conn-status');
        try {
            await fetch(`${_cfg.base}/health`);
            el.innerHTML = '<span class="conn-dot online"></span><span>API Connected</span>';
        } catch {
            el.innerHTML = '<span class="conn-dot offline"></span><span>API Unreachable</span>';
        }
    }

    // ─── Fraud ─────────────────────────────────────────────────────────────
    function initFraud() {
        $('#form-fraud').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('.btn');
            btn.classList.add('loading');
            btn.textContent = 'Scoring…';

            try {
                const payload = {
                    transaction_amount: num('#fr-amount'),
                    merchant_category: $('#fr-merchant').value,
                    transaction_hour: new Date().getHours(),
                    transaction_day_of_week: new Date().getDay(),
                    is_international: parseInt($('#fr-intl').value),
                    is_weekend: [0, 6].includes(new Date().getDay()) ? 1 : 0,
                    customer_age: 35,
                    account_age_days: 365,
                    avg_transaction_amount: 150.0,
                    transaction_count_30d: num('#fr-count30'),
                    amount_std_30d: num('#fr-std30'),
                    distance_from_home: num('#fr-distance'),
                };

                const data = await api('/predict/fraud', 'POST', payload);
                // API shape: { prediction: { is_fraud, fraud_probability, risk_level }, metadata: {...} }
                const p = data.prediction;
                const m = data.metadata;
                const pct = (p.fraud_probability * 100).toFixed(1);

                let riskClass = 'low';
                if (p.risk_level === 'Critical' || p.risk_level === 'High') riskClass = 'high';
                else if (p.risk_level === 'Medium') riskClass = 'med';

                $('#res-fraud').innerHTML = `
                    <div class="result-block">
                        <div class="result-verdict">
                            <div class="verdict-ring risk-${riskClass}">
                                <span class="verdict-pct">${pct}%</span>
                                <span class="verdict-label">Fraud Risk</span>
                            </div>
                            <div>
                                <span class="verdict-tag ${riskClass}">${p.is_fraud ? '⚠ Flagged as Fraud' : '✓ Transaction Cleared'}</span>
                            </div>
                        </div>
                        <div class="result-detail">
                            <div class="detail-row"><span class="detail-key">Risk Level</span><span class="detail-val">${p.risk_level}</span></div>
                            <div class="detail-row"><span class="detail-key">Model</span><span class="detail-val">${m.model_name}</span></div>
                            <div class="detail-row"><span class="detail-key">Inference</span><span class="detail-val">${m.latency_ms}ms</span></div>
                        </div>
                    </div>
                `;
                toast('Fraud assessment complete');
            } catch (err) {
                toast(err.message, true);
            } finally {
                btn.classList.remove('loading');
                btn.textContent = 'Score Transaction';
            }
        });
    }

    // ─── Loan ──────────────────────────────────────────────────────────────
    function initLoan() {
        $('#form-loan').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('.btn');
            btn.classList.add('loading');
            btn.textContent = 'Evaluating…';

            try {
                const payload = {
                    loan_amount: num('#ln-amount'),
                    interest_rate: num('#ln-rate'),
                    loan_term_months: parseInt($('#ln-term').value),
                    credit_score: num('#ln-credit'),
                    debt_to_income_ratio: num('#ln-dti'),
                    annual_income: num('#ln-income'),
                    employment_length_years: 5.0,
                    number_of_accounts: 3,
                    previous_defaults: 0,
                    customer_age: num('#ln-age'),
                };

                const data = await api('/predict/loan-default', 'POST', payload);
                const p = data.prediction;
                const m = data.metadata;
                const pct = (p.default_probability * 100).toFixed(1);

                const actionMap = {
                    'Approve': 'approve',
                    'Review': 'review',
                    'Decline': 'decline',
                };
                const cls = actionMap[p.recommended_action] || 'review';

                let riskClass = 'low';
                if (p.risk_band === 'High') riskClass = 'high';
                else if (p.risk_band === 'Medium') riskClass = 'med';

                $('#res-loan').innerHTML = `
                    <div class="result-block">
                        <div class="decision-banner ${cls}">
                            <div class="decision-action">${p.recommended_action}</div>
                            <div class="decision-sub">${p.risk_band} Risk — ${pct}% default probability</div>
                        </div>
                        <div class="result-verdict" style="padding-top:16px;">
                            <div class="verdict-ring risk-${riskClass}">
                                <span class="verdict-pct">${pct}%</span>
                                <span class="verdict-label">Default</span>
                            </div>
                        </div>
                        <div class="result-detail">
                            <div class="detail-row"><span class="detail-key">Will Default</span><span class="detail-val">${p.will_default ? 'Yes' : 'No'}</span></div>
                            <div class="detail-row"><span class="detail-key">Risk Band</span><span class="detail-val">${p.risk_band}</span></div>
                            <div class="detail-row"><span class="detail-key">Model</span><span class="detail-val">${m.model_name}</span></div>
                            <div class="detail-row"><span class="detail-key">Inference</span><span class="detail-val">${m.latency_ms}ms</span></div>
                        </div>
                    </div>
                `;
                toast('Loan assessment complete');
            } catch (err) {
                toast(err.message, true);
            } finally {
                btn.classList.remove('loading');
                btn.textContent = 'Evaluate Risk';
            }
        });
    }

    // ─── Segmentation ──────────────────────────────────────────────────────
    function initSegment() {
        const personaStyles = {
            'VIP':          { icon: '👑', bg: 'var(--purple-bg)', color: 'var(--purple)' },
            'Mass Market':  { icon: '👥', bg: 'var(--accent-bg)',  color: 'var(--accent)' },
            'Emerging':     { icon: '🌱', bg: 'var(--green-bg)',   color: 'var(--green)' },
            'Dormant':      { icon: '💤', bg: 'var(--amber-bg)',   color: 'var(--amber)' },
        };

        function getStyle(persona) {
            for (const key in personaStyles) {
                if (persona.toLowerCase().includes(key.toLowerCase())) return personaStyles[key];
            }
            return { icon: '🔹', bg: 'var(--surface)', color: 'var(--ink-3)' };
        }

        $('#form-segment').addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('.btn');
            btn.classList.add('loading');
            btn.textContent = 'Analyzing…';

            try {
                const payload = {
                    avg_balance: num('#sg-balance'),
                    total_transactions: num('#sg-txns'),
                    avg_transaction_amount: num('#sg-avg'),
                    tenure_days: num('#sg-tenure'),
                    num_products: num('#sg-products'),
                    credit_score: num('#sg-credit'),
                };

                const data = await api('/predict/segmentation', 'POST', payload);
                const p = data.prediction;
                const m = data.metadata;
                const s = getStyle(p.persona);

                $('#res-segment').innerHTML = `
                    <div class="result-block">
                        <div class="persona-card">
                            <div class="persona-icon" style="background:${s.bg}; color:${s.color};">${s.icon}</div>
                            <div class="persona-name" style="color:${s.color};">${p.persona}</div>
                            <div class="persona-cluster">Cluster ${p.cluster_id}</div>
                            <div class="persona-desc">${p.persona_description || 'No additional description available for this segment.'}</div>
                        </div>
                        <div class="result-detail" style="margin-top:16px;">
                            <div class="detail-row"><span class="detail-key">Model</span><span class="detail-val">${m.model_name}</span></div>
                            <div class="detail-row"><span class="detail-key">Inference</span><span class="detail-val">${m.latency_ms}ms</span></div>
                        </div>
                    </div>
                `;
                toast('Customer segment identified');
            } catch (err) {
                toast(err.message, true);
            } finally {
                btn.classList.remove('loading');
                btn.textContent = 'Identify Persona';
            }
        });
    }

    // ─── Forecast ──────────────────────────────────────────────────────────
    function initForecast() {
        $('#btn-forecast').addEventListener('click', async () => {
            const btn = $('#btn-forecast');
            btn.classList.add('loading');
            btn.textContent = 'Generating…';

            try {
                const metric = $('#fc-metric').value;
                const data = await api(`/forecast/${metric}?horizon=30`);
                const isRevenue = metric === 'revenue';
                const fmtVal = (v) => isRevenue ? usd(v) : fmt(v);

                // Build table rows (show first 7 days, then summary)
                const preview = data.forecast.slice(0, 7);
                const rows = preview.map(d => `
                    <tr>
                        <td>Day ${d.day}</td>
                        <td style="font-weight:500;">${fmtVal(d.mean)}</td>
                        <td>${fmtVal(d.lower_bound)}</td>
                        <td>${fmtVal(d.upper_bound)}</td>
                    </tr>
                `).join('');

                $('#res-forecast').innerHTML = `
                    <div class="result-block">
                        <div class="forecast-summary">
                            <div class="fc-stat">
                                <div class="fc-stat-label">30-Day Cumulative</div>
                                <div class="fc-stat-value">${fmtVal(data.cumulative_total)}</div>
                            </div>
                            <div class="fc-stat">
                                <div class="fc-stat-label">Daily Average</div>
                                <div class="fc-stat-value">${fmtVal(data.cumulative_total / data.horizon_days)}</div>
                            </div>
                        </div>
                        <table class="fc-table">
                            <thead>
                                <tr>
                                    <th>Horizon</th>
                                    <th>Projection</th>
                                    <th>Lower (95%)</th>
                                    <th>Upper (95%)</th>
                                </tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                        <p style="text-align:center; font-size:0.78rem; color:var(--ink-3); margin-top:16px;">
                            Showing 7 of ${data.horizon_days} forecast days · Model: ${data.metadata.model_name}
                        </p>
                    </div>
                `;
                toast('Forecast generated');
            } catch (err) {
                toast(err.message, true);
            } finally {
                btn.classList.remove('loading');
                btn.textContent = 'Generate Forecast';
            }
        });
    }

    // ─── Boot ──────────────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        initNav();
        checkHealth();
        initFraud();
        initLoan();
        initSegment();
        initForecast();
    });
})();
