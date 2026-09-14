# RATHAM AI Implementation Notes

## Custom training
The three datasets are generated from domain-relevant behavioural/operational features rather than copied from a generic benchmark. The generator uses a fixed seed so the experiment is reproducible.

### Need model
Inputs: days since transfusion, usual interval, Hb level, recent Hb drop, fatigue score, prior delays, infection flag, appointment adherence.
Target: need within 7 days.

### Reachability model
Inputs: recent contact load, historical response rate, response latency, distance, availability rate, weekday availability, recent donation interval, opt-in state and night-contact ratio.
Target: reachable/responding.

### Burnout model
Inputs: contact frequency, donation frequency, response/decline behaviour, cooldown history, engagement decline, response latency and opt-outs.
Target: high burnout/disengagement risk.

## Matching policy
The model probabilities are advisory signals. A donor with low reachability is down-ranked; a donor with high burnout risk is down-ranked; backup donors are retained. The system never records a donor as confirmed until an explicit confirmation arrives.

## Production hardening still required
- Replace synthetic data with ethically sourced, consented and clinically validated data.
- Add authentication, RBAC, audit logging and encryption.
- Add blood-group/Rh compatibility rules and medical eligibility checks from authoritative clinical protocols.
- Add PostgreSQL/Redis and real messaging providers only after consent, privacy and compliance review.
- Calibrate models prospectively and monitor drift/fairness.
