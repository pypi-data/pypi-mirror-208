from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import int
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
import os
import platform
from enum import IntEnum
from ctypes import c_int
from ctypes import c_uint
from ctypes import c_char_p
from ctypes import byref
from ctypes import c_double
from ctypes import create_string_buffer
from ctypes import windll

class route_cache_entry_condition(IntEnum):
    REQUIRE_SWITCHED_TO_INITIAL_STATE = 0
    PERFORM_SWITCH_TO_INITIAL_STATE = 1
    KEEP_EXISTING_SWITCHING_STATE = 2

class connection_status_include_options(IntEnum):
    NONE = 0
    WIRES = 1
    IMPLICIT_ROUTES = 2
    NESTED_GROUP_DETAILS = 4
    ROUTE_PIN_INFO = 8

class error_codes(IntEnum):
    SUCCESS = 0
    UNSPECIFIED = -1
    ARG_WRONG = -2
    SERVER__INSTALLATION_CORRUPT = -16
    SERVER__INSTALLATION_DIR_NOT_FOUND = -17
    SERVER__INSTALLATION_DEPENDENCIES_NOT_FOUND = -18
    SERVER__NOT_RUNNING = -256
    SERVER__ALREADY_INITIALIZED = -257
    SERVER__START_ARG_ALREADY_EXISTS = -258
    SERVER__START_ARG_NOT_FOUND = -259
    SERVER__NOT_REACHABLE = -260
    SERVER__START_PROFILE_UNKNOWN = -261
    SERVER__START_ARG_EMPTY = -262
    SERVER__START_ARG_INVALID = -263
    CLIENT__NOT_CONNECTED = -512
    MEM__BUFFER_TO_SMALL = -65280
    MEM__NOT_ALLOCATED = -65281
    PROJECT__ALREADY_OPEN = -4096
    PROJECT__NOT_OPEN = -4097
    PROJECT__COULD_NOT_OPEN = -4098
    PROJECT__COULD_NOT_CLOSE = -4099
    SYSTEM__NO_SETUP_ACTIVATED = -12288
    SYSTEM_SETUP__ITEM_NOT_FOUND = -12289
    SYSTEM__BOOT_ONLINE_FAILED = -8192
    SYSTEM__BOOT_OFFLINE_FAILED = -8193
    SYSTEM__NOT_BOOTED = -8194
    SWITCH__UNKNOWN_ENDPOINTS = -8448
    SWITCH__COULD_NOT_ROUTE_PATH = -8449
    SWITCH__ROUTE_NOT_FOUND = -8450
    SWITCH__ENDPOINTS_NOT_CONNECTED = -8451
    SWITCH__COULD_NOT_DISCONNECT = -8452
    SWITCH__COULD_NOT_CREATE_ROUTE = -8453
    SWITCH__DISCONNECT_ENDPOINT_PATH_FAILED = -8454
    SWITCH__START_ENDPOINT_MUST_BE_DISTINCT = -8455
    SWITCH__COULD_NOT_SET_SHORT_CIRCUIT_DETECTION = -8456
    SWITCH__COULD_NOT_BEGIN_ROUTE_CACHING = -8705
    SWITCH__UNKNOWN_PIN_NAME = -8458
    SWITCH__COULD_NOT_CREATE_SEQUENCE = -8459


class connection_status_display_options(IntEnum):
    NONE = 0
    ENDPOINT_NAMES = 1
    USER_LABELS = 2
    FRONT_LABELS = 4

class res_resistanceValues(IntEnum):
    SHORT = 0
    OPEN = 2147483647

class pi_spm(object):
    def __init__(self):
        libpath = "C:\\Program Files (x86)\\Pickering Interfaces Ltd\\Switch Path Manager\\" \
                  "SPM\\SDK\\Client\\Native\\Pickering.SPM.Client.Native.dll"
        if not os.path.exists(libpath) or '64 bit' in platform.architecture():
            libpath = "C:\\Program Files\\Pickering Interfaces Ltd\\Switch Path Manager\\" \
                      "SPM\\SDK\\Client\\Native\\Pickering.SPM.Client.Native.dll"
        self.__handleSPM = windll.LoadLibrary(libpath)
        self.route_cache_entry_condition = route_cache_entry_condition
        self.cs_include_options = connection_status_include_options
        self.error_codes = error_codes
        self.cs_display_options = connection_status_display_options
        self.res_values = res_resistanceValues

    # #
    # # Common functions
    # #

    def getVersion(self, componentType, componentName):
        bufferSize = c_uint(50)
        versionBuf = create_string_buffer(bufferSize.value)

        err = self.__handleSPM.SPM_GetVersion(  componentType.encode("ascii"),
                                                componentName.encode("ascii"),
                                                byref(versionBuf),
                                                bufferSize)

        return err, str(versionBuf.value, "ascii")

    # #
    # # Server Functions
    # #
    def server_addStartArg(self, arg):
        err = self.__handleSPM.SPM_Server_AddStartArg(arg.encode("ascii"))
        return err

    def server_removeStartArg(self, arg):
        err = self.__handleSPM.SPM_Server_RemoveStartArg(arg.encode("ascii"))
        return err

    def server_clearStartArgs(self):
        err = self.__handleSPM.SPM_Server_ClearStartArgs()
        return err

    def server_start(self):
        err = self.__handleSPM.SPM_Server_Start()
        return err

    def server_startFromProfile(self, profile):
        err = self.__handleSPM.SPM_Server_StartFromProfile(profile)
        return err

    def server_stop(self):
        err = self.__handleSPM.SPM_Server_Stop()
        return err

    def server_isRunning(self):
        isRunning = c_int(0)
        err = self.__handleSPM.SPM_Server_IsRunning(byref(isRunning))
        return err, bool(isRunning)

    # #
    # # Client Functions
    # #
    def client_connect(self):
        err = self.__handleSPM.SPM_Client_Connect()
        return err

    def client_disconnect(self):
        err = self.__handleSPM.SPM_Client_Disconnect()
        return err

    def client_isConnected(self):
        isConnected = c_uint(0)
        err = self.__handleSPM.SPM_Client_IsConnected(byref(isConnected))
        return err, bool(isConnected)

    # #
    # # Project Functions
    # #
    def project_open(self, project_file_path):
        project_file_path = os.path.abspath(os.path.realpath(project_file_path))
        if not os.path.exists(project_file_path):
            return -4098
        err = self.__handleSPM.SPM_Project_Open(project_file_path.encode("ascii"))
        return err

    def project_close(self):
        err = self.__handleSPM.SPM_Project_Close()
        return err

    def project_isOpen(self):
        isOpen = c_uint(0)
        err = self.__handleSPM.SPM_Project_IsOpen(byref(isOpen))
        return err, bool(isOpen)

    def project_getOpenFilePath(self):
        err, buf_size = self.project_getOpenFileBufferSize()
        if not err:
            project_file_path = create_string_buffer(buf_size)
            err = self.__handleSPM.SPM_Project_GetOpenFilePath(project_file_path, buf_size)
        return err, str(project_file_path.value, "ascii")

    def project_getOpenFileBufferSize(self):
        buffer_size = c_uint(0)
        err = self.__handleSPM.SPM_Project_GetOpenFilePathBufferSize(byref(buffer_size))
        return err, int(buffer_size.value)

    # #
    # # System Functions
    # #
    def system_bootOnline(self):
        err = self.__handleSPM.SPM_System_BootOnline()
        return err

    def system_bootOffline(self):
        err = self.__handleSPM.SPM_System_BootOffline()
        return err

    def system_isBooted(self):
        isBooted = c_uint(0)
        err = self.__handleSPM.SPM_System_IsBooted(byref(isBooted))
        return err, bool(isBooted)

    def system_isBootedOnline(self):
        isBootedOnline = c_uint(0)
        err = self.__handleSPM.SPM_System_IsBootedOnline(byref(isBootedOnline))
        return err, bool(isBootedOnline)

    def system_isBootedOffline(self):
        isBootedOffline = c_uint(0)
        err = self.__handleSPM.SPM_System_IsBootedOffline(byref(isBootedOffline))
        return err, bool(isBootedOffline)

    def system_shutdown(self):
        err = self.__handleSPM.SPM_System_Shutdown()
        return err

    def system_resetFull(self):
        err = self.__handleSPM.SPM_System_ResetFull()
        return err

    # #
    # # Switch Setup Project
    # #
    def switch_setup_getRouteNamesBufferSize(self):
        buffer_size = c_uint(0)
        err = self.__handleSPM.SPM_Switch_Setup_GetRouteNamesBufferSize(byref(buffer_size))
        return err, int(buffer_size.value)

    def switch_setup_getRouteNames(self, buffer_size = None):
        if type(buffer_size) is not int or buffer_size is None:
            err, buffer_size = self.switch_setup_getRouteNamesBufferSize()
            if err != 0:
                buffer_size = 100

        route_names = (c_char_p * buffer_size)()
        route_count = c_int(0)
        err = self.__handleSPM.SPM_Switch_Setup_GetRouteNames(route_names, byref(route_count))

        route_names = route_names[0:route_count.value]
        rt_names = [str(route, "ascii") for route in route_names]

        return err, rt_names

    def switch_setup_checkRouteExists(self, route):
        is_exists = c_int(0)
        err = self.__handleSPM.SPM_Switch_Setup_CheckRouteExists(route.encode('ascii'), byref(is_exists))
        return err, is_exists.value

    def switch_checkRouteAvailable(self, routeName):
        available = c_uint(0)

        err = self.__handleSPM.SPM_Switch_CheckRouteAvailable(routeName.encode("ascii"), byref(available))

        return err, bool(available.value)

    def switch_setup_configureRouteGroupFromConnectedEndpoints(self, route_group):
        err = self.__handleSPM.SPM_Switch_Setup_ConfigureRouteGroupFromConnectedEndpoints(route_group.encode('ascii'))
        return err

    def switch_setup_applySwitchingConfig(self):
        err = self.__handleSPM.SPM_Switch_Setup_ApplySwitchingConfig()
        return err

    def switch_setup_deleteRoute(self, route_name):
        err = self.__handleSPM.SPM_Switch_Setup_DeleteRoute(route_name.encode("ascii"))
        return err

    def switch_setup_getEndpointNamesBufferSize(self):
        buffer_size = c_int(0)
        err = self.__handleSPM.SPM_Switch_Setup_GetEndpointNamesBufferSize(byref(buffer_size))
        return err, int(buffer_size.value)

    def switch_setup_getEndpointNames(self, buffer_size = None):
        if type(buffer_size) is not int or buffer_size is None:
            err, buffer_size = self.switch_setup_getEndpointNamesBufferSize()
            if err != 0:
                buffer_size = 100

        endpoint_names = (c_char_p * buffer_size)()
        endpoint_count = c_int(0)
        err = self.__handleSPM.SPM_Switch_Setup_GetEndpointNames(endpoint_names, byref(endpoint_count))

        endpoint_names = endpoint_names[0:endpoint_count.value]
        ep_names = [str(name, "ascii") for name in endpoint_names]

        return err, ep_names

    def switch_setup_getRelayGroupNamesBufferSize(self):
        buffer_size = c_uint(0)
        err = self.__handleSPM.SPM_Switch_Setup_GetRelayGroupNamesBufferSize(byref(buffer_size))
        return err, int(buffer_size.value)

    def switch_setup_getRelayGroupNames(self, buffer_size = None):
        if type(buffer_size) is not int or buffer_size is None:
            err, buffer_size = self.switch_setup_getRelayGroupNamesBufferSize()
            if err != 0:
                buffer_size = 100

        relaygrp_names = (c_char_p * buffer_size)()
        relaygrp_count = c_uint(0)
        err = self.__handleSPM.SPM_Switch_Setup_GetRelayGroupNames(relaygrp_names, byref(relaygrp_count))

        relaygrp_names = relaygrp_names[0:relaygrp_count.value]
        rg_names = [str(name, "ascii") for name in relaygrp_names]

        return err, rg_names

    def switch_setShortCircuitDetection(self, is_enable):
        err = self.__handleSPM.SPM_Switch_SetShortCircuitDetection(c_int(is_enable))
        return err

    def switch_getShortCircuitDetection(self):
        is_enabled = c_int(0)
        err = self.__handleSPM.SPM_Switch_GetShortCircuitDetection(byref(is_enabled))
        return err, is_enabled.value

    def switch_getRouteStatusInfoAll(self, include_options, display_options):
        include_opt = c_uint(include_options)
        display_opt = c_uint(display_options)
        buf_size = c_int(1024)
        route_status_buf = create_string_buffer(buf_size.value)

        err = self.__handleSPM.SPM_Switch_GetRouteStatusInfoAll(include_opt,display_opt, route_status_buf, buf_size)
        return err, str(route_status_buf.value, "ascii")

    def switch_getRelayGroupStatusInfoAll(self, display_options):
        display_opt = c_uint(display_options)
        buf_size = c_int(1024)
        status_buf = create_string_buffer(buf_size.value)

        err = self.__handleSPM.SPM_Switch_GetRelayGroupStatusInfoAll(display_opt, status_buf, buf_size)
        return err, str(status_buf.value, "ascii")

    def switch_setup_getLogicalPinFromEndpointName(self, endpointName):
        logicalPinNameBufSize = c_uint(50)
        logicalPinNameBuf = create_string_buffer(logicalPinNameBufSize.value)

        err = self.__handleSPM.SPM_Switch_Setup_GetLogicalPinFromEndpointName(  endpointName.encode("ascii"),
                                                                                byref(logicalPinNameBuf),
                                                                                logicalPinNameBufSize)
        return err, str(logicalPinNameBuf.value, "ascii")

    def switch_setup_getEndpointNameOfLogicalPin(self, logicalPinName):
        endpointNameBufSize = c_uint(50)
        endpointNameBuf = create_string_buffer(endpointNameBufSize.value)

        err = self.__handleSPM.SPM_Switch_Setup_GetEndpointNameOfLogicalPin(    logicalPinName.encode("ascii"),
                                                                                byref(endpointNameBuf),
                                                                                endpointNameBufSize)

        return err, str(endpointNameBuf.value, "ascii")

    # #
    # # Caching Functions
    # #
    def switch_startRoutingCache(self, start_conditions):
        start_con = c_uint(start_conditions)
        err = self.__handleSPM.SPM_Switch_StartRoutingCache(start_con)
        return err

    def switch_stopAndKeepRoutingCache(self):
        return self.__handleSPM.SPM_Switch_StopAndKeepRoutingCache()

    def switch_stopAndClearRoutingCache(self):
        return self.__handleSPM.SPM_Switch_StopAndClearRoutingCache()

    def switch_getRoutingCacheActive(self):
        is_active = c_int(0)
        err = self.__handleSPM.SPM_Switch_GetRoutingCacheActive(byref(is_active))
        return err, bool(is_active.value)

    def switch_getRoutingCacheStarted(self):
        is_started = c_int(0)
        err = self.__handleSPM.SPM_Switch_GetRoutingCacheStarted(byref(is_started))
        return err, bool(is_started.value)

    # #
    # # Switch Functions
    # #
    def switch_toInitialState(self):
        return self.__handleSPM.SPM_Switch_SwitchToInitialState()

    def switch_getEndpointsConnectedStatus(self, from_endpoint, to_endpoint):        
        err = 0
        is_connected = c_int(0)
        err = self.__handleSPM.SPM_Switch_GetEndpointsConnectedStatus(from_endpoint.encode("ascii"), to_endpoint.encode("ascii"), byref(is_connected))
        return err, is_connected.value

    def switch_connectEndpoints(self, from_endpoint, to_endpoint):
        err = self.__handleSPM.SPM_Switch_ConnectEndpoints(from_endpoint.encode("ascii"), to_endpoint.encode("ascii"))

        return err

    def switch_disconnectEndpoints(self, from_endpoint, to_endpoint):
        err = self.__handleSPM.SPM_Switch_DisconnectEndpoints(from_endpoint.encode("ascii"),
                                                              to_endpoint.encode("ascii"))

        return err

    def switch_disconnectEndpointsForced(self, from_endpoint, to_endpoint):
        err = self.__handleSPM.SPM_Switch_DisconnectEndpointsForced(from_endpoint.encode("ascii"),
                                                                    to_endpoint.encode("ascii"))

        return err

    def switch_disconnectEndpointsForcedCsv(self, from_endpoint, to_endpoints_csv):
        err = self.__handleSPM.SPM_Switch_DisconnectEndpointsForcedCsv( from_endpoint.encode("ascii"),
                                                                        to_endpoints_csv.encode("ascii"))

        return err

    def switch_disconnectEndpointsForcedArr(self, from_endpoint, to_ep_array):
        ep_count = len(to_ep_array)
        to_ep_arr = (c_char_p * ep_count)()

        for idx in range(ep_count):
            to_ep_arr[idx] = to_ep_array[idx].encode("ascii")

        err = self.__handleSPM.SPM_Switch_DisconnectEndpointsForcedArr(from_endpoint.encode("ascii"),
                                                                       to_ep_arr,
                                                                       ep_count)

        return err

    def switch_connectEndpointsCsv(self, from_endpoint, to_endpoint):
        err = self.__handleSPM.SPM_Switch_ConnectEndpointsCsv(from_endpoint.encode("ascii"), to_endpoint.encode("ascii"))
        return err

    def switch_disconnectEndpointsCsv(self, from_endpoint, to_endpoint):
        err = self.__handleSPM.SPM_Switch_DisconnectEndpointsCsv(from_endpoint.encode("ascii"), to_endpoint.encode("ascii"))
        return err

    def switch_connectEndpointsArr(self, from_endpoint, to_ep_array):
        ep_count = len(to_ep_array)
        to_ep_arr = (c_char_p * ep_count)()
        for idx in range(ep_count):
            to_ep_arr[idx] = to_ep_array[idx].encode("ascii")
        err = self.__handleSPM.SPM_Switch_ConnectEndpointsArr(from_endpoint.encode("ascii"), to_ep_arr, ep_count)
        return err

    def switch_disconnectEndpointsArr(self, from_endpoint, to_ep_array):
        ep_count = len(to_ep_array)
        to_ep_arr = (c_char_p * ep_count)()
        for idx in range(ep_count):
            to_ep_arr[idx] = to_ep_array[idx].encode("ascii")
        err = self.__handleSPM.SPM_Switch_DisconnectEndpointsArr(from_endpoint.encode("ascii"), to_ep_arr, ep_count)
        return err

    def switch_connectRoute(self, route_name):
        err = self.__handleSPM.SPM_Switch_ConnectRoute(route_name.encode("ascii"))
        return err

    def switch_disconnectRoute(self, route_name):
        err = self.__handleSPM.SPM_Switch_DisconnectRoute(route_name.encode("ascii"))
        return err

    def switch_disconnectRouteForced(self, route_name):
        err = self.__handleSPM.SPM_Switch_DisconnectRouteForced(route_name.encode("ascii"))

        return err

    def switch_getRouteConnectedStatus(self, route_name):
        is_connected = c_int(0)
        err = self.__handleSPM.SPM_Switch_GetRouteConnectedStatus(route_name.encode("ascii"), byref(is_connected))
        return err, is_connected.value

    def switch_connectRoutes(self, routes):
        rt_count = len(routes)
        rt_names = (c_char_p * rt_count)()
        for idx in range(rt_count):
            rt_names[idx] = routes[idx].encode("ascii")
        err = self.__handleSPM.SPM_Switch_ConnectRoutes(rt_names, rt_count)
        return err

    def switch_disconnectRoutes(self, routes):
        rt_count = len(routes)
        rt_names = (c_char_p * rt_count)()
        for idx in range(rt_count):
            rt_names[idx] = routes[idx].encode("ascii")
        err = self.__handleSPM.SPM_Switch_DisconnectRoutes(rt_names, rt_count)
        return err

    def switch_disconnectRoutesForced(self, routes):
        rt_count = len(routes)
        rt_names = (c_char_p * rt_count)()

        for idx in range(rt_count):
            rt_names[idx] = routes[idx].encode("ascii")

        err = self.__handleSPM.SPM_Switch_DisconnectRoutesForced(rt_names, rt_count)

        return err

    def switch_connectRelayGroup(self, relay_grp):
        err = self.__handleSPM.SPM_Switch_ConnectRelayGroup(relay_grp.encode("ascii"))
        return err

    def switch_disconnectRelayGroup(self, relay_grp):
        err = self.__handleSPM.SPM_Switch_DisconnectRelayGroup(relay_grp.encode("ascii"))
        return err

    def switch_disconnectAllRoutes(self):
        err = self.__handleSPM.SPM_Switch_DisconnectAllRoutes()
        return err

    def switch_disconnectAll(self):
        err = self.__handleSPM.SPM_Switch_DisconnectAll()
        return err

    # New since November 2020
    def switch_checkHasInitialSwitchingState(self):
        initialState = c_uint(0)

        err = self.__handleSPM.SPM_Switch_CheckHasInitialSwitchingState(byref(initialState))

        return err, int(initialState.value)

    # New since April 2023
    # #
    # # Protection functions
    # #

    def spm_protectionResetEnable(self, chassis, timeoutInSeconds):
        err = self.__handleSPM.SPM_ProtectionResetEnable(c_int(chassis), c_int(timeoutInSeconds))
        return err

    def spm_protectionResetDisable(self, chassisNumber):
        err = self.__handleSPM.SPM_ProtectionResetDisable(c_int(chassisNumber))
        return err
    
    def spm_getProtectionResetEnabled(self, chassis):
        state = c_int(0)
        err = self.__handleSPM.SPM_GetProtectionResetEnabled(chassis, byref(state))
        return err, state.value
    
    def spm_getProtectionResetTimeout(self, chassis):
        timeout = c_int(0)
        err = self.__handleSPM.SPM_GetProtectionResetTimeout(self, chassis, byref(timeout))
        return err, timeout.value

    # #
    # # Sequencing Functions
    # #
    def sequence_start(self, disable_notification, project_file,
                       reset, boot_online, show_endmsg, open_close_IDE, reload_prj):
        disable_notif = c_int(disable_notification)
        prj_file = project_file.encode('ascii')
        rst = c_int(reset)
        bt_ol = c_int(boot_online)
        shw_msg = c_int(show_endmsg)
        oc_IDE = c_int(open_close_IDE)
        rld_prj = c_int(reload_prj)
        err = self.__handleSPM.SPM_StartSequence(disable_notif, prj_file, rst, bt_ol, shw_msg, oc_IDE, rld_prj)
        return err

    def sequence_stop(self, reset, stop_server):
        rst = c_int(reset)
        stop_srvr = c_int(stop_server)
        err = self.__handleSPM.SPM_StopSequence(rst, stop_srvr)
        return err

    def switch_setup_getSequenceNames(self):
        sequenceNamesBufferSize = c_uint(0)
        numOfSequences = c_uint(0)
        err = self.__handleSPM.SPM_Switch_Setup_GetSequenceNamesBufferSize(byref(sequenceNamesBufferSize))


        sequenceNames = (c_char_p * sequenceNamesBufferSize.value)()
        err = self.__handleSPM.SPM_Switch_Setup_GetSequenceNames(   sequenceNames,
                                                                    byref(numOfSequences))
        sequenceNames = sequenceNames[0:numOfSequences.value]

        return err, [str(name, "ascii") for name in sequenceNames]

    def switch_setup_checkSequenceExists(self, sequenceName):
        exists = c_uint(0)

        err = self.__handleSPM.SPM_Switch_Setup_CheckSequenceExists(sequenceName.encode("ascii"), byref(exists))

        return err, bool(exists.value)

    def switch_setup_deleteSequence(self, sequenceName):

        err = self.__handleSPM.SPM_Switch_Setup_DeleteSequence(sequenceName.encode())

        return err

    def switch_checkSequenceAvailable(self, sequenceName):
        available = c_uint(0)

        err = self.__handleSPM.SPM_Switch_CheckSequenceAvailable(sequenceName.encode("ascii"), byref(available))

        return err, bool(available)

    def switch_connectSequence(self, sequenceName):

        err = self.__handleSPM.SPM_Switch_ConnectSequence(sequenceName.encode("ascii"))

        return err

    def switch_disconnectSequence(self, sequenceName):

        err = self.__handleSPM.SPM_Switch_DisconnectSequence(sequenceName.encode("ascii"))

        return err






    # #
    # # Resistor Functions
    # #
    def res_getResistance(self, resource_id):
        err = 0
        resistance = c_double(0.0)
        err = self.__handleSPM.SPM_RES_GetResistance(resource_id.encode('ascii'), byref(resistance))
        return err, resistance.value

    def res_setResistance(self, resource_id, resistance):
        err = 0
        res = c_double(resistance)
        err = self.__handleSPM.SPM_RES_SetResistance(resource_id.encode('ascii'), res)
        return err

    # #
    # # App Functions
    # #
    def app_showMainWindow(self):
        err = self.__handleSPM.SPM_App_ShowMainWindow()
        return err

    def app_closeMainWindow(self):
        err = self.__handleSPM.SPM_App_CloseMainWindow()
        return err

    def app_setMainWindowMinimized(self):
        err = self.__handleSPM.SPM_App_SetMainWindowMinimized()
        return err

    def app_setMainWindowMaximized(self):
        err = self.__handleSPM.SPM_App_SetMainWindowMaximized()
        return err

    def app_setMainWindowNormal(self):
        err = self.__handleSPM.SPM_App_SetMainWindowNormal()
        return err

    # #
    # # Error Functions
    # #
    def error_getErrorMessage(self, error_code):
        get_err_msg = self.__handleSPM.SPM_GetErrorMessage
        get_err_msg.restype = c_char_p
        msg = self.__handleSPM.SPM_GetErrorMessage(error_code)
        return str(msg, "ascii")

    def error_getLastErrorCode(self):
        err_code = self.__handleSPM.SPM_GetLastErrorCode()
        return int(err_code)

    def error_getErrorCodeName(self, error_code):
        get_err_code_name = self.__handleSPM.SPM_GetErrorCodeName
        get_err_code_name.restype = c_char_p
        msg = get_err_code_name(error_code)
        return str(msg, "ascii")

    def error_getLastErrorDetails(self):
        get_err_details = self.__handleSPM.SPM_GetLastErrorDetails
        get_err_details.restype = c_char_p
        msg = get_err_details()
        return str(msg, "ascii")