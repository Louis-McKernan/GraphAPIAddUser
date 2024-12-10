#runUserQuery.py
import requests

# Replace with your access token
ACCESS_TOKEN = "your-access-token"

def get_group_id_by_name(group_name):
    """
    Get the group ID from the group name using Microsoft Graph API.
    """
    url = f"https://graph.microsoft.com/v1.0/groups?$filter=displayName eq '{group_name}'"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['value']:
            return data['value'][0]['id']
        else:
            print(f"Group not found: {group_name}")
            return None
    else:
        print(f"Failed to fetch group ID for {group_name}: {response.status_code} - {response.text}")
        return None

def get_user_details(email):
    """
    Get the user's details (ID, Display Name, Job Title) from the email address using Microsoft Graph API.
    """
    url = f"https://graph.microsoft.com/v1.0/users?$filter=mail eq '{email}'"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['value']:
            user = data['value'][0]
            return {
                "id": user["id"],
                "name": user.get("displayName", "N/A"),
                "email": user.get("mail", "N/A"),
                "job_title": user.get("jobTitle", "N/A")
            }
        else:
            print(f"Email not found: {email}")
            return None
    else:
        print(f"Failed to fetch user details for {email}: {response.status_code} - {response.text}")
        return None

def check_user_in_group(user_id, group_id):
    """
    Check if a user is in the group using Microsoft Graph API.
    """
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/{user_id}/$ref"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 204:  # No Content means the user is in the group
        return True
    elif response.status_code == 404:  # Not Found means the user is not in the group
        return False
    else:
        print(f"Error checking group membership for user ID {user_id}: {response.status_code} - {response.text}")
        return None

def add_user_to_group(user_id, group_id):
    """
    Add a user to the group using Microsoft Graph API.
    """
    url = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
    }
    response = requests.post(url, headers=headers, json=body)
    
    if response.status_code == 204:
        print(f"User ID {user_id} successfully added to the group.")
    else:
        print(f"Failed to add User ID {user_id} to the group: {response.status_code} - {response.text}")

def process_emails(emails, group_name):
    """
    Process the list of email addresses to determine if they are in the group and add missing users to the group.
    """
    group_id = get_group_id_by_name(group_name)
    if not group_id:
        print(f"Group '{group_name}' not found. Exiting.")
        return [], []

    users_in_group = []
    users_not_in_group = []
    
    for email in emails:
        print(f"Processing email: {email}")
        user_details = get_user_details(email)
        if user_details:
            is_in_group = check_user_in_group(user_details["id"], group_id)
            user_info = {
                "Name": user_details["name"],
                "Email": user_details["email"],
                "Job Description": user_details["job_title"]
            }
            if is_in_group is True:
                users_in_group.append(user_info)
            elif is_in_group is False:
                users_not_in_group.append(user_info)
                add_user_to_group(user_details["id"], group_id)  # Add the user to the group
    
    return users_in_group, users_not_in_group

if __name__ == "__main__":
    # Example input list of email addresses
    emails = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ]

    # Replace with your target group name
    group_name = "Your Group Name"
    
    users_in_group, users_not_in_group = process_emails(emails, group_name)
    
    print("\nUsers already in the group:")
    for user in users_in_group:
        print(user)
    
    print("\nUsers not in the group (added):")
    for user in users_not_in_group:
        print(user)
