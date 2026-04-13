# Skill Feedback

Use this when the user reports that the skill gave incorrect guidance, is missing information, or could be improved. This is about the skill (agent instructions), not about Supabase the product.

## Steps

1. **Ask permission** — Ask the user if they'd like to submit feedback to the skill maintainers. If they decline, move on.

2. **Draft the issue** — Structure the feedback using these fields:
   - **Skill name:** `supabase-developer`
   - **Reference file:** which specific reference file and section caused the problem
   - **Description:** what guidance was wrong or missing
   - **Expected behavior:** what the correct guidance should be
   - **Context:** what the user was trying to do

3. **Submit** — Create a GitHub Issue on the `supabase/agent-skills` repository using the draft as the issue body. The title must follow this format: `user-feedback: <summary of the problem>`.

4. **Share the result** — Share the issue URL with the user after submission. If submission fails, give the user this link to create the issue manually:

```
https://github.com/supabase/agent-skills/issues/new
```
