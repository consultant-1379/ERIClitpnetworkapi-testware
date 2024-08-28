"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     August 2014
@author:    Kieran Duggan, Matt Boyer, Mary Russell, Igor Milovanovic
@summary:   Integration
            Agile: STORY LITPCDS-2069
"""
from litp_generic_test import GenericTest, attr
import test_constants


class Story2069(GenericTest):
    """
    As a LITP User, I want link aggregation (bonding) so that
    I can achieve higher network bandwidth and/or redundancy
    """

    def setUp(self):
        """
        Description:
            Runs before every single test.
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and
            variables common to all tests are available
        """
        # 1. Call super class setup
        super(Story2069, self).setUp()
        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filename()
        self.mn_nodes = self.get_managed_node_filenames()
        self.bond_name = 'bond2069'
        self.ms_url = "/ms"
        self.bond_ms_url = "{0}/network_interfaces/b_2069".format(self.ms_url)
        self.if_url = "{0}/network_interfaces/if_2069".format(self.ms_url)
        self.bond_ipaddress = '10.10.10.1'

        free_nics = self.verify_backup_free_nics(
            self.ms_node, self.ms_url, backup_files=False)
        self.test_ms_if1 = free_nics[0]
        self.test_ms_if1_mac = self.test_ms_if1["MAC"]
        self.test_ms_if1_name = self.test_ms_if1["NAME"]

        self.test_passed = True

    def tearDown(self):
        """
        Description:
            Runs after each test.
        Actions:
            1. Cleanup after test if global results value has been used
            2. Call the superclass teardown method
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics.
        """
        # 1. Call teardown
        if self.test_passed:
            super(Story2069, self).tearDown()

    def _data_driven_test_verify(self, bond_props, node_urls):
        """
        Description:
            Checks system configuration, output of run_plan. Returns any errors
        Args:
            bond_props (list): Bond properties
            node_urls (list): All nodes to be configured
        Returns:
            stderr (list): Any errors from checking configuration
        """
        errors = []

        for bond_prop in bond_props:
            for node_url in node_urls:
                self.log("info", "VERIFYING NODE {0}".format(node_url))
                node_fname = self.get_node_filename_from_url(
                    self.ms_node, node_url)

                # CHECK BOND CONFIG FILE EXISTS
                device_name = bond_prop["device_name"]
                path = "{0}/ifcfg-{1}".format(
                    test_constants.NETWORK_SCRIPTS_DIR, device_name)
                dir_contents = self.list_dir_contents(node_fname, path)
                if dir_contents == []:
                    errors.append("ifcfg-{0} doesn't exist".format(
                        device_name))

                # CHECK BOND FILE CONTENT
                std_out = self.get_file_contents(node_fname, path)

                if not self.is_text_in_list('DEVICE="{0}"'.format(
                        device_name), std_out):
                    errors.append('DEVICE="{0}" is not configured'.format(
                        device_name))

                if 'mode' in bond_props:
                    mode = bond_prop["mode"]
                    if not self.is_text_in_list("mode={0}".format(
                            mode), std_out):
                        errors.append("MODE is not configured")

                if 'miimon' in bond_props:
                    miimon = bond_prop["miimon"]
                    if not self.is_text_in_list("miimon={0}".format(
                            miimon), std_out):
                        errors.append("MIIMON is not configured")

                if 'ipaddress' in bond_props:
                    ip_address = bond_prop["ipaddress"]
                    if not self.is_text_in_list('IPADDR="{0}"'.format(
                            ip_address), std_out):
                        errors.append('IPADDR="{0}" is not configured'.format(
                            ip_address))

                if 'ipv6address' in bond_props:
                    ipv6_address = bond_prop["ipv6address"]
                    if not self.is_text_in_list('IPV6ADDR="{0}"'.format(
                            ipv6_address), std_out):
                        errors.append('IPV6ADDR="{0}" is not configured'
                                      .format(ipv6_address))

        return errors

    def _register_cleanup_bonds(self):
        """
        Description:
            Register nodes for cleanup of bonds.
        """
        for node in self.mn_nodes:
            self.add_nic_to_cleanup(node, self.bond_name, is_bond=True)

    @attr('all', 'revert', 'story2069', 'story2069_tc06')
    def test_06_n_create_bonded_interface_with_ipaddress(self):
        """
        @tms_id: litpcds_2069_tc06
        @tms_requirements_id: LITPCDS-2069
        @tms_title: test_06_n_create_bonded_interface_with_ipaddress
        @tms_description: Create bonds with different properties defined
        @tms_test_steps:
            @step: Create bond item with device_name=bondX
            @result: Bond created successfully
            @step: Create eth item with master=bondX and an ipaddress
            @result: Item fails to create with ValidationError
            @step: Create an 'eth' with master=bondX and a ipv6address
            @result: Item fails to create with ValidationError
            @step: Create an 'eth' with master=bondX and a network_name
            @result: Item fails to create with ValidationError
            @step: Remove previously created bond item
            @result: Item successfully removed
            @step: Create bond item without specifying device_name
            @result: Item fails to create with MissingRequiredPropertyError
            @step: Create bond item without specifying mode property
            @result: Item created successfully, 'mode' property
                appears in properties of bond item
            @step: Remove previously created bond item
            @result: Item successfully removed
            @step: Create bond item with ipaddress
                property but no network_name property
            @result: Item fails to create with ValidationError
            @step: Remove previously created eth item
            @result: Item successfully removed
            @step: Create test network
            @result: Successfully created test network
            @step: Create bond interface with valid macaddress and device_name
            @result: Successfully created eth item
            @step: Create bond item with mode=1 and miimon=100
            @result: Item created successfully
            @step: Create/run litp plan
            @result: Plan runs successfully
            @result: "Bonding Mode: fault-tolerance active-backup"
                (mode=1) is present in "/proc/net/bonding/bondX"
            @step: Update bond mode property with mode=6
            @result: Item updated successfully
            @step: Create/run litp plan
            @result: Plan runs successfully
            @result: "Bonding Mode: adaptive load balancing"
                (mode=6) is present in "/proc/net/bonding/bondX"
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Create a bond item.")
        bond_props = "device_name='{0}' " \
                     "ipaddress='{1}' network_name='test1' mode='1' " \
                     "miimon='100'".format(self.bond_name, self.bond_ipaddress)
        self.execute_cli_create_cmd(
            self.ms_node, self.bond_ms_url, "bond", bond_props)

        self.log("info", "2. Attempt to create an eth item with 'master' "
                         "and 'ipaddress' properties. Assert that it "
                         "fails with appropriate errors.")
        eth_props = "macaddress='{0}' device_name='{1}' master='{2}' " \
                    "ipaddress='10.10.10.11'".format(self.test_ms_if1_mac,
                                    self.test_ms_if1_name, self.bond_name)
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node, self.if_url, "eth", eth_props, expect_positive=False)

        master_error = 'Properties "ipaddress"/"ipv6address" and' \
                       ' "network_name" and "bridge" are not ' \
                       'allowed if "master" is specified.'
        self.assertTrue(self.is_text_in_list(master_error, std_err) and
                        self.is_text_in_list("ValidationError", std_err),
                        "Expected ValidationError '{0}' not returned.".format(
                            master_error))

        # START TEST test_07_n_create_bonded_interface_with_ipv6address
        self.log("info", "3. Attempt to create an eth item with 'master' "
                         "and 'ipv6address' properties. Assert that it "
                         "fails with appropriate errors.")
        eth_props = "macaddress='{0}' device_name='{1}' master='{2}' " \
            "ipv6address='2001:abcd:ef::05'".format(self.test_ms_if1_mac,
                                    self.test_ms_if1_name, self.bond_name)
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node, self.if_url, "eth", eth_props, expect_positive=False)

        network_error = 'Property "network_name" is required on this item, ' \
                        'if "bridge" property is not specified and' \
                        ' "ipaddress" or "ipv6address" property is specified.'
        self.assertTrue(self.is_text_in_list('ValidationError', std_err) and
                        self.is_text_in_list(network_error, std_err) and
                        self.is_text_in_list(master_error, std_err),
                        "Expected ValidationError(s) '{0}' and/or {1} "
                        "not returned.".format(network_error, master_error))

        # END TEST test_07_n_create_bonded_interface_with_ipv6address

        # START TEST test_08_n_create_bonded_interface_with_network_name
        self.log("info", "4. Attempt to create an eth item with 'master' "
                         "and 'network_name' properties. Assert that it "
                         "fails with appropriate errors.")
        eth_props = "macaddress='{0}' device_name='{1}' master='{2}' " \
                    "network_name='test1'".format(self.test_ms_if1_mac,
                                    self.test_ms_if1_name, self.bond_name)
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node, self.if_url, "eth", eth_props, expect_positive=False)

        self.assertTrue(self.is_text_in_list("ValidationError", std_err) and
                        self.is_text_in_list(master_error, std_err),
                        "Expected ValidationError '{0}' "
                        "not returned.".format(master_error))
        # END TEST test_08_n_create_bonded_interface_with_network_name

        self.log("info", "5. Remove previously created bond item.")
        self.execute_cli_remove_cmd(self.ms_node, self.bond_ms_url)

        # START TEST test_11_n_create_bond_without_device_name
        self.log("info", "6. Attempt to create a bond item without "
                         "specifying 'device_name' property. Assert "
                         "that it fails with appropriate errors.")
        bond_props = "ipaddress='{0}' network_name='test1' " \
                     "mode='1' miimon='100'".format(self.bond_ipaddress)

        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node, self.bond_ms_url, "bond",
            bond_props, expect_positive=False)
        device_error = 'ItemType "bond" is required to have' \
                       ' a property with name "device_name"'
        self.assertTrue(
            self.is_text_in_list("MissingRequiredPropertyError", std_err) and
            self.is_text_in_list(device_error, std_err),
            "Expected MissingRequiredPropertyError '{0}' "
            "not returned.".format(device_error))

        # END TEST test_11_n_create_bond_without_device_name

        # START TEST test_14_p_create_bond_without_mode_property
        self.log("info", "7. Create a bond item without"
                         " specifying 'mode' property.")
        bond_props = "device_name='{0}' ipaddress='{1}' " \
                     "network_name='test1'".format(self.bond_name,
                                                   self.bond_ipaddress)
        self.execute_cli_create_cmd(self.ms_node, self.bond_ms_url,
                                    "bond", bond_props)

        self.log("info", "7.1. Assert 'mode' property "
                         "is in bond item properties.")
        stdout, _, _ = self.execute_cli_show_cmd(
            self.ms_node, self.bond_ms_url)
        prop_check = "mode: 1"
        self.assertTrue(self.is_text_in_list(prop_check, stdout),
                        "Expected property '{0}' not present "
                        "under {1}".format(prop_check, self.bond_ms_url))
        # END TEST test_14_p_create_bond_without_mode_property

        self.log("info", "8. Remove previously created bond item.")
        self.execute_cli_remove_cmd(self.ms_node, self.bond_ms_url)

        # START TEST test_24_n_validate_bond_network_name
        self.log("info", "9. Attempt to create a bond item with 'ipaddress' "
                         "property set but 'network_name' not set. Assert "
                         "that it fails with appropriate errors.")
        eth_props = "macaddress='{0}' device_name='{1}' master='{2}'".format(
            self.test_ms_if1_mac, self.test_ms_if1_name, self.bond_name)
        self.execute_cli_create_cmd(
            self.ms_node, self.if_url, "eth", eth_props)

        bond_props = "ipaddress='{0}' mode='1' device_name='{1}'".format(
            self.bond_ipaddress, self.bond_name)
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node, self.bond_ms_url, "bond",
            bond_props, expect_positive=False)

        self.assertTrue(self.is_text_in_list("ValidationError", std_err) and
                        self.is_text_in_list(network_error, std_err),
                        "Expected ValidationError '{0}' "
                        "not returned.".format(master_error))
        # END TEST test_24_n_validate_bond_network_name

        self.log("info", "10. Remove previously created eth item.")
        self.execute_cli_remove_cmd(self.ms_node, self.if_url)

        # START TEST test_22_p_validate_mode_miimon_property
        self.log("info", "11. Create network 'test1'.")
        networks_path = self.find(
            self.ms_node, "/infrastructure", "network", False)[0]
        network_url = networks_path + "/test_network2069"
        props = "name='test1' subnet='10.10.10.0/24'"
        self.execute_cli_create_cmd(
            self.ms_node, network_url, "network", props)

        self.log("info", "12. Create eth item.")
        eth_props = "macaddress='{0}' device_name='{1}' master='{2}'".format(
            self.test_ms_if1_mac, self.test_ms_if1_name, self.bond_name)
        self.execute_cli_create_cmd(
            self.ms_node, self.if_url, "eth", eth_props)

        self.log("info", "13. Create bond item with mode='1'.")
        bond_props = "ipaddress='{0}' miimon='100' network_name='test1' " \
                     "mode='1' device_name='{1}'".format(self.bond_ipaddress,
                                                         self.bond_name)
        self.execute_cli_create_cmd(
            self.ms_node, self.bond_ms_url, "bond", bond_props)

        self.log("info", "14. Create/run LITP plan, wait "
                         "for it to complete successfully.")
        self.execute_cli_createplan_cmd(self.ms_node)

        self._register_cleanup_bonds()

        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(
            self.ms_node, test_constants.PLAN_COMPLETE),
            "Plan did not complete successfully.")

        self.log("info", "15. Check sysconfig file has correct configuration.")
        props = self.get_props_from_url(self.ms_node, self.bond_ms_url)
        std_err = self._data_driven_test_verify([props], [self.ms_url])
        self.assertEqual([], std_err)

        self.log("info", "16. Check bonding file has correct configuration.")
        bonding_file = "/proc/net/bonding/{0}".format(self.bond_name)
        bond_params = self.get_file_contents(self.ms_node, bonding_file)
        prop_check = "Bonding Mode: fault-tolerance (active-backup)"
        self.assertTrue(prop_check in bond_params,
                        "Expected '{0}' not present in {1}".format(
                            prop_check, bonding_file))

        self.log("info", "17. Update bond item property mode='6'.")
        bond_props = "mode='6'"
        self.execute_cli_update_cmd(self.ms_node, self.bond_ms_url, bond_props)

        self.log("info", "18. Create/run LITP plan, wait "
                         "for it to complete successfully.")
        self.execute_cli_createplan_cmd(self.ms_node)

        self._register_cleanup_bonds()

        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(
            self.ms_node, test_constants.PLAN_COMPLETE),
            "Plan did not complete successfully.")

        self.log("info", "19. Check bonding file has been updated correctly.")
        bond_params = self.get_file_contents(self.ms_node, bonding_file)
        adaptive = "Bonding Mode: adaptive load balancing"
        if not self.is_text_in_list(adaptive, bond_params):
            self.test_passed = False
        self.assertTrue(adaptive in bond_params,
                        "Expected '{0}' not present in {1}".format(
                            adaptive, bonding_file))
