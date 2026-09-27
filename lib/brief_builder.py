class HandoffBriefBuilder:
    """Builds prompts and verifies output for shift handoff briefs."""

    REQUIRED_SECTIONS = (
        "Shift Summary:",
        "Open Issues:",
        "Action Items:",
        "Follow-Up Questions:",
        "Risk Notes:",
    )

    def _section_list(self):
        return "\n".join(self.REQUIRED_SECTIONS)

    def build_brief_prompt(self, notes):
        if notes is None or not notes.strip():
            raise ValueError("Shift notes cannot be empty.")

        return (
            "You are helping a store manager write a shift handoff brief.\n"
            "Turn the shift notes below into a clear handoff brief for the next shift.\n\n"
            "Use exactly these section labels, in this order:\n"
            f"{self._section_list()}\n\n"
            "Rules:\n"
            "- Only use information from the shift notes. Do not invent names, times, "
            "numbers, or other details.\n"
            "- If a section has no supporting details, write Unknown.\n"
            "- Keep each section short and practical.\n\n"
            f"Shift notes:\n{notes.strip()}"
        )

    def build_revision_prompt(self, feedback):
        if feedback is None or not feedback.strip():
            raise ValueError("Revision feedback cannot be empty.")

        return (
            "Revise the previous shift handoff brief from earlier in this conversation "
            "using the manager's feedback below.\n\n"
            "Keep exactly these section labels, in this order:\n"
            f"{self._section_list()}\n\n"
            "Rules:\n"
            "- Only use information from the original shift notes and the feedback. "
            "Do not invent new details.\n"
            "- If a section has no supporting details, write Unknown.\n\n"
            f"Manager feedback:\n{feedback.strip()}"
        )

    def is_usable_brief(self, response_text):
        if response_text is None or not response_text.strip():
            return False
        return all(section in response_text for section in self.REQUIRED_SECTIONS)

    def format_brief(self, response_text):
        return f"\nShift Handoff Brief\n{response_text}"

    def format_revised_brief(self, response_text):
        return f"\nRevised Shift Handoff Brief\n{response_text}"

    def create_brief(self, ai_client, notes):
        prompt = self.build_brief_prompt(notes)
        response_text = ai_client.send(prompt)

        if not self.is_usable_brief(response_text):
            raise RuntimeError("AI response did not include required sections.")

        return self.format_brief(response_text)

    def revise_brief(self, ai_client, feedback):
        prompt = self.build_revision_prompt(feedback)
        response_text = ai_client.send(prompt)

        if not self.is_usable_brief(response_text):
            raise RuntimeError("AI response did not include required sections.")

        return self.format_revised_brief(response_text)