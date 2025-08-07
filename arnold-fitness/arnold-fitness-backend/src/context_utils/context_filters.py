def filter_current_in_progress_checklist(context: dict) -> dict:
    filtered_context = {
        "test_id": context["test_id"],
        "pt_type": context["pt_type"],
        "scope": context.get("scope", {}),
        "credentials": context.get("credentials", {}),
        "goal": context.get("goal", ""),
        "current_phase_id": context.get("current_phase_id"),
        "findings": context.get("findings", []),
        "evidence": context.get("evidence", []),
        "meta": context.get("meta", {})
    }

    current_phase_id = context.get("current_phase_id")
    checklist = context.get("checklist", [])

    # Trova la fase corrente
    for phase in checklist:
        if phase.get("phase_id") == current_phase_id:
            filtered_tasks = []

            for task in phase.get("tasks", []):
                in_progress_checks = [
                    check for check in task.get("checks", [])
                    if check.get("state") == "in_progress"
                ]
                if in_progress_checks:
                    filtered_tasks.append({
                        "task_id": task["task_id"],
                        "title": task["title"],
                        "checks": in_progress_checks
                    })

            if filtered_tasks:
                filtered_context["checklist"] = [{
                    "phase_id": phase["phase_id"],
                    "title": phase["title"],
                    "tasks": filtered_tasks
                }]
            break

    return filtered_context