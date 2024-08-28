"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     September 2014
@author:    Kieran Duggan, Boyan Mihovski, Remy Horton,
            Carlos Novo, Mary Russell
@summary:   Integration
            Agile: STORY LITPCDS-5175
"""
from litp_generic_test import GenericTest, attr


class Story5175(GenericTest):
    """
    Description:
        As a LITP User, I want to create IPv6 routes,
        so I can control connectivity to remote networks
    """

    def setUp(self):
        """
        Description:
            Runs before every single test
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and
            variables common to all tests are available
        """
        # 1. Call super class setup
        super(Story5175, self).setUp()
        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filename()
        self.test_nodes = self.get_managed_node_filenames()
        self.test_nodes.sort()

        self.test_route = "route6"
        self.route_url = self.find(self.ms_node, "/infrastructure",
                                   "route-base", False, find_refs=True)[0]
        self.route_path = self.route_url + "/{0}_test".format(self.test_route)

        self.subnet_val_err = 'ValidationError in property: "subnet"'
        self.subnet_prefix_err = 'Subnet must include prefix length'
        self.invalid_value = "Invalid value '{0}'."
        self.gw_val_err = 'ValidationError in property: "gateway"'
        self.reserved_nw = 'Subnet cannot be a reserved network.'
        self.invalid_ipv6_val = "Invalid IPv6Address value '{0}'"
        self.invalid_ipv6_sub = "Invalid IPv6 subnet value '{0}'"
        self.value_ipv6 = "Value must be an IPv6 {0}"
        self.reserved_gw = "The gateway address {0} cannot be reserved."
        self.subnet_gw_props = "subnet='{0}' gateway='{1}'"
        self.missing_prop = 'MissingRequiredPropertyError in property: "{0}"'
        self.required_prop = 'ItemType "{0}" is required to ' \
                             'have a property with name "{1}"'

    def tearDown(self):
        """
        Description:
            Run after each test
        Actions:
            1. Cleanup after test if global results value has been used
            2. Call the superclass teardown method
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        # 1. Call teardown
        super(Story5175, self).tearDown()

    def invalid_subnet_gateway_props(self, sub_props, gw_props, errors):
        """
        Description:
            Attempts to create a route6 item with
                the given subnet and gateway properties.
            Asserts that item creation fails and throws the expected errors.
        Args:
            sub_props (str): Subnet value. Pass in 'None' to not set at all
            gw_props (str): Gateway value. Pass in 'None' to not set at all
            errors (list): Expected errors from failed creation
        """
        # Set subnet and gateway properties
        if sub_props is None and gw_props:
            route_props = "gateway='{0}'".format(gw_props)
        elif gw_props is None and sub_props:
            route_props = "subnet='{0}'".format(sub_props)
        else:
            route_props = self.subnet_gw_props.format(sub_props, gw_props)

        # Attempt to create the item
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node, self.route_path, self.test_route,
            route_props, expect_positive=False)

        # Ensure all expected errors are returned
        for err in errors:
            self.assertTrue(self.is_text_in_list(err, std_err),
                            "Expected error '{0}' not returned.".format(err))

    @attr('all', 'revert', 'story5175', 'story5175_tc14')
    def test_14_n_validate_route6_item(self):
        """
        @tms_id: litpcds_5175_tc14
        @tms_requirements_id: LITPCDS-5175
        @tms_title: test_14_n_validate_route6_item
        @tms_description: Assert errors are returned when creating
            'route6' item types with invalid subnet and/or gateway values
        @tms_test_steps:
            @step: Create 'route6' item with
                invalid subnet and/or gateway properties
            @result: Item creation fails with correct error(s)
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log("info", "1. Create route6 item without subnet prefix.")
        subprops = '2121::'
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, self.subnet_prefix_err]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "2. Create route6 item without specifying gateway.")
        subprops = '2121::/64'
        errors = [self.missing_prop.format('gateway'),
                  self.required_prop.format(self.test_route, 'gateway')]
        self.invalid_subnet_gateway_props(subprops, None, errors)

        self.log("info", "3. Create route6 item without specifying subnet.")
        errors = [self.missing_prop.format('subnet'),
                  self.required_prop.format(self.test_route, 'subnet')]
        self.invalid_subnet_gateway_props(None, gwprops, errors)

        self.log("info", "4. Create route6 item without value for gateway.")
        subprops = '2001::/48'
        errors = [self.gw_val_err, self.invalid_value.format('')]
        self.invalid_subnet_gateway_props(subprops, '', errors)

        self.log("info", "5. Create route6 item with empty value for gateway.")
        errors = [self.gw_val_err, self.invalid_value.format('')]
        self.invalid_subnet_gateway_props(subprops, ' ', errors)

        self.log("info", "6. Create route6 item without value for subnet.")
        errors = [self.subnet_val_err, self.invalid_value.format('')]
        self.invalid_subnet_gateway_props('', gwprops, errors)

        self.log("info", "7. Create route6 item with empty value for subnet.")
        errors = [self.subnet_val_err, self.invalid_value.format('')]
        self.invalid_subnet_gateway_props(' ', gwprops, errors)

        self.log("info", "8. Create route6 item without "
                         "values for subnet or gateway.")
        # Expected errors
        ipv6_nw = "{0} {1}".format(
            self.invalid_value.format(''), self.value_ipv6.format('network'))
        ipv6_addr = "{0} {1}".format(
            self.invalid_value.format(''), self.value_ipv6.format('address'))
        errors = [self.subnet_val_err, self.gw_val_err, ipv6_nw, ipv6_addr]
        self.invalid_subnet_gateway_props('', '', errors)

        self.log("info", "9. Create route6 item with "
                         "empty values for subnet and gateway.")
        self.invalid_subnet_gateway_props(' ', ' ', errors)

        self.log("info", "10. Create route6 item with more than "
                         "one replaced group of zeros for subnet.")
        subprops = '2000:::/48'
        gwprops = '2001:DB8:0:0:800:27FF:FE00:0'
        errors = [self.subnet_val_err, self.invalid_ipv6_sub.format(subprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "11. Create route6 item with more than "
                         "one replaced group of zeros for gateway.")
        subprops = '2000::/48'
        gwprops = '2001:DB8:::0'
        errors = [self.gw_val_err, self.invalid_ipv6_val.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "12. Create route6 item with more than one "
                         "replaced group of zeros for subnet and gateway.")
        subprops = '2000:::/48'
        errors = [self.gw_val_err, self.subnet_val_err,
                  self.invalid_ipv6_sub.format(subprops),
                  self.invalid_ipv6_val.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "13. Create route6 item with '/' in "
                         "subnet but without defining prefix length.")
        subprops = '2121::/'
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, self.invalid_ipv6_sub.format(subprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "14. Create route6 item with '\\' in subnet.")
        subprops = '2001:DB8::dc\\71'
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, self.invalid_value.format(subprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "15. Create route6 item with '\\' in gateway.")
        subprops = '2121::/64'
        gwprops = '2001:DB8::dc\\71'
        errors = [self.gw_val_err, self.invalid_value.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "16. Create route6 item with"
                         " '\\' in suvbnet and gateway.")
        subprops = '2001:DB8::dc\\71/48'
        gwprops = '2001:b\\::1:1'
        errors = [self.subnet_val_err, self.gw_val_err,
                  self.invalid_value.format(subprops),
                  self.invalid_value.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "17. Create route6 item with '\\\\' in gateway.")
        subprops = '2001:DB8::dc71/48'
        gwprops = '2001:b\\\\::1:1'
        errors = [self.gw_val_err, self.invalid_value.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "18. Create route6 item with invalid subnet.")
        subprops = 'xxx::xxx/64'
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, self.invalid_value.format(subprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "19. Create route6 item with invalid gateway.")
        subprops = '::/0'
        gwprops = '2001:xx::1:1'
        errors = [self.gw_val_err, self.invalid_ipv6_val.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "20. Create route6 item with multicast in gateway.")
        gwprops = 'ff01::300'
        errors = [self.gw_val_err, "Cannot use multicast "
                                   "address {0} as gateway".format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        self.log("info", "21. Create route6 item with multicast in subnet.")
        subprops = 'ff01::300/64'
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, "Subnet cannot be a multicast address."]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)

        # START test_16_n_validate_subnet_prefix
        self.log("info", "22. Create route6 item where subnet property "
                         "has prefix of 0 and network part is global address.")
        subprops = '2121::/0'
        err = "Routing destination '2121::' cannot have prefix length 0, " \
              "because it is reserved for the default route only (::/0)."
        errors = [self.subnet_val_err, err]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_16_n_validate_subnet_prefix

        # START test_17_n_create_route6_with_loopback_address_gateway
        self.log("info", "23. Create route6 item where gateway "
                         "property is set to local loopback.")
        subprops = '2002::/64'
        gwprops = '::1'
        err = "The gateway address {0} cannot " \
              "be local loopback.".format(gwprops)
        errors = [self.gw_val_err, err]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_17_n_create_route6_with_loopback_address_gateway

        # START test_18_n_create_route6_with_loopback_address_subnet
        self.log("info", "24. Create route6 item where subnet"
                         "property is set to a reserved network.")
        subprops = '::1/128'
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, self.reserved_nw]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_18_n_create_route6_with_loopback_address_subnet

        # START test_19_n_create_route6_with_unspecified_address_gateway
        self.log("info", "25. Create route6 item where gateway "
                         "property is set to an undefined address.")
        subprops = '2002::/64'
        gwprops = '::'
        err = "The gateway address {0} cannot " \
              "be the undefined address.".format(gwprops)
        errors = [self.gw_val_err, err]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_19_n_create_route6_with_unspecified_address_gateway

        # START test_20_n_create_route6_with_unspecified_address_subnet
        self.log("info", "26. Create route6 item where subnet "
                         "property is set to a reserved network.")
        subprops = '::/128'
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, self.reserved_nw]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_20_n_create_route6_with_unspecified_address_subnet

        # START test_21_n_create_route6_with_ipv4_subnet_for_gateway
        self.log("info", "27. Create route6 item with gateway set to IPv4.")
        subprops = '::/0'
        gwprops = '10.0.0.0'
        errors = [self.gw_val_err, self.invalid_value.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_21_n_create_route6_with_ipv4_subnet_for_gateway

        # START test_22_n_create_route6_with_ipv4_addr_for_gw_and_sub
        self.log("info", "28. Create route6 item with subnet "
                         "and gateway set to IPv4 address.")
        subprops = '10.0.0.0/8'
        gwprops = '10.0.0.1'
        errors = [self.subnet_val_err, self.gw_val_err,
                  self.invalid_value.format(subprops),
                  self.invalid_value.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_22_n_create_route6_with_ipv4_addr_for_gw_and_sub

        # START test_23_n_create_route6_with_ipv4_subnet_for_destination
        self.log("info", "29. Create route6 item with subnet set to IPv4.")
        gwprops = '2001:bb::1:1'
        errors = [self.subnet_val_err, self.invalid_value.format(subprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_23_n_create_route6_with_ipv4_subnet_for_destination

        # START test_24_n_create_route6_with_local_link_address_for_subnet
        self.log("info", "30. Create route6 item where subnet "
                         "property is set to link-local address.")
        subprops = 'fe80::900/48'
        err = "Cannot use link-local address fe80::/48 as subnet."
        errors = [self.subnet_val_err, err]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_24_n_create_route6_with_local_link_address_for_subnet

        # START test_25_n_create_route6_with_loopback_addr_for_sub_and_gw
        self.log("info", "31. Create route6 item where subnet and gateway "
                         "properties are set to a reserved network.")
        props = '::1/128'
        errors = [self.subnet_val_err, self.gw_val_err, self.reserved_nw,
                  self.invalid_value.format(props)]
        self.invalid_subnet_gateway_props(props, props, errors)
        # END test_25_n_create_route6_with_loopback_addr_for_sub_and_gw

        # START test_26_n_create_route6_with_local_link_addr_for_sub_and_gw
        self.log("info", "32. Create route6 item where subnet and "
                         "gateway properties are set to link-local.")
        subprops = 'fe80::/10'
        gwprops = 'fe80::800:27ff:fe00:1'
        err1 = "Cannot use link-local address {0} as subnet.".format(subprops)
        err2 = "The gateway address {0} cannot be link-local.".format(gwprops)
        errors = [self.subnet_val_err, self.gw_val_err, err1, err2]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_26_n_create_route6_with_local_link_addr_for_sub_and_gw

        # START test_27_n_create_route6_with_prefix_for_gateway
        self.log("info", "33. Create route6 item where gateway property "
                         "is set to a prefix IPv6 address.")
        subprops = '3001:db8::/64'
        gwprops = '2001:DB8:0:0:800:27FF:FE00:0/64'
        errors = [self.gw_val_err, self.invalid_value.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_27_n_create_route6_with_prefix_for_gateway

        # START test_28_n_create_route6_with_reserved_address_for_subnet
        self.log("info", "34. Create route6 items where subnet "
                         "property is set to a reserved network.")
        subnets_to_check = ['0000::/8', '0100::/8', '0200::/7', '0400::/6',
                            '0800::/5', '1000::/4', '4000::/3', '6000::/3',
                            '8000::/3', 'a000::/3', 'c000::/3', 'e000::/4',
                            'f000::/5', 'fe00::/9']

        gwprops = "2001:DB8:0:0:800:27FF:FE00:0"
        errors = [self.reserved_nw]
        for subprops in subnets_to_check:
            self.invalid_subnet_gateway_props(
                subprops, gwprops, errors)
        # END test_28_n_create_route6_with_reserved_address_for_subnet

        # START test_29_n_create_route6_with_reserved_address_for_gateway
        self.log("info", "35. Create route6 items where gateway "
                         "property is set to a reserved network.")
        gateways_to_check = ['00b8::0', '01b8::1', '02db::0', '04db::1',
                             '08aa::1', '18aa::1', '48bb::1', '68ba::1',
                             '87bc::1', 'aa00:db8::0', 'cb01:db8::0',
                             'eabd::1', 'f0ac::2', 'fe0a:db8::1']

        subprops = '3001:db8::/64'
        for gwprops in gateways_to_check:
            errors = [self.reserved_gw.format(gwprops)]
            self.invalid_subnet_gateway_props(
                subprops, gwprops, errors)
        # END test_29_n_create_route6_with_reserved_address_for_gateway

        # START test_30_n_create_route6_with_reserved_addr_for_gw_and_sub
        self.log("info", "36. Create route6 items where subnet and gateway "
                         "properties are set to a reserved network.")
        subprops = 'c000:db8::/3'
        gwprops = '00b8::0'
        errors = [self.subnet_val_err, self.gw_val_err, self.reserved_nw,
                  self.reserved_gw.format(gwprops)]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_30_n_create_route6_with_reserved_addr_for_gw_and_sub

        # START test_32_n_route6_with_res_addr_for_sub_and_uniq_addr_for_gw
        self.log("info", "37. Create route6 items where subnet "
                         "property is set to a reserved network.")
        subprops = 'c000:db8::/3'
        gwprops = '2001:D88::800:27FF:FE00:0'
        errors = [self.reserved_nw]
        self.invalid_subnet_gateway_props(subprops, gwprops, errors)
        # END test_32_n_route6_with_res_addr_for_sub_and_uniq_addr_for_gw
