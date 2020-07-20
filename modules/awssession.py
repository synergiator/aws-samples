from modules.constants import AWS_CONSTANTS
import boto3
import time

""" wrapper for AWS session context"""
class AWSSession:
  def __init__(self):
    self.clients = {}
    self.resources = {}

    self.default_region = "eu-central-1"

    self.alias = "n/a"

    self.session = None


  def __populate_session(self):
    self.resources['iam'] = self.get_resource('iam')
    self.clients['iam'] = self.get_client('iam')

    self.clients['sts'] = self.get_client('sts')

    self.clients['s3'] = self.get_client('s3')
    self.resources['s3'] = self.get_resource('s3')

    self.clients['cloudtrail'] = self.get_client('cloudtrail')


  def assume_role_profile(self, accountid, role, profile_name="default", session_lifetime=AWS_CONSTANTS.STS_MINIMUM_LIFETIME):
    """ Assume role: create new session using local profile/SAML sign-in"""
    client = boto3.client('sts')

    self.session = client.assume_role(
        RoleArn='arn:aws:sts::' + accountid + ':role/' + role,
        RoleSessionName="ROOT",
        DurationSeconds=session_lifetime)['Credentials']

    account_arn =  client.get_caller_identity()['Arn']
    # assert accountid in account_arn, "PROFILE SIGN-IN: %s does not match %s" % (accountid, account_arn)

    self.__populate_session()
 
    self.account_id = self.clients['sts'].get_caller_identity().get('Account')
    self.account_arn = self.clients['sts'].get_caller_identity().get('Arn')
    self.alias = self.get_client("iam").list_account_aliases()['AccountAliases'][0]

    print("current AWS identity (API or SAML sign-in): %s" % client.get_caller_identity()['Arn'])




  def assume_role_sts(self, accountid, role, session_name, session_lifetime=AWS_CONSTANTS.STS_MINIMUM_LIFETIME):
    """ Assume role: create new session via STS service"""
    if self.session == None:
      raise Exception("No STS session available. Sign-in using assume_role_profile()")
    else:
      client = self.get_client('sts')

    self.session = client.assume_role(
        RoleArn='arn:aws:sts::' + accountid + ':role/' + role,
        RoleSessionName=session_name,
        DurationSeconds=session_lifetime)['Credentials']

    account_arn =  client.get_caller_identity()['Arn']
    # assert accountid in account_arn, "STS: %s does not match %s" % (accountid, account_arn)

    self.__populate_session()

    self.account_id = self.clients['sts'].get_caller_identity().get('Account')
    self.account_arn = self.clients['sts'].get_caller_identity().get('Arn')
    self.alias = self.get_client("iam").list_account_aliases()['AccountAliases'][0]

    print("current AWS identity (STS): %s in %s" % (client.get_caller_identity()['Arn'], self.alias))



  def get_client(self, service):
      if service in ['cloudtrail']:
        region_name=self.default_region
        client = boto3.client(service, aws_access_key_id=self.session['AccessKeyId'],
                                    aws_secret_access_key=self.session['SecretAccessKey'],
                                    aws_session_token=self.session['SessionToken'],
                                    region_name=region_name)


      client = boto3.client(service, aws_access_key_id=self.session['AccessKeyId'],
                                    aws_secret_access_key=self.session['SecretAccessKey'],
                                    aws_session_token=self.session['SessionToken'])
      
      return client

  def get_resource(self, service):
    resource = boto3.resource(service, aws_access_key_id=self.session['AccessKeyId'],
                                  aws_secret_access_key=self.session['SecretAccessKey'],
                                  aws_session_token=self.session['SessionToken'])
    
    return resource

  def useSession(self, session):
    self.session = session

    self.__populate_session()



  ### BOILERPLATE HELPER METHODS TO ACCESS AWS ###


  def iam_policy_delete(self, handle):
        """Deletes a policy. Handle can be Arn einer policy's name"""
        arn = None
        if handle.startswith("arn:"):
            arn = handle
            print("going to delete policy with ARN in %s: %s" % (arn, self.alias))
            time.sleep(60)
            self.clients['iam'].delete_policy(PolicyArn=handle)

        else: # search by name and recur
            response = self.clients['iam'].list_policies(Scope='Local')
            for policy in response['Policies']:
                if policy['PolicyName'] == handle:
                    arn = policy['Arn']
                    self.iam_policy_delete(policy['Arn'])

        while(self.iam_policy_arn_exists(arn)):
            print("wait for AWS to delete IAM policy %s" % arn)
            time.sleep(2)


  def iam_policy_exists(self, policy_name):
      response = self.clients['iam'].list_policies(Scope='Local')
      for policy in response['Policies']:
          if policy['PolicyName'] == policy_name:
              return True
      return False




  def iam_role_exists(self,name):
      try:
          role = self.resources['iam'].Role(name)
          role.load()
          assert role.name == name
          return True
      except:
          return False


  def iam_policy_find_arn_by_name(self, name, scope="Local"):

      response = self.clients['iam'].list_policies(Scope=scope)
      for policy in response['Policies']:
          if policy['PolicyName'] == name:
              return policy['Arn']
  
      raise Exception("cant't find policy ARN by name: " + name)
      return None


  def iam_policy_arn_exists(self, policy_arn, scope="Local"):
      response = self.clients['iam'].list_policies(Scope=scope)
      for policy in response['Policies']:
          if policy['Arn'] == policy_arn:
              return True

      return False


  def iam_policy_attached_to_role(self, role, policy):

    response = self.clients['iam'].list_attached_role_policies(RoleName=role)
    for item in response['AttachedPolicies']:
      if item['PolicyName'] == policy:
        return True

    return False