from crewai import Agent, Task, Crew

def build_crew():
    researcher = Agent(
        role="Researcher",
        goal="Find concise, accurate facts",
        backstory="You read docs and extract the signal.",
        verbose=True,
    )
    writer = Agent(
        role="Writer",
        goal="Explain findings clearly in bullet points",
        backstory="You turn research into crisp summaries.",
        verbose=True,
    )
    t1 = Task(
        description="Research CrewAI core concepts and typical patterns.",
        agent=researcher,
        expected_output="A short fact list with references."
    )
    t2 = Task(
        description="Summarize the research for a newcomer.",
        agent=writer,
        expected_output="Five bullets, no fluff."
    )
    return Crew(agents=[researcher, writer], tasks=[t1, t2])
