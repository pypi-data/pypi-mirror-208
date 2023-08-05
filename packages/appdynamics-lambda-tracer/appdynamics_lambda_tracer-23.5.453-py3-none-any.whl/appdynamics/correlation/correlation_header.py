import logging

import appdynamics.util.constants as constants
from appdynamics.util.tracer_errors import CorrelationHeaderError


class CorrelationHeader:
    def __init__(self, agent_config_resp, **kwargs):
        self.logger = logging.getLogger(constants.APPDYNAMICS_LOGGER_NAME)
        self.app_id = agent_config_resp.application_id
        self.account_guid = agent_config_resp.account_guid
        self.controller_guid = agent_config_resp.controller_guid
        self.tier_id = agent_config_resp.tier_id
        self.cross_app_correlation = False
        self.txn_detect = True
        self.header_string_valid = True
        self.sub_headers = {}
        self.header_string = kwargs.get("header_string")
        if self.header_string:
            try:
                self.sub_headers = self.parse_header_string(self.header_string)
                self.txn_detect = not self.is_txn_detection_disabled()
                self.header_string_validity = self.validate_incoming_header()
                self.cross_app_correlation = self.is_cross_app()
            except CorrelationHeaderError as e:
                raise e

    def sanitize_header(self, header_string):
        # sanitize header based on CORE-20346
        delimiter = ", "
        header_components = header_string.split(delimiter)
        return header_components[len(header_components) - 1]

    def parse_header_string(self, header_string):
        header_string = self.sanitize_header(header_string)
        header_str_components = header_string.split("*")
        header_components_key_val = dict((key_val.split("=")[0], key_val.split("=")[
                                         1]) for key_val in header_str_components)
        # update the values in the components with "," to array with all those values
        header_comp_with_list_values = [constants.COMPONENT_ID_FROM, constants.COMPONENT_ID_TO,
                                        constants.EXIT_CALL_TYPE_ORDER, constants.EXIT_CALL_SUBTYPE_KEY, constants.THREAD_CALL_CHAIN_FOR_OUT_OF_PROCESS]
        header_comp_with_list_int_values = [constants.COMPONENT_ID_FROM]

        for key in header_comp_with_list_values:
            if header_components_key_val.get(key):
                value = header_components_key_val.get(
                    key)
                if value:
                    value = value.split(",")
                    # update the values in the components with integer string value to integer
                    if key in header_comp_with_list_int_values:
                        value = list(map(int, value))
                    header_components_key_val[key] = value

        # update the values in the components with boolean string value to boolean value
        header_comp_with_boolean_values = [constants.DONOTRESOLVE, constants.SNAPSHOT_ENABLE, constants.DISABLE_TRANSACTION_DETECTION,
                                           constants.FORCE_HOTSPOT_COLLECT, constants.HOTSPOT_COLLECTING_CPU_TIME, constants.DEV_MODE_ENABLED, constants.ASYNC_CALL, constants.DEBUG_ENABLED]
        for key in header_comp_with_boolean_values:
            if header_components_key_val.get(key) == "true":
                header_components_key_val[key] = True

        # update the values in the components with integer string value to integer
        header_comp_with_integer_values = [constants.APP_ID]

        for key in header_comp_with_integer_values:
            if header_components_key_val.get(key):
                try:
                    header_components_key_val[key] = int(
                        header_components_key_val[key])
                except ValueError:
                    self.logger.error(
                        f"{key} in correlation header should have valid integer value")
                    raise CorrelationHeaderError(
                        "Correlation header is invalid")
        return header_components_key_val

    def is_txn_detection_disabled(self):
        # Disable transaction detection if notxdetect sub header is set
        disable_txn_detection_header_value = self.sub_headers.get(
            constants.DISABLE_TRANSACTION_DETECTION)
        if disable_txn_detection_header_value is True:
            self.logger.info(
                "Transaction detection is disabled from the origination tier.")
            return True
        return False

    def is_cross_app(self):
        incoming_account_guid = self.sub_headers.get(constants.ACCOUNT_GUID)
        incoming_app_id = self.sub_headers.get(constants.APP_ID)
        if incoming_account_guid and incoming_app_id:
            self.logger.debug(
                f"Correlation header is coming with app id = {incoming_app_id} to app id = {self.app_id}")
            self.logger.debug(
                f"Correlation header is coming with account guid = {incoming_account_guid} to account guid = {self.account_guid}")
            return incoming_app_id != self.app_id or incoming_account_guid != self.account_guid
        return False

    def read_caller_chain(self):
        exit_call_position_vs_latest_thread_add_id = None
        tcops = self.sub_headers.get(
            constants.THREAD_CALL_CHAIN_FOR_OUT_OF_PROCESS)
        if tcops and len(tcops) > 0:
            exit_call_position_vs_latest_thread_add_id = {}
            for tcop in tcops:
                # Each threadChain is of the format $exit_call_position:$thread_add_id(s)
                # Note, the portion following the ':' may be one or more ADD IDs, in case an upstream agent sending the
                # header was older than the one receiving
                pos_and_ids = tcop.split(":")
                exit_call_position_string = pos_and_ids[0]
                thread_add_id_string = pos_and_ids[1]
                # parse based on the old encoding, which should cover both old agents and the new
                ids = thread_add_id_string.split("-")
                exit_call_position_vs_latest_thread_add_id[exit_call_position_string] = ids[len(
                    ids) - 1]

        cid_from_arr = self.sub_headers.get(constants.COMPONENT_ID_FROM, [])
        cid_to_arr = self.sub_headers.get(constants.COMPONENT_ID_TO, [])
        e_type_order_arr = self.sub_headers.get(
            constants.EXIT_CALL_TYPE_ORDER, [])
        e_sub_type_arrr = self.sub_headers.get(
            constants.EXIT_CALL_SUBTYPE_KEY, [])
        # parse components
        component_links = []
        for i in range(len(cid_from_arr)):
            component_link = {}
            component_link[constants.COMPONENT_ID_FROM] = cid_from_arr[i]
            component_link[constants.COMPONENT_ID_TO] = cid_to_arr[i]
            component_link[constants.EXIT_CALL_TYPE_ORDER] = e_type_order_arr[i]
            component_link[constants.EXIT_CALL_SUBTYPE_KEY] = e_sub_type_arrr[i]
            if exit_call_position_vs_latest_thread_add_id and exit_call_position_vs_latest_thread_add_id.get(str(i+1)):
                component_link["latestThreadAddId"] = exit_call_position_vs_latest_thread_add_id.get(
                    str(i+1))
            component_links.append(component_link)
        self.logger.debug(f"Caller Chain is {component_links}")
        return component_links

    def calculate_caller_chain_length(self, caller_chain):
        curr_length = 0
        for component in caller_chain:
            curr_length += 30 + len(self.get_string_value(component.get(constants.COMPONENT_ID_FROM))) + len(self.get_string_value(component.get(constants.COMPONENT_ID_TO))) + (len(self.get_string_value(component.get(constants.EXIT_CALL_TYPE_ORDER))) if component.get(constants.EXIT_CALL_TYPE_ORDER) is not None else 0) + (len(self.get_string_value(component.get(
                constants.EXIT_CALL_SUBTYPE_KEY))) if component.get(constants.EXIT_CALL_SUBTYPE_KEY) is not None else 0) + (len(self.get_string_value(component.get('latestThreadAddId'))) if component.get('latestThreadAddId') is not None else 0)
        return curr_length + constants.METRIC_NAME_LENGTH

    def validate_incoming_header(self):
        cid_from = self.sub_headers.get(constants.COMPONENT_ID_FROM, [])
        cid_to = self.sub_headers.get(constants.COMPONENT_ID_TO, [])
        exit_call_type_order = self.sub_headers.get(
            constants.EXIT_CALL_TYPE_ORDER, [])
        exit_call_sub_type_order = self.sub_headers.get(
            constants.EXIT_CALL_SUBTYPE_KEY, [])

        if len(cid_from) != len(cid_to) or len(cid_from) != len(exit_call_type_order):
            self.logger.error("Malformed caller chain")
            return False

        if (len(exit_call_sub_type_order) == 0 and len(exit_call_type_order) > 0):
            exit_call_sub_type_order = exit_call_type_order[:]
            self.sub_headers[constants.EXIT_CALL_SUBTYPE_KEY] = exit_call_sub_type_order

        if len(exit_call_sub_type_order) != len(exit_call_type_order):
            self.logger.error(
                f"Malformed incoming header. Exit type and sub exit types count don't match. Exit types are {exit_call_type_order}. Sub exit types are {exit_call_sub_type_order}")
            return False

        component_links = self.read_caller_chain()
        component_links_length = self.calculate_caller_chain_length(
            component_links)
        if component_links_length > constants.MAX_METRIC_LENGTH:
            return False
        return True

    def get_string_value(self, header_value):
        if isinstance(header_value, str):
            return header_value
        if isinstance(header_value, list) and header_value:
            if isinstance(header_value[0], str):
                return ",".join(header_value)
            return ",".join(list(map(str, header_value)))
        return str(header_value)

    def get_caller_chain(self):
        caller_chain_map = []
        caller_chain_header_names = [constants.APP_ID, constants.ACCOUNT_GUID,
                                     constants.COMPONENT_ID_FROM, constants.COMPONENT_ID_TO,
                                     constants.EXIT_CALL_TYPE_ORDER, constants.EXIT_CALL_SUBTYPE_KEY,
                                     constants.UNRESOLVED_EXIT_ID]
        caller_chain_boolean_val_header_names = [constants.DONOTRESOLVE]
        for header_name in caller_chain_header_names:
            if self.sub_headers.get(header_name):
                caller_chain_map.append(
                    header_name + "=" + self.get_string_value(self.sub_headers.get(header_name)))
        for header_name in caller_chain_boolean_val_header_names:
            if self.sub_headers.get(header_name) is not None:
                caller_chain_map.append(
                    header_name + "=" + self.get_string_value(self.sub_headers.get(header_name)))
        return "*".join(caller_chain_map)

    def update_txn_for_continuing_txn(self, txn):
        bt_id = self.sub_headers.get(constants.BT_ID)
        if bt_id:
            try:
                txn.bt_id = int(bt_id)
            except ValueError:
                error_msg = "Incoming btid is not valid integer"
                self.logger.error(error_msg)
                raise CorrelationHeaderError(error_msg)
        else:
            error_msg = "Invalid correlation header to create continuining transaction. Incoming header is missing btid"
            self.logger.error(error_msg)
            raise CorrelationHeaderError(error_msg)

        txn.request_guid = self.sub_headers.get(constants.REQUEST_GUID)
        txn.skew_adjusted_start_wall_time = self.sub_headers.get(
            constants.TIMESTAMP)
        txn.caller_chain = self.get_caller_chain()
        return

    def add_subheader(self, name, value):
        self.sub_headers[name] = value

    def generate_sub_headers(self, txn, exit_call):
        # if the upstream tier has sent a notxdetect=true, then we should
        # also pass it on to all downstream tiers
        if (txn.corr_header and txn.corr_header.txn_detect is False):
            self.add_subheader(constants.DISABLE_TRANSACTION_DETECTION, True)
            return

        if (txn.ignore):
            return

        incoming_header = None
        if txn.corr_header:
            if txn.corr_header.cross_app_correlation is False:
                incoming_header = txn.corr_header

        #  if backend call is not registered
        if not exit_call.backend_id:
            self.add_subheader(constants.DISABLE_TRANSACTION_DETECTION, True)
            if incoming_header and incoming_header.sub_headers.get(constants.DEBUG_ENABLED):
                self.add_subheader(constants.DEBUG_ENABLED, True)
            return

        # add app id subheader
        self.add_subheader(constants.ACCOUNT_GUID, self.account_guid)
        self.add_subheader(constants.APP_ID, self.app_id)
        self.add_subheader(constants.CONTROLLER_GUID, self.controller_guid)

        # add BT related subheaders
        if txn.bt_id:
            self.add_subheader(constants.BT_ID, txn.bt_id)

        # add request guid subheader
        self.add_subheader(constants.REQUEST_GUID, txn.request_guid)
        if txn.skew_adjusted_start_wall_time:
            self.add_subheader(constants.TIMESTAMP,
                               txn.skew_adjusted_start_wall_time)

        if incoming_header:
            incoming_header_boolean_controls = [constants.DEBUG_ENABLED, constants.SNAPSHOT_ENABLE,
                                                constants.DEV_MODE_ENABLED, constants.FORCE_HOTSPOT_COLLECT,
                                                constants.HOTSPOT_COLLECTING_CPU_TIME, constants.ASYNC_CALL]
            for boolean_control in incoming_header_boolean_controls:
                if incoming_header.sub_headers.get(boolean_control):
                    self.add_subheader(boolean_control, True)

        if exit_call.exit_component and exit_call.exit_component.backend_id:
            self.add_subheader(constants.UNRESOLVED_EXIT_ID,
                               str(exit_call.exit_component.backend_id))

        # add exit guid subheader
        if incoming_header and incoming_header.sub_headers.get(constants.EXIT_POINT_GUID):
            incoming_sequence_info = incoming_header.sub_headers.get(
                constants.EXIT_POINT_GUID)
            self.add_subheader(constants.EXIT_POINT_GUID,
                               incoming_sequence_info + "|" + self.get_string_value(exit_call.sequence_info))
        else:
            self.add_subheader(constants.EXIT_POINT_GUID,
                               self.get_string_value(exit_call.sequence_info))

        # add component link subheaders
        comp_from = []
        comp_to = []
        exit_order = []
        exit_sub_type = []
        exit_call_position_vs_latest_thread_add_id = None

        if incoming_header:
            comp_from = incoming_header.sub_headers.get(
                constants.COMPONENT_ID_FROM)
            comp_to = incoming_header.sub_headers.get(
                constants.COMPONENT_ID_TO)
            exit_order = incoming_header.sub_headers.get(
                constants.EXIT_CALL_TYPE_ORDER)
            exit_sub_type = incoming_header.sub_headers.get(
                constants.EXIT_CALL_SUBTYPE_KEY)
            exit_call_position_vs_latest_thread_add_id = incoming_header.sub_headers.get(
                constants.THREAD_CALL_CHAIN_FOR_OUT_OF_PROCESS)

        comp_from.append(self.tier_id)
        if exit_call.exit_component:
            comp_to.append(
                str(exit_call.exit_component))
        exit_order.append(exit_call.exit_point_type)
        exit_sub_type.append(exit_call.exit_point_sub_type)
        self.add_subheader(constants.COMPONENT_ID_FROM, comp_from)
        self.add_subheader(constants.COMPONENT_ID_TO, comp_to)
        self.add_subheader(constants.EXIT_CALL_TYPE_ORDER, exit_order)
        self.add_subheader(constants.EXIT_CALL_SUBTYPE_KEY, exit_sub_type)
        if exit_call_position_vs_latest_thread_add_id:
            self.add_subheader(constants.THREAD_CALL_CHAIN_FOR_OUT_OF_PROCESS,
                               exit_call_position_vs_latest_thread_add_id)
        return

    def __str__(self):
        key_val_pairs = []
        for sub_header_key, sub_header_val in self.sub_headers.items():
            if sub_header_val:
                if isinstance(sub_header_val, bool):
                    sub_header_val = str(sub_header_val).lower()
                else:
                    sub_header_val = self.get_string_value(sub_header_val)
                key_val_pairs.append(sub_header_key + "=" + sub_header_val)
        return "*".join(key_val_pairs)
