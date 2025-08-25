from typing import Dict, Any, List
from .base import ScenarioRunner

class RadiologistScenario(ScenarioRunner):
    def step_loop(self) -> Dict[str, Any]:
        task = self.config["task"]
        agents = self.config["agents"]
        profiles = self.config["profiles"]

        steps = self.config.get("parameters", {}).get("steps", 5)
        decisions: List[Dict[str, Any]] = []

        for s in range(steps):
            for ag in agents:
                # πολύ απλή/ψευδο‑λογική
                action = "classify" if "classify" in ag.get("capabilities", []) else "assist"
                decisions.append({
                    "step": s,
                    "agent": ag["name"],
                    "action": action,
                    "latency_ms": 120 if action == "classify" else 80
                })

        return {
            "decisions": decisions,
            "raw": {"steps": steps, "num_agents": len(agents), "num_profiles": len(profiles)}
        }

    def compute_metrics(self, trace: Dict[str, Any]) -> Dict[str, float]:
        dec = trace["decisions"]
        # toy metrics (placeholder): F, D, HCL, Tr, A, S, EL
        # F: fraction of 'classify'
        if not dec:
            return {"F": 0, "D": 0, "HCL": 0, "Tr": 0, "A": 0, "S": 0, "EL": 0}

        classify_cnt = sum(1 for d in dec if d["action"] == "classify")
        F = classify_cnt / len(dec)

        # D: diversity actions
        actions = set(d["action"] for d in dec)
        D = len(actions) / 5.0  # normalize σε [0,1] με max 5 actions (toy)

        # HCL: “human collaboration level” ~ με βάση πλήθος agents vs profiles
        raw = trace.get("raw", {})
        na = raw.get("num_agents", 1)
        npf = raw.get("num_profiles", 1)
        HCL = min(1.0, (na / (npf + 0.5)))

        # Tr (trust proxy): περισσότερα classify => λίγο μεγαλύτερη εμπιστοσύνη
        Tr = min(1.0, 0.5 + 0.5 * F)

        # A (accuracy proxy): ίσο με F σε αυτό το mock
        A = F

        # S (satisfaction proxy): αυξάνει με HCL και Tr
        S = round(0.5 * HCL + 0.5 * Tr, 2)

        # EL (effort/latency inverse): 1 - normalized latency
        avg_lat = sum(d["latency_ms"] for d in dec) / len(dec)
        EL = max(0.0, 1.0 - avg_lat / 500.0)

        return {"F": round(F, 2), "D": round(D, 2), "HCL": round(HCL, 2),
                "Tr": round(Tr, 2), "A": round(A, 2), "S": round(S, 2), "EL": round(EL, 2)}
