"""This script tests the ADH Security Python sample script"""

import unittest
from program import main, get_appsettings, get_tenant_member_role_id
from ocs_sample_library_preview import (ADHClient, Trustee, TrusteeType, AccessControlList,
                                        AccessControlEntry, AccessType, CommonAccessRightsEnum, )


class ADHSecuritySampleTests(unittest.TestCase):
    """Tests for the ADH Security Python sample"""

    @classmethod
    def test_main(cls):
        """Tests the ADH Security Python main sample script"""
        success = True
        try:
            user, stream_owner, custom_role, stream_acl, streams_acl, type_acl = main(True)

            # Read appsettings and create a client
            appsettings = get_appsettings()

            tenant_id = appsettings.get('TenantId')
            namespace_id = appsettings.get('NamespaceId')

            client = ADHClient(appsettings.get('ApiVersion'),
                           appsettings.get('TenantId'),
                           appsettings.get('Resource'),
                           appsettings.get('ClientId'),
                           appsettings.get('ClientSecret'))

            # Step 9 - Verify the results of the previous steps
            print('Verifying the results of the previous steps')
            trustee = Trustee(TrusteeType.Role, tenant_id, get_tenant_member_role_id(client))
            entry = AccessControlEntry(trustee, AccessType.Allowed, CommonAccessRightsEnum.none)
            stream_acl.RoleTrusteeAccessControlEntries.append(entry)
            assert compare_acls(client.Types.getAccessControl(namespace_id, 'example_type-security_management_sample'), type_acl)
            assert compare_acls(client.Streams.getAccessControl(namespace_id, 'example_stream-security_management_sample'), stream_acl)
            assert compare_acls(client.Streams.getDefaultAccessControl(namespace_id), streams_acl)
            assert client.Streams.getOwner(namespace_id, 'example_stream-security_management_sample').ObjectId == stream_owner.ObjectId

        except Exception as error:
            print((f'Encountered Error: {error}'))
            print()
            success =  False

        finally:
            # Step 10 - Clean up
            print('Cleaning Up')
            suppress_error(lambda: client.Streams.deleteStream(namespace_id, 'example_stream-security_management_sample'))
            suppress_error(lambda: client.Types.deleteType(namespace_id, 'example_type-security_management_sample'))
            suppress_error(lambda: client.Roles.deleteRole(custom_role.Id))
            suppress_error(lambda: client.Users.deleteUser(user.Id))
            cleaned_streams_acl = []
            for acl in streams_acl.RoleTrusteeAccessControlEntries:
                if acl.Trustee.ObjectId != custom_role.Id:
                    cleaned_streams_acl.append(acl)
            streams_acl.RoleTrusteeAccessControlEntries = cleaned_streams_acl
            suppress_error(lambda: client.Streams.updateDefaultAccessControl(namespace_id, streams_acl))

        assert success

def suppress_error(sds_call):
    """Suppress an error thrown by SDS"""
    try:
        sds_call()
    except Exception as error:
        print(f'Encountered Error: {error}')

def compare_acls(acl1: AccessControlList, acl2: AccessControlList):
    """Helper function for comparing two access control lists"""
    if not (len(acl1.RoleTrusteeAccessControlEntries) == len(acl2.RoleTrusteeAccessControlEntries)):
        return False

    for ace1 in acl1.RoleTrusteeAccessControlEntries:
        ace_match = False
        for ace2 in acl2.RoleTrusteeAccessControlEntries:
            if ace1.AccessType == ace2.AccessType and \
                    ace1.Trustee.ObjectId == ace2.Trustee.ObjectId and \
                    ace1.Trustee.TenantId == ace2.Trustee.TenantId and \
                    ace1.Trustee.Type == ace2.Trustee.Type and \
                    ace1.AccessRights == ace2.AccessRights:
                ace_match = True
                break
        if not ace_match:
            return False

    return True

if __name__ == '__main__':
    unittest.main()
