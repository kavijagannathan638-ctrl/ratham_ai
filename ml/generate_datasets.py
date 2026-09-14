from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data'
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)
n = 5000

# Patient 7-day need dataset
patient = pd.DataFrame({
    'days_since_transfusion': rng.integers(1, 36, n),
    'usual_interval_days': rng.integers(18, 31, n),
    'hb_level': np.clip(rng.normal(8.2, 1.25, n), 5.2, 12.5),
    'recent_hb_drop': np.clip(rng.normal(0.45, 0.35, n), 0, 2.2),
    'fatigue_score': rng.integers(1, 11, n),
    'prior_delay_count': rng.integers(0, 5, n),
    'infection_flag': rng.binomial(1, 0.12, n),
    'appointment_adherence': rng.uniform(0.45, 1.0, n),
})
need_logit = (
    0.20 * patient.days_since_transfusion
    - 0.34 * patient.hb_level
    + 1.20 * patient.recent_hb_drop
    + 0.18 * patient.fatigue_score
    + 0.30 * patient.prior_delay_count
    + 0.75 * patient.infection_flag
    - 0.03 * patient.usual_interval_days
    - 0.8 * patient.appointment_adherence
    - 2.0
)
p_need = 1 / (1 + np.exp(-need_logit))
patient['need_within_7d'] = rng.binomial(1, np.clip(p_need, .02, .98))
patient['urgency_score'] = np.clip(45 + 8*patient.days_since_transfusion - 5*patient.hb_level + 16*patient.recent_hb_drop + 5*patient.fatigue_score + 12*patient.infection_flag, 0, 100)
patient.to_csv(OUT / 'patient_need.csv', index=False)

# Donor reachability dataset
reach = pd.DataFrame({
    'days_since_last_contact': rng.integers(0, 31, n),
    'contacts_last_30d': rng.integers(0, 16, n),
    'response_rate_90d': rng.uniform(0.05, 1.0, n),
    'avg_response_hours': np.clip(rng.lognormal(1.1, 0.7, n), 0.2, 48),
    'distance_km': rng.uniform(0.5, 40, n),
    'availability_rate_90d': rng.uniform(0.05, 1.0, n),
    'weekday_availability': rng.uniform(0.1, 1.0, n),
    'recent_donation_days': rng.integers(10, 220, n),
    'opt_in_active': rng.binomial(1, .88, n),
    'night_contact_ratio': rng.uniform(0, 1, n),
})
reach_logit = (
    2.0*reach.response_rate_90d + 1.7*reach.availability_rate_90d + 0.9*reach.weekday_availability
    - 0.065*reach.contacts_last_30d - 0.025*reach.distance_km
    - 0.035*reach.avg_response_hours - 0.8*reach.night_contact_ratio
    + 0.7*reach.opt_in_active - 1.1
)
p_reach = 1/(1+np.exp(-reach_logit))
reach['reachable'] = rng.binomial(1, np.clip(p_reach, .02, .98))
reach.to_csv(OUT / 'donor_reachability.csv', index=False)

# Burnout / disengagement dataset
burn = pd.DataFrame({
    'contacts_last_14d': rng.integers(0, 13, n),
    'contacts_last_30d': rng.integers(0, 22, n),
    'successful_donations_90d': rng.integers(0, 7, n),
    'days_since_last_donation': rng.integers(5, 240, n),
    'response_rate_30d': rng.uniform(0.0, 1.0, n),
    'decline_rate_30d': rng.uniform(0.0, 1.0, n),
    'cooldown_days_observed': rng.integers(0, 31, n),
    'engagement_drop_pct': rng.uniform(0, 100, n),
    'avg_response_hours': np.clip(rng.lognormal(1.1, .65, n), .2, 48),
    'voluntary_opt_outs': rng.integers(0, 5, n),
})
burn_logit = (
    .20*burn.contacts_last_14d + .075*burn.contacts_last_30d
    + .15*burn.successful_donations_90d + .025*burn.avg_response_hours
    + .035*burn.engagement_drop_pct + .40*burn.decline_rate_30d
    + .45*burn.voluntary_opt_outs - .035*burn.cooldown_days_observed
    - 1.6*burn.response_rate_30d - 1.0
)
p_burn = 1/(1+np.exp(-burn_logit))
burn['burnout_risk'] = rng.binomial(1, np.clip(p_burn, .02, .98))
burn.to_csv(OUT / 'donor_burnout.csv', index=False)
print('Generated:', ', '.join(str(p.name) for p in OUT.glob('*.csv')))
