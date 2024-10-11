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
