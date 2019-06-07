# -*- coding: utf-8 -*-


import logging
import time
from thehive4py.models import (CaseTask, Case, CaseTaskLog, CaseObservable,
                               CustomFieldHelper)
import uuid
log = logging.getLogger(__name__)


class CaseCreationModel(object):
    def __init__(self, event, tenant):

        # Case attributes
        user = event['user']
        nature = event['nature']
        case_name = event['case']['name']
        case_id = event['case']['id']
        case_url = event['case']['url']
        case_tags = ['McAfee Investigator', case_id, nature]

        # Task attributes
        task_owner = tenant.hive_user
        # task_start_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        task_start_date = int(time.time()) * 1000
        task_description = "Autogenerated task to track MI case events"
        tasks = [CaseTask(title='MI - analytics investigation',
                          status='InProgress',
                          owner=task_owner,
                          startDate=task_start_date,
                          description=task_description),
                 CaseTask(title='MI - system events',
                          status='InProgress',
                          owner=task_owner,
                          startDate=task_start_date,
                          description=task_description),
                 CaseTask(
                     title='MI - user events',
                     status='Waiting',
                     description="Auto generated task to track MI user events")
                 ]

        # Prepare the custom fields (values are searchable)
        customFields = CustomFieldHelper()\
            .add_boolean('MI-autogenerated', True)\
            .add_string('MI-caseid', case_id)\
            .add_string('MI-user', user)\
            .add_string('MI-nature', nature)\
            .build()

        case = Case(title=case_name,
                    tlp=0,
                    flag=False,
                    description="For additional info see " + case_url,
                    tags=case_tags,
                    tasks=tasks,
                    customFields=customFields)

        self.case = case


class CasePriorityUpdateModel(object):
    def __init__(self, event, tenant):
        priority = event['case']['priority']
        tasklog = CaseTaskLog(
            message="Priority updated to {}".format(priority))
        self.tasklog = tasklog


def case_tasks_log_model(event):
    entity = event['entity']
    return CaseTaskLog(message="{} {} {}".format(
        entity, event['type'], event[entity]['url']))


def case_observable_model(event):

    return CaseObservable(
        dataType=event['observable']['type'],
        message=(event['observable']['description'] +
                 ' ' + event['observable']['url']),
        tags=[event['observable']['id'], event['case']['id']],
        data=str(uuid.uuid4()))