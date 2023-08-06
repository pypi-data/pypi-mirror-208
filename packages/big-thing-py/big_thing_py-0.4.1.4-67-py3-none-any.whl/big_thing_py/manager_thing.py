from big_thing_py.big_thing import *
from big_thing_py.staff_thing import *
from big_thing_py.manager import *
import uuid


class MXManagerThing(MXBigThing, metaclass=ABCMeta):

    MANAGER_THREAD_TIME_OUT = THREAD_TIME_OUT

    def __init__(self, name: str, service_list: List[MXService], alive_cycle: float, is_super: bool = False, is_parallel: bool = True,
                 ip: str = None, port: int = None, ssl_ca_path: str = None, ssl_enable: bool = False, log_name: str = None, log_enable: bool = True, log_mode: MXPrintMode = MXPrintMode.ABBR, append_mac_address: bool = True,
                 manager_mode: MXManagerMode = MXManagerMode.SPLIT, scan_cycle=5):
        super().__init__(name, service_list, alive_cycle, is_super, is_parallel, ip, port,
                         ssl_ca_path, ssl_enable, log_name, log_enable, log_mode, append_mac_address)

        self._scan_cycle = scan_cycle
        self._manager_mode = MXManagerMode.get(
            manager_mode) if isinstance(manager_mode, str) else manager_mode

        self._staff_thing_list: List[MXStaffThing] = []
        self._manager_mode_handler = ManagerModeHandler(
            mode=self._manager_mode)

        self._last_scan_time = 0

        # Threading
        self._thread_func_list += [
            self._scan_staff_message_thread_func,
            self._receive_staff_message_thread_func,
            self._publish_staff_message_thread_func
        ]

    # override
    def run(self):
        try:
            # Start main threads
            for thread in self._comm_thread_list + self._thread_list:
                thread.start()

            if self._manager_mode == MXManagerMode.JOIN:
                # Register try
                retry = 5
                while not self._registered and retry:
                    MXLOG_DEBUG(f'Register try {6-retry}', 'yellow')
                    retry -= 1

                    # FIXME: Need to override to fit managerThing (Receive StaffThing as a factor)
                    self._subscribe_init_topic_list(self)
                    self._send_TM_REGISTER()

                    current_time = get_current_time()
                    while get_current_time() - current_time < 5:
                        if self._registered:
                            break
                        else:
                            time.sleep(0.1)
            elif self._manager_mode == MXManagerMode.SPLIT:
                # SPLIT 모드일 땐, manager thing 자기자신은 등록하지 않는다.
                pass
            else:
                pass

            # Maintain main thread
            while not self._g_exit.wait(THREAD_TIME_OUT):
                time.sleep(1000)
        except KeyboardInterrupt as e:
            MXLOG_DEBUG('Ctrl + C Exit', 'red')
            return self.wrapup()
        except ConnectionRefusedError as e:
            MXLOG_DEBUG(
                'Connection error while connect to broker. Check ip and port', 'red')
            return self.wrapup()
        except Exception as e:
            print_error(e)
            return self.wrapup()

    # override
    def wrapup(self):
        try:
            for staff_thing in self._staff_thing_list:
                self._send_TM_UNREGISTER()
            cur_time = get_current_time()

            self._g_exit.set()
            for thread in self._thread_list:
                thread.join()
                MXLOG_DEBUG(f'{thread._name} is terminated', 'yellow')

            while not ((self._publish_queue.empty() and self._receive_queue.empty()) or (get_current_time() - cur_time > 3)):
                time.sleep(THREAD_TIME_OUT)

            self._g_comm_exit.set()
            for thread in self._comm_thread_list:
                thread.join()
                MXLOG_DEBUG(f'{thread._name} is terminated', 'yellow')

            self._mqtt_client.disconnect()
            MXLOG_DEBUG('Thing Exit', 'red')
            return True
        except Exception as e:
            print_error(e)
            return False

    # ===========================================================================================
    #  _    _                             _    __                      _    _
    # | |  | |                           | |  / _|                    | |  (_)
    # | |_ | |__   _ __   ___   __ _   __| | | |_  _   _  _ __    ___ | |_  _   ___   _ __   ___
    # | __|| '_ \ | '__| / _ \ / _` | / _` | |  _|| | | || '_ \  / __|| __|| | / _ \ | '_ \ / __|
    # | |_ | | | || |   |  __/| (_| || (_| | | |  | |_| || | | || (__ | |_ | || (_) || | | |\__ \
    #  \__||_| |_||_|    \___| \__,_| \__,_| |_|   \__,_||_| |_| \___| \__||_| \___/ |_| |_||___/
    # ===========================================================================================

    # override
    def _alive_publishing_thread_func(self, stop_event: Event) -> Union[bool, None]:
        try:
            while not stop_event.wait(THREAD_TIME_OUT):
                if self._manager_mode == MXManagerMode.JOIN:
                    current_time = get_current_time()
                    if current_time - self._last_alive_time > self._alive_cycle:
                        for staff_thing in self._staff_thing_list:
                            self._send_TM_ALIVE()
                            staff_thing._last_alive_time = current_time
                elif self._manager_mode == MXManagerMode.SPLIT:
                    # split 모드일 때는 staff thing이 alive 신호를 받아서 보내므로 생략
                    # current_time = get_current_time()
                    # for staff_thing in self._staff_thing_list:
                    #     if current_time - staff_thing._last_alive_time > staff_thing._alive_cycle:
                    #         self._send_TM_ALIVE()
                    #         staff_thing._last_alive_time = current_time
                    pass
                else:
                    raise Exception('Invalid Manager Mode')
        except Exception as e:
            stop_event.set()
            print_error(e)
            return False

    # override
    def _value_publishing_thread_func(self, stop_event: Event) -> Union[bool, None]:
        try:
            while not stop_event.wait(THREAD_TIME_OUT):
                for staff_thing in self._staff_thing_list:
                    if not staff_thing._registered:
                        continue
                    current_time = get_current_time()
                    for value in staff_thing._value_list:
                        if not (current_time - value.get_last_update_time()) > value.get_cycle():
                            continue
                        arg_list = tuple(value.get_arg_list())
                        if value.update(*arg_list) is not None:
                            self._send_TM_VALUE_PUBLISH(value=value)
        except Exception as e:
            stop_event.set()
            print_error(e)
            return False

    ############################################################################################################################

    def _scan_staff_message_thread_func(self, stop_event: Event):
        try:
            staff_thing_info_list = []

            while not stop_event.wait(self.MANAGER_THREAD_TIME_OUT):
                if not (get_current_time() - self._last_scan_time > self._scan_cycle):
                    continue

                staff_thing_info_list = self._scan_staff_thing()
                if staff_thing_info_list == False:
                    raise Exception('Scan staff thing error')

                old_staff_thing_list = [
                    staff_thing for staff_thing in self._staff_thing_list]
                new_staff_thing_list: List[MXStaffThing] = []
                latest_staff_thing_list: List[MXStaffThing] = []
                removed_staff_thing_list: List[MXStaffThing] = []
                for staff_thing_info in staff_thing_info_list:
                    staff_thing = self._create_staff(staff_thing_info)

                    staff_thing_level, staff_thing = self._check_staff_thing_duplicate(
                        staff_thing)
                    latest_staff_thing_list.append(staff_thing)
                    if staff_thing_level == MXNewStaffThingLevel.NEW:
                        MXLOG_DEBUG(
                            f'New staff_thing!!! name: [{staff_thing.get_name()}]', 'green')
                        new_staff_thing_list.append(staff_thing)
                    elif staff_thing_level == MXNewStaffThingLevel.DUPLICATE:
                        MXLOG_DEBUG(
                            f'Staff thing [{staff_thing.get_name()}] was still alive...', 'yellow')

                removed_staff_thing_list = [
                    item for item in old_staff_thing_list if item not in latest_staff_thing_list]
                for staff_thing in new_staff_thing_list:
                    self._staff_thing_list.append(staff_thing)
                    self._connect_staff_thing(staff_thing)
                for staff_thing in removed_staff_thing_list:
                    try:
                        self._disconnect_staff_thing(staff_thing)
                        self._staff_thing_list.remove(staff_thing)
                    except ValueError:
                        raise Exception(f'[{get_current_function_name()}][{staff_thing.get_name()}] is not in staff thing list')

                staff_thing_info_list = None
                self._last_scan_time = get_current_time()
        except Exception as e:
            stop_event.set()
            print_error(e)
            return False

    def _receive_staff_message_thread_func(self, stop_event: Event):
        try:
            while not stop_event.wait(self.MANAGER_THREAD_TIME_OUT):
                staff_msg = self._receive_staff_message()
                if staff_msg is None:
                    continue
                self._handle_staff_message(staff_msg)
        except Exception as e:
            stop_event.set()
            print_error(e)
            return False

    def _publish_staff_message_thread_func(self, stop_event: Event):
        try:
            while not stop_event.wait(self.MANAGER_THREAD_TIME_OUT):
                for staff_thing in self._staff_thing_list:
                    if not staff_thing.is_connected() or not staff_thing.get_registered():
                        continue
                    staff_msg = staff_thing._publish_queue.get(
                        timeout=self.MANAGER_THREAD_TIME_OUT)
                    self._publish_staff_message(staff_msg)
        except Empty as e:
            pass
        except Exception as e:
            stop_event.set()
            print_error(e)
            return False

    # ====================================================================================================================
    #  _                        _  _        ___  ___ _____  _____  _____
    # | |                      | || |       |  \/  ||  _  ||_   _||_   _|
    # | |__    __ _  _ __    __| || |  ___  | .  . || | | |  | |    | |    _ __ ___    ___  ___  ___   __ _   __ _   ___
    # | '_ \  / _` || '_ \  / _` || | / _ \ | |\/| || | | |  | |    | |   | '_ ` _ \  / _ \/ __|/ __| / _` | / _` | / _ \
    # | | | || (_| || | | || (_| || ||  __/ | |  | |\ \/' /  | |    | |   | | | | | ||  __/\__ \\__ \| (_| || (_| ||  __/
    # |_| |_| \__,_||_| |_| \__,_||_| \___| \_|  |_/ \_/\_\  \_/    \_/   |_| |_| |_| \___||___/|___/ \__,_| \__, | \___|
    #                                                                                                         __/ |
    #                                                                                                        |___/
    # ====================================================================================================================

    # override
    def _handle_MT_RESULT_REGISTER(self, msg: mqtt.MQTTMessage):
        register_result_msg = MXRegisterResultMessage(msg)
        target_staff_thing = self._get_staff_thing_by_name(
            register_result_msg.thing_name)

        if target_staff_thing is False:
            MXLOG_DEBUG(
                f'[{get_current_function_name()}] Wrong payload arrive... {self._name} should be arrive, not {register_result_msg.thing_name}', 'red')
            raise

        if self._manager_mode == MXManagerMode.JOIN:
            # FIXME: This method will be deprecated
            ret = self._check_register_result(
                register_result_msg.error, thing=target_staff_thing)
            if ret:
                self._middleware_name = register_result_msg.middleware_name
                self._registered = True
                # FIXME: Need to override to fit managerThing (Receive StaffThing as a factor)
                self._subscribe_service_topic_list(self)
                self._send_RESULT_REGISTER_staff_message(
                    target_staff_thing, register_result_msg.payload)
            else:
                MXLOG_DEBUG(
                    f'[{get_current_function_name()}] Register failed... error code : {register_result_msg.error}')
        elif self._manager_mode == MXManagerMode.SPLIT:
            # FIXME: This method will be deprecated
            ret = self._check_register_result(
                register_result_msg.error, thing=target_staff_thing)
            if ret:
                target_staff_thing.set_middleware_name(
                    register_result_msg.middleware_name)
                target_staff_thing.set_registered(True)
                # FIXME: Need to override to fit managerThing (Receive StaffThing as a factor)
                self._subscribe_service_topic_list(target_staff_thing)
                self._send_RESULT_REGISTER_staff_message(
                    target_staff_thing, register_result_msg.payload)
            else:
                MXLOG_DEBUG(
                    f'[{get_current_function_name()}] Register failed... error code : {register_result_msg.error}')

    # override
    def _handle_MT_RESULT_UNREGISTER(self, msg: mqtt.MQTTMessage):
        unregister_result_msg = MXUnregisterResultMessage(msg)
        target_staff_thing = self._get_staff_thing_by_name(
            unregister_result_msg.thing_name)

        if target_staff_thing is False:
            MXLOG_DEBUG(
                f'[{get_current_function_name()}] Wrong payload arrive... {self._name} should be arrive, not {unregister_result_msg.thing_name}', 'red')
            raise

        if self._manager_mode == MXManagerMode.JOIN:
            # FIXME: This method will be deprecated
            if self._check_register_result(unregister_result_msg.error):
                self._registered = False
                self._unsubscribe_all_topic_list(self)
                self._send_RESULT_UNREGISTER_staff_message(
                    target_staff_thing, unregister_result_msg.payload)
            else:
                MXLOG_DEBUG(
                    f'[{get_current_function_name()}] Unregister failed... error code : {unregister_result_msg.error}')
        elif self._manager_mode == MXManagerMode.SPLIT:
            # manager thing의 토픽중 해당 staff thing에 관련된 것만 unsubscribe한다
            # FIXME: This method will be deprecated
            if self._check_register_result(unregister_result_msg.error):
                target_staff_thing._registered = False
                self._unsubscribe_all_topic_list(target_staff_thing)
                for topic in self._subscribed_topic_set:
                    if target_staff_thing.get_name() in topic:
                        self._unsubscribe(topic, thing=target_staff_thing)
                self._send_RESULT_UNREGISTER_staff_message(
                    target_staff_thing, unregister_result_msg.payload)
            else:
                MXLOG_DEBUG(
                    f'[{get_current_function_name()}] Unregister failed... error code : {unregister_result_msg.error}')

    @override
    def _handle_MT_EXECUTE(self, msg: mqtt.MQTTMessage):
        execute_msg = MXExecuteMessage(msg)

        target_staff_thing = self._get_staff_thing_by_name(
            execute_msg.thing_name)
        target_function = target_staff_thing._get_function(
            execute_msg.function_name)

        if target_function:
            execute_thread = target_function.start_execute_thread(execute_msg)
        else:
            MXLOG_DEBUG('function not exist', 'red')
            return False

    # ========================
    #         _    _  _
    #        | |  (_)| |
    #  _   _ | |_  _ | | ___
    # | | | || __|| || |/ __|
    # | |_| || |_ | || |\__ \
    #  \__,_| \__||_||_||___/
    # ========================

    @abstractmethod
    def _scan_staff_thing(self, timeout: float) -> List[dict]:
        '''
            지속적으로 staff thing을 발견하여 정보를 수집하여 반환하는 함수.
            timeout을 지정하여 한 번 staff thing을 검색하는데 소요될 시간을 지정할 수 있다.

            Args: 
                timeout (float): staff thing을 검색하는데 소요될 시간 

            Returns:
                List[dict]: staff thing의 정보를 담고 있는 리스트
        '''
        pass

    @abstractmethod
    def _receive_staff_message(self) -> str:
        '''
            staff thing으로부터 메시지를 수신하여 반환하는 함수. 

            Args: 
                (None)

            Returns:
                str: 수신받은 staff thing의 메시지
        '''
        pass

    @abstractmethod
    def _publish_staff_message(self, staff_msg: str) -> None:
        '''
            staff thing에 메시지를 전송하는 함수.
            staff thing의 프로토콜에 맞게 staff_msg를 전송한다.

            Args: 
                staff_msg (str): staff thing에 전송할 메시지

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _parse_staff_message(self, staff_msg) -> Tuple[MXProtocolType, str, str]:
        '''
            staff thing으로 부터 받은 패킷이 어느 MySSIX 프로토콜에 해당하는지 파싱하는 함수.
            staff thing가 보내는 패킷의 프로토콜은 다음 MySSIX 프로토콜 중에 하나로 분류가 되어야한다. 

            - MXProtocolType.Base.TM_REGISTER
            - MXProtocolType.Base.TM_UNREGISTER
            - MXProtocolType.Base.TM_ALIVE
            - MXProtocolType.Base.TM_VALUE_PUBLISH
            - MXProtocolType.Base.TM_RESULT_EXECUTE

            Args: 
                staff_msg (str): 파싱할 staff thing의 패킷

            Returns:
                protocol(MXProtocolType): staff thing 패킷의 MySSIX 프로토콜
                device_id(str): staff thing의 device id
                payload(str): staff thing 패킷의 payload
        '''
        pass

    @abstractmethod
    def _create_staff(self, staff_thing_info: dict) -> MXStaffThing:
        '''
            _scan_staff_thing() 함수를 통해 수집된 staff thing 정보를 바탕으로 staff thing을 생성하는 함수.
            만약 스캔하는 것만으로 완벽한 staff thing의 정보를 수집할 수 없다면, staff thing의 register 메시지를 받아 처리하는
            _handle_REGISTER_staff_message() 함수에서 staff thing을 self._staff_thing_list에서 찾아 정보를 추가할 수 있다.

            Args: 
                staff_thing_info (dict): staff thing의 정보를 담고 있는 딕셔너리

            Returns:
                staff_thing(MXStaffThing): 생성한 staff thing 인스턴스
        '''
        pass

    @abstractmethod
    def _connect_staff_thing(self, staff_thing: MXStaffThing) -> bool:
        '''
            staff thing과 연결하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _disconnect_staff_thing(self, staff_thing: MXStaffThing) -> bool:
        '''
            staff thing과 연결해제하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _handle_REGISTER_staff_message(self, staff_thing: MXStaffThing, payload: dict) -> Tuple[str, dict]:
        '''
            staff thing으로부터 받은 register 메시지를 처리하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스
                payload (dict): staff thing으로부터 받은 register 메시지의 payload. (MXThing.dump()의 결과)

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _handle_UNREGISTER_staff_message(self, staff_thing: MXStaffThing) -> str:
        '''
            staff thing으로부터 받은 unregister 메시지를 처리하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _handle_ALIVE_staff_message(self, staff_thing: MXStaffThing) -> str:
        '''
            staff thing으로부터 받은 alive 메시지를 처리하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _handle_VALUE_PUBLISH_staff_message(self, staff_thing: MXStaffThing, payload: dict) -> Tuple[str, str, dict]:
        '''
            staff thing으로부터 받은 value publish 메시지를 처리하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스
                payload (dict): staff thing으로부터 받은 value publish 메시지의 payload. (MXValue.dump()의 결과)

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _handle_RESULT_EXECUTE_staff_message(self, staff_thing: MXStaffThing, payload: dict) -> str:
        '''
            staff thing으로부터 받은 result execute 메시지를 처리하는 함수.
            해당 기능은 아직 구현되지 않았음.
        '''
        pass

    @abstractmethod
    def _send_RESULT_REGISTER_staff_message(self, staff_thing: MXStaffThing, payload: str) -> str:
        '''
            staff thing에게 result register 메시지를 전송하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스
                payload (str): staff thing 에게 보낼 register result 메시지의 payload. (커스텀형식의 payload)

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _send_RESULT_UNREGISTER_staff_message(self, staff_thing: MXStaffThing, payload: str) -> str:
        '''
            staff thing에게 result unregister 메시지를 전송하는 함수.

            Args: 
                staff_thing (MXStaffThing): 타겟 staff thing 인스턴스
                payload (str): staff thing 에게 보낼 unregister result 메시지의 payload. (커스텀형식의 payload)

            Returns:
                (None)
        '''
        pass

    @abstractmethod
    def _send_EXECUTE_staff_message(self, staff_thing: MXStaffThing, payload: str) -> str:
        '''
            staff thing에게 execute 메시지를 전송하는 함수.
            해당 기능은 아직 구현되지 않았음.
        '''
        pass

    ############################################################################################################################

    def _handle_staff_message(self, staff_msg):
        staff_protocol, staff_device_id, staff_payload = self._parse_staff_message(
            staff_msg)
        target_staff_thing = self._get_staff_thing_by_device_id(
            staff_device_id)

        if staff_protocol == MXProtocolType.Base.TM_REGISTER:
            thing_name, payload = self._handle_REGISTER_staff_message(
                target_staff_thing, staff_payload)
            self._subscribe_init_topic_list(target_staff_thing)
            self._send_TM_REGISTER()
            target_staff_thing.set_registered(True)

            if staff_device_id in [staff_thing._device_id for staff_thing in self._staff_thing_list]:
                target_staff_thing._device_id = staff_device_id
            else:
                target_staff_thing._device_id = self._generate_device_id()
        elif staff_protocol == MXProtocolType.Base.TM_UNREGISTER:
            thing_name = self._handle_UNREGISTER_staff_message(
                target_staff_thing)
            self._send_TM_UNREGISTER()
            target_staff_thing.set_registered(False)
        elif staff_protocol == MXProtocolType.Base.TM_ALIVE:
            thing_name = self._handle_ALIVE_staff_message(target_staff_thing)
            self._send_TM_ALIVE()
        elif staff_protocol == MXProtocolType.Base.TM_VALUE_PUBLISH:
            # FIXME: MXValue 를 리턴하도록 수정
            value = self._handle_VALUE_PUBLISH_staff_message(
                target_staff_thing, staff_payload)
            self._send_TM_VALUE_PUBLISH(value=value)
        elif staff_protocol == MXProtocolType.Base.TM_RESULT_EXECUTE:
            # TODO: complete this
            pass
            # TM/RESULT/EXECUTE/[FunctionName]/[ThingName]/([MiddlewareName]/[Request_ID])
            # Request_ID = requester_middleware@super_thing@super_service@subrequest_order
            # function_name, thing_name, middleware_name, request_ID, return_value = self._handle_RESULT_EXECUTE_staff_message(
            #     target_staff_thing, staff_payload)
            # target_staff_thing_function = target_staff_thing._get_function(function_name)
            # self._send_TM_RESULT_EXECUTE(function_name, thing_name, target_staff_thing_function.get_return_type(), return_value,
            #                              middleware_name)

    ############################################################################################################################

    def _generate_device_id(self) -> str:
        return str(uuid.uuid4())

    def _get_staff_thing_by_name(self, staff_name: str) -> MXStaffThing:
        for staff_thing in self._staff_thing_list:
            if staff_thing.get_name() == staff_name:
                return staff_thing
        return False

    def _get_staff_thing_by_device_id(self, device_id: str) -> MXStaffThing:
        for staff_thing in self._staff_thing_list:
            if staff_thing._device_id == device_id:
                return staff_thing
        return False

    def _append_staff_thing_value(self, new_staff_thing: MXStaffThing):
        self._staff_thing_list.append(new_staff_thing)
        for value in new_staff_thing.get_value_list():
            if not value in self._value_list:
                staff_value_name = f'{new_staff_thing.get_name()}/{value.get_name()}'
                value.set_name(staff_value_name)
                self._value_list.append(value)

    def _check_staff_thing_duplicate(self, new_staff_thing: MXStaffThing) -> Tuple[MXNewStaffThingLevel, MXStaffThing]:
        for staff_thing in self._staff_thing_list:
            if new_staff_thing == staff_thing:
                return MXNewStaffThingLevel.DUPLICATE, staff_thing
        else:
            return MXNewStaffThingLevel.NEW, new_staff_thing
