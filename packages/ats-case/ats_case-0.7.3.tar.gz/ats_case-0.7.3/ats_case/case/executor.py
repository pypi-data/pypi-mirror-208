from importlib import import_module

import gevent
from ats_base.common import func
from ats_base.log.logger import logger

from ats_case.case import translator, command
from ats_case.case.context import Context
from ats_case.common.enum import *
from ats_case.common.error import *


def execute(context: Context):
    try:
        if context.mode == WorkMode.FORMAL:
            FormalExecutor(context).exec()
        else:
            DebugExecutor(context).exec()
    except APIError as ae:
        logger.info(str(ae))
        raise AssertionError(str(ae))
    except ClientError as ce:
        logger.info(str(ce))
        command.client().message(str(ce)).error(context)
        raise AssertionError(str(ce))
    except MeterOperationError as pe:
        logger.info(str(pe))
        command.client().message(str(pe)).error(context)
        raise AssertionError(str(pe))
    except Exception as e:
        logger.error(str(e))
        command.client().message(str(e)).error(context)
        raise AssertionError(str(e))


class Executor(object):
    def __init__(self, context: Context):
        self._context = context
        self._model = None
        self._steps = []

    def exec(self):
        self.handle()

        index = self._load()  # 加载在断点续测时所需关键变量
        while index < len(self._steps):
            self._context.runtime.step = self._steps[index]
            if self.loop_meet():
                self.loop_exec()
            else:
                self.step_exec()

            index = self._steps.index(self._context.runtime.step) + 1

    def handle(self):
        pass

    def _load(self):
        if self._context.renew == 1:
            self._context.runtime.loop_index = self._context.session.get('breakpoint', 'loop_index')
            if self._context.runtime.loop_index == 'NULL':
                self._context.runtime.loop_index = 0

            self._context.runtime.loop_sn = self._context.session.get('breakpoint', 'loop_sn')
            if self._context.runtime.loop_sn == 'NULL':
                self._context.runtime.loop_sn = 0

            try:
                return self._steps.index(self._context.session.get('breakpoint', 'step'))
            except:
                pass

        return 0

    def _flush(self):
        self._context.session.set('breakpoint', 'step', self._context.runtime.step)
        self._context.session.set('breakpoint', 'loop_sn', self._context.runtime.loop_sn)
        self._context.session.set('breakpoint', 'loop_index', self._context.runtime.loop_index)

    def is_exec(self):
        ifs = self._context.case.control.get('ifs')
        if ifs is not None and type(ifs) is dict and len(ifs) > 0:
            for fc, values in ifs.items():
                if command.ats().operation(fc).parameter(values).exec(self._context):
                    return False
        return True

    def step_exec(self):
        if self._context.mode == WorkMode.FORMAL:   # 协程切换
            gevent.sleep(0.05)

        logger.info('~ @TCC-STEP-> steps[#{}] execute'.format(self._context.runtime.step))

        self._flush()  # 缓存在断点续测时所需关键变量
        if self.is_exec():
            getattr(self._model, 'step_{}'.format(self._context.runtime.step))(self._context)

    def loop_meet(self):
        loops = self._context.case.control.get('loops')

        if loops is None or type(loops) is not list or len(loops) <= 0:
            return False

        if self._context.runtime.loop_sn >= len(loops):
            return False
        loop = loops[self._context.runtime.loop_sn]
        ranges = loop.get('range')
        count = loop.get('count')

        step_start = int(ranges.split(':')[0])
        step_end = int(ranges.split(':')[1])

        if step_start <= self._context.runtime.step <= step_end:
            self._context.runtime.loop_start_step = step_start
            self._context.runtime.loop_end_step = step_end
            self._context.runtime.loop_count = int(count)
            return True

        return False

    def loop_exec(self):
        logger.info('~ @TCC-LOOP-> loops[#{}] start. -range {}:{}  -count {}'.format(
            self._context.runtime.loop_sn, self._context.runtime.loop_start_step,
            self._context.runtime.loop_end_step, self._context.runtime.loop_count))

        command.client().message('[#{}]循环开始 - 步骤范围[{}-{}], 共{}次'.format(
            self._context.runtime.loop_sn, self._context.runtime.loop_start_step,
            self._context.runtime.loop_end_step, self._context.runtime.loop_count)).show(self._context)

        while self._context.runtime.loop_index < self._context.runtime.loop_count:
            logger.info('~ @TCC-LOOP-> loops[#{}], -count {}, -index {}'.format(
                self._context.runtime.loop_sn, self._context.runtime.loop_count,
                self._context.runtime.loop_index + 1))
            command.client().message('[#{}]循环 - 共{}次, 当前执行第{}次'.format(
                self._context.runtime.loop_sn, self._context.runtime.loop_count,
                self._context.runtime.loop_index + 1)).show(self._context)

            for step in range(self._context.runtime.loop_start_step, self._context.runtime.loop_end_step + 1):
                index = None
                try:
                    index = self._steps.index(step)
                except ValueError as e:
                    pass

                if index is not None:
                    self._context.runtime.step = step
                    self.step_exec()

            self._context.runtime.loop_index += 1

        self._context.runtime.loop_index = 0

        command.client().message("[#{}]循环结束...".format(self._context.runtime.loop_sn)).show(self._context)
        logger.info('~ @TCC-LOOP-> loops[#{}] end.'.format(self._context.runtime.loop_sn))

        self._context.runtime.loop_sn += 1


def extract_steps(content: list):
    n_s = []
    for s in content:
        if s.upper().find('STEP_') >= 0:
            num = func.extract_digit(s)
            n_s.append(int(num))

    return sorted(n_s)


class FormalExecutor(Executor):
    def handle(self):
        # 分为两种情况: 0. 手动编写脚本 1.自动编写脚本
        if self._context.case.script == ScriptClazz.AUTO:
            self._steps = translator.translate(self._context)
            self._model = import_module('script.auto.{}.tsm_{}'.format(self._context.tester.username.lower()
                                                                       , self._context.meter.pos))
        else:
            self._model = import_module('script.manual.formal.{}'.format(self._context.case.steps))
            self._steps = extract_steps(dir(self._model))


class DebugExecutor(Executor):
    def handle(self):
        if self._context.case.script == ScriptClazz.AUTO:
            self._steps = translator.translate(self._context)
            self._model = import_module('script.auto.{}.tsm_{}'.format(self._context.tester.username.lower()
                                                                       , self._context.meter.pos))
        else:
            self._model = import_module('script.manual.debug.{}'.format(self._context.case.steps))
            self._steps = extract_steps(dir(self._model))
