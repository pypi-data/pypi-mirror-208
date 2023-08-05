"""
PDS Validate Wrapper

Tool that downloads PDS Validate Tool and executes based upon
input arguments.
"""
import github3


def get_latest_release(token, org, repo, github_object=None):
    if not github_object:
        github_object = github3.login(token=token)

    repo = github_object.repository(org, repo)
    return repo.latest_release()


def convert_pds4_version_to_alpha(pds4_version):
    pds4_version_short = ''
    version_list = pds4_version.split('.')
    for num in version_list:
        if int(num) >= 10:
            pds4_version_short += chr(ord('@') + (int(num) - 9))
        else:
            pds4_version_short += num

    return pds4_version_short