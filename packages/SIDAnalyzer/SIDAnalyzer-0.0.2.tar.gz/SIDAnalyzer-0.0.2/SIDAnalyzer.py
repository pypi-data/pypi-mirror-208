#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This script analyzes Microsoft SID
#    Copyright (C) 2023  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##################

"""
This script analyzes Microsoft SID
"""

__version__ = "0.0.2"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = "This script analyzes Microsoft SID."
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/SIDAnalyzer"

copyright = """
SIDAnalyzer  Copyright (C) 2023  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = []

print(copyright)

sids = {
    r"S-1-0-0(-[\d-]*\d)?": [
        "NULL",
        "No Security principal."
    ],
    r"S-1-1-0(-[\d-]*\d)?": [
        "EVERYONE",
        "A group that includes all users."
    ],
    r"S-1-2-0(-[\d-]*\d)?": [
        "LOCAL",
        "A group that includes all users who have logged on locally."
    ],
    r"S-1-2-1(-[\d-]*\d)?": [
        "CONSOLE_LOGON",
        "A group that includes users who are logged on to the physical console. This SID can be used to implement security policies that grant different rights based on whether a user has been granted physical access to the console."
    ],
    r"S-1-3-0(-[\d-]*\d)?": [
        "CREATOR_OWNER",
        "A placeholder in an inheritable access control entry (ACE). When the ACE is inherited, the system replaces this SID with the SID for the object's creator."
    ],
    r"S-1-3-1(-[\d-]*\d)?": [
        "CREATOR_GROUP",
        "A placeholder in an inheritable ACE. When the ACE is inherited, the system replaces this SID with the SID for the primary group of the object's creator."
    ],
    r"S-1-3-2(-[\d-]*\d)?": [
        "OWNER_SERVER",
        "A placeholder in an inheritable ACE. When the ACE is inherited, the system replaces this SID with the SID for the object's owner server."
    ],
    r"S-1-3-3(-[\d-]*\d)?": [
        "GROUP_SERVER",
        "A placeholder in an inheritable ACE. When the ACE is inherited, the system replaces this SID with the SID for the object's group server."
    ],
    r"S-1-3-4(-[\d-]*\d)?": [
        "OWNER_RIGHTS",
        "A group that represents the current owner of the object. When an ACE that carries this SID is applied to an object, the system ignores the implicit READ_CONTROL and WRITE_DAC permissions for the object owner."
    ],
    r"S-1-5(-[\d-]*\d)?": [
        "NT_AUTHORITY",
        "A SID containing only the SECURITY_NT_AUTHORITY identifier authority."
    ],
    r"S-1-5-1(-[\d-]*\d)?": [
        "DIALUP",
        "A group that includes all users who have logged on through a dial-up connection. "
    ],
    r"S-1-5-2(-[\d-]*\d)?": [
        "NETWORK",
        "A group that includes all users who have logged on through a network connection. "
    ],
    r"S-1-5-3(-[\d-]*\d)?": [
        "BATCH",
        "A group that includes all users who have logged on through a batch queue facility."
    ],
    r"S-1-5-4(-[\d-]*\d)?": [
        "INTERACTIVE",
        "A group that includes all users who have logged on interactively."
    ],
    r"S-1-5-5(-[\d-]*\d)(-[\d-]*\d)": [
        "LOGON_ID",
        "A logon session. The X and Y values for these SIDs are different for each logon session and are recycled when the operating system is restarted."
    ],
    r"S-1-5-6(-[\d-]*\d)?": [
        "SERVICE",
        "A group that includes all security principals that have logged on as a service."
    ],
    r"S-1-5-7(-[\d-]*\d)?": [
        "ANONYMOUS",
        "A group that represents an anonymous logon. "
    ],
    r"S-1-5-8(-[\d-]*\d)?": [
        "PROXY",
        "Identifies a SECURITY_NT_AUTHORITY Proxy."
    ],
    r"S-1-5-9(-[\d-]*\d)?": [
        "ENTERPRISE_DOMAIN_CONTROLLERS",
        "A group that includes all domain controllers in a forest that uses an Active Directory directory service."
    ],
    r"S-1-5-10(-[\d-]*\d)?": [
        "PRINCIPAL_SELF",
        "A placeholder in an inheritable ACE on an account object or group object in Active Directory. When the ACE is inherited, the system replaces this SID with the SID for the security principal that holds the account."
    ],
    r"S-1-5-11(-[\d-]*\d)?": [
        "AUTHENTICATED_USERS",
        "A group that includes all users whose identities were authenticated when they logged on. Users authenticated as Guest or Anonymous are not members of this group. "
    ],
    r"S-1-5-12(-[\d-]*\d)?": [
        "RESTRICTED_CODE",
        "This SID is used to control access by untrusted code. ACL validation against tokens with RC consists of two checks, one against the token's normal list of SIDs and one against a second list (typically containing RC - the &quot;RESTRICTED_CODE&quot; token - and a subset of the original token SIDs). Access is granted only if a token passes both tests. Any ACL that specifies RC must also specify WD - the &quot;EVERYONE&quot; token. When RC is paired with WD in an ACL, a superset of &quot;EVERYONE&quot;, including untrusted code, is described."
    ],
    r"S-1-5-13(-[\d-]*\d)?": [
        "TERMINAL_SERVER_USER",
        "A group that includes all users who have logged on to a Terminal Services server. "
    ],
    r"S-1-5-14(-[\d-]*\d)?": [
        "REMOTE_INTERACTIVE_LOGON",
        "A group that includes all users who have logged on through a terminal services logon. "
    ],
    r"S-1-5-15(-[\d-]*\d)?": [
        "THIS_ORGANIZATION",
        "A group that includes all users and computers from another organization. If this SID is present, THIS_ORGANIZATION SID MUST NOT be present."
    ],
    r"S-1-5-17(-[\d-]*\d)?": [
        "IUSR",
        "An account that is used by the default Internet Information Services (IIS) user."
    ],
    r"S-1-5-18(-[\d-]*\d)?": [
        "LOCAL_SYSTEM",
        "An account that is used by the operating system."
    ],
    r"S-1-5-19(-[\d-]*\d)?": [
        "LOCAL_SERVICE",
        "A local service account."
    ],
    r"S-1-5-20(-[\d-]*\d)?": [
        "NETWORK_SERVICE",
        "A network service account."
    ],
    r"S-1-5-21(-[\d-]*\d)-498": [
        "ENTERPRISE_READONLY_DOMAIN_CONTROLLERS",
        "A universal group containing all read-only domain controllers in a forest."
    ],
    "S-1-5-21-0-0-0-496": [
        "COMPOUNDED_AUTHENTICATION",
        "Device identity is included in the Kerberos service ticket. If a forest boundary was crossed, then claims transformation occurred."
    ],
    "S-1-5-21-0-0-0-497": [
        "CLAIMS_VALID",
        "Claims were queried for in the account's domain, and if a forest boundary was crossed, then claims transformation occurred."
    ],
    r"S-1-5-21(-[\d-]*\d)-500": [
        "ADMINISTRATOR",
        "A user account for the system administrator. By default, it is the only user account that is given full control over the system."
    ],
    r"S-1-5-21(-[\d-]*\d)-501": [
        "GUEST",
        "A user account for people who do not have individual accounts. This user account does not require a password. By default, the Guest account is disabled."
    ],
    r"S-1-5-21(-[\d-]*\d)-512": [
        "DOMAIN_ADMINS",
        "A global group whose members are authorized to administer the domain. By default, the DOMAIN_ADMINS group is a member of the Administrators group on all computers that have joined a domain, including the domain controllers. DOMAIN_ADMINS is the default owner of any object that is created by any member of the group."
    ],
    r"S-1-5-21(-[\d-]*\d)-513": [
        "DOMAIN_USERS",
        "A global group that includes all user accounts in a domain. "
    ],
    r"S-1-5-21(-[\d-]*\d)-514": [
        "DOMAIN_GUESTS",
        "A global group that has only one member, which is the built-in Guest account of the domain."
    ],
    r"S-1-5-21(-[\d-]*\d)-515": [
        "DOMAIN_COMPUTERS",
        "A global group that includes all clients and servers that have joined the domain."
    ],
    r"S-1-5-21(-[\d-]*\d)-516": [
        "DOMAIN_DOMAIN_CONTROLLERS",
        "A global group that includes all domain controllers in the domain. "
    ],
    r"S-1-5-21(-[\d-]*\d)-517": [
        "CERT_PUBLISHERS",
        "A global group that includes all computers that are running an enterprise certification authority. Cert Publishers are authorized to publish certificates for User objects in Active Directory."
    ],
    r"S-1-5-21(-[\d-]*\d)(-[\d-]*\d)-518": [
        "SCHEMA_ADMINISTRATORS",
        "A universal group in a native-mode domain, or a global group in a mixed-mode domain. The group is authorized to make schema changes in Active Directory. "
    ],
    r"S-1-5-21(-[\d-]*\d)(-[\d-]*\d)-519": [
        "ENTERPRISE_ADMINS",
        "A universal group in a native-mode domain, or a global group in a mixed-mode domain. The group is authorized to make forestwide changes in Active Directory, such as adding child domains."
    ],
    r"S-1-5-21(-[\d-]*\d)-520": [
        "GROUP_POLICY_CREATOR_OWNERS",
        "A global group that is authorized to create new Group Policy Objects in Active Directory. "
    ],
    r"S-1-5-21(-[\d-]*\d)-521": [
        "READONLY_DOMAIN_CONTROLLERS",
        "A global group that includes all read-only domain controllers."
    ],
    r"S-1-5-21(-[\d-]*\d)-522": [
        "CLONEABLE_CONTROLLERS",
        "A global group that includes all domain controllers in the domain that can be cloned."
    ],
    r"S-1-5-21(-[\d-]*\d)-525": [
        "PROTECTED_USERS",
        "A global group that is afforded additional protections against authentication security threats. For more information, see [MS-APDS] and [MS-KILE]."
    ],
    r"S-1-5-21(-[\d-]*\d)-526": [
        "KEY_ADMINS",
        "A security group for delegated write access on the msdsKeyCredentialLink attribute only. The group is intended for use in scenarios where trusted external authorities (for example, Active Directory Federated Services) are responsible for modifying this attribute. Only trusted administrators should be made a member of this group."
    ],
    r"S-1-5-21(-[\d-]*\d)-527": [
        "ENTERPRISE_KEY_ADMINS",
        "A security group for delegated write access on the msdsKeyCredentialLink attribute only. The group is intended for use in scenarios where trusted external authorities (for example, Active Directory Federated Services) are responsible for modifying this attribute. Only trusted enterprise administrators should be made a member of this group."
    ],
    r"S-1-5-21(-[\d-]*\d)-553": [
        "RAS_SERVERS",
        "A domain local group for Remote Access Services (RAS) servers. By default, this group has no members. Servers in this group have Read Account Restrictions and Read Logon Information access to User objects in the Active Directory domain local group. "
    ],
    r"S-1-5-21(-[\d-]*\d)-571": [
        "ALLOWED_RODC_PASSWORD_REPLICATION_GROUP",
        "Members in this group can have their passwords replicated to all read-only domain controllers in the domain."
    ],
    r"S-1-5-21(-[\d-]*\d)-572": [
        "DENIED_RODC_PASSWORD_REPLICATION_GROUP",
        "Members in this group cannot have their passwords replicated to all read-only domain controllers in the domain."
    ],
    "S-1-5-32-544": [
        "BUILTIN_ADMINISTRATORS",
        "A built-in group. After the initial installation of the operating system, the only member of the group is the Administrator account. When a computer joins a domain, the Domain Administrators group is added to the Administrators group. When a server becomes a domain controller, the Enterprise Administrators group also is added to the Administrators group."
    ],
    "S-1-5-32-545": [
        "BUILTIN_USERS",
        "A built-in group. After the initial installation of the operating system, the only member is the Authenticated Users group. When a computer joins a domain, the Domain Users group is added to the Users group on the computer."
    ],
    "S-1-5-32-546": [
        "BUILTIN_GUESTS",
        "A built-in group. The Guests group allows users to log on with limited privileges to a computer's built-in Guest account."
    ],
    "S-1-5-32-547": [
        "POWER_USERS",
        "A built-in group. Power users can perform the following actions:"
    ],
    "S-1-5-32-548": [
        "ACCOUNT_OPERATORS",
        "A built-in group that exists only on domain controllers. Account Operators have permission to create, modify, and delete accounts for users, groups, and computers in all containers and organizational units of Active Directory except the Built-in container and the Domain Controllers OU. Account Operators do not have permission to modify the Administrators and Domain Administrators groups, nor do they have permission to modify the accounts for members of those groups."
    ],
    "S-1-5-32-549": [
        "SERVER_OPERATORS",
        "A built-in group that exists only on domain controllers. Server Operators can perform the following actions:"
    ],
    "S-1-5-32-550": [
        "PRINTER_OPERATORS",
        "A built-in group that exists only on domain controllers. Print Operators can manage printers and document queues."
    ],
    "S-1-5-32-551": [
        "BACKUP_OPERATORS",
        "A built-in group. Backup Operators can back up and restore all files on a computer, regardless of the permissions that protect those files."
    ],
    "S-1-5-32-552": [
        "REPLICATOR",
        "A built-in group that is used by the File Replication Service (FRS) on domain controllers."
    ],
    "S-1-5-32-554": [
        "ALIAS_PREW2KCOMPACC",
        "A backward compatibility group that allows read access on all users and groups in the domain."
    ],
    "S-1-5-32-555": [
        "REMOTE_DESKTOP",
        "An alias. Members of this group are granted the right to log on remotely."
    ],
    "S-1-5-32-556": [
        "NETWORK_CONFIGURATION_OPS",
        "An alias. Members of this group can have some administrative privileges to manage configuration of networking features."
    ],
    "S-1-5-32-557": [
        "INCOMING_FOREST_TRUST_BUILDERS",
        "An alias. Members of this group can create incoming, one-way trusts to this forest."
    ],
    "S-1-5-32-558": [
        "PERFMON_USERS",
        "An alias. Members of this group have remote access to monitor this computer."
    ],
    "S-1-5-32-559": [
        "PERFLOG_USERS",
        "An alias. Members of this group have remote access to schedule the logging of performance counters on this computer."
    ],
    "S-1-5-32-560": [
        "WINDOWS_AUTHORIZATION_ACCESS_GROUP",
        "An alias. Members of this group have access to the computed tokenGroupsGlobalAndUniversal attribute on User objects."
    ],
    "S-1-5-32-561": [
        "TERMINAL_SERVER_LICENSE_SERVERS",
        "An alias. A group for Terminal Server License Servers."
    ],
    "S-1-5-32-562": [
        "DISTRIBUTED_COM_USERS",
        "An alias. A group for COM to provide computer-wide access controls that govern access to all call, activation, or launch requests on the computer."
    ],
    "S-1-5-32-568": [
        "IIS_IUSRS",
        "A built-in group account for IIS users."
    ],
    "S-1-5-32-569": [
        "CRYPTOGRAPHIC_OPERATORS",
        "A built-in group account for cryptographic operators."
    ],
    "S-1-5-32-573": [
        "EVENT_LOG_READERS",
        "A built-in local group.  Members of this group can read event logs from the local machine."
    ],
    "S-1-5-32-574": [
        "CERTIFICATE_SERVICE_DCOM_ACCESS",
        "A built-in local group. Members of this group are allowed to connect to Certification Authorities in the enterprise."
    ],
    "S-1-5-32-575": [
        "RDS_REMOTE_ACCESS_SERVERS",
        "Servers in this group enable users of RemoteApp programs and personal virtual desktops access to these resources. This group needs to be populated on servers running RD Connection Broker. RD Gateway servers and RD Web Access servers used in the deployment need to be in this group."
    ],
    "S-1-5-32-576": [
        "RDS_ENDPOINT_SERVERS",
        "A group that enables member servers to run virtual machines and host sessions."
    ],
    "S-1-5-32-577": [
        "RDS_MANAGEMENT_SERVERS",
        "A group that allows members to access WMI resources over management protocols (such as WS-Management via the Windows Remote Management service)."
    ],
    "S-1-5-32-578": [
        "HYPER_V_ADMINS",
        "A group that gives members access to all administrative features of Hyper-V."
    ],
    "S-1-5-32-579": [
        "ACCESS_CONTROL_ASSISTANCE_OPS",
        "A local group that allows members to remotely query authorization attributes and permissions for resources on the local computer."
    ],
    "S-1-5-32-580": [
        "REMOTE_MANAGEMENT_USERS",
        "Members of this group can access Windows Management Instrumentation (WMI) resources over management protocols (such as WS-Management [DMTF-DSP0226]). This applies only to WMI namespaces that grant access to the user."
    ],
    "S-1-5-33": [
        "WRITE_RESTRICTED_CODE",
        "A SID that allows objects to have an ACL that lets any service process with a write-restricted token to write to the object."
    ],
    "S-1-5-64-10": [
        "NTLM_AUTHENTICATION",
        "A SID that is used when the NTLM authentication package authenticated the client."
    ],
    "S-1-5-64-14": [
        "SCHANNEL_AUTHENTICATION",
        "A SID that is used when the SChannel authentication package authenticated the client. "
    ],
    "S-1-5-64-21": [
        "DIGEST_AUTHENTICATION",
        "A SID that is used when the Digest authentication package authenticated the client."
    ],
    "S-1-5-65-1": [
        "THIS_ORGANIZATION_CERTIFICATE",
        "A SID that indicates that the client's Kerberos service ticket's PAC contained a NTLM_SUPPLEMENTAL_CREDENTIAL structure (as specified in [MS-PAC] section 2.6.4). If the OTHER_ORGANIZATION SID is present, then this SID MUST NOT be present"
    ],
    "S-1-5-80": [
        "NT_SERVICE",
        "An NT Service account prefix."
    ],
    "S-1-5-84-0-0-0-0-0": [
        "USER_MODE_DRIVERS",
        "Identifies a user-mode driver process."
    ],
    "S-1-5-113": [
        "LOCAL_ACCOUNT",
        "A group that includes all users who are local accounts."
    ],
    "S-1-5-114": [
        "LOCAL_ACCOUNT_AND_MEMBER_OF_ADMINISTRATORS_GROUP",
        "A group that includes all users who are local accounts and members of the administrators group."
    ],
    "S-1-5-1000": [
        "OTHER_ORGANIZATION",
        "A group that includes all users and computers from another organization. If this SID is present, THIS_ORGANIZATION SID MUST NOT be present."
    ],
    "S-1-15-2-1": [
        "ALL_APP_PACKAGES",
        "All applications running in an app package context."
    ],
    "S-1-16-0": [
        "ML_UNTRUSTED",
        "An untrusted integrity level."
    ],
    "S-1-16-4096": [
        "ML_LOW",
        "A low integrity level."
    ],
    "S-1-16-8192": [
        "ML_MEDIUM",
        "A medium integrity level."
    ],
    "S-1-16-8448": [
        "ML_MEDIUM_PLUS",
        "A medium-plus integrity level."
    ],
    "S-1-16-12288": [
        "ML_HIGH",
        "A high integrity level."
    ],
    "S-1-16-16384": [
        "ML_SYSTEM",
        "A system integrity level."
    ],
    "S-1-16-20480": [
        "ML_PROTECTED_PROCESS",
        "A protected-process integrity level."
    ],
    "S-1-16-28672": [
        "ML_SECURE_PROCESS",
        "A secure process integrity level."
    ],
    "S-1-18-1": [
        "AUTHENTICATION_AUTHORITY_ASSERTED_IDENTITY",
        "A SID that means the client's identity is asserted by an authentication authority based on proof of possession of client credentials."
    ],
    "S-1-18-2": [
        "SERVICE_ASSERTED_IDENTITY",
        "A SID that means the client's identity is asserted by a service."
    ],
    "S-1-18-3": [
        "FRESH_PUBLIC_KEY_IDENTITY",
        "A SID that means the client's identity is asserted by an authentication authority based on proof of current possession of client public key credentials."
    ],
    "S-1-18-4": [
        "KEY_TRUST_IDENTITY",
        "A SID that means the client's identity is based on proof of possession of public key credentials using the key trust object."
    ],
    "S-1-18-5": [
        "KEY_PROPERTY_MFA",
        "A SID that means the key trust object had the multifactor authentication (MFA) property."
    ],
    "S-1-18-6": [
        "KEY_PROPERTY_ATTESTATION",
        "A SID that means the key trust object had the attestation property."
    ]
}

from sys import argv, stdin
from re import fullmatch

sids_ = argv[1:]

if not sids_:
    sids_ = stdin.read().split()

for sid_ in sids_:
    for sid in sids:
        # print(sid, sid_)
        if fullmatch(sid, sid_):
            print("\x1b[38;2;183;121;227m", "\r" + sid_, "\x1b[38;2;255;240;175m\b", sids[sid][0], "\x1b[38;2;255;208;11m\b", sids[sid][1], "\x1b[39m")
