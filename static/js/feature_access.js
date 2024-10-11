document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('feature-access-form');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const featureAccessData = {};

        for (let [key, value] of formData.entries()) {
            if (key.startsWith('feature_access')) {
                const [_, userId, feature] = key.match(/feature_access\[(\d+)\]\[(.+)\]/);
                if (!featureAccessData[userId]) {
                    featureAccessData[userId] = {};
                }
                featureAccessData[userId][feature] = value === 'on';
            }
        }

        // Add all features for each user, including unchecked ones
        const users = document.querySelectorAll('tr[data-user-id]');
        const features = Array.from(document.querySelectorAll('th')).slice(1).map(th => th.textContent.trim().toLowerCase().replace(' ', '_'));

        users.forEach(userRow => {
            const userId = userRow.dataset.userId;
            if (!featureAccessData[userId]) {
                featureAccessData[userId] = {};
            }
            features.forEach(feature => {
                if (!(feature in featureAccessData[userId])) {
                    featureAccessData[userId][feature] = false;
                }
            });
        });

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
