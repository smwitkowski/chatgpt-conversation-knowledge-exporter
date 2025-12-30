"""DSPy signature and program for atom refinement."""

try:
    import dspy
except ImportError:
    dspy = None  # type: ignore


if dspy:
    class RefineAtoms(dspy.Signature):  # type: ignore
        """
        Refine and consolidate knowledge atoms from multiple chunks.

        Args:
            conversation_id: Conversation identifier
            conversation_title: Conversation title
            candidates_json: JSON string of candidate atoms to refine
            facts_json: Refined facts as JSON array string
            decisions_json: Refined decisions as JSON array string
            open_questions_json: Refined open questions as JSON array string
        """

        conversation_id: str = dspy.InputField(desc="Conversation identifier")
        conversation_title: str = dspy.InputField(desc="Conversation title")
        candidates_json: str = dspy.InputField(desc="JSON string of candidate atoms to refine")
        facts_json: str = dspy.OutputField(desc="Refined facts as JSON array string")
        decisions_json: str = dspy.OutputField(desc="Refined decisions as JSON array string")
        open_questions_json: str = dspy.OutputField(desc="Refined open questions as JSON array string")
else:
    # Placeholder when dspy is not installed
    class RefineAtoms:  # type: ignore
        pass


def create_refine_atoms_program(lm: "dspy.LM") -> "dspy.Module":
    """
    Create a DSPy program for atom refinement.

    Args:
        lm: Configured DSPy language model

    Returns:
        DSPy module for atom refinement
    """
    if dspy is None:
        raise ImportError("dspy-ai is not installed. Install it with: uv sync --extra dspy")

    # Set the LM
    dspy.configure(lm=lm)

    # Create a chain-of-thought program
    class RefineAtomsProgram(dspy.Module):
        def __init__(self):
            super().__init__()
            self.refiner = dspy.ChainOfThought(RefineAtoms)

        def forward(
            self, conversation_id: str, conversation_title: str, candidates_json: str
        ) -> dict[str, str]:
            result = self.refiner(
                conversation_id=conversation_id,
                conversation_title=conversation_title,
                candidates_json=candidates_json,
            )
            return {
                "facts_json": result.facts_json,
                "decisions_json": result.decisions_json,
                "open_questions_json": result.open_questions_json,
            }

    return RefineAtomsProgram()
