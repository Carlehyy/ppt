# Layout Mapping Rules

This document outlines the logic for mapping content types to template layouts.

## Default Mapping Logic

The agent uses a multi-layered approach to select the best layout for each slide:

### 1. LLM-Powered Recommendation

During the **Outline Planning** stage, the LLM is provided with a list of all available layouts from your template, along with their inferred best-use cases (e.g., "Title and Content", "Comparison", "Data Chart").

Based on the `content_type` of the slide being planned (e.g., `achievement_list`, `data_showcase`), the LLM makes an intelligent recommendation for the `layout_index`.

### 2. Name-Based Inference

During the **Template Analysis** stage, the `analyze_template.py` script infers a `best_for` description for each layout based on its name. This provides the LLM with strong hints.

**Common Inferences:**

| Layout Name Contains | Inferred Usage |
| :--- | :--- |
| `title`, `slide` | Cover Page, Section Title |
| `title`, `content` | Standard Content, Bullet Points |
| `section`, `divider` | Section Divider |
| `two`, `comparison` | Comparison, Two-Column Layout |
| `blank` | Custom Content, Flexible Layout |
| `picture`, `image` | Image Showcase |
| `chart`, `data` | Data Chart, Statistics |
| `quote` | Quote, Emphasis |
| `thank`, `end` | End Page, Thank You |

### 3. Fallback Mechanism

If a suitable layout cannot be determined, or if the recommended `layout_index` is invalid, the agent will fall back to a common default, typically the layout named "Title and Content" (often at index 1).

## Customization

While there is no hard-coded mapping file to edit, you can influence the layout selection in several ways:

1.  **Use Clear Layout Names**: When creating your template in PowerPoint, give your layouts descriptive names (e.g., "Comparison - Two Columns", "Data Chart with Title"). This provides the strongest signal to the agent.
2.  **Tune the Outline Planning Prompt**: For advanced control, you can modify the `prompts/outline_planning.txt` prompt to include more specific instructions for the LLM on how to select layouts.
3.  layouts for certain content types.

By providing a well-designed template with clearly named layouts, you empower the agent to make the best possible decisions for structuring your presentation.
