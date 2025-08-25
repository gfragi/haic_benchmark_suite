from typing import Dict, Any, List
from .base import ScenarioRunner

class KitchenScenario(ScenarioRunner):
    """Μικροσενάριο πάνω στη λογική 'cooks': move -> pick -> place -> deliver."""
    def step_loop(self) -> Dict[str, Any]:
        task = self.config["task"]
        agents = self.config["agents"]
        profiles = self.config["profiles"]

        steps = self.config.get("parameters", {}).get("steps", 8)
        decisions: List[Dict[str, Any]] = []

        for s in range(steps):
            for ag in agents:
                # toy FSM
                if s % 4 == 0:
                    action = "move"
                elif s % 4 == 1:
                    action = "pickup"
                elif s % 4 == 2:
                    action = "place_in_pot"
                else:
                    action = "deliver"

                decisions.append({
                    "step": s,
                    "agent": ag["name"],
                    "action": action,
                    "reward": 1.0 if action in ("place_in_pot", "deliver") else 0.0
                })

        return {
            "decisions": decisions,
            "raw": {"steps": steps, "num_agents": len(agents), "num_profiles": len(profiles)}
        }

    def compute_metrics(self, trace: Dict[str, Any]) -> Dict[str, float]:
        dec = trace["decisions"]
        if not dec:
            return {"F":0,"D":0,"HCL":0,"Tr":0,"A":0,"S":0,"EL":0}

        total_rew = sum(d.get("reward", 0.0) for d in dec)
        steps = trace["raw"]["steps"]
        # F: fraction of “productive” actions
        productive = sum(1 for d in dec if d["action"] in ("place_in_pot","deliver"))
        F = productive / len(dec)

        # D: diversity των actions
        actions = set(d["action"] for d in dec)
        D = min(1.0, len(actions)/6.0)

        # HCL: συνεργασία ~ αν >1 agents, μεγαλύτερη
        na = trace["raw"]["num_agents"]
        HCL = 0.5 if na == 1 else 0.8

        # Trust proxy: συνάρτηση του μέσου reward per step
        Tr = min(1.0, (total_rew/steps)/2.0 + 0.4)

        # Accuracy proxy: ίσο με F εδώ
        A = F

        # Satisfaction: μίξη HCL & Tr
        S = round(0.5*HCL + 0.5*Tr, 2)

        # Effort/Latency (EL): proxy 1 - steps normalized
        EL = max(0.0, 1 - steps/20.0)

        return {"F": round(F,2), "D": round(D,2), "HCL": round(HCL,2),
                "Tr": round(Tr,2), "A": round(A,2), "S": round(S,2), "EL": round(EL,2)}
