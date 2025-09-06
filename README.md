# Upliftt AI: YAML-driven CrewAI generator (Docker)

**UpliftAI** builds a single JSON program (workouts + meals) by running a CrewAI agent configured entirely from YAML. It's fully containerized and writes the result to `output/program.json`.

## Quickstart

### 1. Build the Docker image

From the project root, build the image with a tag:

```bash
docker build -t upliftai:yaml .
```

### 2. Set up your API key

Ensure you have your OpenAI API key in a file named `.env` in the project root.

**.env**
```env
OPENAI_API_KEY=sk-...
```

### 3. Create the output directory

Create a writable directory on your host machine to receive the generated file.

```bash
mkdir -p output
```

### 4. Run the container

This command runs the container, mounts the output directory, and passes your API key from the `.env` file. It will write the result to `output/program.json` on your host.

```bash
docker run --rm -it --env-file .env \
  -v "$PWD/output:/app/output" \
  upliftai:yaml
```

You should see output indicating success:

```
Saved JSON -> /app/output/program.json
```

To view the first 80 lines of the generated file:

```bash
sed -n '1,80p' output/program.json
```

The agent is pinned to `openai/gpt-4o-mini` with `temperature: 0` for stable, strict JSON output.

## What It Does

**UpliftAI** uses CrewAI and YAML (no separate prompt files) to instruct a single "Generator" agent.

- The agent receives a **TEMPLATE** (embedded in `tasks.yaml`) and must output strict JSON with the exact same structure.
- If the template shows only Week 1, the agent expands it to Weeks 1-4 (configurable).
- The runner validates the model's output as JSON and saves it to `output/program.json`.

## Project Layout

```
src/upliftai/
  config/
    agents.yaml     # Agent definition, model, temperature, etc.
    tasks.yaml      # Task description + embedded template
  crew.py           # CrewBase class that loads YAML and pins LLM settings
  main.py           # CLI runner: kickoff + JSON validation + file write
Dockerfile
pyproject.toml
uv.lock
.env / .env.example
output/             # Host-mounted directory for program.json
```

## Configuration

### Agent (model & behavior)

The `src/upliftai/config/agents.yaml` file defines the agent's role, goal, backstory, and LLM settings.

**src/upliftai/config/agents.yaml**
```yaml
generator:
  role: >
    Generator
  goal: >
    Produce a single JSON object that EXACTLY matches the TEMPLATE structure,
    extending weeks as required.
  backstory: >
    Certified fitness & nutrition expert; creates safe, progression-minded plans.
  llm: openai/gpt-4o-mini
  temperature: 0
```

You can change `llm` to another provider/model supported by CrewAI/LiteLLM. The `crew.py` file also hard-pins runtime safety settings like `max_tokens=10000`, `timeout=120`, and single shot (`max_iter=1`).

### Task & Template (weeks, rules, structure)

The `src/upliftai/config/tasks.yaml` file contains the rules, template structure, and the target number of weeks. To generate a different span (e.g., 1-10), edit the language in the `description` and `expected_output` fields.

## Build & Run (Copy/Paste)

### Build

```bash
docker build -t upliftai:yaml .
```

### Run with image-baked YAML

```bash
docker run --rm -it --env-file .env \
  -v "$PWD/output:/app/output" \
  upliftai:yaml
```

### Run while editing YAML (no rebuild required)

```bash
docker run --rm -it --env-file .env \
  -v "$PWD/src/upliftai/config:/app/src/upliftai/config:ro" \
  -v "$PWD/output:/app/output" \
  upliftai:yaml
```

### If you hit host-permission issues

Run the container as your user ID:

```bash
docker run --rm -it --env-file .env \
  -v "$PWD/output:/app/output" \
  --user $(id -u):$(id -g) \
  -e HOME=/tmp -e XDG_DATA_HOME=/tmp/.local/share \
  upliftai:yaml
```

## How It Works (Under the Hood)

1. The **ENTRYPOINT** for the container runs `python -m upliftai.main`.
2. `main.py` calls `UpliftCrew().crew().kickoff()`, validates the JSON response, and writes it to `/app/output/program.json`.
3. `crew.py` sets a strict LLM profile with `temperature=0`, `max_tokens`, and `timeout` to ensure the output is well-structured JSON.

## Customization Tips

- **Change model**: Edit `agents.yaml` or the LLM in `crew.py`.
- **More/fewer weeks**: Update the wording in `tasks.yaml` (e.g., "generate weeks 1..10").
- **Different domain**: Replace the template in `tasks.yaml` with your desired structure; the agent will mirror it.
- **Determinism**: Keep `temperature: 0` and avoid vague instructions.

## Troubleshooting

- **No file created**: Check the container output for "Saved JSON...". Ensure the volume mount is correct (`-v "$PWD/output:/app/output"`).
- **Permission denied**: Make sure `output/` exists on the host and is writable. Use the `--user $(id -u):$(id -g)` option if needed.
- **Truncated/invalid JSON**: Increase `max_tokens` in `crew.py` or tighten the wording in `tasks.yaml`.
- **Slow/thinking**: Lower the prompt size, reduce the number of weeks, or check the timeout setting in `crew.py`.