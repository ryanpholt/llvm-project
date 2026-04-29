"""
Test that expression evaluation on one thread is not interrupted by a
background thread throwing caught C++ exceptions.

The fix restricts the internal __cxa_allocate_exception breakpoint (set during
expression evaluation) to only fire on the expression's thread, so other
threads throwing and catching exceptions don't interfere.
"""

import lldb
from lldbsuite.test.decorators import *
from lldbsuite.test.lldbtest import *
from lldbsuite.test import lldbutil


class TestExprExceptionThreadSpecificity(TestBase):
    NO_DEBUG_INFO_TESTCASE = True

    @skipIfWindows
    def test_expr_not_interrupted_by_background_exception(self):
        """Evaluate a slow expression while a background thread throws
        caught C++ exceptions.  The expression must complete successfully."""
        self.build()
        source_file = lldb.SBFileSpec("main.cpp")

        (target, process, thread, bkpt) = lldbutil.run_to_source_breakpoint(
            self, "Break here", source_file
        )

        # Use TryAllThreads so the background thread keeps running and
        # throwing exceptions during expression evaluation.
        options = lldb.SBExpressionOptions()
        options.SetTryAllThreads(True)
        options.SetTimeoutInMicroSeconds(5000000)  # 5 second timeout
        options.SetUnwindOnError(True)

        frame = thread.GetFrameAtIndex(0)
        result = frame.EvaluateExpression("slow_function()", options)

        # The expression must succeed — before the fix it would be
        # interrupted by the background thread's exception hitting the
        # process-wide __cxa_allocate_exception breakpoint.
        self.assertSuccess(
            result.GetError(),
            "Expression was interrupted by background thread exception",
        )
        self.assertEqual(result.GetValueAsUnsigned(), 42)
