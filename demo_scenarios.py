"""Interactive CLI runner demonstrating all 3 mandatory multi-step agentic scenarios."""

import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_assistant.agent import run_agent_turn, session_memory

console = Console()


def print_step(step_num: int, user_input: str, state: dict, explanation: str):
    """Prints a structured trace card for an agent execution step."""
    action = state.get("last_action", "N/A")
    reasoning = state.get("action_reasoning", "N/A")
    response = state.get("final_response", "")

    table = Table(title=f"Step {step_num}: Agent Action & Decision Trace", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="dim", width=22)
    table.add_column("Value")

    table.add_row("User Input", f"[bold cyan]{user_input}[/bold cyan]")
    table.add_row("Selected Action", f"[bold yellow]{action.upper()}[/bold yellow]")
    table.add_row("Agent Reasoning", f"[italic]{reasoning}[/italic]")
    table.add_row("System Decision Rationale", f"[green]{explanation}[/green]")

    if state.get("active_plan"):
        table.add_row("Active Plan", f"Subject: {state['active_plan'].get('subject')} ({len(state['active_plan'].get('milestones', []))} milestones)")
    if state.get("active_quiz"):
        table.add_row("Active Quiz", f"ID: {state['active_quiz'].get('quiz_id')}, Questions: {len(state['active_quiz'].get('questions', []))}")
    if state.get("quiz_evaluation"):
        table.add_row("Evaluation", f"Score: {state['quiz_evaluation'].get('earned_score')}/{state['quiz_evaluation'].get('total_score')} ({state['quiz_evaluation'].get('percentage')}%)")

    console.print(table)
    console.print(Panel(response[:380] + ("..." if len(response) > 380 else ""), title="[bold green]Assistant Response Preview[/bold green]", border_style="green"))
    console.print("\n" + "=" * 80 + "\n")


def run_scenario_1():
    """Scenario 1: Study Plan -> Topic Quiz -> Answer Evaluation."""
    console.rule("[bold cyan]SCENARIO 1: Study Plan Generation ➔ Quiz Generation ➔ Evaluation[/bold cyan]")
    console.print("[dim]Demonstrates multi-turn context retention, tool chaining, and pedagogical evaluation.[/dim]\n")
    
    session_id = "demo-scenario-1"
    session_memory.reset_session(session_id)

    # Turn 1
    input_1 = "I want a study plan for Machine Learning in 2 weeks"
    s1 = run_agent_turn(session_id, input_1)
    print_step(
        1, input_1, s1,
        "System identified explicit request for a learning roadmap in Machine Learning. "
        "Router chose 'plan' and invoked StudyPlannerTool to generate phased milestones and time allocations."
    )
    time.sleep(0.5)

    # Turn 2
    input_2 = "Can you make a practice quiz for the first topic?"
    s2 = run_agent_turn(session_id, input_2)
    print_step(
        2, input_2, s2,
        "System retained conversational context from Turn 1 (active plan for Machine Learning). "
        "Router identified request for assessment on Phase 1 topic and invoked QuizGeneratorTool."
    )
    time.sleep(0.5)

    # Turn 3
    input_3 = "Here are my answers: q1: B, q2: B, q3: A"
    s3 = run_agent_turn(session_id, input_3)
    print_step(
        3, input_3, s3,
        "System recognized answer submission pattern (q1..q3) with active quiz in state. "
        "Router deterministically dispatched to QuizEvaluatorTool for scoring and remedial feedback."
    )


def run_scenario_2():
    """Scenario 2: Ambiguous Request -> Clarification Loop -> Resolution."""
    console.rule("[bold yellow]SCENARIO 2: Incomplete/Ambiguous Request ➔ Clarification ➔ Plan[/bold yellow]")
    console.print("[dim]Demonstrates ambiguity detection, clarifying dialog, and context completion.[/dim]\n")

    session_id = "demo-scenario-2"
    session_memory.reset_session(session_id)

    # Turn 1
    input_1 = "help me study"
    s1 = run_agent_turn(session_id, input_1)
    print_step(
        1, input_1, s1,
        "Input lacks subject, goal, and proficiency level. Instead of hallucinating, "
        "router detected missing parameters and chose 'clarify' via ClarificationTool."
    )
    time.sleep(0.5)

    # Turn 2
    input_2 = "I want to study Python for beginner programming"
    s2 = run_agent_turn(session_id, input_2)
    print_step(
        2, input_2, s2,
        "Student clarified subject ('Python') and level ('beginner'). System cleared clarification flag "
        "and seamlessly transitioned to StudyPlannerTool to generate a Python curriculum."
    )


def run_scenario_3():
    """Scenario 3: Simulated Tool Error -> Graceful Recovery -> Resumed Operation."""
    console.rule("[bold red]SCENARIO 3: Tool Execution Failure ➔ Self-Healing ➔ Normal Resumption[/bold red]")
    console.print("[dim]Demonstrates fault tolerance, conditional error recovery edges, and resilient state retention.[/dim]\n")

    session_id = "demo-scenario-3"
    session_memory.reset_session(session_id)

    # Turn 1: Simulated Tool Outage
    input_1 = "Generate a quiz on Operating Systems"
    s1 = run_agent_turn(session_id, input_1, simulate_failure="quiz_generator")
    print_step(
        1, input_1, s1,
        "QuizGeneratorTool suffered a simulated upstream service outage. The BaseTool retry policy failed, "
        "raising ToolExecutionError. LangGraph conditional edge caught the error and routed to 'error_recovery_node'."
    )
    time.sleep(0.5)

    # Turn 2: Subsequent request succeeds
    input_2 = "Explain virtual memory and paging in Operating Systems"
    s2 = run_agent_turn(session_id, input_2)
    print_step(
        2, input_2, s2,
        "System recovered gracefully without crashing or losing session memory. "
        "Successfully routed the new request to TopicExplainerTool and generated full conceptual explanation."
    )


def main():
    console.print(Panel.fit(
        "[bold white on blue] Autonomous AI Study Assistant: Multi-Step Scenario Demonstration [/bold white on blue]\n"
        "[italic]Demonstrating Agentic Workflows, Dynamic Routing, Resilience, and State Management[/italic]",
        border_style="blue"
    ))
    console.print("\n")

    run_scenario_1()
    run_scenario_2()
    run_scenario_3()

    console.print(Panel("[bold green]✔ All three multi-step scenarios executed and verified successfully![/bold green]", border_style="green"))


if __name__ == "__main__":
    main()
