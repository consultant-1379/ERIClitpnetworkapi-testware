'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     June 2014
@author:    Kieran Duggan
@summary:   Integration
            Agile: STORY-2064
'''

from litp_generic_test import GenericTest, attr
from xml_utils import XMLUtils
import test_constants


class Story2064(GenericTest):

    """
    As a LITP User, I want to create IPs for IPv6 addresses,
    so I can to assign IPv6 address to network interfaces
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
            Runs before every single test
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and variables
            common to all tests are available.
        """

        # 1. Call super class setup
        super(Story2064, self).setUp()

        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filename()
        self.xml = XMLUtils()

    def tearDown(self):
        """
        Description:
            Run after each test and performs the following:
        Actions:
            1. Cleanup after test if global results value has been used
            2. Call the superclass teardown method
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        # 1. call teardown
        super(Story2064, self).tearDown()

        # DECONFIGURE test interface ON MS
        if self.test_ms_if1 is not None:
            cmd = "/sbin/ifdown {0}".format(self.test_ms_if1["NAME"])
            self.run_command(self.ms_node, cmd, su_root=True)
            cmd = "/sbin/ifdown {0}.{1}".format(self.test_ms_if1["NAME"],
                                                self.VLAN1_ID)
            self.run_command(self.ms_node, cmd, su_root=True)
        if self.test_ms_if2 is not None:
            cmd = "/sbin/ifdown {0}".format(self.test_ms_if2["NAME"])
            self.run_command(self.ms_node, cmd, su_root=True)
            cmd = "/sbin/ifdown {0}.{1}".format(self.test_ms_if2["NAME"],
                                                self.VLAN2_ID)
            self.run_command(self.ms_node, cmd, su_root=True)

        # DECONFIGURE test interface ON MNs
        all_nodes = self.get_managed_node_filenames()
        for node in all_nodes:
            if self.test_node_if1 is not None:
                cmd = "/sbin/ifdown {0}".format(self.test_node_if1["NAME"])
                self.run_command(node, cmd, su_root=True)
                cmd = "/sbin/ifdown {0}.{1}".format(self.test_node_if1["NAME"],
                                                    self.VLAN1_ID)
                self.run_command(node, cmd, su_root=True)
            if self.test_node_if2 is not None:
                cmd = "/sbin/ifdown {0}".format(self.test_node_if2["NAME"])
                self.run_command(node, cmd, su_root=True)
                cmd = "/sbin/ifdown {0}.{1}".format(self.test_node_if2["NAME"],
                                                    self.VLAN2_ID)
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
                    self.test_node_if1["NAME"],
                    self.VLAN1_ID)
                self.remove_item(node, ifcfg_file, su_root=True)
            if self.test_node_if2 is not None:
                ifcfg_file = "{0}/ifcfg-{1}.{2}".format(
                    test_constants.NETWORK_SCRIPTS_DIR,
                    self.test_node_if2["NAME"],
                    self.VLAN2_ID)
                self.remove_item(node, ifcfg_file, su_root=True)

    @attr('all', 'revert', 'story2064', 'story2064_tc27', 'kgb-other')
    def test_27_n_validate_bridge_configured(self):
        """
            @tms_id:
                litpcds_2064_tc27
            @tms_requirements_id: LITPCDS-2064
            @tms_title:
                test_27_n_validate_bridge_configured.
            @tms_description:
                Test that ip6address can't be set if bridge is also configured
                assert that the correct error is thrown.
            @tms_test_steps:
             @step:
                create a bridge item with valid properties.
             @result:
                litp cli create bridge command runs successfully.
             @step:
                create an eth item that use the previously created bridge
                as bridge name which contains an ipv6address.
             @result:
                litp cli create eth item command fails to execute.
             @step:
                Check a Validation Error is thrown that tells the user that
                ip6address is not allowed if bridge is also specified.
             @result:
                A Validation Error is thrown that tells the user that
                ip6address is not allowed if bridge is also specified.
            @tms_test_precondition:
                NA
            @tms_execution_type: Automated
        """
        free_nics = \
            self.verify_backup_free_nics(self.ms_node, "/ms",
                                         backup_files=False)
        self.test_ms_if1 = free_nics[0]

        # CREATE TEST BRIDGE
        br_url = "/ms/network_interfaces/br2064"
        props = "device_name='br2064' ipaddress='10.10.10.2' " \
            "forwarding_delay='0' stp='false' network_name='test'"
        self.execute_cli_create_cmd(self.ms_node, br_url, "bridge", props)
        # CREATE TEST INTERFACE
        if_url = "/ms/network_interfaces/if2064"
        props = "macaddress='{0}' device_name='{1}' bridge='br2064' "\
                "ipv6address='0:0:0:0:0:ffff:a0a:a01'".\
            format(self.test_ms_if1["MAC"], self.test_ms_if1["NAME"])
        _, stderr, _ = self.execute_cli_create_cmd(
            self.ms_node, if_url, "eth", props, expect_positive=False)

        self.assertTrue(self.is_text_in_list("ValidationError", stderr))
        self.assertTrue(self.is_text_in_list('not allowed if "bridge"',
                                             stderr))
