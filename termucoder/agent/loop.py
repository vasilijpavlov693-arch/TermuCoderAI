"""Agent Loop — основной цикл агента (v2.0)."""
import json
import os
from termucoder.tools import create_default_registry
from termucoder.agent.prompts import SYSTEM, TASK_PROMPT
from termucoder.agent.history import log_action, log_done, new_session_id
from termucoder.agent.checkpoint import save_checkpoint, load_checkpoint
from termucoder.api import LLMClient


def run_agent(task, max_iterations=10, auto_approve=False, resume=None):
    registry = create_default_registry()
    llm = LLMClient()
    tools_summary = registry.summary()
    system_prompt = SYSTEM.format(tools=tools_summary)

    # Resume or new session
    session_id = resume or new_session_id()
    start_step = 1

    if resume:
        ckpt = load_checkpoint(resume)
        if ckpt:
            history = ckpt.get("history", [])
            context = ckpt.get("context", "")
            start_step = ckpt.get("step", 0) + 1
            task = ckpt.get("task", task)
            print("  Resumed session:", resume)
            print("  From step:", start_step)
        else:
            print("  Checkpoint not found, starting fresh")
            history = []
            context = "Work dir: " + os.getcwd()
    else:
        history = []
        context = "Work dir: " + os.getcwd()

    print()
    print("  Agent:", task)
    print("  Tools:", len(registry.list_tools()))
    print("  Max steps:", max_iterations)
    print("  Session:", session_id)
    print()

    for iteration in range(start_step, max_iterations + 1):
        print("  --- Step %d/%d ---" % (iteration, max_iterations))

        history_text = chr(10).join(history[-10:]) if history else "(no actions yet)"
        user_prompt = TASK_PROMPT.format(
            task=task, context=context, history=history_text,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = llm.chat(messages)

        # Parse response
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                action = json.loads(json_str)
            else:
                print("  Unrecognized:", response[:200])
                history.append("[Step %d] Unrecognized" % iteration)
                continue
        except json.JSONDecodeError:
            print("  JSON error:", response[:200])
            history.append("[Step %d] JSON error" % iteration)
            continue

        # Done
        if action.get("action") == "done":
            result = action.get("result", "Done")
            print("  Done:", result)
            history.append("[Step %d] DONE: %s" % (iteration, result))
            log_action(session_id, iteration, action, result)
            log_done(session_id, result)
            return result

        # Tool call
        if action.get("action") == "tool_call":
            tool_name = action.get("tool", "")
            params = action.get("params", {})

            # Confirmation
            if not auto_approve:
                print("  Tool:", tool_name)
                print("  Params:", json.dumps(params, ensure_ascii=False)[:200])
                try:
                    confirm = input("  Execute? (y/n/q): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("  Cancelled")
                    return "Cancelled"
                if confirm == "q":
                    return "Cancelled"
                if confirm == "n":
                    history.append("[Step %d] Skipped: %s" % (iteration, tool_name))
                    continue

            # Execute
            result = registry.execute(tool_name, **params)
            print("  Result:", result[:300])
            history.append("[Step %d] %s: %s" % (iteration, tool_name, result[:200]))
            context = "Last result: " + result[:500]

            # Log and checkpoint
            log_action(session_id, iteration, action, result)
            save_checkpoint(session_id, task, history, context, iteration)
        else:
            print("  Unknown action:", action)
            history.append("[Step %d] Unknown" % iteration)

    print()
    print("  Limit reached (%d)" % max_iterations)
    return "Limit reached"
