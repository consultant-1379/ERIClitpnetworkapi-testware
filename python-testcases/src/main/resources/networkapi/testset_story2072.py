"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     June 2014
@author:    Gabor Szabo
@summary:   Integration
            Agile: STORY LITPCDS-2072
"""
from litp_generic_test import GenericTest, attr
import test_constants


class Story2072(GenericTest):
    """
    As a LITP User, I want to configure network interfaces with IEEE 802.1q
    VLAN tags, so that I can have secure and scalable network management
    """
    test_ms_if1 = None
    test_ms_if2 = None
    test_node_if1 = None
    test_node_if2 = None
    VLAN1_ID = 72
    VLAN2_ID = 73

    def setUp(self):
        """
        Description:
            Runs before every single test.
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and
            variables common to all tests are available.
        """
        # 1. Call super class setup
        super(Story2072, self).setUp()

        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filename()
        self.vlan_url = "/ms/network_interfaces/vlan_2072"
        self.vlan_props = "device_name='{0}' network_name='test'"

    def tearDown(self):
        """
        Description:
            Runs after each test.
        Actions:
            1. Cleanup after test if global results value has been used
            2. Call the superclass teardown method
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        # 1. Call teardown
        super(Story2072, self).tearDown()

        # DECONFIGURE test interface on MS
        if self.test_ms_if1 is not None:
            cmd = "/sbin/ip link del {0}.{1}".format(
                self.test_ms_if1["NAME"], self.VLAN1_ID)
            self.run_command(self.ms_node, cmd, su_root=True)
            cmd = "/sbin/ifdown {0}".format(self.test_ms_if1["NAME"])
            self.run_command(self.ms_node, cmd, su_root=True)
        if self.test_ms_if2 is not None:
            cmd = "/sbin/ip link del {0}.{1}".format(
                self.test_ms_if2["NAME"], self.VLAN2_ID)
            self.run_command(self.ms_node, cmd, su_root=True)
            cmd = "/sbin/ifdown {0}".format(self.test_ms_if2["NAME"])
            self.run_command(self.ms_node, cmd, su_root=True)

        # DECONFIGURE test interface on MNs
        all_nodes = self.get_managed_node_filenames()
        for node in all_nodes:
            if self.test_node_if1 is not None:
                cmd = "/sbin/ip link del {0}.{1}".format(
                    self.test_node_if1["NAME"], self.VLAN1_ID)
                self.run_command(node, cmd, su_root=True)
                cmd = "/sbin/ifdown {0}".format(
                    self.test_node_if1["NAME"])
                self.run_command(node, cmd, su_root=True)
            if self.test_node_if2 is not None:
                cmd = "/sbin/ip link del {0}.{1}".format(
                    self.test_node_if2["NAME"], self.VLAN2_ID)
                self.run_command(node, cmd, su_root=True)
                cmd = "/sbin/ifdown {0}".format(
                    self.test_node_if2["NAME"])
                self.run_command(node, cmd, su_root=True)

        # REMOVE VLAN IFCFG FILE ON MS
        if self.test_ms_if1 is not None:
            ifcfg_file = "{0}/ifcfg-{1}.{2}".format(
                test_constants.NETWORK_SCRIPTS_DIR, self.test_ms_if1["NAME"],
                self.VLAN1_ID)
            self.remove_item(self.ms_node, ifcfg_file, su_root=True)
        if self.test_ms_if2 is not None:
            ifcfg_file = "{0}/ifcfg-{1}.{2}".format(
                test_constants.NETWORK_SCRIPTS_DIR, self.test_ms_if2["NAME"],
                self.VLAN2_ID)
            self.remove_item(self.ms_node, ifcfg_file, su_root=True)

        # REMOVE VLAN IFCFG FILE ON MNs
        all_nodes = self.get_managed_node_filenames()
        for node in all_nodes:
            if self.test_node_if1 is not None:
                ifcfg_file = "{0}/ifcfg-{1}.{2}".format(
                    test_constants.NETWORK_SCRIPTS_DIR,
                    self.test_node_if1["NAME"], self.VLAN1_ID)
                self.remove_item(node, ifcfg_file, su_root=True)
            if self.test_node_if2 is not None:
                ifcfg_file = "{0}/ifcfg-{1}.{2}".format(
                    test_constants.NETWORK_SCRIPTS_DIR,
                    self.test_node_if2["NAME"], self.VLAN2_ID)
                self.remove_item(node, ifcfg_file, su_root=True)

    def _create_invalid_vlan(self, vlan_id):
        """
        Description:
            Attempts to create a LITP VLAN item with the given invalid ID.
            Asserts that the creation of the VLAN fails
                with 'ValidationError' and 'Invalid value' error.
        Args:
            vlan_id (str): Invalid ID to create VLAN with.
        """
        props = self.vlan_props.format(vlan_id)
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node, self.vlan_url,
            "vlan", props, expect_positive=False)

        # Check expected "ValidationError" is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err),
                        "Expected ValidationError not returned.")

        # Check expected "Invalid value" error is present
        self.assertTrue(self.is_text_in_list("Invalid value", std_err),
                        "Expected 'Invalid value' error not returned.")

        # Assert that "Device must not be already tagged" is not present
        self.assertFalse(self.is_text_in_list(
            "Device must not be already tagged", std_err))

    @attr('all', 'revert', 'story2072', 'story2072_tc10')
    def test_10_n_validation_vlan_id(self):
        """
        @tms_id: litpcds_2072_tc10
        @tms_requirements_id: LITPCDS-2072
        @tms_title: test_10_n_validation_vlan_id
        @tms_description: Validation Error returned when creating network VLAN
            item with ID not in range 1-4094 and invalid values for device_name
        @tms_test_steps:
            @step: Create network VLAN item type with invalid ID '0'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type with invalid ID '4095'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type with invalid ID 'test'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type with
                invalid device_name 'eth45678901.3456'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type with invalid device_name ''
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type
                with invalid device_name 'eth9'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type
                with invalid device_name 'eth9..10'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @result: "Device must not be already tagged" not in std_err
            @step: Create network VLAN item type
                with invalid device_name 'eth9.10.11'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type
                with invalid device_name 'eth9.'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type
                with invalid device_name '.12'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create network VLAN item type
                with invalid device_name 'eth9.eth10'
            @result: Creation of VLAN fails with "ValidationError"
            @result: Creation of VLAN fails with "Invalid value"
            @step: Create VLAN without specifying any property
            @result: Creation of VLAN fails with "MissingRequiredPropertyError"
            @result: Error states that "device_name" is required
            @result: Creation of VLAN fails with "ValidationError"
            @result: Error states that "network_name" is required
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Attempt to create VLAN items with invalid "
                         "IDs. Assert creation of each VLAN fails "
                         "with 'ValidationError'.")
        self._create_invalid_vlan('eth72.0')
        self._create_invalid_vlan('eth72.4095')
        self._create_invalid_vlan('test')
        self._create_invalid_vlan('eth45678901.3456')
        self._create_invalid_vlan('')
        self._create_invalid_vlan('eth9')
        self._create_invalid_vlan('eth9..10')
        self._create_invalid_vlan('eth9.10.11')
        self._create_invalid_vlan('eth9.')
        self._create_invalid_vlan('.12')
        self._create_invalid_vlan('eth9.eth10')

        self.log("info", "2. Attempt to create a VLAN item without "
                         "specifying any property. Assert that creation "
                         "fails with 'MissingRequiredPropertyError' and"
                         " 'ValidationError' errors.")
        props = ""
        _, std_err, rc = self.execute_cli_create_cmd(
            self.ms_node, self.vlan_url, "vlan", props, expect_positive=False)
        self.assertNotEqual(0, rc)

        # Check expected 'MissingRequiredPropertyError' is present
        self.assertTrue(self.is_text_in_list(
            "MissingRequiredPropertyError", std_err),
            "Expected MissingRequiredPropertyError not returned.")

        expected_err = 'ItemType "vlan" is required to have' \
                       ' a property with name "device_name"'
        self.assertTrue(
            self.is_text_in_list(expected_err, std_err),
            "Expected error '{0}' not returned.".format(expected_err))

        # Check expected "ValidationError" is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err),
                        "Expected ValidationError not returned.")

        expected_err = 'Property "network_name" is required on this item, ' \
                       'if "bridge" property is not specified.'
        self.assertTrue(
            self.is_text_in_list(expected_err, std_err),
            "Expected error '{0}' not returned.".format(expected_err))
