"""
Simple test mode registry for dependency injection.

This module provides a lightweight singleton registry that tracks whether
the system should use fake implementations for testing.
"""


class TestModeRegistry:
    """Singleton registry for tracking test mode state."""

    _instance = None
    _test_mode = False

    def __new__(cls) -> "TestModeRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def set_test_mode(cls, enabled: bool = True) -> None:
        """Set test mode on or off."""
        instance = cls()
        instance._test_mode = enabled

    @classmethod
    def is_test_mode(cls) -> bool:
        """Check if we're in test mode."""
        instance = cls()
        return instance._test_mode

    @classmethod
    def reset(cls) -> None:
        """Reset to non-test mode."""
        cls.set_test_mode(False)


# Convenience functions
def set_test_mode(enabled: bool = True) -> None:
    """Set test mode on or off."""
    TestModeRegistry.set_test_mode(enabled)


def is_test_mode() -> bool:
    """Check if we're in test mode."""
    return TestModeRegistry.is_test_mode()


def reset_test_mode() -> None:
    """Reset to non-test mode."""
    TestModeRegistry.reset()
