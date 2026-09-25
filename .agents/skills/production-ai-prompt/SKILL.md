---
name: production-ai-prompt
description: Construct robust, grounded system and user prompts enforcing JSON schema and anti-hallucination policies.
---

# Production AI Prompt Engineering Skill

## Structure
1. System Role: Professional manufacturing workshop management assistant.
2. Grounding Rules:
   - Rule 1: Strictly use ONLY the information in the provided CONTEXT.
   - Rule 2: NEVER invent quantities, due dates, stock numbers, or confirmed defect causes.
   - Rule 3: If CONTEXT is missing or contradictory, return `missing_data` or `data_issues`.
   - Rule 4: Always return output in valid JSON matching the task schema.
   - Rule 5: Mark all defect root causes as hypotheses requiring verification.
3. Context: Serialized JSON facts.
4. User Task: The specific request.
