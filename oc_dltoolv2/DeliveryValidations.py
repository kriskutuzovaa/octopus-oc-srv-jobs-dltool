import re

"""
Is used only via wizard
"""

_artifactid_error_template = ("Incorrect artifactid %s for branch %s\n"
                              "Artifactid format:\n"
                              "1) I{IDT} for any project with IDT\n"
                              "2) {project name} for prj-... branches\n"
                              "3) {client name}... for all other deliveries")
_version_error_template = ("Version should have format v(YYYYmmdd)_(optional minor number)\n"
                           "Given: %s")


def validate_artifactid(artifactid, client_name, branch_rel_to_client):
    msg = _artifactid_error_template % (artifactid, branch_rel_to_client)

    validate_artifactid_symbols(artifactid)

    if any([_is_idt_based_delivery(artifactid),
            _is_custom_client_delivery(artifactid, client_name),
            _is_specific_project_delivery(artifactid, branch_rel_to_client),
            _is_jira_issue_delivery(artifactid)]):
        return True

    raise ValidationException(msg)


def validate_artifactid_symbols(artifactid):
    structure = r"^[a-zA-Z0-9\._\-]+$"
    if not re.match(structure, artifactid):
        raise ValidationException("Artifactid must be made of alphanumerics, '-', '.' and '_'")


def _is_idt_based_delivery(artifactid):
    # delivery from CRM issue
    idt_regexp = re.compile("^I\d+$")
    return bool(idt_regexp.match(artifactid))


def _is_custom_client_delivery(artifactid, client_name):
    # custom delivery for client
    if artifactid.startswith(client_name + "-"):
        project_name = artifactid.replace(client_name + "-", "").strip()
        return len(project_name) > 0


def _is_specific_project_delivery(artifactid, source_branch):
    # for projects only: artifactid matches project name
    if _is_project_branch(source_branch):
        mentioned_project = _extract_project_name(source_branch)
        return mentioned_project == artifactid


def _is_jira_issue_delivery(artifactid):
    # project group in capital letters and number, dash-separated
    jira_regexp = re.compile("^[A-Z]+?-\d+$")
    return bool(jira_regexp.match(artifactid))


def validate_delivery_name(delivery_name, client_name, branch_rel_to_client):
    if "-v" not in delivery_name:
        raise ValidationException("Version not found in delivery name")

    artifactid, version_wo_v = delivery_name.rsplit("-v", 1)
    version = "v" + version_wo_v
    validate_artifactid(artifactid, client_name, branch_rel_to_client)
    validate_version(version)


def validate_version(version):
    pattern = "^v[\d_\-\.]+$"
    if not re.match(pattern, version):
        raise ValidationException(_version_error_template % version)
    return True


def validate_comments(comments):
    if not comments.strip():
        raise ValidationException("Please provide comments for delivery")


def validate_project_branch(branch):
    if not _is_project_branch(branch):
        raise ValidationException("Branch %s is not a project branch" % branch)


def _is_project_branch(branch_rel_to_client):
    return branch_rel_to_client.startswith("branches/prj-")


def _extract_project_name(branch_rel_to_client):
    branch_name = branch_rel_to_client.strip('/').split('/')[-1]
    mentioned_project = branch_name.replace("prj-", "")
    return mentioned_project


class ValidationException(Exception):
    pass
