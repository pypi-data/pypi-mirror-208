# asyncio-task-logger
Allows logging on long-running tasks that throw an exception but are still loaded into memory. By default, a task's future doesn't spit out exceptions until it gets garbage collected or completed. This is a problem for long-running tasks.

# Where this code came from
This solution was created by [Quantlane](https://github.com/qntln "Quantlane on GitHub"), but as they didn't seem to be hosting it on PyPI and it would be convenient for me (and probably others) to have it on PyPI, I created this package.

[Link to the original article on Quantlane's website](https://quantlane.com/blog/ensure-asyncio-task-exceptions-get-logged/)
