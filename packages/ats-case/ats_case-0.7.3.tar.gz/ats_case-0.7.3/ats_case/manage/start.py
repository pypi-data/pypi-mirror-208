import os
import threading

import gevent
import pytest

from datetime import datetime

from ats_base.common import func
from ats_base.service import mm

from ats_case.common.enum import WorkMode


def run(**kwargs):
    try:
        mode = WorkMode(kwargs.get('mode'))
        if mode == WorkMode.FORMAL:
            pt = FormalMode(kwargs)
        else:
            pt = DebugMode(kwargs)
        pt.run()
    except:
        pass


class ExecMode(object):
    def __init__(self, data: dict):
        self._data = data
        self._username = self._data.get('tester').get('username', '')
        self._now = datetime.now().strftime('%y%m%d%H%M%S%f')

        self._init()

    def _init(self):
        pass

    def run(self):
        pass

    def _build(self, work_mode: WorkMode, code: str = None):
        if code is None:
            code = 'case'

        user_dir = func.makeDir(func.project_dir(), 'testcase', work_mode.value.lower(), self._username)
        template_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template', 'testcase_v1.tmp')
        script_file = os.path.join(user_dir, 'test_{}.py'.format(code))

        with open(template_file, 'r', encoding='UTF-8') as file:
            content = file.read()
            content = content.replace('{script}', code.upper())
        with open(script_file, 'w', encoding='UTF-8') as file:
            file.write(content)

        return script_file


class FormalMode(ExecMode):
    def _init(self):
        self._sn = self._data.get('test_sn')
        if self._sn is None or len(self._sn) == 0:
            self._sn = self._username.upper() + self._now
            mm.Dict.put('test:log', self._sn, self._data)
            self._save()
        else:  # 断点续测
            self._data = mm.Dict.get('test:log', self._sn)
            self._data['renew'] = 1

        self._cases = self._data.get('cases', [])
        self.meters = self._data.get('meters', [])

    def _save(self):
        pass  # 存数据库

    def run(self):
        while self._cases:
            case_task = self.CaseTask(self, self._cases.pop(0))
            case_task.start()
            case_task.join()

            mm.Dict.put('test:log', self._sn, self._data)

    class CaseTask(threading.Thread):
        def __init__(self, parent, case):
            super(FormalMode.CaseTask, self).__init__()
            self._parent = parent
            self._case = case

        def run(self):
            gs = []
            for meter in self._parent.meters:
                # i = 0 执行操作表台 传入参数index
                gs.append(gevent.spawn(self._parent.exec, self._parent.flush(case=self._case, meter=meter)))

            gevent.joinall(gs)

    def flush(self, case, meter):
        self._data['usercase'] = case
        self._data['meter'] = meter

        test_sn = '{}:{}:{}'.format(self._sn, case['id'], meter['pos'])
        mm.Dict.put('test:log', test_sn, self._data)

        return test_sn

    def exec(self, test_sn):
        pytest.main(["-sv", self._build(WorkMode.FORMAL), '--sn={}'.format(test_sn)])


class DebugMode(ExecMode):
    def _init(self):
        self._test_sn = '{}:{}:{}'.format(self._username.upper() + self._now,
                                          self._data['usercase']['id'], self._data['meter']['pos'])
        mm.Dict.put('test:log', self._test_sn, self._data)

    def run(self):
        pytest.main(["-sv", self._build(WorkMode.DEBUG), '--sn={}'.format(self._test_sn)])
