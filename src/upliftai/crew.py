# src/upliftai/crew.py
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class UpliftCrew:
    """upliftAI — YAML-configured generator"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def generator(self) -> Agent:
        safe_llm = LLM(
            model="openai/gpt-4o-mini",
            temperature=0,
            # allow enough space for weeks 1..4; raise if you still see truncation
            max_tokens=10000,
            # some CrewAI versions expect request_timeout instead of timeout
            timeout=120,

        )
        return Agent(
            config=self.agents_config["generator"],
            verbose=True,
            llm=safe_llm,
            max_iter=1,
            allow_delegation=False,
        )

    @task
    def program_task(self) -> Task:
        return Task(
            config=self.tasks_config["program_task"],  # from tasks.yaml
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
