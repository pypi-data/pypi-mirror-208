from ats_base.service import mm

from ats_case.common.enum import WorkMode, ScriptClazz


class Context(object):
    """
    测试用例上下文
    """

    def __init__(self, sn):
        self._test_sn = sn
        self._parse()

    def _parse(self):
        tl = mm.Dict.get("test:log", self._test_sn)

        self._renew = tl.get('renew', 0)
        self._mode = WorkMode(tl.get('mode'))
        self._tester = self.Tester(tl.get('tester'))
        self._case = self.Case(tl.get('usercase'))
        self._meter = self.Meter(tl.get('meter'))
        self._bench = self.Bench(tl.get('bench'))
        # 运行时
        self._runtime = self.Runtime()
        self._session = self.Session(self)
        # Debug模式 - 测试开发人员本机调试数据比对服务使用
        self._acd_url = tl.get('acd_url')

    @property
    def mode(self):
        return self._mode

    @property
    def renew(self):
        return self._renew

    @property
    def test_sn(self):
        return self._test_sn

    @property
    def tester(self):
        return self._tester

    @property
    def bench(self):
        return self._bench

    @property
    def case(self):
        return self._case

    @property
    def meter(self):
        return self._meter

    @property
    def runtime(self):
        return self._runtime

    @property
    def session(self):
        return self._session

    @property
    def acd_url(self):
        return self._acd_url

    class Tester(object):
        def __init__(self, data: dict):
            self._ip = data.get('ip')
            self._port = data.get('port')
            self._username = data.get('username')
            self._hostname = data.get('hostname')

        @property
        def ip(self):
            return self._ip

        @property
        def port(self):
            return self._port

        @property
        def username(self):
            return self._username

        @property
        def hostname(self):
            return self._hostname

        @property
        def api(self):
            return "http://{}:{}/accept".format(self.ip, self.port)

    class Bench(object):
        def __init__(self, data: dict):
            if data is not None and len(data) > 0:
                self._manufacture = data.get('manufacture', '')
                self._model = data.get('model', '')
                self._port = data.get('port', 0)

        #         self._iabc = data.get('iabc', 'H')
        #
        @property
        def manufacture(self):
            return self._manufacture

        @property
        def model(self):
            return self._model

        @property
        def port(self):
            return self._port

    #
    #     @property
    #     def iabc(self):
    #         return self._iabc
    #
    #     @iabc.setter
    #     def iabc(self, value):
    #         self._iabc = value

    class Case(object):
        def __init__(self, data: dict):
            self._id = data.get('id', -1)
            self._name = data.get('name', 'test')
            #         self._code = data.get('code')
            #         self._version = data.get('version')
            #         self._scope = data.get('scope')
            #         self._purpose = data.get('purpose')
            self._script = ScriptClazz(data.get('script', 1))
            self._control = data.get('control', {})
            self._steps = data.get('steps')

        #         self._script = 'script.{}'.format(data.get('script'))
        #         self._bench_step_orders = data.get('bench_step_orders', [])
        #         # 用户发起的参数
        #         self._req_params = self.ReqParams(data.get('req_params'))
        #
        #         lps = data.get('loops')
        #         if lps is not None and lps != '':
        #             self._loops = []
        #             lps = eval(data.get('loops'))
        #             if type(lps) is list:
        #                 for lp in lps:
        #                     self._loops.append(self.Loop(lp))
        #
        #             if self._script is None:
        #                 raise Exception('Path of script file is null.')
        #             pfs = self._script.split('.')
        #             pfs[-1] = '{}.py'.format(pfs[-1])
        #             if not util.exist(*pfs):
        #                 raise Exception('Script file[{}] is not exist.'.format(self._script))

        @property
        def id(self):
            return self._id

        @property
        def name(self):
            return self._name

        @property
        def script(self):
            return self._script

        @property
        def control(self):
            return self._control

        @property
        def steps(self):
            return self._steps

    #     @property
    #     def code(self):
    #         return self._code
    #
    #     @property
    #     def version(self):
    #         return self._version
    #
    #     @property
    #     def scope(self):
    #         return self._scope
    #
    #     @property
    #     def purpose(self):
    #         return self._purpose
    #
    #     @property
    #     def loops(self):
    #         return self._loops
    #
    #     @property
    #     def script(self):
    #         return self._script
    #
    #     @property
    #     def bench_step_orders(self):
    #         return self._bench_step_orders
    #
    #     @property
    #     def req_params(self):
    #         return self._req_params

    class Meter(object):
        def __init__(self, data: dict):
            self._pos = data.get('pos')
            self._addr = data.get('addr')
            self._no = data.get('no')
            self._protocol = data.get('protocol')
            self._model = data.get('model')
            self._connect = data.get('connect')
            self._rated_voltage = data.get('rated_voltage')
            self._rated_current = data.get('rated_current')
            self._max_current = data.get('max_current')
            self._min_current = data.get('min_current')
            self._transfer_current = data.get('transfer_current')
            self._frequency = data.get('frequency')
            self._mconst = data.get('mconst')
            self._mpluse = data.get('mpluse')
            self._iabc = 'H'

            if self._connect == 0:
                self._iabc = 'A'

        #         self._channel = {'RS485': data.get('baudrate_485'), 'IR': data.get('baudrate_ir'),
        #                          'PLC': data.get('baudrate_plc')}
        #
        #     def get_channel(self, c: CHANNEL):
        #         return func.to_dict(type=c.value, baudrate=self._channel.get(c.value))

        @property
        def pos(self):
            return self._pos

        @property
        def addr(self):
            return self._addr

        @property
        def no(self):
            return self._no

        @property
        def protocol(self):
            return self._protocol

        @property
        def model(self):
            return self._model

        @property
        def connect(self):
            return self._connect

        @property
        def rated_voltage(self):
            return self._rated_voltage

        @property
        def rated_current(self):
            return self._rated_current

        @property
        def max_current(self):
            return self._max_current

        @property
        def min_current(self):
            return self._min_current

        @property
        def transfer_current(self):
            return self._transfer_current

        @property
        def frequency(self):
            return self._frequency

        @property
        def mconst(self):
            return self._mconst

        @property
        def mpluse(self):
            return self._mpluse

        @property
        def iabc(self):
            return self._iabc

    class Runtime(object):
        """
        运行时
        """

        def __init__(self):
            self._step = -1
            self._loop_sn = 0
            self._loop_start_step = 0
            self._loop_end_step = 0
            self._loop_count = 0
            self._loop_index = 0
            self._steps = {}
            # 多帧时使用
            self._final_result = None

        @property
        def step(self):
            return self._step

        @step.setter
        def step(self, value):
            self._step = value

        @property
        def loop_sn(self):
            return self._loop_sn

        @loop_sn.setter
        def loop_sn(self, value):
            self._loop_sn = value

        @property
        def loop_start_step(self):
            return self._loop_start_step

        @loop_start_step.setter
        def loop_start_step(self, value):
            self._loop_start_step = value

        @property
        def loop_end_step(self):
            return self._loop_end_step

        @loop_end_step.setter
        def loop_end_step(self, value):
            self._loop_end_step = value

        @property
        def loop_count(self):
            return self._loop_count

        @loop_count.setter
        def loop_count(self, value):
            self._loop_count = value

        @property
        def loop_index(self):
            return self._loop_index

        @loop_index.setter
        def loop_index(self, value):
            self._loop_index = value

        @property
        def steps(self):
            return self._steps

        @property
        def final_result(self):
            return self._final_result

        @final_result.setter
        def final_result(self, value):
            self._final_result = value

    class Session(object):
        def __init__(self, parent):
            self._parent = parent

        def get(self, name: str, key: str):
            return mm.Dict.get('{}:{}'.format(self._parent.test_sn, name), key)

        def set(self, name: str, key: str, data):
            return mm.Dict.put('{}:{}'.format(self._parent.test_sn, name), key, data)
