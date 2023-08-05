from contextlib import contextmanager
import sentry_sdk
from ddtrace import tracer
from ddtrace.constants import USER_KEEP
from ddtrace import Span


@contextmanager
def instrument(resource_type: str, resource_name: str, service_name: str):
    """
    This context manager will help with the tracing and instrumentation in datadog.
    It automatically takes care of handling the unwanted exceptions properly by sending them to sentry.
    Usage:
        with instrument(resource_type="cron/worker", resource_name="some_name"):
            // write code here
    :param str resource_type: type of the resource being traced. Use `cron` for cron jobs and `worker` for worker jobs
    :param str resource_name: name of the resource being traced. Pass the name of the cron/worker
    Note: Use service name as mentioned in the manifest.
    """
    try:
        with tracer.trace(
            name=resource_type, service=service_name, resource=resource_name
        ):
            item = tracer.context_provider.active()
            if isinstance(item, Span):
                item.context.sampling_priority = USER_KEEP
            else:
                item.sampling_priority = USER_KEEP
            yield
    except Exception as e:
        sentry_sdk.capture_exception(e)
