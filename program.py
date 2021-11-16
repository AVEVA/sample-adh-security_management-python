import json
import jsonpatch
import traceback

from ocs_sample_library_preview import (OCSClient, Role, RoleScope, Trustee, TrusteeType, User, UserInvitation, AccessControlList,
                                        AccessControlEntry, AccessType, CommonAccessRightsEnum, SdsType, SdsTypeProperty, SdsTypeCode, SdsStream)

custom_role_name = 'custom role - security management sample'

def get_appsettings():
    """Open and parse the appsettings.json file"""

    # Try to open the configuration file
    try:
        with open(
            'appsettings.json',
            'r',
        ) as f:
            appsettings = json.load(f)
    except Exception as error:
        print(f'Error: {str(error)}')
        print(f'Could not open/read appsettings.json')
        exit()

    return appsettings


def get_tenant_member_role_id(client: OCSClient):
    """Helper function that retrieves the first role with the Tenant Member role type Id"""
    roles = client.Roles.getRoles()
    for role in roles:
        if role.RoleTypeId == client.Roles.TenantMemberRoleTypeId:
            return role.Id


def main(test = False):
    """This function is the main body of the security sample script"""
    global custom_role_name

    try:
        print('Sample starting...')

        # Read appsettings and create a client
        appsettings = get_appsettings()

        tenant_id = appsettings.get('TenantId')
        namespace_id = appsettings.get('NamespaceId')
        contact_given_name = appsettings.get('ContactGivenName')
        contact_surname = appsettings.get('ContactSurname')
        contact_email = appsettings.get('ContactEmail')

        client = OCSClient(appsettings.get('ApiVersion'),
                           appsettings.get('TenantId'),
                           appsettings.get('Resource'),
                           appsettings.get('ClientId'),
                           appsettings.get('ClientSecret'))

        # Step 1
        print('Creating a role')
        custom_role = Role(name=custom_role_name,
                           role_scope=RoleScope.Tenant, tenant_id=tenant_id)
        custom_role = client.Roles.createRole(custom_role)

        # Step 2
        print('Creating a user and invite them')
        user = User(contact_given_name=contact_given_name, contact_surname=contact_surname, contact_email=contact_email,
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
        print('Adding custom role to example type, example stream, and streams collection access control lists using PUT')
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
        
        # The access control list (ACL) of the Streams collection is modified in this step
        # The collection ACL is used as a default for all new items in a collection, so any new stream created will have this ACL
        # In addition, it governs who has access to a collection and who can make new collection items (such as new streams)
        streams_acl = client.Streams.get  DefaultAccessControl(namespace_id)
        streams_acl.RoleTrusteeAccessControlEntries.append(entry)
        client.Streams.updateDefaultAccessControl(namespace_id, streams_acl)

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

    except Exception as error:
        print((f'Encountered Error: {error}'))
        print()
        traceback.print_exc()
        print()
        if test:
            raise error
    
    finally:
        if test:
            return user, stream_owner, custom_role, stream_acl, streams_acl, type_acl
    
    print('Complete!')


if __name__ == '__main__':

    main()
