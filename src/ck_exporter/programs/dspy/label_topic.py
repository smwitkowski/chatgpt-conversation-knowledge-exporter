"""DSPy signature and program for topic labeling."""

try:
    import dspy
except ImportError:
    dspy = None  # type: ignore


if dspy:
    class LabelTopic(dspy.Signature):  # type: ignore
        """
        Label a topic cluster based on representative documents and keywords.

        Args:
            representative_docs: Representative conversation documents from the topic cluster
            keywords: Top keywords from the topic model
            name: Short topic name (3-5 words) that captures the main theme
            description: 1-2 sentence description of what this topic is about
        """

        representative_docs: str = dspy.InputField(desc="Representative conversation documents from the topic cluster")
        keywords: str = dspy.InputField(desc="Top keywords from the topic model")
        name: str = dspy.OutputField(desc="Short topic name (3-5 words) that captures the main theme")
        description: str = dspy.OutputField(desc="1-2 sentence description of what this topic is about")
else:
    # Placeholder when dspy is not installed
    class LabelTopic:  # type: ignore
        pass


def create_label_topic_program(lm: "dspy.LM") -> "dspy.Module":
    """
    Create a DSPy program for topic labeling.

    Args:
        lm: Configured DSPy language model

    Returns:
        DSPy module for topic labeling
    """
    if dspy is None:
        raise ImportError("dspy-ai is not installed. Install it with: uv sync --extra dspy")

    # Set the LM with LangSmith tracing if enabled
    from ck_exporter.observability.langsmith import configure_dspy_with_langsmith
    configure_dspy_with_langsmith(lm)

    # Create a simple chain-of-thought program
    class LabelTopicProgram(dspy.Module):
        def __init__(self):
            super().__init__()
            self.labeler = dspy.ChainOfThought(LabelTopic)

        def forward(self, representative_docs: str, keywords: str) -> dict[str, str]:
            result = self.labeler(representative_docs=representative_docs, keywords=keywords)
            return {
                "name": result.name,
                "description": result.description,
            }

    return LabelTopicProgram()
