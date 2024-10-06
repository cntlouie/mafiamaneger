function joinFaction() {
    const invitationCode = document.getElementById('invitation-code').value;

    fetch('/faction/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ invitation_code: invitationCode }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message);
            getFactionMembers();
        }
    })
    .catch(error => console.error('Error:', error));
}

function getFactionMembers() {
    fetch('/faction/members')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
        } else {
            updateFactionMembersDisplay(data.members);
        }
    })
    .catch(error => console.error('Error:', error));
}

function updateFactionMembersDisplay(members) {
    const membersList = document.getElementById('faction-members');
    membersList.innerHTML = '';
    members.forEach(member => {
        const li = document.createElement('li');
        li.textContent = member.username;
        membersList.appendChild(li);
    });
}

// Call getFactionMembers when the page loads
document.addEventListener('DOMContentLoaded', getFactionMembers);
