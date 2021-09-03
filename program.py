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


def main(test=False):
    """This function is the main body of the security sample script"""
    exception = None
    try:
        print('Sample starting...')

        # Read config and create a client
        config = configparser.ConfigParser()
        config.read('config.ini')

        tenant_id = config.get('SourceConfiguration', 'TenantId')
        namespace_id = config.get('SourceConfiguration', 'NamespaceId')

        client = OCSClient(config.get('SourceConfiguration', 'ApiVersion'),
                        config.get(
            'SourceConfiguration', 'TenantId'),
            config.get(
            'SourceConfiguration', 'Resource'),
            config.get(
            'SourceConfiguration', 'ClientId'),
            config.get('SourceConfiguration', 'ClientSecret'))

        # Get the tenant memeber role for later use
        roles = client.Roles.getRoles()
        for role in roles:
            if role.RoleTypeId == client.Roles.TenantMemberRoleTypeId:
                tenant_member_role = role

        # Step 1
        print('Creating a role')
        custom_role = Role(name='custom role', role_scope=RoleScope.Tenant, tenant_id=config.get(
            'SourceConfiguration', 'TenantId'))
        custom_role = client.Roles.createRole(custom_role)

        # Step 2
        print('Creating a user and invite them')
        user = User(contact_given_name='Big', contact_surname='Tex', contact_email='collin.bardini@aveva.com',
                    identity_provider_id=client.Users.MicrosoftIdentityProviderId, role_ids=[custom_role.Id])
        
        user.RoleIds.append(tenant_member_role.Id)
        user = client.Users.createUser(user)
        invitation = UserInvitation(send_invitation=True)
        client.Users.createOrUpdateInvitation(user.Id, invitation)

        # Step 3
        print('Creating a type')
        date_time_type = SdsType('DateTimeType', SdsTypeCode.DateTime)
        int_type = SdsType('IntType', SdsTypeCode.Int32)
        date_time_property = SdsTypeProperty('DateTime', True, date_time_type)
        int_property = SdsTypeProperty('Value', False, int_type)
        example_type = SdsType('example_type', SdsTypeCode.Object, [
                            date_time_property, int_property], 'This is a type example.')
        example_type = client.Types.getOrCreateType(namespace_id, example_type)

        # Step 4
        print('Creating a stream')
        example_stream = SdsStream('example_stream', example_type.Id)
        example_stream = client.Streams.getOrCreateStream(
            namespace_id, example_stream)

        # Step 5
        print('Adding custom role to example stream access control list using PUT')
        stream_acl = client.Streams.getAccessControl(
            namespace_id, example_stream.Id)
        trustee = Trustee(TrusteeType.Role, tenant_id, custom_role.Id)
        entry = AccessControlEntry(trustee, AccessType.Allowed,
                                CommonAccessRightsEnum.Read | CommonAccessRightsEnum.Write)
        stream_acl.RoleTrusteeAccessControlEntries.append(entry)
        client.Streams.updateAccessControl(
            namespace_id, example_stream.Id, stream_acl)

        # Step 6
        print('Adding a role from the example stream access control list using PATCH')
        patch = jsonpatch.JsonPatch(
        [{
            'op': 'add', 'path': '/RoleTrusteeAccessControlEntries/-',
            'value': {
                'AccessRights': 1, 'AccessType': 0,
                'Trustee': {'ObjectId': tenant_member_role.Id, 'TenantId': tenant_id, 'Type': 'Role'}
            }
        }])
        client.Streams.patchAccessControl(
            namespace_id, example_stream.Id, patch)

        # Step 7
        print('Changing owner of example stream')
        stream_owner = client.Streams.getOwner(namespace_id, example_stream.Id)
        stream_owner.ObjectId = user.Id
        stream_owner.Type = TrusteeType.User
        client.Streams.updateOwner(namespace_id, example_stream.Id, stream_owner)

        # Step 8
        print('Retrieving the access rights of the example stream')
        access_rights = client.Streams.getAccessRights(namespace_id, example_stream.Id)
        for access_right in access_rights:
            print(access_right.name)

    except Exception as error:
        print((f'Encountered Error: {error}'))
        print()
        traceback.print_exc()
        print()
        exception = error

    finally:
        # Step 9
        print('Cleaning Up')
        suppress_error(lambda: client.Streams.deleteStream(namespace_id, example_stream.Id))
        suppress_error(lambda: client.Types.deleteType(namespace_id, example_type.Id))
        suppress_error(lambda: client.Roles.deleteRole(custom_role.Id))
        suppress_error(lambda: client.Users.deleteUser(user.Id))

    print('Complete!')


if __name__ == '__main__':

    main()
