function updateStats() {
    const stats = {
        total_wins: parseFormattedNumber(document.getElementById('total-wins').value),
        total_losses: parseFormattedNumber(document.getElementById('total-losses').value),
        assaults_won: parseFormattedNumber(document.getElementById('assaults-won').value),
        assaults_lost: parseFormattedNumber(document.getElementById('assaults-lost').value),
        defending_battles_won: parseFormattedNumber(document.getElementById('defending-battles-won').value),
        defending_battles_lost: parseFormattedNumber(document.getElementById('defending-battles-lost').value),
        kills: parseFormattedNumber(document.getElementById('kills').value),
        destroyed_traps: parseFormattedNumber(document.getElementById('destroyed-traps').value),
        lost_associates: parseFormattedNumber(document.getElementById('lost-associates').value),
        lost_traps: parseFormattedNumber(document.getElementById('lost-traps').value),
        healed_associates: parseFormattedNumber(document.getElementById('healed-associates').value),
        wounded_enemy_associates: parseFormattedNumber(document.getElementById('wounded-enemy-associates').value),
        enemy_turfs_destroyed: parseFormattedNumber(document.getElementById('enemy-turfs-destroyed').value),
        turf_destroyed_times: parseFormattedNumber(document.getElementById('turf-destroyed-times').value),
        eliminated_enemy_influence: parseFormattedNumber(document.getElementById('eliminated-enemy-influence').value)
    };

    fetch('/stats', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(stats),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`Error: ${data.error}\n${data.details || ''}`);
        } else {
            alert(data.message);
            getStats();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An unexpected error occurred. Please try again.');
    });
}

function getStats() {
    fetch('/stats')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            alert(`Error: ${data.error}\n${data.details || ''}`);
        } else {
            updateStatsDisplay(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An unexpected error occurred while fetching stats. Please try again.');
    });
}

function updateStatsDisplay(stats) {
    for (const [key, value] of Object.entries(stats)) {
        const element = document.getElementById(key.replace(/_/g, '-'));
        if (element) {
            element.value = formatNumber(value.current);
        }
    }
}

// Call getStats when the page loads
document.addEventListener('DOMContentLoaded', getStats);
