document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('feature-access-form');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const featureAccessData = {};

        // Get all users and features
        const users = document.querySelectorAll('tr[data-user-id]');
        const features = Array.from(document.querySelectorAll('th')).slice(1).map(th => th.textContent.trim().toLowerCase().replace(' ', '_'));

        // Initialize featureAccessData for all users and features
        users.forEach(userRow => {
            const userId = userRow.dataset.userId;
            featureAccessData[userId] = {};
            features.forEach(feature => {
                featureAccessData[userId][feature] = false;
            });
        });

        // Update featureAccessData with checked boxes
        for (let [key, value] of formData.entries()) {
            if (key.startsWith('feature_access')) {
                const [_, userId, feature] = key.match(/feature_access\[(\d+)\]\[(.+)\]/);
                featureAccessData[userId][feature] = true;
            }
        }

        console.log('Sending feature access data:', featureAccessData);

        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(featureAccessData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Feature access updated successfully');
            } else {
                alert('Error updating feature access: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An unexpected error occurred');
        });
    });
});
