---
name: ppt-report-agent
description: Intelligent PPT generation from documents and templates for professional work reports. Use for: creating presentations from Docx/PDF/PPT materials, applying template styles and layouts, generating business reports with structured narratives, and automating slide content based on source materials.
license: MIT
---

# PPT Report Agent

This skill generates professional, editable PowerPoint presentations from source documents and a reference template, following a multi-stage intelligent pipeline.

## Quick Start

### 1. Prerequisites

Ensure dependencies are installed:
```bash
pip install -r /home/ubuntu/skills/ppt-report-agent/requirements.txt
```

Verify your LLM configuration (requires `OPENAI_API_KEY` environment variable).

### 2. Place Your Template

Place your high-quality `.pptx` template inside the `/home/ubuntu/skills/ppt-report-agent/templates/user_templates/` directory.

### 3. Basic Usage

To run the full pipeline, use the `orchestrator.py` script. This is the main entry point for the skill.

```bash
python /home/ubuntu/skills/ppt-report-agent/scripts/orchestrator.py \
  --input /path/to/your/document1.docx /path/to/your/document2.pdf \
  --template /home/ubuntu/skills/ppt-report-agent/templates/user_templates/your_template.pptx
```

Or, from within a Python script:

```python
from ppt_report_agent.scripts.orchestrator import PPTAgentOrchestrator

# Initialize the agent
agent = PPTAgentOrchestrator()

# Run the complete pipeline
output_path, review = agent.run(
    input_files=[
        "/path/to/quarterly_report.docx",
        "/path/to/data_summary.pdf"
    ],
    template_path="/home/ubuntu/skills/ppt-report-agent/templates/user_templates/your_template.pptx"
)

print(f"Generated: {output_path}")
print(f"Review Score: {review.get('overall_score', 0)}/100")
```

## The Multi-Stage Pipeline

The skill follows the PRD-defined five-stage pipeline to ensure high-quality output.

### Stage 1+2: Content Parsing & Template Analysis (Parallel)

- **Content Parsing**: The agent first reads all input documents (`.docx`, `.pdf`, `.pptx`) and uses an LLM to extract structured semantic units (achievements, data points, plans, etc.).
- **Template Analysis**: Concurrently, the agent analyzes the provided `.pptx` template, identifying all available layouts, their placeholder structures, and inferring their best-use cases.

### Stage 0: Intelligent Consultation

Based on the initial analysis, the agent generates targeted questions to clarify the user's intent, such as the presentation scenario, core message, and desired length. In an automated workflow, it proceeds with sensible defaults.

### Stage 3: Outline Planning (User Confirmation Required)

The agent's LLM then acts as a professional presentation designer, creating a logical, story-driven outline. It maps content types to the most suitable layouts from your template and structures the narrative. The agent will present this outline for confirmation before proceeding.

### Stage 4: Slide Generation

Once the outline is confirmed, the agent generates the content for each slide, one by one. The LLM crafts concise, powerful text that fits the constraints of the chosen layout, pulling information from the parsed content pool.

### Stage 5: Global Review

After all slides are generated, the agent performs a final quality check. The LLM reviews the entire presentation against five key dimensions (Content Accuracy, Focus Precision, Logic Coherence, Style Consistency, Quality Standards) and provides a score and suggestions for improvement.

## Advanced Features

### Custom Configuration

You can modify the `config.json` file to tune the agent's behavior, such as changing the LLM model, adjusting temperature, or setting page limits.

### Prompt Tuning

For fine-grained control over the LLM's output, you can edit the prompt templates located in the `/prompts/` directory.

### Layout Mapping

The agent uses a combination of layout name analysis and LLM-driven inference to map content to layouts. For more explicit control, you can consult the `references/layout_mapping_rules.md` file.

## Troubleshooting

- **Template Not Found**: Ensure your template is placed in the `templates/user_templates/` directory and the path is correct.
- **Dependency Errors**: Run `pip install -r requirements.txt` again.
- **LLM Errors**: Check if your `OPENAI_API_KEY` is correctly set as an environment variable.
