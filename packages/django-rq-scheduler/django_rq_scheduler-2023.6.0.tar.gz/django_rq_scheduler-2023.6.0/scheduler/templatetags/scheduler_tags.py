from django import template

from scheduler.rq_classes import JobExecution, DjangoQueue
from scheduler.tools import get_scheduled_job

register = template.Library()


@register.filter
def show_func_name(rq_job: JobExecution) -> str:
    try:
        if rq_job.func_name == 'scheduler.tools.run_job':
            job = get_scheduled_job(*rq_job.args)
            return job.function_string()
        return rq_job.func_name
    except Exception as e:
        return repr(e)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def scheduled_job(job: JobExecution):
    scheduled_job = get_scheduled_job(*job.args)
    return scheduled_job.get_absolute_url()


@register.filter
def worker_scheduler_pid(worker):
    return worker.scheduler_pid()


@register.filter
def job_result(job: JobExecution):
    result = job.latest_result()
    return result.type.name.capitalize() if result else None


@register.filter
def job_status(job: JobExecution):
    result = job.get_status()
    return result.capitalize()


@register.filter
def job_runtime(job: JobExecution):
    ended_at = job.ended_at
    if ended_at:
        runtime = job.ended_at - job.started_at
        return f'{int(runtime.microseconds / 1000)}ms'
    elif job.started_at:
        return "Still running"
    else:
        return "-"


@register.filter
def job_scheduled_time(job: JobExecution, queue: DjangoQueue):
    try:
        return queue.scheduled_job_registry.get_scheduled_time(job.id)
    except Exception:
        return None
