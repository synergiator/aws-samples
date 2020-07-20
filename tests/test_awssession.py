import pytest

# IDs of customer accounts
accounts = [("")]

from modules.awssession import AWSSession
from modules.constants import AWS_CONSTANTS


""" Goal: find an AWS configuration so that both tests succeed."""
""" That is, is it possible to assume a role in a way that caller identity ARN"""
""" matches it?"""
""" Note: in this setup, super admin and customer admin can't be same persona """

class TestAWSSession:

    """ Assume allowed role - works """
    @pytest.mark.parametrize("account_id", accounts)
    def test_assume_role_normal(self, account_id):
      session = AWSSession()
      
      """ If the profile uses normal account credentials, """
      """ you get the 'transitive' session scenario. """
      session.assume_role_profile(accountid=AWS_CONSTANTS.SUPER_ACCOUNT, 
                                  role=AWS_CONSTANTS.ROLE_SUPER_ADMIN,
                                  profile_name="default")

      alias = session.clients["iam"].list_account_aliases()['AccountAliases'][0]
      caller_arn = session.clients['sts'].get_caller_identity()['Arn']
      print("%s -> %s" % (alias, caller_arn))
      assert AWS_CONSTANTS.SUPER_ACCOUNT in caller_arn

      session_name="my-assumed-session"
      session.assume_role_sts(account_id, AWS_CONSTANTS.ROLE_SUPER_ADMIN, session_name)
      alias = session.clients["iam"].list_account_aliases()['AccountAliases'][0]
      caller_arn = session.clients['sts'].get_caller_identity()['Arn']
      print("%s -> %s" % (alias, caller_arn))


    """Assume role _becoming_ the role - fails"""
    @pytest.mark.parametrize("account_id", accounts)
    def test_really_assume_role_experiment(self, account_id):
      session = AWSSession()
      
      """ If the profile uses normal account credentials, """
      """ you get the 'transitive' session scenario. """
      session.assume_role_profile(accountid=AWS_CONSTANTS.SUPER_ACCOUNT, 
                                  role=AWS_CONSTANTS.ROLE_SUPER_ADMIN,
                                  profile_name="default")

      alias = session.clients["iam"].list_account_aliases()['AccountAliases'][0]
      caller_arn = session.clients['sts'].get_caller_identity()['Arn']
      print("%s -> %s" % (alias, caller_arn))
      assert AWS_CONSTANTS.SUPER_ACCOUNT in caller_arn

      """ ERROR"""
      """ An error occurred (AccessDenied) 
          when calling the AssumeRole operation: 
          User: arn:aws:sts::SUPER_ACCOUNT:assumed-role/SUPER_ADMIN_ROLE/ROOT 
          is not authorized to perform: sts:AssumeRole on resource: 
          arn:aws:sts::CUSTOMER_ACCOUNT:role/CUSTOMER_ADMIN
      """
      session_name="my-really-assumed-session"
      session.assume_role_sts(account_id, AWS_CONSTANTS.ROLE_ACCOUNT_ADMIN, session_name)
      alias = session.clients["iam"].list_account_aliases()['AccountAliases'][0]
      caller_arn = session.clients['sts'].get_caller_identity()['Arn']
      print("%s -> %s" % (alias, caller_arn))
      assert account_id in caller_arn # we can now simulate customer activities in this session

