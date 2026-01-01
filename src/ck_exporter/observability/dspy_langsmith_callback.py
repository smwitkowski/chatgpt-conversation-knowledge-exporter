"""DSPy callback that emits LangSmith traces for program executions and LM calls."""

import threading
from typing import Any, Dict, Optional

from ck_exporter.logging import get_logger
from ck_exporter.observability.langsmith import get_tracing_metadata

logger = get_logger(__name__)

# Thread-local storage for tracking nested runs
_local = threading.local()


class LangSmithDSPyCallback:
    """
    DSPy callback that creates LangSmith runs for program executions and LM calls.

    This callback uses LangSmith's RunTree to create nested traces that reflect
    the DSPy program structure and individual LM calls.
    """

    def __init__(self):
        """Initialize the callback."""
        self._langsmith_available = self._check_langsmith_available()
        if self._langsmith_available:
            from langsmith.run_trees import RunTree
            self._run_tree_class = RunTree
        else:
            self._run_tree_class = None

    def _check_langsmith_available(self) -> bool:
        """Check if langsmith is available."""
        try:
            import langsmith
            return True
        except ImportError:
            return False

    def _get_current_run_tree(self) -> Optional[Any]:
        """Get the current run tree from thread-local storage."""
        return getattr(_local, 'current_run_tree', None)

    def _set_current_run_tree(self, run_tree: Optional[Any]) -> None:
        """Set the current run tree in thread-local storage."""
        _local.current_run_tree = run_tree

    def on_module_start(self, call_id: str, inputs: Dict[str, Any], **kwargs) -> None:
        """Called when a DSPy module starts execution."""
        if not self._langsmith_available:
            return

        try:
            # Get tracing metadata from context
            metadata = get_tracing_metadata()
            step = metadata.get("step", "dspy_module")
            
            # Build name with step if available
            name = f"DSPy {step}"
            if "conversation_id" in metadata:
                name += f" (conv: {metadata['conversation_id'][:16]}...)"
            elif "topic_id" in metadata:
                name += f" (topic: {metadata['topic_id']})"
            
            # Create a new run tree for this module
            # Include metadata in inputs for visibility
            enhanced_inputs = {**inputs}
            if metadata:
                enhanced_inputs["_metadata"] = metadata
            
            run_tree = self._run_tree_class(
                run_type="chain",
                name=name,
                inputs=enhanced_inputs,
                tags=["dspy", "module", step],
            )

            # Link to parent run if one exists
            parent_run = self._get_current_run_tree()
            if parent_run:
                run_tree.parent_run_id = parent_run.id

            # Start the run
            run_tree.post()

            # Store as current for nested calls
            self._set_current_run_tree(run_tree)

            logger.debug(
                "Started DSPy module run",
                extra={
                    "event": "observability.dspy.module_start",
                    "call_id": call_id,
                    "run_id": run_tree.id,
                    "step": step,
                },
            )

        except Exception as e:
            logger.debug(
                "Failed to create DSPy module run",
                extra={
                    "event": "observability.dspy.module_start_error",
                    "call_id": call_id,
                    "error": str(e),
                },
            )

    def on_module_end(self, call_id: str, outputs: Dict[str, Any], exception: Optional[Exception], **kwargs) -> None:
        """Called when a DSPy module ends execution."""
        if not self._langsmith_available:
            return

        try:
            current_run = self._get_current_run_tree()
            if current_run:
                # End the current run
                current_run.end(outputs=outputs, error=str(exception) if exception else None)
                current_run.patch()

                # Restore parent run (if any)
                # Note: This is a simple stack - in practice DSPy may have more complex nesting
                self._set_current_run_tree(None)

                logger.debug(
                    "Ended DSPy module run",
                    extra={
                        "event": "observability.dspy.module_end",
                        "call_id": call_id,
                        "run_id": current_run.id,
                        "exception": str(exception) if exception else None,
                    },
                )

        except Exception as e:
            logger.debug(
                "Failed to end DSPy module run",
                extra={
                    "event": "observability.dspy.module_end_error",
                    "call_id": call_id,
                    "error": str(e),
                },
            )

    def on_lm_start(self, call_id: str, messages: list[Dict[str, Any]], **kwargs) -> None:
        """Called when a DSPy LM call starts."""
        if not self._langsmith_available:
            return

        try:
            # Extract model info if available
            model = kwargs.get("model", "unknown")
            temperature = kwargs.get("temperature", "unknown")
            
            # Get tracing metadata from context
            metadata = get_tracing_metadata()
            step = metadata.get("step", "dspy_lm")

            # Create a run tree for this LM call
            # Include metadata in inputs for visibility
            enhanced_inputs = {
                "messages": messages,
                "model": model,
                "temperature": temperature,
            }
            if metadata:
                enhanced_inputs["_metadata"] = metadata
            
            lm_run = self._run_tree_class(
                run_type="llm",
                name=f"DSPy LM Call ({model})",
                inputs=enhanced_inputs,
                tags=["dspy", "llm", model, step],
            )

            # Link to current module run if one exists
            parent_run = self._get_current_run_tree()
            if parent_run:
                lm_run.parent_run_id = parent_run.id

            # Start the run
            lm_run.post()

            # Store LM run in thread-local for completion
            _local.current_lm_run = lm_run

            logger.debug(
                "Started DSPy LM run",
                extra={
                    "event": "observability.dspy.lm_start",
                    "call_id": call_id,
                    "run_id": lm_run.id,
                    "model": model,
                    "step": step,
                },
            )

        except Exception as e:
            logger.debug(
                "Failed to create DSPy LM run",
                extra={
                    "event": "observability.dspy.lm_start_error",
                    "call_id": call_id,
                    "error": str(e),
                },
            )

    def on_lm_end(self, call_id: str, outputs: Any, exception: Optional[Exception], **kwargs) -> None:
        """Called when a DSPy LM call ends."""
        if not self._langsmith_available:
            return

        try:
            lm_run = getattr(_local, 'current_lm_run', None)
            if lm_run:
                # End the LM run
                lm_run.end(outputs={"response": outputs}, error=str(exception) if exception else None)
                lm_run.patch()

                # Clear the LM run
                _local.current_lm_run = None

                logger.debug(
                    "Ended DSPy LM run",
                    extra={
                        "event": "observability.dspy.lm_end",
                        "call_id": call_id,
                        "run_id": lm_run.id,
                        "exception": str(exception) if exception else None,
                    },
                )

        except Exception as e:
            logger.debug(
                "Failed to end DSPy LM run",
                extra={
                    "event": "observability.dspy.lm_end_error",
                    "call_id": call_id,
                    "error": str(e),
                },
            )

    # Fallback methods for different DSPy versions
    def on_tool_start(self, *args, **kwargs) -> None:
        """Called when a DSPy tool starts (if available in DSPy version)."""
        pass

    def on_tool_end(self, *args, **kwargs) -> None:
        """Called when a DSPy tool ends (if available in DSPy version)."""
        pass

    def on_adapter_start(self, *args, **kwargs) -> None:
        """Called when a DSPy adapter starts (if available in DSPy version)."""
        pass

    def on_adapter_end(self, *args, **kwargs) -> None:
        """Called when a DSPy adapter ends (if available in DSPy version)."""
        pass
