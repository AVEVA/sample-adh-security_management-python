import configparser
import jsonpatch
import traceback

from ocs_sample_library_preview import (OCSClient, Role, RoleScope, Trustee, TrusteeType, User, UserInvitation, AccessControlList,
                                        AccessControlEntry, AccessType, CommonAccessRightsEnum, SdsType, SdsTypeProperty, SdsTypeCode, SdsStream)


def suppress_error(sds_call):
    """Suppress an error thrown by SDS"""
    try:
        sds_call()
    except Exception as error:
        print(f'Encountered Error: {error}')


def get_tenant_member_role_id(client: OCSClient):
    """Helper function that retrieves the first role with the Tenant Member role type Id"""
    roles = client.Roles.getRoles()
    for role in roles:
        if role.RoleTypeId == client.Roles.TenantMemberRoleTypeId:
            return role.Id


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


def main():
    """This function is the main body of the security sample script"""
    exception = None
    try:
        print('Sample starting...')

        # Read config and create a client
        config = configparser.ConfigParser()
        config.read('config.ini')

        tenant_id = config.get('Access', 'TenantId')
        namespace_id = config.get('Configurations', 'NamespaceId')

        client = OCSClient(config.get('Access', 'ApiVersion'),
                           config.get('Access', 'TenantId'),
                           config.get('Access', 'Resource'),
                           config.get('Credentials', 'ClientId'),
                           config.get('Credentials', 'ClientSecret'))

        # Step 1
        print('Creating a role')
        custom_role = Role(name='custom role - security management sample',
                           role_scope=RoleScope.Tenant, tenant_id=tenant_id)
        custom_role = client.Roles.createRole(custom_role)

        # Step 2
        print('Creating a user and invite them')
        user = User(contact_given_name='Big', contact_surname='Tex', contact_email='collin.bardini@aveva.com',
                    identity_provider_id=client.Users.MicrosoftIdentityProviderId, role_ids=[custom_role.Id])

        user.RoleIds.append(get_tenant_member_role_id(client))
        user = client.Users.createUser(user)
        invitation = UserInvitation(send_invitation=True)
        client.Users.createOrUpdateInvitation(user.Id, invitation)

        # Step 3
        print('Creating a type')
        date_time_type = SdsType('DateTimeType', SdsTypeCode.DateTime)
        int_type = SdsType('IntType', SdsTypeCode.Int32)
        date_time_property = SdsTypeProperty('DateTime', True, date_time_type)
        int_property = SdsTypeProperty('Value', False, int_type)
        example_type = SdsType('example_type-security_management_sample', SdsTypeCode.Object, [
            date_time_property, int_property], 'This is a type example.')
        example_type = client.Types.getOrCreateType(namespace_id, example_type)

        # Step 4
        print('Creating a stream')
        example_stream = SdsStream(
            'example_stream-security_management_sample', example_type.Id)
        example_stream = client.Streams.getOrCreateStream(
            namespace_id, example_stream)

        # Step 5
        print(
            'Adding custom role to example type and stream access control lists using PUT')
        trustee = Trustee(TrusteeType.Role, tenant_id, custom_role.Id)
        entry = AccessControlEntry(trustee, AccessType.Allowed,
                                   CommonAccessRightsEnum.Read | CommonAccessRightsEnum.Write)

        type_acl = client.Types.getAccessControl(
            namespace_id, example_type.Id)
        type_acl.RoleTrusteeAccessControlEntries.append(entry)
        client.Types.updateAccessControl(
            namespace_id, example_type.Id, type_acl)

        stream_acl = client.Streams.getAccessControl(
            namespace_id, example_stream.Id)
        stream_acl.RoleTrusteeAccessControlEntries.append(entry)
        client.Streams.updateAccessControl(
            namespace_id, example_stream.Id, stream_acl)

        # Step 6
        print('Adding a role from the example stream access control list using PATCH')
        patch = jsonpatch.JsonPatch(
            [{
                'op': 'add', 'path': '/RoleTrusteeAccessControlEntries/-',
                'value': {
                    'AccessRights': 0,
                    'AccessType': 'Allowed',
                    'Trustee': {'ObjectId': get_tenant_member_role_id(client), 'TenantId': tenant_id, 'Type': 'Role'}
                }
            }])
        client.Streams.patchAccessControl(
            namespace_id, example_stream.Id, patch)

        # Step 7
        print('Changing owner of example stream')
        stream_owner = client.Streams.getOwner(namespace_id, example_stream.Id)
        stream_owner.ObjectId = user.Id
        stream_owner.Type = TrusteeType.User
        client.Streams.updateOwner(
            namespace_id, example_stream.Id, stream_owner)

        # Step 8
        print('Retrieving the access rights of the example stream')
        access_rights = client.Streams.getAccessRights(
            namespace_id, example_stream.Id)
        for access_right in access_rights:
            print(access_right.name)
        
        # Step 9
        print('Verifying the results of the previous steps')
        trustee = Trustee(TrusteeType.Role, tenant_id, get_tenant_member_role_id(client))
        entry = AccessControlEntry(trustee, AccessType.Allowed, CommonAccessRightsEnum.none)
        stream_acl.RoleTrusteeAccessControlEntries.append(entry)
        assert compare_acls(client.Types.getAccessControl(namespace_id, example_type.Id), type_acl)
        assert compare_acls(client.Streams.getAccessControl(namespace_id, example_stream.Id), stream_acl)
        assert client.Streams.getOwner(namespace_id, example_stream.Id).ObjectId == stream_owner.ObjectId

    except Exception as error:
        print((f'Encountered Error: {error}'))
        print()
        traceback.print_exc()
        print()
        exception = error

    finally:
        # Step 10
        print('Cleaning Up')
        suppress_error(lambda: client.Streams.deleteStream(namespace_id, example_stream.Id))
        suppress_error(lambda: client.Types.deleteType(namespace_id, example_type.Id))
        suppress_error(lambda: client.Roles.deleteRole(custom_role.Id))
        suppress_error(lambda: client.Users.deleteUser(user.Id))

    print('Complete!')


if __name__ == '__main__':

    main()
