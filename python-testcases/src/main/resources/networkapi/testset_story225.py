"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     January 2014
@author:    Kieran Duggan
@summary:   Integration test for creating a bridge for virtual nodes
            Agile: STORY LITPCDS-225
"""
from litp_generic_test import GenericTest, attr


class Story225(GenericTest):
    """
    As an Administrator I want to create a bridge over a physical
    interface so I can attach virtual nodes to the network.
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
            variables common to all tests are available.
        """
        # 1. Call super class setup
        super(Story225, self).setUp()

        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filename()
        self.br_url = "/ms/network_interfaces/br225"
        self.if_url = "/ms/network_interfaces/if225"

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
        super(Story225, self).tearDown()

    @attr('all', 'revert', 'story225', 'story225_tc11')
    def test_11_p_validate_default_values(self):
        """
        @tms_id: litpcds_225_tc11
        @tms_requirements_id: LITPCDS-225
        @tms_title: test_11_p_validate_default_values
        @tms_description: Bridge item is created with default values for "stp"
            and "forwarding_delay" properties. Correct error returned when
            creating bridge interface with invalid/missing properties.
        @tms_test_steps:
            @step: Create bridge item with only mandatory properties
            (specifically, without 'stp' and 'forwarding_delay' properties)
            @result: Bridge item created with 'stp' and 'forwarding_delay'
                properties which are set to correct default values
            @step: Create network bridge item with valid properties
            @result: Bridge item created successfully
            @step: Create eth network interface for
                bridge without "macaddress" or "device_name" properties
            @result: eth network interface item fails to create
            @result: 'MissingRequiredPropertyError' thrown
            @result: "macaddress" property required error thrown
            @result: "device_name" property required error thrown
            @step: Create eth network interface for bridge with valid
                "macaddress", "device_name", and "ipaddress" properties
            @result: eth network interface item fails to create
            @result: 'ValidationError' thrown
            @result: Error informing user that properties "ipaddress",
                "ipv6address" and "network_name" are not
                allowed if "bridge" is specified
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Create bridge item-type with mandatory"
                         " 'device_name' and 'network_name' properties.")
        props = "device_name='br225' network_name='test'"
        self.execute_cli_create_cmd(self.ms_node, self.br_url, "bridge", props)

        self.log("info", "2. Check that default value 'stp' has "
                         "been created with correct value.")
        stp_prop = self.get_props_from_url(self.ms_node, self.br_url, "stp")
        self.assertEqual("false", stp_prop)

        self.log("info", "3. Check that default value 'forwarding_delay' has "
                         "been created with correct value.")
        fwd_delay_prop = self.get_props_from_url(
            self.ms_node, self.br_url, "forwarding_delay")
        self.assertEqual("4", fwd_delay_prop)

        self.log("info", "4. Remove previously created bridge item.")
        self.execute_cli_remove_cmd(self.ms_node, self.br_url)

        self.log("info", "5. Create bridge item-type "
                         "with 'stp' and 'forwarding_delay' properties.")
        props = "device_name='br225' ipaddress='10.10.10.2' " \
                "forwarding_delay='4' stp='false' network_name='test'"
        self.execute_cli_create_cmd(self.ms_node, self.br_url, "bridge", props)

        self.log("info", "5. Attempt to create test interface without "
                         "mandatory 'macaddress' and 'device_name' "
                         "properties. Assert that "
                         "'MissingRequiredPropertyError' error is returned for"
                         " 'macaddress' and 'device_name'.")
        props = "bridge='br225'"
        _, stderr, _ = self.execute_cli_create_cmd(
            self.ms_node, self.if_url, "eth", props, expect_positive=False)

        # Check expected MissingRequiredPropertyError is present
        self.assertTrue(
            self.is_text_in_list("MissingRequiredPropertyError", stderr),
            "Expected MissingRequiredPropertyError not returned.")

        item_type_error = 'ItemType "eth" is required to ' \
                          'have a property with name "{0}"'
        # Check expected 'macaddress' error is present
        self.assertTrue(self.is_text_in_list(
            item_type_error.format("macaddress"), stderr),
            "Expected 'macaddress' error not returned.")

        # Check expected 'device_name' error is present
        self.assertTrue(self.is_text_in_list(
            item_type_error.format("device_name"), stderr),
            "Expected 'device_name' error not returned.")

        self.log("info", "6. Attempt to create test interface with"
                         " 'ipaddress' and 'network_name' properties. "
                         "Assert that a 'ValidationError' error is "
                         "returned with correct error info.")
        props = "bridge='br225' macaddress='2C:59:E5:3D:83:5B' " \
                "device_name='eth6' ipaddress='10.10.10.2' network_name='test'"
        _, stderr, _ = self.execute_cli_create_cmd(
            self.ms_node, self.if_url, "eth", props, expect_positive=False)

        # Check expected ValidationError is present
        self.assertTrue(self.is_text_in_list("ValidationError", stderr),
                        "Expected ValidationError not returned.")

        # Check expected error is present
        check_err = 'Properties "ipaddress"/"ipv6address" and' \
                    ' "network_name" are not allowed if "bridge" is specified'
        self.assertTrue(
            self.is_text_in_list(check_err, stderr),
            "Expected error '{0}' not returned.".format(check_err))
